# Usage Examples: Real-World Scenarios

## Example 1: Simple Documentation Update

**Scenario**: You update the README and push it.

```markdown
**User**: I've finished the README update; push it.

**Orchestrator Analysis**:
- Changes found: README.md (+12 lines)
- Auth check: ✓ Git config OK
- Rules check: ✓ README.md is allowed
- Message: "docs: update README"
- Commit: ✓ Success (hash: abc123)
- Push: ✓ Success on main
- Telemetry: ✓ Logged (ID: log-2026-02-05-001)

**Result**: 
✓ Push complete
  Commit: abc123
  Branch: main
  Changes: +12, ~0, -0
  Log: log-2026-02-05-001

**What to do next**: Check GitHub to see your commit
```

---

## Example 2: Feature Implementation (Multiple Files)

**Scenario**: You've completed a feature touching 5 files.

```markdown
**User**: I've finished the user auth feature; push it.

**Files Changed**:
- src/auth.rs (+120 lines, modified)
- src/models.rs (+30 lines, modified)
- tests/auth_test.rs (new file, +80 lines)
- docs/API.md (+10 lines, modified)
- Cargo.toml (+1 line, modified)

**Orchestrator Analysis**:
- Changes found: 5 files
- Auth check: ✓ OK
- Rules check: ✓ All files approved
- Message: "feat: add user authentication"
  Details:
  - Modified: src/auth.rs, src/models.rs, docs/API.md, Cargo.toml
  - Added: tests/auth_test.rs
  - Total: +241, ~4, -0
- Commit: ✓ Success (hash: def456)
- Push: ✓ Success on feature/auth
- Telemetry: ✓ Logged (ID: log-2026-02-05-002)

**Result**:
✓ Push complete
  Commit: def456
  Branch: feature/auth
  Changes: +241, ~4, -0
  Log: log-2026-02-05-002

**What to do next**: Open a PR on GitHub
```

---

## Example 3: Blocked Files (.env Secret)

**Scenario**: You accidentally staged `.env` with database password.

```markdown
**User**: I've finished setup; push all changes.

**Files Changed**:
- src/config.rs (modified)
- .env (new file, contains DATABASE_PASSWORD)

**Orchestrator Analysis**:
- Changes found: 2 files
- Auth check: ✓ OK
- Rules check: ✗ BLOCKED
  - src/config.rs: ✓ Allowed
  - .env: ✗ Blocked (matches excluded pattern)
- Telemetry: ✓ Logged (ID: log-2026-02-05-003)

**Result**:
✗ BLOCKED: Excluded files detected
  Blocked files: .env
  Reason: Matches exclusion pattern (secrets)
  Log: log-2026-02-05-003

**What to do next**:
1. Run: git reset .env
2. Run: echo .env >> .gitignore
3. Try pushing again
4. Also: Never commit .env; use .env.example instead

**Operator Note**: Review log-2026-02-05-003 to audit
```

---

## Example 4: Missing Git Credentials

**Scenario**: You're on a new machine and haven't configured git yet.

```markdown
**User**: Push my changes.

**Orchestrator Analysis**:
- Changes found: src/main.rs (+10 lines)
- Auth check: ✗ FAILED
  - Git user.name: Not configured
  - Git user.email: Not configured
- Telemetry: ✓ Logged (ID: log-2026-02-05-004)

**Result**:
✗ ERROR: Git credentials missing
  Issue: user.name and user.email not configured
  Log: log-2026-02-05-004

**What to do next**:
  git config user.name "Your Name"
  git config user.email "your.email@example.com"
  git config --global user.name "Your Name"  # (for all repos)
  git config --global user.email "your.email@example.com"
```

---

## Example 5: Large File Warning (Allowed)

**Scenario**: You commit a video file larger than 50MB.

```markdown
**User**: Push the video demo and code changes.

**Files Changed**:
- src/demo.rs (+20 lines)
- demo-output.mp4 (new file, 150 MB)

**Orchestrator Analysis**:
- Changes found: 2 files
- Auth check: ✓ OK
- Rules check: ✓ Allowed (with warning)
  - src/demo.rs: ✓ Allowed
  - demo-output.mp4: ⚠ Size 150MB > 50MB limit
    (Allowed but logged as warning)
- Message: "docs: add demo video and implementation"
- Commit: ✓ Success (hash: ghi789)
- Push: ✓ Success on main
- Telemetry: ✓ Logged (ID: log-2026-02-05-005, includes size warning)

**Result**:
⚠ Push complete (with warnings)
  Commit: ghi789
  Branch: main
  Changes: +20, +150MB, -0
  Warnings: Large file (demo-output.mp4: 150MB > 50MB)
  Log: log-2026-02-05-005

**What to do next**:
  Note: GitHub may warn on files > 100MB in future
  Consider: Use Git LFS for large binary files
  Review log-2026-02-05-005 for details
```

---

## Example 6: Network Timeout

**Scenario**: The push command times out due to slow network.

```markdown
**User**: Push changes to server.

**Orchestrator Analysis**:
- Changes found: src/main.rs (+15 lines)
- Auth check: ✓ OK
- Rules check: ✓ OK
- Message: "fix: update main function"
- Commit: ✓ Success (hash: jkl012)
- Push: ✗ TIMEOUT
  - Origin: github.com/user/repo
  - Branch: main
  - Timeout: 5 seconds exceeded
  - Network: Check connection
- Telemetry: ✓ Logged (ID: log-2026-02-05-006)

**Result**:
✗ ERROR: git push timeout
  Issue: Network took > 5 seconds; push aborted
  Commit: jkl012 (exists locally, not pushed)
  Log: log-2026-02-05-006

**What to do next**:
  1. Check internet connection
  2. Retry: Run git-push-autonomous again
  3. If persistent: Check server status
  4. If server down: Wait and retry
```

---

## Example 7: Dry-Run Mode

**Scenario**: You want to preview the commit message before pushing.

```markdown
**User**: Dry run: show what would be committed without pushing.

**Orchestrator Analysis** (dry-run mode):
- Changes found: src/main.rs, tests/unit.rs, docs/API.md
- Auth check: ✓ OK (not critical for dry-run)
- Rules check: ✓ OK
- Message (preview):
  Subject: "chore: update 3 files (+20, ~5, -0)"
  Body:
    Modified:
    - src/main.rs
    - docs/API.md
    Added:
    - tests/unit.rs

**Result**:
--- Dry Run: Commit Preview ---
chore: update 3 files (+20, ~5, -0)

Modified:
- src/main.rs
- docs/API.md
Added:
- tests/unit.rs
--- End Preview ---

**What to do next**:
  If message looks good: "Push changes" (no dry-run flag)
  If message needs change: "Push with message: 'feat: add unit tests'"
```

---

## Example 8: Branch Protection Rule Rejection

**Scenario**: Server-side branch protection rejects the push.

```markdown
**User**: Push to main.

**Orchestrator Analysis**:
- Changes found: src/main.rs (+10 lines)
- Auth check: ✓ OK
- Rules check: ✓ OK
- Message: "fix: bug in main function"
- Commit: ✓ Success (hash: mno345)
- Push: ✗ REJECTED
  - Branch: main
  - Reason: Branch protection rule (requires PR)
  - Server: github.com rejected push
- Telemetry: ✓ Logged (ID: log-2026-02-05-007)

**Result**:
✗ ERROR: git push rejected by server
  Issue: main branch requires PR; direct push not allowed
  Commit: mno345 (exists locally, not pushed)
  Log: log-2026-02-05-007

**What to do next**:
  1. Create a feature branch: git checkout -b fix/bug
  2. Cherry-pick commit: git cherry-pick mno345
  3. Push feature branch: git push origin fix/bug
  4. Open PR on GitHub
  (Or: Contact repo admin if rule is too strict)
```

---

## Example 9: Partial Success (Mixed Files)

**Scenario**: You staged both safe and unsafe files; orchestrator blocks all.

```markdown
**User**: Push all my changes.

**Files Changed**:
- src/main.rs (safe)
- .secrets/api-key.txt (blocked)
- config.yaml (safe)

**Orchestrator Analysis**:
- Changes found: 3 files
- Auth check: ✓ OK
- Rules check: ✗ BLOCKED
  - src/main.rs: ✓ Allowed
  - .secrets/api-key.txt: ✗ Blocked (pattern: ^secrets/.*)
  - config.yaml: ✓ Allowed
- Telemetry: ✓ Logged (ID: log-2026-02-05-008)

**Result**:
✗ BLOCKED: Excluded files detected
  Blocked: .secrets/api-key.txt (matches secrets pattern)
  Safe files: src/main.rs, config.yaml (NOT pushed)
  Log: log-2026-02-05-008

**Note**: Currently all-or-nothing (no partial pushes)

**What to do next**:
  1. Remove or rename .secrets/api-key.txt
  2. Or: Move to .gitignore + upload to secure vault
  3. Retry push
  
  (Future Phase 2: Partial push could allow safe files only)
```

---

## Example 10: Learning from Telemetry (Phase 2 Preview)

**Scenario**: Operator analyzes logs after 100 pushes.

```markdown
**Phase 1 Summary** (first week):
- Total pushes attempted: 47
- Success: 42
- Blocked (excluded files): 3
- Blocked (auth): 2
- Failures: 0

**Blocked files analysis**:
- .env: 2 occurrences (operator keeps forgetting)
- .secrets/*.key: 1 occurrence (new pattern learned)

**Confidence trends**:
- auth_validator: 1.00 (never fails)
- rules_engine: 0.98 (very reliable)
- Large files: 0.95 (occasional warnings)

**Phase 2 recommendations**:
1. Add reminder/pre-check for .env files
2. Keep / refine excluded patterns
3. Consider auto-gitignore setup for new repos
4. Confidence thresholds look good; no changes needed

**Decision**: Ready for Phase 2 SDK upgrade
```

---

## Common Patterns

### Pattern A: Iterative Development
```
1. Code → Push (safely auto-commits)
2. Review feedback → Code → Push (auto-commits)
3. Repeat 10+ times per day
→ Perfect for autonomous workflow
```

### Pattern B: Scheduled Cleanup
```
1. Cron job or scheduler runs: "Push any staged changes"
2. Skill auto-validates, commits, pushes
3. Telemetry recorded for audit
→ Autonomous backup/sync workflow
```

### Pattern C: CI/CD Integration
```
1. Test passes → Trigger git-push-autonomous
2. Auto-commit test results, coverage, docs
3. Push results alongside code
→ Reduces manual commit overhead
```

---

## When NOT to Use This Skill

❌ **Code Review Required**: Use code-review-orchestrator first  
❌ **Security Sensitive**: Requires security-scan-orchestrator  
❌ **Team Coordination**: Requires PR approval  
❌ **Learning**: Use manual git commands to understand concepts  

---

**Last updated**: 2026-02-05  
**Version**: 1.0  
**Status**: Ready for testing
