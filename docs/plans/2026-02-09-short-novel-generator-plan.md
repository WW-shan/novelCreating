# Short Novel Generator - Implementation Plan

Date: 2026-02-09
Design Doc: [short-novel-generator-design.md](./2026-02-09-short-novel-generator-design.md)

---

## Phase 1: Project Setup & Core Infrastructure

### Task 1.1: Create project structure
Create the `short_novel/` directory with all subdirectories.

```
short_novel/
  analyze.py
  generate.py
  config.py
  core/
    __init__.py
    ai_client.py
    template_manager.py
    analyzer.py
    generator.py
    scraper.py
    prompts/
  templates/
    男频/
    女频/
  stories/
  sources/
```

### Task 1.2: Implement config.py
- Load API key from environment variable
- Define constants: MODEL, MAX_TOKENS, directory paths
- Model: `claude-opus-4-6`

### Task 1.3: Implement ai_client.py
- Simple wrapper around Anthropic SDK
- Single function: `generate(system_prompt, user_prompt, max_tokens) -> str`
- Handle API errors with retry logic

---

## Phase 2: Template System

### Task 2.1: Define template YAML schema
Create a reference template file with all five layers:
- Reader Psychology Contract
- Character Function System
- Plot Rhythm Engine
- Writing Style Control
- Chapter Hook System

### Task 2.2: Implement template_manager.py
- `list_templates(category=None) -> List[str]`
- `load_template(name) -> dict`
- `save_template(name, data) -> None`
- `get_template_summary(name) -> str`

### Task 2.3: Create initial templates
Create 2 starter templates:
- `templates/男频/赘婿逆袭.yaml` - full example
- `templates/女频/闪婚总裁.yaml` - full example

---

## Phase 3: Template Analyzer

### Task 3.1: Implement scraper.py
- `fetch_url(url) -> str | None` - best-effort URL fetch
- Simple HTML parsing to extract text content
- Return None on failure (user falls back to paste)

### Task 3.2: Create analysis prompts
Create prompt files in `core/prompts/`:
- `analyze_structure.txt` - Round 1: Structure decomposition
- `analyze_emotion.txt` - Round 2: Emotion curve analysis
- `analyze_technique.txt` - Round 3: Technique extraction
- `analyze_abstract.txt` - Round 4: Abstract to template

### Task 3.3: Implement analyzer.py
- `analyze_structure(text) -> dict` - Chapter boundaries, plot nodes
- `analyze_emotion(text, structure) -> dict` - Emotion curves
- `analyze_technique(text, structure, emotion) -> dict` - Writing techniques
- `abstract_to_template(structure, emotion, technique) -> dict` - Final template

### Task 3.4: Implement analyze.py entry point
Interactive CLI:
1. Choose input method (paste / URL)
2. Input text
3. Run 4-round analysis with progress display
4. Show result, allow user to edit
5. Save to templates/

---

## Phase 4: Novel Generator

### Task 4.1: Create generation prompts
Create prompt files:
- `generate_setting.txt` - Generate characters and setting
- `generate_outline.txt` - Generate chapter-by-chapter outline
- `generate_chapter.txt` - Generate single chapter

### Task 4.2: Implement generator.py - Setting
- `generate_setting(template) -> dict`
- Generate protagonist, antagonists, female lead, setting
- Return structured setting data

### Task 4.3: Implement generator.py - Outline
- `generate_outline(template, setting) -> List[dict]`
- Per-chapter outline with:
  - Chapter title
  - Beat reference
  - Key scenes
  - Emotion target
  - Hook type

### Task 4.4: Implement generator.py - Chapter
- `generate_chapter(template, setting, outline, chapter_num, previous_chapters) -> str`
- Include all context in prompt:
  - Template beat definition
  - Chapter outline
  - Full previous chapters (coherence)
  - Writing style rules
  - Hook requirement

### Task 4.5: Implement generate.py entry point
Interactive CLI:
1. Select template from library
2. Generate or input setting
3. Generate outline, user confirms/edits
4. Chapter loop:
   - Generate chapter
   - User reviews: approve / regenerate / revise / manual edit
   - Save chapter
5. Output complete story

---

## Phase 5: Polish & Testing

### Task 5.1: Error handling
- API failures with retry
- Invalid template format detection
- Graceful interruption (save progress)

### Task 5.2: User experience
- Progress indicators
- Clear prompts and instructions
- Color output for terminal

### Task 5.3: Manual testing
- Analyze a sample novel
- Generate a complete short novel
- Verify template quality

---

## Implementation Order

```
Phase 1 (Infrastructure)
  1.1 Project structure
  1.2 config.py
  1.3 ai_client.py

Phase 2 (Templates)
  2.1 Template schema
  2.2 template_manager.py
  2.3 Initial templates

Phase 3 (Analyzer)
  3.1 scraper.py
  3.2 Analysis prompts
  3.3 analyzer.py
  3.4 analyze.py CLI

Phase 4 (Generator)
  4.1 Generation prompts
  4.2 Setting generation
  4.3 Outline generation
  4.4 Chapter generation
  4.5 generate.py CLI

Phase 5 (Polish)
  5.1 Error handling
  5.2 UX improvements
  5.3 Manual testing
```

---

## Files to Create

| File | Purpose |
|------|---------|
| `short_novel/config.py` | Configuration and constants |
| `short_novel/core/__init__.py` | Package init |
| `short_novel/core/ai_client.py` | Claude API wrapper |
| `short_novel/core/template_manager.py` | Template CRUD |
| `short_novel/core/scraper.py` | URL fetch helper |
| `short_novel/core/analyzer.py` | 4-round analysis |
| `short_novel/core/generator.py` | Story generation |
| `short_novel/core/prompts/analyze_*.txt` | Analysis prompts (4) |
| `short_novel/core/prompts/generate_*.txt` | Generation prompts (3) |
| `short_novel/analyze.py` | Analyzer CLI entry |
| `short_novel/generate.py` | Generator CLI entry |
| `short_novel/templates/男频/赘婿逆袭.yaml` | Example template |
| `short_novel/templates/女频/闪婚总裁.yaml` | Example template |

Total: ~15 files

---

## Estimated Effort

- Phase 1: 30 min
- Phase 2: 45 min
- Phase 3: 1 hour
- Phase 4: 1.5 hours
- Phase 5: 30 min

**Total: ~4 hours**
