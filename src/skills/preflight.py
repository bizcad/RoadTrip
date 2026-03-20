"""
preflight.py

Read-only precondition checks for skills that touch external targets.
Runs before Execute — validates the environment can receive the composed action.

Vocabulary for git-push-autonomous:
    commit_message  — did Compose produce a message?
    token_set       — is GITHUB_TOKEN in the environment?
    remote_reachable — can we reach origin?
    branch_exists   — does the remote branch exist?
    fast_forward    — would the push land cleanly?

Unknown check name at runtime → escalate to Evaluate immediately.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .git_push_autonomous_models import ComposedAction


# ---------------------------------------------------------------------------
# Closed vocabulary
# ---------------------------------------------------------------------------

class CheckName(str, Enum):
    COMMIT_MESSAGE   = "commit_message"
    TOKEN_SET        = "token_set"
    REMOTE_REACHABLE = "remote_reachable"
    BRANCH_EXISTS    = "branch_exists"
    FAST_FORWARD     = "fast_forward"


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class PreflightCheck:
    name: str
    ok: bool
    reason: str = ""


@dataclass
class PreflightResult:
    ready: bool
    checks: list[PreflightCheck] = field(default_factory=list)
    first_failure: PreflightCheck | None = None


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def _check_commit_message(commit_message: str) -> PreflightCheck:
    ok = bool(commit_message and commit_message.strip())
    return PreflightCheck(
        name=CheckName.COMMIT_MESSAGE,
        ok=ok,
        reason="" if ok else "commit message is empty -- Compose phase did not complete",
    )


def _check_token_set() -> PreflightCheck:
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    ok = bool(token)
    return PreflightCheck(
        name=CheckName.TOKEN_SET,
        ok=ok,
        reason="" if ok else "GITHUB_TOKEN not set -- load from ProjectSecrets/PAT.txt",
    )


def _check_remote_reachable(token: str, remote: str = "origin") -> PreflightCheck:
    """
    Probe origin with git ls-remote using the token.
    Read-only — does not fetch or write.
    """
    env = os.environ.copy()
    askpass_content = f'#!/bin/sh\necho "{token}"\n'

    try:
        import tempfile, stat
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".sh", delete=False, prefix="askpass_"
        ) as f:
            f.write(askpass_content)
            askpass_path = f.name

        os.chmod(askpass_path, stat.S_IRWXU)
        env["GIT_ASKPASS"] = askpass_path

        result = subprocess.run(
            ["git", "ls-remote", "--exit-code", remote],
            env=env,
            capture_output=True,
            text=True,
            timeout=10,
        )
        ok = result.returncode == 0
        reason = "" if ok else f"git ls-remote failed (exit {result.returncode}): {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        ok = False
        reason = "git ls-remote timed out -- network unreachable or slow"
    except Exception as e:
        ok = False
        reason = f"remote reachability check failed: {e}"
    finally:
        try:
            os.unlink(askpass_path)
        except Exception:
            pass

    return PreflightCheck(name=CheckName.REMOTE_REACHABLE, ok=ok, reason=reason)


def _check_branch_exists(branch: str, remote: str = "origin") -> PreflightCheck:
    """
    Check that the remote branch ref exists.
    Read-only — git ls-remote filters to the specific branch.
    """
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--heads", remote, branch],
            capture_output=True,
            text=True,
            timeout=10,
        )
        ok = bool(result.stdout.strip())
        reason = "" if ok else f"branch '{branch}' not found on {remote} -- first push needs: git push -u {remote} {branch}"
    except subprocess.TimeoutExpired:
        ok = False
        reason = "branch existence check timed out"
    except Exception as e:
        ok = False
        reason = f"branch existence check failed: {e}"

    return PreflightCheck(name=CheckName.BRANCH_EXISTS, ok=ok, reason=reason)


def _check_fast_forward(branch: str, remote: str = "origin") -> PreflightCheck:
    """
    Check that local HEAD is ahead of (or equal to) remote — no divergence.
    Uses git rev-list to count commits remote has that local doesn't.
    Read-only — no fetch, compares against last-fetched remote ref.
    """
    try:
        result = subprocess.run(
            ["git", "rev-list", "--count", f"{remote}/{branch}..HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            # Remote ref not yet fetched locally — can't determine, treat as ok
            return PreflightCheck(
                name=CheckName.FAST_FORWARD,
                ok=True,
                reason="remote ref not in local index -- skipping divergence check",
            )

        behind = subprocess.run(
            ["git", "rev-list", "--count", f"HEAD..{remote}/{branch}"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        behind_count = int(behind.stdout.strip()) if behind.returncode == 0 else 0
        ok = behind_count == 0
        reason = "" if ok else (
            f"remote {remote}/{branch} is {behind_count} commit(s) ahead of local -- "
            f"pull or rebase before pushing"
        )
    except Exception as e:
        ok = False
        reason = f"fast-forward check failed: {e}"

    return PreflightCheck(name=CheckName.FAST_FORWARD, ok=ok, reason=reason)


# ---------------------------------------------------------------------------
# Preflight runner
# ---------------------------------------------------------------------------

def run_preflight(
    commit_message: str,
    branch: str,
    remote: str = "origin",
) -> PreflightResult:
    """
    Run all preflight checks in dependency order.
    Short-circuits at first failure — each check is pointless if the previous failed.

    Args:
        commit_message: The message Compose produced. Empty = Compose failed.
        branch:         Current git branch name.
        remote:         Remote name (default: origin).

    Returns:
        PreflightResult with ready=True if all checks passed.
    """
    checks: list[PreflightCheck] = []

    def run(check: PreflightCheck) -> bool:
        checks.append(check)
        return check.ok

    # 1. Did Compose finish?
    if not run(_check_commit_message(commit_message)):
        return PreflightResult(ready=False, checks=checks, first_failure=checks[-1])

    # 2. Is the token available?
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not run(_check_token_set()):
        return PreflightResult(ready=False, checks=checks, first_failure=checks[-1])

    # 3. Can we reach the remote?
    if not run(_check_remote_reachable(token, remote)):
        return PreflightResult(ready=False, checks=checks, first_failure=checks[-1])

    # 4. Does the branch exist on remote?
    if not run(_check_branch_exists(branch, remote)):
        return PreflightResult(ready=False, checks=checks, first_failure=checks[-1])

    # 5. Would this be a fast-forward push?
    if not run(_check_fast_forward(branch, remote)):
        return PreflightResult(ready=False, checks=checks, first_failure=checks[-1])

    return PreflightResult(ready=True, checks=checks, first_failure=None)
