---
name: commit-message
version: v1.0
last_updated: 2026-02-07
author: Phase 1b Implementation
document_type: SKILL_DESIGN_SPECIFICATION
---

# commit-message Skill Design & Tier Strategy

## Problem: Balancing Quality vs. Cost

Autonomous commit messages need to be:
1. **Semantically clear** (developers understand what changed)
2. **Consistent** (follows Conventional Commits format)
3. **Cost-effective** (not every commit needs an LLM call)

### Option A: Always Deterministic (Tier 1 Only)

```python
if single_file and file.endswith(".md"):
    return "docs: update README"
else:
    return "feat: update module"
```

**Pros**: Cheap ($0), fast, deterministic  
**Cons**: Low quality, generic, developers often edit the message

### Option B: Always AI (LLM Every Time)

```python
return await claude.generate_message(diff)  # Every commit
```

**Pros**: High quality  
**Cons**: Expensive ($0.01-0.05 per commit), slow, overkill for simple changes

### ✅ **Option C: Tiered Approach (CHOSEN)**

```python
# Tier 1: Fast heuristics
confidence, message = tier1_deterministic(files, diff)

if confidence >= 0.85:
    return (message, cost=$0)  # 90% of commits

# Tier 2: LLM fallback
confidence, message = await tier2_llm(diff)
if confidence >= 0.75:
    return (message, cost=$0.001-0.01)  # ~10% of commits

# Tier 3: User override
if user_message:
    return (user_message, cost=$0)  # Always available
```

**Rationale**:
- **Cost-effective**: ~$0/commit (90% Tier 1)
- **Quality**: High for complex cases (Tier 2 for hard ones)
- **User control**: Can always override
- **Measurable**: Track confidence, cost, user edits
- **Scalable**: Easy to improve Tier 1 patterns over time

---

## Design Decision 1: Confidence Threshold (0.85)

### Why Not 0.95?
```
Tier 1 accuracy: Heuristics right 95% of time
BUT: When heuristic wrong, very wrong (generic message)
Trade-off: Use 0.85 threshold to catch edge cases

0.95 threshold → Tier 2 for 5% (correct, but expensive)
0.85 threshold → Tier 2 for 15% (catches edge cases, reasonable cost)
0.75 threshold → Tier 2 for 25% (too expensive, diminishing return)
```

**Decision**: 0.85 balances cost vs. quality. Target: 90% Tier 1, 10% Tier 2.

---

## Design Decision 2: Deterministic Patterns (Tier 1)

What makes a good heuristic?

### Pattern 1: Single File
```
File: docs/README.md
Confidence: 0.95
Pattern: "docs: {action from diff}"

Why high confidence?
- Single file = single concern
- .md file = documentation
- Action obvious from diff (add/update/remove section)
```

### Pattern 2: Multiple Files, Same Directory
```
Files: src/auth.py, src/models.py, src/validator.py
Confidence: 0.88
Pattern: "feat: {subcategory from file names}"

Why 0.88?
- All in src/ = feature addition
- Multiple related files = coherent change
- But can't infer exact subcategory from names alone
```

### Pattern 3: Mixed Directories
```
Files: src/auth.py, tests/test_auth.py, docs/API.md
Confidence: 0.60
Pattern: "chore: update multiple modules"

Why low confidence?
- Different directories = different concerns
- Can't summarize without understanding full diff
- Generic fallback until we read diff more deeply
```

---

## Design Decision 3: Why Conventional Commits?

### Option A: Free-Form Messages
```
"updated the thing"
"fixed bug"
"added new stuff"
```
**Problem**: Non-standardized, hard to parse for automation

### Option B: Custom Format
```
[COMPONENT] ACTION
```
**Problem**: Proprietary, developers must learn

### ✅ **Option C: Conventional Commits (CHOSEN)**
```
feat(auth): implement 4-layer authorization
fix(cache): prevent stale entries
docs: update installation guide
```

**Rationale**:
- **Standard**: Recognized across projects, tools (commitlint, changeloggen)
- **Parseable**: Type + scope + subject
- **CLI generation**: Can auto-generate CHANGELOG from commits
- **Team familiar**: Most teams already use this

---

## Design Decision 4: File Extension Heuristics

Why are .md, .yml, .json treated as "docs"?

```
.md files:
  → Always documentation
  → No functional code
  → High confidence for "docs:" prefix

.py files in src/:
  → Feature code
  → Could be feat, fix, refactor
  → Need diff to distinguish
  → Medium confidence for "feat:"

.py files in tests/:
  → Test code
  → Pattern: "test: add test for X"
  → High confidence for "test:"

.json, .yml files:
  → Configuration or data
  → Usually "chore:" changes
  → Medium confidence
```

---

## Design Decision 5: Tier 2 Model Choice

Why Claude Sonnet instead of GPT-4?

### Option A: Claude 3.5 Sonnet
```
Cost: $0.003 input, $0.015 output
Speed: Fast (1-2 sec)
Quality: Excellent (matches GPT-4 on most tasks)
Availability: Available globally
```

### Option B: GPT-4 Turbo
```
Cost: $0.01 input, $0.03 output
Speed: Fast
Quality: Excellent (best in class)
Availability: Same
Drawback: 3x cost for marginal quality gain
```

### ✅ **Option C: Claude 3.5 Sonnet (CHOSEN)**

**Rationale**:
- **Cost**: 3x cheaper for commit messages (marginal quality gain not worth it)
- **Quality**: Excellent at understanding diffs
- **Speed**: Fast enough for interactive use
- **Precedent**: DotNetSkills uses Sonnet; aligns with org standards

**Fallback**: If Sonnet hits rate limits, fall back to Tide 1 with confidence reduction.

---

## Design Decision 6: Confidence Scoring

How to score Tier 1?

```python
# Option A: Binary (0 or 1)
if single_file:
    confidence = 1.0
else:
    confidence = 0.0
# Problem: No nuance, can't compare approaches

# Option B: Percentile (0-100 scale)
confidence = (1.0 if single_file else 0.0) \
           + (0.1 if same_directory else 0.0) \
           + (0.05 if < 5 files else 0.0)
# Problem: Arbitrary weights, hard to justify

# ✅ Option C: Explicit accuracy rate (CHOSEN)
# Based on historical data:
pattern_match = "single .md file"
historical_accuracy = 0.95  # This pattern right 95% of time
confidence = historical_accuracy
```

**Rationale**:
- **Data-driven**: Confidence = measured accuracy on training data
- **Interpretable**: "0.95 means this pattern works 95% of time"
- **Improvable**: Collect user edits, retrain in Phase 2

---

## Design Decision 7: Cost Tracking Structure

What to log for Tier 2 calls?

```json
{
  "timestamp": "ISO-8601",
  "approach": "tier2",
  "model": "claude-3-5-sonnet-20241022",
  "tokens": {
    "input": 342,
    "output": 45,
    "total": 387
  },
  "cost_usd": 0.00582,
  "confidence": 0.96,
  "message": "feat: add authorization validator skill",
  "user_edited": false  # Did user change this message?
}
```

**Why?**:
- **Tokens**: Understand what consumes cost
- **Confidence**: Track which Tier 2 calls were "right" vs. "user edited"
- **User edits**: Learning signal for Phase 2 improvements
- **Timestamp**: Trend analysis (peak usage times, cost curves)

---

## Tier 1: File Categorization Algorithm

```
INPUT: list of file paths

STEP 1: Extract Metadata
  FOR EACH file:
    extension = file.split('.')[-1]
    directory = file.split('/')[0]
    Add to (extension, directory) buckets

STEP 2: Determine Primary Category
  IF all files same directory:
    category = that directory
    confidence = 0.90
  
  ELSE IF all files same extension:
    category = extension_to_category(extension)
    confidence = 0.b85
  
  ELSE:
    category = "mixed"
    confidence = 0.60

STEP 3: Generate Message
  IF category == "md":
    verb = parse_action_verb(diff)  # "add", "update", "remove"
    message = f"docs: {verb} documentation"
    confidence = min(0.95, confidence)
  
  ELSE IF category == "src":
    type_from_diff = infer_change_type(diff)  # "feature", "bug", "refactor"
    message = f"{type_from_diff}: {summary_from_files(files)}"
    confidence = min(0.90, confidence)
  
  ELSE IF category == "tests":
    message = f"test: add test coverage"
    confidence = min(0.92, confidence)
  
  ELSE:
    message = f"chore: update {category}"
    confidence = min(0.75, confidence)

RETURN (message, confidence)
```

---

## When Tier 1 Fails

Scenarios where Tier 1 is < 0.85:

1. **Mixed categories + many files**
   ```
   Files: src/auth.py, tests/test_auth.py, docs/AUTH.md
   Confidence: 0.60 (can't infer intent without reading)
   → Tier 2 needed
   ```

2. **Refactoring across multiple modules**
   ```
   Files: src/utils.py, src/helpers.py, tests/utils_test.py
   Confidence: 0.70 (could be refactor or multiple features)
   → Tier 2 needed to understand intent
   ```

3. **Large changeset (> 10 files)**
   ```
   Files: [dozen files across multiple dirs]
   Confidence: 0.65 (too much to summarize)
   → Tier 2 to identify common theme
   ```

---

## Phase 2: Learning Loop

Track usage to improve Tier 1:

```python
# Phase 1b: Hardcoded patterns
if file_count == 1 and file.endswith(".md"):
    confidence = 0.95

# Phase 2: Learned patterns
# Analyze: Did users accept/edit this message?
# If 98% accepted → increase confidence to 0.98
# If 60% accepted → decrease to 0.70, move more to Tier 2
```

**Metrics to collect**:
- Tier 1 accuracy (% users don't edit)
- Tier 2 quality (% users accept LLM message)
- Cost trends (total $ per week)
- User edits (which patterns need improvement)

---

## Success Criteria (Phase 1b MVP)

- ✅ 90% of commits use Tier 1 ($0)
- ✅ 10% use Tier 2 (~$0.001-0.01 each)
- ✅ Average cost < $0.01 per commit
- ✅ All Tier 1 tests pass
- ✅ All Tier 2 tests pass (mocked LLM)
- ✅ Cost tracking accurate and complete
- ✅ Ready for orchestrator integration
