---
name: commit-message
version: specs-v1.0
description: Generates semantic commit messages using cost-optimized Tier 1→2→3 approach. Tier 1 (deterministic, $0) handles 90% of commits. Tier 2 (LLM fallback, ~$0.001-0.01) for complex cases. Tier 3 (user override). Use when you need high-quality, consistent commit messages without excess API costs.
license: Internal use. RoadTrip project.
---

# Commit Message Skill

## Overview

Generates semantic commit messages using a **cost-optimized, confidence-based approach**. Most commits use deterministic patterns (Tier 1, $0). Complex cases fall back to LLM (Tier 2, cost-tracked). Users can always override (Tier 3).

## The Tier 1→2→3 Strategy

Why three tiers instead of one approach?

**Tier 1 (Deterministic, $0)**: 
- Heuristics based on file extensions, directories, number of files
- Examples: "feat: add auth validation" (2 files in src/), "docs: update README" (1 .md file)
- Confidence: High (0.85-0.99) for most commits
- Cost: $0 (no API calls)
- Success Rate: ~90% of commits (target)

**Tier 2 (LLM Fallback, ~$0.001-$0.01)**:
- Invoked when Tier 1 confidence < 0.85
- Claude 3.5 Sonnet reads diff and generates message
- Examples: Complex refactoring, cross-cutting changes
- Confidence: Very high (0.95-0.99) after LLM review
- Cost: Pay-per-call (~$0.001-0.01 typical)
- Success Rate: ~10% of commits (target)

**Tier 3 (User Override, $0)**:
- User provides explicit message via `-Message "feat: ..."` parameter
- Bypasses Tier 1 & 2
- Confidence: 1.0 (user knows best)
- Cost: $0

## Input

```json
{
  "staged_files": [
    "src/auth.py",
    "src/models.py",
    "tests/test_auth.py"
  ],
  "diff": "--- a/src/auth.py\n+++ b/src/auth.py\n@@ -1,3 +1,10 @@\n...",
  "strategy": "hybrid",
  "confidence_threshold": 0.85,
  "user_message": null
}
```

## Output

```json
{
  "message": "feat: implement 4-layer authorization\n\nAdds AuthValidator skill with group/role/tool/resource checks.\nSupports MFA validation and branch-level access control.",
  "approach_used": "tier1",
  "confidence": 0.92,
  "cost_estimate": 0.0,
  "reasoning": "3 files in src/ (high-confidence pattern match); category = feat",
  "tier1_score": {
    "file_count": 3,
    "categories": ["src"],
    "single_category": true,
    "pattern_match": "feat: {action}",
    "confidence": 0.92
  },
  "cost_tracking": {
    "model": null,
    "tokens_input": 0,
    "tokens_output": 0,
    "cost_usd": 0.0
  }
}
```

## Configuration

Reads: `config/commit-strategy.yaml`

```yaml
commit_message:
  strategy: "hybrid"                   # hybrid|deterministic|ai
  cost_tracking: true
  
  # Tier 1→2 Switch
  confidence_threshold: 0.85           # If Tier 1 confidence < 0.85, use Tier 2
  min_confidence_accept: 0.75          # If Tier 2 < 0.75, request user input
  
  # Tier 1 Patterns (deterministic)
  tier1_rules:
    single_file:
      extensions: [".md", ".txt", ".yml", ".yaml", ".json"]
      pattern: "docs: {action}"
      confidence: 0.95
    
    src_only:
      paths: ["src/**"]
      pattern: "feat: {action}"
      confidence: 0.90
    
    test_only:
      paths: ["tests/**"]
      pattern: "test: {action}"
      confidence: 0.92
    
    multiple_files_same_category:
      min_files: 2
      max_files: 10
      pattern: "{category}: {action}"
      confidence: 0.88
  
  # Tier 2 LLM Config
  tier2_model: "claude-3-5-sonnet-20241022"
  tier2_max_tokens: 500
  tier2_temperature: 0.0              # Deterministic (no randomness)
  
  # Tier 3 Override
  allow_user_override: true            # -Message parameter accepted

# Cost tracking & reporting
cost_tracking:
  enabled: true
  track_per_call: true                # Log each Tier 2 call
  report_frequency: "daily"
  alert_threshold_usd: 10.0           # Alert if daily > $10

# Conventional Commits (for message formatting)
conventional_commits:
  types: ["feat", "fix", "refactor", "docs", "test", "chore", "perf", "ci"]
  breaking_change_prefix: "BREAKING CHANGE:"
  footer_tokens: ["Co-authored-by:", "Fixes:", "Refs:"]
```

## Tier 1: Deterministic Logic

### Algorithm

```
INPUT: staged_files list, committed files with extensions/paths

STEP 1: Categorize Files
  FOR EACH file:
    ext = file extension
    dir = parent directory (src, tests, docs, etc.)
    IF all files in same category:
      category = that category
      single_category = true
    ELSE:
      category = "mixed"
      single_category = false

STEP 2: Calculate Confidence
  IF user_message provided:
    return TIER_3 (confidence 1.0)
  
  IF single_file:
    IF extension in ["md", "yml", "yaml", "json"]:
      confidence = 0.95
      verb = extract_action(diff)  # e.g., "update"
      message = f"docs: {verb} {filename}"
    ELSE IF in src/:
      confidence = 0.90
      verb = extract_action(diff)
      message = f"feat: {verb} module"

  ELSE IF single_category and file_count <= 10:
    confidence = 0.88  # Multiple related files
    subcategory = infer_subcategory(files, diff)
    message = f"feat: {subcategory}"

  ELSE IF file_count > 10:
    confidence = 0.70  # Too many files; ambiguous
    message = f"chore: bulk update"

  ELSE IF mixed categories:
    confidence = 0.60  # Mixed; very ambiguous
    message = "chore: update multiple modules"

STEP 3: Decision
  IF confidence >= confidence_threshold:
    return TIER_1 (message, confidence, cost=$0)
  ELSE:
    return TIER_2_NEEDED (reason="confidence < threshold")
```

### Examples

**Example 1: Single .md file**
```
staged_files: ["docs/README.md"]
diff: "- Missing section\n+ Added installation section"

Tier 1 Analysis:
  single_file = true
  extension = ".md"
  verb = "add" (inferred from diff)
  confidence = 0.95
  message = "docs: add installation section"

Result: TIER_1 ($0)
```

**Example 2: 3 files in src/**
```
staged_files: ["src/auth.py", "src/models.py", "tests/test_auth.py"]
  
Tier 1 Analysis:
  single_category? src + tests = mixed ❌
  confidence = 0.70 (mixed categories)
  < 0.85 threshold
  
Result: TIER_2_NEEDED (mixed categories)
```

**Example 3: Multiple src files, single change type**
```
staged_files: ["src/auth.py", "src/validator.py", "src/models.py"]

Tier 1 Analysis:
  category = "src"
  single_category = true
  file_count = 3
  diff type = "feature" (new functions added)
  confidence = 0.88
  >= 0.85 threshold ✅
  message = "feat: implement authorization layer"

Result: TIER_1 ($0)
```

## Tier 2: LLM Fallback

### Prompt Template

```
You are generating a git commit message using Conventional Commits format.

User has staged these files:
{staged_files_list}

The changes are:
{unified_diff}

Generate a concise, clear commit message in this format:
type(scope): subject

body (if needed)

Rules:
- Types: feat, fix, refactor, docs, test, chore, perf, ci
- Subject: imperative mood, no period
- Max 72 chars for subject line
- Body (optional): explain WHY not WHAT
- Keep it short (under 100 words total)

Generate ONLY the commit message, no explanations.
```

### When to Use Tier 2

- Confidence from Tier 1 < 0.85
- Mix of categories (src + docs + tests)
- Complex refactoring with multi-file changes
- User explicitly requests LLM

### Cost Tracking

Every Tier 2 call logged:
```json
{
  "timestamp": "2026-02-07T14:32:45Z",
  "approach": "tier2",
  "model": "claude-3-5-sonnet-20241022",
  "tokens": {
    "input": 342,
    "output": 45,
    "total": 387
  },
  "cost_usd": 0.00582,  # $0.015 per 1M input, $0.045 per 1M output
  "confidence": 0.96,
  "message": "feat: add authorization validator skill"
}
```

## Tier 3: User Override

```bash
# User provides explicit message
git-push-autonomous -Message "feat: critical security fix\n\nClosed: VULN-2026-001"

# Bypasses Tier 1 & 2, uses message directly
# Confidence: 1.0
# Cost: $0
```

## Test Cases (Phase 1b MVP)

### Tier 1 Tests (Deterministic)
- **Test 1.1**: Single .md file → TIER_1 (docs:)
- **Test 1.2**: Single .py file → TIER_1 (feat:)
- **Test 1.3**: 3 files all in src/ → TIER_1 (feat:)
- **Test 1.4**: Single file in tests/ → TIER_1 (test:)

### Tier 1 Edge Cases
- **Test 2.1**: 11 files (> threshold) → Tier 1 (lower confidence)
- **Test 2.2**: Mixed src + docs → insufficient confidence → TIER_2_NEEDED
- **Test 2.3**: Config file (yaml) → TIER_1 (chore:)

### Tier 2 Tests (LLM Fallback)
- **Test 3.1**: Complex diff, mixed files → TIER_2_NEEDED
- **Test 3.2**: LLM generates valid message → confidence 0.95+
- **Test 3.3**: LLM message meets 72-char limit

### Tier 3 Tests (User Override)
- **Test 4.1**: User provides message → TIER_3 (confidence 1.0)
- **Test 4.2**: User message overrides all tiers

### Cost Tracking Tests
- **Test 5.1**: Tier 1 call → cost_usd = 0.0
- **Test 5.2**: Tier 2 call → cost tracked with tokens
- **Test 5.3**: Multiple Tier 2 calls → costs aggregated

---

## Phase 2 Integration (Future)

- **Learning Loop**: Track which messages users accept/edit; retrain Tier 1 patterns
- **Multi-Language Support**: Translate conventional commits to different styles
- **AI Confidence Tuning**: Analyze patterns that frequently require Tier 2 → improve Tier 1

---

**Status**: Phase 1b MVP. Core logic: Tier 1 heuristics + Tier 2 LLM fallback + Tier 3 override.

**Dependencies**:
- `config/commit-strategy.yaml` (patterns)
- `anthropic` library (Tier 2 API calls)
- dataclasses (result serialization)

**Success Metric**: 90% Tier 1, 10% Tier 2, average cost < $0.01 per commit
