# Edit Plan: Principles-and-Processes.md

**Task**: Apply 8 review suggestions to `docs/Principles-and-Processes.md`
**Date**: 2026-02-06
**File**: `G:\repos\AI\RoadTrip\docs\Principles-and-Processes.md`
**User decisions**: orchestrator = `skill_orchestrator`, commits = Conventional Commits

---

## Context

Claude reviewed `docs/Principles-and-Processes.md` and identified 8 suggestions. The user provided reasoning for each, resulting in these agreed edits:

| # | Edit | User's Reasoning |
|---|------|-----------------|
| 1 | Reframe Principle #4 (Idempotency) | "Artifacts are the point of software engineering" |
| 2 | Add Principle #7 (Error Handling) | "'Block in doubt' is a trap for autonomy" |
| 3 | Generalize tool references | "Modularity and replaceability — no lock-in" |
| 4 | De-duplicate Code Organization | "These should be examples, de-dup is fine" |
| 5 | Add orchestrator to Module table | "Orchestrator is essential — should be generic, not hardcoded" |
| 6 | Add false positive metric | "Necessary for the learning process" |
| 7 | Adopt Conventional Commits | User chose formal over loose examples |
| 8 | Add workflows/ to docs | "Reproducible 1-button clicks for commit boundaries" |

---

## Edits (8 changes, in document order)

### Edit 1: Reframe Principle #4 — Idempotency (lines 72-78)

**Why**: Artifacts and side effects are the point. Evaluation skills are pure; execution skills produce artifacts.

**Old**:
```markdown
### 4. Idempotency & Side-Effect Freedom

**Skills must be:**
- **Idempotent**: Running twice = same effect as running once (no mutations)
- **Side-effect free**: No persistent state, no global modifications
- **Deterministic**: Same input → identical output
- **Testable**: Can run in CI/CD loops without locks or cleanup
```

**New**:
```markdown
### 4. Idempotent Evaluation, Intentional Artifacts

**Evaluation skills** (rules-engine, auth-validator) are pure functions:
- **Idempotent**: Running twice = same result (no mutations)
- **Deterministic**: Same input → identical output
- **Testable**: Can run in CI/CD loops without locks or cleanup

**Execution skills** (telemetry-logger, orchestrator) produce intentional artifacts:
- Log files, commit history, push results are the *point* of the system
- Artifacts are append-only and auditable
- Execution is idempotent in *effect* (re-pushing the same commit is a no-op)

The distinction: evaluation functions have no side effects; execution functions have *deliberate, logged* side effects.
```

### Edit 2: Add Principle #7 — Error Handling & Resilience (after Principle #6)

**Why**: Autonomous agents need error handling, retry, and guardrails — not just "block in doubt."

**Insert after line 95 (end of Principle #6), before the `---`**:
```markdown
### 7. Error Handling & Resilience

**"Fail safely, recover gracefully, explain always."**

Autonomous agents must handle errors without human intervention:

- **Graceful degradation**: If a specialist crashes (not just returns FAIL), the orchestrator catches the exception, logs it, and falls back to a conservative decision
- **Retry with backoff**: Network-dependent operations (git ls-remote, git push) retry up to 3 times with exponential backoff before declaring failure
- **Guardrails over gates**: Prefer warning + logging over hard blocking when the risk is low. Reserve hard blocks for security (credentials, secrets)
- **Structured error reporting**: Every failure includes: what failed, why, what was attempted, what the operator should do next
- **Exit codes map to recovery actions**: Each error code has a documented recovery path (see `skills/git-push-autonomous/decision-tree.md`)

**Error hierarchy** (most to least severe):
1. **Security violation** → Hard block, no retry, log immediately
2. **Auth failure** → Block, suggest credential fix, no retry
3. **Rules violation** → Block, list offending files, suggest removal
4. **Network timeout** → Retry with backoff, then block with explanation
5. **Telemetry failure** → Warn, continue (non-critical)
```

### Edit 3: Generalize tool references (lines 201-213)

**Why**: No lock-in to specific AI tools.

**Old**: `2. CODE GENERATION (Claude Does This)` / `3. CODE REVIEW (Copilot Does This)`
**New**: `2. CODE GENERATION (LLM Code Agent)` / `3. CODE REVIEW (Review Agent)` with `*Current tooling: X — replaceable*` notes

### Edit 4: De-duplicate Code Organization (lines 144-167)

**Why**: Section appears twice. Replace brief version with cross-link to comprehensive version.

**Old**: Full directory tree under "Software Engineering Standards"
**New**: `*See [Code Organization](#code-organization) section for full directory structure.*`

### Edit 5: Add orchestrator to Module Responsibilities table (line 289)

**Why**: Orchestrator is a first-class module.

**Add row**: `| skill_orchestrator.py | Workflow orchestration | Calls specialists in sequence; manages exit codes; produces artifacts |`

### Edit 6: Add false positive metric (after line 464)

**Why**: Feeds the Phase 2 learning loop.

**Add row**: `| False positive rate | <5% of pushes blocked incorrectly | 📊 Tracking starts Phase 1b |`

### Edit 7: Adopt Conventional Commits (lines 411-434)

**Why**: Formal spec enables auto-changelogs and aligns with `commit_message.py`.

**Old**: Three example blocks (feat, fix, docs)
**New**: Table with 6 types (feat, fix, docs, refactor, test, chore) + link to conventionalcommits.org

### Edit 8: Add workflows/ to Documentation Files + update footer

**Why**: `workflows/` captures reproducible process artifacts.

**Add rows**: `workflows/plan.md` and `workflows/NNN-name/plan.md`
**Add paragraph**: Explains workflows/ as commit boundaries
**Update footer**: `GitHub Copilot + Claude 4.6` → `LLM code agents (currently Claude Code + GitHub Copilot)`
