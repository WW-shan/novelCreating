# 🔄 AI 小说生成器 - 详细工作流程

## 📋 目录
1. [总体流程](#总体流程)
2. [步骤详解](#步骤详解)
3. [数据流转](#数据流转)
4. [文件结构](#文件结构)
5. [核心组件](#核心组件)

---

## 总体流程

```
┌─────────────────────────────────────────────────────────────┐
│                     用户操作流程                              │
└─────────────────────────────────────────────────────────────┘

1. 配置阶段
   python3 configure_novel.py
   ↓
   [交互式问答] → 生成配置文件
   ↓
   bible/novel_config_latest.yaml
   bible/novel_config_latest.json

2. 生成阶段
   ./run_novel.sh
   ↓
   启动 LangGraph 工作流
   ↓
   四层递归生成循环

3. 输出阶段
   ↓
   manuscript/[小说名]/chapter_001.md
   bible/[小说名]_world_state.json
   novel_state.db (持久化状态)
```

---

## 步骤详解

### 第一步：配置小说 (configure_novel.py)

#### 交互式配置流程：

```
┌──────────────────────────────────────────┐
│  Step 1: 选择模板                         │
│  • 赛博朋克                                │
│  • 玄幻修仙                                │
│  • 都市爱情                                │
│  • 悬疑推理                                │
│  • 武侠江湖                                │
└──────────────────────────────────────────┘
            ↓
┌──────────────────────────────────────────┐
│  Step 2: 基础信息                         │
│  • 小说标题                                │
│  • 故事梗概 (1-3句话)                      │
│  • 目标章节数 (1-100)                      │
└──────────────────────────────────────────┘
            ↓
┌──────────────────────────────────────────┐
│  Step 3: 世界观设定                       │
│  • 时代背景                                │
│  • 主要场景                                │
│  • 力量体系/特殊设定                        │
│  • 派系/组织 (可选)                         │
└──────────────────────────────────────────┘
            ↓
┌──────────────────────────────────────────┐
│  Step 4: 角色设定                         │
│  循环创建角色 (至少2个):                    │
│  • 姓名                                    │
│  • 年龄                                    │
│  • 职业/身份                                │
│  • 性格特点 (3-5个)                         │
│  • 核心目标                                │
│  • 初始位置                                │
└──────────────────────────────────────────┘
            ↓
┌──────────────────────────────────────────┐
│  Step 5: 写作风格                         │
│  • 整体风格 (严肃/幽默/黑暗/热血/浪漫)        │
│  • 叙事节奏 (快/中/慢)                      │
│  • 重点元素 (动作/对话/心理/环境/悬念)        │
└──────────────────────────────────────────┘
            ↓
┌──────────────────────────────────────────┐
│  Step 6: 差异性设定 (关键!)                │
│  • 随机性强度 (低/中/高)                    │
│    → 影响 temperature 参数                 │
│  • 伏笔策略 (保守/适中/激进)                 │
│    → 决定AI自由度                          │
│  • 角色自主性 (严格/适中/自由)               │
│    → 角色行为可变性                         │
└──────────────────────────────────────────┘
            ↓
┌──────────────────────────────────────────┐
│  Step 7: 预览和保存                       │
│  • 显示配置摘要                            │
│  • 保存为 YAML + JSON                     │
│  • 设为默认配置                            │
└──────────────────────────────────────────┘
```

#### 生成的配置文件结构：

```yaml
metadata:
  created_at: 2026-02-04T12:00:00
  version: '1.0'

novel:
  title: "小说标题"
  synopsis: "故事梗概"
  target_chapters: 20
  type: "cyberpunk"

worldbuilding:
  era: "2087年"
  setting: "霓虹闪烁的超大都市"
  power_system: "神经接口技术"
  factions: ["正派-武当派", "邪派-血魔教"]
  technology: []
  magic_system: {}
  geography: {}

characters:
  - name: "主角名"
    age: "25"
    occupation: "黑客"
    traits: ["勇敢", "聪明", "神秘"]
    goal: "揭露公司阴谋"
    location: "贫民窟"
    status: "Alive"
    relationships: {}

style:
  tone: "dark"
  style_name: "黑暗压抑"
  pace: "2"  # 快节奏
  focus_elements: ["action", "suspense"]

generation:
  temperature: 0.7          # 基础温度
  planner_temp: 0.6         # 规划温度
  writer_temp: 0.9          # 写作温度
  critic_temp: 0.3          # 评审温度
  randomness_level: "medium"
  foreshadow_strategy: "moderate"
  character_autonomy: "moderate"
  enable_plot_twists: true
  seed: null  # 每次不同
```

---

### 第二步：生成小说 (run_novel.sh → src/main.py)

#### 启动流程：

```bash
#!/bin/bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 加载环境变量
export $(cat .env | xargs)

# 3. 启动主程序
python3 src/main.py
```

#### 主程序执行流程：

```
┌──────────────────────────────────────────┐
│  main.py 启动                             │
└──────────────────────────────────────────┘
            ↓
┌──────────────────────────────────────────┐
│  1. 检查 API Key                          │
│     if not ANTHROPIC_API_KEY:             │
│         exit(1)                           │
└──────────────────────────────────────────┘
            ↓
┌──────────────────────────────────────────┐
│  2. 加载配置文件                           │
│     config = load_config()                │
│     - 读取 novel_config_latest.yaml       │
│     - 转换为 dict                          │
└──────────────────────────────────────────┘
            ↓
┌──────────────────────────────────────────┐
│  3. 构建初始状态                           │
│     initial_state = {                     │
│       'world_bible': {...},               │
│       'synopsis': "...",                  │
│       'chapters': [],                     │
│       'current_chapter_index': 1,         │
│       'config': config                    │
│     }                                     │
└──────────────────────────────────────────┘
            ↓
┌──────────────────────────────────────────┐
│  4. 构建 LangGraph 工作流                 │
│     workflow = StateGraph(NovelState)     │
│     workflow.add_node("planner", ...)     │
│     workflow.add_node("writer", ...)      │
│     workflow.add_node("critic", ...)      │
│     workflow.add_node("memory", ...)      │
└──────────────────────────────────────────┘
            ↓
┌──────────────────────────────────────────┐
│  5. 配置边和循环逻辑                       │
│     planner → writer → critic → memory    │
│                                           │
│     if target_chapters > 1:               │
│         memory → [条件判断] → planner/END  │
│     else:                                 │
│         memory → END                      │
└──────────────────────────────────────────┘
            ↓
┌──────────────────────────────────────────┐
│  6. 编译工作流 + 持久化                    │
│     memory = SqliteSaver(novel_state.db)  │
│     app = workflow.compile(memory)        │
└──────────────────────────────────────────┘
            ↓
┌──────────────────────────────────────────┐
│  7. 启动流式执行                           │
│     for step in app.stream(...):          │
│         处理每个节点输出                    │
│         保存章节文件                        │
└──────────────────────────────────────────┘
```

---

### 第三步：四层递归生成循环

#### 完整循环示意图：

```
                  ┌─────────────────────┐
                  │   START (初始状态)   │
                  │  • world_bible      │
                  │  • synopsis         │
                  │  • config           │
                  └─────────┬───────────┘
                            ↓
    ╔═══════════════════════════════════════════════════╗
    ║              CHAPTER GENERATION LOOP               ║
    ╚═══════════════════════════════════════════════════╝
                            ↓
    ┌────────────────────────────────────────────────────┐
    │  NODE 1: PLANNER (Sonnet 4.5)                      │
    │  温度: 0.7 | 超时: 120s | 重试: 2次                  │
    │                                                    │
    │  输入:                                              │
    │  • world_bible (角色/世界观/伏笔)                    │
    │  • synopsis (总体梗概)                              │
    │  • previous_chapters (已生成章节)                   │
    │  • current_chapter_index                           │
    │                                                    │
    │  任务:                                              │
    │  1. 分析当前故事进度                                 │
    │  2. 生成本章节大纲 (Beats)                          │
    │  3. 包含 3-5 个场景/冲突点                          │
    │  4. 考虑伏笔铺设和角色发展                           │
    │                                                    │
    │  输出:                                              │
    │  • current_beats: "场景1: ...\\n场景2: ..."         │
    └────────────────────┬───────────────────────────────┘
                         ↓
    ┌────────────────────────────────────────────────────┐
    │  NODE 2: WRITER (Sonnet 4.5)                       │
    │  温度: 0.8 | 超时: 180s | 重试: 2次                  │
    │                                                    │
    │  输入:                                              │
    │  • current_beats (本章大纲)                         │
    │  • world_bible                                     │
    │  • style (写作风格配置)                             │
    │                                                    │
    │  任务:                                              │
    │  1. 根据大纲创作正文                                 │
    │  2. 至少 2000 字                                    │
    │  3. 应用风格设定 (幽默/黑暗/热血...)                  │
    │  4. 包含对话、动作、心理描写                          │
    │  5. 体现角色自主性设定                               │
    │                                                    │
    │  输出:                                              │
    │  • draft: "第X章正文..."                            │
    └────────────────────┬───────────────────────────────┘
                         ↓
    ┌────────────────────────────────────────────────────┐
    │  NODE 3: CRITIC (Sonnet 4.5)                       │
    │  温度: 0.2 | 超时: 120s | 重试: 2次                  │
    │                                                    │
    │  输入:                                              │
    │  • draft (初稿)                                     │
    │  • world_bible                                     │
    │  • synopsis                                        │
    │                                                    │
    │  任务:                                              │
    │  1. 检查逻辑一致性                                   │
    │  2. 验证角色行为合理性                               │
    │  3. 确认设定不矛盾                                   │
    │  4. 评估情节连贯性                                   │
    │  5. 提供改进建议                                     │
    │                                                    │
    │  输出:                                              │
    │  • feedback: "逻辑评审..."                          │
    │  • approved: true/false                            │
    └────────────────────┬───────────────────────────────┘
                         ↓
    ┌────────────────────────────────────────────────────┐
    │  NODE 4: MEMORY (Sonnet 4.5)                       │
    │  温度: 0.1 | 超时: 120s | 重试: 2次                  │
    │                                                    │
    │  输入:                                              │
    │  • draft (最终稿)                                   │
    │  • world_bible (当前状态)                           │
    │  • feedback (评审意见)                              │
    │                                                    │
    │  任务:                                              │
    │  1. 提取章节中的事件                                 │
    │  2. 更新角色状态 (位置/关系/目标)                     │
    │  3. 记录新伏笔                                       │
    │  4. 解决已揭示的伏笔                                 │
    │  5. 更新世界状态                                     │
    │                                                    │
    │  输出:                                              │
    │  • updated world_bible                             │
    │  • current_chapter_index += 1                      │
    └────────────────────┬───────────────────────────────┘
                         ↓
              ┌──────────┴──────────┐
              │  条件判断              │
              │  chapter < target?   │
              └──────────┬───────────┘
                 YES ↓   │ NO
                     ↓   └────────→ END
                  [循环回 PLANNER]
```

#### 节点间数据传递：

```python
# 状态对象结构 (NovelState)
{
    # 核心数据
    "world_bible": {
        "characters": {
            "张三": {
                "age": 25,
                "occupation": "黑客",
                "traits": ["勇敢", "聪明"],
                "goal": "揭露阴谋",
                "location": "贫民窟",
                "status": "Alive",
                "relationships": {}
            }
        },
        "worldbuilding": {...},
        "plot_tracks": [
            {
                "id": 1,
                "description": "主线...",
                "foreshadowed": True,
                "resolved": False
            }
        ]
    },

    # 生成状态
    "synopsis": "总体故事梗概",
    "chapters": [
        {
            "index": 1,
            "beats": "场景1...",
            "draft": "第一章正文...",
            "feedback": "评审意见..."
        }
    ],

    # 当前状态
    "current_beats": "当前章节大纲",
    "draft": "当前章节正文",
    "feedback": "当前评审",
    "current_chapter_index": 2,

    # 配置
    "config": {...},  # 完整配置对象
    "iteration": 5
}
```

---

## 数据流转

### 文件生成流程：

```
配置阶段:
  configure_novel.py
  ↓
  bible/novel_config_latest.yaml  ← 主配置文件
  bible/novel_config_latest.json  ← JSON格式备份

生成阶段:
  src/main.py
  ↓
  novel_state.db  ← SQLite持久化 (自动保存进度)
  ↓
  [每章生成完成后]
  ↓
  manuscript/[小说名]/chapter_001.md
  manuscript/[小说名]/chapter_002.md
  ...
  ↓
  [全部完成后]
  ↓
  bible/[小说名]_world_state.json  ← 最终世界状态
```

### 持久化机制：

```python
# 使用 LangGraph 的 SqliteSaver
memory = SqliteSaver(conn)
app = workflow.compile(checkpointer=memory)

# 自动保存特性:
# 1. 每个节点执行后自动保存状态
# 2. 断点续传: 重新运行自动从上次位置继续
# 3. thread_id: 根据小说标题识别进度
config = {"configurable": {"thread_id": f"novel_{title}"}}
```

---

## 文件结构

```
/project/novel/
│
├── 📁 src/                      # 核心代码
│   ├── main.py                  # 主程序入口 (400+ 行)
│   │   • load_config()          # 加载配置
│   │   • build_graph()          # 构建工作流
│   │   • save_chapter_to_file() # 保存章节
│   │   • save_world_bible()     # 保存世界状态
│   │
│   ├── state.py                 # 状态定义 (TypedDict)
│   │   • NovelState             # 主状态类型
│   │
│   └── 📁 nodes/                # 四个智能节点
│       ├── planner.py           # 大纲规划节点
│       │   • planner_node()     # Sonnet 4.5, temp=0.6
│       │
│       ├── writer.py            # 正文写作节点
│       │   • writer_node()      # Opus 4.5, temp=0.9
│       │
│       ├── critic.py            # 逻辑评审节点
│       │   • critic_node()      # Sonnet 4.5, temp=0.3
│       │
│       └── memory.py            # 记忆更新节点
│           • memory_update_node() # Sonnet 4.5, temp=0.5
│
├── 📁 bible/                    # 配置和世界状态
│   ├── novel_config_latest.yaml # 当前配置 (自动生成)
│   ├── novel_config_latest.json # JSON格式
│   ├── novel_config_[标题]_[时间].yaml  # 历史配置
│   └── [小说名]_world_state.json # 最终世界状态
│
├── 📁 manuscript/               # 生成的小说
│   └── [小说名]/
│       ├── chapter_001.md
│       ├── chapter_002.md
│       └── ...
│
├── 📁 logs/                     # 日志文件 (预留)
│
├── 📄 configure_novel.py        # 配置向导 (450+ 行)
├── 📄 run_novel.sh              # 生成脚本
├── 📄 test_api.sh               # API 测试脚本
├── 📄 start.sh                  # 完整启动脚本
│
├── 📄 novel_state.db            # SQLite 持久化数据库
│   novel_state.db-shm           # (共享内存)
│   novel_state.db-wal           # (写入日志)
│
├── 📄 .env                      # 环境变量 (API Key)
├── 📄 requirements.txt          # Python 依赖
│
└── 📁 venv/                     # Python 虚拟环境
```

---

## 核心组件

### 1. LangGraph 工作流引擎

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

# 特性:
# • 有向无环图 (DAG) 执行
# • 自动状态管理
# • 断点续传
# • 条件路由
# • 流式输出
```

### 2. Claude 4.5 统一模型系统

```
Sonnet 4.5 (claude-sonnet-4-5-20250929) - 所有节点
  • Planner: 温度 0.7, 超时 120s, 重试 2次
  • Writer: 温度 0.8, 超时 180s, 重试 2次
  • Critic: 温度 0.2, 超时 120s, 重试 2次
  • Memory: 温度 0.1, 超时 120s, 重试 2次

优势:
  • 速度快，避免超时
  • 成本更低
  • 稳定性更好
  • 统一模型便于调试
```

### 3. 状态持久化系统

```python
SqliteSaver
  • 自动检查点 (每个节点后)
  • Thread-based 进度跟踪
  • 断点续传
  • 支持并发
```

### 4. 差异性保证机制

```yaml
# 每次生成都不同的原因:

1. 随机种子
   seed: null  # 每次运行使用不同的随机数种子

2. 温度参数
   randomness_level: medium  → temperature: 0.7
   randomness_level: high    → temperature: 0.9

3. AI 策略
   foreshadow_strategy: aggressive  # AI自由创造伏笔
   character_autonomy: free         # 角色自主决策

4. 概率性生成
   AI 本质上是概率模型，即使相同输入也会产生不同输出
```

---

## 使用示例

### 完整工作流示例：

```bash
# ====== 第一次使用 ======

# 1. 配置小说
python3 configure_novel.py
# 选择: 2 (玄幻修仙)
# 标题: 逆天传说
# 梗概: 废柴少年获得神秘传承，踏上逆天修炼之路
# 章节: 20
# 角色: 李云帆 (18岁, 废柴弟子)
# 风格: 热血激昂
# 随机性: 中
# ... 完成配置

# 2. 生成小说
./run_novel.sh
# [等待生成...]
# ✅ 成功生成 20 章

# 3. 查看结果
ls manuscript/逆天传说/
# chapter_001.md
# chapter_002.md
# ...

# ====== 修改设定后重新生成 ======

# 4. 编辑配置 (可选)
vim bible/novel_config_latest.yaml
# 修改: randomness_level: high  (更高创意)

# 5. 再次生成 (产生完全不同的故事！)
./run_novel.sh
# 即使设定相同，情节发展也会不同

# ====== 创建全新小说 ======

# 6. 重新配置
python3 configure_novel.py
# 选择: 1 (赛博朋克)
# ... 全新设定

# 7. 生成新小说
./run_novel.sh
```

---

## 常见问题

### Q: 生成中断怎么办？
A: 重新运行 `./run_novel.sh`，系统会从断点继续（通过 novel_state.db）

### Q: 如何确保每次生成都不同？
A: 系统默认 `seed: null`，每次运行使用不同随机种子

### Q: 如何调整章节长度？
A: 编辑 `src/nodes/writer.py`，修改 "Write at least 2000 words" 提示

### Q: 如何修改已有配置？
A: 直接编辑 `bible/novel_config_latest.yaml`

### Q: 如何查看生成进度？
A: 终端会实时显示每个节点的执行状态

### Q: 如何删除旧项目？
A: 删除 `manuscript/[小说名]/` 和 `bible/[小说名]_*` 文件

---

## 技术亮点

1. **双模型协作**: Opus 创作 + Sonnet 把关
2. **自动持久化**: 断点续传，永不丢失进度
3. **差异性保证**: 配置化随机性控制
4. **模块化设计**: 四个独立节点，易于扩展
5. **交互式配置**: 零代码配置小说设定
6. **流式输出**: 实时查看生成进度

---

**最后更新**: 2026-02-04
**版本**: 1.0
**作者**: AI Novel Generator Team
