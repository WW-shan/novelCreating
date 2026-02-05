# 长篇小说（200+章）使用指南

## 现状说明

**核心组件已实现✅，工作流集成待完成⏳**

当前系统 (`main.py`) 是为短篇小说（< 100章）优化的。所有长篇组件已开发并测试，但尚未集成到主工作流中。

---

## 方案一：分批生成（推荐，立即可用）

将长篇小说分成多个批次生成，每批 50 章。

### 步骤

```bash
# 第1批：第1-50章
# 编辑 bible/novel_config_latest.yaml
# 设置 target_chapters: 50

./run_novel.sh

# 第2批：第51-100章
# 手动更新 world_bible（从第1批的输出）
# 设置 target_chapters: 50

./run_novel.sh

# 重复直到完成
```

### 优点
- ✅ 立即可用
- ✅ 使用稳定的现有系统
- ✅ 可控的内存占用

### 缺点
- ⚠️ 需要手动管理批次
- ⚠️ 需要手动更新状态

---

## 方案二：手动使用长篇组件（高级）

使用已实现的长篇组件，但需要编写自定义脚本。

### 已实现的组件

1. **分层记忆系统**
   ```python
   from src.memory.layered_memory import (
       initialize_layered_memory,
       compress_volume_memory,
       get_context_for_planner
   )
   ```

2. **RAG 系统**（可选）
   ```python
   from src.memory.rag_memory import create_rag_memory
   ```

3. **卷规划节点**
   ```python
   from src.nodes.volume_planner import volume_planner_node
   ```

4. **卷审查节点**
   ```python
   from src.nodes.volume_review import volume_review_node
   ```

5. **里程碑审查节点**
   ```python
   from src.nodes.milestone_review import milestone_review_node
   ```

### 示例：卷记忆压缩

```python
from src.memory.layered_memory import compress_volume_memory

# 在第25章完成后
if current_chapter % 25 == 0:
    volume_index = current_chapter // 25
    state = compress_volume_memory(state, volume_index)
    print(f"✅ 第{volume_index}卷记忆已压缩")
```

### 示例：使用 RAG

```python
from src.memory.rag_memory import create_rag_memory

# 初始化
rag = create_rag_memory(
    novel_title="我的小说",
    enabled=True
)

# 添加章节
rag.add_chapter(chapter_index, summary, volume_index)

# 检索相似内容
similar = rag.retrieve_similar_chapters(
    query="主角面临选择",
    current_chapter=100
)
```

### 优点
- ✅ 使用真正的长篇组件
- ✅ 内存压缩和 RAG 支持
- ✅ 灵活可控

### 缺点
- ⚠️ 需要编写自定义代码
- ⚠️ 需要理解系统架构
- ⚠️ 高级用户专用

---

## 方案三：等待完整集成（未来）

等待 `main_long.py` 的完整实现。

### 开发计划

待完成的工作：
1. ⏳ 创建 `main_long.py` 主程序
2. ⏳ 创建 `configure_long_novel.py` 配置工具
3. ⏳ 设计总纲和卷框架格式
4. ⏳ 集成所有长篇节点到工作流
5. ⏳ 端到端测试

预计工作量：**4-8 小时**

---

## 长篇组件测试

所有长篇组件已通过测试：

```bash
./test_core_logic.sh

✅ 伏笔年龄计算修复验证通过
✅ 分层记忆数据结构正确
✅ Prompt 长度控制有效

内存压缩率: 80.5%
```

---

## 技术细节

### 分层记忆工作原理

```
章节 1-25 (第1卷)
  → 详细记忆（热记忆）
  → 卷结束时压缩为500字摘要
  → 移到冷记忆

章节 26-50 (第2卷)
  → 详细记忆（热记忆）
  → 卷结束时压缩
  → 移到冷记忆

...

到第200章：
  热记忆: 第176-200章详细 (~6,000字)
  冷记忆: 前7卷摘要 (~3,500字)
  总计: ~9,500字 (vs 旧系统的50,000字)
```

### 伏笔追踪修复

```python
# 旧版（错误）
age = len(plot_threads) - index  # ❌

# 新版（正确）
thread = {
    "text": "伏笔内容",
    "created_at": chapter_index,
    "resolved": False
}
age = current_chapter - thread["created_at"]  # ✅
```

---

## 推荐方案

**对于大多数用户**: 使用**方案一（分批生成）**

- 简单可靠
- 立即可用
- 无需修改代码

**对于高级用户**: 研究**方案二（手动使用组件）**

- 参考 `src/memory/` 和 `src/nodes/` 中的实现
- 查看 `test_core_logic.sh` 了解用法
- 阅读 `LONG_NOVEL_IMPLEMENTATION.md` 了解设计

**对于开发者**: 贡献**方案三（完整集成）**

- 参考设计文档：`docs/plans/2026-02-04-long-novel-system-design.md`
- 使用现有组件
- 提交 Pull Request

---

## 参考文档

- `LONG_NOVEL_IMPLEMENTATION.md` - 实现报告
- `docs/plans/2026-02-04-long-novel-system-design.md` - 设计文档
- `QUICK_START_LONG_NOVEL.md` - 快速开始
- `src/memory/` - 记忆系统实现
- `src/nodes/volume_*.py` - 长篇节点实现

---

**总结**: 长篇系统的核心已完成并测试通过，但为了保持系统稳定性和简单性，建议当前使用分批生成方式。完整集成将在未来版本中提供。
