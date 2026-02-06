#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Novel Configuration Tool (优化版)
交互式小说配置工具 - 适配多项目系统和番茄小说风格
"""

import os
import yaml
import json
from datetime import datetime

class NovelConfigurator:
    def __init__(self):
        self.config = {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'version': '2.0'
            },
            'novel': {},
            'characters': [],
            'worldbuilding': {},
            'style': {},
            'generation': {}
        }

        # 预设模板（新增番茄小说风格模板）
        self.templates = {
            '1': {
                'name': '番茄爽文（末世/系统流）',
                'novel_type': 'fanqie_shuangwen',
                'era': '现代末世',
                'setting': '全球灾变后的废土世界',
                'power_system': '系统、生存点、技能',
                'example_synopsis': '全球末日降临，主角获得收割系统，在别人挣扎求生时开始收割生存点，从弱者逆袭成最强收割者',
                'style': 'fast_pace',
                'tone': 'intense'
            },
            '2': {
                'name': '番茄爽文（都市修仙）',
                'novel_type': 'fanqie_urban_cultivation',
                'era': '现代都市',
                'setting': '华夏都市',
                'power_system': '修真等级、灵力',
                'example_synopsis': '修真归来的仙尊重生都市，碾压一切不服，收美女、打脸敌人、称霸商界',
                'style': 'fast_pace',
                'tone': 'domineering'
            },
            '3': {
                'name': '玄幻修仙（传统）',
                'novel_type': 'xuanhuan',
                'era': '架空古代',
                'setting': '九州大陆',
                'power_system': '灵力修炼体系（炼气→筑基→金丹→元婴）',
                'example_synopsis': '少年从废材逆袭，获得神秘传承，踏上逆天修炼之路，复仇、收徒、建立宗门',
                'style': 'balanced',
                'tone': 'epic'
            },
            '4': {
                'name': '赛博朋克/科幻',
                'novel_type': 'cyberpunk',
                'era': '2087年',
                'setting': '霓虹闪烁的超大都市',
                'power_system': '神经接口技术、黑客技能',
                'example_synopsis': '一个底层黑客发现公司控制人类意识的阴谋，决定反抗这个dystopian世界',
                'style': 'dark',
                'tone': 'tense'
            },
            '5': {
                'name': '悬疑推理',
                'novel_type': 'mystery',
                'era': '现代',
                'setting': '都市与郊区',
                'power_system': '无',
                'example_synopsis': '侦探接到神秘委托调查连环失踪案，背后牵扯出惊人真相',
                'style': 'slow_burn',
                'tone': 'mysterious'
            },
            '6': {
                'name': '自定义',
                'novel_type': 'custom',
                'era': '',
                'setting': '',
                'power_system': '',
                'example_synopsis': '完全自定义你的小说设定',
                'style': 'balanced',
                'tone': 'neutral'
            }
        }

        # 性格特质词库
        self.trait_library = {
            '正面': ['勇敢', '聪明', '善良', '正直', '忠诚', '坚韧', '幽默', '温柔', '果断', '睿智'],
            '中性': ['冷静', '理性', '神秘', '孤独', '内向', '叛逆', '固执', '谨慎'],
            '负面': ['傲慢', '冲动', '贪婪', '懦弱', '多疑', '残忍', '自私'],
            '番茄风格': ['狠辣', '腹黑', '霸道', '冷酷', '算计', '果敢', '狂傲']
        }

        # 写作风格选项（新增番茄风格）
        self.style_options = {
            '1': {'name': '番茄爽文（快节奏、爽点密集）', 'temperature': 0.75, 'tone': 'intense', 'pace': 'fast'},
            '2': {'name': '热血激昂', 'temperature': 0.8, 'tone': 'passionate', 'pace': 'fast'},
            '3': {'name': '悬疑紧张', 'temperature': 0.7, 'tone': 'tense', 'pace': 'medium'},
            '4': {'name': '黑暗压抑', 'temperature': 0.7, 'tone': 'dark', 'pace': 'medium'},
            '5': {'name': '轻松幽默', 'temperature': 0.8, 'tone': 'humorous', 'pace': 'medium'}
        }

    def print_header(self, text):
        """打印标题"""
        print("\n" + "="*60)
        print(f"  {text}")
        print("="*60)

    def print_section(self, text):
        """打印章节标题"""
        print(f"\n{'─'*60}")
        print(f"📝 {text}")
        print(f"{'─'*60}")

    def get_input(self, prompt, default=None, validate=None):
        """获取用户输入，支持默认值和验证"""
        if default:
            full_prompt = f"{prompt} [默认: {default}]: "
        else:
            full_prompt = f"{prompt}: "

        while True:
            user_input = input(full_prompt).strip()
            if not user_input and default:
                return default
            if not user_input:
                print("❌ 这是必填项，请输入内容")
                continue
            if validate and not validate(user_input):
                continue
            return user_input

    def get_choice(self, prompt, options):
        """获取用户选择"""
        print(f"\n{prompt}")
        for key, value in options.items():
            if isinstance(value, dict) and 'name' in value:
                print(f"  {key}. {value['name']}")
            else:
                print(f"  {key}. {value}")

        while True:
            choice = input("请选择（输入数字）: ").strip()
            if choice in options:
                return choice
            print("❌ 无效选择，请重新输入")

    def step_1_choose_template(self):
        """步骤1：选择小说模板"""
        self.print_header("欢迎使用 AI 小说生成器 🎭")
        print("\n🎯 多项目管理系统已启用")
        print("   每个小说拥有独立的配置、进度和文件")
        print("   你可以同时创作多个小说项目！\n")

        print("首先，让我们选择一个小说类型作为起点...")
        print("（你可以在后续步骤中完全自定义所有设定）")

        template_choice = self.get_choice(
            "\n请选择小说类型模板：",
            self.templates
        )

        template = self.templates[template_choice]
        if template_choice != '6':
            print(f"\n✅ 已选择：{template['name']}")
            print(f"   示例梗概：{template['example_synopsis']}")
        else:
            print(f"\n✅ 已选择：完全自定义模式")

        return template

    def step_2_basic_info(self, template):
        """步骤2：基础信息"""
        self.print_section("第一部分：基础设定")

        # 小说标题
        title = self.get_input("1. 给你的小说起个标题")

        # 故事梗概
        print(f"\n2. 用1-3句话描述你的故事")
        if template.get('example_synopsis'):
            print(f"   示例：{template['example_synopsis']}")
        synopsis = self.get_input("   你的故事")

        # 目标章节数（支持1-500章）
        def validate_chapters(x):
            try:
                num = int(x)
                if num < 1:
                    print("❌ 章节数至少为1")
                    return False
                if num > 500:
                    print("❌ 章节数不能超过500（建议100章以内）")
                    return False
                if num > 100:
                    confirm = input(f"   警告：{num}章是长篇小说，生成时间较长。确认？(y/n): ").strip().lower()
                    if confirm != 'y':
                        return False
                return True
            except:
                print("❌ 请输入有效的数字")
                return False

        print("\n3. 计划写多少章？")
        print("   提示：短篇(10-30章) | 中篇(30-60章) | 长篇(60-100章) | 超长篇(100+章)")
        chapters = int(self.get_input("   章节数", default="100", validate=validate_chapters))

        self.config['novel'] = {
            'title': title,
            'synopsis': synopsis,
            'target_chapters': chapters,
            'type': template['novel_type']
        }

    def step_3_worldbuilding(self, template):
        """步骤3：世界观设定"""
        self.print_section("第二部分：世界观设定")

        # 时代背景
        if template.get('era'):
            print(f"1. 时代背景 [参考: {template['era']}]")
            era = self.get_input("   你的设定", default=template['era'])
        else:
            era = self.get_input("1. 时代背景（如：现代、古代、未来2077年）")

        # 主要场景
        if template.get('setting'):
            print(f"\n2. 故事发生的地点 [参考: {template['setting']}]")
            setting = self.get_input("   你的设定", default=template['setting'])
        else:
            setting = self.get_input("2. 主要场景/地点")

        # 力量体系/特殊设定
        if template.get('power_system'):
            print(f"\n3. 特殊设定（力量体系/科技水平/魔法规则等）")
            print(f"   [参考: {template['power_system']}]")
            power_system = self.get_input("   你的设定", default=template['power_system'])
        else:
            print("\n3. 特殊设定（力量体系/系统/科技等，可选）")
            power_system = input("   你的设定（按回车跳过）: ").strip() or "无"

        self.config['worldbuilding'] = {
            'era': era,
            'setting': setting,
            'power_system': power_system
        }

    def step_4_characters(self):
        """步骤4：角色设定（简化版）"""
        self.print_section("第三部分：角色设定")

        print("💡 提示：至少需要1个主角，建议2-3个主要角色")
        print("   （可以先创建主角，其他角色由AI自动生成）\n")

        char_count = 1
        while True:
            print(f"\n{'─'*40}")
            print(f"⭐ 角色 #{char_count}")
            print(f"{'─'*40}")

            # 角色姓名
            name = self.get_input("1. 姓名")

            # 年龄
            age = self.get_input("2. 年龄", default="25")

            # 职业/身份
            occupation = self.get_input("3. 职业/身份", default="未知")

            # 性格特点（简化）
            print("\n4. 性格特点（选择3-5个，或自己输入）")
            print(f"   常用：{', '.join(self.trait_library['正面'][:5] + self.trait_library['番茄风格'][:3])}")
            traits_input = self.get_input("   输入特点（用逗号,分隔）", default="冷静,理性,果断")
            traits = [t.strip() for t in traits_input.split(',') if t.strip()]

            # 目标/动机
            goal = self.get_input("5. 角色的核心目标", default="变强/生存")

            character = {
                'name': name,
                'age': age,
                'occupation': occupation,
                'traits': traits,
                'goal': goal,
                'location': self.config['worldbuilding']['setting'],
                'status': 'Alive',
                'relationships': {}
            }

            self.config['characters'].append(character)

            print(f"\n✅ 角色 '{name}' 创建完成！")

            # 询问是否继续添加
            if char_count >= 1:
                continue_add = input("\n是否添加更多角色？(y/n) [n]: ").strip().lower()
                if continue_add != 'y':
                    break

            char_count += 1

            if char_count > 5:
                print("\n💡 建议：不要创建太多角色，AI会根据需要自动生成配角")
                break

    def step_5_style_settings(self):
        """步骤5：写作风格设定（优化版）"""
        self.print_section("第四部分：写作风格")

        # 风格选择
        style_choice = self.get_choice(
            "1. 选择整体风格：",
            self.style_options
        )

        style = self.style_options[style_choice]

        # 是否番茄风格
        is_fanqie = '番茄' in style['name']

        self.config['style'] = {
            'tone': style['tone'],
            'style_name': style['name'],
            'pace': style.get('pace', 'medium'),
            'is_fanqie_style': is_fanqie
        }

        # 生成参数
        self.config['generation'] = {
            'temperature': style['temperature'],
            'planner_temp': style['temperature'] - 0.05,
            'writer_temp': style['temperature'] + 0.2,
            'critic_temp': 0.3,
            'max_revision_iterations': 2
        }

    def step_6_uniqueness_settings(self):
        """步骤6：差异性设定（简化版）"""
        self.print_section("第五部分：创作差异性设定")

        print("💡 这些设置决定了每次生成的独特性\n")

        # 随机性强度
        print("1. 创作随机性：")
        print("  1. 低 - 更可控，严格按设定（适合严谨题材）")
        print("  2. 中 - 平衡随机性和可控性（推荐✨）")
        print("  3. 高 - 更有创意，可能出现意外惊喜")
        randomness_options = {'1': 'low', '2': 'medium', '3': 'high'}
        randomness_choice = self.get_choice("", randomness_options)
        randomness = randomness_options[randomness_choice]

        # 根据选择调整温度
        temp_adjustment = {'low': -0.1, 'medium': 0, 'high': 0.15}
        base_temp = self.config['generation']['temperature']
        self.config['generation']['temperature'] = min(0.95, base_temp + temp_adjustment[randomness])
        self.config['generation']['writer_temp'] = min(0.95, base_temp + temp_adjustment[randomness] + 0.2)

        # 伏笔生成策略
        print("\n2. 伏笔/剧情深度：")
        print("  1. 简单 - 直线剧情，爽快推进")
        print("  2. 适中 - 适当伏笔和支线（推荐✨）")
        print("  3. 复杂 - 多重伏笔、复杂悬念")
        foreshadow_options = {'1': 'conservative', '2': 'moderate', '3': 'aggressive'}
        foreshadow_choice = self.get_choice("", foreshadow_options)
        foreshadow = foreshadow_options[foreshadow_choice]

        # 角色自主性
        print("\n3. 角色自主性：")
        print("  1. 严格 - 角色按设定行动")
        print("  2. 适中 - 允许合理发展（推荐✨）")
        print("  3. 自由 - 角色可能做出意想不到的决定")
        autonomy_options = {'1': 'strict', '2': 'medium', '3': 'free'}
        autonomy_choice = self.get_choice("", autonomy_options)
        autonomy = autonomy_options[autonomy_choice]

        self.config['generation'].update({
            'randomness_level': randomness,
            'foreshadow_strategy': foreshadow,
            'character_autonomy': autonomy,
            'enable_plot_twists': True if randomness != 'low' else False,
            'seed': None  # 每次运行使用不同的随机种子
        })

    def step_7_review_and_save(self):
        """步骤7：预览和保存"""
        self.print_section("配置完成！让我们预览一下")

        print(f"\n📖 小说标题：{self.config['novel']['title']}")
        print(f"📝 类型：{self.config['novel']['type']}")
        print(f"📚 目标章节：{self.config['novel']['target_chapters']}")
        print(f"\n🌍 世界观：")
        print(f"   时代：{self.config['worldbuilding']['era']}")
        print(f"   场景：{self.config['worldbuilding']['setting']}")
        print(f"   力量体系：{self.config['worldbuilding']['power_system']}")
        print(f"\n👥 角色：")
        for char in self.config['characters']:
            print(f"   - {char['name']} ({char['age']}岁, {char['occupation']})")
            print(f"     特点：{', '.join(char['traits'][:5])}")
            print(f"     目标：{char['goal']}")
        print(f"\n🎨 风格：{self.config['style']['style_name']}")
        print(f"🎲 随机性：{self.config['generation']['randomness_level']}")
        print(f"📖 伏笔策略：{self.config['generation']['foreshadow_strategy']}")

        # 确认保存
        print("\n" + "─"*60)
        confirm = input("确认保存配置并创建项目？(y/n) [y]: ").strip().lower()
        if confirm == 'n':
            print("❌ 配置未保存")
            return False

        # 保存为默认配置（用于main.py读取）
        default_path = '/project/novel/bible/novel_config_latest.yaml'
        os.makedirs('/project/novel/bible', exist_ok=True)

        with open(default_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)

        print(f"\n✅ 配置已保存到：{default_path}")

        # 🔧 立即创建项目（不等main.py）
        from src.project_manager import ProjectManager
        pm = ProjectManager()

        try:
            project_id, project_info = pm.create_project(self.config)
            print(f"\n✅ 项目已创建：{project_info['title']}")
            print(f"   项目ID: {project_id}")
            print(f"   位置: projects/{project_id}/")
        except Exception as e:
            # 如果项目已存在，不报错
            if "已存在" in str(e):
                print(f"\n✅ 项目已存在：{self.config['novel']['title']}")
            else:
                print(f"\n⚠️  项目创建警告: {e}")

        print(f"\n💡 下一步：")
        print(f"   运行 python3 main.py 或 ./novel.sh generate 开始生成")

        return True

    def run(self):
        """运行完整的配置流程"""
        try:
            # 步骤1-7
            template = self.step_1_choose_template()
            self.step_2_basic_info(template)
            self.step_3_worldbuilding(template)
            self.step_4_characters()
            self.step_5_style_settings()
            self.step_6_uniqueness_settings()
            success = self.step_7_review_and_save()

            if success:
                self.print_header("🎉 配置完成！")
                print("\n📊 创作差异性说明：")
                print("   即使用相同配置，每次生成的故事也会不同，因为：")
                print(f"   • 随机性等级：{self.config['generation']['randomness_level']}")
                print(f"   • AI温度参数：{self.config['generation']['writer_temp']:.2f}")
                print(f"   • 每次使用不同的随机种子")
                print(f"   • AI会根据上下文做出不同决策")

                print("\n🎯 多项目管理：")
                print("   • 此配置会自动创建独立项目")
                print("   • 可随时使用 ./novel.sh projects 切换项目")
                print("   • 每个项目的进度独立保存")

        except KeyboardInterrupt:
            print("\n\n⚠️  配置已取消")
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    configurator = NovelConfigurator()
    configurator.run()
