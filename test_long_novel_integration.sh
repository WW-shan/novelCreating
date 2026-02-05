#!/bin/bash
# 测试长篇小说集成

set -e  # Exit on error

source venv/bin/activate

echo "=========================================="
echo "长篇小说集成测试"
echo "=========================================="
echo

# Test 1: 检测逻辑
echo "Test 1: 检测 50 章自动启用分层记忆"
echo "----------------------------------------"
python3 << 'EOF'
from src.main import config_to_initial_state
import yaml

with open('bible/novel_config_latest.yaml', 'r') as f:
    config = yaml.safe_load(f)

# 测试 49 章（不启用）
config['novel']['target_chapters'] = 49
state = config_to_initial_state(config)
assert 'hot_memory' not in state, "❌ 49章不应启用分层记忆"
print("✅ 49 章：使用简单记忆")

# 测试 50 章（启用）
config['novel']['target_chapters'] = 50
state = config_to_initial_state(config)
assert 'hot_memory' in state, "❌ 50章应启用分层记忆"
assert 'cold_memory' in state, "❌ 50章应有冷记忆"
print("✅ 50 章：启用分层记忆")

# 测试 200 章（启用）
config['novel']['target_chapters'] = 200
state = config_to_initial_state(config)
assert 'hot_memory' in state, "❌ 200章应启用分层记忆"
print("✅ 200 章：启用分层记忆")
EOF
echo

# Test 2: 工作流节点
echo "Test 2: 长篇工作流包含卷节点"
echo "----------------------------------------"
python3 << 'EOF'
from src.main import build_graph
import yaml

with open('bible/novel_config_latest.yaml', 'r') as f:
    config = yaml.safe_load(f)

# 短篇工作流
config['novel']['target_chapters'] = 10
app = build_graph(config)
nodes = list(app.nodes.keys())
assert 'volume_planner' not in nodes, "❌ 短篇不应有卷节点"
print(f"✅ 短篇工作流节点: {len(nodes)} 个")

# 长篇工作流
config['novel']['target_chapters'] = 50
app = build_graph(config)
nodes = list(app.nodes.keys())
assert 'volume_planner' in nodes, "❌ 长篇应有 volume_planner"
assert 'volume_review' in nodes, "❌ 长篇应有 volume_review"
print(f"✅ 长篇工作流节点: {len(nodes)} 个（含卷管理）")
EOF
echo

# Test 3: 字段名统一
echo "Test 3: 字符笔记字段名统一（recent_notes）"
echo "----------------------------------------"
python3 << 'EOF'
import inspect
from src.nodes.memory import update_bible_with_parsed_data

source = inspect.getsource(update_bible_with_parsed_data)
assert 'recent_notes' in source, "❌ memory.py 应使用 recent_notes"
assert '"notes"' not in source, "❌ memory.py 不应使用旧的 notes 字段"
print("✅ memory.py 使用 recent_notes 字段")
EOF
echo

# Test 4: 压缩触发
echo "Test 4: 第25章触发压缩逻辑"
echo "----------------------------------------"
python3 << 'EOF'
import inspect
from src.nodes.memory import memory_update_node

source = inspect.getsource(memory_update_node)
assert 'compress_volume_memory' in source, "❌ memory 节点应调用压缩函数"
assert '% 25 == 0' in source, "❌ 应检查 25 章边界"
print("✅ memory_update_node 包含压缩触发逻辑")
EOF
echo

# Test 5: 热记忆更新
echo "Test 5: 热记忆同步更新"
echo "----------------------------------------"
python3 << 'EOF'
import inspect
from src.nodes.memory import memory_update_node

source = inspect.getsource(memory_update_node)
assert 'hot_memory["recent_chapters"].append' in source, "❌ 应更新 hot_memory"
assert 'chapters_in_volume' in source, "❌ 应递增 chapters_in_volume"
print("✅ memory_update_node 同步更新热记忆")
EOF
echo

# Test 6: 分层记忆数据结构
echo "Test 6: 分层记忆数据结构完整性"
echo "----------------------------------------"
python3 << 'EOF'
from src.memory.layered_memory import initialize_layered_memory

config = {'generation': {'chapters_per_volume': 25}}
hot, cold = initialize_layered_memory(config)

assert hot['current_volume'] == 1, "❌ 应从第1卷开始"
assert hot['chapters_in_volume'] == 0, "❌ 初始卷内章节应为0"
assert hot['chapters_per_volume'] == 25, "❌ 每卷应为25章"
assert 'recent_chapters' in hot, "❌ 应有 recent_chapters 字段"
assert 'volume_summaries' in cold, "❌ 冷记忆应有卷摘要"

print(f"✅ 热记忆字段: {list(hot.keys())}")
print(f"✅ 冷记忆字段: {list(cold.keys())}")
EOF
echo

echo "=========================================="
echo "✅ 所有集成测试通过！"
echo "=========================================="
echo
echo "系统已就绪："
echo "  • < 50 章：自动使用简单记忆"
echo "  • ≥ 50 章：自动使用分层记忆"
echo "  • 每 25 章：自动压缩卷记忆"
echo "  • 工作流：自动添加卷管理节点"
echo
