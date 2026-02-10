"""
Novel Generator - Setting, outline, and chapter generation
"""
import json
import re
import random
from pathlib import Path
from typing import Optional
import yaml

from .ai_client import generate

# Direct paths to avoid import issues
PROMPTS_DIR = Path(__file__).parent / "prompts"
MAX_TOKENS_PER_CHAPTER = 1800  # 约1000字输出
MAX_TOKENS_ANALYSIS = 4000

# 随机人名库
MALE_NAMES = ["陈默", "林风", "张远", "王浩", "李明", "赵阳", "周毅", "吴凡", "郑宇", "孙强", "刘峰", "杨磊"]
FEMALE_NAMES = ["苏晴", "林婉", "陈雨", "王璇", "李婷", "赵雪", "周琳", "吴梦", "郑薇", "孙萌", "刘诗", "杨柳"]
VILLAIN_NAMES = ["钱少", "周公子", "赵董", "孙总", "马老板", "刘少爷", "王董事"]


def get_random_names() -> dict:
    """生成随机角色名"""
    male = random.choice(MALE_NAMES)
    female = random.choice(FEMALE_NAMES)
    # 确保姓不同
    while female[0] == male[0]:
        female = random.choice(FEMALE_NAMES)
    villain = random.choice(VILLAIN_NAMES)
    return {"male": male, "female": female, "villain": villain}


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
    Uses random names for each generation.

    Args:
        template: The plot template
        user_requirements: Optional user-specified requirements

    Returns:
        Setting configuration as dict
    """
    # 获取随机角色名
    names = get_random_names()

    # 完整模板信息
    template_yaml = yaml.dump(template, allow_unicode=True, default_flow_style=False)

    prompt = f"""根据以下模板生成角色设定。

{template_yaml}

使用以下角色名：
- 主角名：{names['male']}
- 女主名：{names['female']}
- 主要反派：{names['villain']}

用户要求：{user_requirements or "无特殊要求"}

输出JSON格式，包含：
- title: 小说标题
- protagonist: {{name: "{names['male']}", hidden_identity, public_identity}}
- female_lead: {{name: "{names['female']}", identity, relationship}}
- antagonists: [{{name: "{names['villain']}", identity, level}}, ...] (3个反派)
- setting: {{time_period, location}}

直接输出JSON："""

    response = generate(
        system_prompt="网文设定师。只输出JSON，不要解释。必须使用指定的角色名。",
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
    template_yaml = yaml.dump(template, allow_unicode=True, default_flow_style=False)
    setting_json = json.dumps(setting, ensure_ascii=False, indent=2)

    prompt = f"""为小说生成{total_chapters}章大纲。

模板：
{template_yaml}

角色设定：
{setting_json}

输出JSON格式：
{{"chapters": [
  {{"chapter_num": 1, "title": "标题", "story_goal": "本章目标", "word_target": 1000}},
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
    Generate a single chapter (~1000 words).
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

    # Full previous chapters for context (quality first)
    if previous_chapters:
        prev_context = "\n\n---\n\n".join(previous_chapters)
    else:
        prev_context = "（这是第一章开头）"

    prompt = f"""你是顶级网文写手，正在写一部番茄小说。

=== 写作风格要求 ===
{writing_style}

=== 角色设定 ===
{json.dumps(setting, ensure_ascii=False, indent=2)}

=== 完整大纲 ===
{json.dumps(outline, ensure_ascii=False, indent=2)}

=== 本章大纲 ===
{json.dumps(chapter_outline, ensure_ascii=False, indent=2)}

=== 前文内容 ===
{prev_context}

=== 任务 ===
写完整的第{chapter_num}章，约1000字。

要求：
1. 直接输出正文，不要标题或解释
2. 对话占比60%以上
3. 每段不超过3行
4. 结尾留钩子
5. 与前文保持人名、情节一致
6. 严格控制在1000字左右

现在开始写："""

    response = generate(
        system_prompt="你是番茄小说签约作者。直接输出小说正文，不要任何解释或标题。字数严格控制在1000字左右。",
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
    """Revise a chapter based on user feedback."""
    prompt = f"""修改以下小说章节。

角色：主角={setting.get('protagonist', {}).get('name', '主角')}
本章目标：{chapter_outline.get('story_goal', '')}

原文：
{chapter_text}

修改要求：{feedback}

直接输出修改后的完整正文，约1000字："""

    response = generate(
        system_prompt="网文写手。直接输出修改后的正文，不要解释。字数控制在1000字。",
        user_prompt=prompt,
        max_tokens=MAX_TOKENS_PER_CHAPTER,
    )

    return response.strip()
