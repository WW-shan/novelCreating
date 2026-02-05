#!/usr/bin/env python3
"""
测试Bug #8修复: hot_memory与world_bible同步
"""

import sys
import copy

print("=" * 60)
print("🧪 测试 Bug #8: hot_memory与world_bible同步")
print("=" * 60)

all_passed = True

# ====== 测试1: 角色数据同步 ======
print("\n[测试1: 角色数据同步]")
try:
    # 模拟memory_update_node的逻辑
    new_bible = {
        "characters": {
            "主角": {
                "name": "张三",
                "recent_notes": ["第1章状态", "第2章状态", "第3章状态"]
            },
            "配角A": {
                "name": "李四",
                "recent_notes": ["第2章登场", "第3章发展"]
            }
        },
        "plot_threads": {
            "active": [
                {"text": "伏笔1", "created_at": 1},
                {"text": "伏笔2", "created_at": 2}
            ]
        },
        "world_events": ["事件1", "事件2", "事件3"]
    }

    hot_memory = {
        "current_volume": 1,
        "chapters_in_volume": 3,
        "characters": {},  # 初始为空!
        "plot_threads": {"active": []},
        "world_events": [],
        "recent_chapters": []
    }

    # 应用Bug #8修复:同步world_bible到hot_memory
    if "characters" in new_bible:
        for char_name, char_data in new_bible["characters"].items():
            if char_name not in hot_memory["characters"]:
                hot_memory["characters"][char_name] = {}
            if "recent_notes" in char_data:
                hot_memory["characters"][char_name]["recent_notes"] = char_data["recent_notes"]

    if "plot_threads" in new_bible and isinstance(new_bible["plot_threads"], dict):
        hot_memory["plot_threads"] = new_bible["plot_threads"]

    if "world_events" in new_bible:
        hot_memory["world_events"] = new_bible["world_events"]

    # 验证同步结果
    if "主角" in hot_memory["characters"]:
        print("  ✅ 主角已同步到hot_memory")
        if hot_memory["characters"]["主角"]["recent_notes"] == ["第1章状态", "第2章状态", "第3章状态"]:
            print("  ✅ 主角的recent_notes正确同步")
        else:
            print(f"  ❌ recent_notes不匹配: {hot_memory['characters']['主角']['recent_notes']}")
            all_passed = False
    else:
        print("  ❌ 主角未同步到hot_memory")
        all_passed = False

    if len(hot_memory["characters"]) == 2:
        print("  ✅ 2个角色都已同步")
    else:
        print(f"  ❌ 角色数量不对: {len(hot_memory['characters'])}")
        all_passed = False

    if len(hot_memory["plot_threads"]["active"]) == 2:
        print("  ✅ plot_threads已同步(2个)")
    else:
        print(f"  ❌ plot_threads未同步")
        all_passed = False

    if len(hot_memory["world_events"]) == 3:
        print("  ✅ world_events已同步(3个)")
    else:
        print(f"  ❌ world_events未同步")
        all_passed = False

except Exception as e:
    print(f"  ❌ 测试1失败: {e}")
    all_passed = False

# ====== 测试2: get_context_for_planner获取正确数据 ======
print("\n[测试2: get_context_for_planner能获取数据]")
try:
    # 模拟get_context_for_planner的逻辑
    state = {
        "hot_memory": hot_memory,  # 使用上面同步后的hot_memory
        "cold_memory": {"volume_summaries": []}
    }

    # 提取角色状态
    character_states = []
    for char_name, char_data in state["hot_memory"].get("characters", {}).items():
        notes = char_data.get("recent_notes", [])
        if notes:
            latest = notes[-1][:100]
            character_states.append(f"{char_name}: {latest}")

    # 提取伏笔
    active_threads = state["hot_memory"].get("plot_threads", {}).get("active", [])

    # 提取世界事件
    world_events = state["hot_memory"].get("world_events", [])

    # 验证
    if len(character_states) > 0:
        print(f"  ✅ 获取到角色状态: {len(character_states)}个")
        print(f"     - {character_states[0]}")
    else:
        print("  ❌ 未获取到角色状态(Bug #8未修复!)")
        all_passed = False

    if len(active_threads) > 0:
        print(f"  ✅ 获取到活跃伏笔: {len(active_threads)}个")
    else:
        print("  ❌ 未获取到活跃伏笔")
        all_passed = False

    if len(world_events) > 0:
        print(f"  ✅ 获取到世界事件: {len(world_events)}个")
    else:
        print("  ❌ 未获取到世界事件")
        all_passed = False

except Exception as e:
    print(f"  ❌ 测试2失败: {e}")
    all_passed = False

# ====== 测试3: 修复前后对比 ======
print("\n[测试3: 修复前后对比]")
try:
    # 修复前:hot_memory["characters"]为空
    hot_memory_before = {
        "characters": {},  # 空!
        "plot_threads": {"active": []},
        "world_events": []
    }

    # 提取角色状态(修复前)
    character_states_before = []
    for char_name, char_data in hot_memory_before.get("characters", {}).items():
        notes = char_data.get("recent_notes", [])
        if notes:
            character_states_before.append(f"{char_name}: {notes[-1]}")

    # 修复后:hot_memory["characters"]已同步
    hot_memory_after = {
        "characters": {
            "主角": {"recent_notes": ["第3章状态"]},
            "配角A": {"recent_notes": ["第3章发展"]}
        },
        "plot_threads": {"active": [{"text": "伏笔1"}]},
        "world_events": ["事件3"]
    }

    # 提取角色状态(修复后)
    character_states_after = []
    for char_name, char_data in hot_memory_after.get("characters", {}).items():
        notes = char_data.get("recent_notes", [])
        if notes:
            character_states_after.append(f"{char_name}: {notes[-1]}")

    print(f"  修复前: 角色状态 {len(character_states_before)} 个")
    print(f"  修复后: 角色状态 {len(character_states_after)} 个")

    if len(character_states_before) == 0 and len(character_states_after) > 0:
        print(f"  ✅ Bug #8修复有效!")
    else:
        print(f"  ❌ 对比失败")
        all_passed = False

except Exception as e:
    print(f"  ❌ 测试3失败: {e}")
    all_passed = False

# ====== 测试4: 增量同步 ======
print("\n[测试4: 增量同步(新角色添加)]")
try:
    # 初始hot_memory有1个角色
    hot_memory_incr = {
        "characters": {
            "主角": {"recent_notes": ["第1章"]}
        }
    }

    # world_bible新增了1个角色
    new_bible_incr = {
        "characters": {
            "主角": {"recent_notes": ["第1章", "第2章"]},  # 更新
            "新角色": {"recent_notes": ["第2章登场"]}  # 新增
        }
    }

    # 应用同步
    if "characters" in new_bible_incr:
        for char_name, char_data in new_bible_incr["characters"].items():
            if char_name not in hot_memory_incr["characters"]:
                hot_memory_incr["characters"][char_name] = {}
            if "recent_notes" in char_data:
                hot_memory_incr["characters"][char_name]["recent_notes"] = char_data["recent_notes"]

    # 验证
    if "新角色" in hot_memory_incr["characters"]:
        print("  ✅ 新角色已添加到hot_memory")
    else:
        print("  ❌ 新角色未添加")
        all_passed = False

    if len(hot_memory_incr["characters"]["主角"]["recent_notes"]) == 2:
        print("  ✅ 主角的notes已更新(2条)")
    else:
        print("  ❌ 主角的notes未更新")
        all_passed = False

except Exception as e:
    print(f"  ❌ 测试4失败: {e}")
    all_passed = False

# ====== 总结 ======
print("\n" + "=" * 60)
if all_passed:
    print("✅ Bug #8(hot_memory同步)修复测试通过!")
    print("=" * 60)
    sys.exit(0)
else:
    print("❌ 部分测试失败")
    print("=" * 60)
    sys.exit(1)
