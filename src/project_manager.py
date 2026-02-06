"""
多小说项目管理器
- 为每个小说创建独立的工作空间
- 管理配置文件、数据库、章节文件
- 支持切换项目和断点续传
"""

import os
import json
import yaml
from pathlib import Path
from datetime import datetime


class ProjectManager:
    """小说项目管理器"""

    def __init__(self, base_dir="/project/novel"):
        self.base_dir = Path(base_dir)
        self.projects_dir = self.base_dir / "projects"
        self.projects_dir.mkdir(exist_ok=True)

        self.index_file = self.projects_dir / "projects_index.json"
        self.current_project_file = self.projects_dir / "current_project.txt"

    def list_projects(self):
        """列出所有项目"""
        if not self.index_file.exists():
            return {}

        with open(self.index_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_current_project(self):
        """获取当前激活的项目"""
        if not self.current_project_file.exists():
            return None

        with open(self.current_project_file, 'r', encoding='utf-8') as f:
            project_id = f.read().strip()

        projects = self.list_projects()
        return projects.get(project_id)

    def get_current_project_id(self):
        """仅获取当前项目ID（不含详细信息）"""
        if not self.current_project_file.exists():
            return None

        with open(self.current_project_file, 'r', encoding='utf-8') as f:
            return f.read().strip()

    def create_project(self, config):
        """创建新项目"""
        novel_title = config['novel']['title']

        # 生成项目ID（安全文件名）
        safe_title = "".join(c for c in novel_title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')

        # 检查是否已存在
        projects = self.list_projects()

        # 生成唯一ID（如果重名，添加时间戳）
        project_id = safe_title
        if project_id in projects:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_id = f"{safe_title}_{timestamp}"

        # 创建项目目录结构
        project_dir = self.projects_dir / project_id
        project_dir.mkdir(exist_ok=True)

        (project_dir / "manuscript").mkdir(exist_ok=True)
        (project_dir / "bible").mkdir(exist_ok=True)

        # 保存配置文件
        config_file = project_dir / "config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

        # 数据库路径
        db_file = project_dir / "state.db"

        # 添加到项目索引
        projects[project_id] = {
            "title": novel_title,
            "project_id": project_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "config_file": str(config_file),
            "db_file": str(db_file),
            "manuscript_dir": str(project_dir / "manuscript"),
            "bible_dir": str(project_dir / "bible"),
            "target_chapters": config['novel'].get('target_chapters', 1),
            "current_chapter": 0,
            "status": "created"
        }

        self._save_index(projects)

        # 设置为当前项目
        self.set_current_project(project_id)

        print(f"\n✅ 创建项目: {novel_title}")
        print(f"   项目ID: {project_id}")
        print(f"   配置: {config_file}")
        print(f"   数据库: {db_file}")
        print(f"   稿件目录: {project_dir / 'manuscript'}")

        return project_id, projects[project_id]

    def set_current_project(self, project_id):
        """切换到指定项目"""
        projects = self.list_projects()

        if project_id not in projects:
            raise ValueError(f"项目不存在: {project_id}")

        with open(self.current_project_file, 'w', encoding='utf-8') as f:
            f.write(project_id)

        return projects[project_id]

    def update_project_progress(self, project_id, current_chapter):
        """更新项目进度"""
        projects = self.list_projects()

        if project_id in projects:
            projects[project_id]["current_chapter"] = current_chapter
            projects[project_id]["updated_at"] = datetime.now().isoformat()

            # 更新状态
            target = projects[project_id]["target_chapters"]
            if current_chapter >= target:
                projects[project_id]["status"] = "completed"
            elif current_chapter > 0:
                projects[project_id]["status"] = "in_progress"

            self._save_index(projects)

    def get_project_paths(self, project_id):
        """获取项目的所有路径"""
        projects = self.list_projects()

        if project_id not in projects:
            raise ValueError(f"项目不存在: {project_id}")

        project = projects[project_id]

        return {
            "config_file": project["config_file"],
            "db_file": project["db_file"],
            "manuscript_dir": project["manuscript_dir"],
            "bible_dir": project["bible_dir"]
        }

    def delete_project(self, project_id):
        """删除项目"""
        projects = self.list_projects()

        if project_id not in projects:
            raise ValueError(f"项目不存在: {project_id}")

        # 删除项目目录
        project_dir = self.projects_dir / project_id
        if project_dir.exists():
            import shutil
            shutil.rmtree(project_dir)

        # 从索引中移除
        del projects[project_id]
        self._save_index(projects)

        # 如果是当前项目，清空当前项目标记
        current = self.get_current_project()
        if current and current["project_id"] == project_id:
            if self.current_project_file.exists():
                self.current_project_file.unlink()

        print(f"✅ 已删除项目: {project_id}")

    def _save_index(self, projects):
        """保存项目索引"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(projects, f, ensure_ascii=False, indent=2)

    def print_projects_table(self, show_current_header=True):
        """打印项目列表（表格形式）"""
        projects = self.list_projects()

        if not projects:
            print("\n暂无项目")
            return

        current = self.get_current_project()
        current_id = current["project_id"] if current else None

        # 显示当前项目（独立区域）
        if show_current_header and current:
            print("\n" + "="*80)
            print("🎯 当前项目")
            print("="*80)

            status_icon = {
                "created": "📝",
                "in_progress": "⏳",
                "completed": "✅"
            }.get(current["status"], "❓")

            progress = f"{current['current_chapter']}/{current['target_chapters']}"
            progress_pct = int((current['current_chapter'] / current['target_chapters']) * 100) if current['target_chapters'] > 0 else 0

            # 格式化时间显示
            updated_time = current['updated_at']
            if 'T' in updated_time:
                updated_time = updated_time.replace('T', ' ').split('.')[0]
            if len(updated_time) > 19:
                updated_time = updated_time[:19]

            print(f"{status_icon} {current['title']}")
            print(f"   项目ID: {current_id}")
            print(f"   进度: {progress} 章 ({progress_pct}%)")
            print(f"   状态: {current['status']}")
            print(f"   更新时间: {updated_time}")
            print()

        # 显示所有项目列表
        print("="*80)
        print("📚 所有项目列表")
        print("="*80)

        for project_id, info in projects.items():
            marker = "👉 " if project_id == current_id else "   "
            status_icon = {
                "created": "📝",
                "in_progress": "⏳",
                "completed": "✅"
            }.get(info["status"], "❓")

            progress = f"{info['current_chapter']}/{info['target_chapters']}"

            # 格式化时间显示（只显示日期和时间，不显示毫秒）
            updated_time = info['updated_at']
            if 'T' in updated_time:
                updated_time = updated_time.replace('T', ' ').split('.')[0]
            if len(updated_time) > 19:
                updated_time = updated_time[:19]

            print(f"{marker}{status_icon} {info['title']}")
            print(f"     ID: {project_id}")
            print(f"     进度: {progress} 章")
            print(f"     更新: {updated_time}")
            print()
