#!/usr/bin/env python3
"""
轻量级短篇小说生成器 - 分10段生成，每段约1000字
每次API调用: 输入<500 tokens, 输出~1000字
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

# 10段剧情模板（赘婿逆袭类）
PLOT_BEATS = [
    "开局：主角在岳父家被羞辱，众人嘲笑他是废物赘婿",
    "蓄压：小舅子当众羞辱主角，女主心疼但无奈",
    "第一次反转：有人认出主角身份的蛛丝马迹，主角掩饰",
    "危机：富二代出现追求女主，威胁主角",
    "小爆发：主角小露一手，震惊众人，但没暴露身份",
    "升级：更大的反派出现，要对付主角和女主",
    "逼到绝境：主角被逼到不得不出手的境地",
    "身份初露：主角展现部分实力，反派开始害怕",
    "全面爆发：主角真实身份曝光，全场震惊跪拜",
    "结局：所有人态度反转，主角和女主甜蜜收尾",
]

PLOT_BEATS_FEMALE = [
    "开局：女主被迫闪婚，嫁给传说中的'废物'男主",
    "新婚：婆家人嫌弃，男主却偷偷对她好",
    "暗中保护：女主遇到麻烦，男主暗中帮忙解决",
    "心动：女主发现男主的不同寻常，心跳加速",
    "情敌出现：白莲花出现，想抢走男主",
    "误会：女主误解男主，两人冷战",
    "危机：女主被人陷害，处境危险",
    "男主护妻：男主霸气出手，打脸所有人",
    "身份曝光：男主真实身份揭露，原来是隐藏大佬",
    "甜蜜结局：所有人后悔，男女主甜蜜撒糖",
]


def random_names():
    """生成随机人名"""
    male = random.choice(MALE_NAMES)
    female = random.choice(FEMALE_NAMES)
    while female[0] == male[0]:
        female = random.choice(FEMALE_NAMES)
    return {"male": male, "female": female}


def generate_segment(
    segment_num: int,
    plot_beat: str,
    names: dict,
    previous_ending: str = "",
) -> str:
    """
    生成一个段落（约1000字）
    输入prompt非常短，输出控制在1000字
    """
    prompt = f"""写第{segment_num}/10段，1000字。

主角:{names['male']} 女主:{names['female']}
本段剧情:{plot_beat}
上段结尾:{previous_ending if previous_ending else '无，这是开头'}

要求:对话多，每段3行内，结尾留悬念。直接写正文:"""

    return generate(
        system_prompt="番茄爽文写手。只输出正文，1000字。",
        user_prompt=prompt,
        max_tokens=1800,  # 约1000-1200字
    )


def main():
    print("=" * 50)
    print("  轻量级生成器 (10段×1000字)")
    print("=" * 50)

    # 选择类型
    print("\n选择类型:")
    print("  1. 赘婿逆袭 (男频)")
    print("  2. 闪婚总裁 (女频)")

    choice = input("\n选择 [1/2]: ").strip()
    plot_beats = PLOT_BEATS_FEMALE if choice == "2" else PLOT_BEATS
    genre = "闪婚总裁" if choice == "2" else "赘婿逆袭"

    # 随机人名
    names = random_names()
    print(f"\n角色: {names['male']}(主角), {names['female']}(女主)")

    change = input("换名字? [y/N]: ").strip().lower()
    if change == 'y':
        names['male'] = input(f"主角[{names['male']}]: ").strip() or names['male']
        names['female'] = input(f"女主[{names['female']}]: ").strip() or names['female']

    # 创建输出目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent / "stories" / f"{genre}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n保存到: {output_dir}")
    print("\n剧情大纲:")
    for i, beat in enumerate(plot_beats, 1):
        print(f"  {i}. {beat}")

    input("\n按回车开始生成...")

    # 逐段生成
    segments = []
    previous_ending = ""

    for i in range(1, 11):
        print(f"\n{'='*30}")
        print(f"生成第 {i}/10 段: {plot_beats[i-1][:20]}...")
        print("=" * 30)

        try:
            segment = generate_segment(
                segment_num=i,
                plot_beat=plot_beats[i-1],
                names=names,
                previous_ending=previous_ending,
            )

            # 保存
            seg_file = output_dir / f"segment_{i:02d}.txt"
            seg_file.write_text(segment, encoding="utf-8")
            segments.append(segment)

            # 提取结尾作为下一段的上文
            previous_ending = segment[-200:] if len(segment) > 200 else segment

            # 预览
            print(f"\n{segment[:300]}...")
            print(f"\n[字数: {len(segment)}]")

            # 确认
            if i < 10:
                cont = input("\n继续? [Y/n]: ").strip().lower()
                if cont == 'n':
                    break

        except Exception as e:
            print(f"\n生成失败: {e}")
            retry = input("重试? [Y/n]: ").strip().lower()
            if retry != 'n':
                continue
            else:
                break

    # 合并
    if segments:
        full = "\n\n---\n\n".join(segments)
        (output_dir / "full_novel.txt").write_text(full, encoding="utf-8")

        total = sum(len(s) for s in segments)
        print("\n" + "=" * 50)
        print(f"完成! 共 {len(segments)} 段, {total} 字")
        print(f"文件: {output_dir / 'full_novel.txt'}")
        print("=" * 50)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消")
