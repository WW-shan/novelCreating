#!/usr/bin/env python3
"""测试 memory 节点的 JSON 解析鲁棒性"""

import json
import re

def extract_json_from_response(content):
    """从响应中提取 JSON（模拟 memory.py 的逻辑）"""
    # 尝试查找 JSON 代码块
    if "```json" in content:
        start = content.find("```json") + 7
        end = content.find("```", start)
        if end > start:
            return content[start:end].strip()
    
    # 尝试查找纯 JSON (以 { 开始)
    if "{" in content:
        start = content.find("{")
        end = content.rfind("}") + 1
        if end > start:
            return content[start:end].strip()
    
    return None

# 测试各种可能的 AI 响应格式
test_responses = [
    # 正常格式
    '''```json
{
  "chapter_summary": {
    "index": 1,
    "summary": "第一章摘要"
  },
  "character_updates": {
    "张三": "状态变化"
  }
}
```''',
    
    # 缺少逗号的错误格式（可能由 AI 生成）
    '''```json
{
  "chapter_summary": {
    "index": 1
    "summary": "第一章摘要"
  }
}
```''',
    
    # 包含注释的格式
    '''```json
{
  "chapter_summary": {
    "index": 1,  // 章节号
    "summary": "第一章摘要"
  }
}
```''',
]

print("测试 JSON 解析鲁棒性")
print("=" * 60)

for i, response in enumerate(test_responses, 1):
    print(f"\n测试 {i}:")
    json_content = extract_json_from_response(response)
    
    if json_content:
        # 尝试清理可能的注释
        json_content_clean = re.sub(r'//.*', '', json_content)
        
        try:
            parsed = json.loads(json_content_clean)
            print(f"✅ 解析成功: {list(parsed.keys())}")
        except json.JSONDecodeError as e:
            print(f"❌ 解析失败: {e}")
            print(f"   错误位置: line {e.lineno} column {e.colno}")
            print(f"   问题片段: {json_content_clean[max(0, e.pos-20):e.pos+20]}")
    else:
        print("❌ 未找到 JSON 内容")

print("\n" + "=" * 60)
print("\n建议:")
print("1. 在 memory.py 中添加 JSON 错误重试机制")
print("2. 在 prompt 中强调 JSON 格式规范")
print("3. 添加 JSON 语法预检查")
