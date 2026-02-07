# Git-Push Autonomous: Decision Logic & Reasoning
**How the Orchestrator Makes Safe Decisions**
**Specs Version**: v1.0

---

## Purpose

This document explains the **reasoning process** for the git-push-autonomous skill. It's not a tutorial (see SKILL.md) or reference (see decision-tree.md)—it's the mental model for how autonomous decisions happen.

---

## The Core Decision Question

**"Is it safe to automatically stage, commit, and push these changes?"**

This breaks into three sub-questions:

1. **Am I authorized?** → `auth-validator` skill
2. **Are the files safe?** → `rules-engine` skill  
3. **Should I record this?** → `telemetry-logger` skill

Only if all three say YES → proceed to git operations.

---

## Decision Flow (High Level)

```
┌─────────────────────────┐
│  User calls git-push    │
│  (or workflow invokes)  │
└────────────┬────────────┘
             │
             ▼
    ┌─────────────────┐
    │ Stage Changes?  │ ← Analyze working tree
    │ Any files?      │
    └────────┬────────┘
             │ No → Exit (no changes)
             │ Yes ↓
    ┌─────────────────────────────────┐
    │ Call auth-validator skill       │ ← Check credentials, permissions
    │ "Am I authorized to push?"      │
    └────────┬────────────────────────┘
             │ FAIL → Log reason + Exit
             │ PASS ↓
    ┌─────────────────────────────────┐
    │ Call rules-engine skill         │ ← Check file patterns
    │ "Do files pass safety rules?"   │
    └────────┬────────────────────────┘
             │ FAIL → Log reason + Exit
             │ BLOCKED FILES → Log + skip (future: partial push)
             │ PASS ↓
    ┌─────────────────────────────────┐
    │ Generate commit message         │ ← Auto or provided
    │ (from staged files)             │
    └────────┬────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────┐
    │ Git add + commit                │ ← Actually stage & commit
    └────────┬────────────────────────┘
             │ FAIL → Log error + Exit
             │ SUCCESS ↓
    ┌─────────────────────────────────┐
    │ Git push origin <branch>        │ ← Push to remote
    └────────┬────────────────────────┘
             │ FAIL → Log error + Exit
             │ SUCCESS ↓
    ┌─────────────────────────────────┐
    │ Call telemetry-logger skill     │ ← Record full decision + result
    │ "Log this success"              │
    └────────┬────────────────────────┘
             │
             ▼
      ┌───────────────┐
      │  Exit SUCCESS │
      └───────────────┘
```

---

## Key Design Decisions

### 1. **Fail Early, Fail Often**

Check permissions *before* modifying working tree. If auth-validator says NO, we haven't touched git yet.

- Reason: Minimize side effects when decision uncertain
- Consequence: User sees rejection before anything changes
- Feedback: Clear log explains why decision rejected

### 2. **Rules Are Data, Not Code**

File exclusion rules live in `safety-rules.md` + config files. Skill reads them, doesn't embed them.

- Reason: SOLID Open/Closed; easy to tune without editing skill
- Consequence: Phase 2 can auto-adjust thresholds
- Feedback: Rules become learning signal

### 3. **Confidence Scoring (Future)**

Today: Pass/Fail binary. Tomorrow: confidence 0-1 per check.

```json
{
  "auth_validator": { "decision": "PASS", "confidence": 0.99 },
  "rules_engine": { "decision": "PASS", "confidence": 0.87 },
  "overall_confidence": 0.856  // geometric mean
}
```

If overall < threshold (0.90), block and request operator review.

### 4. **Audit Trail Over Speed**

Every decision logged with full context. Phase 2 learning depends on this.

- Reason: Autonomy means we can't ask for help later; must prove we decided wisely
- Consequence: Slightly slower (I/O for logging) but fully traceable
- Feedback: Operator can review logs, adjust if patterns emerge

### 5. **Graceful Degradation**

If a specialist skill fails (e.g., auth-validator service down), block push rather than guess.

- Reason: Better to miss a legitimate push than accidentally commit secrets
- Consequence: Operator must fix dependency + retry
- Feedback: Clear logs show what to fix

---

## Specialist Skill Contracts

### Auth-Validator Skill

**What I ask it:**
```
"Can I push changes to repo <repo-name> on branch <branch>?"
```

**What it returns:**
```json
{
  "decision": "PASS" | "FAIL",
  "reason": "string (explain why)",
  "confidence": 0.0-1.0,
  "permissions_checked": [ "push", "commit", ... ]
}
```

**If FAIL**: Orchestrator exits with message to owner: "Check your credentials or branch permissions"

### Rules-Engine Skill

**What I ask it:**
```
"Do these files pass safety rules?"
files: ["src/main.rs", ".env", "docs/README.md"]
context: "pre-commit-check"
```

**What it returns:**
```json
{
  "decision": "APPROVE" | "BLOCK_ALL" | "BLOCK_SOME",
  "blocked_files": [
    { "path": ".env", "reason": "excluded (secrets)" }
  ],
  "approved_files": ["src/main.rs", "docs/README.md"],
  "confidence": 0.95
}
```

**If BLOCK_ALL**: Exit with reason  
**If BLOCK_SOME** (future): Log warning, offer to push only approved files  
**If APPROVE**: Continue to next step

### Telemetry-Logger Skill

**What I ask it:**
```
"Log this decision and its result"
decision_log: { <full decision structure> }
```

**What it returns:**
```json
{
  "status": "RECORDED",
  "log_entry_id": "uuid",
  "reason": "string if failed"
}
```

**On failure**: Log warning but don't block push (non-critical)

---

## Confidence Thresholds (Phase 2 Tuning)

Today: Binary (pass/fail). Tomorrow: Confidence-based gating.

**Proposed thresholds** (can be configured):

```yaml
# config/confidence-thresholds.yaml
overall_confidence_minimum: 0.90
auth_validator_minimum: 0.95  # Auth failures are unforgivable
rules_engine_minimum: 0.85    # Rules can improve over time
telemetry_minimum: 0.70       # Logging failures aren't critical
```

**Decision logic** (Phase 2):
```
if overall_confidence >= threshold → PUSH
else → BLOCK + log reason + notify operator
```

---

## Handling Ambiguity

**When is a file blocked?**

Rules-engine checks patterns:
1. Explicit blocklist: `.env`, `node_modules/`, `*.tmp`
2. Pattern match: `**/secrets/*`, `dist/`, `build/`
3. Size threshold: > 50MB flagged (future: configurable)
4. Scan results: If contains secret patterns (future: integration with tool)

**When in doubt**: Block. Operator can:
- Override (manual review + approval)
- Update rules (future: auto-learning)

---

## Why This Approach Scales to Multi-Agent

This orchestrator is designed to **compose** with other orchestrators:

- **Separate orchestrator for code review?** Call it post-push
- **Separate orchestrator for testing?** Call it pre-commit
- **Each is independent** but shares telemetry + rules

```
    git-push-autonomous
         ↓ calls
    ┌────┬────┬────┐
    ↓    ↓    ↓    ↓
  code-review-orchestrator
  test-runner-orchestrator  
  security-scan-orchestrator
```

All log to same telemetry. All read same rules (SOLID Open/Closed).

---

## Meta: How to Improve This CLAUDE.md

This document should evolve as we learn:

1. **After Phase 1 testing**: What decisions surprised you? Add to "ambiguity" section
2. **After Phase 2 threshold tuning**: What thresholds worked? Document here
3. **After real-world pushes**: What patterns emerged in telemetry? Update confidence logic

Each iteration: **Plan → Code → Test → Adjust This Doc**.

---

## Relationship to SKILL.md

- **This file** (CLAUDE.md): "How do I reason about what to do?"
- **SKILL.md**: "When should I be called? What do I do?"
- **decision-tree.md**: Step-by-step walkthrough
- **safety-rules.md**: Concrete rules (data)
- **config/**: Configuration values

**They're separate but connected**: SKILL.md describes the interface; CLAUDE.md explains the reasoning inside.

---

**Last updated**: 2026-02-05  
**Version**: 1.0  
**Status**: Ready for implementation + testing
