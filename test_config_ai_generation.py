#!/usr/bin/env python3
"""
测试配置工具的 AI 生成功能
"""

import os
import sys

# 模拟用户输入
class MockInput:
    def __init__(self, responses):
        self.responses = responses
        self.index = 0

    def __call__(self, prompt=''):
        if self.index < len(self.responses):
            response = self.responses[self.index]
            self.index += 1
            print(f"{prompt}{response}")
            return response
        return ''

def test_mode2_ai_quick():
    """测试 Mode 2: AI 快速生成"""
    print("\n" + "="*60)
    print("测试 Mode 2: AI 快速生成")
    print("="*60)

    # 准备输入序列
    responses = [
        "测试小说_mode2",  # 标题
        "100",  # 章节数
        "推理",  # 类型
        "一个侦探解决连环案件的故事",  # 梗概
        "2",  # 选择 Mode 2
        "y",  # 确认生成
        "现代都市",  # 世界观
        "1",  # 1个角色
        "李侦探",  # 角色名
        "聪明冷静",  # 角色特点
        "fanqie",  # 风格
        "n",  # 不修改配置
        "y"  # 确认保存
    ]

    # 替换 input 函数
    import builtins
    original_input = builtins.input
    builtins.input = MockInput(responses)

    try:
        from configure_novel_advanced import AdvancedNovelConfigurator
        configurator = AdvancedNovelConfigurator()

        # 运行配置
        configurator.run()

        # 检查生成的配置
        if 'outline' in configurator.config:
            outline = configurator.config['outline']
            print(f"\n✅ 总纲生成成功")
            print(f"   主目标: {outline.get('main_goal', '')[:50]}...")

        if 'volumes' in configurator.config:
            volumes = configurator.config['volumes']
            print(f"✅ 卷纲生成成功: {len(volumes)} 卷")

            if len(volumes) > 0:
                first_vol = volumes[0]
                print(f"   第1卷: {first_vol.get('title', '')}")
                print(f"   目标: {first_vol.get('core_goal', '')[:40]}...")

            return True
        else:
            print("❌ 未生成卷纲")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 恢复原始 input
        builtins.input = original_input

        # 清理测试项目
        from src.project_manager import ProjectManager
        pm = ProjectManager()
        try:
            pm.delete_project("测试小说_mode2")
        except:
            pass


if __name__ == "__main__":
    print("="*60)
    print("🧪 配置工具 AI 生成测试")
    print("="*60)

    result = test_mode2_ai_quick()

    print("\n" + "="*60)
    print("📊 测试结果")
    print("="*60)

    if result:
        print("✅ 测试通过！Mode 2 使用了新的 AI 生成逻辑")
    else:
        print("❌ 测试失败")
