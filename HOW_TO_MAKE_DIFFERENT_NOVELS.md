# 📚 AI 小说生成器 - 完整使用指南

## 🚀 快速开始（3步走）

### 第1步：安装依赖

```bash
cd /project/novel
pip install -r requirements.txt pyyaml
```

### 第2步：配置你的小说

```bash
python3 configure_novel.py
```

程序会引导你一步步填写：
- 选择小说类型（科幻/玄幻/武侠/爱情/悬疑）
- 输入故事梗概
- 设定角色和世界观
- 选择写作风格
- **配置差异性参数**（让每次生成都不同）

### 第3步：生成小说

```bash
./run_novel.sh
```

系统会自动根据你的配置生成章节！

---

## 🎨 让每篇小说不同的秘密

### 核心机制

系统通过以下方式确保每次生成的小说都不同：

#### 1. **AI 温度参数（Temperature）**
```
低温度 (0.2-0.5) → 更可控、更接近设定
中温度 (0.6-0.8) → 平衡创意和一致性  ✅ 推荐
高温度 (0.9-1.2) → 更有创意、可能出现意外情节
```

在配置时，你可以选择：
- **低随机性**：temperature ≈ 0.5（严谨题材）
- **中随机性**：temperature ≈ 0.7（推荐）
- **高随机性**：temperature ≈ 0.9（脑洞大开）

#### 2. **随机种子（Seed）**
- 默认：`seed = None` → **每次运行使用不同种子**
- 这意味着即使配置完全相同，AI 也会产生不同的创作

#### 3. **伏笔生成策略**
```
保守模式：只使用你预设的伏笔
适中模式：AI 适当添加新伏笔  ✅ 推荐
激进模式：AI 自由创造大量伏笔和支线
```

#### 4. **角色自主性**
```
严格模式：角色严格按设定行动
适中模式：角色可在合理范围内自主发展  ✅ 推荐
自由模式：角色可能做出意想不到的决定
```

---

## 📝 配置文件示例

运行 `configure_novel.py` 后，会生成类似这样的配置：

```yaml
novel:
  title: "赛博迷城"
  synopsis: "2087年，黑客张伟发现公司试图控制人类意识的阴谋"
  target_chapters: 20
  type: cyberpunk

characters:
  - name: "张伟"
    age: 28
    traits: ["聪明", "叛逆", "孤独"]
    occupation: "黑客"
    goal: "揭露真相"

worldbuilding:
  era: "2087年"
  setting: "霓虹闪烁的超大都市"
  power_system: "神经接口技术"

style:
  tone: "dark"
  style_name: "黑暗压抑"
  pace: "2"
  focus_elements: ["action", "suspense"]

generation:
  temperature: 0.7
  writer_temp: 0.9
  randomness_level: "medium"
  foreshadow_strategy: "moderate"
  character_autonomy: "moderate"
  seed: null  # 每次不同！
```

---

## 🎯 常见使用场景

### 场景1：写一个短篇故事（1-5章）

```bash
# 1. 配置
python3 configure_novel.py
# 选择章节数：5

# 2. 生成
./run_novel.sh
```

### 场景2：写一部长篇小说（20-100章）

```bash
# 1. 配置
python3 configure_novel.py
# 选择章节数：50
# 选择随机性：中等（避免后期崩溃）

# 2. 分批生成（建议）
# 编辑配置文件，每次生成5-10章
nano bible/novel_config_latest.yaml
# 修改 target_chapters: 10

# 3. 多次运行
./run_novel.sh  # 生成第1-10章
./run_novel.sh  # 生成第11-20章（从断点继续）
```

### 场景3：同一个设定，生成多个不同版本

```bash
# 保存原始配置
cp bible/novel_config_latest.yaml bible/version_1.yaml

# 生成版本1
./run_novel.sh

# 调整随机性参数
python3 configure_novel.py
# 选择"高随机性"

# 生成版本2（会有不同的情节发展）
./run_novel.sh
```

### 场景4：测试不同写作风格

```bash
# 1. 使用相同角色和世界观
# 2. 修改 style 配置：
#    - 第一次：严肃正剧
#    - 第二次：轻松幽默
#    - 第三次：黑暗压抑

# 对比生成结果，找到最适合的风格
```

---

## 🔧 高级定制

### 1. 直接编辑配置文件

```bash
nano bible/novel_config_latest.yaml
```

你可以修改：
- `temperature` 值（控制随机性）
- `foreshadow_strategy`（伏笔策略）
- `character_autonomy`（角色自主性）
- `focus_elements`（重点元素）

### 2. 为不同节点设置不同温度

编辑 `src/nodes/writer.py`：
```python
# 获取配置中的温度参数
config = state.get('config', {})
writer_temp = config.get('generation', {}).get('writer_temp', 0.8)

llm = ChatAnthropic(model="claude-opus-4-5-20251101", temperature=writer_temp)
```

### 3. 添加自定义提示词

编辑节点文件，在 `prompt` 中添加你的指导：

```python
# 在 src/nodes/writer.py 的 prompt 中添加：
SPECIAL_INSTRUCTIONS:
- 每章必须以环境描写开场
- 对话要符合角色性格
- 多用"show don't tell"手法
```

---

## 🧪 实验：让小说更加多样化

### 实验1：极端随机性

```yaml
generation:
  temperature: 1.1  # 高温度
  writer_temp: 1.3
  randomness_level: "high"
  foreshadow_strategy: "aggressive"
  character_autonomy: "free"
```

**结果**：情节可能出现意想不到的转折，角色可能做出反常决定

### 实验2：严格控制

```yaml
generation:
  temperature: 0.3  # 低温度
  writer_temp: 0.5
  randomness_level: "low"
  foreshadow_strategy: "conservative"
  character_autonomy: "strict"
```

**结果**：严格遵循你的设定，情节可预测但逻辑严密

### 实验3：动态调整（手动）

```bash
# 前期（1-10章）：低随机性建立世界观
# 中期（11-30章）：中随机性发展情节
# 后期（31-50章）：高随机性高潮迭起
```

每个阶段修改配置文件的 temperature 参数。

---

## 📊 差异性验证

### 测试方法：

1. **保持配置不变**
2. **运行3次生成**
3. **对比输出**

你会发现：
- ✅ 角色性格一致，但具体对话不同
- ✅ 主线情节相似，但细节和支线不同
- ✅ 伏笔位置和呈现方式不同
- ✅ 环境描写的侧重点不同

### 为什么会不同？

```python
# 系统内部（你不需要改，只需要了解）

# 1. 每次运行，random seed不同
if generation.get('seed'):
    random.seed(generation['seed'])  # 固定
else:
    # 不设置seed，使用系统时间 → 每次不同

# 2. AI的采样过程
# temperature = 0.8 意味着：
# - 不是总选最可能的词
# - 在概率分布中随机采样
# → 每次采样结果不同

# 3. 伏笔动态生成
# AI会根据当前情节自动创造新伏笔
# → 每次创造的伏笔内容和时机不同
```

---

## ❓ 常见问题

### Q: 如何让小说更加一致？
A: 降低 `temperature` 值（0.3-0.5），选择"低随机性"，使用"保守"伏笔策略。

### Q: 如何让小说更有创意？
A: 提高 `temperature` 值（0.9-1.2），选择"高随机性"，使用"激进"伏笔策略。

### Q: 生成的章节太短/太长？
A: 编辑 `src/nodes/writer.py`，修改提示词中的字数要求：
```python
- Write at least 3000 words.  # 改为你想要的字数
```

### Q: 如何固定某些情节，只让其他部分随机？
A: 在配置的 `plot_tracks` 中明确指定必须发生的情节，选择"保守"伏笔策略。

### Q: 能否生成完全相同的小说？
A: 可以！设置 `seed: 12345`（任意固定数字），同时设置低温度参数。

---

## 🎁 示例配置模板

我已经为你准备了5个模板：

1. **赛博朋克** - 科幻题材，高科技低生活
2. **玄幻修仙** - 东方玄幻，修炼体系
3. **都市爱情** - 现代言情，情感细腻
4. **悬疑推理** - 逻辑严密，抽丝剥茧
5. **武侠江湖** - 传统武侠，快意恩仇

运行 `python3 configure_novel.py` 时选择即可！

---

## 📞 获取帮助

- 查看系统日志：`cat logs/*.log`
- 检查生成结果：`cat manuscript/你的小说名/chapter_001.md`
- 查看世界状态：`cat bible/你的小说名_world_state.json`

祝你创作愉快！🎉
