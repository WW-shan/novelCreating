#!/usr/bin/env python3
"""
总纲和卷纲生成与审查工具

功能：
1. 读取配置文件
2. 使用 AI 生成总纲和卷纲
3. 保存到文件
4. 显示给用户审查
5. 询问是否继续
"""

import sys
import os
import yaml
from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

# 加载环境变量
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)


def generate_novel_outline(config):
    """使用 AI 生成总纲"""

    novel_config = config['novel']
    synopsis = novel_config['synopsis']
    target_chapters = novel_config.get('target_chapters', 100)

    prompt = f"""你是资深小说策划，负责为长篇小说创建总纲。

【小说信息】
标题: {novel_config.get('title', '未命名')}
梗概: {synopsis}
目标章节数: {target_chapters} 章

【任务】
为这部小说创建总纲，包括：

1. **主线目标**: 整部小说的核心目标（50字以内）
2. **主要冲突**: 贯穿全文的主要矛盾（100字以内）
3. **主角成长弧**: 主角从开始到结束的变化（100字以内）
4. **关键里程碑**: 3-5个重要的剧情节点（每个30字以内）

【输出格式】
严格按以下 YAML 格式输出：

```yaml
main_goal: "主线目标描述"
main_conflict: "主要冲突描述"
protagonist_arc: "主角成长弧描述"
key_milestones:
  - milestone: "里程碑1"
    target_chapter: 20
  - milestone: "里程碑2"
    target_chapter: 50
  - milestone: "里程碑3"
    target_chapter: {target_chapters}
```

只输出 YAML，不要其他内容。"""

    try:
        llm = ChatAnthropic(
            model="claude-sonnet-4-5-20250929",
            temperature=0.7,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            anthropic_api_url=os.getenv("ANTHROPIC_BASE_URL"),
            timeout=60.0,
            max_retries=2
        )

        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()

        # 提取 YAML
        if "```yaml" in content:
            start = content.find("```yaml") + 7
            end = content.find("```", start)
            yaml_content = content[start:end].strip()
        elif "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            yaml_content = content[start:end].strip()
        else:
            yaml_content = content

        outline = yaml.safe_load(yaml_content)
        return outline

    except Exception as e:
        print(f"⚠️  AI 生成总纲失败: {e}")
        # 返回默认总纲
        return {
            'main_goal': f"完成故事：{synopsis[:100]}",
            'main_conflict': '待AI生成（请重试）',
            'protagonist_arc': '待AI生成（请重试）',
            'key_milestones': []
        }


def generate_volume_frameworks(config, novel_outline):
    """使用 AI 生成卷纲"""

    novel_config = config['novel']
    synopsis = novel_config['synopsis']
    target_chapters = novel_config.get('target_chapters', 100)
    total_volumes = (target_chapters + 24) // 25

    prompt = f"""你是资深小说策划，负责为长篇小说划分卷纲。

【小说信息】
标题: {novel_config.get('title', '未命名')}
梗概: {synopsis}
总章节数: {target_chapters} 章
总卷数: {total_volumes} 卷（每卷25章）

【总纲】
main_goal: {novel_outline.get('main_goal', '未设置')}
main_conflict: {novel_outline.get('main_conflict', '未设置')}
protagonist_arc: {novel_outline.get('protagonist_arc', '未设置')}

【任务】
为每一卷创建框架，包括：

1. **卷标题**: 有吸引力的卷名
2. **核心目标**: 本卷要达成的目标（50字以内）
3. **关键事件**: 本卷的3-5个重要事件（每个20字以内）
4. **结尾状态**: 本卷结束时的状态（30字以内）
5. **伏笔**: 本卷需要埋下的伏笔（3个以内，每个20字）

【输出格式】
严格按以下 YAML 格式输出：

```yaml
- title: "第一卷标题"
  chapters: "1-25"
  core_goal: "核心目标描述"
  key_events:
    - "关键事件1"
    - "关键事件2"
    - "关键事件3"
  ending_state: "结尾状态"
  foreshadowing:
    - "伏笔1"
    - "伏笔2"

- title: "第二卷标题"
  chapters: "26-50"
  core_goal: "核心目标描述"
  key_events:
    - "关键事件1"
    - "关键事件2"
  ending_state: "结尾状态"
  foreshadowing:
    - "伏笔1"

... (重复到第{total_volumes}卷)
```

只输出 YAML，不要其他内容。"""

    try:
        llm = ChatAnthropic(
            model="claude-sonnet-4-5-20250929",
            temperature=0.7,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            anthropic_api_url=os.getenv("ANTHROPIC_BASE_URL"),
            timeout=90.0,
            max_retries=2
        )

        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()

        # 提取 YAML
        if "```yaml" in content:
            start = content.find("```yaml") + 7
            end = content.find("```", start)
            yaml_content = content[start:end].strip()
        elif "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            yaml_content = content[start:end].strip()
        else:
            yaml_content = content

        frameworks = yaml.safe_load(yaml_content)
        return frameworks

    except Exception as e:
        print(f"⚠️  AI 生成卷纲失败: {e}")
        # 返回默认卷纲
        frameworks = []
        for vol_idx in range(1, total_volumes + 1):
            start_ch = (vol_idx - 1) * 25 + 1
            end_ch = min(vol_idx * 25, target_chapters)
            frameworks.append({
                'title': f'第{vol_idx}卷',
                'chapters': f'{start_ch}-{end_ch}',
                'core_goal': '待AI生成（请重试）',
                'key_events': [],
                'ending_state': '待定',
                'foreshadowing': []
            })
        return frameworks


def display_outline_and_frameworks(novel_outline, volume_frameworks):
    """显示总纲和卷纲供用户审查"""

    print("\n" + "=" * 70)
    print("📖 总纲 (Novel Outline)")
    print("=" * 70)

    print(f"\n🎯 主线目标:")
    print(f"   {novel_outline.get('main_goal', '未设置')}")

    print(f"\n⚔️  主要冲突:")
    print(f"   {novel_outline.get('main_conflict', '未设置')}")

    print(f"\n🌱 主角成长弧:")
    print(f"   {novel_outline.get('protagonist_arc', '未设置')}")

    milestones = novel_outline.get('key_milestones', [])
    if milestones:
        print(f"\n🎯 关键里程碑:")
        for i, ms in enumerate(milestones, 1):
            print(f"   {i}. 第{ms.get('target_chapter', '?')}章: {ms.get('milestone', '未设置')}")

    print("\n" + "=" * 70)
    print("📚 卷纲 (Volume Frameworks)")
    print("=" * 70)

    for i, vol in enumerate(volume_frameworks, 1):
        print(f"\n【第 {i} 卷】{vol.get('title', f'第{i}卷')}")
        print(f"   章节范围: {vol.get('chapters', '未知')}")
        print(f"   核心目标: {vol.get('core_goal', '未设置')}")

        events = vol.get('key_events', [])
        if events:
            print(f"   关键事件:")
            for j, event in enumerate(events, 1):
                print(f"      {j}. {event}")

        print(f"   结尾状态: {vol.get('ending_state', '未设置')}")

        foreshadows = vol.get('foreshadowing', [])
        if foreshadows:
            print(f"   埋下伏笔:")
            for j, fs in enumerate(foreshadows, 1):
                print(f"      {j}. {fs}")

    print("\n" + "=" * 70)


def save_outline_and_frameworks(config_path, novel_outline, volume_frameworks):
    """保存总纲和卷纲到配置文件"""

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    config['novel_outline'] = novel_outline
    config['volume_frameworks'] = volume_frameworks

    # 备份原文件
    import shutil
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = config_path.replace('.yaml', f'_backup_{timestamp}.yaml')
    shutil.copy2(config_path, backup_path)
    print(f"\n💾 原配置已备份到: {backup_path}")

    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"💾 总纲和卷纲已保存到: {config_path}")


def main():
    """主函数"""

    print("\n🎬 总纲和卷纲生成工具")
    print("=" * 70)

    # 读取配置
    config_path = "bible/novel_config_latest.yaml"

    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在: {config_path}")
        print("提示: 请先运行 ./novel.sh new 创建配置")
        return 1

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 检查是否已有总纲和卷纲
    existing_outline = config.get('novel_outline')
    existing_frameworks = config.get('volume_frameworks')

    if existing_outline and existing_frameworks:
        print("\n⚠️  配置文件中已有总纲和卷纲")
        print("\n选项:")
        print("  1. 查看现有总纲和卷纲")
        print("  2. 重新生成（覆盖现有内容）")
        print("  3. 退出")

        choice = input("\n请选择 (1-3): ").strip()

        if choice == '1':
            display_outline_and_frameworks(existing_outline, existing_frameworks)
            return 0
        elif choice == '2':
            print("\n重新生成...")
        else:
            print("\n退出")
            return 0

    # 生成总纲
    print("\n🤖 使用 AI 生成总纲...")
    novel_outline = generate_novel_outline(config)
    print("✅ 总纲生成完成")

    # 生成卷纲
    print("\n🤖 使用 AI 生成卷纲...")
    volume_frameworks = generate_volume_frameworks(config, novel_outline)
    print("✅ 卷纲生成完成")

    # 显示
    display_outline_and_frameworks(novel_outline, volume_frameworks)

    # 询问用户
    print("\n" + "=" * 70)
    print("请审查以上总纲和卷纲是否合理")
    print("=" * 70)

    while True:
        choice = input("\n是否保存到配置文件？ (y/n/r)  [y=保存, n=放弃, r=重新生成]: ").strip().lower()

        if choice == 'y':
            save_outline_and_frameworks(config_path, novel_outline, volume_frameworks)
            print("\n✅ 完成！现在可以运行 ./novel.sh generate 开始生成")
            return 0
        elif choice == 'n':
            print("\n已放弃，配置文件未修改")
            return 0
        elif choice == 'r':
            print("\n重新生成...")
            novel_outline = generate_novel_outline(config)
            volume_frameworks = generate_volume_frameworks(config, novel_outline)
            display_outline_and_frameworks(novel_outline, volume_frameworks)
        else:
            print("无效选择，请输入 y, n 或 r")


if __name__ == "__main__":
    sys.exit(main())
