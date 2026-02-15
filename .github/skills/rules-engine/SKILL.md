---
name: rules-engine
version: specs-v1.0
description: Evaluates files against safety and validation rules. Checks for exclusions, size limits, and blocked patterns. Use when you need to determine if files are safe to commit/push.
license: Internal use. RoadTrip project.
---

# Rules Engine Skill

## Overview

Validates files against pre-configured safety rules before operations like commits and pushes.

## What It Checks

### Phase 1 (Now)
- File exclusions (blocklist + patterns)
- File size limits (< 50 MB default)
- Blocked path patterns

## Input

```json
{
  "files": ["path/to/file1", "path/to/file2"],
  "context": "pre-commit|pre-push",
  "repo_root": "/path/to/repo"
}
```

## Output

```json
{
  "decision": "APPROVE|BLOCK_ALL|BLOCK_SOME",
  "approved_files": ["file1", "file2"],
  "blocked_files": [{"path": "file3", "reason": "pattern match"}],
  "confidence": 0.95,
  "warnings": []
}
```

## Configuration

Reads: `config/rules-config.yaml` and `safety-rules.md`

```yaml
blocked_files:
  - ".env"
  - ".secrets"
blocked_patterns:
  - "^secrets/.*"
  - "node_modules/.*"
max_file_size_mb: 50
```

## Phase 1 Logic

```
For each file:
  1. Check explicit blocklist → blocked?
  2. Check patterns (regex) → blocked?
  3. Check size → warning?
  4. Result: PASS | BLOCK | WARN

Aggregate:
  - If any blocked: BLOCK_ALL
  - If any warning: APPROVE_WITH_WARN
  - Otherwise: APPROVE
```

---

**Status**: Phase 1 MVP
