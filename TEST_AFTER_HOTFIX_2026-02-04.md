# 🧪 修复后测试指南

## 紧急修复已完成

✅ 修复了 `TypeError: unhashable type: 'slice'` 错误
✅ critic.py 和 planner.py 现在能正确处理两种 plot_threads 数据结构

---

## 测试步骤

### 1. 短篇模式测试 (< 50 章)

```bash
# 如果你的配置是短篇（target_chapters < 50）
./novel.sh generate
```

**预期结果**:
- ✅ 能正常运行
- ✅ 没有 TypeError
- ✅ Critic 和 Planner 节点正常工作

---

### 2. 长篇模式测试 (≥ 50 章)

```bash
# 如果你的配置是长篇（target_chapters >= 50）
./novel.sh generate
```

**预期结果**:
- ✅ 能正常运行（之前会崩溃）
- ✅ 没有 TypeError
- ✅ 使用分层记忆
- ✅ Critic 和 Planner 能正确读取 plot_threads["active"]

---

## 如果仍有错误

### 清除旧状态

如果之前生成失败，数据库可能有损坏的状态：

```bash
# 清除旧状态
./novel.sh clean

# 重新开始
./novel.sh generate
```

---

## 验证要点

### Planner 节点

查看输出，应该能看到：
```
--- PLANNER NODE ---
  📋 规划第 X 章...
  🧠 使用分层记忆系统  # 长篇模式
  或
  📖 使用完整记忆系统  # 短篇模式
  ✅ 大纲生成成功
```

**不应该看到**:
```
TypeError: unhashable type: 'slice'
```

---

### Critic 节点

查看输出，应该能看到：
```
--- CRITIC NODE ---
  📏 检查完整内容 (XXXX 字符)
  ✅ 评审完成
     状态: ✅ 通过  # 或 ⚠️ 需改进
```

**不应该看到**:
```
TypeError: unhashable type: 'slice'
```

---

## 当前系统状态

### 已修复的 Bug（总计 6 个）

1. ✅ 浅拷贝导致状态污染
2. ✅ plot_tracks 拼写错误
3. ✅ plot_threads 数据结构不一致（memory.py）
4. ✅ state 参数缺失
5. ✅ JSON 解析失败
6. ✅ **plot_threads 切片错误（critic.py, planner.py）** ← 新修复

### 已优化的功能

1. ✅ Critic 超时延长（90秒）
2. ✅ 字数调整（1500-2000字）
3. ✅ 总纲生成工具集成

---

## 推荐测试流程

### 完整测试

```bash
# 1. 创建新配置（测试总纲生成）
./novel.sh new

# 输入信息，选择生成总纲 (y)

# 2. 查看配置（确认总纲已保存）
./novel.sh config

# 3. 开始生成
./novel.sh generate

# 4. 观察输出
# - 检查是否有错误
# - 验证字数（1500-2000字）
# - 验证 Memory 节点成功
# - 验证 Critic 节点成功
```

---

## 问题排查

### 如果看到 TypeError

1. **检查 Python 版本**
   ```bash
   python3 --version
   # 应该是 3.8+
   ```

2. **检查修复是否应用**
   ```bash
   grep -A 3 "isinstance(plot_threads, dict)" src/nodes/critic.py
   # 应该能看到修复后的代码
   ```

3. **重新加载代码**
   ```bash
   # 退出并重新运行
   ./novel.sh generate
   ```

---

## 预期效果

### 短篇模式
- plot_threads 是 list
- 直接切片 `plot_threads[-5:]`
- ✅ 正常工作

### 长篇模式
- plot_threads 是 dict `{"active": [...]}`
- 先提取 `plot_threads.get("active", [])`
- 再切片 `active_threads[-5:]`
- ✅ 正常工作

---

**修复完成时间**: 2026-02-04
**测试建议**: 立即测试长篇模式
**优先级**: 🔴 Critical
**状态**: ✅ 已修复
