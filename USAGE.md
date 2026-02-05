# 使用指南

## 快速开始

### 1. 配置 API Key

首先，创建 `.env` 文件并添加你的 Anthropic API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件，添加你的 API Key：

```
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### 2. 运行小说生成器

使用以下命令启动程序：

```bash
./run_novel.sh
```

程序会自动：
1. 加载你的 API Key
2. 初始化 LangGraph 工作流
3. 生成第一章小说
4. 保存生成的内容到文件

### 3. 查看生成的内容

生成完成后，你可以在以下位置找到结果：

- **小说章节**: `./manuscript/chapter_001.md`
- **世界状态**: `./bible/world_state.json`
- **数据库**: `./novel_state.db` (持久化状态)

## 自定义你的小说

### 修改故事设定

编辑 `src/main.py` 文件中的 `initial_state` 部分：

```python
initial_state = {
    "world_bible": {
        "characters": {
            "你的角色名": {
                "age": 25,
                "status": "Alive",
                "occupation": "职业",
                "location": "位置",
                "traits": ["特征1", "特征2"],
                "goal": "目标"
            }
        },
        "worldbuilding": {
            "era": "时代背景",
            "setting": "场景描述",
            "power_system": "力量体系",
            # ... 更多设定
        }
    },
    "synopsis": "你的小说梗概",
    # ...
}
```

### 生成多个章节

如果你想连续生成多个章节，可以修改 `src/main.py`:

```python
# 找到这一行 (第33行左右):
workflow.add_edge("memory", END)  # End after one cycle

# 替换为:
workflow.add_edge("memory", "planner")  # Continuous generation
```

然后添加章节数量限制：

```python
# 在 initial_state 中添加:
"max_chapters": 10,  # 生成10章
```

## 工作流程详解

系统按照以下步骤生成小说：

```
1. PLANNER (Claude Sonnet 4.5)
   ↓ 生成章节大纲(Beats)

2. WRITER (Claude Opus 4.5)
   ↓ 根据大纲创作正文(2000+字)

3. CRITIC (Claude Sonnet 4.5)
   ↓ 检查逻辑一致性

4. MEMORY (Claude Sonnet 4.5)
   ↓ 更新世界状态

→ 循环 (如果启用多章节模式)
```

## 文件结构说明

```
/project/novel/
├── src/
│   ├── main.py           # 主程序入口
│   ├── state.py          # 状态定义
│   └── nodes/            # 各个节点实现
│       ├── planner.py    # 情节规划节点
│       ├── writer.py     # 写作节点
│       ├── critic.py     # 评论节点
│       └── memory.py     # 记忆更新节点
├── manuscript/           # 生成的章节存储
├── bible/               # 世界设定存储
├── logs/                # 日志文件
├── venv/                # Python 虚拟环境
├── .env                 # API Key 配置
├── run_novel.sh        # 运行脚本
└── README.md           # 项目说明
```

## 常见问题

### Q: 如何调整生成的字数？

A: 编辑 `src/nodes/writer.py`，修改提示词中的字数要求：

```python
# 找到这一行:
- Write at least 2000 words.

# 改为:
- Write at least 3000 words.
```

### Q: 如何改变写作风格？

A: 编辑 `src/nodes/writer.py` 中的 `prompt`，添加风格指导：

```python
INSTRUCTIONS:
- Write in a noir detective style.
- Use short, punchy sentences.
- Focus on atmosphere and mood.
```

### Q: 如何查看 AI 的思考过程？

A: 程序运行时会在终端显示每个节点的执行状态和摘要信息。

### Q: 生成失败了怎么办？

A: 检查以下几点：
1. API Key 是否正确设置
2. 网络连接是否正常
3. API 配额是否充足
4. 查看错误信息并根据提示解决

## 高级用法

### 1. 从检查点恢复

如果生成中断，系统会自动保存状态到 `novel_state.db`。重新运行即可继续。

### 2. 修改模型温度

编辑各个节点文件，调整 `temperature` 参数：

```python
# 更保守的生成 (更一致)
llm = ChatAnthropic(model="claude-sonnet-4-5-20250929", temperature=0.3)

# 更有创意的生成
llm = ChatAnthropic(model="claude-opus-4-5-20251101", temperature=1.0)
```

### 3. 批量生成

创建一个循环脚本：

```bash
#!/bin/bash
for i in {1..10}
do
    echo "Generating chapter $i..."
    ./run_novel.sh
done
```

## 技术支持

如遇问题，请检查：
- Python 版本 >= 3.10
- 所有依赖已正确安装 (`pip install -r requirements.txt`)
- API Key 有效且有足够配额
