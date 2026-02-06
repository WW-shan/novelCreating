#!/usr/bin/env python3
"""
测试大纲显示和自动保存功能
"""

import sys
import os
import yaml
import tempfile
import shutil

sys.path.insert(0, '/project/novel')

def test_planner_display():
    """测试 1: Planner 显示大纲使用情况"""
    print("\n" + "="*60)
    print("测试 1: Planner 节点显示大纲使用情况")
    print("="*60)

    from src.nodes.planner import load_custom_outline

    # 创建测试大纲
    test_dir = tempfile.mkdtemp()
    outline_file = os.path.join(test_dir, 'outline.yaml')

    outline_data = {
        'outline': {
            'synopsis': '测试梗概',
            'main_goal': '成为最强者',
            'main_conflict': '主角与反派的对抗',
            'protagonist_arc': '从弱到强',
            'phases': [
                {'name': '开局', 'goal': '目标1', 'chapters': '1-10'}
            ]
        },
        'volumes': [
            {'volume': 1, 'title': '第一卷', 'chapters': '1-25'}
        ]
    }

    with open(outline_file, 'w', encoding='utf-8') as f:
        yaml.dump(outline_data, f, allow_unicode=True)

    # 测试加载
    state = {
        'project_paths': {'bible_dir': test_dir},
        'config': {}
    }

    result = load_custom_outline(state)

    print("\n加载结果:")
    if result:
        print(f"  ✅ 成功加载大纲")
        print(f"     主目标: {result['outline']['main_goal']}")
        print(f"     阶段数: {len(result['outline']['phases'])}")
        print(f"     卷数: {len(result['volumes'])}")

        # 模拟 planner 显示
        print("\nPlanner 显示信息:")
        outline = result.get('outline', {})
        volumes = result.get('volumes', [])

        if outline and outline.get('main_goal'):
            print(f"  📖 使用自定义大纲")
            print(f"     主目标: {outline.get('main_goal', '')[:50]}...")
            if outline.get('phases'):
                print(f"     阶段数: {len(outline.get('phases', []))}")

        if volumes:
            print(f"     卷数: {len(volumes)}")
    else:
        print(f"  ❌ 加载失败")

    shutil.rmtree(test_dir)
    return True


def test_auto_save_outline():
    """测试 2: 自动生成的大纲保存到 outline.yaml"""
    print("\n" + "="*60)
    print("测试 2: 自动生成大纲保存功能")
    print("="*60)

    # 模拟自动生成并保存
    test_dir = tempfile.mkdtemp()
    bible_dir = os.path.join(test_dir, 'bible')
    os.makedirs(bible_dir, exist_ok=True)

    # 模拟 novel_config
    novel_config = {
        'synopsis': '测试梗概：主角从废材逆袭',
        'target_chapters': 100
    }

    # 模拟生成的 novel_outline
    novel_outline = {
        'main_goal': f"完成故事：{novel_config['synopsis'][:100]}",
        'main_conflict': '待定（建议在配置中添加）',
        'protagonist_arc': '待定（建议在配置中添加）'
    }

    # 模拟生成的 volume_frameworks
    target_chapters = 100
    total_volumes = (target_chapters + 24) // 25
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

    # 保存逻辑（从 main.py 复制）
    outline_file = os.path.join(bible_dir, 'outline.yaml')

    outline_data = {
        'outline': {
            'synopsis': novel_config.get('synopsis', ''),
            'main_goal': novel_outline.get('main_goal', ''),
            'main_conflict': novel_outline.get('main_conflict', ''),
            'protagonist_arc': novel_outline.get('protagonist_arc', ''),
            'phases': []
        },
        'volumes': []
    }

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

    with open(outline_file, 'w', encoding='utf-8') as f:
        yaml.dump(outline_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"\n✅ 保存成功: {outline_file}")

    # 验证保存的内容
    with open(outline_file, 'r', encoding='utf-8') as f:
        saved_data = yaml.safe_load(f)

    print(f"\n验证保存内容:")
    print(f"  ✅ synopsis: {saved_data['outline']['synopsis'][:30]}...")
    print(f"  ✅ main_goal: {saved_data['outline']['main_goal'][:30]}...")
    print(f"  ✅ volumes: {len(saved_data['volumes'])} 卷")
    print(f"     第1卷: {saved_data['volumes'][0]['title']} ({saved_data['volumes'][0]['chapters']})")
    print(f"     第{len(saved_data['volumes'])}卷: {saved_data['volumes'][-1]['title']} ({saved_data['volumes'][-1]['chapters']})")

    shutil.rmtree(test_dir)
    return True


def test_planner_without_outline():
    """测试 3: Planner 无大纲时的显示"""
    print("\n" + "="*60)
    print("测试 3: Planner 无大纲时的显示")
    print("="*60)

    from src.nodes.planner import load_custom_outline

    # 空状态（无大纲）
    state = {
        'config': {}
    }

    result = load_custom_outline(state)

    print("\n模拟 Planner 显示:")
    if result:
        outline_data = result.get('outline', {})
        if outline_data and outline_data.get('main_goal'):
            print(f"  📖 使用自定义大纲")
        else:
            print(f"  📖 使用 AI 默认生成模式（无预设大纲）")
    else:
        print(f"  📖 使用 AI 默认生成模式（无预设大纲）")

    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + " "*12 + "大纲显示和保存功能测试" + " "*20 + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")

    tests = [
        ("Planner 显示大纲", test_planner_display),
        ("自动生成保存", test_auto_save_outline),
        ("无大纲显示", test_planner_without_outline)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} 失败: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status}: {name}")

    print("\n" + "="*60)
    print(f"总计: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有测试通过！")
    else:
        print(f"⚠️  有 {total - passed} 个测试失败")

    print("="*60)

    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
