from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic
from src.state import NovelState
import os
import json
import time
from pathlib import Path


def save_chapter_to_file(chapter_index, content, state):
    """保存章节到文件"""
    try:
        # 获取项目路径（从state中读取）
        project_paths = state.get('project_paths', {})
        manuscript_dir = project_paths.get('manuscript_dir')

        if not manuscript_dir:
            # 降级方案：使用旧路径
            config = state.get('config', {})
            novel_info = config.get('novel', {})
            title = novel_info.get('title', '未命名小说')
            manuscript_dir = f"/project/novel/manuscript/{title}"

        # 创建输出目录
        output_dir = Path(manuscript_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 生成章节标题（基于内容）
        chapter_title = generate_chapter_title(content, chapter_index)

        # 清理Markdown格式，转换为纯文本
        clean_content = content
        # 移除 # 标题符号
        clean_content = clean_content.replace('# 第', '第')
        # 移除 ** 加粗标记
        clean_content = clean_content.replace('**', '')
        # 移除 * 斜体标记
        clean_content = clean_content.replace('*', '')

        # 添加章节标题到内容开头
        final_content = f"第 {chapter_index} 章：{chapter_title}\n\n" + clean_content.split('\n', 1)[-1] if '\n' in clean_content else clean_content

        # 保存章节（txt格式）
        filename = output_dir / f"chapter_{chapter_index:03d}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(final_content)

        print(f"  💾 已保存: {filename}")
        print(f"  📖 章节标题: {chapter_title}")

    except Exception as e:
        print(f"  ⚠️  保存失败: {str(e)[:50]}")


def generate_chapter_title(content, chapter_index):
    """基于章节内容生成标题"""
    try:
        # 使用AI生成简洁的章节标题
        llm = ChatAnthropic(
            model="claude-sonnet-4-5-20250929",
            temperature=0.3,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            anthropic_api_url=os.getenv("ANTHROPIC_BASE_URL"),
            timeout=20.0,
            max_retries=1
        )

        # 提取章节前500字作为参考
        content_preview = content[:500]

        prompt = f"""基于以下章节内容，生成一个简洁的章节标题（4-8个字）。

章节内容预览：
{content_preview}

要求：
1. 标题要简洁（4-8个字）
2. 反映本章核心情节或关键事件
3. 不要使用引号或其他标点
4. 直接输出标题，不要其他内容

章节标题："""

        response = llm.invoke([HumanMessage(content=prompt)])
        title = response.content.strip()

        # 清理标题（移除引号等）
        title = title.replace('"', '').replace("'", '').replace('《', '').replace('》', '')

        # 限制长度
        if len(title) > 12:
            title = title[:12]

        return title

    except Exception as e:
        # 如果生成失败，返回默认标题
        print(f"  ⚠️  标题生成失败，使用默认标题")
        return f"第{chapter_index}章"


def writer_node(state: NovelState) -> NovelState:
    """
    High quality Writer Node with segmented generation.
    完整版：利用角色历史状态确保一致性
    """
    print("--- WRITER NODE ---")

    current_beats = state.get("current_beats", "")
    world_bible = state.get("world_bible", {})
    characters = world_bible.get("characters", {})
    chapter_index = state.get('current_chapter_index', 1)
    config = state.get('config', {})
    iteration = state.get("iteration", 0)
    critic_feedback = state.get("feedback", "")

    # 如果是修订版本,显示 Critic 反馈
    if iteration > 0 and critic_feedback:
        print(f"  🔄 修订版本 (第 {iteration} 次)")
        print(f"  📝 Critic 反馈: {critic_feedback[:100]}...")

    # 提取角色当前状态（完整版功能）
    character_states = extract_character_states(characters)
    if character_states:
        print(f"  👥 角色状态追踪: {len(character_states)} 个主要角色")

    # 读取配置
    style = config.get('style', {})
    tone = style.get('tone', 'neutral')
    focus_elements = style.get('focus_elements', [])

    print(f"  📝 章节 {chapter_index} - 高质量分段生成")
    print(f"     风格: {tone}")

    # 拆分场景
    beat_lines = [line.strip() for line in current_beats.split('\n') if line.strip()]

    if len(beat_lines) <= 2:
        print(f"  📌 场景较少，单段生成")
        return generate_single_quality(current_beats, characters, chapter_index, state, tone, focus_elements)

    print(f"  📌 分 {len(beat_lines)} 段生成")

    segments = []
    for i, beat in enumerate(beat_lines, 1):
        print(f"\n  🔸 第 {i}/{len(beat_lines)} 段...")

        segment = generate_one_segment(
            beat, i, len(beat_lines), characters,
            "\n\n".join(segments), tone, focus_elements, critic_feedback, character_states
        )

        if segment:
            segments.append(segment)
            print(f"     ✅ 完成 ({len(segment)} 字符)")
        else:
            print(f"     ⚠️  失败")
            segments.append(f"\n[场景 {i}: {beat}]\n")

    full_draft = f"第 {chapter_index} 章\n\n" + "\n\n".join(segments)

    # 质量检查
    issues = check_quality(full_draft)
    if issues:
        print(f"\n  ⚠️  发现 {len(issues)} 个质量问题:")
        for issue in issues[:2]:
            print(f"     - {issue}")

    print(f"\n  ✅ 章节完成！{len(full_draft)} 字符")

    # 💾 立即保存章节到文件
    save_chapter_to_file(chapter_index, full_draft, state)

    return {"draft": full_draft, "iteration": state.get("iteration", 0) + 1}


def generate_one_segment(beat, num, total, characters, prev_content, tone, focus, critic_feedback="", character_states=None):
    """生成单个段落（完整版：考虑角色状态）"""

    if character_states is None:
        character_states = {}

    context = prev_content[-600:] if len(prev_content) > 600 else prev_content

    # 风格指导
    tones = {
        'serious': '严肃正式，深刻内心',
        'humorous': '轻松幽默，机智对话',
        'dark': '阴暗压抑，沉重氛围',
        'passionate': '激昂热血，生动动作',
        'romantic': '温柔细腻，情感微妙'
    }
    style_hint = tones.get(tone, '')

    # 重点提示
    focus_hints = []
    if 'action' in focus:
        focus_hints.append('动作场面')
    if 'dialogue' in focus:
        focus_hints.append('对话刻画')
    if 'psychology' in focus:
        focus_hints.append('心理描写')
    if 'environment' in focus:
        focus_hints.append('环境渲染')
    if 'suspense' in focus:
        focus_hints.append('悬念营造')

    focus_text = '、'.join(focus_hints) if focus_hints else '场景细节'

    # 连贯提示
    connect_hint = '自然衔接前文' if num > 1 else '开头引人入胜'

    # Critic 反馈提示
    critic_hint = ""
    if critic_feedback:
        critic_hint = f"\n\n【⚠️ 编辑反馈（需要改进）】\n{critic_feedback[:200]}\n请在本次写作中避免上述问题。"

    # 角色状态提示（完整版功能）
    character_state_hint = ""
    if character_states:
        state_lines = [f"- {name}: {state}" for name, state in character_states.items()]
        character_state_hint = f"\n\n【角色当前状态】\n" + "\n".join(state_lines) + "\n请确保角色行为符合当前状态。"

    # 构建 prompt
    prompt = f"""你是专业小说作家。

【角色基本信息】
{json.dumps(characters, indent=2, ensure_ascii=False)[:400]}{character_state_hint}

{'【前文】' + context if context else '【章节开头】'}

【当前场景要求】（第{num}/{total}段）
{beat}

【风格】{style_hint}
【重点】{focus_text}{critic_hint}

【写作要求】
1. 字数: 250-400字
2. 手法: 展示不告知（Show, don't tell）
3. 细节: 感官描写丰富
4. 对话: 符合角色性格
5. 语言: 简体中文，避免陈词滥调
6. 连贯: {connect_hint}

【关键原则】
⚠️ 重要: 本段只写【当前场景要求】中描述的内容
- 不要跳到下一个场景
- 不要回顾之前的场景（除非衔接需要）
- 聚焦当前场景的核心事件
- 场景结束时自然收尾，不要延伸

【禁忌】
- 少用: 突然、原来、竟然
- 避免: 只见、只听
- 性格: 通过行动展现，不要说明
- 严禁: 偏离当前场景大纲

直接输出段落正文。"""

    for attempt in range(3):
        try:
            llm = ChatAnthropic(
                model="claude-sonnet-4-5-20250929",
                temperature=0.85,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
                anthropic_api_url=os.getenv("ANTHROPIC_BASE_URL"),
                timeout=75.0,
                max_retries=0
            )

            response = llm.invoke([HumanMessage(content=prompt)])
            text = response.content.strip()

            if len(text) < 200:
                if attempt < 2:
                    continue

            return text

        except Exception as e:
            if attempt < 2:
                wait = (attempt + 1) * 4
                print(f"       ⏳ 重试 ({attempt+2}/3)...")
                time.sleep(wait)

    return None


def generate_single_quality(beats, characters, idx, state, tone, focus):
    """单段高质量生成"""

    tones = {
        'serious': '严肃正式',
        'humorous': '轻松幽默',
        'dark': '阴暗压抑',
        'passionate': '激昂热血',
        'romantic': '温柔细腻'
    }
    style = tones.get(tone, '')

    focus_text = '、'.join(focus) if focus else '场景细节'

    prompt = f"""你是专业小说作家。

【角色】
{json.dumps(characters, indent=2, ensure_ascii=False)[:500]}

【大纲】
{beats}

【风格】{style}
【重点】{focus_text}

【要求】
1. 字数: 1500-2000字（严格控制）
2. 展示不告知
3. 感官细节丰富
4. 对话符合性格
5. 简体中文

【禁忌】
少用突然、原来、竟然等词

直接输出正文。"""

    for attempt in range(3):
        try:
            llm = ChatAnthropic(
                model="claude-sonnet-4-5-20250929",
                temperature=0.85,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
                anthropic_api_url=os.getenv("ANTHROPIC_BASE_URL"),
                timeout=75.0,
                max_retries=0
            )

            response = llm.invoke([HumanMessage(content=prompt)])
            draft = f"第 {idx} 章\n\n" + response.content.strip()

            if len(response.content) < 500:
                if attempt < 2:
                    continue

            print(f"     ✅ 完成 ({len(draft)} 字符)")

            # 💾 立即保存章节到文件
            save_chapter_to_file(idx, draft, state)

            return {"draft": draft, "iteration": state.get("iteration", 0) + 1}

        except:
            if attempt < 2:
                print(f"     ⏳ 重试...")
                time.sleep((attempt + 1) * 5)

    fallback = f"第 {idx} 章\n\n{beats}\n\n（生成失败）"
    return {"draft": fallback, "iteration": state.get("iteration", 0) + 1}


def check_quality(text):
    """质量检查"""
    issues = []

    if len(text) < 500:
        issues.append("过短")

    overused = ['突然', '原来', '竟然', '只见', '只听']
    for word in overused:
        count = text.count(word)
        if count > 3:
            issues.append(f"'{word}' 过多({count}次)")

    if '"' not in text and '「' not in text:
        issues.append("缺少对话")

    return issues

def extract_character_states(characters):
    """提取角色当前状态（完整版功能）"""
    states = {}
    for name, char_data in list(characters.items())[:3]:  # 最多3个主要角色
        # 🔧 Bug #12修复: 应该使用recent_notes而不是notes
        notes = char_data.get("recent_notes", char_data.get("notes", []))
        if notes:
            # 获取最新状态
            latest_state = notes[-1] if isinstance(notes[-1], str) else str(notes[-1])
            states[name] = latest_state[:100]  # 限制长度
        else:
            # 使用基本信息
            personality = char_data.get("personality", [])
            if personality:
                states[name] = f"性格: {', '.join(personality[:3])}"
    return states
