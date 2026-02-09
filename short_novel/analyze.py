#!/usr/bin/env python3
"""
Template Analyzer - Extract reusable plot templates from successful novels
"""
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import yaml
from core.scraper import fetch_url
from core.analyzer import analyze_novel
from core.template_manager import save_template


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def get_novel_text() -> str:
    """Get novel text from user (paste or URL)."""
    print_header("短篇小说模板分析器")

    print("请选择输入方式：")
    print("  1. 粘贴小说文本")
    print("  2. 输入URL（实验性功能）")
    print()

    choice = input("选择 [1/2]: ").strip()

    if choice == "2":
        url = input("\n请输入URL: ").strip()
        print("\n正在获取内容...")
        text = fetch_url(url)
        if text:
            print(f"成功获取 {len(text)} 字符")
            preview = text[:200] + "..." if len(text) > 200 else text
            print(f"\n预览：\n{preview}\n")
            confirm = input("是否使用此内容？[Y/n]: ").strip().lower()
            if confirm != "n":
                return text
        print("\nURL获取失败或内容不合适，请改用粘贴方式")

    print("\n请粘贴小说全文（粘贴完成后输入 END 并回车）：\n")
    lines = []
    while True:
        try:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        except EOFError:
            break

    text = "\n".join(lines)
    print(f"\n已接收 {len(text)} 字符")
    return text


def progress_callback(message: str):
    """Display analysis progress."""
    print(f"\n>>> {message}")


def main():
    # Get novel text
    novel_text = get_novel_text()

    if len(novel_text) < 1000:
        print("\n错误：文本太短，请提供完整的小说内容")
        return

    print_header("开始四轮分析")

    try:
        # Run analysis
        structure, emotion, technique, template_yaml = analyze_novel(
            novel_text,
            progress_callback=progress_callback,
        )

        print("\n" + "-" * 40)
        print("分析完成！")
        print("-" * 40)

        # Show template preview
        print("\n生成的模板预览：")
        print("-" * 40)
        preview_lines = template_yaml.split("\n")[:30]
        print("\n".join(preview_lines))
        if len(template_yaml.split("\n")) > 30:
            print("... (更多内容)")
        print("-" * 40)

        # Get template info
        print("\n请提供模板保存信息：")
        name = input("模板名称（如：赘婿逆袭）: ").strip()
        if not name:
            name = "未命名模板"

        print("\n选择类别：")
        print("  1. 男频")
        print("  2. 女频")
        cat_choice = input("选择 [1/2]: ").strip()
        category = "女频" if cat_choice == "2" else "男频"

        # Parse YAML and save
        template_data = yaml.safe_load(template_yaml)
        template_data["name"] = name

        saved_path = save_template(name, category, template_data)
        print(f"\n✓ 模板已保存至：{saved_path}")

        # Ask if user wants to edit
        print("\n是否要编辑模板文件？")
        edit = input("[y/N]: ").strip().lower()
        if edit == "y":
            print(f"\n请手动编辑文件：{saved_path}")

        print("\n分析完成！可以使用 generate.py 基于此模板生成新小说。")

    except KeyboardInterrupt:
        print("\n\n已取消")
    except Exception as e:
        print(f"\n错误：{e}")
        raise


if __name__ == "__main__":
    main()
