"""
Template Analyzer - Four-round novel analysis
"""
import json
import re
from pathlib import Path
from typing import Callable, Optional

from .ai_client import generate
from .template_manager import save_template

# Direct paths to avoid import issues
PROMPTS_DIR = Path(__file__).parent / "prompts"
MAX_TOKENS_ANALYSIS = 8192


def _load_prompt(name: str) -> str:
    """Load a prompt template from file."""
    path = PROMPTS_DIR / f"{name}.txt"
    return path.read_text(encoding="utf-8")


def _extract_json(text: str) -> dict:
    """Extract JSON from model response."""
    # Try to find JSON block
    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if json_match:
        json_str = json_match.group(1).strip()
    else:
        # Try to find raw JSON
        json_str = text.strip()

    # Clean up common issues
    json_str = re.sub(r",\s*}", "}", json_str)
    json_str = re.sub(r",\s*]", "]", json_str)

    return json.loads(json_str)


def _extract_yaml(text: str) -> str:
    """Extract YAML from model response."""
    yaml_match = re.search(r"```(?:yaml)?\s*([\s\S]*?)```", text)
    if yaml_match:
        return yaml_match.group(1).strip()
    return text.strip()


def analyze_structure(
    novel_text: str,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> dict:
    """
    Round 1: Analyze novel structure.

    Args:
        novel_text: Full text of the novel
        progress_callback: Optional callback for progress updates

    Returns:
        Structure analysis as dict
    """
    if progress_callback:
        progress_callback("第一轮分析：结构分解...")

    prompt = _load_prompt("analyze_structure")
    full_prompt = prompt + "\n\n" + novel_text

    response = generate(
        system_prompt="你是一个专业的网文结构分析师。请用中文回答，输出规范的JSON格式。",
        user_prompt=full_prompt,
        max_tokens=MAX_TOKENS_ANALYSIS,
    )

    return _extract_json(response)


def analyze_emotion(
    novel_text: str,
    structure: dict,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> dict:
    """
    Round 2: Analyze emotion curves.

    Args:
        novel_text: Full text of the novel
        structure: Result from round 1
        progress_callback: Optional callback for progress updates

    Returns:
        Emotion analysis as dict
    """
    if progress_callback:
        progress_callback("第二轮分析：情绪曲线...")

    prompt_template = _load_prompt("analyze_emotion")
    prompt = prompt_template.replace("{structure_json}", json.dumps(structure, ensure_ascii=False, indent=2))
    full_prompt = prompt + "\n\n" + novel_text

    response = generate(
        system_prompt="你是一个专业的读者情绪分析师。请用中文回答，输出规范的JSON格式。",
        user_prompt=full_prompt,
        max_tokens=MAX_TOKENS_ANALYSIS,
    )

    return _extract_json(response)


def analyze_technique(
    novel_text: str,
    structure: dict,
    emotion: dict,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> dict:
    """
    Round 3: Extract writing techniques.

    Args:
        novel_text: Full text of the novel
        structure: Result from round 1
        emotion: Result from round 2
        progress_callback: Optional callback for progress updates

    Returns:
        Technique analysis as dict
    """
    if progress_callback:
        progress_callback("第三轮分析：写作技巧...")

    prompt_template = _load_prompt("analyze_technique")
    prompt = prompt_template.replace("{structure_json}", json.dumps(structure, ensure_ascii=False, indent=2))
    prompt = prompt.replace("{emotion_json}", json.dumps(emotion, ensure_ascii=False, indent=2))
    full_prompt = prompt + "\n\n" + novel_text

    response = generate(
        system_prompt="你是一个专业的网文写作技巧分析师。请用中文回答，输出规范的JSON格式。",
        user_prompt=full_prompt,
        max_tokens=MAX_TOKENS_ANALYSIS,
    )

    return _extract_json(response)


def abstract_to_template(
    novel_text: str,
    structure: dict,
    emotion: dict,
    technique: dict,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> str:
    """
    Round 4: Abstract to reusable template.

    Args:
        novel_text: Full text of the novel
        structure: Result from round 1
        emotion: Result from round 2
        technique: Result from round 3
        progress_callback: Optional callback for progress updates

    Returns:
        Template as YAML string
    """
    if progress_callback:
        progress_callback("第四轮分析：抽象为模板...")

    prompt_template = _load_prompt("analyze_abstract")
    prompt = prompt_template.replace("{structure_json}", json.dumps(structure, ensure_ascii=False, indent=2))
    prompt = prompt.replace("{emotion_json}", json.dumps(emotion, ensure_ascii=False, indent=2))
    prompt = prompt.replace("{technique_json}", json.dumps(technique, ensure_ascii=False, indent=2))
    full_prompt = prompt + "\n\n" + novel_text

    response = generate(
        system_prompt="你是一个专业的网文模板设计师。请用中文回答，输出规范的YAML格式。",
        user_prompt=full_prompt,
        max_tokens=MAX_TOKENS_ANALYSIS,
    )

    return _extract_yaml(response)


def analyze_novel(
    novel_text: str,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> tuple[dict, dict, dict, str]:
    """
    Run full four-round analysis on a novel.

    Args:
        novel_text: Full text of the novel
        progress_callback: Optional callback for progress updates

    Returns:
        Tuple of (structure, emotion, technique, template_yaml)
    """
    structure = analyze_structure(novel_text, progress_callback)
    emotion = analyze_emotion(novel_text, structure, progress_callback)
    technique = analyze_technique(novel_text, structure, emotion, progress_callback)
    template_yaml = abstract_to_template(novel_text, structure, emotion, technique, progress_callback)

    return structure, emotion, technique, template_yaml
