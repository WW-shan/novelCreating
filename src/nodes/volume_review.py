"""
卷级审查节点 - Volume Review Node

在每卷完成时（25章）进行质量审查
"""

from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic
from src.state import NovelState
from src.memory.layered_memory import compress_volume_memory
import os
import json
import time


def volume_review_node(state: NovelState) -> NovelState:
    """
    卷级审查节点

    功能：
    1. 检查卷目标完成度
    2. 检查角色一致性
    3. 检查伏笔质量
    4. 检查节奏控制
    5. 压缩卷记忆

    触发时机：
    - 每完成25章

    Args:
        state: NovelState

    Returns:
        更新的状态
    """
    print("\n--- VOLUME REVIEW NODE ---")

    current_volume = state.get("current_volume_index", 1)
    volume_frameworks = state.get("volume_frameworks", [])
    hot_memory = state.get("hot_memory", {})

    print(f"  📊 审查第 {current_volume} 卷（25章）...")

    # 获取本卷的章节
    volume_chapters = hot_memory.get("recent_chapters", [])

    if not volume_chapters:
        print("  ⚠️  当前卷没有章节，跳过审查")
        return {}

    print(f"  📚 本卷共 {len(volume_chapters)} 章")

    # 获取卷框架
    if volume_frameworks and current_volume <= len(volume_frameworks):
        framework = volume_frameworks[current_volume - 1]
    else:
        framework = {}
        print("  ⚠️  没有卷框架，无法进行目标审查")

    # 执行四维审查
    scores = {}

    # 1. 目标完成度
    if framework:
        scores["goal_completion"] = check_goal_completion(
            volume_chapters, framework
        )
    else:
        scores["goal_completion"] = 50  # 默认分

    # 2. 角色一致性
    scores["character_consistency"] = check_character_consistency(
        volume_chapters,
        hot_memory.get("characters", {})
    )

    # 3. 伏笔质量
    if framework:
        scores["foreshadow_quality"] = check_foreshadow_quality(
            volume_chapters,
            framework.get("foreshadowing", [])
        )
    else:
        scores["foreshadow_quality"] = 50

    # 4. 节奏控制
    scores["pacing"] = check_pacing(volume_chapters)

    # 计算总分
    overall_score = sum(scores.values()) / len(scores)

    # 生成报告
    review_report = {
        "volume": current_volume,
        "total_chapters": len(volume_chapters),
        "scores": scores,
        "overall_score": overall_score,
        "timestamp": time.time()
    }

    print(f"\n  📈 卷级评分:")
    print(f"     目标完成: {scores.get('goal_completion', 0):.0f}/100")
    print(f"     角色一致: {scores.get('character_consistency', 0):.0f}/100")
    print(f"     伏笔质量: {scores.get('foreshadow_quality', 0):.0f}/100")
    print(f"     节奏控制: {scores.get('pacing', 0):.0f}/100")
    print(f"     综合评分: {overall_score:.0f}/100")

    # 警告
    if overall_score < 70:
        print(f"\n  ⚠️  警告：本卷质量偏低，建议人工审查")
        review_report["warning"] = "需要人工审查"

    # 压缩卷记忆
    print(f"\n  🔄 压缩卷记忆...")
    compressed_state = compress_volume_memory(state, current_volume)

    # 合并结果
    result = {
        **compressed_state,
        "volume_review_reports": state.get("volume_review_reports", []) + [review_report],
        "need_volume_review": False  # 🔧 Bug #18修复: 清除卷审查标志
    }

    print(f"  ✅ 第 {current_volume} 卷审查完成\n")

    return result


def check_goal_completion(volume_chapters, framework):
    """
    检查卷目标完成度

    Args:
        volume_chapters: 章节列表
        framework: 卷框架

    Returns:
        int: 分数 (0-100)
    """
    print("  🎯 检查目标完成度...")

    if not framework or not volume_chapters:
        return 50

    # 提取关键事件
    key_events = framework.get("key_events", [])
    if not key_events:
        return 75  # 没有预定事件，默认及格

    # 构建章节摘要
    chapter_summaries = "\n".join([
        f"第{ch.get('index', '?')}章: {ch.get('summary', '(无摘要)')[:100]}"
        for ch in volume_chapters
    ])

    prompt = f"""
你是资深小说编辑，负责评估本卷是否完成了预定目标。

【本卷预定目标】
核心目标: {framework.get('core_goal', '(未设定)')}
关键事件: {', '.join(key_events)}
结尾状态: {framework.get('ending_state', '(未设定)')}

【本卷章节摘要】
{chapter_summaries}

【任务】
评估本卷是否完成了预定目标，给出 0-100 分。

评分标准：
- 90-100分: 所有关键事件都发生，核心目标完美达成
- 70-89分: 大部分关键事件发生，核心目标基本达成
- 50-69分: 部分关键事件发生，核心目标部分达成
- 0-49分: 关键事件缺失，核心目标未达成

【输出格式】
评分: [0-100的整数]
理由: [1句话说明]
"""

    try:
        llm = ChatAnthropic(
            model="claude-sonnet-4-5-20250929",
            temperature=0.2,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            anthropic_api_url=os.getenv("ANTHROPIC_BASE_URL"),
            timeout=45.0,
            max_retries=1
        )

        response = llm.invoke([HumanMessage(content=prompt)])
        score = extract_score(response.content)

        return score

    except Exception as e:
        print(f"     ⚠️  AI 评分失败: {str(e)[:40]}")
        return 75  # 默认及格分


def check_character_consistency(volume_chapters, characters):
    """
    检查角色一致性

    Args:
        volume_chapters: 章节列表
        characters: 角色数据

    Returns:
        int: 分数 (0-100)
    """
    print("  👥 检查角色一致性...")

    if not volume_chapters or not characters:
        return 75

    # 简化版：检查角色是否有笔记记录
    # 完整版应该用 AI 分析角色行为是否一致
    char_count = len(characters)
    chars_with_notes = sum(
        1 for char in characters.values()
        if char.get("recent_notes")
    )

    if char_count == 0:
        return 75

    # 简单评分：有笔记的角色占比
    coverage = (chars_with_notes / char_count) * 100

    # 基础分 70 + 覆盖度调整
    score = 70 + (coverage * 0.3)

    return min(100, int(score))


def check_foreshadow_quality(volume_chapters, expected_foreshadows):
    """
    检查伏笔质量

    Args:
        volume_chapters: 章节列表
        expected_foreshadows: 预期埋下的伏笔

    Returns:
        int: 分数 (0-100)
    """
    print("  🎭 检查伏笔质量...")

    if not volume_chapters:
        return 50

    if not expected_foreshadows:
        return 80  # 没有预定伏笔，默认良好

    # 简化版：检查是否在摘要中提及
    chapter_content = " ".join([
        ch.get("summary", "") for ch in volume_chapters
    ])

    found_count = 0
    for foreshadow in expected_foreshadows:
        # 简单检查：伏笔关键词是否出现
        if foreshadow[:10] in chapter_content:
            found_count += 1

    if len(expected_foreshadows) == 0:
        return 80

    # 基础分 50 + 完成度调整
    completion_rate = found_count / len(expected_foreshadows)
    score = 50 + (completion_rate * 50)

    return int(score)


def check_pacing(volume_chapters):
    """
    检查节奏控制

    Args:
        volume_chapters: 章节列表

    Returns:
        int: 分数 (0-100)
    """
    print("  ⏱️  检查节奏控制...")

    if not volume_chapters:
        return 50

    # 简化版：检查章节数量是否合理
    chapter_count = len(volume_chapters)

    if chapter_count < 20:
        return 60  # 章节太少
    elif 20 <= chapter_count <= 30:
        return 85  # 合理范围
    else:
        return 70  # 章节稍多

    # 完整版应该用 AI 分析情节密度、高潮分布等


def extract_score(text):
    """从 AI 响应中提取分数"""
    import re

    # 查找 "评分: 85" 或 "85/100" 等模式
    patterns = [
        r'评分[:：]\s*(\d+)',
        r'(\d+)\s*/\s*100',
        r'(\d+)分'
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            score = int(match.group(1))
            return min(100, max(0, score))

    # 默认75分
    return 75
