# Critical Bugs Found - 2026-02-04

## Systematic Debugging Report

Following systematic debugging methodology - Phase 1: Root Cause Investigation complete.

---

## 🐛 BUG #1: Shallow Copy Causes State Corruption

**File**: `src/nodes/memory.py:254`

**Severity**: 🔴 **CRITICAL** - Causes state corruption

**Root Cause**:
```python
updated_bible = world_bible.copy()  # ❌ SHALLOW COPY
```

**Impact**:
- Nested dictionaries (`characters`, `plot_threads`) are shared references
- Modifications to `updated_bible` mutate the original `world_bible`
- State corruption across chapters
- Character notes accumulate incorrectly
- Plot threads shared across iterations

**Evidence**:
```python
# Demonstration
world_bible = {"characters": {"A": {"notes": []}}}
updated_bible = world_bible.copy()  # Shallow
updated_bible["characters"]["A"]["notes"].append("new")
# Result: world_bible["characters"]["A"]["notes"] == ["new"]  ❌ CORRUPTED!
```

**Fix**:
```python
import copy
updated_bible = copy.deepcopy(world_bible)  # ✅ DEEP COPY
```

---

## 🐛 BUG #2: plot_tracks vs plot_threads Typo

**File**: `src/main.py:69`

**Severity**: 🔴 **CRITICAL** - Initial plot setup lost

**Root Cause**:
```python
initial_state = {
    'world_bible': {
        'plot_tracks': plot_tracks  # ❌ TYPO: should be plot_threads
    }
}
```

**Impact**:
- Initial plot setup is stored as `plot_tracks`
- All other code expects `plot_threads`
- Initial plot hints are completely ignored
- Story starts with empty plot context

**Evidence**:
- `plot_tracks`: 3 occurrences (only in initialization)
- `plot_threads`: 34 occurrences (everywhere else)

**Fix**:
```python
'plot_threads': plot_tracks  # ✅ Use correct key name
```

---

## 🐛 BUG #3: Inconsistent plot_threads Data Structure

**Files**:
- `src/nodes/memory.py:270`
- `src/memory/layered_memory.py:33-35`

**Severity**: 🟡 **HIGH** - Mode switching breaks

**Root Cause**:

**Short novel mode** (< 50 chapters):
```python
# memory.py creates as list
updated_bible["plot_threads"] = []  # ❌ list
```

**Long novel mode** (≥ 50 chapters):
```python
# layered_memory.py expects dict
hot_memory = {
    "plot_threads": {
        "active": []  # ✅ dict with "active" key
    }
}
```

**Impact**:
- Mode switching at chapter 50 will fail
- `.get("plot_threads", {}).get("active", [])` returns `None` if it's a list
- Planner node crashes or gets empty plot context

**Evidence**:
```bash
# Short mode creates list:
src/nodes/memory.py:270:  updated_bible["plot_threads"] = []

# Long mode expects dict:
src/memory/layered_memory.py:93:  hot_memory.get("plot_threads", {}).get("active", [])
```

**Fix**:

Option 1: Use consistent structure everywhere (dict with "active"):
```python
# In memory.py
updated_bible["plot_threads"] = {"active": []}
```

Option 2: Normalize on read:
```python
# In layered_memory.py
plot_threads = hot_memory.get("plot_threads", [])
if isinstance(plot_threads, list):
    active_threads = plot_threads
else:
    active_threads = plot_threads.get("active", [])
```

**Recommendation**: Option 1 (consistent structure)

---

## 🐛 BUG #4: Missing Import in memory.py

**File**: `src/nodes/memory.py`

**Severity**: 🟡 **HIGH** - Fix for Bug #1 requires this

**Root Cause**:
- `copy` module not imported
- Needed for `copy.deepcopy()`

**Fix**:
```python
import copy  # Add at top of file
```

---

## 🐛 BUG #5: Potential Performance Issue - Repeated AI Calls in Volume Compression

**File**: `src/memory/layered_memory.py:257-258`

**Severity**: 🟢 **MEDIUM** - Performance degradation

**Root Cause**:
```python
# Line 257-258
for char_name, char_data in characters.items():
    # ... AI call ...
    time.sleep(1)  # Sleep between each character
```

**Impact**:
- For 10 characters: 10 AI calls + 10 seconds sleep = ~20+ seconds
- Unnecessary delay in volume compression
- User waits longer between volumes

**Fix**:
Use batch processing or parallel calls:
```python
# Option 1: Remove sleep if rate limiting not needed
# Option 2: Use async/await for parallel processing
# Option 3: Batch all characters into single AI call
```

---

## Summary of Critical Bugs

| Bug | Severity | Impact | Fix Complexity |
|-----|----------|--------|----------------|
| #1 Shallow Copy | 🔴 Critical | State corruption | Low (1 line) |
| #2 plot_tracks typo | 🔴 Critical | Plot setup lost | Low (1 line) |
| #3 Inconsistent structure | 🟡 High | Mode switching fails | Medium (multiple files) |
| #4 Missing import | 🟡 High | Blocks fix #1 | Low (1 line) |
| #5 Performance | 🟢 Medium | Slow compression | Medium (refactor) |

---

## Testing Required

After fixes:
1. Test short novel generation (< 50 chapters)
2. Test long novel generation (≥ 50 chapters)
3. Test mode switching at chapter 50
4. Test volume compression (chapter 25, 50, 75)
5. Test checkpoint/resume functionality
6. Verify character state propagation
7. Verify plot thread tracking

---

## Next Steps

1. **Phase 3**: Form hypotheses about interaction effects
2. **Phase 4**: Implement fixes in order of criticality
3. **Verification**: Run tests to confirm fixes

---

**Debugging Method Used**: Systematic Debugging (Phase 1 & 2 complete)
**Evidence Gathered**: Code inspection, grep analysis, data flow tracing
**Pattern Analysis**: Compared short vs long mode, identified inconsistencies
