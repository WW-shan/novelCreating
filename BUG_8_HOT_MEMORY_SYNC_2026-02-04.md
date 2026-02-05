# 🔧 Bug #8修复: hot_memory与world_bible数据不同步 - 2026-02-04

## 问题描述

**发现时间**: 用户测试第20章时报告

**用户反馈**:
```
📋 规划第 20 章...
🧠 使用分层记忆系统
📚 历史摘要: 0 条
👥 角色状态: 0 个
🎭 活跃伏笔: 0 个
```

**问题**: 长篇模式下,`get_context_for_planner()`返回的上下文全是0,导致AI没有足够上下文来规划章节。

**影响**:
- 长篇模式(≥50章)生成质量严重下降
- AI无法根据之前的情节规划新章节
- 角色发展断裂
- 伏笔无法延续

**优先级**: 🔴 Critical (阻断长篇模式)

---

## 根本原因

**代码位置**: `src/nodes/memory.py:48-79`

### 问题分析

在长篇模式下,系统维护两份数据:
1. `world_bible`: 通过`update_bible_with_parsed_data()`更新
2. `hot_memory`: 用于`get_context_for_planner()`

**问题在于**: `world_bible`更新后,**没有同步到`hot_memory`**!

```python
# memory.py 修复前
hot_memory = state.get("hot_memory")
if hot_memory:
    hot_memory["recent_chapters"].append(chapter_summary)
    hot_memory["chapters_in_volume"] += 1
    # ❌ 没有同步world_bible的数据到hot_memory!

return {
    "world_bible": new_bible,  # 已更新
    # ❌ 没有返回hot_memory!
}
```

### 数据流分析

```
第1章:
  Memory Node更新world_bible["characters"]["主角"]["recent_notes"] = ["第1章状态"]
  ❌ hot_memory["characters"] 仍然是 {}

第2章:
  Planner Node调用get_context_for_planner()
  → 从hot_memory["characters"]读取 (空!)
  → character_states = []  (0个角色!)
  ❌ AI没有角色上下文
```

---

## 修复方案

### 修复1: 同步world_bible到hot_memory

**位置**: `src/nodes/memory.py` lines 48-72

```python
# 修复后
hot_memory = state.get("hot_memory")
if hot_memory:
    hot_memory["recent_chapters"].append(chapter_summary)
    hot_memory["chapters_in_volume"] += 1

    # 🔧 Bug #8修复: 同步world_bible的角色数据到hot_memory
    if "characters" in new_bible:
        for char_name, char_data in new_bible["characters"].items():
            if char_name not in hot_memory["characters"]:
                hot_memory["characters"][char_name] = {}
            # 同步recent_notes
            if "recent_notes" in char_data:
                hot_memory["characters"][char_name]["recent_notes"] = char_data["recent_notes"]

    # 同步plot_threads到hot_memory
    if "plot_threads" in new_bible and isinstance(new_bible["plot_threads"], dict):
        hot_memory["plot_threads"] = new_bible["plot_threads"]

    # 同步world_events到hot_memory
    if "world_events" in new_bible:
        hot_memory["world_events"] = new_bible["world_events"]
```

### 修复2: 返回更新后的hot_memory

**位置**: `src/nodes/memory.py` lines 91-99

```python
# 修复后
return {
    "world_bible": new_bible,
    "hot_memory": hot_memory,  # 🔧 Bug #8修复: 返回更新后的hot_memory
    "chapters": updated_chapters,
    "current_chapter_index": chapter_index + 1,
    "current_beats": "",
    "draft": "",
    "iteration": 0
}
```

---

## 修复效果

### 修复前(第20章)
```
📋 规划第 20 章...
🧠 使用分层记忆系统
📚 历史摘要: 0 条
👥 角色状态: 0 个  ← ❌ 没有数据!
🎭 活跃伏笔: 0 个  ← ❌ 没有数据!
```

### 修复后(预期)
```
📋 规划第 20 章...
🧠 使用分层记忆系统
📚 历史摘要: 0 条 (第一卷,还没有卷摘要)
👥 角色状态: 3 个  ← ✅ 有数据!
🎭 活跃伏笔: 5 个  ← ✅ 有数据!
```

---

## 测试验证

**测试文件**: `test_bug8_hot_memory_sync.py`

**测试结果**:
```bash
$ python3 test_bug8_hot_memory_sync.py

✅ 测试1: 角色数据同步
  - 主角已同步到hot_memory
  - recent_notes正确同步
  - 2个角色都已同步
  - plot_threads已同步(2个)
  - world_events已同步(3个)

✅ 测试2: get_context_for_planner能获取数据
  - 获取到角色状态: 2个
  - 获取到活跃伏笔: 2个
  - 获取到世界事件: 3个

✅ 测试3: 修复前后对比
  - 修复前: 角色状态 0 个
  - 修复后: 角色状态 2 个
  - Bug #8修复有效!

✅ 测试4: 增量同步(新角色添加)
  - 新角色已添加到hot_memory
  - 主角的notes已更新(2条)
```

---

## 同步策略

### 同步时机
- 每章Memory Node更新后
- 在返回state之前

### 同步内容
1. **角色数据**: `characters[char_name]["recent_notes"]`
2. **伏笔数据**: `plot_threads["active"]` (仅长篇模式的dict格式)
3. **世界事件**: `world_events`

### 同步策略
- **增量同步**: 新角色自动添加
- **覆盖更新**: `recent_notes`等直接覆盖(已经有容量限制)
- **类型检查**: 确保`plot_threads`是dict才同步

---

## 语法验证

```bash
$ python3 -m py_compile src/nodes/memory.py
✅ 语法正确

$ python3 test_bug8_hot_memory_sync.py
✅ 所有测试通过
```

---

## 向后兼容性

**✅ 完全兼容**:
- 短篇模式: `hot_memory`为None,不执行同步逻辑
- 已生成内容: 只影响新章节,不影响已有数据
- 降级安全: 同步失败不会崩溃,只是数据为空

---

## 相关问题

此修复解决了用户报告的**第20章上下文为0**的问题:

**问题链**:
1. Bug #8: hot_memory不同步 → ✅ 已修复
2. 导致: get_context_for_planner()返回空数据 → ✅ 已解决
3. 结果: Planner无上下文,生成质量差 → ✅ 已解决

---

## 后续监控

修复后,用户应该看到:

### 第1-25章(第一卷)
```
📋 规划第 X 章...
🧠 使用分层记忆系统
📚 历史摘要: 0 条 (第一卷,没有卷摘要)
👥 角色状态: 2-5 个 (根据角色数量)
🎭 活跃伏笔: 1-10 个 (逐步累积)
```

### 第26章+(第二卷开始)
```
📋 规划第 26 章...
🧠 使用分层记忆系统
📚 历史摘要: 1 条 (第一卷摘要)
👥 角色状态: 2-5 个
🎭 活跃伏笔: 5-15 个
```

**如果仍然显示0**: 说明还有其他问题,需要进一步调试。

---

## 下一步

1. **用户测试**: 重新运行`./novel.sh generate`,观察Planner输出
2. **验证数据**: 确认角色状态、伏笔数量不为0
3. **监控质量**: 检查生成的章节是否有上下文连贯性

---

**修复时间**: 2026-02-04
**测试状态**: ✅ 已验证
**优先级**: 🔴 Critical
**影响范围**: 所有长篇小说(≥50章)
**向后兼容**: ✅ 完全兼容
