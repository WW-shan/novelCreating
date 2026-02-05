# 🚀 快速开始指南

## 📋 前置条件

- Python 3.10+
- API Key（已配置在 `.env` 中）
- 已安装依赖（运行过 `pip install -r requirements.txt`）

---

## 🎯 三步生成小说

### 第 1 步：配置小说

```bash
python3 configure_novel.py
```

按照提示完成：
1. 选择类型（赛博朋克/玄幻/武侠/爱情/悬疑）
2. 输入标题和梗概
3. 设定角色（至少 2 个）
4. 选择风格
5. **调整差异性**（重要：决定每次生成的不同程度）

### 第 2 步：验证配置

```bash
./verify_config.sh
```

应该看到：
```
✅ 所有节点已统一使用 Sonnet 4.5
✅ 已添加超时和重试保护
```

### 第 3 步：生成小说

```bash
./run_novel.sh
```

等待生成完成（每章约 1-2 分钟）。

---

## 📁 查看结果

生成完成后：

```bash
# 查看章节文件
ls manuscript/[你的小说名]/

# 读取第一章
cat manuscript/[你的小说名]/chapter_001.md

# 查看世界状态
cat bible/[你的小说名]_world_state.json
```

---

## 🔧 常用命令

### 测试 API 连接

```bash
./test_api.sh
```

### 查看配置文件

```bash
cat bible/novel_config_latest.yaml
```

### 编辑配置（微调）

```bash
vim bible/novel_config_latest.yaml
# 或
nano bible/novel_config_latest.yaml
```

### 清除旧数据重新开始

```bash
# 清除状态数据库
rm novel_state.db*

# 重新生成
./run_novel.sh
```

---

## 💡 配置技巧

### 调整生成章节数

编辑 `bible/novel_config_latest.yaml`:

```yaml
novel:
  target_chapters: 10  # 改为你想要的章节数
```

### 调整随机性

```yaml
generation:
  randomness_level: high  # low/medium/high
  writer_temp: 0.9        # 0.1-1.2，越高越随机
```

### 调整写作风格

```yaml
style:
  tone: dark              # serious/humorous/dark/passionate/romantic
  focus_elements:
    - action              # 动作场面
    - dialogue            # 对话
    - suspense            # 悬念
```

---

## 🐛 故障排除

### 问题：找不到配置文件

```bash
python3 configure_novel.py
```

重新生成配置。

### 问题：API 超时

1. 检查网络连接
2. 等待几分钟后重试
3. 已添加自动重试，通常会自动恢复

### 问题：生成中断

状态已自动保存，直接重新运行：

```bash
./run_novel.sh
```

会从断点继续。

### 问题：质量不满意

调整温度参数：

```yaml
generation:
  writer_temp: 0.9  # 提高创意
```

或重新运行生成不同版本（每次都会不同）。

---

## 📊 系统架构

```
配置阶段                生成阶段
┌─────────┐           ┌─────────┐
│ 配置向导  │ ────────→ │ 工作流   │
│ (交互式) │           │ (自动)   │
└─────────┘           └─────────┘
     │                     │
     ↓                     ↓
 config.yaml          4层循环:
                      Planner → Writer
                      → Critic → Memory
                           │
                           ↓
                      chapter_*.md
```

---

## 🎨 示例配置

### 赛博朋克风格

```yaml
novel:
  title: "霓虹之下"
  type: "cyberpunk"
  target_chapters: 15

style:
  tone: dark
  focus_elements: [action, suspense]

generation:
  randomness_level: high
  writer_temp: 0.9
```

### 武侠风格

```yaml
novel:
  title: "剑啸江湖"
  type: "wuxia"
  target_chapters: 20

style:
  tone: passionate
  focus_elements: [action, dialogue]

generation:
  randomness_level: medium
  writer_temp: 0.8
```

### 爱情风格

```yaml
novel:
  title: "时光里的你"
  type: "romance"
  target_chapters: 12

style:
  tone: romantic
  focus_elements: [dialogue, psychology]

generation:
  randomness_level: low
  writer_temp: 0.7
```

---

## 🌟 高级功能

### 批量生成不同版本

```bash
# 生成第一版
./run_novel.sh

# 重命名结果
mv manuscript/[小说名] manuscript/[小说名]_v1

# 清除状态
rm novel_state.db*

# 生成第二版（会完全不同）
./run_novel.sh
```

### 查看生成历史

```bash
ls -la bible/
# 会看到所有历史配置文件
```

---

## 📚 相关文档

- `README.md` - 项目总览
- `WORKFLOW.md` - 详细工作流程
- `CHANGELOG.md` - 更新日志
- `FIX_TIMEOUT.md` - 超时问题解决方案
- `USAGE.md` - 详细使用手册

---

## ⚡ 性能提示

1. **首次生成建议先测试 1 章**：
   ```yaml
   target_chapters: 1
   ```

2. **网络不稳定时降低章节数**

3. **避免同时运行多个生成任务**

4. **定期清理旧的状态数据库**

---

**准备好了吗？开始创作你的小说！** 🎉

```bash
python3 configure_novel.py
./run_novel.sh
```
