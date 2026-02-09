#!/usr/bin/env python3
"""
Novel Generator - Generate short novels from templates
"""
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import yaml
from core.template_manager import list_templates, load_template, get_template_summary
from core.generator import generate_setting, generate_outline, generate_chapter, revise_chapter

# Direct path to avoid import issues
STORIES_DIR = Path(__file__).parent / "stories"
STORIES_DIR.mkdir(exist_ok=True)


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def select_template() -> dict:
    """Let user select a template from library."""
    templates = list_templates()

    if not templates:
        print("错误：模板库为空。请先使用 analyze.py 创建模板。")
        sys.exit(1)

    print("可用模板：\n")
    for i, t in enumerate(templates, 1):
        print(f"  {i}. [{t['category']}] {t['name']}")

    print()
    while True:
        choice = input(f"选择模板 [1-{len(templates)}]: ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(templates):
                template = load_template(templates[idx]["name"])
                print(f"\n已选择：{templates[idx]['name']}")
                print("\n" + get_template_summary(templates[idx]["name"]))
                return template
        except (ValueError, IndexError):
            pass
        print("无效选择，请重试")


def get_setting(template: dict) -> dict:
    """Generate or load setting."""
    print_header("角色与设定")

    print("选择设定方式：")
    print("  1. AI自动生成设定")
    print("  2. 从文件加载设定")
    print()

    choice = input("选择 [1/2]: ").strip()

    if choice == "2":
        path = input("请输入设定文件路径: ").strip()
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"加载失败：{e}，将自动生成")

    print("\n请输入任何特殊要求（直接回车跳过）：")
    requirements = input("> ").strip()

    print("\n正在生成角色设定...")
    setting = generate_setting(template, requirements)

    # Show setting
    print("\n生成的设定：")
    print("-" * 40)
    print(f"标题：{setting.get('title', '未命名')}")
    print(f"主角：{setting.get('protagonist', {}).get('name', '?')} - {setting.get('protagonist', {}).get('hidden_identity', '?')}")
    print(f"女主：{setting.get('female_lead', {}).get('name', '?')}")
    print(f"反派：{len(setting.get('antagonists', []))} 个")
    print("-" * 40)

    # Confirm
    confirm = input("\n确认使用此设定？[Y/n]: ").strip().lower()
    if confirm == "n":
        print("重新生成...")
        return get_setting(template)

    return setting


def get_outline(template: dict, setting: dict) -> dict:
    """Generate or load outline."""
    print_header("章节大纲")

    chapters_input = input("总章节数 [默认10]: ").strip()
    total_chapters = int(chapters_input) if chapters_input.isdigit() else 10

    print(f"\n正在生成 {total_chapters} 章大纲...")
    outline = generate_outline(template, setting, total_chapters)

    # Show outline
    print("\n大纲预览：")
    print("-" * 40)
    for ch in outline.get("chapters", []):
        print(f"第{ch['chapter_num']}章：{ch.get('title', '')} - {ch.get('story_goal', '')[:30]}...")
    print("-" * 40)

    # Confirm
    confirm = input("\n确认大纲？[Y/n]: ").strip().lower()
    if confirm == "n":
        print("重新生成...")
        return get_outline(template, setting)

    return outline


def create_story_dir(title: str) -> Path:
    """Create directory for new story."""
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c for c in title if c.isalnum() or c in "_ -")[:20]
    dir_name = f"{safe_title}_{date_str}"

    story_dir = STORIES_DIR / dir_name
    story_dir.mkdir(parents=True, exist_ok=True)
    (story_dir / "chapters").mkdir(exist_ok=True)

    return story_dir


def generate_chapters(
    template: dict,
    setting: dict,
    outline: dict,
    story_dir: Path,
):
    """Generate chapters one by one with user review."""
    chapters = []
    total = len(outline.get("chapters", []))

    for chapter_num in range(1, total + 1):
        print_header(f"生成第 {chapter_num}/{total} 章")

        # Generate
        print("正在生成...")
        chapter_text = generate_chapter(
            template,
            setting,
            outline,
            chapter_num,
            chapters,
        )

        # Save draft
        chapter_path = story_dir / "chapters" / f"chapter_{chapter_num:02d}.md"
        chapter_path.write_text(chapter_text, encoding="utf-8")

        # Show preview
        print("\n" + "-" * 40)
        preview = chapter_text[:500] + "..." if len(chapter_text) > 500 else chapter_text
        print(preview)
        print("-" * 40)
        print(f"\n完整内容已保存至：{chapter_path}")
        print(f"字数：{len(chapter_text)} 字")

        # User review
        while True:
            print("\n操作选项：")
            print("  1. 确认，继续下一章")
            print("  2. 重新生成此章")
            print("  3. 提供反馈修改")
            print("  4. 手动编辑后继续")
            print("  5. 保存进度并退出")
            print()

            action = input("选择 [1-5]: ").strip()

            if action == "1":
                chapters.append(chapter_text)
                break

            elif action == "2":
                print("\n重新生成...")
                chapter_text = generate_chapter(
                    template, setting, outline, chapter_num, chapters
                )
                chapter_path.write_text(chapter_text, encoding="utf-8")
                preview = chapter_text[:500] + "..."
                print("\n" + "-" * 40)
                print(preview)
                print("-" * 40)

            elif action == "3":
                feedback = input("\n请输入修改意见: ").strip()
                if feedback:
                    print("\n正在修改...")
                    chapter_outline = outline["chapters"][chapter_num - 1]
                    chapter_text = revise_chapter(
                        chapter_text, feedback, template, setting, chapter_outline
                    )
                    chapter_path.write_text(chapter_text, encoding="utf-8")
                    preview = chapter_text[:500] + "..."
                    print("\n" + "-" * 40)
                    print(preview)
                    print("-" * 40)

            elif action == "4":
                input("\n请编辑文件后按回车继续...")
                chapter_text = chapter_path.read_text(encoding="utf-8")
                chapters.append(chapter_text)
                break

            elif action == "5":
                save_progress(story_dir, template, setting, outline, chapters)
                print(f"\n进度已保存至：{story_dir}")
                print("下次可从此目录继续")
                sys.exit(0)

    return chapters


def save_progress(
    story_dir: Path,
    template: dict,
    setting: dict,
    outline: dict,
    chapters: list,
):
    """Save current progress."""
    # Save config
    config = {
        "template": template,
        "setting": setting,
        "outline": outline,
        "completed_chapters": len(chapters),
    }
    with open(story_dir / "config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)


def main():
    print_header("短篇小说生成器")

    # Step 1: Select template
    print("第一步：选择模板\n")
    template = select_template()

    # Step 2: Generate/load setting
    setting = get_setting(template)

    # Create story directory
    story_dir = create_story_dir(setting.get("title", "未命名"))
    print(f"\n项目目录：{story_dir}")

    # Step 3: Generate outline
    outline = get_outline(template, setting)

    # Save initial config
    save_progress(story_dir, template, setting, outline, [])

    # Step 4: Generate chapters
    print_header("开始生成章节")
    chapters = generate_chapters(template, setting, outline, story_dir)

    # Final save
    save_progress(story_dir, template, setting, outline, chapters)

    # Combine all chapters
    full_novel = "\n\n---\n\n".join(chapters)
    full_path = story_dir / "full_novel.md"
    full_path.write_text(full_novel, encoding="utf-8")

    print_header("生成完成！")
    print(f"总字数：{len(full_novel)} 字")
    print(f"完整小说：{full_path}")
    print(f"分章节：{story_dir / 'chapters'}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消")
    except Exception as e:
        print(f"\n错误：{e}")
        raise
