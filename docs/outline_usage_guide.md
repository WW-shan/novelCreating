# 📖 大纲系统使用指南

## 目录
1. [快速开始](#快速开始)
2. [三种工作流程](#三种工作流程)
3. [大纲格式说明](#大纲格式说明)
4. [常见问题](#常见问题)

---

## 快速开始

### 推荐工作流（两阶段）

```bash
# 阶段 1：快速创建项目
./novel.sh new
# 选择简易模式，只输入标题和梗概

# 阶段 2：AI 生成详细大纲（可选但推荐）
./novel.sh outline
# AI 自动生成总纲和卷纲，审查后保存

# 阶段 3：开始生成小说
./novel.sh generate
```

---

## 三种工作流程

### 工作流 A：快速启动（AI 全自动）

**适合**：想快速开始，对大纲没有明确想法

```bash
# 1. 创建项目（简易模式）
./novel.sh new
# 输入：标题、类型、梗概、角色

# 2. AI 生成大纲
./novel.sh outline
# AI 自动生成总纲（主线目标、冲突、成长弧）
# AI 自动生成卷纲（每卷 25 章，包含关键事件）

# 3. 开始生成
./novel.sh generate
```

**优点**：
- ✅ 最快速
- ✅ AI 辅助规划
- ✅ 自动生成里程碑

**缺点**：
- ❌ 灵活性较低
- ❌ 每卷固定 25 章

---

### 工作流 B：完全自定义（手动控制）

**适合**：对故事有明确构思，想完全控制大纲

```bash
# 1. 使用高级配置工具
python3 configure_novel_advanced.py

# 2. 选择"完整大纲"模式
# 手动输入：
#   - 总纲（主目标、冲突、成长线）
#   - 阶段划分（3-15 阶段，自定义章节范围）
#   - 卷纲（自定义每卷章节数、关键事件）

# 3. 开始生成
./novel.sh generate
```

**优点**：
- ✅ 完全可控
- ✅ 灵活的章节分配
- ✅ 精确的阶段规划

**缺点**：
- ❌ 配置时间较长
- ❌ 需要预先规划

---

### 工作流 C：混合模式（推荐）

**适合**：想要 AI 辅助，但也想手动调整

```bash
# 1. 快速创建项目
./novel.sh new

# 2. AI 生成初始大纲
./novel.sh outline

# 3. 手动编辑大纲文件
# 编辑 projects/<项目名>/config.yaml
# 修改 novel_outline 和 volume_frameworks 字段

# 4. 开始生成
./novel.sh generate
```

**优点**：
- ✅ 平衡速度和控制
- ✅ AI 提供基础，人工优化
- ✅ 灵活调整

---

## 大纲格式说明

### 格式 1：旧格式（在配置文件中）

保存在 `projects/<项目名>/config.yaml`：

```yaml
novel_outline:
  main_goal: "主角要完成的终极目标"
  main_conflict: "贯穿全文的核心矛盾"
  protagonist_arc: "主角从开始到结束的成长变化"
  key_milestones:
    - milestone: "第一个重要节点"
      target_chapter: 20
    - milestone: "第二个重要节点"
      target_chapter: 50
    - milestone: "最终高潮"
      target_chapter: 100

volume_frameworks:
  - title: "第一卷：起始之章"
    chapters: "1-25"
    core_goal: "本卷要达成的目标"
    key_events:
      - "主角获得系统"
      - "第一次战斗"
      - "结识重要角色"
    ending_state: "主角完成新手阶段"
    foreshadowing:
      - "神秘组织的线索"
      - "主角真实身世的暗示"

  - title: "第二卷：成长之路"
    chapters: "26-50"
    core_goal: "提升实力，面对更强敌人"
    key_events:
      - "突破境界"
      - "击败强敌"
      - "揭示部分真相"
    ending_state: "主角成为高手"
    foreshadowing:
      - "更大危机的预兆"
```

**生成方式**：`./novel.sh outline`

---

### 格式 2：新格式（独立文件）

保存在 `projects/<项目名>/bible/outline.yaml`：

```yaml
outline:
  synopsis: "简短的故事梗概"
  main_goal: "主线目标"
  main_conflict: "主线冲突"
  protagonist_arc: "主角成长线"
  phases:
    - name: "开局阶段"
      goal: "建立世界观和角色"
      chapters: "1-20"
    - name: "发展阶段"
      goal: "推进主线冲突"
      chapters: "21-60"
    - name: "高潮阶段"
      goal: "解决核心矛盾"
      chapters: "61-100"

volumes:
  - volume: 1
    title: "第一卷"
    chapters: "1-30"
    core_goal: "核心目标"
    key_events: ["事件1", "事件2", "事件3"]
    foreshadowing: ["伏笔1", "伏笔2"]
    ending_state: "结尾状态"

  - volume: 2
    title: "第二卷"
    chapters: "31-60"
    core_goal: "核心目标"
    key_events: ["事件1", "事件2"]
    foreshadowing: ["伏笔1"]
    ending_state: "结尾状态"
```

**生成方式**：`python3 configure_novel_advanced.py`（选择"完整大纲"模式）

---

## Planner 如何使用大纲

### 自动检测和加载

```python
# Planner 会自动：
1. 优先查找 projects/<id>/bible/outline.yaml
2. 如果没有，查找 config 中的 novel_outline
3. 根据当前章节号，找到对应的阶段/卷
4. 将大纲信息添加到规划 prompt 中
```

### 大纲指引示例

当生成第 15 章时，planner 会添加：

```
【当前阶段】第15章位于：开局阶段
阶段目标: 建立世界观和角色

【当前卷】第1卷：起始之章
卷核心目标: 主角获得系统并适应新世界
关键事件: 主角获得系统, 第一次战斗, 结识重要角色

【总纲】
主目标: 成为最强者并揭开世界真相
主线冲突: 主角与暗黑势力的对抗
```

---

## 常见问题

### Q1: 两种格式可以同时存在吗？

**可以**。Planner 会优先使用 `outline.yaml`，如果不存在才使用配置文件中的字段。

---

### Q2: 已经开始生成了，还能修改大纲吗？

**可以**。直接编辑大纲文件，下次生成章节时会使用新大纲。

---

### Q3: 不想用大纲可以吗？

**可以**。如果两种格式都不存在，planner 会纯靠梗概和历史章节生成，完全由 AI 自由发挥。

---

### Q4: 卷纲必须每卷 25 章吗？

- **旧格式**（AI 生成）：固定 25 章
- **新格式**（手动配置）：可以自定义，例如 "1-30", "31-55"

---

### Q5: 如何查看当前项目的大纲？

```bash
# 方法 1：运行 outline 工具
./novel.sh outline
# 选择"查看现有总纲和卷纲"

# 方法 2：直接查看文件
cat projects/<项目名>/config.yaml | grep -A 50 "novel_outline"
# 或
cat projects/<项目名>/bible/outline.yaml
```

---

### Q6: 可以导入已有的大纲吗？

**即将支持**。`configure_novel_advanced.py` 中有"导入大纲"选项，但目前还在开发中。

暂时可以手动创建 `outline.yaml` 文件。

---

## 推荐配置流程

### 短篇小说（10-50 章）

```bash
./novel.sh new              # 简易模式
./novel.sh generate         # 不需要大纲，直接生成
```

---

### 中篇小说（50-200 章）

```bash
./novel.sh new              # 简易模式
./novel.sh outline          # AI 生成大纲
# 手动编辑 config.yaml 调整卷纲
./novel.sh generate
```

---

### 长篇小说（200-500 章）

```bash
python3 configure_novel_advanced.py  # 完整大纲模式
# 手动规划 8-15 个阶段
# 手动规划卷纲（每卷 20-30 章）
./novel.sh generate
```

---

## 总结

| 工作流 | 速度 | 控制 | 适合场景 |
|--------|------|------|----------|
| **快速启动（A）** | ⚡⚡⚡ | ⭐ | 快速测试、短篇小说 |
| **完全自定义（B）** | ⚡ | ⭐⭐⭐ | 长篇小说、精确控制 |
| **混合模式（C）** | ⚡⚡ | ⭐⭐ | 中长篇小说、推荐！ |

**推荐**：大部分情况使用混合模式（C），既省时又灵活！
