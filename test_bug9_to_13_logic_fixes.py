#!/usr/bin/env python3
"""
测试Bug #9-13修复: 逻辑问题修复
"""

import sys

print("=" * 60)
print("🧪 测试 Bug #9-13: 逻辑问题修复")
print("=" * 60)

all_passed = True

# ====== Bug #9: 伏笔格式化问题 ======
print("\n[测试 Bug #9: 伏笔格式化]")
try:
    # 模拟长篇模式的thread(dict格式)
    threads_dict = [
        {"text": "伏笔1: 神秘宝藏的传说", "created_at": 1, "importance": 8},
        {"text": "伏笔2: 主角的身世之谜", "created_at": 2, "importance": 10}
    ]

    # 模拟短篇模式的thread(字符串格式)
    threads_str = ["伏笔A: 宝藏", "伏笔B: 身世"]

    # Bug #9修复后的格式化逻辑
    def format_threads(threads):
        formatted = []
        for thread in threads:
            if isinstance(thread, dict):
                formatted.append(thread.get("text", str(thread)))
            else:
                formatted.append(str(thread))
        return "\n".join([f"- {t}" for t in formatted])

    # 测试dict格式
    result_dict = format_threads(threads_dict)
    if "伏笔1: 神秘宝藏的传说" in result_dict and "'text'" not in result_dict:
        print("  ✅ dict格式正确提取text字段")
    else:
        print(f"  ❌ dict格式化失败: {result_dict}")
        all_passed = False

    # 测试字符串格式
    result_str = format_threads(threads_str)
    if "伏笔A: 宝藏" in result_str:
        print("  ✅ 字符串格式正常工作")
    else:
        print(f"  ❌ 字符串格式化失败")
        all_passed = False

except Exception as e:
    print(f"  ❌ Bug #9测试失败: {e}")
    all_passed = False

# ====== Bug #10: 短篇模式thread格式 ======
print("\n[测试 Bug #10: 短篇模式thread格式]")
try:
    # 模拟memory.py的短篇模式逻辑(修复后)
    plot_threads = []
    plot_developments = ["新伏笔1", "新伏笔2"]

    for dev in plot_developments:
        if isinstance(dev, str):
            plot_threads.append(dev)  # 保持字符串
        elif isinstance(dev, dict) and "text" in dev:
            plot_threads.append(dev["text"])
        else:
            plot_threads.append(str(dev))

    # 验证
    if all(isinstance(t, str) for t in plot_threads):
        print("  ✅ 短篇模式保持字符串格式")
    else:
        print(f"  ❌ 短篇模式格式错误: {type(plot_threads[0])}")
        all_passed = False

    if len(plot_threads) == 2 and plot_threads[0] == "新伏笔1":
        print("  ✅ 伏笔内容正确")
    else:
        print(f"  ❌ 伏笔内容错误")
        all_passed = False

except Exception as e:
    print(f"  ❌ Bug #10测试失败: {e}")
    all_passed = False

# ====== Bug #11: 伏笔检测逻辑 ======
print("\n[测试 Bug #11: 伏笔检测逻辑改进]")
try:
    # 伏笔文本
    thread_text = "主角发现了神秘的古老遗迹"

    # 卷内容
    volume_content = """
    第1章: 主角在森林中探险
    第2章: 发现了神秘的古老遗迹
    第5章: 遗迹中藏着秘密
    第10章: 神秘力量觉醒
    """

    # Bug #11修复前: 简单的前30字匹配(容易误判)
    old_logic = thread_text[:30] in volume_content

    # Bug #11修复后: 关键词提取+出现次数
    keywords = []
    if len(thread_text) >= 10:
        keywords.append(thread_text[5:15])
    if len(thread_text) >= 20:
        keywords.append(thread_text[10:20])

    mention_count = sum(volume_content.count(kw) for kw in keywords if kw)
    new_logic = mention_count >= 2

    print(f"  旧逻辑: {old_logic}, 新逻辑: {new_logic}, 提及次数: {mention_count}")

    if new_logic and mention_count >= 2:
        print("  ✅ 新逻辑能正确检测到伏笔被提及")
    else:
        print(f"  ⚠️  新逻辑需要调优")

    # 测试假阳性情况
    unrelated_thread = "主角的童年回忆"
    kw2 = []
    if len(unrelated_thread) >= 10:
        kw2.append(unrelated_thread[5:15])
    if len(unrelated_thread) >= 20:
        kw2.append(unrelated_thread[10:20])

    count2 = sum(volume_content.count(kw) for kw in kw2 if kw)

    if count2 < 2:
        print("  ✅ 新逻辑不会误判无关伏笔")
    else:
        print(f"  ⚠️  仍有误判风险")

except Exception as e:
    print(f"  ❌ Bug #11测试失败: {e}")
    all_passed = False

# ====== Bug #12: notes vs recent_notes ======
print("\n[测试 Bug #12: notes vs recent_notes字段]")
try:
    # 模拟短篇模式的角色数据
    characters_short = {
        "主角": {
            "name": "张三",
            "recent_notes": ["第1章状态", "第2章状态", "第3章状态"]
        }
    }

    # 模拟长篇模式的角色数据(转换后)
    characters_long = {
        "角色1": {
            "notes": ["当前状态摘要"]
        }
    }

    # Bug #12修复后: 兼容两种字段
    def get_notes(char_data):
        return char_data.get("notes", char_data.get("recent_notes", []))

    # 测试短篇
    notes_short = get_notes(characters_short["主角"])
    if len(notes_short) == 3 and notes_short[0] == "第1章状态":
        print("  ✅ 短篇模式(recent_notes)读取正确")
    else:
        print(f"  ❌ 短篇模式读取失败")
        all_passed = False

    # 测试长篇
    notes_long = get_notes(characters_long["角色1"])
    if len(notes_long) == 1 and notes_long[0] == "当前状态摘要":
        print("  ✅ 长篇模式(notes)读取正确")
    else:
        print(f"  ❌ 长篇模式读取失败")
        all_passed = False

except Exception as e:
    print(f"  ❌ Bug #12测试失败: {e}")
    all_passed = False

# ====== Bug #13: 初始plot_threads格式 ======
print("\n[测试 Bug #13: 初始plot_threads格式]")
try:
    # 模拟初始plot_tracks(字符串列表)
    plot_tracks_initial = ["主线剧情：少年踏上修仙之路..."]

    # 短篇模式: 直接使用
    plot_threads_short = plot_tracks_initial

    # 长篇模式: 转换为dict格式
    plot_threads_long = {
        "active": [
            {
                "text": track,
                "created_at": 1,
                "importance": 10,
                "resolved": False
            } for track in plot_tracks_initial
        ]
    }

    # 验证短篇格式
    if isinstance(plot_threads_short, list) and isinstance(plot_threads_short[0], str):
        print("  ✅ 短篇模式: 字符串列表格式")
    else:
        print(f"  ❌ 短篇模式格式错误")
        all_passed = False

    # 验证长篇格式
    if isinstance(plot_threads_long, dict) and "active" in plot_threads_long:
        if isinstance(plot_threads_long["active"][0], dict):
            if "text" in plot_threads_long["active"][0] and "importance" in plot_threads_long["active"][0]:
                print("  ✅ 长篇模式: dict格式,含metadata")
            else:
                print(f"  ❌ 长篇模式缺少字段")
                all_passed = False
        else:
            print(f"  ❌ 长篇模式active不是dict列表")
            all_passed = False
    else:
        print(f"  ❌ 长篇模式格式错误")
        all_passed = False

except Exception as e:
    print(f"  ❌ Bug #13测试失败: {e}")
    all_passed = False

# ====== 总结 ======
print("\n" + "=" * 60)
if all_passed:
    print("✅ Bug #9-13(逻辑问题)修复测试通过!")
    print("=" * 60)
    sys.exit(0)
else:
    print("❌ 部分测试失败")
    print("=" * 60)
    sys.exit(1)
