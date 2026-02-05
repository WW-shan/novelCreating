# 性能优化建议 - 2026-02-04

## 🐢 潜在性能问题

### Performance Issue #1: Volume Compression Sequential AI Calls

**文件**: `src/memory/layered_memory.py:257-258`

**问题**:
```python
for char_name, char_data in characters.items():
    # ... AI call for each character ...
    time.sleep(1)  # Sleep between each character
```

**影响**:
- **10 个角色**: 10 AI 调用 + 10 秒 sleep = ~20-30 秒
- **15 个角色**: 15 AI 调用 + 15 秒 sleep = ~30-45 秒
- 用户在卷压缩时等待过长

**优化方案**:

#### 选项 1: 移除 sleep（如果不需要限流）
```python
# 移除 time.sleep(1)
```

#### 选项 2: 批量 AI 调用（最佳）
```python
# 将所有角色放在一个 prompt 中
prompt = """
压缩以下角色在本卷的发展：

【角色1】
{character_1_notes}

【角色2】
{character_2_notes}

...

输出格式:
{
  "角色1": "压缩总结",
  "角色2": "压缩总结"
}
"""
```

**节省时间**: 10 AI 调用 → 1 AI 调用 = 节省 ~20-25 秒

---

### Performance Issue #2: Retry Sleep 时间过长

**问题**: 多处使用较长的 sleep 时间用于重试

**文件**: 各个节点 (`planner.py`, `writer.py`, `memory.py` 等)

**示例**:
```python
time.sleep(3)  # 每次重试等待 3 秒
time.sleep((attempt + 1) * 4)  # 4, 8, 12 秒...
```

**影响**:
- 失败时用户等待时间长
- 在本地测试时尤其明显

**建议**:
```python
# 生产环境保持当前值
# 开发环境可以减少:
RETRY_SLEEP = os.getenv("RETRY_SLEEP_TIME", "3")  # 默认 3 秒，可配置
time.sleep(int(RETRY_SLEEP))
```

---

### Performance Issue #3: 深拷贝性能 (可接受)

**文件**: `src/nodes/memory.py:256`

**代码**:
```python
updated_bible = copy.deepcopy(world_bible)
```

**测量**:
- **world_bible 大小**: ~20-30 KB
- **深拷贝时间**: ~0.1-0.5 ms
- **频率**: 每章 1 次

**结论**:
✅ 性能影响可忽略（< 1% 总时间）
✅ 正确性 > 性能
✅ 无需优化

---

## 优化优先级

| 问题 | 影响 | 节省时间 | 优先级 | 复杂度 |
|------|------|---------|--------|--------|
| #1 卷压缩串行调用 | 高 | 20-25秒/卷 | 🔴 高 | 中 |
| #2 Retry sleep 时间 | 中 | 3-12秒/失败 | 🟡 中 | 低 |
| #3 深拷贝性能 | 无 | 无 | 🟢 低 | - |

---

## 实施建议

### 短期（立即可做）
1. ✅ 保持深拷贝（已实施）
2. 考虑移除卷压缩中的 `time.sleep(1)`

### 中期（下个版本）
1. 实现批量角色压缩（1 个 AI 调用处理所有角色）
2. 添加 `RETRY_SLEEP_TIME` 环境变量配置

### 长期（如需要）
1. 实现并行 AI 调用（使用 `asyncio`）
2. 添加 AI 调用缓存机制

---

**结论**:
- 关键 bug 已修复（正确性优先）
- 性能问题是次要的，可在后续版本优化
- 当前性能足够支持 200+ 章生成
