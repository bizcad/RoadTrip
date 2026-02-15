---
name: git-push-autonomous
version: specs-v1.0
description: Autonomously stages, commits, and pushes repository changes after safety validation. Use when you need to push changes without manual approval, with automatic validation against exclusion rules and safety checks. Logs all decisions for audit trail and learning.
license: Internal use. RoadTrip project.
---

# Git-Push Autonomous Skill

## Overview

Safely and autonomously stages, commits, and pushes repository changes with zero user interaction. Designed for **trusted workflows** where files are pre-filtered and safety rules are well-established.

**Key capability**: Eliminates manual `git add`, `git commit`, `git push` ceremony while maintaining safety via automated validation.

## What This Skill Does

1. **Detects changes** in working tree
2. **Validates permissions** (auth-validator skill)
3. **Checks files against rules** (rules-engine skill)
4. **Generates commit message** from file changes (or uses custom message)
5. **Stages all validated files** (`git add`)
6. **Commits** with auto-generated or custom message
7. **Pushes to origin** on current branch
8. **Logs decision + result** (telemetry-logger skill)

**Result**: Fully committed and pushed, auditable via telemetry logs.

## Safety Mechanisms

### 1. Exclusion Rules (Pre-Configured)
Files matching patterns are **always blocked**:
- `.env`, `.secrets`, `credentials.json`
- `node_modules/`, `dist/`, `build/`
- `*.tmp`, `*.log`

### 2. Permission Validation
Calls `auth-validator` skill to verify git identity and permissions.

### 3. Audit Trail
Every decision logged with timestamp, decision, reason, files affected, and confidence scores.

### 4. Graceful Degradation
If a validator fails, blocks push rather than guessing.

## Examples

### Example 1: Simple Push
```
You: "Push my changes"

Orchestrator:
1. Check changes: src/main.rs, docs/README.md → Safe
2. Validate auth: ✓ Credentials valid
3. Validate rules: ✓ No blocked files
4. Generate message: "chore: update 2 files (+12, ~3, -0)"
5. Commit + push: Success
6. Log: Entry ID log-2026-02-05-abc123

Result: ✓ Done. Telemetry: log-2026-02-05-abc123
```

### Example 2: Blocked Files
```
You: "Push changes"

Orchestrator:
1. Check changes: src/main.rs, .env, config.yaml
2. Validate rules: ✗ .env is blocked

Result: ✗ BLOCKED. .env matches exclusion pattern.
        Remove it and retry.
        Telemetry: log-2026-02-05-xyz789
```

## Phase Roadmap

### Phase 1 (Now)
- ✅ Autonomous push with CLI-based git
- ✅ File exclusion rules
- ✅ Auth validation (basic)
- ✅ Telemetry logging
- Status: **Ready to test**

### Phase 2 (Next)
- Swap CLI → GitHub SDK
- Confidence-based gating
- Learning: Auto-tune rules from successful pushes

---

**Status**: Phase 1 MVP ready for testing
