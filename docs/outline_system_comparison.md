# 大纲系统对比

## 旧系统 (generate_outline.py)

### 特点
- ✅ 完全 AI 自动生成
- ✅ 保存在配置文件的 `novel_outline` 和 `volume_frameworks` 字段
- ✅ 卷纲固定每卷 25 章
- ✅ 支持审查和重新生成
- ❌ 不支持手动自定义
- ❌ 无法调整章节分配

### 数据结构
```yaml
novel_outline:
  main_goal: "主线目标"
  main_conflict: "主要冲突"
  protagonist_arc: "主角成长弧"
  key_milestones:
    - milestone: "里程碑1"
      target_chapter: 20
    - milestone: "里程碑2"
      target_chapter: 50

volume_frameworks:
  - title: "第一卷标题"
    chapters: "1-25"
    core_goal: "核心目标"
    key_events: ["事件1", "事件2"]
    ending_state: "结尾状态"
    foreshadowing: ["伏笔1", "伏笔2"]
```

---

## 新系统 (configure_novel_advanced.py)

### 特点
- ✅ 支持手动自定义
- ✅ 阶段划分灵活（3-15 阶段）
- ✅ 卷章节数可调整
- ✅ 保存到独立文件 `bible/outline.yaml`
- ✅ 三种模式：简易/完整/导入
- ❌ 需要手动输入

### 数据结构
```yaml
outline:
  synopsis: "故事梗概"
  main_goal: "主目标"
  main_conflict: "主线冲突"
  protagonist_arc: "主角成长线"
  phases:
    - name: "第1阶段"
      goal: "阶段目标"
      chapters: "1-20"
    - name: "第2阶段"
      goal: "阶段目标"
      chapters: "21-50"

volumes:
  - volume: 1
    title: "第一卷"
    chapters: "1-30"
    core_goal: "核心目标"
    key_events: ["事件1", "事件2"]
    foreshadowing: ["伏笔1"]
    ending_state: "结尾状态"
```

---

## 推荐方案：整合两个系统

### 方案 A：两阶段流程（推荐）

1. **快速配置**：使用 `configure_novel_advanced.py` 创建项目
   - 选择"简易模式"
   - 只输入梗概和基本信息

2. **AI 补全**：运行 `generate_outline.py` 生成详细大纲
   - AI 自动生成总纲和卷纲
   - 审查后保存

3. **生成小说**：运行 `./novel.sh generate`
   - planner 同时读取两处大纲
   - 优先使用详细的 AI 生成内容

### 方案 B：完全手动（适合有明确构思的作者）

直接使用 `configure_novel_advanced.py` 完整模式
- 手动输入所有阶段和卷纲
- 不需要 AI 生成

### 方案 C：完全自动（适合快速开始）

1. 使用旧的 `configure_novel.py` 创建配置
2. 运行 `generate_outline.py` 生成大纲
3. 开始生成

---

## 实现统一接口

创建统一的大纲加载函数，支持两种格式：

```python
def load_unified_outline(state):
    """
    统一加载大纲，支持两种格式：
    1. 新格式：bible/outline.yaml
    2. 旧格式：config 中的 novel_outline 和 volume_frameworks
    """
    # 尝试新格式
    custom = load_custom_outline(state)
    if custom:
        return custom

    # 回退到旧格式
    config = state.get('config', {})
    novel_outline = config.get('novel_outline')
    volume_frameworks = config.get('volume_frameworks')

    if novel_outline or volume_frameworks:
        return {
            'outline': novel_outline,
            'volumes': volume_frameworks
        }

    return None
```
