#!/bin/bash
# Short Novel Generator - Quick Start Script

cd "$(dirname "$0")"

# Activate virtual environment if exists
if [ -f "../venv/bin/activate" ]; then
    source ../venv/bin/activate
fi

echo "==================================="
echo "   短篇小说生成器 - Quick Start"
echo "==================================="
echo ""
echo "请选择操作："
echo "  1. 分析小说提取模板 (analyze.py)"
echo "  2. 生成新小说 (generate.py)"
echo ""
read -p "选择 [1/2]: " choice

case $choice in
    1)
        python3 analyze.py
        ;;
    2)
        python3 generate.py
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac
