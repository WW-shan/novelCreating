"""
里程碑审查节点 - Milestone Review Node

每50章进行一次全局审查
"""

from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic
from src.state import NovelState
import os
import time


def milestone_review_node(state: NovelState) -> NovelState:
    """
    里程碑审查节点

    功能：
    1. 检查总纲对齐度
    2. 检查主线进度
    3. 检查伏笔健康度

    触发时机：
    - 每50章
    - 到达预定里程碑

    Args:
        state: NovelState

    Returns:
        更新的状态
    """
    print("\n" + "="*60)
    print("🎯 MILESTONE REVIEW - 里程碑审查")
    print("="*60)

    current_chapter = state.get("current_chapter_index", 1)
    novel_outline = state.get("novel_outline", {})
    cold_memory = state.get("cold_memory", {})
    hot_memory = state.get("hot_memory", {})

    print(f"\n  📊 已完成 {current_chapter - 1} 章，进行全局审查...\n")

    scores = {}

    # 1. 总纲对齐度
    scores["outline_alignment"] = check_outline_alignment(
        novel_outline=novel_outline,
        cold_memory=cold_memory,
        hot_memory=hot_memory,
        current_chapter=current_chapter
    )

    # 2. 主线进度
    scores["plot_progress"] = check_plot_progress(
        novel_outline=novel_outline,
        current_chapter=current_chapter,
        cold_memory=cold_memory
    )

    # 3. 伏笔健康度
    scores["foreshadow_health"] = check_foreshadow_health(
        hot_memory=hot_memory,
        current_chapter=current_chapter
    )

    # 生成报告
    overall_score = sum(scores.values()) / len(scores)

    report = {
        "milestone_chapter": current_chapter - 1,
        "scores": scores,
        "overall_score": overall_score,
        "timestamp": time.time()
    }

    print(f"  📈 里程碑评分:")
    print(f"     总纲对齐: {scores['outline_alignment']:.0f}/100")
    print(f"     主线进度: {scores['plot_progress']:.0f}/100")
    print(f"     伏笔健康: {scores['foreshadow_health']:.0f}/100")
    print(f"     综合评分: {overall_score:.0f}/100\n")

    # 严重警告
    if scores["outline_alignment"] < 60:
        print("  🚨 严重警告：故事已严重偏离总纲！")
        print("     建议：人工审查并调整后续规划\n")
        report["critical_warning"] = "故事偏离总纲"

    if scores["foreshadow_health"] < 50:
        print("  🚨 严重警告：伏笔管理混乱！")
        print("     建议：整理伏笔列表，标记已解决的伏笔\n")
        report["critical_warning"] = "伏笔管理问题"

    print("="*60 + "\n")

    return {
        "milestone_reports": state.get("milestone_reports", []) + [report]
    }


def check_outline_alignment(novel_outline, cold_memory, hot_memory, current_chapter):
    """
    检查总纲对齐度

    Args:
        novel_outline: 总纲
        cold_memory: 冷记忆
        hot_memory: 热记忆
        current_chapter: 当前章节

    Returns:
        int: 分数 (0-100)
    """
    print("  🎯 检查总纲对齐度...")

    if not novel_outline:
        print("     ⚠️  没有总纲，无法检查")
        return 75

    # 构建当前故事摘要
    story_summary = build_story_summary(cold_memory, hot_memory)

    prompt = f"""
你是资深小说编辑，负责检查故事是否偏离总纲。

【总纲】
主目标: {novel_outline.get('main_goal', '(未设定)')}
主线冲突: {novel_outline.get('main_conflict', '(未设定)')}
主角成长线: {novel_outline.get('protagonist_arc', '(未设定)')}

【当前进度】
已完成章节: {current_chapter - 1}

【已完成的故事】
{story_summary[:1500]}

【任务】
评估当前故事是否符合总纲方向。

评分标准：
- 90-100分: 完全符合总纲，发展自然
- 70-89分: 基本符合，有小偏离但可接受
- 50-69分: 有明显偏离，但可以调整回来
- 0-49分: 严重偏离，需要重新规划

【输出格式】
评分: [0-100的整数]
偏离点: [如果有，简要说明]
"""

    try:
        llm = ChatAnthropic(
            model="claude-sonnet-4-5-20250929",
            temperature=0.2,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            anthropic_api_url=os.getenv("ANTHROPIC_BASE_URL"),
            timeout=50.0,
            max_retries=1
        )

        response = llm.invoke([HumanMessage(content=prompt)])
        score = extract_score(response.content)

        return score

    except Exception as e:
        print(f"     ⚠️  AI 评分失败: {str(e)[:40]}")
        return 75


def check_plot_progress(novel_outline, current_chapter, cold_memory):
    """
    检查主线进度

    Args:
        novel_outline: 总纲
        current_chapter: 当前章节
        cold_memory: 冷记忆

    Returns:
        int: 分数 (0-100)
    """
    print("  📈 检查主线进度...")

    milestones = novel_outline.get("key_milestones", [])
    if not milestones:
        return 80  # 没有里程碑，默认良好

    # 检查应该到达的里程碑
    expected_milestone = None
    for milestone in milestones:
        if milestone["chapter"] <= current_chapter - 1:
            expected_milestone = milestone

    if not expected_milestone:
        return 85  # 还没到第一个里程碑

    # 检查是否达成
    story_summary = "\n".join([
        vol["summary"] for vol in cold_memory.get("volume_summaries", [])
    ])

    event = expected_milestone["event"]

    # 简化检查：事件关键词是否出现
    if event[:15] in story_summary:
        return 90  # 达成
    else:
        print(f"     ⚠️  应达成里程碑「{event}」，但未检测到")
        return 65  # 未达成


def check_foreshadow_health(hot_memory, current_chapter):
    """
    检查伏笔健康度

    Args:
        hot_memory: 热记忆
        current_chapter: 当前章节

    Returns:
        int: 分数 (0-100)
    """
    print("  🎭 检查伏笔健康度...")

    active_threads = hot_memory.get("plot_threads", {}).get("active", [])

    if not active_threads:
        return 70  # 没有活跃伏笔，默认及格

    # 检查伏笔数量
    thread_count = len(active_threads)

    if thread_count > 30:
        print(f"     ⚠️  伏笔过多({thread_count}个)，可能管理困难")
        return 55

    # 检查老旧伏笔
    old_threads = 0
    for thread in active_threads:
        if isinstance(thread, dict):
            created_at = thread.get("created_at", current_chapter)
            age = current_chapter - created_at
            if age > 30:  # 超过30章
                old_threads += 1

    if old_threads > 5:
        print(f"     ⚠️  有 {old_threads} 个伏笔超过30章未解决")
        return 60

    # 健康状态
    if thread_count < 20 and old_threads < 3:
        return 85  # 健康
    else:
        return 70  # 一般


def build_story_summary(cold_memory, hot_memory):
    """构建当前故事摘要"""
    lines = []

    # 历史卷摘要
    for vol in cold_memory.get("volume_summaries", []):
        lines.append(f"第{vol['volume']}卷: {vol['summary']}")

    # 当前卷章节
    current_chapters = hot_memory.get("recent_chapters", [])
    if current_chapters:
        current_summary = " → ".join([
            ch.get("summary", "")[:50]
            for ch in current_chapters[-5:]
        ])
        lines.append(f"当前卷（最近5章）: {current_summary}")

    return "\n\n".join(lines)


def extract_score(text):
    """从 AI 响应中提取分数"""
    import re

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

    return 75
