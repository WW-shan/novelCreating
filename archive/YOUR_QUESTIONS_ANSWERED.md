# 📚 您的问题解答 - 配置和切换指南

## ❓ 您的问题

1. **配置是怎么样的？**
2. **如果想同时配置几本不同的设定要怎么切换？**

---

## ✅ 答案 1：您当前的配置

### 当前激活配置

**文件位置**: `bible/novel_config_latest.yaml`

**小说详情**:

```
标题: 末日真理：从收割生存点开始
类型: mystery（悬疑）
目标章节: 1 章

梗概:
在规则扭曲的末世无限流背景，男主陆沉是极度理性的利己主义者，
拥有能推演死局概率的"因果模拟"能力，文风基调严肃冷峻，
核心看点在于主角如何摒弃感性、利用规则漏洞与人性博弈，
在信息不对称的悬疑副本中实现个人利益最大化。

主要角色:
1. 陆沉 (26岁) - 心理医生
   性格: 聪明, 睿智, 冷静, 理性, 谨慎, 自私
   目标: 让自己变得最强，自身利益最大化

2. 松姜恒 (29岁) - 未知
   性格: 睿智, 冷静, 谨慎, 傲慢, 多疑
   目标: 建立并统治末世下的"新绝对秩序"

世界观:
时代: 末世无限流
场景: 都市主角家里
力量体系: 有异能但不能打破无限流剧本规则的程度

风格:
名称: 黑暗压抑
基调: dark（黑暗）
节奏: 适中
重点元素: action, dialogue, environment, suspense

生成参数:
随机性: medium
写作温度: 0.9
伏笔策略: moderate
角色自主性: moderate
```

### 配置文件内容

您的配置包含以下几个部分：

1. **novel** - 小说基本信息（标题、类型、梗概、章节数）
2. **characters** - 角色列表（姓名、年龄、职业、性格、目标）
3. **worldbuilding** - 世界观设定（时代、场景、力量体系）
4. **style** - 写作风格（风格名、基调、节奏、重点元素）
5. **generation** - 生成参数（随机性、温度、伏笔策略等）

---

## ✅ 答案 2：如何管理和切换多本小说

### 方法一：手动切换（简单直接）

#### 步骤 1：保存当前配置

```bash
# 给当前配置一个有意义的名字
cp bible/novel_config_latest.yaml bible/novel_config_末日真理.yaml
```

#### 步骤 2：创建新配置

```bash
# 运行配置向导
python3 configure_novel.py

# 按提示输入：
# - 小说标题: 比如"修仙传奇"
# - 类型: 比如 fantasy
# - 角色、世界观等...

# 配置完成后，保存为新名字
cp bible/novel_config_latest.yaml bible/novel_config_修仙传奇.yaml
```

#### 步骤 3：切换配置

```bash
# 切换到末日小说
cp bible/novel_config_末日真理.yaml bible/novel_config_latest.yaml
rm novel_state.db  # 清除旧状态
./run_novel.sh

# 切换到修仙小说
cp bible/novel_config_修仙传奇.yaml bible/novel_config_latest.yaml
rm novel_state.db  # 清除旧状态
./run_novel.sh
```

---

### 方法二：使用脚本（自动化，推荐）

我已经为您创建了两个脚本：

#### 1. 查看当前配置

```bash
./show_config.sh
```

**输出示例**:
```
============================================================
📖 当前小说配置
============================================================

标题: 末日真理：从收割生存点开始
类型: mystery
目标章节: 1

梗概:
在规则扭曲的末世无限流背景...

主要角色:
  1. 陆沉 (26岁) - 心理医生
     性格: 聪明, 睿智, 冷静, 理性, 谨慎
  ...
============================================================
```

#### 2. 切换配置

```bash
./switch_novel.sh
```

**交互示例**:
```
==========================================
📚 小说配置切换器
==========================================

可用的小说配置：

  1. 末日真理：从收割生存点开始
  2. 修仙传奇
  3. 都市爱情故事

选择要切换的配置 (1-3) 或按 q 退出: 2

切换到: 修仙传奇
✅ 已备份当前配置
✅ 已切换配置

⚠️  检测到 novel_state.db
是否删除旧的生成状态? (y/n): y
✅ 已删除 novel_state.db

==========================================
✅ 配置切换完成
==========================================

运行以下命令开始生成:
  ./run_novel.sh
```

---

## 📝 完整工作流示例

### 场景：同时创作 3 本小说

#### 第 1 本：末日悬疑（已有）

```bash
# 已配置完成，保存为:
# bible/novel_config_末日真理.yaml
```

#### 第 2 本：修仙小说

```bash
# 1. 创建配置
python3 configure_novel.py
# 输入标题: 逆天剑修
# 输入类型: fantasy
# ... 配置完成

# 2. 保存配置
cp bible/novel_config_latest.yaml bible/novel_config_逆天剑修.yaml

# 3. 生成小说
rm novel_state.db
./run_novel.sh
```

#### 第 3 本：都市爱情

```bash
# 1. 创建配置
python3 configure_novel.py
# 输入标题: 霸总的小娇妻
# 输入类型: romance
# ... 配置完成

# 2. 保存配置
cp bible/novel_config_latest.yaml bible/novel_config_霸总的小娇妻.yaml

# 3. 生成小说
rm novel_state.db
./run_novel.sh
```

#### 后续切换

```bash
# 方法 1：使用脚本
./switch_novel.sh
# 选择 1, 2 或 3

# 方法 2：手动切换
cp bible/novel_config_末日真理.yaml bible/novel_config_latest.yaml
rm novel_state.db
./run_novel.sh
```

---

## 📁 目录结构

生成后的目录结构：

```
novel/
├── bible/                              # 配置目录
│   ├── novel_config_latest.yaml        # 当前激活（每次运行使用）
│   ├── novel_config_末日真理.yaml       # 末日小说配置
│   ├── novel_config_逆天剑修.yaml       # 修仙小说配置
│   └── novel_config_霸总的小娇妻.yaml   # 爱情小说配置
│
├── manuscript/                         # 生成的小说
│   ├── 末日真理：从收割生存点开始/
│   │   ├── chapter_001.md
│   │   ├── chapter_002.md
│   │   └── ...
│   ├── 逆天剑修/
│   │   ├── chapter_001.md
│   │   └── ...
│   └── 霸总的小娇妻/
│       └── ...
│
├── switch_novel.sh                     # 切换脚本 ⭐
├── show_config.sh                      # 查看配置脚本 ⭐
└── run_novel.sh                        # 生成脚本
```

---

## 💡 重要提示

### 1. 每次切换都要删除 novel_state.db

```bash
rm novel_state.db
```

**原因**: 避免不同小说的生成状态混淆

### 2. 配置文件命名建议

- ✅ `novel_config_末日真理.yaml`
- ✅ `novel_config_修仙传奇.yaml`
- ✅ `novel_config_霸总的小娇妻.yaml`
- ❌ `novel_config_1.yaml`（不够清晰）
- ❌ `novel_config_test.yaml`（含义模糊）

### 3. 备份重要配置

```bash
# 创建备份目录
mkdir -p bible/backups

# 备份配置
cp bible/novel_config_末日真理.yaml bible/backups/末日真理_v1.0.yaml
```

---

## 🎯 快速命令参考

```bash
# 查看当前配置
./show_config.sh

# 创建新配置
python3 configure_novel.py
cp bible/novel_config_latest.yaml bible/novel_config_新小说.yaml

# 切换配置
./switch_novel.sh

# 或手动切换
cp bible/novel_config_末日真理.yaml bible/novel_config_latest.yaml
rm novel_state.db
./run_novel.sh

# 查看所有配置
ls bible/novel_config_*.yaml
```

---

## 📚 详细文档

更多信息请查看：
- `MULTI_CONFIG_GUIDE.md` - 多配置完整指南
- `CHECKPOINT_QUICK_FIX.md` - 断点续传说明

---

**总结**:
1. 您当前配置了一本末日悬疑小说
2. 使用 `./switch_novel.sh` 可以轻松切换不同小说
3. 每个小说的配置保存为独立的 `.yaml` 文件
4. 生成的章节保存在 `manuscript/小说标题/` 目录下
