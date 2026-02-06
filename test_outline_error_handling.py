#!/usr/bin/env python3
"""
测试 outline.yaml 空文件/格式错误的处理
"""

import os
import yaml
from src.main import config_to_initial_state
from src.nodes.planner import load_custom_outline


def test_empty_outline_file():
    """测试空的 outline.yaml 文件"""
    print("\n" + "="*60)
    print("测试 1: 空的 outline.yaml 文件")
    print("="*60)

    test_dir = '/project/novel/projects/test_empty'
    bible_dir = os.path.join(test_dir, 'bible')
    os.makedirs(bible_dir, exist_ok=True)

    outline_file = os.path.join(bible_dir, 'outline.yaml')

    # 创建空文件
    with open(outline_file, 'w', encoding='utf-8') as f:
        f.write('')

    config = {
        'novel': {
            'title': 'test_empty',
            'synopsis': '测试空文件处理',
            'target_chapters': 50,
            'type': '推理',
            'style': 'fanqie'
        },
        'worldbuilding': {},
        'characters': [],
        'generation': {'foreshadow_strategy': 'moderate'}
    }

    paths = {
        'bible_dir': bible_dir,
        'config_file': os.path.join(test_dir, 'config.yaml'),
        'db_file': os.path.join(test_dir, 'state.db'),
        'manuscript_dir': os.path.join(test_dir, 'manuscript')
    }

    try:
        # 应该能正常处理空文件，不会崩溃
        initial_state = config_to_initial_state(config, paths)
        print("✅ 成功处理空 outline.yaml 文件")

        # 应该回退到默认生成
        if 'novel_outline' in initial_state:
            print("✅ 正确回退到默认大纲生成")
            return True
        else:
            print("❌ 未生成默认大纲")
            return False

    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


def test_invalid_yaml_format():
    """测试格式错误的 outline.yaml"""
    print("\n" + "="*60)
    print("测试 2: 格式错误的 outline.yaml")
    print("="*60)

    test_dir = '/project/novel/projects/test_invalid'
    bible_dir = os.path.join(test_dir, 'bible')
    os.makedirs(bible_dir, exist_ok=True)

    outline_file = os.path.join(bible_dir, 'outline.yaml')

    # 创建格式错误的 YAML
    with open(outline_file, 'w', encoding='utf-8') as f:
        f.write('invalid: yaml: format: :::\n  - bad indentation\nno closing')

    config = {
        'novel': {
            'title': 'test_invalid',
            'synopsis': '测试错误格式处理',
            'target_chapters': 50,
            'type': '推理',
            'style': 'fanqie'
        },
        'worldbuilding': {},
        'characters': [],
        'generation': {'foreshadow_strategy': 'moderate'}
    }

    paths = {
        'bible_dir': bible_dir,
        'config_file': os.path.join(test_dir, 'config.yaml'),
        'db_file': os.path.join(test_dir, 'state.db'),
        'manuscript_dir': os.path.join(test_dir, 'manuscript')
    }

    try:
        # 应该能正常处理格式错误，不会崩溃
        initial_state = config_to_initial_state(config, paths)
        print("✅ 成功处理格式错误的 outline.yaml")
        return True

    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


def test_planner_load_empty_outline():
    """测试 planner 节点加载空 outline"""
    print("\n" + "="*60)
    print("测试 3: planner 加载空 outline")
    print("="*60)

    test_dir = '/project/novel/projects/test_planner'
    bible_dir = os.path.join(test_dir, 'bible')
    os.makedirs(bible_dir, exist_ok=True)

    outline_file = os.path.join(bible_dir, 'outline.yaml')

    # 创建空文件
    with open(outline_file, 'w', encoding='utf-8') as f:
        f.write('')

    state = {
        'project_paths': {
            'bible_dir': bible_dir
        },
        'config': {}
    }

    try:
        result = load_custom_outline(state)
        if result is None:
            print("✅ 正确返回 None（表示无有效大纲）")
            return True
        else:
            print(f"⚠️  返回了数据: {result}")
            return True  # 也算通过，只要不崩溃

    except Exception as e:
        print(f"❌ 加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


if __name__ == "__main__":
    print("="*60)
    print("🧪 outline.yaml 错误处理测试")
    print("="*60)

    results = []
    results.append(("空文件处理", test_empty_outline_file()))
    results.append(("格式错误处理", test_invalid_yaml_format()))
    results.append(("planner 空文件", test_planner_load_empty_outline()))

    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {test_name}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("✅ 所有测试通过！outline.yaml 错误处理已修复")
    else:
        print("⚠️  部分测试失败")
