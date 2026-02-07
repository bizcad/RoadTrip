# Decision Tree: Step-by-Step Walkthrough

## Purpose

This document shows the **exact decision points** the skill encounters, in order, with explanations.

Use this to debug unexpected behavior or understand why a push was blocked.

---

## Decision Tree Flow

```
START: User calls git-push-autonomous
│
├─→ STEP 1: Check for changes
│   │
│   ├─→ No changes found?
│   │   └─→ EXIT: "No changes to commit"
│   │
│   └─→ Changes found?
│       └─→ Continue to STEP 2
│
├─→ STEP 2: Validate Authorization
│   │
│   ├─→ Call auth-validator skill
│   │   │
│   │   ├─→ Git credentials not set?
│   │   │   └─→ EXIT: "Git credentials missing. Run: git config..."
│   │   │
│   │   ├─→ No permission to push?
│   │   │   └─→ EXIT: "Permission denied. Check repo access."
│   │   │
│   │   └─→ Authorized?
│   │       └─→ Continue to STEP 3
│   │
│   └─→ Auth service unavailable?
│       └─→ EXIT: "Auth service down. Retry later."
│
├─→ STEP 3: Validate File Safety
│   │
│   ├─→ Call rules-engine skill
│   │   │
│   │   ├─→ Any blocked files found?
│   │   │   └─→ EXIT: "Blocked files: .env, credentials/..."
│   │   │
│   │   ├─→ Any files > 50MB?
│   │   │   └─→ WARN: "Large file detected: video.mp4 (100MB)"
│   │   │       Continue anyway (logged as warning)
│   │   │
│   │   └─→ All files approved?
│   │       └─→ Continue to STEP 4
│   │
│   └─→ Rules service unavailable?
│       └─→ EXIT: "Rules engine down. Cannot proceed safely."
│
├─→ STEP 4: Generate Commit Message
│   │
│   ├─→ Custom message provided?
│   │   ├─→ Yes: Use it
│   │   └─→ No: Go to STEP 4a
│   │
│   └─→ STEP 4a: Auto-generate from changes
│       │
│       ├─→ Single file changed?
│       │   └─→ Generate: "Add: file.rs" (or Update/Remove)
│       │
│       ├─→ Multiple files changed?
│       │   ├─→ Count: +3 added, ~2 modified, -1 deleted
│       │   └─→ Generate: "chore: update 6 files"
│       │
│       └─→ Message generation failed?
│           └─→ EXIT: "Cannot auto-generate commit message"
│
├─→ STEP 5: Execute Git Commit
│   │
│   ├─→ Run: git add -A
│   │   │
│   │   └─→ Failed?
│   │       └─→ EXIT: "git add failed (code 4)"
│   │
│   ├─→ Run: git commit -F message-file
│   │   │
│   │   ├─→ Success?
│   │   │   └─→ Continue to STEP 6
│   │   │
│   │   └─→ Failed?
│   │       └─→ EXIT: "git commit failed (code 5)"
│   │
│   └─→ Cleanup temp file
│       └─→ Warn if cleanup fails (non-critical)
│
├─→ STEP 6: Execute Git Push
│   │
│   ├─→ Determine target branch
│   │   ├─→ Could not determine?
│   │   │   └─→ Default to "main"
│   │   └─→ Determined: "main"
│   │
│   ├─→ Verify origin remote exists
│   │   │
│   │   └─→ Does not exist?
│   │       └─→ EXIT: "origin remote not found (code 7)"
│   │
│   ├─→ Run: git push origin <branch>
│   │   │
│   │   ├─→ Success?
│   │   │   ├─→ Commit hash: abc123def456
│   │   │   ├─→ Continue to STEP 7
│   │   │   │
│   │   │   └─→ Failure?
│   │   │       └─→ EXIT: "git push failed (code 6)"
│   │   │
│   │   └─→ Network timeout?
│   │       └─→ EXIT: "Push timeout (5s). Check network."
│   │
│   └─→ Log result to telemetry
│
├─→ STEP 7: Log Success & Exit
│   │
│   ├─→ Call telemetry-logger skill
│   │   │
│   │   ├─→ Success?
│   │   │   └─→ Return log ID
│   │   │
│   │   └─→ Failed?
│   │       └─→ WARN: "Telemetry failed" (non-critical)
│   │
│   └─→ EXIT: "Push complete. Log: [ID]"
│
└─→ END
```

---

## Example: Success Path

**Scenario**: Normal push, 3 files changed

```
START
  ↓
STEP 1: Check changes
  Found: src/main.rs, Cargo.toml, docs/README.md
  ↓ Continue
STEP 2: Validate Authorization
  auth-validator: ✓ Credentials OK, permission OK
  ↓ Continue
STEP 3: Validate File Safety
  rules-engine: ✓ All files approved
  ↓ Continue
STEP 4: Commit Message
  Auto-generate: "chore: update 3 files (+5, ~2, -0)"
  ↓ Continue
STEP 5: Git Commit
  git add -A: ✓ Success
  git commit: ✓ Success
  ↓ Continue
STEP 6: Git Push
  Branch: main
  origin remote: ✓ Found
  git push: ✓ Success
  Commit: abc123def456
  ↓ Continue
STEP 7: Log Success
  telemetry-logger: ✓ Recorded (ID: log-abc123)
  ↓
EXIT: "Push complete. Telemetry: log-abc123"
```

---

## Example: Blocked Path (.env File)

**Scenario**: User tries to push `.env` file

```
START
  ↓
STEP 1: Check changes
  Found: src/main.rs, .env
  ↓ Continue
STEP 2: Validate Authorization
  auth-validator: ✓ Credentials OK
  ↓ Continue
STEP 3: Validate File Safety
  rules-engine: ✗ .env blocked (explicit)
  ↓
  telemetry-logger: Recorded (ID: log-blocked-123)
  ↓
EXIT: "BLOCKED: .env matches excluded files. Telemetry: log-blocked-123"
```

**No commits made. No git state changed.**

---

## Example: Auth Failure

**Scenario**: Git credentials not configured

```
START
  ↓
STEP 1: Check changes
  Found: src/main.rs
  ↓ Continue
STEP 2: Validate Authorization
  auth-validator: ✗ No git user.name configured
  ↓
  telemetry-logger: Recorded (ID: log-auth-456)
  ↓
EXIT: "ERROR: Git credentials missing. Run: git config user.name 'Your Name'"
```

**No changes staged/committed.**

---

## Example: Network Timeout

**Scenario**: Git push times out

```
START
  ↓
  ... [STEPS 1-5 succeed] ...
  ↓
STEP 6: Git Push
  Branch: main
  origin remote: ✓ Found
  git push: ✗ Timeout (> 5s)
  ↓
  telemetry-logger: Recorded (ID: log-timeout-789)
  ↓
EXIT: "ERROR: git push timeout. Check network/server. Telemetry: log-timeout-789"
```

**Commit exists locally; not pushed.**

---

## Conditional Decision Points

### Should We Continue?

At each step, the skill asks: **"Is it safe to proceed?"**

| Step | Block If | Continue If |
|------|----------|-------------|
| Step 1 | No changes | Changes found |
| Step 2 | Auth fails | Auth passes |
| Step 3 | Files blocked | Files approved |
| Step 4 | Message gen fails | Message generated |
| Step 5 | Commit fails | Commit succeeds |
| Step 6 | Push fails | Push succeeds |
| Step 7 | (non-critical) | Always logs |

### Fail-Safe Design

**On doubt: BLOCK**

If any step encounters unexpected error:
- Log the error with full context
- Do not proceed
- Operator sees clear reason why

---

## Debugging: Which Step Failed?

**Log output format**:
```
✗ ERROR at STEP <N>: <reason>
  Context: <details>
  Telemetry: <log-id>
  Action: <what to fix>
```

**Examples**:
```
✗ ERROR at STEP 2: Git credentials missing
  Context: user.name not configured
  Telemetry: log-auth-123
  Action: Run: git config user.name "Your Name"
```

```
✗ ERROR at STEP 3: Blocked files (rules-engine)
  Context: .env matches excluded pattern
  Telemetry: log-blocked-456
  Action: Remove .env from working tree or .gitignore it
```

---

## How Telemetry Records Each Step

Each step results are logged:

```json
{
  "step": 1,
  "name": "Check changes",
  "status": "SUCCESS",
  "details": {
    "files_found": 3,
    "files": ["src/main.rs", "Cargo.toml", "docs/README.md"]
  }
}
```

```json
{
  "step": 3,
  "name": "Validate file safety",
  "status": "BLOCKED",
  "details": {
    "blocked_files": [".env"],
    "reason": "matches excluded pattern"
  }
}
```

Full telemetry entry chains all steps together.

---

## Exit Codes

| Code | Step Failed | Meaning |
|------|------------|---------|
| 0 | None | Success |
| 1 | (internal) | Generic error |
| 2 | Pre-flight | git not installed |
| 3 | Pre-flight | Not a git repo |
| 4 | Step 5 | git add failed |
| 5 | Step 5 | git commit failed |
| 6 | Step 6 | git push failed |
| 7 | Step 6 | origin remote missing |
| 8 | Step 7 | Telemetry failed (non-critical) |

---

## How to Use This Tree for Debugging

1. **Note the exit code** (e.g., 5 = commit failed)
2. **Look up in tree** which step produces that code (STEP 5)
3. **Check the conditions** that lead to that step
4. **Review telemetry log** for full context
5. **Take the suggested action**

---

**Last updated**: 2026-02-05  
**Version**: 1.0  
**Status**: Ready for implementation
