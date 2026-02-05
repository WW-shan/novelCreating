# 断点续传功能说明

## 🔍 问题分析

**用户反馈**: "我运行 runnovel 退出，下次运行会重新开始生成"

**根本原因**:
- 系统已使用 `SqliteSaver` 保存状态到 `novel_state.db`
- 但 `main.py:308` 每次都传入 `initial_state`，覆盖了已保存的进度
- LangGraph 的正确用法是：如果有保存的状态，从保存点恢复；否则使用初始状态

---

## ✅ 解决方案

### 方案 A：自动断点续传（推荐）

修改 `src/main.py` 检查是否有保存的状态：

```python
# 检查是否有保存的状态
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

db_path = "/project/novel/novel_state.db"
conn = sqlite3.connect(db_path, check_same_thread=False)
memory = SqliteSaver(conn)

thread_id = f"novel_{config['novel']['title']}"
config_obj = {"configurable": {"thread_id": thread_id}}

# 尝试获取最后保存的状态
try:
    saved_state = memory.get(config_obj)
    if saved_state and saved_state.values:
        print("\\n🔄 检测到未完成的生成任务")
        current_chapter = saved_state.values.get('current_chapter_index', 1)
        target_chapters = config['novel']['target_chapters']
        print(f"   已完成: {current_chapter - 1}/{target_chapters} 章")
        print(f"   将从第 {current_chapter} 章继续生成...")

        # 从保存点恢复，不传 initial_state
        for step_output in app.stream(None, config=config_obj):
            # 继续处理...
    else:
        # 没有保存状态，从头开始
        print("\\n🎬 开始新的生成任务...")
        for step_output in app.stream(initial_state, config=config_obj):
            # 处理...
except Exception as e:
    # 无法读取保存状态，从头开始
    print("\\n🎬 开始新的生成任务...")
    for step_output in app.stream(initial_state, config=config_obj):
        # 处理...
```

### 方案 B：手动清除重新开始

如果用户想重新开始，删除数据库：

```bash
rm novel_state.db
./run_novel.sh  # 从头开始
```

### 方案 C：使用不同的 thread_id

每次生成使用新的 thread_id：

```python
import time
thread_id = f"novel_{config['novel']['title']}_{int(time.time())}"
```

这样每次都是新的生成任务，不会恢复之前的状态。

---

## 🎯 推荐实现（方案 A）

**优点**:
- 自动检测和恢复
- 用户无需手动操作
- 支持中断后继续

**工作流程**:
1. 检查 `novel_state.db` 中是否有该小说的保存状态
2. 如果有 → 显示进度，从断点恢复
3. 如果没有 → 从头开始生成

---

## 📋 实现步骤

需要修改的文件：`src/main.py`

位置：第 307-308 行

修改前：
```python
for step_output in app.stream(initial_state, config=config_obj):
```

修改后：
```python
# 尝试恢复保存的状态
from langgraph.graph.graph import CompiledGraph

snapshot = app.get_state(config_obj)
if snapshot and snapshot.values and snapshot.values.get('current_chapter_index', 1) > 1:
    current = snapshot.values.get('current_chapter_index', 1)
    target = config['novel']['target_chapters']
    print(f"\\n🔄 检测到未完成任务：已完成 {current-1}/{target} 章")
    print(f"   按 Enter 继续生成，或 Ctrl+C 取消")
    input()

    # 从断点恢复（不传 initial_state）
    for step_output in app.stream(None, config=config_obj):
        # ... 处理逻辑
else:
    # 从头开始
    print("\\n🎬 开始新的生成任务...")
    for step_output in app.stream(initial_state, config=config_obj):
        # ... 处理逻辑
```

---

## 🔧 临时解决方案（立即可用）

如果不想修改代码，可以：

### 选项 1：删除数据库重新开始
```bash
rm /project/novel/novel_state.db
./run_novel.sh
```

### 选项 2：使用不同的小说标题
```bash
python3 configure_novel.py
# 输入新的标题（不同于之前的）
./run_novel.sh
```

### 选项 3：手动恢复（高级）

查看数据库中保存的状态：
```python
import sqlite3
conn = sqlite3.connect('novel_state.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM checkpoints")
print(cursor.fetchall())
```

---

## 📊 对比

| 方案 | 优点 | 缺点 | 实现难度 |
|------|------|------|----------|
| A. 自动续传 | 最智能，用户友好 | 需修改代码 | 中等 |
| B. 手动删除 | 立即可用 | 手动操作 | 零 |
| C. 新 thread_id | 每次独立 | 不支持续传 | 简单 |

---

## ✅ 建议

**短期**（立即使用）:
- 使用方案 B：删除 `novel_state.db` 重新开始

**长期**（改进系统）:
- 实现方案 A：自动断点续传功能

需要我实现方案 A 吗？
