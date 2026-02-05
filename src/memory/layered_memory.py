"""
分层记忆系统 - Layered Memory System

实现两级记忆架构：
- 热记忆 (Hot Memory): 当前卷的详细记忆
- 冷记忆 (Cold Memory): 历史卷的压缩摘要
"""

from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic
import os
import json
import time


def initialize_layered_memory(config):
    """
    初始化分层记忆结构

    Args:
        config: 小说配置

    Returns:
        dict: {hot_memory, cold_memory}
    """
    chapters_per_volume = config.get("generation", {}).get("chapters_per_volume", 25)

    hot_memory = {
        "current_volume": 1,
        "chapters_in_volume": 0,
        "chapters_per_volume": chapters_per_volume,
        "characters": {},  # 角色详细记忆（当前卷）
        "plot_threads": {
            "active": []  # 活跃伏笔
        },
        "world_events": [],  # 当前卷的世界事件
        "recent_chapters": []  # 当前卷的章节摘要
    }

    cold_memory = {
        "volume_summaries": []  # 历史卷的压缩摘要
    }

    return hot_memory, cold_memory


def compress_volume_memory(state, volume_index):
    """
    卷完成时压缩记忆

    流程：
    1. AI 生成卷摘要（500字）
    2. AI 压缩角色发展（每角色100字）
    3. 标记已解决伏笔
    4. 清空热记忆
    5. 保存到冷记忆

    Args:
        state: NovelState
        volume_index: 卷索引

    Returns:
        updated_state: 更新后的状态
    """
    print(f"\n--- 压缩第 {volume_index} 卷记忆 ---")

    hot_memory = state.get("hot_memory", {})
    cold_memory = state.get("cold_memory", {"volume_summaries": []})
    volume_chapters = hot_memory.get("recent_chapters", [])

    if not volume_chapters:
        print("  ⚠️  当前卷没有章节，跳过压缩")
        return state

    print(f"  📚 压缩 {len(volume_chapters)} 章内容...")

    # 1. 生成卷摘要
    volume_summary = ai_generate_volume_summary(
        volume_chapters=volume_chapters,
        volume_index=volume_index,
        max_length=500
    )

    # 2. 压缩角色发展
    character_arcs = ai_compress_character_arcs(
        characters=hot_memory.get("characters", {}),
        volume_index=volume_index,
        max_length_per_char=100
    )

    # 3. 检查并标记已解决伏笔
    resolved_threads = check_resolved_threads(
        plot_threads=hot_memory.get("plot_threads", {}).get("active", []),
        volume_chapters=volume_chapters,
        volume_index=volume_index
    )

    # 4. 保存到冷记忆
    volume_summary_entry = {
        "volume": volume_index,
        "chapters": f"{(volume_index-1)*25+1}-{volume_index*25}",
        "summary": volume_summary,
        "character_arcs": character_arcs,
        "resolved_threads": resolved_threads,
        "total_chapters": len(volume_chapters)
    }

    cold_memory["volume_summaries"].append(volume_summary_entry)

    print(f"  ✅ 卷摘要: {volume_summary[:60]}...")
    print(f"  ✅ 角色发展: {len(character_arcs)} 个角色")
    print(f"  ✅ 已解决伏笔: {len(resolved_threads)} 个")

    # 5. 清空热记忆，准备下一卷
    new_hot_memory = {
        "current_volume": volume_index + 1,
        "chapters_in_volume": 0,
        "chapters_per_volume": hot_memory.get("chapters_per_volume", 25),
        "characters": reset_character_notes(hot_memory.get("characters", {})),
        "plot_threads": {
            "active": remove_resolved_threads(
                hot_memory.get("plot_threads", {}).get("active", []),
                resolved_threads
            )
        },
        "world_events": [],
        "recent_chapters": []
    }

    print(f"  🔄 热记忆已清空，准备第 {volume_index + 1} 卷")
    print(f"  📌 剩余活跃伏笔: {len(new_hot_memory['plot_threads']['active'])} 个\n")

    return {
        "hot_memory": new_hot_memory,
        "cold_memory": cold_memory,
        "current_volume_index": volume_index + 1
    }


def ai_generate_volume_summary(volume_chapters, volume_index, max_length=500):
    """使用 AI 生成卷摘要"""

    if not volume_chapters:
        return f"第{volume_index}卷（无内容）"

    # 构建章节摘要列表
    chapter_summaries = "\n".join([
        f"第{ch.get('index', '?')}章: {ch.get('summary', '(无摘要)')[:100]}"
        for ch in volume_chapters
    ])

    prompt = f"""
你是资深小说编辑，负责将一卷（25章）的内容压缩为精炼摘要。

【本卷章节摘要】
{chapter_summaries}

【任务】
将这25章的内容压缩为 {max_length} 字以内的精炼摘要。

要求：
1. 保留核心情节发展
2. 保留关键事件和转折点
3. 保留主要角色的重要变化
4. 删除次要细节

【输出格式】
直接输出摘要文本，不要标题和解释。
"""

    try:
        llm = ChatAnthropic(
            model="claude-sonnet-4-5-20250929",
            temperature=0.3,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            anthropic_api_url=os.getenv("ANTHROPIC_BASE_URL"),
            timeout=60.0,
            max_retries=2
        )

        response = llm.invoke([HumanMessage(content=prompt)])
        summary = response.content.strip()

        # 确保长度不超过限制
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."

        return summary

    except Exception as e:
        print(f"  ⚠️  AI 摘要失败: {str(e)[:50]}")
        # 降级方案：简单拼接
        return f"第{volume_index}卷: " + " → ".join([
            ch.get("summary", "")[:50] for ch in volume_chapters[:3]
        ]) + "..."


def ai_compress_character_arcs(characters, volume_index, max_length_per_char=100):
    """使用 AI 压缩角色发展"""

    character_arcs = {}

    for char_name, char_data in characters.items():
        notes = char_data.get("recent_notes", [])

        if not notes:
            character_arcs[char_name] = "本卷无显著发展"
            continue

        # 构建 prompt
        notes_text = "\n".join([f"- {note}" for note in notes[-20:]])  # 最多20条笔记

        prompt = f"""
你是资深小说编辑，负责压缩角色在本卷的发展。

【角色】{char_name}

【本卷变化记录】
{notes_text}

【任务】
将这些变化压缩为 {max_length_per_char} 字以内的精炼总结。

要求：
1. 保留核心性格/能力变化
2. 保留重要关系变化
3. 保留关键事件影响
4. 删除细碎状态

【输出格式】
直接输出总结文本，不要标题。
"""

        try:
            llm = ChatAnthropic(
                model="claude-sonnet-4-5-20250929",
                temperature=0.3,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
                anthropic_api_url=os.getenv("ANTHROPIC_BASE_URL"),
                timeout=45.0,
                max_retries=1
            )

            response = llm.invoke([HumanMessage(content=prompt)])
            arc = response.content.strip()

            if len(arc) > max_length_per_char:
                arc = arc[:max_length_per_char-3] + "..."

            character_arcs[char_name] = arc

        except Exception as e:
            print(f"  ⚠️  {char_name} 压缩失败: {str(e)[:30]}")
            # 降级：取最后一条笔记
            character_arcs[char_name] = notes[-1][:max_length_per_char] if notes else "本卷无显著发展"

        # 避免频繁调用
        time.sleep(1)

    return character_arcs


def check_resolved_threads(plot_threads, volume_chapters, volume_index):
    """
    检查哪些伏笔在本卷已解决

    Args:
        plot_threads: 活跃伏笔列表
        volume_chapters: 本卷章节
        volume_index: 卷索引

    Returns:
        list: 已解决的伏笔
    """
    if not plot_threads or not volume_chapters:
        return []

    resolved = []

    # 构建本卷内容摘要
    volume_content = "\n".join([
        f"第{ch.get('index')}章: {ch.get('summary', '')}"
        for ch in volume_chapters
    ])

    # 检查每个伏笔
    for thread in plot_threads:
        if isinstance(thread, str):
            thread_text = thread
        else:
            thread_text = thread.get("text", str(thread))

        # 🔧 Bug #11修复: 改进伏笔检测逻辑
        # 简单检查：伏笔的关键词是否在本卷中被多次提及(不是AI方案,但比之前更准确)
        # 提取关键词(至少5个字)
        keywords = []
        if len(thread_text) >= 10:
            # 提取前10-20个字作为关键词
            keywords.append(thread_text[5:15])
        if len(thread_text) >= 20:
            keywords.append(thread_text[10:20])

        # 检查关键词出现次数
        mention_count = sum(volume_content.count(kw) for kw in keywords if kw)

        # 如果被提及2次以上,可能已揭示
        if mention_count >= 2:
            # 可能已揭示，标记
            if isinstance(thread, dict):
                thread["resolved"] = True
                thread["resolved_at"] = volume_index * 25  # 估算为卷末
                resolved.append(thread)
            else:
                resolved.append({
                    "text": thread,
                    "resolved": True,
                    "resolved_at": volume_index * 25
                })

    return resolved


def reset_character_notes(characters):
    """清空角色的详细笔记，保留核心设定"""
    reset_chars = {}

    for char_name, char_data in characters.items():
        reset_chars[char_name] = {
            "core_traits": char_data.get("core_traits", ""),
            "recent_notes": []  # 清空
        }

    return reset_chars


def remove_resolved_threads(active_threads, resolved_threads):
    """从活跃列表中移除已解决的伏笔"""

    if not resolved_threads:
        return active_threads

    resolved_texts = set()
    for thread in resolved_threads:
        if isinstance(thread, dict):
            resolved_texts.add(thread.get("text", ""))
        else:
            resolved_texts.add(thread)

    remaining = []
    for thread in active_threads:
        if isinstance(thread, dict):
            thread_text = thread.get("text", "")
        else:
            thread_text = thread

        if thread_text not in resolved_texts:
            remaining.append(thread)

    return remaining


def get_context_for_planner(state):
    """
    为 Planner 获取上下文（结合热记忆和冷记忆）

    Returns:
        dict: {
            'character_states': 角色当前状态,
            'plot_threads': 活跃伏笔,
            'world_events': 世界状态,
            'history_summary': 历史摘要
        }
    """
    hot_memory = state.get("hot_memory", {})
    cold_memory = state.get("cold_memory", {})

    # 角色状态（热记忆中的最新状态）
    character_states = []
    for char_name, char_data in hot_memory.get("characters", {}).items():
        notes = char_data.get("recent_notes", [])
        if notes:
            # 🔧 Bug #20修复: notes[-1]可能不是字符串,需要转换
            latest_note = notes[-1]
            if isinstance(latest_note, str):
                latest = latest_note[:100]
            elif isinstance(latest_note, dict):
                # 可能是包含text字段的dict
                latest = latest_note.get("text", str(latest_note))[:100]
            elif isinstance(latest_note, list):
                # 如果是list,取第一个元素或转为字符串
                latest = str(latest_note[0])[:100] if latest_note else "状态未知"
            else:
                # 其他类型,转为字符串
                latest = str(latest_note)[:100]

            character_states.append(f"{char_name}: {latest}")
        else:
            # 如果热记忆中没有，从冷记忆中获取
            if cold_memory.get("volume_summaries"):
                last_volume = cold_memory["volume_summaries"][-1]
                arc = last_volume.get("character_arcs", {}).get(char_name, "")
                if arc:
                    character_states.append(f"{char_name}: {arc}")

    # 活跃伏笔
    active_threads = hot_memory.get("plot_threads", {}).get("active", [])

    # 世界事件
    world_events = hot_memory.get("world_events", [])

    # 历史摘要（冷记忆中的卷摘要）
    history_summary = []
    for vol_summary in cold_memory.get("volume_summaries", [])[-3:]:  # 最近3卷
        summary_text = f"第{vol_summary['volume']}卷: {vol_summary['summary'][:150]}"
        history_summary.append(summary_text)

    return {
        'character_states': character_states,
        'plot_threads': active_threads,
        'world_events': world_events,
        'history_summary': history_summary
    }
