"""
Novel Generator - Setting, outline, and chapter generation
"""
import json
import re
from pathlib import Path
from typing import Optional
import yaml

from .ai_client import generate

# Direct paths to avoid import issues
PROMPTS_DIR = Path(__file__).parent / "prompts"
MAX_TOKENS_PER_PART = 1500  # 每个部分限制输出，防止代理超时
MAX_TOKENS_ANALYSIS = 4000  # 分析类也限制一下
PARTS_PER_CHAPTER = 2  # 每章分2部分生成


def _load_prompt(name: str) -> str:
    """Load a prompt template from file."""
    path = PROMPTS_DIR / f"{name}.txt"
    return path.read_text(encoding="utf-8")


def _extract_json(text: str) -> dict:
    """Extract JSON from model response."""
    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if json_match:
        json_str = json_match.group(1).strip()
    else:
        json_str = text.strip()

    json_str = re.sub(r",\s*}", "}", json_str)
    json_str = re.sub(r",\s*]", "]", json_str)

    return json.loads(json_str)


def generate_setting(
    template: dict,
    user_requirements: str = "",
) -> dict:
    """
    Generate character and setting based on template.

    Args:
        template: The plot template
        user_requirements: Optional user-specified requirements

    Returns:
        Setting configuration as dict
    """
    # 简化模板，只取关键信息
    simplified_template = {
        "name": template.get("name", ""),
        "category": template.get("category", ""),
        "reader_contract": template.get("reader_contract", {}),
        "character_system": template.get("character_system", {}),
    }

    template_yaml = yaml.dump(simplified_template, allow_unicode=True, default_flow_style=False)

    prompt = f"""根据以下模板生成角色设定。

{template_yaml}

用户要求：{user_requirements or "无特殊要求"}

输出JSON格式，包含：
- title: 小说标题
- protagonist: {{name, hidden_identity, public_identity}}
- female_lead: {{name, identity, relationship}}
- antagonists: [{{name, identity, level}}] (3个)
- setting: {{time_period, location}}

直接输出JSON："""

    response = generate(
        system_prompt="网文设定师。只输出JSON，不要解释。",
        user_prompt=prompt,
        max_tokens=MAX_TOKENS_ANALYSIS,
    )

    return _extract_json(response)


def generate_outline(
    template: dict,
    setting: dict,
    total_chapters: int = 10,
) -> dict:
    """
    Generate chapter-by-chapter outline.

    Args:
        template: The plot template
        setting: Character and setting configuration
        total_chapters: Number of chapters to plan

    Returns:
        Outline as dict with chapters list
    """
    # 简化设定信息
    setting_brief = {
        "title": setting.get("title", ""),
        "protagonist": setting.get("protagonist", {}),
        "female_lead": setting.get("female_lead", {}),
    }

    # 提取节拍信息
    beats = template.get("plot_engine", {}).get("beats", [])
    beats_brief = [{"name": b.get("name", ""), "goal": b.get("story_goal", "")} for b in beats]

    prompt = f"""为小说生成{total_chapters}章大纲。

角色：
{json.dumps(setting_brief, ensure_ascii=False)}

节拍参考：
{json.dumps(beats_brief, ensure_ascii=False)}

输出JSON格式：
{{"chapters": [
  {{"chapter_num": 1, "title": "标题", "story_goal": "本章目标", "word_target": 1500}},
  ...
]}}

直接输出JSON："""

    response = generate(
        system_prompt="网文大纲师。只输出JSON。",
        user_prompt=prompt,
        max_tokens=MAX_TOKENS_ANALYSIS,
    )

    return _extract_json(response)


def generate_chapter(
    template: dict,
    setting: dict,
    outline: dict,
    chapter_num: int,
    previous_chapters: list[str],
) -> str:
    """
    Generate a single chapter in multiple parts to prevent timeout.

    Args:
        template: The plot template
        setting: Character and setting configuration
        outline: Full outline
        chapter_num: Chapter number to generate (1-indexed)
        previous_chapters: List of all previous chapter texts

    Returns:
        Generated chapter text (combined from all parts)
    """
    # Get this chapter's outline
    chapter_outline = None
    for ch in outline.get("chapters", []):
        if ch.get("chapter_num") == chapter_num:
            chapter_outline = ch
            break

    if not chapter_outline:
        raise ValueError(f"Chapter {chapter_num} not found in outline")

    # Extract writing style from template
    writing_style = yaml.dump(
        template.get("writing_style", {}),
        allow_unicode=True,
        default_flow_style=False,
    )

    # Get previous chapter summary (not full text, to save tokens)
    if previous_chapters:
        # Only use last chapter's ending for context
        last_chapter = previous_chapters[-1]
        prev_context = last_chapter[-500:] if len(last_chapter) > 500 else last_chapter
    else:
        prev_context = "（这是第一章开头）"

    word_target = chapter_outline.get("word_target", 1500)
    words_per_part = word_target // PARTS_PER_CHAPTER

    # Generate chapter in parts
    chapter_parts = []

    for part_num in range(1, PARTS_PER_CHAPTER + 1):
        print(f"    生成第{chapter_num}章 ({part_num}/{PARTS_PER_CHAPTER})...")

        if part_num == 1:
            # First part - use previous chapter context
            part_context = f"上一章结尾：\n{prev_context}"
            part_instruction = f"写本章的开头部分，约{words_per_part}字。建立场景，引入冲突。"
        else:
            # Subsequent parts - use previous part
            prev_part = chapter_parts[-1]
            part_context = f"本章前文：\n{prev_part[-600:]}"
            if part_num == PARTS_PER_CHAPTER:
                part_instruction = f"写本章的结尾部分，约{words_per_part}字。推向高潮，留下钩子。"
            else:
                part_instruction = f"继续写本章中间部分，约{words_per_part}字。发展冲突，推进剧情。"

        prompt = f"""你是顶级网文写手，正在写一部番茄小说。

=== 写作风格要求 ===
{writing_style}

=== 角色设定 ===
{json.dumps(setting, ensure_ascii=False, indent=2)}

=== 本章大纲 ===
{json.dumps(chapter_outline, ensure_ascii=False, indent=2)}

=== 上下文 ===
{part_context}

=== 任务 ===
{part_instruction}

要求：
1. 直接输出正文，不要标题或解释
2. 对话占比60%以上
3. 每段不超过3行
4. 与前文保持人名、情节一致

现在开始写："""

        response = generate(
            system_prompt="你是番茄小说签约作者。直接输出小说正文，不要任何解释或标题。",
            user_prompt=prompt,
            max_tokens=MAX_TOKENS_PER_PART,
        )

        chapter_parts.append(response.strip())

    # Combine all parts
    full_chapter = "\n\n".join(chapter_parts)
    return full_chapter


def revise_chapter(
    chapter_text: str,
    feedback: str,
    template: dict,
    setting: dict,
    chapter_outline: dict,
) -> str:
    """
    Revise a chapter based on user feedback.
    Split into parts to prevent timeout.
    """
    # 章节太长时分段修改
    if len(chapter_text) > 1500:
        mid = len(chapter_text) // 2
        # 找到中间的段落分隔点
        split_point = chapter_text.rfind("\n\n", 0, mid + 200)
        if split_point == -1:
            split_point = mid

        part1 = chapter_text[:split_point]
        part2 = chapter_text[split_point:]

        # 修改第一部分
        print("    修改前半部分...")
        revised1 = _revise_part(part1, feedback, setting, chapter_outline, "前半部分")

        # 修改第二部分
        print("    修改后半部分...")
        revised2 = _revise_part(part2, feedback, setting, chapter_outline, "后半部分", revised1[-300:])

        return revised1 + "\n\n" + revised2
    else:
        return _revise_part(chapter_text, feedback, setting, chapter_outline, "全文")


def _revise_part(
    text: str,
    feedback: str,
    setting: dict,
    chapter_outline: dict,
    part_name: str,
    prev_context: str = "",
) -> str:
    """Revise a single part of chapter."""
    context_info = f"\n前文结尾：{prev_context}" if prev_context else ""

    prompt = f"""修改以下小说片段（{part_name}）。

角色：主角={setting.get('protagonist', {}).get('name', '主角')}
本章目标：{chapter_outline.get('story_goal', '')}
{context_info}

原文：
{text}

修改要求：{feedback}

直接输出修改后的正文："""

    response = generate(
        system_prompt="网文写手。直接输出修改后的正文，不要解释。",
        user_prompt=prompt,
        max_tokens=MAX_TOKENS_PER_PART,
    )

    return response.strip()
