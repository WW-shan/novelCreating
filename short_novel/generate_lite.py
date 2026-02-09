#!/usr/bin/env python3
"""
高质量短篇小说生成器 - 分段生成防超时
每段输出约1000字，输入包含完整上下文保证质量
"""
import sys
import random
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from core.ai_client import generate

# 人名库
MALE_NAMES = ["陈默", "林风", "张远", "王浩", "李明", "赵阳", "周毅", "吴凡", "郑宇", "孙强"]
FEMALE_NAMES = ["苏晴", "林婉", "陈雨", "王璇", "李婷", "赵雪", "周琳", "吴梦", "郑薇", "孙萌"]
VILLAIN_NAMES = ["钱少", "周公子", "赵董", "孙总", "马老板"]


def random_names():
    male = random.choice(MALE_NAMES)
    female = random.choice(FEMALE_NAMES)
    while female[0] == male[0]:
        female = random.choice(FEMALE_NAMES)
    villain = random.choice(VILLAIN_NAMES)
    return {"male": male, "female": female, "villain": villain}


# 完整的模板信息（保证质量）
TEMPLATE_MALE = """
【套路模板：赘婿逆袭】

核心爽点：主角是隐藏的绝世强者/超级富豪，入赘后被所有人看不起，最后身份曝光打脸所有人。

角色设定：
- 主角{male}：表面是被嘲笑的废物赘婿，实际是隐藏身份的顶级大佬（商业帝王/军方大佬/神医等）
- 女主{female}：主角的妻子，善良但被家人轻视，一直相信主角
- 反派{villain}：有钱有势，看不起主角，追求女主

写作要求：
1. 对话占比60%以上，对话要犀利有冲突
2. 每段最多3行，适合手机阅读
3. 节奏快，不要大段描写
4. 打脸要爽，反派态度反转要明显
5. 每段结尾留悬念钩子
"""

TEMPLATE_FEMALE = """
【套路模板：闪婚总裁】

核心爽点：女主被迫嫁给"废物"，结果老公是隐藏的霸道总裁，宠她入骨，打脸所有看不起她的人。

角色设定：
- 男主{male}：表面是被传为废物的男人，实际是顶级豪门继承人/商业帝国掌门人
- 女主{female}：被家人利用的善良女孩，有骨气不软弱
- 反派：嫌弃女主的婆家人、想抢男主的白莲花、利用女主的渣亲戚

写作要求：
1. 甜宠为主，虐心要少
2. 男主对女主要反差萌（对外冷酷对她温柔）
3. 对话多，甜的细节要具体
4. 打脸要爽，让欺负女主的人后悔
5. 每段结尾留悬念或撒糖
"""

# 10段剧情节拍
BEATS_MALE = [
    {"name": "开局受辱", "goal": "展示主角的憋屈处境，被岳父家人当众羞辱，女主心疼但无奈。埋下主角身份的微小暗示。"},
    {"name": "羞辱加剧", "goal": "小舅子或亲戚变本加厉羞辱主角，甚至动手。主角隐忍，但读者能感觉到他在压制怒火。"},
    {"name": "反派登场", "goal": "有钱有势的反派出现，当众追求女主，羞辱主角是废物，扬言要抢走女主。"},
    {"name": "被逼出手", "goal": "反派触及主角底线（侮辱女主/动手），主角终于出手，一招制敌，但没暴露身份。"},
    {"name": "众人震惊", "goal": "所有人震惊主角的实力，开始怀疑他的身份。反派不服，叫来更大的靠山。"},
    {"name": "危机升级", "goal": "更强的对手出现，威胁主角和女主。局势看似危险，实则是主角身份曝光的铺垫。"},
    {"name": "身份初露", "goal": "有人认出主角的某个身份标志（戒指/电话/旧识），开始震惊。反派还在嚣张不知死活。"},
    {"name": "全面碾压", "goal": "主角真实身份曝光的一部分，反派的靠山反而对主角恭敬，反派开始害怕。"},
    {"name": "终极反转", "goal": "主角完整身份曝光，原来他是XXX！所有人跪拜，之前羞辱他的人瑟瑟发抖。"},
    {"name": "收尾打脸", "goal": "清算所有欺负过主角的人，女主终于知道真相感动落泪，甜蜜结局。"},
]

BEATS_FEMALE = [
    {"name": "闪婚开局", "goal": "女主被迫闪婚嫁给'废物'男主，婆家人嫌弃，但男主新婚夜展现了一丝不同寻常。"},
    {"name": "甜蜜初现", "goal": "男主暗中照顾女主，小细节让女主心动。但她还不知道男主的真实身份。"},
    {"name": "情敌出现", "goal": "白莲花/前女友出现，当众羞辱女主，想抢走男主。女主委屈但坚强。"},
    {"name": "男主护妻", "goal": "男主霸气出手护妻，打脸情敌，但没暴露身份。女主对男主刮目相看。"},
    {"name": "感情升温", "goal": "两人感情升温，甜蜜互动。男主的反差萌让女主心跳加速。"},
    {"name": "误会产生", "goal": "女主发现男主的秘密，产生误会，两人冷战。虐心但读者知道很快会和好。"},
    {"name": "危机降临", "goal": "女主被人陷害/绑架，处境危险。男主得知后怒了。"},
    {"name": "霸气救援", "goal": "男主以真实身份出现救女主，气场全开。所有人震惊他的身份。"},
    {"name": "身份曝光", "goal": "男主身份完全曝光，原来他是XXX！所有欺负过女主的人后悔跪拜。"},
    {"name": "甜蜜结局", "goal": "误会解开，男主深情告白，解释为什么选择她。撒糖结局，意犹未尽。"},
]


def generate_segment(
    segment_num: int,
    beat: dict,
    names: dict,
    template: str,
    previous_text: str,
    all_previous_summary: str,
) -> str:
    """生成一个高质量段落"""

    prompt = f"""{template.format(**names)}

===== 当前任务 =====
写第 {segment_num}/10 段，约1000-1200字。

本段节拍：{beat['name']}
本段目标：{beat['goal']}

===== 前文概要 =====
{all_previous_summary if all_previous_summary else "这是故事开头，没有前文。"}

===== 上一段结尾（保持衔接）=====
{previous_text if previous_text else "无，这是开头。"}

===== 输出要求 =====
1. 直接写正文，不要标题
2. 约1000-1200字
3. 对话占比60%+
4. 结尾要有钩子，让人想看下一段
5. 保持与前文的角色名、情节一致

现在开始写第{segment_num}段的正文："""

    return generate(
        system_prompt="你是番茄小说的顶级签约作者，擅长写节奏紧凑、爽点密集的短篇爽文。直接输出小说正文，不要任何解释。",
        user_prompt=prompt,
        max_tokens=2000,
    )


def summarize_previous(all_text: str) -> str:
    """总结前文要点"""
    if len(all_text) < 500:
        return all_text

    prompt = f"""请用150字以内总结以下小说片段的关键情节、人物状态、重要事件：

{all_text[-3000:]}

只输出总结，不要其他内容："""

    return generate(
        system_prompt="简洁总结小说情节。",
        user_prompt=prompt,
        max_tokens=300,
    )


def main():
    print("=" * 50)
    print("  高质量短篇小说生成器")
    print("  (分10段生成，每段~1000字)")
    print("=" * 50)

    # 选择类型
    print("\n选择类型:")
    print("  1. 赘婿逆袭 (男频爽文)")
    print("  2. 闪婚总裁 (女频甜宠)")

    choice = input("\n选择 [1/2]: ").strip()

    if choice == "2":
        template = TEMPLATE_FEMALE
        beats = BEATS_FEMALE
        genre = "闪婚总裁"
    else:
        template = TEMPLATE_MALE
        beats = BEATS_MALE
        genre = "赘婿逆袭"

    # 随机人名
    names = random_names()
    print(f"\n角色: 主角={names['male']}, 女主={names['female']}, 反派={names['villain']}")

    change = input("更换名字? [y/N]: ").strip().lower()
    if change == 'y':
        names['male'] = input(f"主角名[{names['male']}]: ").strip() or names['male']
        names['female'] = input(f"女主名[{names['female']}]: ").strip() or names['female']
        names['villain'] = input(f"反派名[{names['villain']}]: ").strip() or names['villain']

    # 创建输出目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent / "stories" / f"{genre}_{names['male']}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n保存目录: {output_dir}")

    # 显示剧情大纲
    print("\n" + "=" * 50)
    print("剧情节拍预览:")
    print("=" * 50)
    for i, beat in enumerate(beats, 1):
        print(f"{i:2}. [{beat['name']}] {beat['goal'][:40]}...")

    input("\n按回车开始生成...")

    # 逐段生成
    segments = []
    previous_text = ""
    all_previous_summary = ""

    for i in range(1, 11):
        beat = beats[i-1]

        print(f"\n{'='*50}")
        print(f"第 {i}/10 段: 【{beat['name']}】")
        print(f"目标: {beat['goal']}")
        print("=" * 50)
        print("\n生成中...")

        try:
            segment = generate_segment(
                segment_num=i,
                beat=beat,
                names=names,
                template=template,
                previous_text=previous_text,
                all_previous_summary=all_previous_summary,
            )

            # 保存
            seg_file = output_dir / f"part_{i:02d}_{beat['name']}.txt"
            seg_file.write_text(segment, encoding="utf-8")
            segments.append(segment)

            # 显示
            print(f"\n{'-'*40}")
            print(segment[:500] + "..." if len(segment) > 500 else segment)
            print(f"{'-'*40}")
            print(f"字数: {len(segment)}")

            # 更新上下文
            previous_text = segment[-300:] if len(segment) > 300 else segment

            # 每3段总结一次前文
            if i % 3 == 0 and i < 10:
                print("\n更新前文摘要...")
                full_so_far = "\n\n".join(segments)
                all_previous_summary = summarize_previous(full_so_far)

            # 确认继续
            if i < 10:
                action = input("\n[回车]继续 / [r]重写本段 / [q]保存退出: ").strip().lower()
                if action == 'q':
                    break
                elif action == 'r':
                    segments.pop()
                    print("重新生成本段...")
                    continue

        except Exception as e:
            print(f"\n生成失败: {e}")
            retry = input("[回车]重试 / [s]跳过 / [q]退出: ").strip().lower()
            if retry == 'q':
                break
            elif retry == 's':
                segments.append(f"[第{i}段生成失败，待补充]")
                previous_text = ""
            # 否则重试当前段

    # 合并输出
    if segments:
        # 分段版本
        full_text = ""
        for i, seg in enumerate(segments, 1):
            full_text += f"\n{'='*20} 第{i}段 {'='*20}\n\n{seg}\n"

        (output_dir / "full_novel.txt").write_text(full_text, encoding="utf-8")

        # 纯净版本（无分隔符）
        clean_text = "\n\n".join(segments)
        (output_dir / "clean_novel.txt").write_text(clean_text, encoding="utf-8")

        total_words = sum(len(s) for s in segments)

        print("\n" + "=" * 50)
        print("  生成完成!")
        print("=" * 50)
        print(f"  段数: {len(segments)}/10")
        print(f"  总字数: {total_words}")
        print(f"  分段版: {output_dir / 'full_novel.txt'}")
        print(f"  纯净版: {output_dir / 'clean_novel.txt'}")
        print("=" * 50)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消")
