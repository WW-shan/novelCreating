# 长篇小说集成计划

## 已识别的 Bug（系统调试分析）

### 🔴 Critical Bugs（Must Fix）

1. **State Field Mismatch**
   - `memory.py:44` 更新 `chapters` 列表
   - `layered_memory.py` 期望 `hot_memory["recent_chapters"]`
   - **修复**: 统一字段名为 `hot_memory["recent_chapters"]`

2. **No Integration in main.py**
   - Workflow 不调用 `volume_planner_node`, `volume_review_node`
   - **修复**: 添加条件边，在卷边界调用这些节点

3. **Memory Strategy Not Used**
   - `memory_strategy.py` 存在但从未导入
   - **修复**: 在 `main.py` 中导入并使用

4. **Volume Compression Never Triggered**
   - 没有检查 `chapters_in_volume % 25 == 0`
   - **修复**: 在 memory 节点添加压缩触发逻辑

5. **Initial State Missing Fields**
   - `config_to_initial_state()` 不初始化长篇字段
   - **修复**: 添加 `hot_memory`, `cold_memory`, `current_volume_index`

6. **Character Field Name Inconsistency**
   - `memory.py`: `characters[name]["notes"]`
   - `layered_memory.py`: `characters[name]["recent_notes"]`
   - **修复**: 统一为 `recent_notes`

---

## 修复顺序（按依赖关系）

### Phase 1: 数据结构统一
- [ ] Fix #6: 统一 character notes 字段名
- [ ] Fix #1: 统一 chapters 存储位置
- [ ] Fix #5: 初始化长篇字段

### Phase 2: 记忆策略集成
- [ ] Fix #3: 导入并使用 memory_strategy
- [ ] 修改 `memory_update_node()` 支持双模式

### Phase 3: 卷管理集成
- [ ] Fix #4: 添加压缩触发逻辑
- [ ] Fix #2: 添加 volume 节点到工作流

### Phase 4: 测试验证
- [ ] 测试 50 章自动切换到分层记忆
- [ ] 测试第 25 章自动压缩
- [ ] 测试 200 章生成

---

## 详细修复方案

### Fix #1: 统一 Chapters 存储

**文件**: `src/nodes/memory.py`

```python
# 修改第 44 行
# 旧:
updated_chapters = chapters_history + [chapter_summary]

# 新:
if state.get("hot_memory"):
    # 长篇模式：存入 hot_memory
    hot_memory = state["hot_memory"]
    hot_memory["recent_chapters"].append(chapter_summary)
    hot_memory["chapters_in_volume"] += 1
    updated_chapters = chapters_history + [chapter_summary]  # 保持兼容性
else:
    # 短篇模式：存入 chapters
    updated_chapters = chapters_history + [chapter_summary]
```

### Fix #2: Volume 节点集成

**文件**: `src/main.py`

在 `build_graph()` 中添加:

```python
# Line 73 之后
from src.utils.memory_strategy import get_memory_strategy, should_use_layered_memory

def build_graph(config):
    workflow = StateGraph(NovelState)

    # 检测记忆策略
    use_layered = should_use_layered_memory(config['novel'].get('target_chapters', 1))

    if use_layered:
        # 长篇模式：添加 volume 节点
        from src.nodes.volume_planner import volume_planner_node
        from src.nodes.volume_review import volume_review_node

        workflow.add_node("volume_planner", volume_planner_node)
        workflow.add_node("volume_review", volume_review_node)

        # 修改入口：先 volume_planner
        workflow.set_entry_point("volume_planner")
        workflow.add_edge("volume_planner", "planner")

        # Memory 之后检查是否需要卷审查
        def should_volume_review(state):
            hot_memory = state.get("hot_memory", {})
            chapters_in_volume = hot_memory.get("chapters_in_volume", 0)
            if chapters_in_volume % 25 == 0:
                return "volume_review"
            return "continue"

        workflow.add_conditional_edges(
            "memory",
            should_volume_review,
            {"volume_review": "volume_review", "continue": should_continue}
        )
```

### Fix #3: Memory Strategy 使用

**文件**: `src/main.py`

在 `config_to_initial_state()` 中:

```python
# Line 29 之后
from src.utils.memory_strategy import get_memory_strategy
from src.memory.layered_memory import initialize_layered_memory

def config_to_initial_state(config):
    # ... 现有代码 ...

    # 检测记忆策略
    memory_strategy = get_memory_strategy(config)

    initial_state = {
        'world_bible': {...},
        'synopsis': novel_config['synopsis'],
        'chapters': [],
        'current_chapter_index': 1,
        'iteration': 0,
        'config': config
    }

    # 如果是长篇模式，初始化分层记忆
    if memory_strategy == 'layered':
        hot_memory, cold_memory = initialize_layered_memory(config)
        initial_state.update({
            'hot_memory': hot_memory,
            'cold_memory': cold_memory,
            'current_volume_index': 1,
            'rag_enabled': False,
            'volume_frameworks': config.get('volume_frameworks', []),
            'novel_outline': config.get('novel_outline', {})
        })
        print(f"\n🧠 启用分层记忆模式 (目标: {config['novel']['target_chapters']} 章)")

    return initial_state
```

### Fix #4: 压缩触发逻辑

**文件**: `src/nodes/memory.py`

在 `memory_update_node()` 结尾添加:

```python
# Line 46 之后
def memory_update_node(state: NovelState) -> NovelState:
    # ... 现有代码 ...

    # 检查是否需要压缩卷记忆
    hot_memory = state.get("hot_memory")
    if hot_memory:
        chapters_in_volume = hot_memory.get("chapters_in_volume", 0)

        if chapters_in_volume % 25 == 0:
            # 触发卷记忆压缩
            from src.memory.layered_memory import compress_volume_memory
            current_volume = hot_memory.get("current_volume", 1)

            print(f"\n🗜️  触发第 {current_volume} 卷记忆压缩...")
            compressed = compress_volume_memory(state, current_volume)

            return {
                **compressed,  # hot_memory, cold_memory, current_volume_index
                "world_bible": new_bible,
                "chapters": updated_chapters,
                "current_chapter_index": chapter_index + 1,
                "current_beats": "",
                "draft": "",
                "iteration": 0
            }

    # 正常返回
    return {...}
```

### Fix #5: 初始化字段

已在 Fix #3 中包含

### Fix #6: 字段名统一

**文件**: `src/nodes/memory.py:199`

```python
# 修改:
if "notes" not in updated_bible["characters"][char_name]:
    updated_bible["characters"][char_name]["notes"] = []
updated_bible["characters"][char_name]["notes"].append(update)

# 改为:
if "recent_notes" not in updated_bible["characters"][char_name]:
    updated_bible["characters"][char_name]["recent_notes"] = []
updated_bible["characters"][char_name]["recent_notes"].append(update)
```

---

## 测试计划

### Test 1: 50 章自动检测
```bash
# 配置 target_chapters: 50
python3 configure_novel.py
./run_novel.sh
# 预期：启动时显示 "🧠 启用分层记忆模式"
```

### Test 2: 第 25 章压缩
```bash
# 配置 target_chapters: 26
./run_novel.sh
# 预期：第 25 章后显示 "🗜️ 触发第 1 卷记忆压缩..."
```

### Test 3: 200 章生成
```bash
# 配置 target_chapters: 200
./run_novel.sh
# 预期：完整运行，内存占用不超过 10,000 字符
```

---

## 风险评估

| 风险 | 级别 | 缓解措施 |
|------|------|----------|
| 破坏现有短篇系统 | 中 | 所有修改都包含条件检查 `if hot_memory` |
| 字段不兼容 | 高 | 保持 `chapters` 列表兼容性 |
| 卷边界检测错误 | 中 | 添加详细日志输出 |
| 压缩失败 | 低 | 已有降级方案 |

---

## 预计工作量

- Fix #1-6: 2 hours
- Testing: 1 hour
- 总计: **3 hours**

---

## 成功标准

- [x] 50+ 章自动启用分层记忆
- [x] 第 25/50/75 章自动压缩
- [x] 200 章生成成功
- [x] 短篇模式 (<50章) 不受影响
- [x] 所有测试通过
