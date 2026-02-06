from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic
from src.state import NovelState
from src.utils.plot_manager import analyze_plot_threads, format_plot_thread_guidance
import os
import json
import time
import yaml


def load_custom_outline(state):
    """
    统一加载自定义大纲，支持两种格式：
    1. 新格式：projects/<id>/bible/outline.yaml
    2. 旧格式：config 中的 novel_outline 和 volume_frameworks

    Returns:
        dict or None: 大纲信息（outline, volumes）
    """
    # 🔧 优先尝试新格式（独立的 outline.yaml）
    project_paths = state.get('project_paths', {})
    bible_dir = project_paths.get('bible_dir')

    if bible_dir:
        outline_file = os.path.join(bible_dir, 'outline.yaml')
        if os.path.exists(outline_file):
            try:
                with open(outline_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                print(f"  📖 加载独立大纲文件: outline.yaml")
                return data
            except Exception as e:
                print(f"  ⚠️  读取 outline.yaml 失败: {e}")

    # 🔧 回退到旧格式（配置文件中的字段）
    config = state.get('config', {})
    novel_outline = config.get('novel_outline')
    volume_frameworks = config.get('volume_frameworks')

    if novel_outline or volume_frameworks:
        print(f"  📖 加载配置中的大纲字段")
        return {
            'outline': novel_outline or {},
            'volumes': volume_frameworks or []
        }

    return None


def find_current_phase(outline, chapter_index):
    """
    根据章节号查找当前所在阶段

    Returns:
        dict or None: 当前阶段信息
    """
    if not outline or 'phases' not in outline:
        return None

    for phase in outline['phases']:
        chapters_range = phase.get('chapters', '')
        if '-' in chapters_range:
            try:
                start, end = map(int, chapters_range.split('-'))
                if start <= chapter_index <= end:
                    return phase
            except:
                continue

    return None


def find_current_volume(volumes, chapter_index):
    """
    根据章节号查找当前所在卷

    Returns:
        dict or None: 当前卷信息
    """
    if not volumes:
        return None

    for volume in volumes:
        chapters_range = volume.get('chapters', '')
        if '-' in chapters_range:
            try:
                start, end = map(int, chapters_range.split('-'))
                if start <= chapter_index <= end:
                    return volume
            except:
                continue

    return None

def planner_node(state: NovelState) -> NovelState:
    """
    The Planner Node - 完整版智能场景规划
    利用角色状态、伏笔、世界事件生成连贯深度的场景
    支持从配置文件读取自定义大纲
    """
    print("--- PLANNER NODE ---")

    world_bible = state.get("world_bible", {})
    synopsis = state.get("synopsis", "")
    chapter_history = state.get("chapters", [])
    current_chapter_index = state.get("current_chapter_index", 1)
    config = state.get("config", {})

    print(f"  📋 规划第 {current_chapter_index} 章...")

    # 🔧 新增：加载自定义大纲（如果有）
    custom_outline = load_custom_outline(state)
    if custom_outline:
        print(f"  📖 使用自定义大纲")

    # 检查是否使用分层记忆（长篇模式）
    hot_memory = state.get("hot_memory")
    cold_memory = state.get("cold_memory")

    if hot_memory is not None and cold_memory is not None:
        # 长篇模式：使用分层记忆
        print(f"  🧠 使用分层记忆系统")
        from src.memory.layered_memory import get_context_for_planner
        context = get_context_for_planner(state)

        # 使用分层记忆的上下文
        characters_info = context.get('character_states', [])
        plot_threads = context.get('plot_threads', [])
        world_events = context.get('world_events', [])
        chapter_history = context.get('history_summary', [])

        # 转换为标准格式
        characters = {
            f"角色{i+1}": {"notes": [char_state]}
            for i, char_state in enumerate(characters_info[:3])
        }

        print(f"  📚 历史摘要: {len(chapter_history)} 条")
        print(f"  👥 角色状态: {len(characters_info)} 个")
        print(f"  🎭 活跃伏笔: {len(plot_threads)} 个")
    else:
        # 短篇模式：使用完整记忆
        print(f"  📖 使用完整记忆系统")
        characters = world_bible.get("characters", {})
        plot_threads = world_bible.get("plot_threads", [])
        world_events = world_bible.get("world_events", [])

    # 智能伏笔管理（完整版功能）
    plot_analysis = analyze_plot_threads(plot_threads, current_chapter_index)
    if plot_analysis['should_reveal']:
        print(f"  🎯 伏笔提醒: {len(plot_analysis['should_reveal'])} 个应揭示")

    # 构建智能 prompt
    beats = generate_intelligent_beats(
        characters=characters,
        plot_threads=plot_threads,
        world_events=world_events,
        chapter_history=chapter_history,
        synopsis=synopsis,
        chapter_index=current_chapter_index,
        plot_analysis=plot_analysis,  # 传递伏笔分析
        custom_outline=custom_outline  # 🔧 新增：传递自定义大纲
    )

    if beats:
        print(f"  ✅ 大纲生成成功 ({len(beats)} 字符)")
        return {"current_beats": beats}
    else:
        # 降级方案
        print(f"  ⚠️  使用简化大纲")
        return {"current_beats": "场景1: 角色出现\n场景2: 发生冲突\n场景3: 解决问题"}


def generate_intelligent_beats(characters, plot_threads, world_events, chapter_history, synopsis, chapter_index, plot_analysis=None, custom_outline=None):
    """生成智能场景大纲（完整版：含伏笔管理 + 自定义大纲）"""

    # 🔧 新增：解析自定义大纲
    current_phase = None
    current_volume = None
    outline_guidance = ""

    if custom_outline:
        outline_data = custom_outline.get('outline', {})
        volumes_data = custom_outline.get('volumes', [])

        # 查找当前阶段
        current_phase = find_current_phase(outline_data, chapter_index)
        if current_phase:
            outline_guidance += f"\n【当前阶段】第{chapter_index}章位于：{current_phase.get('name')}\n"
            outline_guidance += f"阶段目标: {current_phase.get('goal')}\n"

        # 查找当前卷
        current_volume = find_current_volume(volumes_data, chapter_index)
        if current_volume:
            outline_guidance += f"\n【当前卷】第{current_volume.get('volume')}卷：{current_volume.get('title')}\n"
            outline_guidance += f"卷核心目标: {current_volume.get('core_goal')}\n"
            if current_volume.get('key_events'):
                outline_guidance += f"关键事件: {', '.join(current_volume.get('key_events', []))}\n"

        # 添加总纲信息
        if outline_data:
            outline_guidance += f"\n【总纲】\n"
            outline_guidance += f"主目标: {outline_data.get('main_goal', '（未设定）')}\n"
            outline_guidance += f"主线冲突: {outline_data.get('main_conflict', '（未设定）')}\n"

    # 构建角色状态摘要
    character_states = []
    for name, char_data in list(characters.items())[:3]:  # 最多3个主要角色
        # 🔧 Bug #12修复: 兼容两种模式 (长篇: notes, 短篇: recent_notes)
        notes = char_data.get("notes", char_data.get("recent_notes", []))
        latest_note = notes[-1] if notes else "初始状态"
        character_states.append(f"{name}: {latest_note}")

    character_summary = "\n".join(character_states) if character_states else "角色状态未知"

    # 构建伏笔摘要（处理不同数据结构）
    if isinstance(plot_threads, dict):
        # 长篇模式：从 dict 中提取 active threads
        active_plot_threads = plot_threads.get("active", [])[-5:]
    elif plot_threads:
        # 短篇模式：直接使用 list
        active_plot_threads = plot_threads[-5:]
    else:
        active_plot_threads = []

    # 🔧 Bug #9修复: 处理dict格式的thread对象
    formatted_threads = []
    for thread in active_plot_threads:
        if isinstance(thread, dict):
            # 长篇模式: thread是 {"text": "...", "created_at": ..., "importance": ...}
            formatted_threads.append(thread.get("text", str(thread)))
        else:
            # 短篇模式: thread是字符串
            formatted_threads.append(str(thread))

    plot_summary = "\n".join([f"- {t}" for t in formatted_threads]) if formatted_threads else "暂无伏笔"

    # 构建世界状态摘要
    recent_events = world_events[-3:] if world_events else []  # 最近3个事件
    world_summary = "\n".join([f"- {event}" for event in recent_events]) if recent_events else "世界初始状态"

    # 构建章节历史
    recent_chapters = chapter_history[-5:] if chapter_history else []

    # 🔧 Bug #19修复: chapter_history可能是字符串列表(长篇)或dict列表(短篇)
    history_lines = []
    for ch in recent_chapters:
        if isinstance(ch, dict):
            # 短篇模式: ch是dict
            history_lines.append(f"第{ch.get('index')}章: {ch.get('summary', '')[:100]}")
        else:
            # 长篇模式: ch已经是格式化的字符串
            history_lines.append(str(ch)[:150])

    history_summary = "\n".join(history_lines) if history_lines else "这是第一章"

    # 构建完整 prompt
    prompt_parts = [
        "你是资深小说规划师，负责创建深度连贯的章节场景。",
        "",
        "【故事梗概】",
        synopsis[:500],
        "",
    ]

    # 🔧 新增：添加自定义大纲指引
    if outline_guidance:
        prompt_parts.extend([
            outline_guidance.strip(),
            ""
        ])

    prompt_parts.extend([
        "【角色当前状态】",
        character_summary,
        "",
        "【未解决的伏笔/谜团】",
        plot_summary,
        "",
        "【世界当前状态】",
        world_summary,
        "",
        "【前几章回顾】",
        history_summary,
        "",
    ])

    # 添加伏笔管理指导（完整版功能）
    if plot_analysis:
        plot_guidance = format_plot_thread_guidance(plot_analysis)
        if plot_guidance:
            prompt_parts.extend([
                "【伏笔管理】",
                plot_guidance,
                ""
            ])

    prompt_parts.extend([
        f"【任务】为第 {chapter_index} 章创建 3-5 个场景大纲",
        "",
        "⚠️ 【番茄小说风格要求】",
        "本书面向番茄小说读者，必须符合以下特点：",
        "1. **节奏快速** - 开门见山，直接进入冲突",
        "2. **爽点密集** - 每章至少2-3个爽点（打脸/反转/收获）",
        "3. **对比强烈** - 别人慌张/主角冷静，别人失败/主角成功",
        "4. **简单直白** - 不要过度心理描写，要直接动作和对话",
        "5. **主角强势** - 智商碾压，行动果断，杀伐决断",
        "",
        "【场景规划原则】",
        "1. **推进主线**: 每个场景都应推进核心故事",
        "2. **制造爽点**: 主角碾压/打脸/反杀/获得好处",
        "3. **强化对比**: 别人的失败衬托主角的强大",
        "4. **伏笔处理**:",
        "   - 如果有应揭示的伏笔，快速揭示不拖沓",
        "   - 埋新伏笔时要有冲击感",
        "5. **节奏控制**: 冲突→爽点→冲突→爽点，快节奏推进",
        "",
        "【场景要求】",
        "- 每个场景 20-40 字，聚焦一个核心事件或爽点",
        "- 避免纯铺垫场景，每个场景都要有冲突或收获",
        "- 总计 4-5 个场景，形成完整1500-2000字章节",
        "- 场景间有清晰递进关系",
        "- 符合角色当前状态和性格",
        "",
        "【输出格式】",
        "场景1: [核心事件]",
        "场景2: [核心事件]",
        "场景3: [核心事件]",
        "",
        "直接输出场景列表，不要解释。"
    ])

    prompt = '\n'.join(prompt_parts)

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            llm = ChatAnthropic(
                model="claude-sonnet-4-5-20250929",
                temperature=0.75,  # 稍高创造性，同时保持连贯
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
                anthropic_api_url=os.getenv("ANTHROPIC_BASE_URL"),
                timeout=60.0,  # 增加到60秒，给予充足时间处理复杂上下文
                max_retries=0
            )

            response = llm.invoke([HumanMessage(content=prompt)])
            beats = response.content.strip()

            # 验证场景数量
            scene_count = beats.count("场景")
            if scene_count < 2:
                print(f"     ⚠️  场景太少({scene_count})，重试")
                if attempt < max_attempts - 1:
                    time.sleep(3)
                    continue

            return beats

        except Exception as e:
            print(f"     ⚠️  生成失败: {str(e)[:40]}")
            if attempt < max_attempts - 1:
                wait = (attempt + 1) * 4
                print(f"     ⏳ 重试 ({attempt+2}/{max_attempts})，等待 {wait}s...")
                time.sleep(wait)
            else:
                return None

    return None
