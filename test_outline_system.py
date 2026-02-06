#!/usr/bin/env python3
"""
大纲系统完整性测试
测试新旧两种格式的大纲加载和使用
"""

import sys
import os
import yaml
import tempfile
import shutil

sys.path.insert(0, '/project/novel')

def test_planner_load_new_format():
    """测试 Planner 加载新格式大纲"""
    print("\n" + "="*60)
    print("测试 1: Planner 加载新格式（outline.yaml）")
    print("="*60)

    from src.nodes.planner import load_custom_outline

    # 创建测试数据
    test_dir = tempfile.mkdtemp()
    outline_file = os.path.join(test_dir, 'outline.yaml')

    test_data = {
        'outline': {
            'synopsis': '测试梗概',
            'main_goal': '主目标',
            'main_conflict': '主冲突',
            'protagonist_arc': '成长弧',
            'phases': [
                {'name': '阶段1', 'goal': '目标1', 'chapters': '1-20'}
            ]
        },
        'volumes': [
            {
                'volume': 1,
                'title': '第一卷',
                'chapters': '1-25',
                'core_goal': '卷目标',
                'key_events': ['事件1'],
                'foreshadowing': ['伏笔1'],
                'ending_state': '结尾'
            }
        ]
    }

    with open(outline_file, 'w', encoding='utf-8') as f:
        yaml.dump(test_data, f, allow_unicode=True)

    state = {
        'project_paths': {
            'bible_dir': test_dir
        }
    }

    result = load_custom_outline(state)

    # 验证
    assert result is not None, "❌ 加载失败"
    assert 'outline' in result, "❌ 缺少 outline"
    assert 'volumes' in result, "❌ 缺少 volumes"
    assert result['outline']['main_goal'] == '主目标', "❌ outline 数据错误"
    assert len(result['volumes']) == 1, "❌ volumes 数量错误"

    # 清理
    shutil.rmtree(test_dir)

    print("✅ 新格式加载成功")
    print(f"   - outline 字段: {list(result['outline'].keys())}")
    print(f"   - volumes 数量: {len(result['volumes'])}")


def test_planner_load_old_format():
    """测试 Planner 加载旧格式大纲"""
    print("\n" + "="*60)
    print("测试 2: Planner 加载旧格式（config 字段）")
    print("="*60)

    from src.nodes.planner import load_custom_outline

    state = {
        'config': {
            'novel_outline': {
                'main_goal': '旧格式目标',
                'main_conflict': '旧格式冲突',
                'protagonist_arc': '旧格式成长'
            },
            'volume_frameworks': [
                {
                    'title': '第一卷',
                    'chapters': '1-25',
                    'core_goal': '卷目标'
                }
            ]
        }
    }

    result = load_custom_outline(state)

    # 验证
    assert result is not None, "❌ 加载失败"
    assert 'outline' in result, "❌ 缺少 outline"
    assert 'volumes' in result, "❌ 缺少 volumes"
    assert result['outline']['main_goal'] == '旧格式目标', "❌ outline 数据错误"
    assert len(result['volumes']) == 1, "❌ volumes 数量错误"

    print("✅ 旧格式加载成功")
    print(f"   - outline['main_goal']: {result['outline']['main_goal']}")
    print(f"   - volumes[0]['title']: {result['volumes'][0]['title']}")


def test_find_current_phase():
    """测试查找当前阶段"""
    print("\n" + "="*60)
    print("测试 3: 查找当前阶段")
    print("="*60)

    from src.nodes.planner import find_current_phase

    outline = {
        'phases': [
            {'name': '开局', 'goal': '建立世界观', 'chapters': '1-20'},
            {'name': '发展', 'goal': '推进主线', 'chapters': '21-60'},
            {'name': '高潮', 'goal': '解决冲突', 'chapters': '61-100'}
        ]
    }

    # 测试不同章节
    test_cases = [
        (5, '开局'),
        (25, '发展'),
        (65, '高潮'),
        (150, None)  # 超出范围
    ]

    for chapter, expected_name in test_cases:
        phase = find_current_phase(outline, chapter)
        if expected_name is None:
            assert phase is None, f"❌ 第{chapter}章应该没有阶段"
            print(f"   第{chapter}章: 无阶段 ✅")
        else:
            assert phase is not None, f"❌ 第{chapter}章应该有阶段"
            assert phase['name'] == expected_name, f"❌ 第{chapter}章阶段错误"
            print(f"   第{chapter}章: {phase['name']} ✅")


def test_find_current_volume():
    """测试查找当前卷"""
    print("\n" + "="*60)
    print("测试 4: 查找当前卷")
    print("="*60)

    from src.nodes.planner import find_current_volume

    volumes = [
        {'volume': 1, 'title': '第一卷', 'chapters': '1-25'},
        {'volume': 2, 'title': '第二卷', 'chapters': '26-50'},
        {'volume': 3, 'title': '第三卷', 'chapters': '51-75'}
    ]

    # 测试不同章节
    test_cases = [
        (10, '第一卷'),
        (30, '第二卷'),
        (55, '第三卷'),
        (100, None)  # 超出范围
    ]

    for chapter, expected_title in test_cases:
        volume = find_current_volume(volumes, chapter)
        if expected_title is None:
            assert volume is None, f"❌ 第{chapter}章应该没有卷"
            print(f"   第{chapter}章: 无卷 ✅")
        else:
            assert volume is not None, f"❌ 第{chapter}章应该有卷"
            assert volume['title'] == expected_title, f"❌ 第{chapter}章卷错误"
            print(f"   第{chapter}章: {volume['title']} ✅")


def test_outline_guidance_generation():
    """测试大纲指引生成"""
    print("\n" + "="*60)
    print("测试 5: 大纲指引生成")
    print("="*60)

    from src.nodes.planner import find_current_phase, find_current_volume

    outline_data = {
        'synopsis': '测试梗概',
        'main_goal': '主目标',
        'main_conflict': '主冲突',
        'protagonist_arc': '成长弧',
        'phases': [
            {'name': '开局', 'goal': '建立世界观', 'chapters': '1-20'}
        ]
    }

    volumes_data = [
        {
            'volume': 1,
            'title': '第一卷',
            'chapters': '1-25',
            'core_goal': '卷目标',
            'key_events': ['事件1', '事件2']
        }
    ]

    chapter_index = 15

    # 模拟 planner 的逻辑
    current_phase = find_current_phase(outline_data, chapter_index)
    current_volume = find_current_volume(volumes_data, chapter_index)

    outline_guidance = ""

    if current_phase:
        outline_guidance += f"\n【当前阶段】第{chapter_index}章位于：{current_phase.get('name')}\n"
        outline_guidance += f"阶段目标: {current_phase.get('goal')}\n"

    if current_volume:
        outline_guidance += f"\n【当前卷】第{current_volume.get('volume')}卷：{current_volume.get('title')}\n"
        outline_guidance += f"卷核心目标: {current_volume.get('core_goal')}\n"
        if current_volume.get('key_events'):
            outline_guidance += f"关键事件: {', '.join(current_volume.get('key_events', []))}\n"

    if outline_data:
        outline_guidance += f"\n【总纲】\n"
        outline_guidance += f"主目标: {outline_data.get('main_goal', '（未设定）')}\n"
        outline_guidance += f"主线冲突: {outline_data.get('main_conflict', '（未设定）')}\n"

    print("✅ 大纲指引生成成功")
    print(outline_guidance)

    # 验证
    assert '【当前阶段】' in outline_guidance, "❌ 缺少阶段信息"
    assert '【当前卷】' in outline_guidance, "❌ 缺少卷信息"
    assert '【总纲】' in outline_guidance, "❌ 缺少总纲信息"
    assert '主目标' in outline_guidance, "❌ 缺少主目标"


def test_priority_order():
    """测试加载优先级：新格式 > 旧格式"""
    print("\n" + "="*60)
    print("测试 6: 加载优先级（新格式优先）")
    print("="*60)

    from src.nodes.planner import load_custom_outline

    # 创建测试数据
    test_dir = tempfile.mkdtemp()
    outline_file = os.path.join(test_dir, 'outline.yaml')

    # 新格式数据
    new_format_data = {
        'outline': {
            'main_goal': '新格式目标'
        },
        'volumes': []
    }

    with open(outline_file, 'w', encoding='utf-8') as f:
        yaml.dump(new_format_data, f, allow_unicode=True)

    # 同时提供新旧两种格式
    state = {
        'project_paths': {
            'bible_dir': test_dir
        },
        'config': {
            'novel_outline': {
                'main_goal': '旧格式目标'
            },
            'volume_frameworks': []
        }
    }

    result = load_custom_outline(state)

    # 验证：应该使用新格式
    assert result['outline']['main_goal'] == '新格式目标', "❌ 应该优先使用新格式"

    # 清理
    shutil.rmtree(test_dir)

    print("✅ 优先级测试通过")
    print(f"   - 实际加载: 新格式 ✅")
    print(f"   - main_goal: {result['outline']['main_goal']}")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + " "*15 + "大纲系统完整性测试" + " "*21 + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")

    tests = [
        test_planner_load_new_format,
        test_planner_load_old_format,
        test_find_current_phase,
        test_find_current_volume,
        test_outline_guidance_generation,
        test_priority_order
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ 测试失败: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ 测试出错: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    print(f"✅ 通过: {passed}")
    if failed > 0:
        print(f"❌ 失败: {failed}")
    else:
        print("🎉 所有测试通过！")
    print("="*60)

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
