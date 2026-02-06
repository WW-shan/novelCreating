#!/usr/bin/env python3
"""
测试大纲自动保存功能修复
"""

import os
import yaml
from src.main import config_to_initial_state


def test_yaml_import_fix():
    """测试 yaml 模块导入不再冲突"""
    print("\n" + "="*60)
    print("测试 1: yaml 模块导入修复")
    print("="*60)

    # 创建最小配置
    config = {
        'novel': {
            'title': 'test_novel',
            'synopsis': '测试故事简介',
            'target_chapters': 100,
            'type': '推理',
            'style': 'fanqie'
        },
        'worldbuilding': {},
        'characters': [],
        'generation': {
            'foreshadow_strategy': 'moderate'
        }
    }

    # 创建临时 paths
    paths = {
        'bible_dir': '/project/novel/projects/test_novel/bible',
        'config_file': '/project/novel/projects/test_novel/config.yaml',
        'db_file': '/project/novel/projects/test_novel/state.db',
        'manuscript_dir': '/project/novel/projects/test_novel/manuscript'
    }

    # 确保目录存在
    os.makedirs(paths['bible_dir'], exist_ok=True)

    try:
        # 调用 config_to_initial_state，应该不再抛出 yaml 错误
        initial_state = config_to_initial_state(config, paths)

        print("✅ 成功调用 config_to_initial_state()")
        print(f"   状态键: {list(initial_state.keys())[:5]}...")

        # 检查是否生成了 outline.yaml
        outline_file = os.path.join(paths['bible_dir'], 'outline.yaml')
        if os.path.exists(outline_file):
            print(f"✅ 成功生成 outline.yaml")

            # 验证文件内容
            with open(outline_file, 'r', encoding='utf-8') as f:
                outline_data = yaml.safe_load(f)

            if 'outline' in outline_data and 'volumes' in outline_data:
                print(f"   大纲主目标: {outline_data['outline'].get('main_goal', '')[:50]}...")
                print(f"   卷数: {len(outline_data['volumes'])}")
                return True
            else:
                print(f"❌ outline.yaml 格式不正确")
                return False
        else:
            print(f"⚠️  未生成 outline.yaml（可能使用了现有大纲）")
            return True

    except Exception as e:
        print(f"❌ 调用失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理测试文件
        outline_file = os.path.join(paths['bible_dir'], 'outline.yaml')
        if os.path.exists(outline_file):
            os.remove(outline_file)


if __name__ == "__main__":
    print("="*60)
    print("🧪 大纲自动保存修复测试")
    print("="*60)

    result = test_yaml_import_fix()

    print("\n" + "="*60)
    print("📊 测试结果")
    print("="*60)

    if result:
        print("✅ 测试通过！yaml 导入冲突已修复")
    else:
        print("❌ 测试失败")
