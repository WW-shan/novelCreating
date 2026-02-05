#!/bin/bash
# novel.sh - AI 小说生成器统一管理脚本

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
    cat << EOF
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        📚 AI 小说生成器 - 统一管理脚本                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

用法: ./novel.sh [命令]

📖 主要命令:
  generate      生成小说（使用当前配置）
  outline       生成/查看总纲和卷纲
  config        查看当前配置
  new           创建新的小说配置
  switch        切换小说配置

🧪 测试命令:
  test          运行所有测试
  test-api      测试 API 连接
  test-flow     测试完整流程（生成1章）

🛠️  维护命令:
  clean         清理生成状态（删除 novel_state.db）
  status        查看系统状态
  help          显示此帮助信息

📚 使用示例:
  ./novel.sh generate     # 开始生成小说
  ./novel.sh config       # 查看当前配置
  ./novel.sh switch       # 切换到其他小说
  ./novel.sh test         # 运行测试验证系统

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

    # 检查配置文件
    if [ ! -f "bible/novel_config_latest.yaml" ]; then
        echo -e "${RED}❌ 未找到配置文件${NC}"
        echo "请先运行: ./novel.sh new"
        exit 1
    fi

    # 检查是否有旧状态
    if [ -f "novel_state.db" ]; then
        echo -e "${YELLOW}⚠️  检测到旧的生成状态 (novel_state.db)${NC}"
        echo
        read -p "是否删除并重新开始? (y/n): " clean_db
        if [[ "$clean_db" == "y" || "$clean_db" == "Y" ]]; then
            rm novel_state.db
            echo -e "${GREEN}✅ 已清除旧状态${NC}"
        fi
        echo
    fi

    # 激活虚拟环境并运行
    source venv/bin/activate
    PYTHONPATH=/project/novel python3 src/main.py
}

# 查看配置
show_config() {
    if [ ! -f "bible/novel_config_latest.yaml" ]; then
        echo -e "${RED}❌ 未找到配置文件${NC}"
        echo "请先运行: ./novel.sh new"
        exit 1
    fi

    source venv/bin/activate 2>/dev/null

    python3 << 'PYEOF'
import yaml

with open('bible/novel_config_latest.yaml', 'r') as f:
    config = yaml.safe_load(f)

print("=" * 60)
print("📖 当前小说配置")
print("=" * 60)
print(f"\n标题: {config['novel']['title']}")
print(f"类型: {config['novel']['type']}")
print(f"目标章节: {config['novel']['target_chapters']}")

synopsis = config['novel']['synopsis']
if len(synopsis) > 200:
    synopsis = synopsis[:200] + "..."
print(f"\n梗概:\n{synopsis}")

print(f"\n风格:")
print(f"  名称: {config['style']['style_name']}")
print(f"  基调: {config['style']['tone']}")

print(f"\n主要角色:")
for i, char in enumerate(config['characters'][:3], 1):
    print(f"  {i}. {char['name']} ({char['age']}岁) - {char['occupation']}")

print(f"\n世界观:")
print(f"  时代: {config['worldbuilding']['era']}")
print(f"  场景: {config['worldbuilding']['setting']}")

print("=" * 60)
PYEOF
}

# 创建新配置
new_config() {
    echo -e "${BLUE}创建新的小说配置...${NC}"
    echo

    source venv/bin/activate
    python3 configure_novel.py

    echo
    echo -e "${GREEN}✅ 基础配置创建完成${NC}"
    echo

    # 询问是否生成总纲和卷纲
    read -p "是否使用 AI 生成总纲和卷纲？(y/n) [推荐]: " gen_outline

    if [[ "$gen_outline" == "y" || "$gen_outline" == "Y" || "$gen_outline" == "" ]]; then
        echo
        echo -e "${BLUE}🤖 生成总纲和卷纲...${NC}"
        python3 generate_outline.py
    else
        echo
        echo -e "${YELLOW}⚠️  跳过总纲生成，可以稍后运行: ./novel.sh outline${NC}"
    fi

    echo
    echo -e "${GREEN}✅ 配置创建完成${NC}"
    echo
    echo "保存此配置："
    read -p "输入配置名称（如：修仙传奇）: " config_name

    if [ -n "$config_name" ]; then
        cp bible/novel_config_latest.yaml "bible/novel_config_${config_name}.yaml"
        echo -e "${GREEN}✅ 已保存为: novel_config_${config_name}.yaml${NC}"
    fi
}

# 切换配置
switch_config() {
    echo "=========================================="
    echo "📚 小说配置切换器"
    echo "=========================================="
    echo

    # 查找所有配置文件
    configs=()
    config_files=()

    for file in bible/novel_config_*.yaml; do
        if [ -f "$file" ]; then
            basename=$(basename "$file" .yaml)
            name=${basename#novel_config_}

            # 只过滤掉 latest
            if [[ "$name" != "latest" ]]; then
                configs+=("$name")
                config_files+=("$file")
            fi
        fi
    done

    if [ ${#configs[@]} -eq 0 ]; then
        echo -e "${RED}❌ 没有找到可用的配置文件${NC}"
        echo "请先运行: ./novel.sh new"
        exit 1
    fi

    # 显示当前配置
    if [ -f "bible/novel_config_latest.yaml" ]; then
        current_title=$(grep "^  title:" "bible/novel_config_latest.yaml" | head -1 | sed 's/.*title: //' | tr -d '"')
        if [ -n "$current_title" ]; then
            echo -e "${BLUE}当前配置: $current_title${NC}"
            echo
        fi
    fi

    echo "可用的小说配置："
    echo
    for i in "${!configs[@]}"; do
        config_file="${config_files[$i]}"
        title=$(grep "^  title:" "$config_file" | head -1 | sed 's/.*title: //' | tr -d '"')
        chapters=$(grep "^  target_chapters:" "$config_file" | head -1 | sed 's/.*target_chapters: //')

        if [ -n "$title" ]; then
            echo "  $((i+1)). $title (${chapters}章)"
        else
            echo "  $((i+1)). ${configs[$i]} (${chapters}章)"
        fi
    done

    echo
    read -p "选择要切换的配置 (1-${#configs[@]}): " choice

    if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#configs[@]}" ]; then
        selected="${configs[$((choice-1))]}"
        selected_file="${config_files[$((choice-1))]}"

        cp "$selected_file" bible/novel_config_latest.yaml

        # 显示切换后的信息
        new_title=$(grep "^  title:" "bible/novel_config_latest.yaml" | head -1 | sed 's/.*title: //' | tr -d '"')
        echo -e "${GREEN}✅ 已切换到: $new_title${NC}"

        # 提示清除数据库
        if [ -f "novel_state.db" ]; then
            echo
            echo -e "${YELLOW}⚠️  检测到旧的生成状态${NC}"
            read -p "是否删除并重新开始? (y/n): " del_db
            if [[ "$del_db" == "y" || "$del_db" == "Y" ]]; then
                rm novel_state.db
                echo -e "${GREEN}✅ 已清除旧状态${NC}"
            fi
        fi
    else
        echo -e "${RED}❌ 无效选择${NC}"
        exit 1
    fi
}

# 运行测试
run_tests() {
    echo -e "${BLUE}运行系统测试...${NC}"
    echo

    source venv/bin/activate

    echo "1. API 连接测试"
    ./test_api.sh

    echo
    echo "2. 核心逻辑测试"
    ./test_core_logic.sh

    echo
    echo "3. 集成测试"
    ./test_long_novel_integration.sh

    echo
    echo -e "${GREEN}✅ 所有测试完成${NC}"
}

# API 测试
test_api() {
    source venv/bin/activate
    ./test_api.sh
}

# 流程测试
test_flow() {
    source venv/bin/activate
    ./test_full_flow.sh
}

# 生成/查看总纲和卷纲
generate_outline() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                                                              ║${NC}"
    echo -e "${BLUE}║              📖 总纲和卷纲生成工具                            ║${NC}"
    echo -e "${BLUE}║                                                              ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo

    source venv/bin/activate
    python3 generate_outline.py
}

# 清理状态
clean_state() {
    if [ -f "novel_state.db" ]; then
        rm novel_state.db
        echo -e "${GREEN}✅ 已删除 novel_state.db${NC}"
    else
        echo "没有找到 novel_state.db"
    fi
}

# 系统状态
show_status() {
    echo "=========================================="
    echo "系统状态"
    echo "=========================================="
    echo

    # 检查配置
    if [ -f "bible/novel_config_latest.yaml" ]; then
        echo -e "${GREEN}✅ 配置文件存在${NC}"
    else
        echo -e "${RED}❌ 配置文件不存在${NC}"
    fi

    # 检查虚拟环境
    if [ -d "venv" ]; then
        echo -e "${GREEN}✅ 虚拟环境存在${NC}"
    else
        echo -e "${RED}❌ 虚拟环境不存在${NC}"
    fi

    # 检查生成状态
    if [ -f "novel_state.db" ]; then
        size=$(ls -lh novel_state.db | awk '{print $5}')
        echo -e "${YELLOW}⚠️  检测到生成状态 ($size)${NC}"
    else
        echo -e "${GREEN}✅ 无旧生成状态${NC}"
    fi

    # 统计已生成的小说
    if [ -d "manuscript" ]; then
        novel_count=$(ls -1 manuscript/ 2>/dev/null | wc -l)
        echo -e "${BLUE}📚 已生成 $novel_count 本小说${NC}"
    fi

    echo
}

# 主逻辑
case "${1:-help}" in
    generate|gen|g)
        generate_novel
        ;;
    outline|ol|o)
        generate_outline
        ;;
    config|cfg|c)
        show_config
        ;;
    new|create|n)
        new_config
        ;;
    switch|sw|s)
        switch_config
        ;;
    test|t)
        run_tests
        ;;
    test-api)
        test_api
        ;;
    test-flow)
        test_flow
        ;;
    clean)
        clean_state
        ;;
    status|st)
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
