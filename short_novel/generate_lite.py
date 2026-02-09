#!/usr/bin/env python3
"""
轻量级短篇小说生成器 - 分段生成，节省API调用
"""
import sys
import random
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from core.ai_client import generate

# 常用人名库
MALE_NAMES = [
    "陈默", "林风", "张远", "王浩", "李明", "赵阳", "周毅", "吴凡",
    "郑宇", "孙强", "刘峰", "杨磊", "黄涛", "周昊", "徐鹏", "马超"
]
FEMALE_NAMES = [
    "苏晴", "林婉", "陈雨", "王璇", "李婷", "赵雪", "周琳", "吴梦",
    "郑薇", "孙萌", "刘诗", "杨柳", "黄莺", "周瑶", "徐静", "马悦"
]
SURNAMES = ["陈", "林", "张", "王", "李", "赵", "周", "吴", "郑", "孙", "刘", "杨"]


def random_names():
    """生成随机人名"""
    male = random.choice(MALE_NAMES)
    female = random.choice(FEMALE_NAMES)
    # 确保姓不同
    while female[0] == male[0]:
        female = random.choice(FEMALE_NAMES)
    villain = random.choice(SURNAMES) + random.choice(["总", "董", "少", "公子"])
    return {"male": male, "female": female, "villain": villain}


def generate_simple_outline(genre: str, names: dict) -> str:
    """生成简单大纲 - 轻量调用"""
    prompt = f"""为一篇1万字的短篇网文生成简要大纲。

类型: {genre}
主角: {names['male']}
女主: {names['female']}
反派: {names['villain']}

要求:
- 分5章，每章约2000字
- 只输出每章的一句话概要
- 格式: 第X章: 概要

直接输出，不要其他内容:"""

    return generate(
        system_prompt="你是网文大纲师。简洁输出。",
        user_prompt=prompt,
        max_tokens=500,
    )


def generate_chapter_lite(
    chapter_num: int,
    total_chapters: int,
    outline: str,
    names: dict,
    genre: str,
    previous_summary: str = "",
) -> str:
    """生成单章 - 控制在1000字左右"""

    prompt = f"""写第{chapter_num}章（共{total_chapters}章），约1000-1200字。

【类型】{genre}
【主角】{names['male']}（隐藏身份的强者）
【女主】{names['female']}（主角的妻子/女友）
【反派】{names['villain']}

【大纲】
{outline}

【前文摘要】
{previous_summary if previous_summary else "这是开头"}

【要求】
1. 对话占60%以上
2. 每段不超过3行
3. 结尾留钩子
4. 字数1000-1200字
5. 直接写正文，不要标题

开始写:"""

    return generate(
        system_prompt="你是番茄小说写手。写爽文，节奏快，对话多。直接输出正文。",
        user_prompt=prompt,
        max_tokens=2000,
    )


def summarize_chapter(chapter_text: str) -> str:
    """总结章节要点 - 用于传递给下一章"""
    prompt = f"""用2-3句话总结这章的关键情节:

{chapter_text[:1500]}

只输出总结:"""

    return generate(
        system_prompt="简洁总结。",
        user_prompt=prompt,
        max_tokens=200,
    )


def main():
    print("=" * 50)
    print("  轻量级短篇小说生成器")
    print("  (分章生成，节省API)")
    print("=" * 50)

    # 选择类型
    print("\n选择小说类型:")
    print("  1. 赘婿逆袭 (男频)")
    print("  2. 闪婚总裁 (女频)")
    print("  3. 自定义")

    choice = input("\n选择 [1/2/3]: ").strip()

    if choice == "1":
        genre = "赘婿逆袭/打脸爽文"
    elif choice == "2":
        genre = "闪婚甜宠/霸总文"
    else:
        genre = input("输入类型: ").strip() or "都市爽文"

    # 生成随机人名
    names = random_names()
    print(f"\n随机角色: 主角={names['male']}, 女主={names['female']}, 反派={names['villain']}")

    change = input("是否更换人名? [y/N]: ").strip().lower()
    if change == 'y':
        names['male'] = input(f"主角名 [{names['male']}]: ").strip() or names['male']
        names['female'] = input(f"女主名 [{names['female']}]: ").strip() or names['female']
        names['villain'] = input(f"反派名 [{names['villain']}]: ").strip() or names['villain']

    total_chapters = 5

    # 创建输出目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent / "stories" / f"{genre[:4]}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n输出目录: {output_dir}")
    print("\n" + "=" * 50)
    print("开始生成...")
    print("=" * 50)

    # Step 1: 生成大纲
    print("\n[1/6] 生成大纲...")
    try:
        outline = generate_simple_outline(genre, names)
        print(outline)
        (output_dir / "outline.txt").write_text(outline, encoding="utf-8")
    except Exception as e:
        print(f"大纲生成失败: {e}")
        return

    input("\n按回车继续生成章节...")

    # Step 2-6: 逐章生成
    chapters = []
    previous_summary = ""

    for i in range(1, total_chapters + 1):
        print(f"\n[{i+1}/6] 生成第{i}章...")

        try:
            chapter = generate_chapter_lite(
                chapter_num=i,
                total_chapters=total_chapters,
                outline=outline,
                names=names,
                genre=genre,
                previous_summary=previous_summary,
            )

            # 保存章节
            chapter_file = output_dir / f"chapter_{i:02d}.txt"
            chapter_file.write_text(f"第{i}章\n\n{chapter}", encoding="utf-8")
            chapters.append(chapter)

            # 显示预览
            preview = chapter[:200] + "..." if len(chapter) > 200 else chapter
            print(f"\n--- 预览 ---\n{preview}\n--- 字数: {len(chapter)} ---")

            # 生成摘要给下一章
            if i < total_chapters:
                print("生成摘要...")
                previous_summary = summarize_chapter(chapter)

            # 确认继续
            if i < total_chapters:
                cont = input("\n继续下一章? [Y/n]: ").strip().lower()
                if cont == 'n':
                    print("已暂停。章节已保存。")
                    break

        except Exception as e:
            print(f"第{i}章生成失败: {e}")
            cont = input("重试? [Y/n]: ").strip().lower()
            if cont != 'n':
                i -= 1  # 重试当前章
            else:
                break

    # 合并完整小说
    if chapters:
        full_novel = ""
        for i, ch in enumerate(chapters, 1):
            full_novel += f"第{i}章\n\n{ch}\n\n{'='*30}\n\n"

        (output_dir / "full_novel.txt").write_text(full_novel, encoding="utf-8")

        total_words = sum(len(ch) for ch in chapters)
        print("\n" + "=" * 50)
        print(f"  生成完成!")
        print(f"  章节数: {len(chapters)}")
        print(f"  总字数: {total_words}")
        print(f"  保存位置: {output_dir}")
        print("=" * 50)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消")
