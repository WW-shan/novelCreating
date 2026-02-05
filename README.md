# 📚 AI 小说生成器

基于 Claude 4.5 的自主小说创作系统

**支持**: 1-200+ 章，自动分层记忆管理

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API

编辑 `.env` 文件：
```bash
ANTHROPIC_API_KEY=你的API密钥
ANTHROPIC_BASE_URL=https://claud.bfund.pro/api
```

### 3. 使用统一脚本

```bash
./novel.sh help        # 查看所有命令
./novel.sh new         # 创建新小说配置
./novel.sh generate    # 开始生成小说
```

---

## 📖 主要命令

| 命令 | 说明 |
|------|------|
| `./novel.sh generate` | 生成小说（使用当前配置） |
| `./novel.sh config` | 查看当前配置 |
| `./novel.sh new` | 创建新的小说配置 |
| `./novel.sh switch` | 切换小说配置 |
| `./novel.sh test` | 运行所有测试 |
| `./novel.sh clean` | 清理生成状态 |
| `./novel.sh status` | 查看系统状态 |

---

## 🎯 完整工作流

### 创建第一本小说

```bash
# 1. 创建配置
./novel.sh new
# 按提示输入：标题、类型、角色、世界观...

# 2. 生成小说
./novel.sh generate

# 3. 查看结果
ls manuscript/你的小说名/
```

### 创建多本小说

```bash
# 第一本：末日小说
./novel.sh new
# 配置完成...

# 第二本：修仙小说
./novel.sh new
# 配置完成...

# 切换并生成
./novel.sh switch      # 选择要生成的小说
./novel.sh generate    # 开始生成
```

---

## 🎨 系统特性

### 自动模式切换

- **1-49 章**: 简单记忆模式
- **50-200+ 章**: 自动启用分层记忆（内存压缩 80%+）

### 智能工作流

- **短篇**: 4 节点（Planner → Writer → Critic → Memory）
- **长篇**: 6 节点（+ Volume Planner + Volume Review）

### 质量保证

- 分段生成避免超时
- 自动修订循环（最多 2 次）
- 5 维度质量评审
- 智能伏笔管理

---

## 📁 目录结构

```
novel/
├── novel.sh              # ⭐ 统一管理脚本
├── configure_novel.py    # 配置向导
├── bible/                # 配置目录
│   ├── novel_config_latest.yaml  # 当前配置
│   ├── novel_config_末日真理.yaml
│   └── novel_config_修仙传奇.yaml
├── manuscript/           # 生成的小说
│   ├── 末日真理/
│   │   ├── chapter_001.md
│   │   └── ...
│   └── 修仙传奇/
│       └── ...
├── src/                  # 源代码
├── test_*.sh             # 测试脚本
└── docs/                 # 文档
```

---

## 🧪 测试

```bash
# 运行所有测试
./novel.sh test

# 单独测试
./novel.sh test-api       # API 连接测试
./novel.sh test-flow      # 完整流程测试（生成1章）
```

---

## 💡 常见问题

### Q: 如何重新开始生成？

```bash
./novel.sh clean
./novel.sh generate
```

### Q: 如何切换到其他小说？

```bash
./novel.sh switch
```

### Q: 如何查看当前配置？

```bash
./novel.sh config
```

### Q: 生成中断了怎么办？

已生成的章节保存在 `manuscript/小说名/`，不会丢失。
下次运行前执行 `./novel.sh clean` 重新开始。

---

## 📚 文档

- **README.md** (本文件) - 快速开始
- **QUICKSTART.md** - 详细快速开始指南
- **USAGE.md** - 使用手册
- **CAPABILITIES.md** - 系统能力说明
- **HOW_TO_MAKE_DIFFERENT_NOVELS.md** - 创作技巧
- **archive/** - 详细技术文档

---

## 🎯 系统能力

| 指标 | 支持范围 |
|------|----------|
| 章节数 | 1-200+ 章 |
| 自动化 | 完全自动 |
| 内存管理 | 分层记忆（压缩 80%+） |
| 成功率 | 95%+ |
| 配置 | 零配置（自动检测） |

---

## 🚀 版本

**v4.1** - 长篇系统完全集成
- ✅ 自动检测和切换（50 章阈值）
- ✅ 分层记忆（内存压缩 80%+）
- ✅ 自动卷管理（每 25 章）
- ✅ 零配置，一键生成

---

**快速命令**:
```bash
./novel.sh new       # 创建配置
./novel.sh generate  # 生成小说
```

需要帮助? 运行 `./novel.sh help`
