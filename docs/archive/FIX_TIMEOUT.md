# 🔧 API 超时问题解决方案

## 问题描述

生成小说时遇到 Cloudflare 524 错误（网关超时）：
```
Error code 524: A timeout occurred
The origin web server timed out responding to this request.
```

这个错误发生在 Writer 节点，因为：
1. Opus 4.5 生成 2000+ 字内容需要较长时间
2. 代理服务器 (claud.bfund.pro) 设置了较短的超时时间
3. 没有实现重试机制

---

## 解决方案

### 方案 1: 添加重试机制和超时处理（推荐）

修改所有节点文件，添加重试逻辑和错误处理。

#### 修改 src/nodes/writer.py

```python
from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic
from src.state import NovelState
import os
import json
import time

def writer_node(state: NovelState) -> NovelState:
    """
    The Writer Node (Claude 4.5 Opus Role).
    Takes the beats from the Planner and expands them into a full prose draft.
    """
    print("--- WRITER NODE ---")

    # 从配置中读取温度参数
    config = state.get('config', {})
    writer_temp = config.get('generation', {}).get('writer_temp', 0.8)

    # Use Claude Opus 4.5 for Writer
    llm = ChatAnthropic(
        model="claude-opus-4-5-20251101",
        temperature=writer_temp,
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        anthropic_api_url=os.getenv("ANTHROPIC_BASE_URL"),
        timeout=300.0,  # 增加超时时间到 5 分钟
        max_retries=3   # 最多重试 3 次
    )

    current_beats = state.get("current_beats", "")
    world_bible = state.get("world_bible", {})
    synopsis = state.get("synopsis", "")

    # Context about characters for voice consistency
    characters = world_bible.get("characters", {})

    # 根据配置调整提示词
    style = config.get('style', {})
    tone = style.get('tone', 'neutral')
    focus_elements = style.get('focus_elements', [])

    # 构建风格指导
    tone_guides = {
        'serious': 'Write in a serious, formal tone with deep character introspection.',
        'humorous': 'Write in a light, humorous tone with witty dialogue.',
        'dark': 'Write in a dark, brooding tone with atmospheric descriptions.',
        'passionate': 'Write in an energetic, passionate tone with dynamic action.',
        'romantic': 'Write in a romantic, tender tone with emotional depth.'
    }

    tone_instruction = tone_guides.get(tone, '')

    # 构建重点元素指导
    focus_instructions = []
    if 'action' in focus_elements:
        focus_instructions.append('- Emphasize action sequences and dynamic movement.')
    if 'dialogue' in focus_elements:
        focus_instructions.append('- Include rich, character-revealing dialogue.')
    if 'psychology' in focus_elements:
        focus_instructions.append('- Explore characters\' inner thoughts and motivations.')
    if 'environment' in focus_elements:
        focus_instructions.append('- Provide detailed environmental descriptions.')
    if 'suspense' in focus_elements:
        focus_instructions.append('- Build tension and suspense throughout.')

    focus_text = '\\n'.join(focus_instructions) if focus_instructions else ''

    prompt = f"""
    You are the Lead Writer (The Poet) for a high-quality novel.
    Your task is to write the full text for the next chapter based on the provided beats.

    CONTEXT:
    - Overall Synopsis: {synopsis}
    - Characters involved: {list(characters.keys())}
    - Character details: {json.dumps(characters, indent=2, ensure_ascii=False)}

    CHAPTER BEATS:
    {current_beats}

    WRITING STYLE:
    {tone_instruction}

    FOCUS ELEMENTS:
    {focus_text}

    INSTRUCTIONS:
    - Write at least 2000 words (approximately 4000 Chinese characters).
    - Focus on "Show, Don't Tell".
    - Include sensory details (smell, sound, texture).
    - Avoid clichés like "suddenly", "in conclusion", etc.
    - Maintain consistent character voices.
    - Write in Chinese (简体中文).

    Write the chapter draft now.
    """

    # 重试机制
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            print(f"  尝试生成... (第 {attempt + 1}/{max_attempts} 次)")
            response = llm.invoke([HumanMessage(content=prompt)])
            print(f"  ✅ 生成成功！字数: {len(response.content)}")
            return {"draft": response.content, "iteration": state.get("iteration", 0) + 1}

        except Exception as e:
            error_msg = str(e)
            print(f"  ❌ 生成失败: {error_msg[:100]}...")

            # 如果是超时错误且不是最后一次尝试，等待后重试
            if '524' in error_msg or 'timeout' in error_msg.lower():
                if attempt < max_attempts - 1:
                    wait_time = (attempt + 1) * 10  # 递增等待时间: 10s, 20s, 30s
                    print(f"  ⏳ 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue

            # 其他错误或最后一次尝试失败
            if attempt == max_attempts - 1:
                print(f"  ⚠️  所有重试均失败，使用备用方案")
                # 返回一个简化的占位内容
                fallback_draft = f"""
                # 第 {state.get('current_chapter_index', 1)} 章

                [由于 API 超时，本章节暂时无法生成]

                章节大纲：
                {current_beats}

                请稍后重试或检查 API 配置。
                """
                return {"draft": fallback_draft, "iteration": state.get("iteration", 0) + 1}

    # 理论上不会到达这里
    return {"draft": "生成失败", "iteration": state.get("iteration", 0) + 1}
```

#### 同样修改其他节点

对 `planner.py`, `critic.py`, `memory.py` 也添加类似的重试机制。

---

### 方案 2: 使用官方 Anthropic API（最稳定）

如果你有官方 Anthropic API Key，直接修改 `.env`:

```bash
# 方案 2A: 使用官方 API（推荐）
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx  # 你的官方 Key
# ANTHROPIC_BASE_URL=  # 注释掉或删除这行

# 方案 2B: 或者使用其他代理
# ANTHROPIC_BASE_URL=https://api.anthropic.com
```

---

### 方案 3: 减少生成字数要求

修改 `src/nodes/writer.py`，减少字数要求以降低超时风险：

```python
prompt = f"""
...
INSTRUCTIONS:
- Write at least 800 words.  # 从 2000 降低到 800
...
"""
```

---

### 方案 4: 分段生成（复杂但可靠）

将长章节拆分成多个小段，逐段生成：

```python
def writer_node_multi_part(state: NovelState) -> NovelState:
    """分段生成长章节"""
    beats = state.get("current_beats", "").split("\\n\\n")  # 按段落分割

    full_draft = ""
    for i, beat in enumerate(beats):
        print(f"  生成第 {i+1}/{len(beats)} 段...")

        # 生成单段
        prompt = f"根据以下情节要点，写作 500-800 字：\\n{beat}"
        response = llm.invoke([HumanMessage(content=prompt)])

        full_draft += response.content + "\\n\\n"
        time.sleep(2)  # 间隔 2 秒，避免请求过快

    return {"draft": full_draft, ...}
```

---

## 立即修复步骤

### 1. 快速修复（推荐）

创建一个修复脚本：

```bash
#!/bin/bash
# fix_timeout.sh

# 备份原文件
cp src/nodes/writer.py src/nodes/writer.py.backup

# 创建新的 writer.py（添加重试机制）
cat > src/nodes/writer_fixed.py << 'EOF'
# [粘贴上面方案1的完整代码]
EOF

# 替换
mv src/nodes/writer_fixed.py src/nodes/writer.py

echo "✅ Writer 节点已修复，添加了重试机制和超时处理"
```

### 2. 测试修复

```bash
# 重新运行
./run_novel.sh

# 观察输出:
# - 应该看到 "尝试生成... (第 1/3 次)"
# - 如果超时，会自动重试
# - 最多重试 3 次
```

---

## 预防措施

### 1. 监控和日志

在 `src/main.py` 添加详细日志：

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/novel_generation.log'),
        logging.StreamHandler()
    ]
)
```

### 2. 渐进式生成

先生成 1 章测试，确认无误后再生成全部：

```yaml
# bible/novel_config_latest.yaml
novel:
  target_chapters: 1  # 先测试生成 1 章
```

### 3. 使用更稳定的模型

如果持续超时，可以临时切换到更快的 Sonnet：

```python
# src/nodes/writer.py (临时方案)
llm = ChatAnthropic(
    model="claude-sonnet-4-5-20250929",  # 使用 Sonnet 而非 Opus
    temperature=0.8,
    ...
)
```

---

## 错误码参考

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| 524 | 网关超时 | 增加超时时间、添加重试、减少生成量 |
| 500 | 服务器内部错误 | 检查 API Key、等待后重试 |
| 429 | 请求过快 | 添加延迟、降低并发 |
| 401 | 认证失败 | 检查 API Key 是否正确 |

---

## 调试命令

```bash
# 1. 测试 API 连接
./test_api.sh

# 2. 查看详细错误
python3 src/main.py 2>&1 | tee logs/debug.log

# 3. 检查数据库状态
sqlite3 novel_state.db "SELECT * FROM checkpoints ORDER BY checkpoint_id DESC LIMIT 5;"

# 4. 清空状态重新开始
rm novel_state.db*
./run_novel.sh
```

---

## 需要我帮你实施哪个方案？

1. ✅ **方案 1**: 添加重试机制（推荐，最稳定）
2. 🔑 **方案 2**: 切换到官方 API（需要官方 Key）
3. ✂️ **方案 3**: 减少字数要求（快速但质量降低）
4. 🧩 **方案 4**: 分段生成（复杂但可靠）

请告诉我你想使用哪个方案，我立即帮你实施！
