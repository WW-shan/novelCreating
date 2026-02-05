# 🔧 Bug #20修复: recent_notes类型不确定 - 2026-02-04

## 问题

**错误**: `TypeError: unhashable type: 'slice'`
**位置**: `layered_memory.py:382`
**代码**: `latest = notes[-1][:100]`

## 原因

假设`notes[-1]`是字符串,但实际可能是:
- 字符串 ✅
- dict对象 ❌
- list对象 ❌
- 其他类型 ❌

## 修复

添加类型检查:
```python
latest_note = notes[-1]
if isinstance(latest_note, str):
    latest = latest_note[:100]
elif isinstance(latest_note, dict):
    latest = latest_note.get("text", str(latest_note))[:100]
elif isinstance(latest_note, list):
    latest = str(latest_note[0])[:100] if latest_note else "状态未知"
else:
    latest = str(latest_note)[:100]
```

**修复时间**: 2026-02-04
**优先级**: 🔴 Critical
**状态**: ✅ 已修复
