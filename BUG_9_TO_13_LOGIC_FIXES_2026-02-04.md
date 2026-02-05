# 🔧 Bug #9-13修复: 逻辑问题修复 - 2026-02-04

## 概述

在Ralph Loop第1次迭代中,系统地检查了每个节点的逻辑,发现了5个**"代码能跑但不对"**的问题。

---

## Bug #9: 伏笔格式化问题

**发现**: 节点逻辑检查
**优先级**: 🟡 Medium
**文件**: `src/nodes/planner.py:102`, `src/nodes/critic.py:72,75`

### 问题

长篇模式下,`plot_threads["active"]`中的thread是dict对象:
```python
{
    "text": "神秘宝藏的传说",
    "created_at": 1,
    "importance": 8,
    "resolved": False
}
```

但代码直接使用`f"- {thread}"`,导致输出:
```
- {'text': '神秘宝藏的传说', 'created_at': 1, 'importance': 8}
```

这不是用户友好的格式!应该只显示text字段。

### 修复

**planner.py** (lines 92-112):
```python
# 构建伏笔摘要（处理不同数据结构）
if isinstance(plot_threads, dict):
    active_plot_threads = plot_threads.get("active", [])[-5:]
elif plot_threads:
    active_plot_threads = plot_threads[-5:]
else:
    active_plot_threads = []

# 🔧 Bug #9修复: 处理dict格式的thread对象
formatted_threads = []
for thread in active_plot_threads:
    if isinstance(thread, dict):
        # 长篇模式: 提取text字段
        formatted_threads.append(thread.get("text", str(thread)))
    else:
        # 短篇模式: 字符串
        formatted_threads.append(str(thread))

plot_summary = "\n".join([f"- {t}" for t in formatted_threads])
```

**critic.py** (lines 67-87): 同样的修复

### 效果

修复前:
```
【未解决的伏笔/谜团】
- {'text': '神秘宝藏的传说', 'created_at': 1}
```

修复后:
```
【未解决的伏笔/谜团】
- 神秘宝藏的传说
```

---

## Bug #10: 短篇模式创建dict格式thread

**发现**: 节点逻辑检查
**优先级**: 🟡 Medium
**文件**: `src/nodes/memory.py:363-377`

### 问题

短篇模式下,`plot_threads`应该是**字符串列表**,但memory.py的代码创建了**dict对象列表**:

```python
# 错误(修复前)
for dev in plot_developments:
    if isinstance(dev, str):
        thread_dict = {
            "text": dev,
            "created_at": chapter_index,
            "resolved": False,
            "importance": 5
        }
        updated_bible["plot_threads"].append(thread_dict)
```

这导致短篇模式和长篇模式的数据结构不一致!

### 修复

```python
# 🔧 Bug #10修复: 短篇模式保持字符串格式
for dev in plot_developments:
    if isinstance(dev, str):
        updated_bible["plot_threads"].append(dev)
    elif isinstance(dev, dict) and "text" in dev:
        # 如果传入的是dict,提取text字段
        updated_bible["plot_threads"].append(dev["text"])
    else:
        updated_bible["plot_threads"].append(str(dev))
```

### 效果

短篇模式:
- 修复前: `[{"text": "伏笔1", ...}, ...]` (错误)
- 修复后: `["伏笔1", "伏笔2"]` (正确)

---

## Bug #11: 伏笔检测逻辑过于简单

**发现**: 节点逻辑检查
**优先级**: 🟡 Medium
**文件**: `src/memory/layered_memory.py:295`

### 问题

卷压缩时,检测哪些伏笔已揭示的逻辑太简单:

```python
# 错误(修复前)
if thread_text[:30] in volume_content:
    # 标记为已解决
```

问题:
- **假阳性**: 前30字可能偶然出现
- **假阴性**: 伏笔用不同措辞揭示

### 修复

```python
# 🔧 Bug #11修复: 改进伏笔检测逻辑
# 提取关键词
keywords = []
if len(thread_text) >= 10:
    keywords.append(thread_text[5:15])
if len(thread_text) >= 20:
    keywords.append(thread_text[10:20])

# 检查关键词出现次数
mention_count = sum(volume_content.count(kw) for kw in keywords if kw)

# 如果被提及2次以上,可能已揭示
if mention_count >= 2:
    # 标记为已解决
```

### 效果

- 更准确的检测
- 减少假阳性和假阴性
- 仍不是完美(AI方案更好),但比之前显著改进

---

## Bug #12: notes vs recent_notes字段不一致

**发现**: 节点逻辑检查
**优先级**: 🟡 Medium
**文件**: `src/nodes/writer.py:282`, `src/nodes/planner.py:86`

### 问题

角色数据结构在两种模式下不同:
- **短篇模式**: `characters[name]["recent_notes"]`
- **长篇模式** (转换后): `characters[name]["notes"]`

但writer.py和planner.py只使用`notes`,导致短篇模式无法提取角色状态!

### 修复

**writer.py**:
```python
# 🔧 Bug #12修复: 兼容两种模式
notes = char_data.get("recent_notes", char_data.get("notes", []))
```

**planner.py**:
```python
# 🔧 Bug #12修复: 兼容两种模式
notes = char_data.get("notes", char_data.get("recent_notes", []))
```

### 效果

现在两种模式都能正确提取角色状态。

---

## Bug #13: 初始plot_threads格式不一致

**发现**: 节点逻辑检查
**优先级**: 🟡 Medium
**文件**: `src/main.py:51-59, 78-95`

### 问题

**问题1**: 初始创建的plot_tracks格式不合适

```python
# 错误(修复前)
plot_tracks.append({
    'id': 1,
    'description': f"主线剧情：{synopsis}",
    'foreshadowed': False,
    'resolved': False
})
```

这个dict结构与后续使用的`{"text": ..., "created_at": ...}`不匹配!

**问题2**: 长篇模式没有转换plot_threads格式

长篇模式需要`{"active": [...]}`结构,但初始化时直接使用了list。

### 修复

**修复1**: 初始使用简单字符串

```python
# 🔧 Bug #13修复: 初始使用简单格式
plot_tracks = []
if generation.get('foreshadow_strategy') != 'conservative':
    plot_tracks.append(f"主线剧情：{novel_config['synopsis'][:50]}...")
```

**修复2**: 长篇模式转换为dict格式

```python
# 🔧 Bug #13修复: 长篇模式转换
if memory_strategy == 'layered':
    if plot_tracks:
        initial_state['world_bible']['plot_threads'] = {
            "active": [
                {
                    "text": track,
                    "created_at": 1,
                    "importance": 10,  # 初始伏笔重要度最高
                    "resolved": False
                } for track in plot_tracks
            ]
        }
```

### 效果

- 短篇模式: 字符串列表 ✅
- 长篇模式: `{"active": [{"text": ..., ...}]}` ✅
- 数据结构一致性 ✅

---

## 测试验证

**测试文件**: `test_bug9_to_13_logic_fixes.py`

**测试结果**:
```bash
$ python3 test_bug9_to_13_logic_fixes.py

✅ Bug #9: 伏笔格式化 - 通过
✅ Bug #10: 短篇模式thread格式 - 通过
✅ Bug #11: 伏笔检测逻辑 - 通过
✅ Bug #12: notes vs recent_notes - 通过
✅ Bug #13: 初始plot_threads格式 - 通过
```

---

## 语法验证

```bash
$ python3 -m py_compile src/nodes/planner.py
✅ 通过

$ python3 -m py_compile src/nodes/critic.py
✅ 通过

$ python3 -m py_compile src/nodes/memory.py
✅ 通过

$ python3 -m py_compile src/nodes/writer.py
✅ 通过

$ python3 -m py_compile src/main.py
✅ 通过

$ python3 -m py_compile src/memory/layered_memory.py
✅ 通过
```

---

## 修复汇总

| Bug | 问题 | 影响 | 修复文件 |
|-----|------|------|---------|
| #9 | 伏笔格式化显示dict | 用户体验差 | planner.py, critic.py |
| #10 | 短篇模式创建dict thread | 数据结构不一致 | memory.py |
| #11 | 伏笔检测逻辑简单 | 误判多 | layered_memory.py |
| #12 | notes vs recent_notes | 短篇无法提取角色状态 | writer.py, planner.py |
| #13 | 初始plot_threads格式 | 数据结构不匹配 | main.py |

---

## 总Bug修复数

**本次Ralph Loop**: Bug #9-13 (5个逻辑问题)
**之前修复**: Bug #1-8 (8个Critical Bug)
**总计**: 13个Bug

---

**修复时间**: 2026-02-04 (Ralph Loop迭代1)
**测试状态**: ✅ 已验证
**优先级**: 🟡 Medium (逻辑问题,非崩溃级)
**影响范围**: 所有模式
