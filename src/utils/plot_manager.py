"""
伏笔管理系统 - 完整版
追踪伏笔状态，提醒适时揭示
"""

def analyze_plot_threads(plot_threads, chapter_index):
    """
    分析伏笔状态

    Args:
        plot_threads: 伏笔列表，每个伏笔应为 dict:
            {
                "text": "伏笔内容",
                "created_at": 章节号,
                "resolved": False,
                "importance": 1-10 (可选)
            }
        chapter_index: 当前章节索引

    Returns:
        dict: {
            'pending': 未解决的伏笔,
            'should_reveal': 应该揭示的伏笔,
            'suggestions': 建议
        }
    """
    if not plot_threads:
        return {
            'pending': [],
            'should_reveal': [],
            'suggestions': ['可以考虑埋下新伏笔']
        }

    # 分析伏笔年龄（从出现到现在经过了多少章）
    pending = []
    should_reveal = []

    for thread in plot_threads:
        # 兼容旧格式（纯字符串）和新格式（字典）
        if isinstance(thread, str):
            # 旧格式：无法计算准确年龄，跳过
            pending.append(thread)
            continue

        # 新格式：使用 created_at 计算准确年龄
        if thread.get("resolved", False):
            # 已解决的伏笔，跳过
            continue

        created_at = thread.get("created_at", chapter_index)
        thread_age = chapter_index - created_at

        # 🔧 Bug #14修复: 将age存储到thread中,供format使用
        thread["age"] = thread_age

        # 如果伏笔已经存在5章以上，建议揭示
        if thread_age >= 5:
            should_reveal.append(thread)
        else:
            pending.append(thread)

    suggestions = []
    if should_reveal:
        suggestions.append(f"有 {len(should_reveal)} 个伏笔应该考虑揭示或推进")
    if len(pending) < 3:
        suggestions.append("伏笔较少，可以考虑埋下新伏笔")

    return {
        'pending': pending,
        'should_reveal': should_reveal,
        'suggestions': suggestions
    }


def format_plot_thread_guidance(analysis):
    """格式化伏笔指导信息"""
    lines = []

    if analysis['should_reveal']:
        lines.append("【应揭示的伏笔】")
        for thread in analysis['should_reveal'][:3]:  # 最多显示3个
            # 兼容新旧格式
            if isinstance(thread, dict):
                text = thread.get("text", str(thread))[:60]
                # 🔧 Bug #14修复: 从analysis中获取age,或者从thread计算
                # analysis中的should_reveal就是thread对象,需要从created_at计算age
                created_at = thread.get("created_at", 0)
                # 但这里没有chapter_index!需要在analysis中传递
                # 临时方案: 使用thread中的age字段(如果有),否则不显示
                if "age" in thread:
                    age = thread["age"]
                    lines.append(f"  - {text} (已埋下{age}章)")
                else:
                    lines.append(f"  - {text}")
            else:
                lines.append(f"  - {thread[:60]}")
        lines.append("  ⚠️ 这些伏笔已埋下较久，建议在本章推进或揭示")
        lines.append("")

    if analysis['pending']:
        lines.append("【未解决的伏笔】")
        for thread in analysis['pending'][:5]:  # 最多显示5个
            if isinstance(thread, dict):
                text = thread.get("text", str(thread))[:60]
            else:
                text = thread[:60]
            lines.append(f"  - {text}")
        lines.append("")

    if analysis['suggestions']:
        lines.append("【建议】")
        for suggestion in analysis['suggestions']:
            lines.append(f"  • {suggestion}")

    return "\n".join(lines) if lines else ""
