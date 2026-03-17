# Coding Plan: SRCGEEE Execute Component
# Target: git-push-autonomous v1.3.0

**Date:** 2026-03-17
**Depends on:** `src/skills/git_push_autonomous.py`, `src/skills/auth_validator.py`,
               `src/skills/telemetry_logger.py`, `skills/git-push-autonomous/SKILL.md`
**New files:** `src/skills/executor.py`, `src/skills/preflight.py`

---

## Overview

Add a proper Execute layer to `git-push-autonomous` with:
1. `preflight.py` — `PreflightCheck`, `PreflightResult`, 5 named checks
2. `executor.py` — `SRCGEEEExecutor` with `dryrun()` and `run()`
3. Wire into `git_push_autonomous.py` — replace bare git call with executor
4. Update `skills/git-push-autonomous/SKILL.md` — bump version, re-stamp fingerprint

---

## Step 1: `src/skills/preflight.py`

### Dataclasses

```python
@dataclass
class PreflightCheck:
    name: str
    ok: bool
    reason: str = ""

@dataclass
class PreflightResult:
    ready: bool
    checks: list[PreflightCheck]          # all that ran, in order
    first_failure: PreflightCheck | None  # None if ready=True
```

### Named checks (in dependency order)

| # | Name | Probes |
|---|---|---|
| 1 | `commit_message` | `action.commit_message` is non-empty string |
| 2 | `token_set` | `os.environ.get("GITHUB_TOKEN")` is non-empty |
| 3 | `remote_reachable` | `git ls-remote --exit-code origin` with token auth |
| 4 | `branch_exists` | remote ref exists for current branch |
| 5 | `fast_forward` | `git fetch --dry-run` or `git status` shows no divergence |

### Implementation notes

- Each check is a private method: `_check_commit_message()`, `_check_token_set()`, etc.
- `run_preflight(action) -> PreflightResult` iterates checks in order, short-circuits on first failure
- All checks are **read-only** — no git writes, no file writes
- `_check_remote_reachable()` uses the same GIT_ASKPASS pattern already in `git_push.ps1`
- `_check_fast_forward()`: run `git fetch origin <branch> --dry-run`, compare local HEAD to FETCH_HEAD

### Closed vocabulary constant

```python
KNOWN_CHECK_NAMES = frozenset({
    "commit_message", "token_set", "remote_reachable",
    "branch_exists", "fast_forward"
})
```

---

## Step 2: `src/skills/executor.py`

### ExecResult

```python
@dataclass
class ExecResult:
    success: bool
    result: dict[str, Any] = field(default_factory=dict)
    escalate_to: Literal["triage", "evaluate"] | None = None
    context: dict[str, Any] = field(default_factory=dict)
```

### SRCGEEEExecutor

```python
class SRCGEEEExecutor:
    def dryrun(self, action: ComposedAction) -> ExecResult
    def run(self, action: ComposedAction) -> ExecResult
    def _to_exec_result(self, preflight: PreflightResult) -> ExecResult
    def _execute(self, action: ComposedAction) -> ExecResult
    def _is_known_failure(self, check_name: str) -> bool
```

### `dryrun()` logic

1. Run `run_preflight(action)`
2. Return `_to_exec_result(preflight)` — never touches the world

### `run()` logic

```
1. Run preflight
2. If not ready:
     known failure  → ExecResult(escalate_to="triage", context=preflight context)
     unknown failure → ExecResult(escalate_to="evaluate", context=preflight context)
3. If ready:
     try: _execute(action) → ExecResult(success=True, result=...)
     except RecoverableError: → ExecResult(escalate_to="triage", context=...)
     except: → ExecResult(escalate_to="evaluate", context=...)
```

### `_to_exec_result()` logic

```python
def _to_exec_result(self, preflight: PreflightResult) -> ExecResult:
    if preflight.ready:
        return ExecResult(success=True, result={"preflight": "pass", "checks": [c.name for c in preflight.checks]})
    check = preflight.first_failure
    target = "triage" if self._is_known_failure(check.name) else "evaluate"
    return ExecResult(
        success=False,
        escalate_to=target,
        context={
            "failed_check": check.name,
            "reason": check.reason,
            "skill_docs": _load_skill_md("git-push-autonomous"),
            "known_failure": target == "triage",
        }
    )
```

---

## Step 3: Wire into `git_push_autonomous.py`

Current flow (simplified):
```python
def execute_push(self, ...) -> GitPushResult:
    # validate auth
    # check rules
    # generate commit message
    # git add / git commit / git push   ← bare, no preflight
```

New flow:
```python
def execute_push(self, ...) -> GitPushResult:
    # validate auth
    # check rules
    # generate commit message
    action = ComposedAction(commit_message=..., files=..., branch=...)
    executor = SRCGEEEExecutor()
    result = executor.run(action)           # preflight + execute
    if not result.success:
        self._handle_escalation(result)     # triage or evaluate routing
        return GitPushResult.from_exec(result)
    return GitPushResult.from_exec(result)
```

`ComposedAction` is a small dataclass — add to `git_push_autonomous_models.py`:
```python
@dataclass
class ComposedAction:
    commit_message: str
    files: list[str]
    branch: str
    skill_name: str = "git-push-autonomous"
    attempt_count: int = 0
```

---

## Step 4: Update SKILL.md

- Bump version: `1.2.0 → 1.3.0`
- Add to changelog section (or create one):
  ```
  ## Changelog
  ### 1.3.0
  - Added SRCGEEEExecutor with preflight checks
  - Preflight vocabulary: commit_message, token_set, remote_reachable,
    branch_exists, fast_forward
  - Unknown failures now escalate to Evaluate immediately
  ```
- Run `py src/skills/skill_scanner.py stamp` to re-stamp fingerprint

---

## Step 5: Tests

File: `tests/test_executor.py`

| Test | Scenario |
|---|---|
| `test_dryrun_pass` | All 5 checks pass → `success=True, escalate_to=None` |
| `test_dryrun_no_commit_message` | Empty message → `failed_check="commit_message"` |
| `test_dryrun_no_token` | TOKEN unset → `failed_check="token_set"` |
| `test_dryrun_short_circuits` | TOKEN unset → remote check never runs |
| `test_run_known_failure_routes_triage` | Known failure → `escalate_to="triage"` |
| `test_run_unknown_failure_routes_evaluate` | Unknown check name → `escalate_to="evaluate"` |
| `test_run_success` | All pass + mock git → `success=True` |

Use existing mock patterns from `tests/test_git_push_autonomous.py`.

---

## Acceptance Criteria

- [ ] `executor.dryrun()` returns `ExecResult` with `success=True` when all 5 checks pass
- [ ] `executor.dryrun()` short-circuits at first failure, remaining checks not run
- [ ] Known failure name → `escalate_to="triage"` in ExecResult context
- [ ] Unknown failure name → `escalate_to="evaluate"` in ExecResult context
- [ ] `run()` runs preflight before any git command
- [ ] Silent token failure (current bug) surfaces as `failed_check="token_set"` not silent exit
- [ ] All existing `test_git_push_autonomous.py` tests still pass
- [ ] `skill_scanner.py` scan shows `[OK]` with new version after stamp

---

## What This Does NOT Include (Next Steps)

- Triage agent implementation (needs memory substrate — episodic_index)
- Evaluate layer (receives escalated ExecResults)
- GitHub Issue/PR creation on novel failures (Evolve — needs thepopebot integration)
- `_check_fast_forward()` full implementation (needs git fetch, may need stub in tests)
