"""
智能记忆管理器 - 自动适配短篇/长篇模式

根据章节数自动选择记忆策略：
- < 50章：完整记忆（现有方式）
- >= 50章：分层记忆（自动压缩）
"""

def should_use_layered_memory(target_chapters):
    """
    判断是否应该使用分层记忆

    Args:
        target_chapters: 目标章节数

    Returns:
        bool: True 表示使用分层记忆
    """
    # 阈值：50章
    return target_chapters >= 50


def get_memory_strategy(config):
    """
    获取记忆策略

    Args:
        config: 配置字典

    Returns:
        str: 'simple' 或 'layered'
    """
    target_chapters = config.get('novel', {}).get('target_chapters', 1)

    if should_use_layered_memory(target_chapters):
        return 'layered'
    else:
        return 'simple'


def print_memory_strategy(strategy, target_chapters):
    """打印记忆策略信息"""
    if strategy == 'layered':
        print(f"\n🧠 记忆策略: 分层记忆")
        print(f"   目标: {target_chapters} 章 (长篇模式)")
        print(f"   • 每25章自动压缩记忆")
        print(f"   • 内存占用可控")
        print(f"   • 支持200+章")
    else:
        print(f"\n🧠 记忆策略: 完整记忆")
        print(f"   目标: {target_chapters} 章 (短篇模式)")
        print(f"   • 保留所有详细记忆")
        print(f"   • 适用于100章以内")
