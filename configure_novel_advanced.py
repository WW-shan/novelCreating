#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Novel Configuration Tool (增强版)
支持自定义大纲、卷纲、更完整的小说配置
"""

import os
import yaml
import json
from datetime import datetime

class AdvancedNovelConfigurator:
    def __init__(self):
        self.config = {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'version': '3.0'
            },
            'novel': {},
            'outline': {},  # 新增：总纲
            'volumes': [],  # 新增：卷纲
            'characters': [],
            'worldbuilding': {},
            'style': {},
            'generation': {}
        }

    def print_header(self, text):
        """打印标题"""
        print("\n" + "="*60)
        print(f"  {text}")
        print("="*60)

    def step_1_outline_mode(self):
        """步骤1：选择大纲模式"""
        self.print_header("步骤 1/8: 选择大纲模式")

        print("\n请选择大纲配置方式：")
        print("  1. 简易模式（只需梗概，AI 自动规划）- 推荐！")
        print("  2. AI 自动生成（完整总纲+卷纲，每卷25章）")
        print("  3. 完整自定义（手动输入所有内容）")
        print("  4. 导入现有大纲（从文件导入）")

        choice = input("\n请选择 (1-4) [1]: ").strip() or "1"

        return choice

    def step_2_basic_info(self):
        """步骤2：基本信息"""
        self.print_header("步骤 2/8: 基本信息")

        title = input("小说标题: ").strip() or "未命名小说"
        novel_type = input("类型（玄幻/都市/科幻/悬疑等）: ").strip() or "未分类"

        print("\n目标章节数：")
        print("  - 短篇：10-50 章")
        print("  - 中篇：50-200 章")
        print("  - 长篇：200-500 章")
        target_chapters = int(input("目标章节数 (10-500): ").strip() or "100")

        self.config['novel'] = {
            'title': title,
            'type': novel_type,
            'target_chapters': target_chapters
        }

        return target_chapters

    def step_3_ai_generate_outline(self, target_chapters):
        """步骤3：AI 自动生成完整大纲"""
        self.print_header("步骤 3/8: AI 自动生成大纲")

        print("\n🤖 AI 将自动生成：")
        print("  - 总纲（主目标、主冲突、成长弧）")
        print("  - 里程碑（3-5个关键节点）")
        print(f"  - 卷纲（共 {(target_chapters + 24) // 25} 卷，每卷25章）")

        confirm = input("\n确认开始生成？(y/n) [y]: ").strip().lower()
        if confirm == 'n':
            print("已取消，将使用简易模式")
            synopsis = input("\n故事梗概: ").strip()
            self.config['novel']['synopsis'] = synopsis
            self.config['outline'] = {
                'synopsis': synopsis,
                'main_goal': "（AI 自动生成）",
                'main_conflict': "（AI 自动生成）",
                'protagonist_arc': "（AI 自动生成）",
                'phases': []
            }
            self.config['volumes'] = []
            return

        # 导入 generate_outline 的功能
        from generate_outline import generate_novel_outline, generate_volume_frameworks

        print("\n🤖 AI 正在生成总纲...")
        novel_outline = generate_novel_outline(self.config)
        print("✅ 总纲生成完成")

        print("\n🤖 AI 正在生成卷纲...")
        volume_frameworks = generate_volume_frameworks(self.config, novel_outline)
        print("✅ 卷纲生成完成")

        # 转换为新格式
        self.config['outline'] = {
            'synopsis': self.config['novel']['synopsis'],
            'main_goal': novel_outline.get('main_goal', ''),
            'main_conflict': novel_outline.get('main_conflict', ''),
            'protagonist_arc': novel_outline.get('protagonist_arc', ''),
            'phases': []
        }

        # 转换 key_milestones 为 phases
        milestones = novel_outline.get('key_milestones', [])
        if milestones:
            phases = []
            for i, ms in enumerate(milestones):
                prev_chapter = milestones[i-1]['target_chapter'] + 1 if i > 0 else 1
                curr_chapter = ms['target_chapter']
                phases.append({
                    'name': f"阶段{i+1}",
                    'goal': ms['milestone'],
                    'chapters': f"{prev_chapter}-{curr_chapter}"
                })
            self.config['outline']['phases'] = phases

        # 转换 volume_frameworks
        volumes = []
        for vol in volume_frameworks:
            volumes.append({
                'volume': len(volumes) + 1,
                'title': vol.get('title', ''),
                'chapters': vol.get('chapters', ''),
                'core_goal': vol.get('core_goal', ''),
                'key_events': vol.get('key_events', []),
                'foreshadowing': vol.get('foreshadowing', []),
                'ending_state': vol.get('ending_state', '')
            })
        self.config['volumes'] = volumes

        print(f"\n✅ AI 生成完成！")
        print(f"   总纲: {len(phases)} 个阶段")
        print(f"   卷纲: {len(volumes)} 卷")

    def step_3_custom_outline(self, target_chapters):
        """步骤3：自定义总纲"""
        self.print_header("步骤 3/8: 总纲设置")

        print("\n【总纲】用于指导整本小说的方向")
        print("提示：")
        print("  - 主目标：主角最终要达成什么")
        print("  - 主线冲突：核心矛盾是什么")
        print("  - 主角成长线：主角如何成长/变化")

        # 梗概
        synopsis = input("\n故事梗概（简短描述）: ").strip()

        # 是否需要详细总纲
        need_detailed = input("\n是否需要详细总纲？(y/n) [y]: ").strip().lower() != 'n'

        if need_detailed:
            main_goal = input("主目标: ").strip() or "（待定）"
            main_conflict = input("主线冲突: ").strip() or "（待定）"
            protagonist_arc = input("主角成长线: ").strip() or "（待定）"

            # 阶段划分
            print("\n故事阶段划分：")
            print("建议：")
            print("  - 短篇（10-50章）：3 阶段")
            print("  - 中篇（50-200章）：5-8 阶段")
            print("  - 长篇（200-500章）：8-15 阶段")

            num_phases = int(input(f"阶段数量 (3-15): ").strip() or "5")

            phases = []
            for i in range(num_phases):
                print(f"\n--- 第 {i+1} 阶段 ---")
                phase_name = input(f"阶段名称: ").strip() or f"第{i+1}阶段"
                phase_goal = input(f"阶段目标: ").strip() or "（待定）"
                phase_chapters = input(f"章节范围（如：1-20）: ").strip()

                phases.append({
                    'name': phase_name,
                    'goal': phase_goal,
                    'chapters': phase_chapters
                })

            self.config['outline'] = {
                'synopsis': synopsis,
                'main_goal': main_goal,
                'main_conflict': main_conflict,
                'protagonist_arc': protagonist_arc,
                'phases': phases
            }
        else:
            self.config['outline'] = {
                'synopsis': synopsis,
                'main_goal': "（AI 自动生成）",
                'main_conflict': "（AI 自动生成）",
                'protagonist_arc': "（AI 自动生成）",
                'phases': []
            }

        self.config['novel']['synopsis'] = synopsis

    def step_4_volume_planning(self, target_chapters):
        """步骤4：卷纲规划（仅长篇）"""
        self.print_header("步骤 4/8: 卷纲规划")

        # 长篇才需要卷纲
        if target_chapters < 100:
            print("\n章节数 < 100，跳过卷纲规划")
            self.config['volumes'] = []
            return

        print(f"\n总计 {target_chapters} 章，建议按卷组织")
        print("推荐：")
        print("  - 每卷 20-30 章")
        print(f"  - 共 {target_chapters // 25} 卷左右")

        need_volumes = input("\n是否配置卷纲？(y/n) [y]: ").strip().lower() != 'n'

        if not need_volumes:
            self.config['volumes'] = []
            return

        num_volumes = int(input("卷数: ").strip() or str(target_chapters // 25))
        chapters_per_volume = target_chapters // num_volumes

        volumes = []
        for i in range(num_volumes):
            print(f"\n--- 第 {i+1} 卷 ---")
            title = input(f"卷标题: ").strip() or f"第{i+1}卷"

            start_ch = i * chapters_per_volume + 1
            end_ch = (i + 1) * chapters_per_volume if i < num_volumes - 1 else target_chapters

            core_goal = input(f"本卷核心目标: ").strip() or "（待定）"

            # 关键事件
            print(f"关键事件（用逗号分隔，如：战斗,突破,反转）:")
            key_events_str = input("  ").strip()
            key_events = [e.strip() for e in key_events_str.split(',') if e.strip()]

            # 伏笔
            print(f"需埋下的伏笔（用逗号分隔）:")
            foreshadowing_str = input("  ").strip()
            foreshadowing = [f.strip() for f in foreshadowing_str.split(',') if f.strip()]

            ending_state = input(f"卷末状态: ").strip() or "（待定）"

            volumes.append({
                'volume': i + 1,
                'title': title,
                'chapters': f"{start_ch}-{end_ch}",
                'core_goal': core_goal,
                'key_events': key_events,
                'foreshadowing': foreshadowing,
                'ending_state': ending_state
            })

        self.config['volumes'] = volumes

    def step_5_worldbuilding(self):
        """步骤5：世界观设定"""
        self.print_header("步骤 5/8: 世界观设定")

        era = input("时代背景: ").strip() or "现代"
        setting = input("主要场景: ").strip() or "都市"
        power_system = input("力量体系（如无则留空）: ").strip() or "无"

        self.config['worldbuilding'] = {
            'era': era,
            'setting': setting,
            'power_system': power_system
        }

    def step_6_characters(self):
        """步骤6：角色设定"""
        self.print_header("步骤 6/8: 角色设定")

        print("\n至少需要 1 个主角")
        num_chars = int(input("角色数量 (1-5): ").strip() or "1")

        characters = []
        for i in range(num_chars):
            print(f"\n--- 角色 {i+1} ---")
            name = input("姓名: ").strip() or f"角色{i+1}"
            age = input("年龄: ").strip() or "未知"
            occupation = input("职业: ").strip() or "未知"
            goal = input("目标: ").strip() or "生存"

            print(f"性格特点（用逗号分隔，如：冷静,理性,果断）:")
            traits_str = input("  ").strip()
            traits = [t.strip() for t in traits_str.split(',') if t.strip()]

            characters.append({
                'name': name,
                'age': age,
                'occupation': occupation,
                'goal': goal,
                'traits': traits,
                'status': 'Alive',
                'location': self.config['worldbuilding']['setting'],
                'relationships': {}
            })

        self.config['characters'] = characters

    def step_7_style_settings(self):
        """步骤7：风格设置"""
        self.print_header("步骤 7/8: 写作风格")

        print("\n请选择风格：")
        print("  1. 番茄爽文（快节奏、爽点密集）")
        print("  2. 传统文学（细腻描写、深度刻画）")
        print("  3. 轻小说（对话多、节奏轻快）")

        style_choice = input("选择 (1-3) [1]: ").strip() or "1"

        style_map = {
            '1': {
                'style_name': '番茄爽文（快节奏、爽点密集）',
                'pace': 'fast',
                'tone': 'intense',
                'is_fanqie_style': True
            },
            '2': {
                'style_name': '传统文学（细腻描写、深度刻画）',
                'pace': 'medium',
                'tone': 'literary',
                'is_fanqie_style': False
            },
            '3': {
                'style_name': '轻小说（对话多、节奏轻快）',
                'pace': 'fast',
                'tone': 'light',
                'is_fanqie_style': False
            }
        }

        self.config['style'] = style_map.get(style_choice, style_map['1'])

    def step_8_generation_settings(self):
        """步骤8：生成参数"""
        self.print_header("步骤 8/8: 生成参数")

        print("\n随机性等级（影响故事差异性）：")
        print("  low: 更一致、可控")
        print("  medium: 平衡")
        print("  high: 更多惊喜、不可预测")

        randomness = input("随机性 (low/medium/high) [medium]: ").strip() or "medium"

        # 根据随机性设置温度
        temp_map = {'low': 0.7, 'medium': 0.85, 'high': 1.0}
        writer_temp = temp_map.get(randomness, 0.85)

        self.config['generation'] = {
            'randomness_level': randomness,
            'writer_temp': writer_temp,
            'planner_temp': 0.7,
            'critic_temp': 0.3,
            'foreshadow_strategy': 'moderate',
            'character_autonomy': 'medium',
            'max_revision_iterations': 2,
            'enable_plot_twists': True
        }

    def step_9_review_and_save(self):
        """步骤9：预览并保存"""
        self.print_header("配置完成！让我们预览一下")

        print(f"\n📖 小说标题：{self.config['novel']['title']}")
        print(f"📝 类型：{self.config['novel']['type']}")
        print(f"📚 目标章节：{self.config['novel']['target_chapters']}")

        print(f"\n🎯 总纲：")
        print(f"   梗概：{self.config['outline']['synopsis']}")
        if self.config['outline']['phases']:
            print(f"   阶段数：{len(self.config['outline']['phases'])}")

        if self.config['volumes']:
            print(f"\n📕 卷纲：共 {len(self.config['volumes'])} 卷")
            for vol in self.config['volumes'][:3]:
                print(f"   - 第{vol['volume']}卷：{vol['title']} ({vol['chapters']}章)")

        print(f"\n🌍 世界观：")
        print(f"   时代：{self.config['worldbuilding']['era']}")
        print(f"   场景：{self.config['worldbuilding']['setting']}")

        print(f"\n👥 角色：")
        for char in self.config['characters']:
            print(f"   - {char['name']} ({char['age']}岁, {char['occupation']})")

        print(f"\n🎨 风格：{self.config['style']['style_name']}")

        print("\n" + "─"*60)
        confirm = input("确认保存配置并创建项目？(y/n) [y]: ").strip().lower()
        if confirm == 'n':
            print("❌ 配置未保存")
            return False

        # 创建项目
        from src.project_manager import ProjectManager
        pm = ProjectManager()

        try:
            project_id, project_info = pm.create_project(self.config)
            print(f"\n✅ 项目已创建：{project_info['title']}")
            print(f"   项目ID: {project_id}")
            print(f"   配置文件: projects/{project_id}/config.yaml")
            print(f"   数据库: projects/{project_id}/state.db")
            print(f"   稿件目录: projects/{project_id}/manuscript/")

            # 如果有大纲，保存到项目目录
            if self.config['outline']['phases'] or self.config['volumes']:
                outline_file = f"projects/{project_id}/bible/outline.yaml"
                os.makedirs(os.path.dirname(outline_file), exist_ok=True)
                with open(outline_file, 'w', encoding='utf-8') as f:
                    yaml.dump({
                        'outline': self.config['outline'],
                        'volumes': self.config['volumes']
                    }, f, allow_unicode=True, default_flow_style=False)
                print(f"   大纲文件: projects/{project_id}/bible/outline.yaml")

        except Exception as e:
            if "已存在" in str(e):
                print(f"\n✅ 项目已存在：{self.config['novel']['title']}")
            else:
                print(f"\n❌ 项目创建失败: {e}")
                return False

        # 兼容性：同时保存到旧位置
        default_path = '/project/novel/bible/novel_config_latest.yaml'
        os.makedirs('/project/novel/bible', exist_ok=True)
        with open(default_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)

        print(f"\n💡 下一步：")
        print(f"   ./novel.sh generate  # 开始生成章节")
        print(f"   ./novel.sh projects  # 管理所有项目")

        return True

    def run(self):
        """运行完整的配置流程"""
        try:
            outline_mode = self.step_1_outline_mode()
            target_chapters = self.step_2_basic_info()

            if outline_mode == '2':
                # AI 自动生成完整大纲
                self.step_3_ai_generate_outline(target_chapters)
                # AI 已经生成了卷纲，跳过手动输入
            elif outline_mode == '3':
                # 完全自定义模式
                self.step_3_custom_outline(target_chapters)
                self.step_4_volume_planning(target_chapters)
            elif outline_mode == '4':
                # TODO: 导入大纲
                print("\n⚠️  导入功能开发中，使用简易模式")
                synopsis = input("\n故事梗概: ").strip()
                self.config['novel']['synopsis'] = synopsis
                self.config['outline'] = {
                    'synopsis': synopsis,
                    'main_goal': "（AI 自动生成）",
                    'main_conflict': "（AI 自动生成）",
                    'protagonist_arc': "（AI 自动生成）",
                    'phases': []
                }
                self.config['volumes'] = []
            else:
                # 简易模式（默认）
                synopsis = input("\n故事梗概: ").strip()
                self.config['novel']['synopsis'] = synopsis
                self.config['outline'] = {
                    'synopsis': synopsis,
                    'main_goal': "（AI 自动生成）",
                    'main_conflict': "（AI 自动生成）",
                    'protagonist_arc': "（AI 自动生成）",
                    'phases': []
                }
                self.config['volumes'] = []

            self.step_5_worldbuilding()
            self.step_6_characters()
            self.step_7_style_settings()
            self.step_8_generation_settings()
            success = self.step_9_review_and_save()

            if success:
                self.print_header("🎉 配置完成！")
                print("\n现在可以开始生成小说了！")

        except KeyboardInterrupt:
            print("\n\n⚠️  配置已取消")
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    configurator = AdvancedNovelConfigurator()
    configurator.run()
