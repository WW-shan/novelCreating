# 🎭 AI Novel Generator - 200+ Chapter Novel Generation System

基于 Claude Sonnet 4.5 和 LangGraph 的智能长篇小说生成系统，支持生成 200+ 章节的连贯长篇小说。

## ✨ 核心特性

### 📚 多项目管理 (NEW!)
- **独立项目空间**: 每个小说拥有独立的配置、数据库、文件目录
- **智能项目切换**: 轻松在多个小说项目间切换
- **进度永久保存**: 每个项目的进度独立保存，互不干扰
- **项目管理工具**: 可视化管理所有小说项目

### 🧠 智能记忆系统
- **分层记忆系统**: 自动管理热记忆（当前卷）和冷记忆（历史摘要）
- **卷压缩机制**: 每 25 章自动压缩，内存优化 87.5%
- **伏笔智能管理**: 自动追踪和揭示剧情伏笔
- **角色状态追踪**: 自动记录和演化角色发展

### ⚙️ 创作控制
- **质量控制**: AI Critic 自动审查章节质量
- **断点续写**: 支持中断后从任意章节继续生成
- **番茄小说风格**: 针对网文平台优化（快节奏、爽点密集）

## 🚀 快速开始

### 1. 环境配置

```bash
# 克隆项目
git clone https://github.com/WW-shan/novelCreating.git
cd novelCreating

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置 API Key
cp .env.example .env
# 编辑 .env 文件，填入你的 ANTHROPIC_API_KEY
```

### 2. 创建新项目

```bash
# 运行配置向导
python3 configure_novel.py
```

向导会引导你：
- 输入小说标题、类型、章节数
- 配置角色、世界观、写作风格
- 自动创建项目目录结构

### 3. 生成章节

```bash
# 开始生成
python3 main.py
```

系统会：
- 自动检测当前项目
- 支持断点续传
- 实时保存章节到项目目录

### 4. 管理项目

```bash
# 启动项目管理器
python3 manage_projects.py
```

功能：
- 📋 查看所有项目列表
- 🔄 切换当前项目
- 🗑️ 删除不需要的项目
- 📊 查看项目详细信息
```

## 📁 项目结构

```
novelCreating/
├── src/
│   ├── main.py              # 主程序入口
│   ├── state.py             # 状态定义
│   ├── nodes/               # LangGraph 节点
│   │   ├── planner.py       # 场景规划
│   │   ├── writer.py        # 章节写作
│   │   ├── critic.py        # 质量审查
│   │   ├── memory.py        # 记忆管理
│   │   └── volume_review.py # 卷审查
│   ├── memory/              # 记忆系统
│   │   └── layered_memory.py
│   └── utils/               # 工具函数
│       └── plot_manager.py  # 伏笔管理
├── configs/                 # 小说配置文件
├── outputs/                 # 生成的小说
├── novel.sh                 # 启动脚本
└── requirements.txt         # 依赖列表
```

## 🎯 生成流程

```
配置 → Planner(规划场景) → Writer(撰写) → Critic(审查)
  ↓                                              ↓
Memory(更新记忆) ← 通过 ←←←←←←←←←←←←←←←←←←←←←
  ↓
每25章 → Volume Compression(卷压缩) → Volume Review(卷审查)
  ↓
继续下一章...
```

## 🛠️ 配置说明

编辑 `configs/your_novel.json`:

```json
{
  "title": "你的小说标题",
  "genre": "玄幻/现代/科幻等",
  "synopsis": "小说梗概...",
  "generation": {
    "total_chapters": 200,
    "chapters_per_volume": 25,
    "target_word_count": 1500
  }
}
```

## 🐛 已修复问题

本系统已经过 3 轮 Ralph Loop 系统性调试，修复了 20+ 个 Bug：

- ✅ 状态污染问题（深拷贝）
- ✅ 记忆同步问题
- ✅ 类型不匹配问题
- ✅ JSON 解析失败
- ✅ 卷压缩触发问题
- ✅ 伏笔检测逻辑
- ✅ 容量限制管理

详细修复记录见提交历史。

## 📊 系统性能

- **短篇模式** (< 50 章): 完整记忆，每章约 2s 规划
- **长篇模式** (≥ 50 章): 分层记忆，内存占用减少 87.5%
- **生成速度**: ~30-60s/章 (取决于 API 响应)
- **质量控制**: 自动重试机制，确保章节连贯性

## 🔧 技术栈

- **LangChain**: 0.3+
- **LangGraph**: StateGraph 工作流
- **Claude API**: Sonnet 4.5 (claude-sonnet-4-5-20250929)
- **Python**: 3.10+

## 📝 使用建议

1. **API 成本**: 200 章小说约消耗 $20-40 (取决于配置)
2. **生成时间**: 完整 200 章约需 3-5 小时
3. **中断恢复**: 使用 SqliteSaver 自动保存检查点
4. **质量优化**: 调整 `target_word_count` 和 Critic 参数

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 License

MIT License

## 👤 作者

WW-shan

---

⭐ 如果这个项目对你有帮助，欢迎 Star！
