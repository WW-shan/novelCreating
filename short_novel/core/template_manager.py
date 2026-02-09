"""
Template management - CRUD operations for plot templates
"""
from pathlib import Path
from typing import Optional
import yaml

# Direct path to avoid import issues when run as script
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def list_templates(category: Optional[str] = None) -> list[dict]:
    """
    List all available templates.

    Args:
        category: Optional filter by category (e.g., "男频", "女频")

    Returns:
        List of dicts with name, category, and path
    """
    templates = []

    search_dirs = [TEMPLATES_DIR / category] if category else TEMPLATES_DIR.iterdir()

    for cat_dir in search_dirs:
        if not cat_dir.is_dir():
            continue
        for yaml_file in cat_dir.glob("*.yaml"):
            templates.append({
                "name": yaml_file.stem,
                "category": cat_dir.name,
                "path": str(yaml_file),
            })

    return sorted(templates, key=lambda x: (x["category"], x["name"]))


def load_template(name: str, category: Optional[str] = None) -> dict:
    """
    Load a template by name.

    Args:
        name: Template name (without .yaml extension)
        category: Optional category to narrow search

    Returns:
        Template data as dict

    Raises:
        FileNotFoundError: If template not found
    """
    # Try direct path first
    if category:
        path = TEMPLATES_DIR / category / f"{name}.yaml"
        if path.exists():
            return yaml.safe_load(path.read_text(encoding="utf-8"))

    # Search all categories
    for template in list_templates():
        if template["name"] == name:
            return yaml.safe_load(Path(template["path"]).read_text(encoding="utf-8"))

    raise FileNotFoundError(f"Template not found: {name}")


def save_template(name: str, category: str, data: dict) -> Path:
    """
    Save a template to the library.

    Args:
        name: Template name
        category: Category (e.g., "男频", "女频")
        data: Template data

    Returns:
        Path to saved file
    """
    cat_dir = TEMPLATES_DIR / category
    cat_dir.mkdir(parents=True, exist_ok=True)

    path = cat_dir / f"{name}.yaml"

    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    return path


def get_template_summary(name: str, category: Optional[str] = None) -> str:
    """
    Get a human-readable summary of a template.

    Args:
        name: Template name
        category: Optional category

    Returns:
        Summary string
    """
    template = load_template(name, category)

    lines = [
        f"【{template.get('name', name)}】",
        f"类型: {template.get('category', '未知')} - {template.get('sub_type', '')}",
        f"标签: {', '.join(template.get('tags', []))}",
        "",
        "读者契约:",
        f"  核心幻想: {template.get('reader_contract', {}).get('core_fantasy', '')}",
        f"  阅读动机: {template.get('reader_contract', {}).get('reading_motivation', '')}",
        "",
        f"主角原型: {template.get('character_system', {}).get('protagonist', {}).get('archetype', '')}",
        f"节拍数量: {len(template.get('plot_engine', {}).get('beats', []))} 个",
    ]

    return "\n".join(lines)
