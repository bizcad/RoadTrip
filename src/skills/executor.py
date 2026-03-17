"""
executor.py

SRCGEEEExecutor — Execute layer for git-push-autonomous.

Wraps GitPushSkill with:
  1. Preflight: read-only precondition checks before touching the world
  2. dryrun(): preflight only, never executes — returns ExecResult
  3. run():    preflight → execute → ExecResult with escalation routing

Escalation routing:
  known preflight failure  → escalate_to="triage"   (table-lookup remediation)
  unknown preflight failure → escalate_to="evaluate" (novel, needs judgment)
  execution failure        → escalate_to="evaluate"  (passed preflight, still failed)
  success                  → escalate_to=None
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Literal

from src.skills.preflight import run_preflight, CheckName, PreflightResult
from src.skills.git_push_autonomous import GitPushSkill, GitPushRequest
from src.skills.commit_message import CommitMessageSkill


# ---------------------------------------------------------------------------
# Input / output types
# ---------------------------------------------------------------------------

@dataclass
class ComposedAction:
    """Output of the Compose phase — everything Execute needs."""
    branch: str
    remote: str = "origin"
    commit_message: str = ""
    skill_name: str = "git-push-autonomous"
    attempt_count: int = 0

    def describe(self) -> str:
        files = _count_staged_files()
        return (
            f"push {files} staged file(s) to {self.remote}/{self.branch} "
            f"with message: {self.commit_message!r}"
        )


@dataclass
class ExecResult:
    """
    Unified result for both dryrun() and run().

    escalate_to:
      None      — success or preflight pass (dryrun)
      "triage"  — known failure, remediation docs available
      "evaluate" — novel or unexpected failure, needs judgment
    """
    success: bool
    result: dict[str, Any] = field(default_factory=dict)
    escalate_to: Literal["triage", "evaluate"] | None = None
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_KNOWN_CHECK_NAMES = frozenset(c.value for c in CheckName)


def _count_staged_files() -> int:
    try:
        r = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, timeout=5,
        )
        return len([l for l in r.stdout.splitlines() if l.strip()])
    except Exception:
        return 0


def _load_skill_md(skill_name: str) -> str:
    """Return SKILL.md content for triage context. Empty string if not found."""
    candidates = [
        Path(f"skills/{skill_name}/SKILL.md"),
        Path(f"../{skill_name}/SKILL.md"),
    ]
    for p in candidates:
        if p.exists():
            return p.read_text(encoding="utf-8")
    return ""


def _get_current_branch() -> str:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        return r.stdout.strip() or "main"
    except Exception:
        return "main"


def _build_commit_message() -> str:
    """Generate commit message via CommitMessageSkill Tier 1."""
    try:
        skill = CommitMessageSkill()
        result = skill.generate()
        return result.message if result.success else ""
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Executor
# ---------------------------------------------------------------------------

class SRCGEEEExecutor:
    """
    Execute layer for git-push-autonomous.

    Usage:
        action = ComposedAction.from_current_state()
        executor = SRCGEEEExecutor()

        result = executor.dryrun(action)   # preflight only, no side effects
        if result.success:
            result = executor.run(action)  # full execution
    """

    def __init__(self, repo_path: str | None = None):
        self._repo_path = repo_path

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def dryrun(self, action: ComposedAction) -> ExecResult:
        """
        Run preflight checks only. Never touches the world.
        Returns ExecResult with same shape as run().

        result.success=True  → preflight passed, safe to call run()
        result.success=False → preflight failed, see context for reason
        """
        preflight = run_preflight(
            commit_message=action.commit_message,
            branch=action.branch,
            remote=action.remote,
        )
        return self._preflight_to_exec_result(preflight, action, dry_run=True)

    def run(self, action: ComposedAction) -> ExecResult:
        """
        Run preflight then execute. Touches the world only if preflight passes.

        Escalation:
          known preflight failure  → triage
          unknown preflight failure → evaluate
          execution failure        → evaluate
          success                  → None
        """
        preflight = run_preflight(
            commit_message=action.commit_message,
            branch=action.branch,
            remote=action.remote,
        )

        if not preflight.ready:
            return self._preflight_to_exec_result(preflight, action, dry_run=False)

        return self._execute(action)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _preflight_to_exec_result(
        self,
        preflight: PreflightResult,
        action: ComposedAction,
        dry_run: bool,
    ) -> ExecResult:
        if preflight.ready:
            return ExecResult(
                success=True,
                result={
                    "dry_run": dry_run,
                    "preflight": "pass",
                    "checks_passed": [c.name for c in preflight.checks],
                    "would_execute": action.describe() if dry_run else None,
                },
            )

        check = preflight.first_failure
        known = check.name in _KNOWN_CHECK_NAMES
        target: Literal["triage", "evaluate"] = "triage" if known else "evaluate"

        return ExecResult(
            success=False,
            escalate_to=target,
            context={
                "dry_run": dry_run,
                "failed_check": check.name,
                "reason": check.reason,
                "checks_run": [c.name for c in preflight.checks],
                "known_failure": known,
                "skill_docs": _load_skill_md(action.skill_name),
                "attempt_count": action.attempt_count,
            },
        )

    def _execute(self, action: ComposedAction) -> ExecResult:
        """
        Execute the push. Preflight has already passed.

        Any failure here is unexpected — escalate to Evaluate.
        """
        try:
            skill = GitPushSkill(repo_path=self._repo_path)
            request = GitPushRequest(
                branch=action.branch,
                remote=action.remote,
                dry_run=False,
            )
            push_result = skill.push(request)

            if push_result.success:
                return ExecResult(
                    success=True,
                    result={
                        "decision": push_result.decision,
                        "commit_count": push_result.commit_count,
                        "commit_hashes": push_result.commit_hashes,
                        "branch": push_result.branch,
                        "remote": push_result.remote,
                        "push_timestamp": push_result.push_timestamp,
                        "git_output": push_result.git_output,
                    },
                )

            # Push returned success=False — unexpected post-preflight
            return ExecResult(
                success=False,
                escalate_to="evaluate",
                context={
                    "reason": "push failed after preflight passed",
                    "errors": push_result.errors,
                    "warnings": push_result.warnings,
                    "decision": push_result.decision,
                    "skill_docs": _load_skill_md(action.skill_name),
                },
            )

        except Exception as exc:
            return ExecResult(
                success=False,
                escalate_to="evaluate",
                context={
                    "reason": f"unexpected exception during execute: {exc}",
                    "exception_type": type(exc).__name__,
                    "skill_docs": _load_skill_md(action.skill_name),
                },
            )


# ---------------------------------------------------------------------------
# Convenience factory
# ---------------------------------------------------------------------------

def composed_action_from_state(
    remote: str = "origin",
    skill_name: str = "git-push-autonomous",
) -> ComposedAction:
    """
    Build a ComposedAction from current git working state.
    Generates commit message via CommitMessageSkill Tier 1.
    """
    return ComposedAction(
        branch=_get_current_branch(),
        remote=remote,
        commit_message=_build_commit_message(),
        skill_name=skill_name,
    )
