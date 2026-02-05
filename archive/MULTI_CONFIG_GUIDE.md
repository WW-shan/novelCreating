# 📚 多本小说配置管理指南

## 📋 您当前的配置

### 当前激活配置
**文件**: `bible/novel_config_latest.yaml`

**小说信息**:
- **标题**: 末日真理：从收割生存点开始
- **类型**: mystery（悬疑）
- **目标章节**: 1 章
- **主角**: 陆沉（26岁，心理医生）
- **反派**: 松姜恒（29岁，未知职业）
- **世界观**: 末世无限流
- **风格**: 黑暗压抑，理性利己主义
- **创建时间**: 2026-02-04

### 备份配置
**文件**: `bible/novel_config_末日真理从收割生存点开始_20260204_135109.yaml`
- 这是自动备份的版本

---

## 🔄 如何管理多本小说配置

### 方案 1：使用配置文件命名（推荐）

每本小说保存为单独的配置文件：

```bash
bible/
├── novel_config_latest.yaml           # 当前激活
├── novel_config_末日真理.yaml          # 末日小说配置
├── novel_config_修仙传奇.yaml          # 修仙小说配置
├── novel_config_都市爱情.yaml          # 爱情小说配置
└── novel_config_科幻冒险.yaml          # 科幻小说配置
```

**切换方法**:
```bash
# 切换到修仙小说
cp bible/novel_config_修仙传奇.yaml bible/novel_config_latest.yaml
./run_novel.sh

# 切换到都市爱情
cp bible/novel_config_都市爱情.yaml bible/novel_config_latest.yaml
./run_novel.sh
```

---

### 方案 2：创建切换脚本（自动化）

创建 `switch_novel.sh`:

```bash
#!/bin/bash
# 小说配置切换脚本

echo "=========================================="
echo "小说配置切换器"
echo "=========================================="
echo

# 列出所有配置文件
configs=(bible/novel_config_*.yaml)
configs=("${configs[@]##bible/novel_config_}")
configs=("${configs[@]%%.yaml}")

# 过滤掉 latest 和备份文件
filtered=()
for config in "${configs[@]}"; do
    if [[ "$config" != "latest" && "$config" != *"_202"* ]]; then
        filtered+=("$config")
    fi
done

echo "可用的小说配置："
for i in "${!filtered[@]}"; do
    echo "  $((i+1)). ${filtered[$i]}"
done

echo
read -p "选择要切换的配置 (1-${#filtered[@]}): " choice

if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#filtered[@]}" ]; then
    selected="${filtered[$((choice-1))]}"
    cp "bible/novel_config_${selected}.yaml" bible/novel_config_latest.yaml
    echo
    echo "✅ 已切换到: $selected"
    echo "   运行 ./run_novel.sh 开始生成"
else
    echo "❌ 无效选择"
    exit 1
fi
```

**使用方法**:
```bash
chmod +x switch_novel.sh
./switch_novel.sh

# 输出：
# 可用的小说配置：
#   1. 末日真理
#   2. 修仙传奇
#   3. 都市爱情
# 选择要切换的配置 (1-3): 2
# ✅ 已切换到: 修仙传奇
```

---

### 方案 3：查看当前配置

创建 `show_config.sh`:

```bash
#!/bin/bash
# 显示当前配置信息

source venv/bin/activate

python3 << 'EOF'
import yaml

with open('bible/novel_config_latest.yaml', 'r') as f:
    config = yaml.safe_load(f)

print("=" * 60)
print("当前小说配置")
print("=" * 60)
print(f"\n标题: {config['novel']['title']}")
print(f"类型: {config['novel']['type']}")
print(f"目标章节: {config['novel']['target_chapters']}")
print(f"\n梗概:\n{config['novel']['synopsis'][:200]}...")
print(f"\n风格: {config['style']['style_name']}")
print(f"基调: {config['style']['tone']}")
print(f"\n主要角色:")
for char in config['characters'][:3]:
    print(f"  • {char['name']} ({char['age']}岁) - {char['occupation']}")
print(f"\n世界观:")
print(f"  时代: {config['worldbuilding']['era']}")
print(f"  场景: {config['worldbuilding']['setting']}")
print("=" * 60)
EOF
```

---

## 📖 创建新小说配置

### 方法 1：使用配置向导

```bash
python3 configure_novel.py
```

**配置完成后，保存为特定名称**:
```bash
# 自动保存为 latest 和带时间戳的备份
# 手动重命名为有意义的名字
cp bible/novel_config_latest.yaml bible/novel_config_你的小说名.yaml
```

### 方法 2：复制并修改现有配置

```bash
# 复制现有配置
cp bible/novel_config_latest.yaml bible/novel_config_新小说.yaml

# 编辑新配置
nano bible/novel_config_新小说.yaml
# 或
vim bible/novel_config_新小说.yaml
```

**修改要点**:
```yaml
novel:
  title: "新的小说标题"        # 必须修改
  type: "science_fiction"      # 修改类型
  synopsis: "新的故事梗概..."
  target_chapters: 100

characters:
  - name: "新主角"
    age: "25"
    # ... 修改角色信息

worldbuilding:
  era: "未来2150年"
  setting: "火星殖民地"
  # ... 修改世界观
```

---

## 🎯 完整工作流示例

### 场景：同时创作3本小说

**1. 创建3个配置**

```bash
# 第1本：末日悬疑（已有）
# bible/novel_config_末日真理.yaml

# 第2本：修仙小说
python3 configure_novel.py
# 配置完成后：
cp bible/novel_config_latest.yaml bible/novel_config_逆天剑修.yaml

# 第3本：都市爱情
python3 configure_novel.py
# 配置完成后：
cp bible/novel_config_latest.yaml bible/novel_config_霸总的小娇妻.yaml
```

**2. 切换并生成**

```bash
# 生成末日小说
cp bible/novel_config_末日真理.yaml bible/novel_config_latest.yaml
rm novel_state.db  # 清除旧状态
./run_novel.sh

# 生成修仙小说
cp bible/novel_config_逆天剑修.yaml bible/novel_config_latest.yaml
rm novel_state.db  # 清除旧状态
./run_novel.sh

# 生成爱情小说
cp bible/novel_config_霸总的小娇妻.yaml bible/novel_config_latest.yaml
rm novel_state.db  # 清除旧状态
./run_novel.sh
```

**3. 查看生成结果**

```bash
ls manuscript/

# 输出：
# 末日真理：从收割生存点开始/
# 逆天剑修/
# 霸总的小娇妻/
```

---

## 📁 推荐的目录结构

```
novel/
├── bible/                              # 配置目录
│   ├── novel_config_latest.yaml        # 当前激活
│   ├── novel_config_末日真理.yaml
│   ├── novel_config_逆天剑修.yaml
│   ├── novel_config_霸总的小娇妻.yaml
│   └── backups/                        # 备份目录（可选）
│       ├── novel_config_末日真理_20260204.yaml
│       └── novel_config_逆天剑修_20260204.yaml
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
│       ├── chapter_001.md
│       └── ...
│
├── switch_novel.sh                     # 切换脚本
├── show_config.sh                      # 查看配置脚本
└── run_novel.sh                        # 生成脚本
```

---

## 🛠️ 实用工具脚本

### 创建备份

```bash
#!/bin/bash
# backup_config.sh
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p bible/backups
cp bible/novel_config_latest.yaml "bible/backups/backup_$DATE.yaml"
echo "✅ 配置已备份到 bible/backups/backup_$DATE.yaml"
```

### 列出所有小说

```bash
#!/bin/bash
# list_novels.sh
echo "已配置的小说："
for config in bible/novel_config_*.yaml; do
    if [[ "$config" != *"latest"* && "$config" != *"_202"* ]]; then
        name=$(basename "$config" .yaml | sed 's/novel_config_//')
        echo "  • $name"
    fi
done
```

---

## 💡 最佳实践

### 1. 命名规范
- 使用有意义的名称：`novel_config_末日真理.yaml`
- 避免使用特殊字符
- 使用中文或拼音都可以

### 2. 切换前备份
```bash
# 在切换前先备份当前配置
cp bible/novel_config_latest.yaml bible/novel_config_latest_backup.yaml
cp bible/novel_config_新小说.yaml bible/novel_config_latest.yaml
```

### 3. 清除数据库
**重要**: 每次切换小说后，删除 `novel_state.db`：
```bash
rm novel_state.db
```

这样避免不同小说的状态混淆。

### 4. 版本管理
定期备份重要配置：
```bash
cp bible/novel_config_末日真理.yaml bible/backups/末日真理_v1.0.yaml
```

---

## 🎨 您当前配置的详细信息

```yaml
novel:
  title: "末日真理：从收割生存点开始"
  type: mystery
  target_chapters: 1
  synopsis: |
    在规则扭曲的末世无限流背景，男主陆沉是极度理性的
    利己主义者，拥有能推演死局概率的"因果模拟"能力，
    文风基调严肃冷峻...

characters:
  - name: 陆沉
    age: 26
    occupation: 心理医生
    traits: [聪明, 睿智, 冷静, 理性, 谨慎, 自私]
    goal: 让自己变得最强，自身利益最大化

  - name: 松姜恒
    age: 29
    traits: [睿智, 冷静, 谨慎, 傲慢, 多疑]
    goal: 建立并统治末世下的"新绝对秩序"

style:
  style_name: 黑暗压抑
  tone: dark
  pace: 适中
  focus_elements: [action, dialogue, environment, suspense]

worldbuilding:
  era: 末世无限流
  setting: 都市主角家里
  power_system: 有异能但不能打破无限流剧本规则的程度

generation:
  randomness_level: medium
  writer_temp: 0.9
  character_autonomy: moderate
  foreshadow_strategy: moderate
```

---

## 🚀 快速切换命令

```bash
# 查看当前配置
./show_config.sh

# 切换配置
./switch_novel.sh

# 或手动切换
cp bible/novel_config_你的小说.yaml bible/novel_config_latest.yaml
rm novel_state.db
./run_novel.sh
```

---

需要我帮您创建这些脚本吗？
