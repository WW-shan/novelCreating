#!/bin/bash
# API 连接测试脚本

echo "============================================"
echo "   🧪 API 连接测试"
echo "============================================"
echo ""

# 加载环境
source /project/novel/venv/bin/activate
export PYTHONPATH=/project/novel:$PYTHONPATH

# 加载 .env 文件
set -a
source /project/novel/.env
set +a

echo "📡 当前配置:"
echo "   Base URL: $ANTHROPIC_BASE_URL"
echo "   API Key: ${ANTHROPIC_API_KEY:0:20}..."
echo ""

# 验证环境变量
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ANTHROPIC_API_KEY 未设置"
    exit 1
fi

if [ -z "$ANTHROPIC_BASE_URL" ]; then
    echo "❌ ANTHROPIC_BASE_URL 未设置"
    exit 1
fi

echo "🔧 测试 API 连接..."

# 导出环境变量供 Python 使用
export ANTHROPIC_API_KEY
export ANTHROPIC_BASE_URL
export ANTHROPIC_AUTH_TOKEN

python3 << 'PYTHON_SCRIPT'
import os
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

# 调试：打印环境变量
api_key = os.getenv("ANTHROPIC_API_KEY")
base_url = os.getenv("ANTHROPIC_BASE_URL")

print(f"DEBUG: API Key from env: {api_key[:20] if api_key else 'None'}...")
print(f"DEBUG: Base URL from env: {base_url}")
print("")

if not api_key:
    print("❌ ANTHROPIC_API_KEY 未在 Python 中获取到")
    exit(1)

try:
    # 使用环境变量中的配置
    llm = ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        temperature=0.7,
        anthropic_api_key=api_key,
        anthropic_api_url=base_url
    )

    print("✅ 客户端初始化成功")
    print("📤 发送测试消息...")

    response = llm.invoke([HumanMessage(content="请用中文回复一句话：系统测试成功")])

    print("✅ API 调用成功！")
    print(f"📥 响应: {response.content}")
    print("")
    print("🎉 系统已准备就绪，可以开始生成小说！")

except Exception as e:
    print(f"❌ 错误: {e}")
    print("")
    print("请检查:")
    print("  1. .env 文件中的 API 配置")
    print("  2. Base URL 是否正确")
    print("  3. API Key 是否有效")
    import traceback
    traceback.print_exc()
    exit(1)
PYTHON_SCRIPT

echo ""
echo "============================================"
