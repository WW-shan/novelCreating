from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from src.state import NovelState
from src.nodes.planner import planner_node
from src.nodes.writer import writer_node
from src.nodes.critic import critic_node
from src.nodes.memory import memory_update_node
from src.project_manager import ProjectManager
import sqlite3
import json
import yaml
import sys
import os
import random
from dotenv import load_dotenv

# 加载环境变量（指定.env文件路径）
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

def load_config():
    """加载配置文件（优先从当前项目加载）"""
    # 🔧 优先从当前项目加载
    pm = ProjectManager()
    current_project = pm.get_current_project()

    if current_project:
        # 从项目目录加载
        config_path = current_project['config_file']
        print(f"   从项目加载: {current_project['title']}")
    else:
        # 回退到旧路径（兼容性）
        config_path = '/project/novel/bible/novel_config_latest.yaml'
        print(f"   从默认位置加载配置")

    if not os.path.exists(config_path):
        print("⚠️  未找到配置文件！")
        print("请先运行: ./novel.sh new")
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    return config

def config_to_initial_state(config):
    """将配置转换为初始状态"""
    from src.utils.memory_strategy import get_memory_strategy
    from src.memory.layered_memory import initialize_layered_memory

    # 提取配置
    novel_config = config['novel']
    worldbuilding = config['worldbuilding']
    characters = config['characters']
    generation = config['generation']

    # 构建角色字典
    char_dict = {}
    for char in characters:
        char_dict[char['name']] = char

    # 构建伏笔列表
    # 🔧 Bug #13修复: 初始伏笔使用简单格式(字符串),稍后会根据模式转换
    plot_tracks = []
    if generation.get('foreshadow_strategy') != 'conservative':
        # 根据故事梗概生成初始伏笔提示
        plot_tracks.append(f"主线剧情：{novel_config['synopsis'][:50]}...")

    # 设置随机种子（None表示每次不同）
    if generation.get('seed'):
        random.seed(generation['seed'])

    initial_state = {
        'world_bible': {
            'characters': char_dict,
            'worldbuilding': worldbuilding,
            'plot_threads': plot_tracks  # Fixed: was plot_tracks (typo)
        },
        'synopsis': novel_config['synopsis'],
        'chapters': [],
        'current_chapter_index': 1,
        'iteration': 0,
        'config': config  # 保存完整配置供节点使用
    }

    # 检测记忆策略
    memory_strategy = get_memory_strategy(config)

    if memory_strategy == 'layered':
        # 长篇模式：初始化分层记忆
        hot_memory, cold_memory = initialize_layered_memory(config)

        # 🔧 Bug #13修复: 长篇模式下,plot_threads应该是dict格式
        # 转换初始plot_threads为dict格式(含metadata)
        if plot_tracks:
            initial_state['world_bible']['plot_threads'] = {
                "active": [
                    {
                        "text": track,
                        "created_at": 1,
                        "importance": 10,  # 初始伏笔重要度最高
                        "resolved": False
                    } for track in plot_tracks
                ]
            }
        else:
            initial_state['world_bible']['plot_threads'] = {
                "active": []
            }

        # 🔧 获取或生成总纲和卷纲（支持新旧两种格式）
        # 优先从 bible/outline.yaml 读取，否则从 config 读取
        novel_outline = None
        volume_frameworks = None

        # 尝试从 bible/outline.yaml 读取（新格式）
        bible_dir = paths.get('bible_dir')
        if bible_dir:
            outline_file = os.path.join(bible_dir, 'outline.yaml')
            if os.path.exists(outline_file):
                try:
                    import yaml
                    with open(outline_file, 'r', encoding='utf-8') as f:
                        outline_data = yaml.safe_load(f)
                    novel_outline = outline_data.get('outline', {})
                    volume_frameworks = outline_data.get('volumes', [])
                    print(f"  📖 加载独立大纲文件: outline.yaml")
                except Exception as e:
                    print(f"  ⚠️  读取 outline.yaml 失败: {e}")

        # 回退到配置文件中的字段（旧格式）
        if novel_outline is None:
            novel_outline = config.get('novel_outline', {})
        if volume_frameworks is None:
            volume_frameworks = config.get('volume_frameworks', [])

        if novel_outline or volume_frameworks:
            print(f"  📖 加载配置中的大纲字段")

        # 如果配置中缺少总纲，生成默认总纲
        auto_generated = False  # 标记是否自动生成
        if not novel_outline:
            print(f"\n⚠️  配置中缺少总纲，使用默认结构")
            novel_outline = {
                'main_goal': f"完成故事：{novel_config['synopsis'][:100]}",
                'main_conflict': '待定（建议在配置中添加）',
                'protagonist_arc': '待定（建议在配置中添加）'
            }
            auto_generated = True

        # 如果配置中缺少卷纲，生成默认卷纲
        if not volume_frameworks:
            target_chapters = novel_config.get('target_chapters', 1)
            total_volumes = (target_chapters + 24) // 25  # 向上取整

            if total_volumes > 0:
                print(f"⚠️  配置中缺少卷纲，生成 {total_volumes} 个默认卷框架")
                volume_frameworks = []
                for vol_idx in range(1, total_volumes + 1):
                    start_ch = (vol_idx - 1) * 25 + 1
                    end_ch = min(vol_idx * 25, target_chapters)
                    volume_frameworks.append({
                        'title': f'第{vol_idx}卷',
                        'chapters': f'{start_ch}-{end_ch}',
                        'core_goal': '待定（建议在配置中添加）',
                        'key_events': [],
                        'ending_state': '待定',
                        'foreshadowing': []
                    })
                auto_generated = True

        # 🔧 新增：如果是自动生成的，保存到 outline.yaml
        if auto_generated and bible_dir:
            print(f"\n💾 保存自动生成的大纲到 outline.yaml...")
            outline_file = os.path.join(bible_dir, 'outline.yaml')

            # 转换为新格式
            outline_data = {
                'outline': {
                    'synopsis': novel_config.get('synopsis', ''),
                    'main_goal': novel_outline.get('main_goal', ''),
                    'main_conflict': novel_outline.get('main_conflict', ''),
                    'protagonist_arc': novel_outline.get('protagonist_arc', ''),
                    'phases': []  # 默认生成暂时没有 phases
                },
                'volumes': []
            }

            # 转换卷纲
            for i, vol in enumerate(volume_frameworks):
                outline_data['volumes'].append({
                    'volume': i + 1,
                    'title': vol.get('title', ''),
                    'chapters': vol.get('chapters', ''),
                    'core_goal': vol.get('core_goal', ''),
                    'key_events': vol.get('key_events', []),
                    'foreshadowing': vol.get('foreshadowing', []),
                    'ending_state': vol.get('ending_state', '')
                })

            try:
                os.makedirs(bible_dir, exist_ok=True)
                with open(outline_file, 'w', encoding='utf-8') as f:
                    yaml.dump(outline_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
                print(f"   ✅ 已保存到: {outline_file}")
                print(f"   📝 提示: 可以手动编辑此文件来完善大纲")
            except Exception as e:
                print(f"   ⚠️  保存失败: {e}")

        initial_state.update({
            'hot_memory': hot_memory,
            'cold_memory': cold_memory,
            'current_volume_index': 1,
            'current_volume_outline': '',
            'rag_enabled': False,
            'rag_storage_path': None,
            'volume_frameworks': volume_frameworks,
            'novel_outline': novel_outline,
            'volume_review_reports': [],
            'milestone_reports': []
        })
        print(f"\n🧠 启用分层记忆模式 (目标: {novel_config['target_chapters']} 章)")
        print(f"   • 每25章自动压缩记忆")
        print(f"   • 内存占用可控")

    return initial_state

def build_graph(config, db_path):
    """构建工作流图"""
    from src.utils.memory_strategy import should_use_layered_memory

    workflow = StateGraph(NovelState)

    # 检测是否使用分层记忆（长篇模式）
    use_layered = should_use_layered_memory(config['novel'].get('target_chapters', 1))

    # 添加基础节点
    workflow.add_node("planner", planner_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("memory", memory_update_node)

    if use_layered:
        # 长篇模式：添加卷管理节点
        from src.nodes.volume_planner import volume_planner_node
        from src.nodes.volume_review import volume_review_node

        workflow.add_node("volume_planner", volume_planner_node)
        workflow.add_node("volume_review", volume_review_node)

        print(f"  🔧 长篇工作流：包含卷规划和卷审查节点")

    # 设置入口点
    if use_layered:
        # 长篇：先卷规划，再章节规划
        workflow.set_entry_point("volume_planner")
        workflow.add_edge("volume_planner", "planner")
    else:
        # 短篇：直接章节规划
        workflow.set_entry_point("planner")

    # 定义边
    workflow.add_edge("planner", "writer")
    workflow.add_edge("writer", "critic")  # Writer always goes to Critic

    # Critic 之后的条件边：决定是否需要修改
    def should_revise(state):
        """检查 Critic 反馈，决定是否需要重写"""
        feedback = state.get("feedback", "")
        iteration = state.get("iteration", 0)
        max_iterations = config.get('generation', {}).get('max_revision_iterations', 2)

        # 如果已经重试太多次，强制通过
        if iteration >= max_iterations:
            print(f"\n  ⚠️  已达最大修订次数({max_iterations})，继续流程")
            return "memory"

        # 检查反馈中是否包含"需修改"或"不合格"
        if "需修改" in feedback or "不合格" in feedback or "问题" in feedback:
            if iteration < max_iterations:
                print(f"\n  🔄 Critic 要求修改，重新生成 (第 {iteration + 1}/{max_iterations} 次)")
                return "writer"

        return "memory"

    workflow.add_conditional_edges(
        "critic",
        should_revise,
        {"writer": "writer", "memory": "memory"}
    )

    # 根据配置决定是否循环
    target_chapters = config['novel'].get('target_chapters', 1)
    if target_chapters > 1:
        # 添加条件边，检查是否完成所有章节
        def should_continue(state):
            current_chapter = state.get('current_chapter_index', 1)
            if current_chapter <= target_chapters:
                # 🔧 Bug #18修复: 检查是否需要卷审查
                # 使用专门的标志而不是chapters_in_volume (因为压缩后会重置)
                if use_layered and state.get("need_volume_review", False):
                    return "volume_review"

                return "planner"
            return "end"

        if use_layered:
            # 长篇：memory → should_continue → volume_review/planner/end
            # volume_review → planner (继续下一卷)
            workflow.add_conditional_edges(
                "memory",
                should_continue,
                {"volume_review": "volume_review", "planner": "planner", "end": END}
            )
            workflow.add_edge("volume_review", "volume_planner")  # 卷审查后，规划下一卷
        else:
            # 短篇：memory → should_continue → planner/end
            workflow.add_conditional_edges(
                "memory",
                should_continue,
                {"planner": "planner", "end": END}
            )
    else:
        workflow.add_edge("memory", END)

    # 持久化（使用项目专属数据库）
    conn = sqlite3.connect(db_path, check_same_thread=False)
    memory = SqliteSaver(conn)

    # 编译
    app = workflow.compile(checkpointer=memory)
    return app

def save_world_bible(world_bible, config, bible_dir):
    """保存世界状态"""
    os.makedirs(bible_dir, exist_ok=True)

    novel_title = config['novel']['title']
    safe_title = "".join(c for c in novel_title if c.isalnum() or c in (' ', '-', '_')).strip()

    filename = f"{bible_dir}/{safe_title}_world_state.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(world_bible, f, indent=2, ensure_ascii=False)

    return filename

if __name__ == "__main__":
    print("=" * 60)
    print("📚 AI 小说生成器 - Powered by Claude 4.5")
    print("=" * 60)

    # 检查API Key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set!")
        print("Please set it in your .env file")
        sys.exit(1)

    # 初始化项目管理器
    pm = ProjectManager()

    # 显示当前项目列表
    pm.print_projects_table()

    # 加载配置
    print("\n📖 加载配置文件...")
    config = load_config()

    # 检查是否为已存在项目或新项目
    current_project = pm.get_current_project()
    novel_title = config['novel']['title']

    if current_project and current_project['title'] == novel_title:
        # 使用现有项目
        print(f"\n🔄 使用现有项目: {novel_title}")
        project_id = current_project['project_id']
        paths = pm.get_project_paths(project_id)
    else:
        # 创建新项目
        print(f"\n✨ 创建新项目: {novel_title}")
        project_id, project_info = pm.create_project(config)
        paths = pm.get_project_paths(project_id)

    print(f"\n✅ 配置加载成功！")
    print(f"   小说标题: {config['novel']['title']}")
    print(f"   类型: {config['novel']['type']}")
    print(f"   目标章节: {config['novel']['target_chapters']}")
    print(f"   角色数量: {len(config['characters'])}")

    # 显示差异性设置
    gen_config = config['generation']
    print(f"\n🎲 创作差异性设置:")
    print(f"   随机性等级: {gen_config['randomness_level']}")
    print(f"   写作温度: {gen_config['writer_temp']:.2f}")
    print(f"   伏笔策略: {gen_config['foreshadow_strategy']}")
    print(f"   角色自主性: {gen_config['character_autonomy']}")
    print(f"   每次运行都会产生不同的故事发展！")

    # 构建初始状态（注入项目路径）
    initial_state = config_to_initial_state(config)
    initial_state['project_paths'] = paths  # 传递给writer节点使用

    # 构建工作流（使用项目专属数据库）
    print("\n🔧 构建工作流...")
    app = build_graph(config, paths['db_file'])
    print("✅ 工作流构建成功")

    # 显示故事设定
    print("\n" + "="*60)
    print("📖 故事设定预览")
    print("="*60)
    print(f"\n{config['novel']['synopsis']}")
    print(f"\n🌍 世界观:")
    print(f"   时代: {config['worldbuilding']['era']}")
    print(f"   场景: {config['worldbuilding']['setting']}")
    print(f"   力量体系: {config['worldbuilding']['power_system']}")

    print(f"\n👥 主要角色:")
    for char in config['characters']:
        print(f"   • {char['name']} ({char['age']}岁) - {char['occupation']}")
        print(f"     性格: {', '.join(char['traits'][:5])}")
        print(f"     目标: {char['goal']}")

    print(f"\n🎨 写作风格: {config['style']['style_name']}")

    # 开始生成
    print("\n" + "="*60)
    print("🎬 开始生成章节...")
    print("="*60)

    # 运行工作流
    thread_id = f"novel_{project_id}"
    config_obj = {"configurable": {"thread_id": thread_id}}

    # 检查是否有保存的状态（支持断点续传）
    snapshot = app.get_state(config_obj)
    resume_from_checkpoint = False

    if snapshot and snapshot.values:
        saved_chapter = snapshot.values.get('current_chapter_index', 1)
        target_chapters = config['novel'].get('target_chapters', 1)

        # 如果已经生成了部分章节，提示用户是否继续
        if saved_chapter > 1 and saved_chapter <= target_chapters:
            print(f"\n🔄 检测到未完成的生成任务")
            print(f"   进度: 已完成 {saved_chapter - 1}/{target_chapters} 章")
            print(f"   将从第 {saved_chapter} 章继续生成")
            print(f"\n   按 Enter 继续，或 Ctrl+C 退出")

            try:
                input()
                resume_from_checkpoint = True
            except KeyboardInterrupt:
                print("\n\n❌ 用户取消")
                sys.exit(0)

    chapter_drafts = []
    final_state = None

    try:
        if resume_from_checkpoint:
            # 从断点恢复（不传 initial_state）
            print("\n🔄 从断点恢复生成...")
            for step_output in app.stream(None, config=config_obj):
                for node_name, node_output in step_output.items():
                    print(f"\n✓ 完成节点: {node_name.upper()}")

                    # 显示进度
                    if node_name == "planner" and "current_beats" in node_output:
                        beats_preview = node_output['current_beats'][:200]
                        print(f"  生成大纲: {len(node_output['current_beats'])} 字符")
                        print(f"  预览: {beats_preview}...")

                    elif node_name == "writer" and "draft" in node_output:
                        draft = node_output['draft']
                        word_count = len(draft)
                        chapter_drafts.append(draft)
                        print(f"  生成正文: {word_count} 字符")
                        print(f"  预计字数: ~{word_count // 2} 字")

                    elif node_name == "critic" and "feedback" in node_output:
                        feedback = node_output['feedback']
                        print(f"  评审反馈: {feedback[:150]}...")

                    elif node_name == "memory":
                        chapter_idx = node_output.get('current_chapter_index', 1) - 1
                        print(f"  已完成第 {chapter_idx} 章")
                        print(f"  世界状态已更新")

                        # 更新项目进度
                        pm.update_project_progress(project_id, chapter_idx)

                    final_state = node_output
        else:
            # 从头开始新的生成
            print("\n🎬 开始新的生成任务...")
            for step_output in app.stream(initial_state, config=config_obj):
                for node_name, node_output in step_output.items():
                    print(f"\n✓ 完成节点: {node_name.upper()}")

                    # 显示进度
                    if node_name == "planner" and "current_beats" in node_output:
                        beats_preview = node_output['current_beats'][:200]
                        print(f"  生成大纲: {len(node_output['current_beats'])} 字符")
                        print(f"  预览: {beats_preview}...")

                    elif node_name == "writer" and "draft" in node_output:
                        draft = node_output['draft']
                        word_count = len(draft)
                        chapter_drafts.append(draft)
                        print(f"  生成正文: {word_count} 字符")
                        print(f"  预计字数: ~{word_count // 2} 字")

                    elif node_name == "critic" and "feedback" in node_output:
                        feedback = node_output['feedback']
                        print(f"  评审反馈: {feedback[:150]}...")

                    elif node_name == "memory":
                        chapter_idx = node_output.get('current_chapter_index', 1) - 1
                        print(f"  已完成第 {chapter_idx} 章")
                        print(f"  世界状态已更新")

                        # 更新项目进度
                        pm.update_project_progress(project_id, chapter_idx)

                    final_state = node_output

        # 生成摘要（章节已在writer节点中实时保存）
        print("\n" + "="*60)
        print("📊 生成完成！")
        print("="*60)
        print(f"\n✅ 成功生成 {len(chapter_drafts)} 章")
        print(f"✅ 总字数约: {sum(len(d) for d in chapter_drafts) // 2} 字")

        print(f"\n📁 文件位置:")
        print(f"   章节目录: {paths['manuscript_dir']}")

        # 保存世界状态
        if final_state and 'world_bible' in final_state:
            bible_file = save_world_bible(final_state['world_bible'], config, paths['bible_dir'])
            print(f"   世界状态: {bible_file}")

        print(f"\n💡 下次运行:")
        print(f"   • 使用相同配置会自动继续此项目")
        print(f"   • 运行 python3 configure_novel.py 创建新项目")
        print(f"   • 运行 python3 manage_projects.py 管理所有项目")

    except KeyboardInterrupt:
        print("\n\n⚠️  生成已中断")
        print("   进度已保存，下次运行将从断点继续")
    except Exception as e:
        print(f"\n❌ 生成过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
