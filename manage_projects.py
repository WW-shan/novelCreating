#!/usr/bin/env python3
"""
小说项目管理工具
- 查看所有项目
- 切换项目
- 删除项目
- 查看项目详情
"""

import sys
from src.project_manager import ProjectManager


def main():
    pm = ProjectManager()

    while True:
        print("\n" + "="*60)
        print("📚 小说项目管理器")
        print("="*60)

        # 显示当前项目和项目列表
        pm.print_projects_table(show_current_header=True)

        print("\n操作选项:")
        print("  1. 切换当前项目")
        print("  2. 删除项目")
        print("  3. 查看项目详情")
        print("  4. 退出")

        choice = input("\n请选择操作 (1-4): ").strip()

        if choice == "1":
            switch_project(pm)
        elif choice == "2":
            delete_project(pm)
        elif choice == "3":
            view_project_details(pm)
        elif choice == "4":
            print("\n👋 再见！")
            break
        else:
            print("\n❌ 无效选项，请重新选择")


def switch_project(pm):
    """切换项目"""
    projects = pm.list_projects()

    if not projects:
        print("\n暂无项目")
        return

    print("\n可用项目:")
    project_list = list(projects.items())
    for i, (project_id, info) in enumerate(project_list, 1):
        print(f"  {i}. {info['title']} ({project_id})")

    try:
        choice = int(input("\n请选择项目编号: ").strip())
        if 1 <= choice <= len(project_list):
            project_id = project_list[choice - 1][0]
            pm.set_current_project(project_id)
            print(f"\n✅ 已切换到项目: {projects[project_id]['title']}")
        else:
            print("\n❌ 无效编号")
    except ValueError:
        print("\n❌ 请输入数字")


def delete_project(pm):
    """删除项目"""
    projects = pm.list_projects()

    if not projects:
        print("\n暂无项目")
        return

    print("\n可用项目:")
    project_list = list(projects.items())
    for i, (project_id, info) in enumerate(project_list, 1):
        status = "✅" if info['status'] == 'completed' else "⏳"
        print(f"  {i}. {status} {info['title']} ({info['current_chapter']}/{info['target_chapters']}章)")

    try:
        choice = int(input("\n请选择要删除的项目编号 (0取消): ").strip())
        if choice == 0:
            return

        if 1 <= choice <= len(project_list):
            project_id = project_list[choice - 1][0]
            title = projects[project_id]['title']

            confirm = input(f"\n⚠️  确认删除项目 '{title}'? (yes/no): ").strip().lower()
            if confirm == 'yes':
                pm.delete_project(project_id)
            else:
                print("\n已取消删除")
        else:
            print("\n❌ 无效编号")
    except ValueError:
        print("\n❌ 请输入数字")


def view_project_details(pm):
    """查看项目详情"""
    projects = pm.list_projects()

    if not projects:
        print("\n暂无项目")
        return

    print("\n可用项目:")
    project_list = list(projects.items())
    for i, (project_id, info) in enumerate(project_list, 1):
        print(f"  {i}. {info['title']}")

    try:
        choice = int(input("\n请选择项目编号: ").strip())
        if 1 <= choice <= len(project_list):
            project_id, info = project_list[choice - 1]

            print("\n" + "="*60)
            print(f"📖 项目详情: {info['title']}")
            print("="*60)
            print(f"  项目ID: {project_id}")
            print(f"  状态: {info['status']}")
            print(f"  进度: {info['current_chapter']}/{info['target_chapters']} 章")
            print(f"  创建时间: {info['created_at'][:19]}")
            print(f"  更新时间: {info['updated_at'][:19]}")
            print(f"\n  配置文件: {info['config_file']}")
            print(f"  数据库: {info['db_file']}")
            print(f"  稿件目录: {info['manuscript_dir']}")
            print(f"  世界观目录: {info['bible_dir']}")

            input("\n按 Enter 继续...")
        else:
            print("\n❌ 无效编号")
    except ValueError:
        print("\n❌ 请输入数字")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 再见！")
        sys.exit(0)
