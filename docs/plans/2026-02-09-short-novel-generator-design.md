# Short Novel Generator Design

Date: 2026-02-09

## Overview

A standalone short novel generator that produces 6k-20k word serialized stories using proven plot template ("套路模板") patterns extracted from successful novels. Target platform: 番茄小说 (Fanqie/Tomato Novel).

### Core Concept

Use market-validated story patterns as templates, AI generates new stories following the same emotional rhythm, character dynamics, and hook techniques. The user reviews and approves each chapter before proceeding.

### Key Decisions

- **Independent project** — not coupled with the existing long-novel system
- **Pure Python + Claude API** — no LangGraph, simple linear flow
- **Claude Opus 4.6** (`claude-opus-4-6`) for all AI calls
- **File-based storage** — simple directory structure, no database
- **Serialized format** — 5-12 chapters, 1200-2000 words each
- **User reviews every chapter** — AI generates, human approves

---

## 1. System Architecture

### Two Entry Points

```
analyze.py   — Input a successful novel, extract a reusable plot template
generate.py  — Select a template, generate a new novel chapter by chapter
```

### Core Flow

```
[Template Library] → [Select Template] → [Configure Setting] → [Generate Outline]
        ↓                                                            ↓
[Analyze Novel] → [Extract Template]                        [User Confirms]
                                                                     ↓
                                                        [Generate Chapter by Chapter]
                                                                     ↓
                                                          [User Reviews Each Chapter]
                                                                     ↓
                                                              [Final Output]
```

### Input Methods for Analyzer

- **Primary:** Paste novel text directly
- **Secondary:** URL fetch (best-effort, fallback to paste if fails)

---

## 2. Template Structure — Five Layers

Each template is a YAML file capturing five layers of what makes a story work.

### Layer 1: Reader Psychology Contract

What readers expect when they click this type of story.

```yaml
name: "赘婿逆袭"
category: "男频"
sub_type: "身份流"
tags: ["打脸", "身份反转", "爽文", "短篇连载"]
source: "分析自《xxxxx》等3篇爆款"
proven_metrics: "原作完读率85%+, 追读率60%+"

reader_contract:
  core_fantasy: "我其实是最强的，只是你们不知道"
  entry_emotion: "憋屈代入"
  payoff_emotion: "碾压释放"
  implicit_promise: "主角一定会翻盘，而且翻得很彻底"
  reading_motivation: "看所有看不起主角的人被打脸"
```

### Layer 2: Character Function System

Characters exist to serve the emotional payoff, not as independent entities.

```yaml
character_system:
  protagonist:
    archetype: "扮猪吃虎型强者"
    inner_trait: "绝对实力 + 主动选择隐忍"
    outer_trait: "被所有人看不起的身份（赘婿/保安/穷亲戚）"
    golden_rule: "主角永远不主动装逼，都是被逼出手"

  power_reveal_strategy:
    method: "洋葱式剥层"
    description: "每次只露一层，让人以为这就是底了，下次再揭一层更猛的"
    layers_example:
      - "原来他不是废物，他会点功夫"
      - "原来他不只是会功夫，他是特种兵王"
      - "原来他不只是兵王，他是最高统帅"

  antagonist_design:
    structure: "打脸阶梯"
    principle: "每个反派比上一个身份高、态度更嚣张、被打脸更惨"
    levels:
      - level: 1
        type: "身边小人"
        example: "势利眼丈母娘/小舅子"
        defeat_method: "小露一手，对方震惊但不服"
      - level: 2
        type: "有背景的对手"
        example: "富二代情敌/商业对手"
        defeat_method: "亮出部分身份，对方开始害怕"
      - level: 3
        type: "大Boss"
        example: "行业大佬/家族掌权者"
        defeat_method: "完全揭露身份，全场跪"

  female_lead:
    arc: "从怀疑到震惊到心疼"
    function: "读者情绪放大器——通过她的反应放大主角的帅"
    key_moment: "得知真相后，理解主角所有隐忍都是为了她"

  crowd_characters:
    function: "弹幕式反应器"
    purpose: "替读者说出'卧槽他居然这么牛'"
    technique: "每次反转必须有旁观者震惊反应，至少3句"
```

### Layer 3: Plot Rhythm Engine

The micro-level emotional control that makes readers unable to stop.

```yaml
plot_engine:
  rhythm_principle: "压3放1 — 每积累3份压抑，释放1份爽感，且释放强度递增"
  tension_curve: "锯齿上升型 — 每次释放后不回到原点，而是在更高处重新蓄压"

  beats:
    - beat_id: 1
      name: "入局"
      chapters: [1]
      story_goal: "30秒内让读者代入主角的憋屈处境"
      emotion_curve:
        start: "平静/日常"
        build: "压抑逐步加深"
        end: "愤怒+好奇（他到底什么来头）"
      micro_rhythm:
        - segment: "冷启动"
          weight: "10%"
          content: "一个具体场景直接展示主角的低地位（不要旁白交代）"
          technique: "用对话和行为展示，不用叙述"
        - segment: "蓄压"
          weight: "50%"
          content: "具体的羞辱事件，层层加码"
          technique: "至少3层递进羞辱：语言嘲讽→当众羞辱→触及底线"
          golden_rule: "羞辱必须具体、画面感强、让读者感同身受"
        - segment: "暗线埋设"
          weight: "15%"
          content: "一个不经意的细节暗示主角身份（只有读者能察觉）"
          technique: "如：主角接了个电话，对方称呼'首长'，但被噪音盖住"
        - segment: "钩子"
          weight: "25%"
          content: "一个不得不翻到下一章的理由"
          hook_type: "危机降临型"
          example: "就在这时，门被推开。来人看到主角的瞬间，脸色大变..."
      writing_rules:
        - "第一章前3段决定读者去留，必须有冲突"
        - "禁止大段背景介绍，所有信息通过冲突场景传递"
        - "第一章字数控制在1200-1500字，短而有力"

    - beat_id: 2
      name: "初次亮剑"
      chapters: [2, 3]
      story_goal: "第一次打脸，释放第一波爽感，但只揭露冰山一角"
      emotion_curve:
        start: "延续压抑（新的挑衅）"
        build: "主角被逼到不得不出手的临界点"
        peak: "反转瞬间——一招制敌"
        end: "余韵+新悬念"
      micro_rhythm:
        - segment: "再次蓄压"
          weight: "30%"
          content: "反派变本加厉，或新的更强反派出现"
          technique: "让读者觉得'这次真的过分了，主角你倒是反击啊'"
        - segment: "临界触发"
          weight: "10%"
          content: "一个具体事件让主角不得不出手"
          golden_rule: "主角出手必须有正当理由，不能主动找事"
        - segment: "碾压释放"
          weight: "30%"
          content: "主角出手，干脆利落"
          technique: "蓄压用50%篇幅，释放只用10%篇幅。越快越爽"
        - segment: "震惊反应"
          weight: "15%"
          content: "所有人的反应"
          technique: "至少写3个不同人的震惊反应，从不同角度放大爽感"
        - segment: "悬念升级"
          weight: "15%"
          content: "暗示这只是冰山一角"

    # Additional beats follow same structure for:
    # beat 3: "危机升级" (chapters 4-6)
    # beat 4: "身份揭露+终极打脸" (chapters 7-9)
    # beat 5: "收尾" (chapter 10)
```

### Layer 4: Writing Style Control

The "taste" that fits the Fanqie platform.

```yaml
writing_style:
  voice: "第三人称有限视角，偶尔切全知来展示反派心理"
  sentence_rhythm: "短句为主，关键时刻用极短句（三五个字一行）制造冲击感"

  paragraph_rules:
    - "对话占比60%以上，大段叙述必须打碎"
    - "每段不超过3行，保持手机阅读体验"
    - "动作描写用短句连发：他抬手。一拳。对方飞出三米。"

  vocabulary_level: "初中水平用词，拒绝文艺腔"

  banned_patterns:
    - "大段心理描写（用行为暗示代替）"
    - "形容词堆砌"
    - "生僻字和文言句式"
    - "说教式旁白"

  power_techniques:
    - name: "三连短句冲击"
      usage: "打脸/反转的关键瞬间"
      example: "他出手了。快得看不见。一拳。"
    - name: "对比蒙太奇"
      usage: "打脸前后的态度反转"
      example: "五分钟前：'就你？也配？' 五分钟后：'大...大人，小的有眼不识泰山！'"
    - name: "读者优越感制造"
      usage: "暗示主角身份时"
      example: "众人哄笑。没人注意到，主角手腕上那块表，全球只有三块。"
```

### Layer 5: Chapter Hook System

```yaml
hook_system:
  principle: "每章最后一句话必须让读者无法停下"

  hook_types:
    - type: "身份悬念"
      pattern: "[某个有权势的人] 看到 [主角/主角的某个物品]，脸色突变：'你...你是...'"
      usage_chapters: "前期章节"
    - type: "危机突降"
      pattern: "就在一切看似圆满时，[主角的手机/门外] 传来一个消息/人——[留白]"
      usage_chapters: "中期章节"
    - type: "实力悬念"
      pattern: "[主角做了一件不可思议的事]，所有人呆住了。而他只是笑了笑：'这只是...随手而已。'"
      usage_chapters: "打脸章节"
    - type: "情感炸弹"
      pattern: "[女主/关键人物] 终于知道了真相。她的眼泪止不住地流：'原来...这些年...'"
      usage_chapters: "后期章节"

  structural_rule: "连续两章不能用同一类型钩子"
```

---

## 3. Template Analyzer

### Purpose

Input a successful novel, output a reusable template YAML.

### Four-Round Analysis Process

```
Input (paste text / URL fetch)
       ↓
Round 1: Structure Decomposition
  - Identify chapter boundaries
  - Map plot nodes and turning points
  - Identify character archetypes and functions
       ↓
Round 2: Emotion Curve Analysis
  - Per-chapter emotion trajectory
  - Tension build/release rhythm
  - Hook type identification
       ↓
Round 3: Technique Extraction
  - Writing techniques used at key moments
  - Sentence patterns and rhythm
  - Style characteristics
       ↓
Round 4: Abstraction
  - Remove specific names, settings, details
  - Preserve structure, rhythm, techniques
  - Output reusable template YAML
       ↓
User Review & Adjust
       ↓
Save to templates/
```

### Why Four Rounds

- Single-pass analysis of 20k words loses detail
- Each round focuses on one dimension for higher quality
- Intermediate results can be reviewed and corrected

### URL Fetch (Best-Effort)

- Simple HTTP request + HTML parsing to extract body text
- Falls back to manual paste on failure
- No complex anti-scraping measures

---

## 4. Novel Generator

### Generation Flow

```
Step 1: Select Template    →  Browse template library, pick one
Step 2: Configure Setting  →  AI generates or user specifies characters/background
Step 3: Generate Outline   →  Per-chapter outline with emotion curves and key scenes
Step 4: User Confirms      →  Approve, modify specific chapters, or regenerate
Step 5: Generate Chapters  →  One at a time, user reviews each
Step 6: Output             →  Complete story in chapters/
```

### Chapter Generation Strategy

Each chapter's prompt includes:
- The template beat definition for this chapter (emotion curve, micro rhythm, techniques)
- The confirmed outline for this chapter
- **Full text of all previously confirmed chapters** (under 20k words, fits in context)
- Writing style rules from template
- Required hook type for chapter ending

This ensures every chapter precisely follows the template rhythm while maintaining perfect coherence with prior chapters.

### User Review Options Per Chapter

1. **Approve** — continue to next chapter
2. **Regenerate** — discard and regenerate from scratch
3. **Revise with feedback** — provide specific notes, AI rewrites based on feedback
4. **Manual edit** — user edits the file directly, then continue

---

## 5. Project Structure

```
short_novel/
  analyze.py                # Entry: template analyzer
  generate.py               # Entry: novel generator
  config.py                 # Global config (API key, model, paths)

  core/
    analyzer.py             # Four-round analysis logic
    generator.py            # Outline + chapter generation logic
    template_manager.py     # Template CRUD operations
    scraper.py              # URL fetch helper (best-effort)
    ai_client.py            # Claude API wrapper
    prompts/
      analyze_structure.txt
      analyze_emotion.txt
      analyze_technique.txt
      analyze_abstract.txt
      generate_setting.txt
      generate_outline.txt
      generate_chapter.txt

  templates/                # Template library
    男频/
      赘婿逆袭.yaml
      兵王归来.yaml
      神医下山.yaml
    女频/
      闪婚总裁.yaml
      重生复仇.yaml
      穿书甜宠.yaml

  stories/                  # Generated novels
    [title]_[date]/
      config.yaml
      outline.yaml
      chapters/
        chapter_01.md
        chapter_02.md
        ...

  sources/                  # Source texts for analysis
```

---

## 6. Configuration

```python
# config.py
API_KEY = "from environment variable"
MODEL = "claude-opus-4-6"
MAX_TOKENS_PER_CHAPTER = 4096

TEMPLATES_DIR = "templates/"
STORIES_DIR = "stories/"
SOURCES_DIR = "sources/"
```

### Cost Estimate

- Analyzing 1 novel: ~$1-3
- Generating 1 complete short novel (10 chapters): ~$3-5
- Total per story including revisions: ~$5-10

---

## 7. Initial Template Library

Ship with 6-10 pre-built templates:

**Male-oriented (男频):**
1. 赘婿逆袭 — 入赘女婿身份反转
2. 兵王归来 — 退伍特种兵回归都市
3. 神医下山 — 隐世医术传人入世
4. 重生商战 — 重生回到商业起点
5. 退婚流 — 被退婚后逆袭打脸

**Female-oriented (女频):**
1. 闪婚总裁 — 闪婚对象是隐藏大佬
2. 重生复仇 — 重生回到被害之前
3. 替嫁甜宠 — 替姐出嫁遇到真爱
4. 穿书逆袭 — 穿越到小说里改写命运
5. 虐渣打脸 — 认清渣男后华丽蜕变
