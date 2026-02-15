---
name: commit-message
version: specs-v1.0
description: Generates semantic commit messages using cost-optimized Tier 1→2→3 approach. Tier 1 (deterministic, $0) handles 90% of commits. Tier 2 (LLM fallback) for complex cases. Tier 3 (user override). Use when you need high-quality commit messages without excess costs.
license: Internal use. RoadTrip project.
---

# Commit Message Skill

## Overview

Generates semantic commit messages using a **cost-optimized, confidence-based approach**.

## The Tier 1→2→3 Strategy

**Tier 1 (Deterministic, $0)**: 
- Heuristics based on file extensions and directories
- Examples: "docs: update README" (1 .md file), "feat: add auth" (src files)
- Confidence: 0.85-0.99
- Cost: $0
- Coverage: ~90% of commits

**Tier 2 (LLM Fallback, ~$0.001-0.01)**:
- Invoked when Tier 1 confidence < 0.85
- Claude 3.5 Sonnet reads diff and generates message
- Confidence: 0.95-0.99
- Coverage: ~10% of commits

**Tier 3 (User Override, $0)**:
- User provides explicit message
- Confidence: 1.0

## Algorithm

```
INPUT: staged_files, diff, confidence_threshold=0.85

IF user_provided_message:
  return TIER_3 (confidence 1.0, cost $0)

IF single_file and extension in [.md, .txt, .yml]:
  confidence = 0.95
  return TIER_1 (docs: ..., cost $0)

IF all files in same_category and count <= 10:
  confidence = 0.88
  return TIER_1 (feat: ..., cost $0)

IF confidence < threshold:
  invoke LLM → return TIER_2 (tracked cost)

ELSE:
  return TIER_1 (cost $0)
```

## Success Metric

- 90% Tier 1 (deterministic, free)
- 10% Tier 2 (LLM, tracked)
- Average cost < $0.01 per commit

---

**Status**: Phase 1b MVP ready for testing
