#!/bin/bash
# 快速测试整个生成流程

echo "🧪 测试完整生成流程（1章）"
echo ""

# 1. 检查配置
if [ ! -f bible/novel_config_latest.yaml ]; then
    echo "❌ 配置文件不存在"
    echo "   请先运行: python3 configure_novel.py"
    exit 1
fi

echo "✅ 配置文件存在"

# 2. 备份当前进度
if [ -f novel_state.db ]; then
    echo "📦 备份当前进度..."
    cp novel_state.db novel_state.db.backup
fi

# 3. 清除状态（测试用）
echo "🗑️  清除旧状态..."
rm -f novel_state.db*

# 4. 修改配置为测试模式（只生成1章）
echo "⚙️  设置测试模式（1章）..."
python3 << 'PYTHON'
import yaml

with open('bible/novel_config_latest.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

original_chapters = config['novel']['target_chapters']
config['novel']['target_chapters'] = 1

with open('bible/novel_config_latest.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

print(f"   已设置: {original_chapters} 章 → 1 章")
PYTHON

# 5. 加载环境变量
if [ ! -f .env ]; then
    echo "❌ 缺少 .env 文件"
    exit 1
fi

set -a
source .env
set +a

# 6. 运行生成
echo ""
echo "🚀 开始生成测试章节..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

source venv/bin/activate
export PYTHONPATH=/project/novel:$PYTHONPATH
python3 src/main.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 7. 检查结果
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 测试完成！"
    echo ""

    # 查找生成的章节
    chapter_file=$(find manuscript/ -name "chapter_001.md" | head -1)

    if [ -n "$chapter_file" ]; then
        echo "📄 生成的章节: $chapter_file"
        echo ""

        word_count=$(wc -m < "$chapter_file")
        echo "📊 统计:"
        echo "   字符数: $word_count"
        echo ""

        echo "📖 前 300 字符预览:"
        echo "────────────────────────────────────────"
        head -c 300 "$chapter_file"
        echo ""
        echo "────────────────────────────────────────"
        echo ""

        # 检查是否是占位内容
        if grep -q "超时未能生成" "$chapter_file"; then
            echo "⚠️  注意: 这是占位内容（部分段落超时）"
            echo "   - 可能的原因: 代理服务器仍然不稳定"
            echo "   - 建议: 等待几分钟后重试"
        else
            echo "✅ 这是真实生成的内容！"
            echo ""
            echo "🎉 分段生成策略工作正常！"
        fi
    else
        echo "⚠️  未找到生成的章节文件"
    fi
else
    echo ""
    echo "❌ 生成失败"
    echo "   查看上方错误信息"
fi

echo ""
echo "💡 提示:"
echo "   - 成功: 运行 ./run_novel.sh 生成完整小说"
echo "   - 失败: 查看错误日志，可能需要等待后重试"
