#!/bin/bash
# novel.sh - AI 小说生成器统一管理脚本（多项目版）

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 显示帮助
show_help() {
    cat <<EOF
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        📚 AI 小说生成器 - 统一管理脚本                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

用法: ./novel.sh [命令]

📖 主要命令:
  generate      生成小说（使用当前项目）
  new           创建新的小说项目
  projects      管理所有项目（切换/删除/查看）
  config        创建新配置（旧命令，推荐用new）

🛠️  维护命令:
  status        查看系统和项目状态
  help          显示此帮助信息

📚 使用示例:
  ./novel.sh new          # 创建新项目
  ./novel.sh generate     # 生成章节
  ./novel.sh projects     # 管理项目
  ./novel.sh status       # 查看状态

EOF
}

# 生成小说
generate_novel() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                                                              ║${NC}"
    echo -e "${BLUE}║              📚 开始生成小说                                  ║${NC}"
    echo -e "${BLUE}║                                                              ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo

    # 检查是否有项目（使用Python检查）
    source venv/bin/activate
    HAS_PROJECT=$(python3 -c "
from src.project_manager import ProjectManager
pm = ProjectManager()
projects = pm.list_projects()
print('yes' if projects else 'no')
" 2>/dev/null)

    if [ "$HAS_PROJECT" != "yes" ]; then
        echo -e "${RED}❌ 未找到任何项目${NC}"
        echo "请先运行: ./novel.sh new"
        exit 1
    fi

    # 激活虚拟环境并运行
    PYTHONPATH=/project/novel python3 src/main.py
}

# 创建新项目
new_project() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                                                              ║${NC}"
    echo -e "${BLUE}║              📝 创建新的小说项目                              ║${NC}"
    echo -e "${BLUE}║                                                              ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo

    source venv/bin/activate
    python3 configure_novel.py

    echo
    echo -e "${GREEN}✅ 项目创建完成${NC}"
    echo
    echo "下一步："
    echo "  ./novel.sh generate  # 开始生成章节"
    echo "  ./novel.sh projects  # 管理所有项目"
}

# 管理项目
manage_projects() {
    source venv/bin/activate
    python3 manage_projects.py
}

# 系统状态
show_status() {
    echo "=========================================="
    echo "📊 系统状态"
    echo "=========================================="
    echo

    # 检查虚拟环境
    if [ -d "venv" ]; then
        echo -e "${GREEN}✅ 虚拟环境存在${NC}"
    else
        echo -e "${RED}❌ 虚拟环境不存在${NC}"
    fi

    # 检查项目（使用Python检查）
    source venv/bin/activate 2>/dev/null
    PROJECT_COUNT=$(python3 -c "
from src.project_manager import ProjectManager
pm = ProjectManager()
print(len(pm.list_projects()))
" 2>/dev/null)

    if [ "$PROJECT_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✅ 已有 $PROJECT_COUNT 个项目${NC}"
    else
        echo -e "${YELLOW}⚠️  暂无项目（运行 ./novel.sh new 创建）${NC}"
    fi

    echo

    # 显示项目列表
    python3 -c "
from src.project_manager import ProjectManager
pm = ProjectManager()
pm.print_projects_table()
"

    echo
}

# 主逻辑
case "${1:-help}" in
    generate|gen|g)
        generate_novel
        ;;
    new|create|n)
        new_project
        ;;
    projects|proj|p)
        manage_projects
        ;;
    config|cfg)
        # 兼容旧命令
        echo -e "${YELLOW}提示: 推荐使用 './novel.sh new' 创建项目${NC}"
        echo
        new_project
        ;;
    status|st|s)
        show_status
        ;;
    help|h|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ 未知命令: $1${NC}"
        echo
        show_help
        exit 1
        ;;
esac
