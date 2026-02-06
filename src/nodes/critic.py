from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic
from src.state import NovelState
import os
import json
import time

def critic_node(state: NovelState) -> NovelState:
    """
    The Critic Node - comprehensive quality check.
    Evaluates complete content with intelligent truncation.
    支持番茄小说风格评审标准
    """
    print("--- CRITIC NODE ---")

    draft = state.get("draft", "")
    world_bible = state.get("world_bible", {})
    current_beats = state.get("current_beats", "")

    # 智能截取:保留完整段落,避免在句子中间截断
    content_to_check = draft
    max_check_chars = 5000  # 增加到5000字符,足够检查3700字的章节

    if len(draft) > max_check_chars:
        # 截取前5000字符,然后找到最后一个完整段落
        truncated = draft[:max_check_chars]
        # 寻找最后的段落结束位置
        last_paragraph_end = max(
            truncated.rfind('\n\n'),
            truncated.rfind('。\n'),
            truncated.rfind('。"'),
            truncated.rfind('。」')
        )
        if last_paragraph_end > 2000:  # 确保至少有2000字符
            content_to_check = truncated[:last_paragraph_end + 1]
        else:
            content_to_check = truncated

        chars_checked = len(content_to_check)
        total_chars = len(draft)
        coverage = (chars_checked / total_chars) * 100
        print(f"  📏 内容较长,检查前 {chars_checked}/{total_chars} 字符 ({coverage:.0f}% 覆盖,完整段落)")
    else:
        print(f"  📏 检查完整内容 ({len(draft)} 字符)")

    # 提取角色状态和伏笔（完整版功能）
    character_states = extract_character_context(world_bible.get('characters', {}))
    plot_threads = world_bible.get('plot_threads', [])

    # 检查是否为番茄小说风格
    config = state.get('config', {})
    style = config.get('style', {})
    is_fanqie = style.get('is_fanqie_style', False)

    # 构建评审 prompt（完整版：多维度评审）
    prompt_parts = [
        "你是资深小说编辑，进行全面深度评审。",
        "",
        "【角色设定】",
        json.dumps(world_bible.get('characters', {}), ensure_ascii=False)[:600],
        "",
    ]

    # 添加角色状态（如果有）
    if character_states:
        prompt_parts.extend([
            "【角色当前状态】",
            character_states,
            ""
        ])

    # 添加伏笔线索（如果有）
    if plot_threads:
        # 处理不同的数据结构（短篇: list, 长篇: dict with "active"）
        if isinstance(plot_threads, dict):
            # 长篇模式：从 dict 中提取 active threads
            active_threads = plot_threads.get("active", [])[-5:]
        else:
            # 短篇模式：直接使用 list
            active_threads = plot_threads[-5:]

        # 🔧 Bug #9修复: 处理dict格式的thread对象
        formatted_threads = []
        for thread in active_threads:
            if isinstance(thread, dict):
                # 长篇模式: thread是 {"text": "...", ...}
                formatted_threads.append(thread.get("text", str(thread)))
            else:
                # 短篇模式: thread是字符串
                formatted_threads.append(str(thread))

        threads_text = "\n".join([f"- {t}" for t in formatted_threads])

        if threads_text:  # 只有在有内容时才添加
            prompt_parts.extend([
                "【现有伏笔/谜团】",
                threads_text,
                ""
            ])

    prompt_parts.extend([
        "【场景大纲】",
        current_beats[:400] if current_beats else "(无)",
        "",
        "【生成内容】",
        content_to_check,
        "",
    ])

    # 根据风格选择评审标准
    if is_fanqie:
        print("  🎯 使用番茄小说评审标准")
        prompt_parts.extend([
            "【评审维度 - 番茄小说标准】",
            "1. **节奏速度**: 是否开门见山，直接进入冲突，无冗长铺垫",
            "2. **爽点密度**: 每章至少2-3个爽点（打脸/反转/收获/碾压）",
            "3. **对比强烈**: 是否有别人vs主角的强烈对比",
            "4. **简洁直白**: 避免过度心理描写，多用动作和对话",
            "5. **主角强势**: 主角是否智商在线、行动果断、占据主动",
            "",
            "【番茄风格要求】",
            "- 冲突→爽点→冲突→爽点，快节奏推进",
            "- 避免纯铺垫场景，每个场景都要有冲突或收获",
            "- 打脸要狠，反转要快，不拖泥带水",
            "",
            "【回答格式】",
            "- 如果通过: '通过 - 爽点: [具体爽点]'",
            "- 如果需修改: '需修改 - 问题: [节奏/爽点/对比等具体问题]'",
            "",
            "请按番茄小说标准评审。"
        ])
    else:
        print("  📖 使用传统文学评审标准")
        prompt_parts.extend([
            "【评审维度】",
            "1. **角色一致性**: 行为/对话是否符合角色性格和当前状态",
            "2. **场景覆盖**: 是否覆盖所有场景大纲要点",
            "3. **逻辑合理性**: 情节发展是否合理，有无明显漏洞",
            "4. **伏笔处理**: 如有伏笔，是否自然融入或推进",
            "5. **文笔质量**: 是否展示不告知，细节是否丰富",
            "",
            "【回答格式】",
            "- 如果通过: '通过 - 亮点: [具体说明]'",
            "- 如果需修改: '需修改 - 问题: [具体问题]'",
            "",
            "请给出专业评审。"
        ])

    prompt = '\n'.join(prompt_parts)

    max_attempts = 2
    for attempt in range(max_attempts):
        try:
            llm = ChatAnthropic(
                model="claude-sonnet-4-5-20250929",
                temperature=0.3,  # 稍高温度,更灵活的评审
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
                anthropic_api_url=os.getenv("ANTHROPIC_BASE_URL"),
                timeout=90.0,  # 增加到90秒,避免评审超时
                max_retries=0
            )

            response = llm.invoke([HumanMessage(content=prompt)])
            feedback = response.content.strip()

            print(f"  ✅ 评审完成")

            # 显示评审结果摘要 (优先检查"需修改"，因为这是更重要的状态)
            if "需修改" in feedback or "不合格" in feedback:
                print(f"     状态: ⚠️  需改进")
            elif "通过" in feedback or "合格" in feedback:
                print(f"     状态: ✅ 通过")
            else:
                print(f"     状态: ❓ 未知")

            return {"feedback": feedback}

        except Exception as e:
            if attempt < max_attempts - 1:
                wait = (attempt + 1) * 4
                print(f"  ⏳ 评审超时,重试 ({attempt+2}/{max_attempts})...")
                time.sleep(wait)
            else:
                print(f"  ⚠️  评审超时,使用快速检查")
                # 快速本地检查
                local_feedback = quick_local_check(draft, world_bible, is_fanqie)
                return {"feedback": local_feedback}


def quick_local_check(draft, world_bible, is_fanqie=False):
    """无AI的快速本地质量检查"""
    issues = []

    # 检查长度
    if len(draft) < 800:
        issues.append("内容过短")

    if is_fanqie:
        # 番茄小说专用检查
        # 检查节奏（避免过长段落）
        paragraphs = draft.split('\n\n')
        long_paragraphs = [p for p in paragraphs if len(p) > 500]
        if len(long_paragraphs) > 2:
            issues.append("段落过长，节奏拖沓")

        # 检查对话（番茄小说需要更多对话）
        dialogue_count = draft.count('「') + draft.count('"') + draft.count('"')
        if dialogue_count < 4 and len(draft) > 1000:
            issues.append("对话太少，需要更多直接对话")

        # 检查爽点关键词
        shuangdian_keywords = ['碾压', '打脸', '震惊', '不敢相信', '怎么可能', '收获', '突破']
        has_shuangdian = any(kw in draft for kw in shuangdian_keywords)
        if not has_shuangdian and len(draft) > 1500:
            issues.append("缺少爽点元素（打脸/碾压/收获）")

    else:
        # 传统文学检查
        # 检查过度使用的词汇
        overused_words = ['突然', '原来', '竟然', '只见', '只听']
        for word in overused_words:
            count = draft.count(word)
            if count > 4:
                issues.append(f"'{word}'使用过多({count}次)")

        # 检查是否有对话
        has_dialogue = ('「' in draft or '"' in draft or '"' in draft or
                        '「' in draft or '『' in draft)
        if not has_dialogue and len(draft) > 1000:
            issues.append("缺少对话")

    # 检查角色名称是否出现
    characters = world_bible.get('characters', {})
    char_mentioned = False
    for char_name in characters.keys():
        if char_name in draft:
            char_mentioned = True
            break

    if not char_mentioned and characters:
        issues.append("未提及主要角色")

    if issues:
        return f"需改进: {'; '.join(issues[:3])}"
    else:
        style_type = "番茄小说标准" if is_fanqie else "传统标准"
        return f"通过(本地检查/{style_type}): 内容长度适中,格式合理,包含必要元素"


def extract_character_context(characters):
    """提取角色上下文（完整版功能）"""
    lines = []
    for name, char_data in list(characters.items())[:3]:
        notes = char_data.get("notes", [])
        if notes:
            latest = notes[-1] if isinstance(notes[-1], str) else str(notes[-1])
            lines.append(f"- {name}: {latest[:80]}")
    return "\n".join(lines) if lines else ""
