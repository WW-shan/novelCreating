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
MAX_TOKENS_PER_CHAPTER = 4096
MAX_TOKENS_ANALYSIS = 8192


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
    prompt_template = _load_prompt("generate_setting")

    template_yaml = yaml.dump(template, allow_unicode=True, default_flow_style=False)
    prompt = prompt_template.replace("{template_yaml}", template_yaml)
    prompt = prompt.replace("{user_requirements}", user_requirements or "无特殊要求")

    response = generate(
        system_prompt="你是一个专业的网文创作者。请用中文回答，输出规范的JSON格式。",
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
    prompt_template = _load_prompt("generate_outline")

    template_yaml = yaml.dump(template, allow_unicode=True, default_flow_style=False)
    setting_json = json.dumps(setting, ensure_ascii=False, indent=2)

    prompt = prompt_template.replace("{template_yaml}", template_yaml)
    prompt = prompt.replace("{setting_json}", setting_json)
    prompt = prompt.replace("{total_chapters}", str(total_chapters))

    response = generate(
        system_prompt="你是一个专业的网文大纲策划。请用中文回答，输出规范的JSON格式。",
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
    Generate a single chapter.

    Args:
        template: The plot template
        setting: Character and setting configuration
        outline: Full outline
        chapter_num: Chapter number to generate (1-indexed)
        previous_chapters: List of all previous chapter texts

    Returns:
        Generated chapter text
    """
    prompt_template = _load_prompt("generate_chapter")

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

    # Format previous chapters
    if previous_chapters:
        prev_text = "\n\n---\n\n".join(previous_chapters)
    else:
        prev_text = "（这是第一章，没有前文）"

    # Build prompt
    prompt = prompt_template.replace("{chapter_num}", str(chapter_num))
    prompt = prompt.replace("{writing_style}", writing_style)
    prompt = prompt.replace("{setting_json}", json.dumps(setting, ensure_ascii=False, indent=2))
    prompt = prompt.replace("{chapter_outline}", json.dumps(chapter_outline, ensure_ascii=False, indent=2))
    prompt = prompt.replace("{previous_chapters}", prev_text)
    prompt = prompt.replace("{word_target}", str(chapter_outline.get("word_target", 1500)))

    response = generate(
        system_prompt="你是一个顶级网文写手。直接输出章节正文，不要加任何解释。",
        user_prompt=prompt,
        max_tokens=MAX_TOKENS_PER_CHAPTER,
    )

    return response.strip()


def revise_chapter(
    chapter_text: str,
    feedback: str,
    template: dict,
    setting: dict,
    chapter_outline: dict,
) -> str:
    """
    Revise a chapter based on user feedback.

    Args:
        chapter_text: Current chapter text
        feedback: User's revision notes
        template: The plot template
        setting: Character and setting configuration
        chapter_outline: This chapter's outline

    Returns:
        Revised chapter text
    """
    writing_style = yaml.dump(
        template.get("writing_style", {}),
        allow_unicode=True,
        default_flow_style=False,
    )

    prompt = f"""你是一个顶级网文写手。请根据反馈修改章节。

=== 写作规范 ===
{writing_style}

=== 角色设定 ===
{json.dumps(setting, ensure_ascii=False, indent=2)}

=== 章节大纲 ===
{json.dumps(chapter_outline, ensure_ascii=False, indent=2)}

=== 当前章节内容 ===
{chapter_text}

=== 修改要求 ===
{feedback}

请输出修改后的完整章节，保持格式不变：
"""

    response = generate(
        system_prompt="你是一个顶级网文写手。直接输出修改后的章节正文。",
        user_prompt=prompt,
        max_tokens=MAX_TOKENS_PER_CHAPTER,
    )

    return response.strip()
