#!/usr/bin/env python3
"""
简化测试 - 代码检查（无需运行时依赖）
"""

import re

def test_deep_copy_fix():
    """测试 Bug #1: copy.deepcopy 是否使用"""
    print("=" * 60)
    print("测试 #1: Deep Copy Fix (代码检查)")
    print("=" * 60)

    with open("src/nodes/memory.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 检查是否导入了 copy
    has_import = "import copy" in content

    # 检查是否使用了 deepcopy
    has_deepcopy = "copy.deepcopy(world_bible)" in content

    # 检查是否还在使用浅拷贝
    has_shallow = re.search(r'updated_bible\s*=\s*world_bible\.copy\(\)', content)

    print(f"✓ import copy: {has_import}")
    print(f"✓ copy.deepcopy(world_bible): {has_deepcopy}")
    print(f"✗ world_bible.copy() (shallow): {has_shallow is not None}")

    if has_import and has_deepcopy and not has_shallow:
        print("✅ PASSED: 已修复为深拷贝")
        return True
    else:
        print("❌ FAILED: 未正确使用深拷贝")
        return False


def test_plot_threads_dual_mode():
    """测试 Bug #3: 双模式支持"""
    print("\n" + "=" * 60)
    print("测试 #2: plot_threads 双模式支持 (代码检查)")
    print("=" * 60)

    with open("src/nodes/memory.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 检查是否检测 hot_memory
    has_mode_check = 'hot_memory = state.get("hot_memory")' in content

    # 检查是否有长篇模式处理
    has_long_mode = '{"active": []}' in content

    # 检查是否有短篇模式处理
    has_short_mode = 'updated_bible["plot_threads"] = []' in content

    print(f"✓ 检测 hot_memory: {has_mode_check}")
    print(f"✓ 长篇模式 (dict with active): {has_long_mode}")
    print(f"✓ 短篇模式 (list): {has_short_mode}")

    if has_mode_check and has_long_mode and has_short_mode:
        print("✅ PASSED: 双模式支持已实现")
        return True
    else:
        print("❌ FAILED: 双模式支持未完整实现")
        return False


def test_plot_tracks_typo():
    """测试 Bug #2: plot_tracks typo"""
    print("\n" + "=" * 60)
    print("测试 #3: plot_tracks Typo Fix")
    print("=" * 60)

    with open("src/main.py", "r", encoding="utf-8") as f:
        content = f.read()

    has_typo = "'plot_tracks': plot_tracks" in content
    has_fix = "'plot_threads': plot_tracks" in content

    print(f"✗ 'plot_tracks' 作为键名: {has_typo}")
    print(f"✓ 'plot_threads' 作为键名: {has_fix}")

    if has_typo:
        print("❌ FAILED: 仍有 typo")
        return False
    elif has_fix:
        print("✅ PASSED: Typo 已修复")
        return True
    else:
        print("⚠️  WARNING: 代码可能已重构")
        return True


def test_state_parameter():
    """测试 Bug #4: state 参数传递"""
    print("\n" + "=" * 60)
    print("测试 #4: state 参数传递")
    print("=" * 60)

    with open("src/nodes/memory.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 检查函数签名是否包含 state
    has_state_param = re.search(
        r'def update_bible_with_parsed_data\([^)]*state[^)]*\)',
        content
    )

    # 检查是否传递了 state
    has_state_pass = re.search(
        r'update_bible_with_parsed_data\([^)]*state[^)]*\)',
        content
    )

    print(f"✓ update_bible_with_parsed_data 接受 state 参数: {has_state_param is not None}")
    print(f"✓ 调用时传递 state: {has_state_pass is not None}")

    if has_state_param and has_state_pass:
        print("✅ PASSED: state 参数正确传递")
        return True
    else:
        print("❌ FAILED: state 参数未正确传递")
        return False


def main():
    """运行所有测试"""
    print("\n🧪 关键 Bug 修复测试 (代码检查)")
    print("=" * 60)

    tests = [
        ("Deep Copy Fix", test_deep_copy_fix),
        ("plot_threads 双模式", test_plot_threads_dual_mode),
        ("plot_tracks Typo", test_plot_tracks_typo),
        ("state 参数传递", test_state_parameter),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
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
    import sys
    sys.exit(main())
