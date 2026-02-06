#!/usr/bin/env python3
"""
测试当前项目显示功能
"""

from src.project_manager import ProjectManager
import os

def test_current_project_display():
    """测试当前项目显示"""
    print("\n" + "="*60)
    print("测试 1: 当前项目显示功能")
    print("="*60)

    pm = ProjectManager()
    projects = pm.list_projects()

    if not projects:
        print("❌ 没有项目，跳过测试")
        return False

    # 获取当前项目
    current = pm.get_current_project()

    if current:
        print(f"✅ 当前项目: {current['title']}")
        print(f"   项目ID: {current['project_id']}")
        print(f"   进度: {current['current_chapter']}/{current['target_chapters']} 章")
    else:
        print("⚠️  未设置当前项目")

    # 显示项目表格
    print("\n测试项目表格显示:")
    pm.print_projects_table(show_current_header=True)

    return True


def test_get_current_project_id():
    """测试获取当前项目ID"""
    print("\n" + "="*60)
    print("测试 2: 获取当前项目ID")
    print("="*60)

    pm = ProjectManager()
    project_id = pm.get_current_project_id()

    if project_id:
        print(f"✅ 当前项目ID: {project_id}")
        return True
    else:
        print("⚠️  未设置当前项目")
        return False


def test_status_display():
    """测试 novel.sh status 的当前项目显示"""
    print("\n" + "="*60)
    print("测试 3: novel.sh status 当前项目显示")
    print("="*60)

    import subprocess

    result = subprocess.run(
        ["bash", "novel.sh", "status"],
        capture_output=True,
        text=True,
        cwd="/project/novel"
    )

    output = result.stdout

    if "🎯 当前项目:" in output:
        print("✅ novel.sh status 显示当前项目")
        # 提取当前项目行
        for line in output.split('\n'):
            if "🎯 当前项目:" in line:
                print(f"   {line.strip()}")
        return True
    else:
        print("❌ novel.sh status 未显示当前项目")
        return False


if __name__ == "__main__":
    print("="*60)
    print("🧪 当前项目显示功能测试")
    print("="*60)

    results = []

    results.append(("当前项目显示", test_current_project_display()))
    results.append(("获取项目ID", test_get_current_project_id()))
    results.append(("novel.sh status", test_status_display()))

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
        print("✅ 所有测试通过！")
    else:
        print("⚠️  部分测试失败")
