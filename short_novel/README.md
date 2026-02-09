# 短篇小说生成器

基于套路模板的短篇小说生成系统，目标平台：番茄小说。

## 快速开始

```bash
# 进入项目目录
cd short_novel

# 运行启动脚本
./run.sh

# 或直接运行
python3 generate.py   # 生成新小说
python3 analyze.py    # 分析小说提取模板
```

## 环境要求

- Python 3.10+
- Anthropic API Key

### API 配置

**方式一：使用 .env 文件（推荐）**

在项目根目录创建 `.env` 文件：

```
ANTHROPIC_API_KEY=your-api-key
ANTHROPIC_BASE_URL=https://your-proxy.com/api
ANTHROPIC_MODEL=claude-opus-4-6
```

**方式二：使用环境变量**

```bash
# 必需：设置 API Key
export ANTHROPIC_API_KEY="your-api-key"

# 可选：使用 API 中转/代理
export ANTHROPIC_BASE_URL="https://your-proxy.com/v1"

# 可选：使用其他模型（默认 claude-opus-4-6）
export ANTHROPIC_MODEL="claude-sonnet-4-5-20250929"
```

支持的配置项：
- `ANTHROPIC_API_KEY` - API密钥（必需）
- `ANTHROPIC_BASE_URL` - 自定义API地址，用于代理/中转（可选）
- `ANTHROPIC_MODEL` - 模型名称（可选，默认 claude-opus-4-6）

## 功能说明

### 1. 模板分析 (analyze.py)

从已有的成功小说中提取可复用的套路模板：

1. 粘贴小说文本（或输入URL）
2. AI进行四轮分析：结构→情绪→技巧→抽象
3. 生成五层模板YAML
4. 保存到模板库

### 2. 小说生成 (generate.py)

基于模板生成新小说：

1. 选择模板（男频/女频）
2. AI生成角色和设定
3. 生成章节大纲
4. 逐章生成，用户审核每章
5. 输出完整小说

### 审核选项

每生成一章后，可以选择：
- **确认** - 继续下一章
- **重新生成** - 从头生成此章
- **提供反馈修改** - 根据你的意见修改
- **手动编辑** - 直接编辑文件后继续
- **保存退出** - 保存进度，下次继续

## 模板结构

五层模板系统：

1. **读者心理契约** - 核心幻想、阅读动机
2. **角色功能系统** - 主角、反派、女主的设计
3. **情节节奏引擎** - 节拍、情绪曲线、微节奏
4. **写作风格控制** - 句式、禁忌、技巧
5. **章末钩子系统** - 钩子类型、使用规则

## 目录结构

```
short_novel/
├── analyze.py          # 模板分析入口
├── generate.py         # 小说生成入口
├── run.sh              # 快速启动
├── core/               # 核心模块
│   ├── ai_client.py    # API封装
│   ├── analyzer.py     # 分析逻辑
│   ├── generator.py    # 生成逻辑
│   ├── template_manager.py
│   ├── scraper.py      # URL抓取
│   └── prompts/        # 提示词
├── templates/          # 模板库
│   ├── 男频/
│   └── 女频/
└── stories/            # 生成的小说
```

## 内置模板

- **男频**: 赘婿逆袭
- **女频**: 闪婚总裁

## 成本估算

使用 Claude Opus 4.6：
- 分析1篇小说：~$1-3
- 生成10章小说：~$3-5
- 含修改总计：~$5-10/篇
