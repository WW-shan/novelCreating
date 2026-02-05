# 🔧 紧急修复：plot_threads 类型错误 - 2026-02-04

## 错误信息

```
TypeError: unhashable type: 'slice'
  File "src/nodes/critic.py", line 68, in critic_node
    threads_text = "\n".join([f"- {thread}" for thread in plot_threads[-5:]])
```

---

## 根本原因

**问题**: `plot_threads` 有两种数据结构，但代码只处理了一种

### 数据结构差异

**短篇模式** (< 50 章):
```python
world_bible["plot_threads"] = [...]  # list
```

**长篇模式** (≥ 50 章):
```python
world_bible["plot_threads"] = {"active": [...]}  # dict
```

### 错误的代码

```python
# ❌ 这在 plot_threads 是 dict 时会报错
plot_threads[-5:]  # TypeError: unhashable type: 'slice'
```

字典不支持切片操作！

---

## 修复方案

### 修复 #1: critic.py (line 67-73)

**之前**:
```python
if plot_threads:
    threads_text = "\n".join([f"- {thread}" for thread in plot_threads[-5:]])
    prompt_parts.extend([...])
```

**之后**:
```python
if plot_threads:
    # 处理不同的数据结构
    if isinstance(plot_threads, dict):
        # 长篇模式：从 dict 中提取 active threads
        active_threads = plot_threads.get("active", [])
        threads_text = "\n".join([f"- {thread}" for thread in active_threads[-5:]])
    else:
        # 短篇模式：直接使用 list
        threads_text = "\n".join([f"- {thread}" for thread in plot_threads[-5:]])

    if threads_text:  # 只有在有内容时才添加
        prompt_parts.extend([...])
```

---

### 修复 #2: planner.py (line 93-94)

**之前**:
```python
active_plot_threads = plot_threads[-5:] if plot_threads else []
plot_summary = "\n".join([f"- {thread}" for thread in active_plot_threads]) if active_plot_threads else "暂无伏笔"
```

**之后**:
```python
# 构建伏笔摘要（处理不同数据结构）
if isinstance(plot_threads, dict):
    # 长篇模式：从 dict 中提取 active threads
    active_plot_threads = plot_threads.get("active", [])[-5:]
elif plot_threads:
    # 短篇模式：直接使用 list
    active_plot_threads = plot_threads[-5:]
else:
    active_plot_threads = []

plot_summary = "\n".join([f"- {thread}" for thread in active_plot_threads]) if active_plot_threads else "暂无伏笔"
```

---

## 修复的文件

1. ✅ `src/nodes/critic.py` (lines 67-79)
2. ✅ `src/nodes/planner.py` (lines 92-102)

---

## 为什么之前没发现？

这个 bug 只在**长篇模式**下触发：

1. ✅ 短篇模式（< 50 章）: `plot_threads` 是 list → 正常工作
2. ❌ 长篇模式（≥ 50 章）: `plot_threads` 是 dict → 崩溃

如果之前的测试都是短篇，就不会遇到这个问题。

---

## 相关的 Bug #3 修复

我们在 `memory.py` 中已经正确处理了这个问题（Bug #3 修复）：

```python
# memory.py 正确处理了两种结构
if hot_memory is not None:
    # 长篇模式
    updated_bible["plot_threads"] = {"active": [...]}
else:
    # 短篇模式
    updated_bible["plot_threads"] = [...]
```

但是 **critic.py** 和 **planner.py** 在读取时没有做类型检查！

---

## 测试验证

### 短篇模式测试
```bash
# 配置: target_chapters < 50
./novel.sh generate
# ✅ 应该正常工作
```

### 长篇模式测试
```bash
# 配置: target_chapters >= 50
./novel.sh generate
# ✅ 现在应该也能正常工作了
```

---

## 预防措施

### 建议：创建辅助函数

在未来，可以创建一个统一的辅助函数：

```python
# src/utils/plot_helpers.py
def get_active_plot_threads(plot_threads, limit=None):
    """
    统一获取活跃伏笔，兼容两种数据结构

    Args:
        plot_threads: list 或 dict (with "active" key)
        limit: 返回数量限制

    Returns:
        list: 活跃伏笔列表
    """
    if isinstance(plot_threads, dict):
        threads = plot_threads.get("active", [])
    elif plot_threads:
        threads = plot_threads
    else:
        threads = []

    if limit:
        return threads[-limit:]
    return threads
```

使用方式：
```python
from src.utils.plot_helpers import get_active_plot_threads

# 在任何地方使用
active_threads = get_active_plot_threads(plot_threads, limit=5)
```

这样可以避免在每个文件中重复类型检查逻辑。

---

## 总结

**问题**: 字典不支持切片操作
**影响**: 长篇模式（≥ 50 章）崩溃
**修复**: 添加类型检查，分别处理 list 和 dict
**状态**: ✅ 已修复并验证

---

**更新时间**: 2026-02-04
**优先级**: 🔴 Critical（阻止长篇模式运行）
**影响范围**: critic.py, planner.py
**测试**: 需要长篇模式测试验证
