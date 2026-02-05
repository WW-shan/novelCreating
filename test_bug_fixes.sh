#!/bin/bash
# 测试Bug修复效果

echo "================================"
echo "测试Bug修复 - 200章长篇系统"
echo "================================"

cd "$(dirname "$0")"

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ 虚拟环境不存在，请先运行: python3 -m venv venv && pip install -r requirements.txt"
    exit 1
fi

# 1. 测试Python语法
echo ""
echo "1️⃣ 检查Python语法..."
python3 -m py_compile src/main.py
if [ $? -eq 0 ]; then
    echo "   ✅ main.py 语法正确"
else
    echo "   ❌ main.py 语法错误"
    exit 1
fi

python3 -m py_compile src/nodes/planner.py
if [ $? -eq 0 ]; then
    echo "   ✅ planner.py 语法正确"
else
    echo "   ❌ planner.py 语法错误"
    exit 1
fi

# 2. 测试断点续传逻辑
echo ""
echo "2️⃣ 测试断点续传逻辑..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/project/novel')

# 检查缩进是否正确 - 查找关键代码片段
with open('src/main.py', 'r') as f:
    content = f.read()

# 检查 resume 分支的关键结构
if 'if resume_from_checkpoint:' in content:
    if 'for step_output in app.stream(None' in content:
        if 'for node_name, node_output in step_output.items():' in content:
            # 检查print语句是否正确缩进（应该在 for node_name 循环内）
            lines = content.split('\n')
            found_resume_loop = False
            correct_indent = False

            for i, line in enumerate(lines):
                if 'if resume_from_checkpoint:' in line:
                    found_resume_loop = True
                if found_resume_loop and 'for node_name, node_output in step_output.items():' in line:
                    # 下一行应该是正确缩进的print
                    next_line = lines[i+1] if i+1 < len(lines) else ""
                    if 'print(f"\\n✓ 完成节点:' in next_line or 'print(f"\\\\n✓ 完成节点:' in next_line:
                        # 检查缩进深度（应该比 for 多4个空格）
                        for_indent = len(line) - len(line.lstrip())
                        print_indent = len(next_line) - len(next_line.lstrip())
                        if print_indent == for_indent + 4:
                            print("   ✅ 断点续传代码缩进正确")
                            correct_indent = True
                        else:
                            print(f"   ❌ 缩进错误: for={for_indent}, print={print_indent}")
                            sys.exit(1)
                        break

            if not correct_indent:
                print("   ❌ 未找到正确的代码结构")
                sys.exit(1)
        else:
            print("   ❌ 缺少 for node_name 循环")
            sys.exit(1)
    else:
        print("   ❌ 缺少 app.stream(None) 调用")
        sys.exit(1)
else:
    print("   ❌ 缺少 resume_from_checkpoint 分支")
    sys.exit(1)
PYEOF

if [ $? -ne 0 ]; then
    exit 1
fi

# 3. 测试总纲和卷纲初始化
echo ""
echo "3️⃣ 测试总纲和卷纲初始化..."
python3 << 'PYEOF'
import sys
import yaml
sys.path.insert(0, '/project/novel')

from src.main import config_to_initial_state

# 创建测试配置（50章，触发长篇模式）
test_config = {
    'novel': {
        'title': '测试小说',
        'synopsis': '这是一个测试小说的梗概',
        'target_chapters': 50,  # 触发长篇模式
        'type': 'mystery'
    },
    'worldbuilding': {
        'era': '现代',
        'setting': '都市',
        'power_system': '无'
    },
    'characters': [
        {
            'name': '主角',
            'age': '25',
            'occupation': '测试员',
            'goal': '完成测试',
            'traits': ['聪明'],
            'relationships': {}
        }
    ],
    'generation': {
        'foreshadow_strategy': 'moderate',
        'seed': None,
        'randomness_level': 'medium',
        'temperature': 0.7
    },
    'style': {
        'tone': 'neutral',
        'focus_elements': []
    }
}

try:
    # 测试初始化
    state = config_to_initial_state(test_config)

    # 检查总纲
    if 'novel_outline' in state:
        outline = state['novel_outline']
        if 'main_goal' in outline:
            print(f"   ✅ 总纲已初始化")
            print(f"      主目标: {outline['main_goal'][:50]}...")
        else:
            print("   ❌ 总纲缺少main_goal字段")
            sys.exit(1)
    else:
        print("   ❌ 总纲未初始化")
        sys.exit(1)

    # 检查卷纲
    if 'volume_frameworks' in state:
        frameworks = state['volume_frameworks']
        expected_volumes = (50 + 24) // 25  # 2卷
        if len(frameworks) == expected_volumes:
            print(f"   ✅ 卷纲已初始化 ({len(frameworks)} 卷)")
            print(f"      第1卷: {frameworks[0]['title']}")
        else:
            print(f"   ❌ 卷纲数量错误: {len(frameworks)} != {expected_volumes}")
            sys.exit(1)
    else:
        print("   ❌ 卷纲未初始化")
        sys.exit(1)

    # 检查分层记忆
    if 'hot_memory' in state and 'cold_memory' in state:
        print(f"   ✅ 分层记忆已初始化")
    else:
        print("   ❌ 分层记忆未初始化")
        sys.exit(1)

except Exception as e:
    print(f"   ❌ 初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF

if [ $? -ne 0 ]; then
    exit 1
fi

# 4. 测试Planner的分层记忆集成
echo ""
echo "4️⃣ 测试Planner分层记忆集成..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/project/novel')

# 检查导入
try:
    from src.nodes.planner import planner_node
    print("   ✅ Planner节点可以导入")

    # 检查是否引用了 get_context_for_planner
    with open('src/nodes/planner.py', 'r') as f:
        content = f.read()

    if 'get_context_for_planner' in content:
        print("   ✅ Planner已集成分层记忆获取")
    else:
        print("   ❌ Planner未集成分层记忆")
        sys.exit(1)

    if 'hot_memory' in content and 'cold_memory' in content:
        print("   ✅ Planner检查热/冷记忆")
    else:
        print("   ❌ Planner未检查热/冷记忆")
        sys.exit(1)

except Exception as e:
    print(f"   ❌ 测试失败: {e}")
    sys.exit(1)
PYEOF

if [ $? -ne 0 ]; then
    exit 1
fi

echo ""
echo "================================"
echo "✅ 所有Bug修复测试通过！"
echo "================================"
echo ""
echo "修复总结："
echo "  1. ✅ 断点续传缩进错误已修复"
echo "  2. ✅ 总纲自动初始化（缺失时）"
echo "  3. ✅ 卷纲自动生成（基于章节数）"
echo "  4. ✅ Planner集成分层记忆"
echo ""
echo "下一步："
echo "  - 运行 ./novel.sh status 查看系统状态"
echo "  - 运行 ./novel.sh generate 开始生成"
echo "  - 对于200+章，建议在配置中手动添加详细的总纲和卷纲"
