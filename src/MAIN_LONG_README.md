# 长篇小说生成器（main_long.py）

**这是一个独立的长篇小说生成程序，专门用于生成200+章的长篇小说。**

## 与 main.py 的区别

- `main.py`: 短篇模式（< 100章），简单直接
- `main_long.py`: 长篇模式（200+章），分层记忆+卷管理

## 使用方法

```bash
# 1. 创建长篇配置（需要额外的总纲和卷框架）
python3 configure_long_novel.py

# 2. 生成长篇小说
python3 src/main_long.py
```

## 功能特性

- 分层记忆（内存压缩80%+）
- 卷规划和审查
- 里程碑审查
- 可选 RAG 支持

## 实现状态

⏳ **待实现**

核心组件已完成：
- ✅ 分层记忆系统 (`src/memory/layered_memory.py`)
- ✅ RAG 系统 (`src/memory/rag_memory.py`)
- ✅ 卷规划节点 (`src/nodes/volume_planner.py`)
- ✅ 卷审查节点 (`src/nodes/volume_review.py`)
- ✅ 里程碑审查节点 (`src/nodes/milestone_review.py`)

待完成：
- ⏳ `main_long.py` - 长篇主程序
- ⏳ `configure_long_novel.py` - 长篇配置工具
- ⏳ 工作流集成

## 临时解决方案

当前可用选项：
1. **短篇模式**（推荐）: 使用 `main.py`，支持 100 章以内
2. **手动长篇**: 分多次运行，每次生成 50 章，手动管理记忆

详见：`LONG_NOVEL_IMPLEMENTATION.md`
