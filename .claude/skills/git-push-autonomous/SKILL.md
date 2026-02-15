---
name: git-push-autonomous
version: specs-v1.0
description: Autonomously stages, commits, and pushes repository changes after safety validation. Use when you need to push changes without manual approval, with automatic validation against exclusion rules and safety checks. Logs all decisions for audit trail and learning. Not for sensitive data review or code approval—safety rules must be pre-configured, and operator maintains oversight via telemetry logs.
license: Internal use. RoadTrip project.
---

# Git-Push Autonomous Skill

## Overview

Safely and autonomously stages, commits, and pushes repository changes with zero user interaction. Designed for **trusted workflows** where files are pre-filtered and safety rules are well-established.

**Key capability**: Eliminates manual `git add`, `git commit`, `git push` ceremony while maintaining safety via automated validation.

**Not a replacement for**: Code review, security scanning, testing—those are separate skills/workflows that can run pre- or post-push.

---

## When to Use This Skill

✅ You want to push changes without typing git commands  
✅ You have exclusion rules configured (what files are safe)  
✅ You trust the auto-generated commit message  
✅ You want full audit trail of every push  
✅ You're building an autonomous multi-agent workflow  

❌ You need human review before pushing  
❌ You're pushing sensitive data  
❌ Safety rules aren't configured yet  
❌ You're learning git (this skill hides the details)  

---

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

---

## Inputs (How to Call This Skill)

When Claude encounters a context that needs to push changes, invoke with:

### Optional: Custom Commit Message
```
"Push changes with message: 'feat: add user authentication'"
```
If omitted, skill auto-generates from file changes.

### Optional: Dry-Run Mode
```
"Dry run: show what would be pushed without executing"
```
Useful to preview changes before committing.

### Optional: Force Mode (Future)
```
"Push even if rules engine blocks some files"
```
Currently not supported; will be added in Phase 2.

---

## Workflow

### Normal Flow (Most Common)
```
You: "I've made changes; push them"
Skill: Validates + commits + pushes → "Done. See telemetry log [ID]"
```

### Dry-Run Flow
```
You: "Dry run: show commit message without pushing"
Skill: Analyzes staged changes → "Would commit with message: 'chore: update 3 files..."
```

### Blocked Flow
```
You: "Push changes"
Skill: Detects `.env` file in changes → "BLOCKED: excluded files detected. Check telemetry log [ID]"
```

---

## Safety Mechanisms

### 1. Exclusion Rules (Pre-Configured)
Files matching patterns are **always blocked**:
- `.env`, `.secrets`, `credentials.json`
- `node_modules/`, `dist/`, `build/`
- `*.tmp`, `*.log`
- Any pattern in `safety-rules.md`

See [safety-rules.md](safety-rules.md) for full list.

### 2. Permission Validation
Calls `auth-validator` skill:
- Verifies git identity configured
- Checks permissions on origin remote
- Confirms push target branch exists (future)

### 3. Audit Trail
Every decision logged:
- Timestamp, decision (APPROVED/BLOCKED), reason
- Files affected, commit hash (if pushed)
- Confidence scores per validation
- Operator can analyze patterns

### 4. Graceful Degradation
If a validator fails (e.g., auth service down):
- Blocks push rather than guessing
- Logs exact failure reason
- Clear message to operator: "Fix X and retry"

---

## Configuration

### Safety Rules
**File**: `safety-rules.md`  
Defines exclusion patterns, validation logic, file types.

### Commit Message Template
**File**: `config/commit-templates.yaml`  
Optional custom template for auto-generated messages.

### Confidence Thresholds
**File**: `config/confidence-thresholds.yaml`  
When to block based on confidence scores (Phase 2).

### Example Config
```yaml
# config/exclusions.yaml
blocked_files:
  - ".env"
  - ".secrets"
  - "*.key"
  - "node_modules/"
  - "dist/"
blocked_patterns:
  - "^credentials/.*"
  - "tmp.*\.log$"
  
max_file_size_mb: 50
require_commit_message: true  # Fail if auto-gen fails
```

---

## Outputs

### Success
```
✓ Push complete
  Commit: abc123def456
  Branch: main
  Files: 5 (+3, ~2, -0)
  Telemetry ID: log-2026-02-05-14-23-45
```

### Blocked
```
✗ BLOCKED: Excluded files detected
  Reason: .env matches blocked pattern
  Telemetry ID: log-2026-02-05-14-23-40
  Action: Remove blocked files and retry
```

### Error
```
✗ ERROR: git push failed
  Code: 6
  Stderr: "rejected by hook"
  Telemetry ID: log-2026-02-05-14-23-35
  Action: Check branch protection rules
```

---

## Telemetry & Learning

Every push (success or failure) creates a **decision log**:

```json
{
  "timestamp": "2026-02-05T14:23:45Z",
  "orchestrator": "git-push-autonomous",
  "decision": "APPROVED",
  "files": ["src/main.rs", "Cargo.toml"],
  "auth_validator": {
    "decision": "PASS",
    "confidence": 0.99
  },
  "rules_engine": {
    "decision": "PASS",
    "confidence": 0.95,
    "blocked_files": []
  },
  "commit_hash": "abc123def456",
  "branch": "main",
  "result": "SUCCESS"
}
```

**Phase 2 uses this data to:**
- Identify safe file patterns (increase confidence)
- Detect false positives in rules
- Tune decision thresholds
- Auto-suggest rule improvements

---

## Examples

### Example 1: Simple Push
```
You: "Push my changes"

Orchestrator:
1. Check changes: src/main.rs, docs/README.md → Safe
2. Validate auth: ✓ Credentials valid
3. Validate rules: ✓ No blocked files
4. Generate message: "chore: update 2 files (+12, ~3, -0)"
5. Commit + push: Success on main
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

### Example 3: Auth Failure
```
You: "Push changes"

Orchestrator:
1. Check changes: ✓ Valid files
2. Validate auth: ✗ Git credentials not configured

Result: ✗ ERROR. No git credentials found.
        Run: git config user.name/user.email
        Telemetry: log-2026-02-05-def456
```

---

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | None |
| 2 | Git not installed | Install git |
| 3 | Not a git repo | cd to git repo root |
| 4 | Auth validation failed | Check credentials |
| 5 | Rules validation failed | Review blocked files |
| 6 | Commit failed | Check git config |
| 7 | Push failed | Check branch/permissions |
| 8 | Telemetry failed | Check logging service (non-critical) |

---

## Phase Roadmap

### Phase 1 (Now)
- ✅ Autonomous push with CLI-based git
- ✅ File exclusion rules
- ✅ Auth validation (basic)
- ✅ Telemetry logging
- Status: **Ready to test**

### Phase 2 (Next)
- Swap CLI → GitHub SDK (better event visibility)
- Confidence-based gating
- Integration with Aspire (auth backend)
- Integration with QuestionManager (telemetry)
- Learning: Auto-tune rules from successful pushes

### Phase 3 (Future)
- GitHub API direct access
- Parallel validation
- Multi-orchestrator coordination
- Security scanning integration
- Code review pre-approval

---

## Limitations

- **Single-branch**: Always pushes to current branch (can't retarget)
- **All-or-nothing**: Either all files push or none (no partial pushes yet)
- **Auto-messages only**: Can't customize commit structure (only message)
- **No hook support**: Can't integrate with git hooks (yet)
- **No signing**: No GPG commit signing (future)

---

## Security Considerations

✓ Never auto-pushes secrets (exclusion rules)  
✓ Validates auth before modifying repo  
✓ Logs every decision for audit  
✓ Fails safely (blocks rather than guesses)  

⚠️ Assumes safety rules are well-maintained  
⚠️ Assumes exclusion patterns cover real secrets  
⚠️ Does not scan for secret patterns (future feature)  

---

## Troubleshooting

**"BLOCKED: .env matches excluded pattern"**
→ You tried to push a `.env` file. Remove it, add to `.gitignore`, and retry.

**"ERROR: git push failed / rejected by hook"**
→ A git hook on the server rejected the push. Check branch protection rules or contact repo admin.

**"ERROR: Not a git repository"**
→ You're not in a git repo. Run from the root of your repo.

**"ERROR: No changes to commit"**
→ Working tree is clean. Make changes first.

---

## Related Skills

- **rules-engine**: Evaluates file patterns against safety rules
- **auth-validator**: Checks git credentials and permissions
- **telemetry-logger**: Records all decisions for learning
- **code-review-orchestrator** (future): Reviews code pre/post-push
- **test-runner-orchestrator** (future): Runs tests before pushing

---

## See Also

- [CLAUDE.md](CLAUDE.md) — Decision logic and reasoning
- [safety-rules.md](safety-rules.md) — Detailed exclusion rules
- [decision-tree.md](decision-tree.md) — Step-by-step walkthrough
- [examples.md](examples.md) — More usage scenarios

---

**Last updated**: 2026-02-05  
**Version**: 1.0  
**Status**: Ready for Phase 1 testing
