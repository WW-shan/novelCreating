#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Novel Configuration Tool
交互式小说配置工具
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
                'version': '1.0'
            },
            'novel': {},
            'characters': [],
            'worldbuilding': {},
            'style': {},
            'generation': {}
        }

        # 预设模板
        self.templates = {
            '1': {
                'name': '赛博朋克',
                'novel_type': 'cyberpunk',
                'era': '2087年',
                'setting': '霓虹闪烁的超大都市',
                'power_system': '神经接口技术',
                'example_synopsis': '一个黑客发现了公司试图控制人类意识的阴谋'
            },
            '2': {
                'name': '玄幻修仙',
                'novel_type': 'xuanhuan',
                'era': '架空古代',
                'setting': '九州大陆',
                'power_system': '灵力修炼体系',
                'example_synopsis': '一个废柴少年获得神秘传承，踏上逆天修炼之路'
            },
            '3': {
                'name': '都市爱情',
                'novel_type': 'romance',
                'era': '现代都市',
                'setting': '繁华的现代大都市',
                'power_system': '无',
                'example_synopsis': '一次意外的相遇，让两个陌生人的命运交织在一起'
            },
            '4': {
                'name': '悬疑推理',
                'novel_type': 'mystery',
                'era': '现代',
                'setting': '都市与郊区',
                'power_system': '无',
                'example_synopsis': '一个侦探接到神秘委托，调查连环失踪案背后的真相'
            },
            '5': {
                'name': '武侠江湖',
                'novel_type': 'wuxia',
                'era': '明朝',
                'setting': '江湖武林',
                'power_system': '内功心法与武功招式',
                'example_synopsis': '一个少年目睹师门被灭，带着秘籍流落江湖寻仇'
            }
        }

        # 性格特质词库
        self.trait_library = {
            '正面': ['勇敢', '聪明', '善良', '正直', '忠诚', '坚韧', '幽默', '温柔', '果断', '睿智'],
            '中性': ['冷静', '理性', '神秘', '孤独', '内向', '叛逆', '固执', '谨慎'],
            '负面': ['傲慢', '冲动', '贪婪', '懦弱', '多疑', '残忍', '自私']
        }

        # 写作风格选项
        self.style_options = {
            '1': {'name': '严肃正剧', 'temperature': 0.6, 'tone': 'serious'},
            '2': {'name': '轻松幽默', 'temperature': 0.8, 'tone': 'humorous'},
            '3': {'name': '黑暗压抑', 'temperature': 0.7, 'tone': 'dark'},
            '4': {'name': '热血激昂', 'temperature': 0.9, 'tone': 'passionate'},
            '5': {'name': '浪漫温馨', 'temperature': 0.7, 'tone': 'romantic'}
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

    def get_choice(self, prompt, options, show_descriptions=True):
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
        print("\n首先，让我们选择一个小说类型作为起点...")
        print("（你可以在后续步骤中完全自定义所有设定）")

        template_choice = self.get_choice(
            "\n请选择小说类型模板：",
            self.templates
        )

        template = self.templates[template_choice]
        print(f"\n✅ 已选择：{template['name']}")
        print(f"   示例梗概：{template['example_synopsis']}")

        return template

    def step_2_basic_info(self, template):
        """步骤2：基础信息"""
        self.print_section("第一部分：基础设定")

        # 小说标题
        title = self.get_input("1. 给你的小说起个标题")

        # 故事梗概
        print(f"\n2. 用1-3句话描述你的故事")
        print(f"   示例：{template['example_synopsis']}")
        synopsis = self.get_input("   你的故事")

        # 目标章节数
        def validate_chapters(x):
            try:
                num = int(x)
                if num < 1 or num > 100:
                    print("❌ 请输入1-100之间的数字")
                    return False
                return True
            except:
                print("❌ 请输入有效的数字")
                return False

        chapters = int(self.get_input("3. 计划写多少章", default="20", validate=validate_chapters))

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
        print(f"1. 时代背景 [参考: {template['era']}]")
        era = self.get_input("   你的设定", default=template['era'])

        # 主要场景
        print(f"\n2. 故事发生的地点 [参考: {template['setting']}]")
        setting = self.get_input("   你的设定", default=template['setting'])

        # 力量体系/特殊设定
        print(f"\n3. 特殊设定（力量体系/科技水平/魔法规则等）")
        print(f"   [参考: {template['power_system']}]")
        power_system = self.get_input("   你的设定", default=template['power_system'])

        # 可选：派系/组织
        print("\n4. 主要派系/组织（可选，按回车跳过）")
        print("   示例：正派-武当派；邪派-血魔教；中立-商人联盟")
        factions_input = input("   输入派系（用分号;分隔）: ").strip()
        factions = [f.strip() for f in factions_input.split(';') if f.strip()]

        self.config['worldbuilding'] = {
            'era': era,
            'setting': setting,
            'power_system': power_system,
            'factions': factions,
            'technology': [],
            'magic_system': {},
            'geography': {}
        }

    def step_4_characters(self):
        """步骤4：角色设定"""
        self.print_section("第三部分：角色设定")

        print("一个好故事至少需要2-3个主要角色")
        print("让我们逐个创建角色...\n")

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

            # 性格特点
            print("\n4. 性格特点（从下面选择3-5个，或自己输入）")
            print(f"   正面特质：{', '.join(self.trait_library['正面'][:10])}")
            print(f"   中性特质：{', '.join(self.trait_library['中性'][:8])}")
            print(f"   负面特质：{', '.join(self.trait_library['负面'][:7])}")
            traits_input = self.get_input("   输入特点（用逗号,分隔）")
            traits = [t.strip() for t in traits_input.split(',') if t.strip()]

            # 目标/动机
            goal = self.get_input("5. 这个角色的核心目标是什么", default="生存下去")

            # 初始位置
            location = self.get_input("6. 角色初始位置", default=self.config['worldbuilding']['setting'])

            character = {
                'name': name,
                'age': age,
                'occupation': occupation,
                'traits': traits,
                'goal': goal,
                'location': location,
                'status': 'Alive',
                'relationships': {}
            }

            self.config['characters'].append(character)

            print(f"\n✅ 角色 '{name}' 创建完成！")

            # 询问是否继续添加
            if char_count >= 2:
                continue_add = input("\n是否添加更多角色？(y/n) [n]: ").strip().lower()
                if continue_add != 'y':
                    break

            char_count += 1

    def step_5_style_settings(self):
        """步骤5：写作风格设定"""
        self.print_section("第四部分：写作风格")

        # 风格选择
        style_choice = self.get_choice(
            "1. 选择整体风格：",
            self.style_options
        )

        style = self.style_options[style_choice]

        # 叙事节奏
        print("\n2. 叙事节奏：")
        print("  1. 快节奏 - 情节紧凑，冲突密集")
        print("  2. 适中 - 张弛有度")
        print("  3. 慢热型 - 注重细节描写和氛围营造")
        pace_options = {'1': '快节奏', '2': '适中', '3': '慢热型'}
        pace_choice = self.get_choice("", pace_options)
        pace = pace_options[pace_choice]

        # 重点元素
        print("\n3. 你希望重点强调哪些元素？（多选，用逗号分隔）")
        print("  1-动作场面  2-对话  3-心理描写  4-环境描写  5-悬念")
        focus_input = input("输入数字（例如：1,2,5）: ").strip()
        focus_map = {
            '1': 'action', '2': 'dialogue', '3': 'psychology',
            '4': 'environment', '5': 'suspense'
        }
        focus_elements = [focus_map[x.strip()] for x in focus_input.split(',') if x.strip() in focus_map]

        self.config['style'] = {
            'tone': style['tone'],
            'style_name': style['name'],
            'pace': pace,
            'focus_elements': focus_elements
        }

        # 生成参数（影响随机性）
        self.config['generation'] = {
            'temperature': style['temperature'],
            'planner_temp': style['temperature'] - 0.1,
            'writer_temp': style['temperature'] + 0.2,
            'critic_temp': 0.3
        }

    def step_6_uniqueness_settings(self):
        """步骤6：差异性设定（让每次生成不同）"""
        self.print_section("第五部分：创作差异性设定")

        print("为了让每次生成的小说都独一无二，我们提供以下选项：\n")

        # 随机性强度
        print("1. 创作随机性强度：")
        print("  1. 低 - 更可控，更接近你的设定（适合严谨题材）")
        print("  2. 中 - 平衡随机性和可控性（推荐）")
        print("  3. 高 - 更有创意，可能出现意外惊喜（适合脑洞题材）")
        randomness_options = {'1': 'low', '2': 'medium', '3': 'high'}
        randomness_choice = self.get_choice("", randomness_options)
        randomness = randomness_options[randomness_choice]

        # 根据选择调整温度
        temp_adjustment = {'low': -0.1, 'medium': 0, 'high': 0.2}
        base_temp = self.config['generation']['temperature']
        self.config['generation']['temperature'] = base_temp + temp_adjustment[randomness]
        self.config['generation']['writer_temp'] = base_temp + temp_adjustment[randomness] + 0.2

        # 伏笔生成策略
        print("\n2. 伏笔生成策略：")
        print("  1. 保守 - 只使用你预设的伏笔")
        print("  2. 适中 - AI会适当添加新伏笔（推荐）")
        print("  3. 激进 - AI自由创造大量伏笔和支线")
        foreshadow_options = {'1': 'conservative', '2': 'moderate', '3': 'aggressive'}
        foreshadow_choice = self.get_choice("", foreshadow_options)
        foreshadow = foreshadow_options[foreshadow_choice]

        # 角色自主性
        print("\n3. 角色行为自主性：")
        print("  1. 严格 - 角色严格按照你的设定行动")
        print("  2. 适中 - 允许角色在合理范围内自主发展（推荐）")
        print("  3. 自由 - 角色可能做出意想不到的决定")
        autonomy_options = {'1': 'strict', '2': 'moderate', '3': 'free'}
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
        print(f"\n👥 角色：")
        for char in self.config['characters']:
            print(f"   - {char['name']} ({char['age']}岁, {char['occupation']})")
            print(f"     特点：{', '.join(char['traits'])}")
        print(f"\n🎨 风格：{self.config['style']['style_name']}")
        print(f"🎲 随机性：{self.config['generation']['randomness_level']}")

        # 确认保存
        print("\n" + "─"*60)
        confirm = input("确认保存配置？(y/n) [y]: ").strip().lower()
        if confirm == 'n':
            print("❌ 配置未保存")
            return False

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c for c in self.config['novel']['title'] if c.isalnum() or c in (' ', '-', '_'))
        filename = f"novel_config_{safe_title}_{timestamp}.yaml"
        filepath = os.path.join('/project/novel/bible', filename)

        # 保存YAML
        os.makedirs('/project/novel/bible', exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)

        # 同时保存JSON格式（便于程序读取）
        json_filepath = filepath.replace('.yaml', '.json')
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 配置已保存到：")
        print(f"   YAML格式: {filepath}")
        print(f"   JSON格式: {json_filepath}")

        # 保存为默认配置
        default_path = '/project/novel/bible/novel_config_latest.yaml'
        with open(default_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)

        print(f"\n💡 提示：配置已设为默认，下次运行生成器将自动使用此配置")

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
                print("\n下一步：")
                print("  运行 ./run_novel.sh 开始生成小说")
                print("  或者编辑配置文件进行微调")
                print("\n💡 为什么每次生成都不同？")
                print(f"  1. 随机性等级：{self.config['generation']['randomness_level']}")
                print(f"  2. AI温度参数：{self.config['generation']['writer_temp']:.1f}")
                print(f"  3. 伏笔策略：{self.config['generation']['foreshadow_strategy']}")
                print(f"  4. 每次运行使用不同的随机种子")
                print("\n  即使用相同配置，AI也会产生不同的情节发展！")

        except KeyboardInterrupt:
            print("\n\n⚠️  配置已取消")
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    configurator = NovelConfigurator()
    configurator.run()
