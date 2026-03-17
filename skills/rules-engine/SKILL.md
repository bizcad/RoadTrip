---
name: rules-engine
description: Evaluates files against safety and validation rules. Use when you need to determine if files are safe to commit/push based on exclusion patterns, size limits, and content scanning. Reads rules from configuration files; extensible for Phase 2 security scanning.
license: Internal use. RoadTrip project.
metadata:
  version: "1.0.0"
  tags:
    - safety
    - validation
    - rules
    - exclusions
    - security
  examples:
    - "check if these files are safe to commit"
    - "validate files against safety rules"
    - "are these files allowed in git"
    - "scan files for secrets patterns"
    - "check exclusion rules"
  entry_point: src/skills/rules_engine.py
  runtime: python
  trust_level: verified
  # Update fingerprint: py src/skills/skill_scanner.py stamp
  fingerprint: "f84506eea2f53473"
---

# Rules Engine Skill

## Overview

Validates files against pre-configured safety rules before operations.

## What It Checks

### Phase 1 (Now)
- File exclusions (blocklist + patterns)
- File size limits
- File type restrictions (future)

### Phase 2 (Future)
- Content scanning (secrets detection)
- License compliance
- Code quality gates

## Input

```json
{
  "files": [ "path/to/file1", "path/to/file2" ],
  "context": "pre-commit|pre-push",
  "repo_root": "/path/to/repo"
}
```

## Output

```json
{
  "decision": "APPROVE|BLOCK_ALL|BLOCK_SOME",
  "approved_files": [ "file1", "file2" ],
  "blocked_files": [
    { "path": "file3", "reason": "pattern match" }
  ],
  "confidence": 0.0-1.0,
  "warnings": [ "large file detected" ]
}
```

## Configuration

Reads: `../git-push-autonomous/safety-rules.md` and `config/rules-config.yaml`

```yaml
blocked_files:
  - ".env"
  - ".secrets"
blocked_patterns:
  - "^secrets/.*"
  - "node_modules/.*"
max_file_size_mb: 50
allow_large_files_warn: true
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

## Phase 2 Integration (Placeholder)

- Content scanning for secrets (AWS keys, API tokens)
- License checking (copyright, GPL, etc.)
- Code quality gates (if integrated with linters)

---

**Status**: Phase 1 stub. Core logic: Apply file patterns and size checks.
