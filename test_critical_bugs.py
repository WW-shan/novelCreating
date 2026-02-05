#!/usr/bin/env python3
"""
测试关键bug修复 - 2026-02-04

测试项:
1. Deep copy 是否正确工作
2. plot_threads 结构是否一致
3. plot_tracks typo 是否修复
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_deep_copy_fix():
    """测试 Bug #1: Deep copy fix"""
    print("=" * 60)
    print("测试 #1: Deep Copy Fix")
    print("=" * 60)

    from src.nodes.memory import update_bible_with_parsed_data

    world_bible = {
        "characters": {
            "角色A": {"name": "角色A", "notes": [], "recent_notes": []}
        },
        "plot_threads": []
    }

    parsed_data = {
        "character_updates": {
            "角色A": "新状态更新"
        }
    }

    # 调用更新函数
    updated_bible = update_bible_with_parsed_data(world_bible, parsed_data, 1)

    # 验证原始 world_bible 未被修改
    original_notes = world_bible["characters"]["角色A"]["recent_notes"]
    updated_notes = updated_bible["characters"]["角色A"]["recent_notes"]

    print(f"原始 world_bible 的 notes: {original_notes}")
    print(f"更新后 updated_bible 的 notes: {updated_notes}")
    print(f"是同一对象吗? {original_notes is updated_notes}")

    if original_notes is updated_notes:
        print("❌ FAILED: 仍在使用浅拷贝（状态会被污染）")
        return False
    elif len(original_notes) == 0 and len(updated_notes) == 1:
        print("✅ PASSED: 深拷贝工作正常，原始状态未被污染")
        return True
    else:
        print(f"❌ FAILED: 预期结果不符 (原始: {len(original_notes)}, 更新: {len(updated_notes)})")
        return False


def test_plot_threads_structure():
    """测试 Bug #3: plot_threads 数据结构一致性"""
    print("\n" + "=" * 60)
    print("测试 #2: plot_threads 数据结构")
    print("=" * 60)

    from src.nodes.memory import update_bible_with_parsed_data

    # 测试短篇模式（无 hot_memory）
    state_short = {}  # No hot_memory = short mode
    world_bible_short = {"plot_threads": []}
    parsed_data = {"plot_developments": ["新伏笔1"]}

    updated_short = update_bible_with_parsed_data(
        world_bible_short, parsed_data, 1, state=state_short
    )
    is_list = isinstance(updated_short["plot_threads"], list)

    print(f"短篇模式 plot_threads 类型: {type(updated_short['plot_threads'])}")
    print(f"是列表吗? {is_list}")

    if not is_list:
        print("❌ FAILED: 短篇模式应该使用 list")
        return False

    # 测试长篇模式（有 hot_memory）
    state_long = {"hot_memory": {"plot_threads": {"active": []}}}
    world_bible_long = {"plot_threads": {"active": []}}

    updated_long = update_bible_with_parsed_data(
        world_bible_long, parsed_data, 1, state=state_long
    )
    is_dict = isinstance(updated_long["plot_threads"], dict)
    has_active = "active" in updated_long["plot_threads"] if is_dict else False

    print(f"\n长篇模式 plot_threads 类型: {type(updated_long['plot_threads'])}")
    print(f"是字典吗? {is_dict}")
    print(f"有 'active' 键吗? {has_active}")

    if not is_dict or not has_active:
        print("❌ FAILED: 长篇模式应该使用 dict 带 'active' 键")
        return False

    print("✅ PASSED: 两种模式的数据结构都正确")
    return True


def test_plot_tracks_typo_fix():
    """测试 Bug #2: plot_tracks typo fix"""
    print("\n" + "=" * 60)
    print("测试 #3: plot_tracks Typo Fix")
    print("=" * 60)

    # 读取 src/main.py 并检查是否使用了正确的键名
    with open("src/main.py", "r", encoding="utf-8") as f:
        content = f.read()

    has_typo = "'plot_tracks': plot_tracks" in content
    has_fix = "'plot_threads': plot_tracks" in content

    print(f"发现 'plot_tracks' 作为键名: {has_typo}")
    print(f"发现 'plot_threads' 作为键名: {has_fix}")

    if has_typo:
        print("❌ FAILED: 仍然使用错误的键名 'plot_tracks'")
        return False
    elif has_fix:
        print("✅ PASSED: 已修复为正确的键名 'plot_threads'")
        return True
    else:
        print("⚠️  WARNING: 找不到相关代码，可能已重构")
        return True


def test_import_copy():
    """测试 Bug #4: copy 模块导入"""
    print("\n" + "=" * 60)
    print("测试 #4: copy 模块导入")
    print("=" * 60)

    with open("src/nodes/memory.py", "r", encoding="utf-8") as f:
        content = f.read()

    has_import = "import copy" in content

    print(f"发现 'import copy': {has_import}")

    if has_import:
        print("✅ PASSED: copy 模块已导入")
        return True
    else:
        print("❌ FAILED: copy 模块未导入")
        return False


def main():
    """运行所有测试"""
    print("\n🧪 关键 Bug 修复测试")
    print("=" * 60)

    tests = [
        ("Deep Copy Fix", test_deep_copy_fix),
        ("plot_threads 结构", test_plot_threads_structure),
        ("plot_tracks Typo Fix", test_plot_tracks_typo_fix),
        ("copy 模块导入", test_import_copy),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            results.append((name, False))

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print(f"\n通过率: {passed}/{total} ({100*passed//total}%)")

    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
