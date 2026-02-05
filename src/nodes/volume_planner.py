"""
卷规划节点 - Volume Planner Node

负责在每卷开始时生成详细卷纲
"""

from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic
from src.state import NovelState
import os
import time


def volume_planner_node(state: NovelState) -> NovelState:
    """
    卷规划节点

    功能：
    1. 读取卷框架（预先定义的卷目标）
    2. 读取上一卷的摘要（如果有）
    3. 用 AI 生成本卷的详细大纲（25章分3-5个阶段）

    触发时机：
    - 开始新卷时

    Args:
        state: NovelState

    Returns:
        更新的状态
    """
    print("--- VOLUME PLANNER NODE ---")

    current_volume = state.get("current_volume_index", 1)
    volume_frameworks = state.get("volume_frameworks", [])
    novel_outline = state.get("novel_outline", {})
    cold_memory = state.get("cold_memory", {})

    print(f"  📋 规划第 {current_volume} 卷...")

    # 检查是否有卷框架
    if not volume_frameworks:
        print("  ⚠️  没有卷框架，跳过卷规划")
        return {"current_volume_outline": ""}

    if current_volume > len(volume_frameworks):
        print(f"  ⚠️  卷索引 {current_volume} 超出范围，共 {len(volume_frameworks)} 卷")
        return {"current_volume_outline": ""}

    # 获取当前卷的框架
    framework = volume_frameworks[current_volume - 1]

    # 生成卷纲
    volume_outline = generate_volume_outline(
        framework=framework,
        novel_outline=novel_outline,
        cold_memory=cold_memory,
        volume_index=current_volume
    )

    if volume_outline:
        print(f"  ✅ 第 {current_volume} 卷大纲生成成功")
        print(f"     卷标题: {framework.get('title', '未命名')}")
        print(f"     章节范围: {framework.get('chapters', '?')}")
        print(f"     大纲长度: {len(volume_outline)} 字符\n")

        return {"current_volume_outline": volume_outline}
    else:
        print(f"  ⚠️  卷大纲生成失败，使用简化版")
        return {"current_volume_outline": f"第{current_volume}卷：{framework.get('title', '未命名')}"}


def generate_volume_outline(framework, novel_outline, cold_memory, volume_index):
    """
    生成详细卷纲

    Args:
        framework: 卷框架
        novel_outline: 总纲
        cold_memory: 冷记忆（历史卷摘要）
        volume_index: 卷索引

    Returns:
        str: 详细卷纲
    """

    # 构建上下文
    if volume_index > 1:
        # 获取上一卷摘要
        volume_summaries = cold_memory.get("volume_summaries", [])
        if volume_summaries:
            prev_summary = volume_summaries[-1]
            prev_context = f"""
【上一卷回顾】（第{prev_summary['volume']}卷）
{prev_summary['summary']}

【角色当前状态】
{format_character_arcs(prev_summary.get('character_arcs', {}))}

【已解决伏笔】
{format_resolved_threads(prev_summary.get('resolved_threads', []))}
"""
        else:
            prev_context = "【上一卷】（摘要缺失）"
    else:
        prev_context = "【这是第一卷】"

    # 构建 prompt
    prompt_parts = [
        "你是资深小说规划师，负责为一卷（25章）生成详细大纲。",
        "",
        "【总纲】",
        f"主目标: {novel_outline.get('main_goal', '(未设定)')}",
        f"主线冲突: {novel_outline.get('main_conflict', '(未设定)')}",
        f"主角成长线: {novel_outline.get('protagonist_arc', '(未设定)')}",
        "",
        prev_context,
        "",
        "【本卷框架】",
        f"卷标题: {framework.get('title', '未命名')}",
        f"章节范围: {framework.get('chapters', '?')}",
        f"核心目标: {framework.get('core_goal', '(未设定)')}",
        f"关键事件: {', '.join(framework.get('key_events', []))}",
        f"结尾状态: {framework.get('ending_state', '(未设定)')}",
        f"需埋下的伏笔: {', '.join(framework.get('foreshadowing', []))}",
        "",
        "【任务】",
        "基于上述信息，生成本卷（25章）的详细大纲。",
        "",
        "要求：",
        "1. 将 25 章分为 3-5 个阶段",
        "2. 每个阶段明确主要情节发展",
        "3. 标注伏笔的埋入和揭示时机",
        "4. 确保符合总纲的里程碑要求",
        "5. 承接上一卷，自然过渡",
        "",
        "【输出格式】",
        f"## 第{volume_index}卷：{framework.get('title', '未命名')}",
        "",
        "### 第一阶段（第X-Y章）",
        "目标: ...",
        "主要情节: ...",
        "伏笔处理: ...",
        "",
        "### 第二阶段（第X-Y章）",
        "...",
        "",
        "### 第三阶段（第X-Y章）",
        "...",
        "",
        "直接输出大纲，不要额外解释。"
    ]

    prompt = '\n'.join(prompt_parts)

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            llm = ChatAnthropic(
                model="claude-sonnet-4-5-20250929",
                temperature=0.7,  # 稍高创造性
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
                anthropic_api_url=os.getenv("ANTHROPIC_BASE_URL"),
                timeout=75.0,  # 给予充足时间
                max_retries=0
            )

            response = llm.invoke([HumanMessage(content=prompt)])
            volume_outline = response.content.strip()

            # 验证大纲长度
            if len(volume_outline) < 200:
                print(f"     ⚠️  大纲过短({len(volume_outline)}字)，重试")
                if attempt < max_attempts - 1:
                    time.sleep(3)
                    continue

            return volume_outline

        except Exception as e:
            print(f"     ⚠️  生成失败: {str(e)[:40]}")
            if attempt < max_attempts - 1:
                wait = (attempt + 1) * 5
                print(f"     ⏳ 重试 ({attempt+2}/{max_attempts})，等待 {wait}s...")
                time.sleep(wait)
            else:
                return None

    return None


def format_character_arcs(character_arcs):
    """格式化角色发展"""
    if not character_arcs:
        return "(无)"

    lines = []
    for char_name, arc in list(character_arcs.items())[:5]:  # 最多5个角色
        lines.append(f"- {char_name}: {arc[:80]}")

    return "\n".join(lines)


def format_resolved_threads(resolved_threads):
    """格式化已解决伏笔"""
    if not resolved_threads:
        return "(无)"

    lines = []
    for thread in resolved_threads[:5]:  # 最多5个
        if isinstance(thread, dict):
            text = thread.get("text", str(thread))[:60]
        else:
            text = thread[:60]
        lines.append(f"- {text}")

    return "\n".join(lines)
