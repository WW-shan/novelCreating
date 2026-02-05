# 🔧 Bug #19修复: chapter_history数据类型不匹配 - 2026-02-04

## 问题描述

**发现时间**: 用户测试卷压缩时报错

**错误信息**:
```
AttributeError: 'str' object has no attribute 'get'
File "/project/novel/src/nodes/planner.py", line 122, in <listcomp>
    f"第{ch.get('index')}章: {ch.get('summary', '')[:100]}"
```

**影响**: 长篇模式第26章(卷压缩后第一章)无法规划,系统崩溃

**优先级**: 🔴 Critical

---

## 根本原因

`chapter_history`在长篇模式和短篇模式下的数据类型不同:

### 短篇模式
```python
chapter_history = state.get("chapters", [])
# 每个元素是dict:
# {"index": 1, "summary": "..."}
```

### 长篇模式
```python
chapter_history = context.get('history_summary', [])
# 从get_context_for_planner返回
# 每个元素是字符串:
# "第1卷: 卷摘要内容..."
```

但`generate_intelligent_beats`中的代码(line 122)假设所有元素都是dict:

```python
# 错误(修复前)
history_summary = "\n".join([
    f"第{ch.get('index')}章: {ch.get('summary', '')[:100]}"
    for ch in recent_chapters
]) if recent_chapters else "这是第一章"
```

当`ch`是字符串时,调用`ch.get('index')`会报错!

---

## 触发场景

1. 用户配置长篇小说(≥50章)
2. 生成第1-25章(正常)
3. 第25章后触发卷压缩
4. **卷压缩完成**,准备生成第26章
5. Planner Node调用`generate_intelligent_beats`
6. 此时`chapter_history`包含卷摘要(字符串)
7. Line 122尝试`ch.get('index')` → **崩溃**!

---

## 修复方案

添加类型检查,兼容两种数据格式:

```python
# 🔧 Bug #19修复
history_lines = []
for ch in recent_chapters:
    if isinstance(ch, dict):
        # 短篇模式: ch是dict
        history_lines.append(f"第{ch.get('index')}章: {ch.get('summary', '')[:100]}")
    else:
        # 长篇模式: ch已经是格式化的字符串
        history_lines.append(str(ch)[:150])

history_summary = "\n".join(history_lines) if history_lines else "这是第一章"
```

---

## 数据流分析

### 短篇模式
```
planner_node:
  chapter_history = world_bible.get("chapters", [])
  # [{"index": 1, "summary": "..."}, ...]

generate_intelligent_beats:
  isinstance(ch, dict) → True
  使用 ch.get('index') ✅
```

### 长篇模式
```
planner_node:
  context = get_context_for_planner(state)
  chapter_history = context.get('history_summary', [])
  # ["第1卷: 摘要...", "第2卷: 摘要..."]

generate_intelligent_beats:
  isinstance(ch, dict) → False
  使用 str(ch) ✅
```

---

## 为什么之前没发现

1. **第1-25章**: 长篇模式下,`chapter_history`是空的(还没有卷摘要)
   - `recent_chapters = []`
   - 走else分支: `"这是第一章"`
   - 没有执行列表推导式,不会报错

2. **第26章**: 卷压缩完成后,`cold_memory`有了第一个卷摘要
   - `chapter_history = ["第1卷: ..."]`
   - 执行列表推导式
   - `ch.get('index')` → **崩溃**!

这是一个**只在卷压缩后才会触发**的bug!

---

## 测试验证

```python
# 测试短篇模式
chapter_history_short = [
    {"index": 1, "summary": "第1章内容"},
    {"index": 2, "summary": "第2章内容"}
]

for ch in chapter_history_short:
    if isinstance(ch, dict):
        line = f"第{ch.get('index')}章: {ch.get('summary', '')[:100]}"
    else:
        line = str(ch)[:150]
# ✅ 正常工作

# 测试长篇模式
chapter_history_long = [
    "第1卷: 第1-25章的摘要内容...",
    "第2卷: 第26-50章的摘要内容..."
]

for ch in chapter_history_long:
    if isinstance(ch, dict):
        line = f"第{ch.get('index')}章: {ch.get('summary', '')[:100]}"
    else:
        line = str(ch)[:150]
# ✅ 正常工作
```

---

## 语法验证

```bash
$ python3 -m py_compile src/nodes/planner.py
✅ 通过
```

---

## 影响范围

- **短篇模式**: 无影响(ch始终是dict)
- **长篇模式**: 修复后才能在第26章后继续运行

---

## 相关Bug

- Bug #12: notes vs recent_notes字段不匹配
- Bug #19: chapter_history类型不匹配

这两个都是**相同类型的问题**: 长篇/短篇模式数据结构不一致。

---

**修复时间**: 2026-02-04
**测试状态**: ✅ 语法验证通过
**优先级**: 🔴 Critical
**触发条件**: 卷压缩后第一章(第26章,第51章,...)
**向后兼容**: ✅ 完全兼容
