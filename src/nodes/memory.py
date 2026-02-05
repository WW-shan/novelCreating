from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic
from src.state import NovelState
import os
import json
import time
import copy  # For deep copying world_bible

def memory_update_node(state: NovelState) -> NovelState:
    """
    The Memory Update Node - 完整版 AI 驱动的世界状态更新
    追踪角色发展、伏笔、世界状态变化
    """
    print("--- MEMORY UPDATE NODE ---")

    draft = state.get("draft", "")
    world_bible = state.get("world_bible", {})
    chapter_index = state.get("current_chapter_index", 1)
    chapters_history = state.get("chapters", [])

    print(f"  📚 分析第 {chapter_index} 章内容...")

    # 使用 AI 进行智能状态更新
    updated_state = update_world_state_with_ai(
        draft=draft,
        world_bible=world_bible,
        chapter_index=chapter_index,
        history=chapters_history,
        state=state  # Pass full state for mode detection
    )

    if updated_state:
        new_bible = updated_state.get("world_bible", world_bible)
        chapter_summary = updated_state.get("chapter_summary", {})

        print(f"  ✅ 第 {chapter_index} 章已记录")
        print(f"     摘要: {chapter_summary.get('summary', '')[:60]}...")

        # 显示重要更新
        if updated_state.get("important_changes"):
            print(f"  📝 重要变化:")
            for change in updated_state.get("important_changes", [])[:3]:
                print(f"     - {change}")

        # 更新章节历史
        updated_chapters = chapters_history + [chapter_summary]

        # 如果启用分层记忆，同时更新 hot_memory
        hot_memory = state.get("hot_memory")
        if hot_memory:
            hot_memory["recent_chapters"].append(chapter_summary)
            hot_memory["chapters_in_volume"] += 1

            # 🔧 Bug #8修复: 同步world_bible的角色数据到hot_memory
            # 确保hot_memory["characters"]与world_bible["characters"]同步
            if "characters" in new_bible:
                for char_name, char_data in new_bible["characters"].items():
                    if char_name not in hot_memory["characters"]:
                        hot_memory["characters"][char_name] = {}
                    # 同步recent_notes
                    if "recent_notes" in char_data:
                        hot_memory["characters"][char_name]["recent_notes"] = char_data["recent_notes"]

            # 同步plot_threads到hot_memory
            if "plot_threads" in new_bible and isinstance(new_bible["plot_threads"], dict):
                hot_memory["plot_threads"] = new_bible["plot_threads"]

            # 同步world_events到hot_memory
            if "world_events" in new_bible:
                hot_memory["world_events"] = new_bible["world_events"]

            # 检查是否需要压缩卷记忆（每25章）
            # 🔧 Bug #15修复: 添加>0检查,防止chapters_in_volume=0时误触发
            if hot_memory["chapters_in_volume"] > 0 and hot_memory["chapters_in_volume"] % 25 == 0:
                from src.memory.layered_memory import compress_volume_memory

                current_volume = hot_memory.get("current_volume", 1)
                print(f"\n🗜️  触发第 {current_volume} 卷记忆压缩...")

                compressed = compress_volume_memory(state, current_volume)

                # 🔧 Bug #18修复: 设置标志表示需要卷审查
                return {
                    **compressed,  # hot_memory, cold_memory, current_volume_index
                    "world_bible": new_bible,
                    "chapters": updated_chapters,
                    "current_chapter_index": chapter_index + 1,
                    "current_beats": "",
                    "draft": "",
                    "iteration": 0,
                    "need_volume_review": True  # 标记需要卷审查
                }

        return {
            "world_bible": new_bible,
            "hot_memory": hot_memory,  # 🔧 Bug #8修复: 返回更新后的hot_memory
            "chapters": updated_chapters,
            "current_chapter_index": chapter_index + 1,
            "current_beats": "",
            "draft": "",
            "iteration": 0
        }
    else:
        # AI 更新失败，使用降级方案
        print(f"  ⚠️  AI 更新失败，使用基础记录")
        return fallback_update(state, draft, world_bible, chapter_index, chapters_history)


def update_world_state_with_ai(draft, world_bible, chapter_index, history, state=None):
    """使用 AI 智能更新世界状态"""

    # 构建上下文
    recent_history = "\n".join([
        f"第{ch.get('index')}章: {ch.get('summary', '')[:100]}"
        for ch in history[-3:]  # 最近3章
    ])

    # 构建分析 prompt
    prompt_parts = [
        "你是专业小说编辑，负责追踪世界状态和角色发展。",
        "",
        "【当前世界设定】",
        json.dumps(world_bible, ensure_ascii=False, indent=2)[:1000],
        "",
        "【前几章回顾】",
        recent_history if recent_history else "(这是第一章)",
        "",
        f"【第 {chapter_index} 章内容】",
        draft[:3000],  # 发送前3000字符（足够覆盖2500字的章节）
        "",
        "【任务】",
        "分析本章内容，更新以下信息：",
        "",
        "1. **角色发展**: 主要角色的状态、情感、关系变化",
        "2. **伏笔/谜团**: 新出现的伏笔，已揭示的谜团",
        "3. **世界状态**: 环境、设定的重要变化",
        "4. **章节摘要**: 本章核心情节(50-100字)",
        "",
        "【输出格式 - 严格 JSON】",
        "⚠️ 重要：必须是合法的 JSON 格式！",
        "",
        "关键规则：",
        "1. 每个对象内的字段后面必须有逗号（除了最后一个字段）",
        "2. 对象结尾 } 后面如果还有其他字段，也必须有逗号",
        "3. 不要有尾部逗号（最后一个字段后不能有逗号）",
        "",
        "示例:",
        "```json",
        "{",
        '  "chapter_summary": {',
        f'    "index": {chapter_index},',
        '    "summary": "本章核心情节摘要"',
        '  },  ← 注意这里的逗号！',
        '  "character_updates": {',
        '    "角色名": "状态/情感/关系变化"',
        '  },  ← 注意这里的逗号！',
        '  "plot_developments": [',
        '    "新伏笔或谜团揭示"',
        '  ],  ← 注意这里的逗号！',
        '  "world_changes": [',
        '    "环境或设定的重要变化"',
        '  ],  ← 注意这里的逗号！',
        '  "important_changes": [',
        '    "最重要的3个变化"',
        '  ]  ← 最后一个字段没有逗号',
        "}",
        "```",
        "",
        "只输出 JSON，不要其他内容。"
    ]

    prompt = '\n'.join(prompt_parts)

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            llm = ChatAnthropic(
                model="claude-sonnet-4-5-20250929",
                temperature=0.3,  # 较低温度，确保准确性
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
                anthropic_api_url=os.getenv("ANTHROPIC_BASE_URL"),
                timeout=60.0,  # 60秒超时
                max_retries=0,
                max_tokens=2048  # 增加 max_tokens 防止截断
            )

            response = llm.invoke([HumanMessage(content=prompt)])
            content = response.content.strip()

            # 提取 JSON
            json_content = extract_json_from_response(content)
            if json_content:
                # 尝试清理和修复常见的 JSON 错误
                import re

                # 1. 移除注释
                json_content_clean = re.sub(r'//.*', '', json_content)

                # 2. 检查并修复未闭合的 JSON
                # 计算引号数量，如果是奇数，说明有未闭合的字符串
                quote_count = json_content_clean.count('"')
                if quote_count % 2 != 0:
                    print(f"     ⚠️  检测到未闭合的字符串（引号数: {quote_count}）")
                    # 尝试闭合最后一个字符串
                    json_content_clean = json_content_clean.rstrip() + '"'

                # 3. 修复缺失的逗号（在 } 或 ] 后面跟 "）
                json_content_clean = re.sub(r'([}\]])(\s*\n\s*)(")', r'\1,\2\3', json_content_clean)

                # 4. 修复缺失的逗号（在 " 后面跟 "）
                json_content_clean = re.sub(r'(")\s*\n(\s*")', r'\1,\n\2', json_content_clean)

                # 5. 修复缺失的逗号（数组/对象之间）
                json_content_clean = re.sub(r'([}\]])(\s*\n\s*)([{\[])', r'\1,\2\3', json_content_clean)

                # 6. 移除尾部逗号
                json_content_clean = re.sub(r',(\s*[}\]])', r'\1', json_content_clean)

                # 7. 确保 JSON 正确闭合
                # 统计大括号和方括号
                open_braces = json_content_clean.count('{') - json_content_clean.count('}')
                open_brackets = json_content_clean.count('[') - json_content_clean.count(']')

                if open_braces > 0 or open_brackets > 0:
                    print(f"     ⚠️  检测到未闭合的括号（{{: {open_braces}, [: {open_brackets}）")
                    # 尝试添加缺失的闭合括号
                    json_content_clean = json_content_clean.rstrip()
                    json_content_clean += '\n' + ('  ]' * open_brackets) + '\n' + ('}' * open_braces)

                try:
                    parsed = json.loads(json_content_clean)
                except json.JSONDecodeError as json_err:
                    # 如果还是失败，打印详细信息方便调试
                    print(f"     ⚠️  JSON 格式错误: {str(json_err)[:80]}")
                    print(f"     修复后的JSON前200字符: {json_content_clean[:200]}")
                    if attempt < max_attempts - 1:
                        time.sleep(3)
                        continue
                    else:
                        raise

                # 更新 world_bible
                updated_bible = update_bible_with_parsed_data(
                    world_bible,
                    parsed,
                    chapter_index,  # 传递 chapter_index
                    state  # 传递 state for mode detection
                )

                return {
                    "world_bible": updated_bible,
                    "chapter_summary": parsed.get("chapter_summary", {}),
                    "important_changes": parsed.get("important_changes", [])
                }
            else:
                print(f"     ⚠️  JSON 解析失败，重试 ({attempt + 1}/{max_attempts})")
                if attempt < max_attempts - 1:
                    time.sleep(3)
                    continue

        except json.JSONDecodeError as e:
            print(f"     ⚠️  JSON 格式错误: {str(e)[:50]}")
            if attempt < max_attempts - 1:
                time.sleep(3)
                continue
        except Exception as e:
            print(f"     ⚠️  AI 调用失败: {str(e)[:50]}")
            if attempt < max_attempts - 1:
                time.sleep((attempt + 1) * 4)
                continue

    return None


def extract_json_from_response(content):
    """从响应中提取 JSON"""
    # 尝试查找 JSON 代码块
    if "```json" in content:
        start = content.find("```json") + 7
        end = content.find("```", start)
        if end > start:
            return content[start:end].strip()

    # 尝试查找纯 JSON (以 { 开始)
    if "{" in content:
        start = content.find("{")
        end = content.rfind("}") + 1
        if end > start:
            return content[start:end].strip()

    return None


def update_bible_with_parsed_data(world_bible, parsed_data, chapter_index, state=None):
    """根据解析的数据更新 world_bible"""
    # Use deep copy to prevent state corruption
    updated_bible = copy.deepcopy(world_bible)

    # 更新角色状态
    character_updates = parsed_data.get("character_updates", {})
    if character_updates and "characters" in updated_bible:
        for char_name, update in character_updates.items():
            if char_name in updated_bible["characters"]:
                # 添加状态更新到角色的备注中（使用 recent_notes 兼容分层记忆）
                if "recent_notes" not in updated_bible["characters"][char_name]:
                    updated_bible["characters"][char_name]["recent_notes"] = []
                updated_bible["characters"][char_name]["recent_notes"].append(update)

                # 🔧 Bug #7修复: 限制recent_notes容量,防止长篇小说内存爆炸
                MAX_RECENT_NOTES = 10  # 只保留最近10条
                if len(updated_bible["characters"][char_name]["recent_notes"]) > MAX_RECENT_NOTES:
                    updated_bible["characters"][char_name]["recent_notes"] = \
                        updated_bible["characters"][char_name]["recent_notes"][-MAX_RECENT_NOTES:]

    # 更新伏笔追踪（适配双模式）
    plot_developments = parsed_data.get("plot_developments", [])
    if plot_developments:
        # Check if using layered memory (long mode) or simple memory (short mode)
        hot_memory = state.get("hot_memory")

        if hot_memory is not None:
            # Long mode: plot_threads is dict with "active" key
            if "plot_threads" not in updated_bible:
                updated_bible["plot_threads"] = {"active": []}
            elif isinstance(updated_bible["plot_threads"], list):
                # Migration: convert old list format to new dict format
                updated_bible["plot_threads"] = {"active": updated_bible["plot_threads"]}

            # Add to active threads
            for dev in plot_developments:
                if isinstance(dev, str):
                    thread_dict = {
                        "text": dev,
                        "created_at": chapter_index,
                        "resolved": False,
                        "importance": 5
                    }
                    updated_bible["plot_threads"]["active"].append(thread_dict)
                else:
                    if "created_at" not in dev:
                        dev["created_at"] = chapter_index
                    if "resolved" not in dev:
                        dev["resolved"] = False
                    updated_bible["plot_threads"]["active"].append(dev)

            # 🔧 Bug #7修复: 限制active plot_threads容量,防止长篇小说内存爆炸
            MAX_ACTIVE_THREADS = 30  # 最多保留30个活跃伏笔
            if len(updated_bible["plot_threads"]["active"]) > MAX_ACTIVE_THREADS:
                # 优先保留重要度高的和最近的
                sorted_threads = sorted(
                    updated_bible["plot_threads"]["active"],
                    key=lambda x: (x.get("importance", 5), x.get("created_at", 0)),
                    reverse=True
                )
                updated_bible["plot_threads"]["active"] = sorted_threads[:MAX_ACTIVE_THREADS]

        else:
            # Short mode: plot_threads is a list
            if "plot_threads" not in updated_bible:
                updated_bible["plot_threads"] = []
            elif isinstance(updated_bible["plot_threads"], dict):
                # Migration: extract active threads from dict
                updated_bible["plot_threads"] = updated_bible["plot_threads"].get("active", [])

            # Add to list
            for dev in plot_developments:
                # 🔧 Bug #10修复: 短篇模式应该保持字符串格式,不要创建dict
                if isinstance(dev, str):
                    updated_bible["plot_threads"].append(dev)
                elif isinstance(dev, dict) and "text" in dev:
                    # 如果传入的是dict,提取text字段
                    updated_bible["plot_threads"].append(dev["text"])
                else:
                    # fallback: 转为字符串
                    updated_bible["plot_threads"].append(str(dev))

            # 🔧 Bug #7修复: 限制plot_threads容量(短篇模式也需要,防止超过50章)
            MAX_PLOT_THREADS = 20  # 短篇模式最多20个伏笔
            if len(updated_bible["plot_threads"]) > MAX_PLOT_THREADS:
                updated_bible["plot_threads"] = updated_bible["plot_threads"][-MAX_PLOT_THREADS:]

    # 更新世界状态
    world_changes = parsed_data.get("world_changes", [])
    if world_changes:
        if "world_events" not in updated_bible:
            updated_bible["world_events"] = []
        updated_bible["world_events"].extend(world_changes)

        # 🔧 Bug #7修复: 限制world_events容量,防止长篇小说内存爆炸
        MAX_WORLD_EVENTS = 15  # 最多保留15个世界事件
        if len(updated_bible["world_events"]) > MAX_WORLD_EVENTS:
            updated_bible["world_events"] = updated_bible["world_events"][-MAX_WORLD_EVENTS:]

    return updated_bible


def fallback_update(state, draft, world_bible, chapter_index, chapters_history):
    """降级方案：基础状态更新"""
    print(f"  📌 使用基础记录模式")

    # 简单提取摘要
    summary = extract_simple_summary(draft, chapter_index)

    chapter_summary = {
        "index": chapter_index,
        "summary": summary
    }

    updated_chapters = chapters_history + [chapter_summary]

    print(f"  ✅ 第 {chapter_index} 章已记录")
    print(f"     摘要: {summary[:60]}...")

    # 🔧 Bug #17修复: fallback也需要更新hot_memory
    hot_memory = state.get("hot_memory")
    result = {
        "world_bible": copy.deepcopy(world_bible),  # 🔧 Bug #16修复: 使用深拷贝
        "chapters": updated_chapters,
        "current_chapter_index": chapter_index + 1,
        "current_beats": "",
        "draft": "",
        "iteration": 0
    }

    if hot_memory:
        hot_memory["recent_chapters"].append(chapter_summary)
        hot_memory["chapters_in_volume"] += 1
        result["hot_memory"] = hot_memory

        # 检查卷压缩
        if hot_memory["chapters_in_volume"] > 0 and hot_memory["chapters_in_volume"] % 25 == 0:
            from src.memory.layered_memory import compress_volume_memory
            current_volume = hot_memory.get("current_volume", 1)
            print(f"\n🗜️  触发第 {current_volume} 卷记忆压缩...")
            compressed = compress_volume_memory(state, current_volume)
            result.update(compressed)

    return result


def extract_simple_summary(draft, chapter_index):
    """简单提取摘要"""
    lines = [
        line.strip()
        for line in draft.split('\n')
        if line.strip() and not line.startswith('#')
    ]

    if lines:
        first_paragraph = lines[0][:100]
        return f"第{chapter_index}章: {first_paragraph}..."
    else:
        return f"第{chapter_index}章"
