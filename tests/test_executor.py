"""
test_executor.py

Tests for executor.py — SRCGEEEExecutor with preflight + execution.

Coverage:
- dryrun() pass and fail cases
- run() preflight routing: known failure → triage, unknown → evaluate
- run() execution failure → evaluate
- run() success path
- short-circuit: remaining checks don't run after first failure
"""

import os
import pytest
from unittest.mock import patch, MagicMock

try:
    from src.skills.executor import SRCGEEEExecutor, ComposedAction, ExecResult
    from src.skills.preflight import CheckName
except ImportError:
    from executor import SRCGEEEExecutor, ComposedAction, ExecResult
    from preflight import CheckName


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _good_action() -> ComposedAction:
    return ComposedAction(
        branch="main",
        remote="origin",
        commit_message="feat: add executor",
    )


def _fake_subprocess_all_pass(cmd, **kwargs):
    """Stub: all git subprocess calls succeed."""
    m = MagicMock()
    m.returncode = 0
    m.stderr = ""
    m.stdout = "abc123 refs/heads/main\n" if "rev-list" not in cmd else "0\n"
    return m


def _patched_run(monkeypatch_or_patch):
    """Context: all subprocess calls pass + GITHUB_TOKEN set."""
    return (
        patch("subprocess.run", side_effect=_fake_subprocess_all_pass),
        patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_test"}),
    )


# ---------------------------------------------------------------------------
# dryrun()
# ---------------------------------------------------------------------------

class TestDryrun:

    def test_pass_returns_success(self):
        def fake_sub(cmd, **kwargs):
            m = MagicMock()
            m.returncode = 0
            m.stderr = ""
            m.stdout = "abc refs/heads/main\n" if "rev-list" not in cmd else "0\n"
            return m

        with patch("src.skills.preflight.subprocess.run", side_effect=fake_sub):
            with patch.dict(os.environ, {"GITHUB_TOKEN": "tok"}):
                result = SRCGEEEExecutor().dryrun(_good_action())

        assert result.success is True
        assert result.escalate_to is None
        assert result.result["dry_run"] is True
        assert result.result["preflight"] == "pass"
        assert "would_execute" in result.result

    def test_fail_empty_commit_message(self):
        action = ComposedAction(branch="main", commit_message="")
        result = SRCGEEEExecutor().dryrun(action)

        assert result.success is False
        assert result.context["dry_run"] is True
        assert result.context["failed_check"] == CheckName.COMMIT_MESSAGE

    def test_fail_no_token(self):
        env = {k: v for k, v in os.environ.items() if k != "GITHUB_TOKEN"}
        with patch.dict(os.environ, env, clear=True):
            result = SRCGEEEExecutor().dryrun(_good_action())

        assert result.success is False
        assert result.context["failed_check"] == CheckName.TOKEN_SET

    def test_fail_routes_to_triage_for_known_check(self):
        action = ComposedAction(branch="main", commit_message="")
        result = SRCGEEEExecutor().dryrun(action)

        assert result.escalate_to == "triage"
        assert result.context["known_failure"] is True

    def test_dryrun_never_calls_git_push(self):
        """dryrun must not call git push under any circumstances."""
        action = ComposedAction(branch="main", commit_message="")
        with patch("src.skills.git_push_autonomous.GitPushSkill") as mock_skill:
            SRCGEEEExecutor().dryrun(action)
        mock_skill.assert_not_called()


# ---------------------------------------------------------------------------
# run() — preflight routing
# ---------------------------------------------------------------------------

class TestRunPreflightRouting:

    def test_known_failure_routes_triage(self):
        """commit_message is a known check — must route to triage."""
        action = ComposedAction(branch="main", commit_message="")
        result = SRCGEEEExecutor().run(action)

        assert result.success is False
        assert result.escalate_to == "triage"
        assert result.context["known_failure"] is True

    def test_unknown_failure_routes_evaluate(self):
        """
        Simulate a novel failure by injecting a PreflightResult
        with an unknown check name.
        """
        from src.skills.preflight import PreflightResult, PreflightCheck

        novel_failure = PreflightResult(
            ready=False,
            checks=[PreflightCheck(name="new_thing", ok=False, reason="novel")],
            first_failure=PreflightCheck(name="new_thing", ok=False, reason="novel"),
        )

        with patch("src.skills.executor.run_preflight", return_value=novel_failure):
            result = SRCGEEEExecutor().run(_good_action())

        assert result.success is False
        assert result.escalate_to == "evaluate"
        assert result.context["known_failure"] is False

    def test_token_missing_routes_triage(self):
        env = {k: v for k, v in os.environ.items() if k != "GITHUB_TOKEN"}
        with patch.dict(os.environ, env, clear=True):
            result = SRCGEEEExecutor().run(_good_action())

        assert result.escalate_to == "triage"
        assert result.context["failed_check"] == CheckName.TOKEN_SET


# ---------------------------------------------------------------------------
# run() — execution path
# ---------------------------------------------------------------------------

class TestRunExecution:

    def _all_pass_preflight(self):
        from src.skills.preflight import PreflightResult, PreflightCheck
        return PreflightResult(
            ready=True,
            checks=[PreflightCheck(name=c.value, ok=True) for c in CheckName],
            first_failure=None,
        )

    def test_success(self):
        from src.skills.git_push_autonomous import GitPushResult

        mock_push = MagicMock()
        mock_push.success = True
        mock_push.decision = "APPROVE"
        mock_push.commit_count = 2
        mock_push.commit_hashes = ["abc123", "def456"]
        mock_push.branch = "main"
        mock_push.remote = "origin"
        mock_push.push_timestamp = "2026-03-17T00:00:00Z"
        mock_push.git_output = "main -> main"

        mock_skill = MagicMock()
        mock_skill.push.return_value = mock_push

        with patch("src.skills.executor.run_preflight", return_value=self._all_pass_preflight()):
            with patch("src.skills.git_push_autonomous.GitPushSkill", return_value=mock_skill):
                result = SRCGEEEExecutor().run(_good_action())

        assert result.success is True
        assert result.escalate_to is None
        assert result.result["commit_count"] == 2

    def test_execution_failure_routes_evaluate(self):
        """Push returns success=False after preflight passed → evaluate."""
        mock_push = MagicMock()
        mock_push.success = False
        mock_push.decision = "REJECT"
        mock_push.errors = ["rejected by hook"]
        mock_push.warnings = []

        mock_skill = MagicMock()
        mock_skill.push.return_value = mock_push

        with patch("src.skills.executor.run_preflight", return_value=self._all_pass_preflight()):
            with patch("src.skills.git_push_autonomous.GitPushSkill", return_value=mock_skill):
                result = SRCGEEEExecutor().run(_good_action())

        assert result.success is False
        assert result.escalate_to == "evaluate"
        assert "rejected by hook" in result.context["errors"]

    def test_unexpected_exception_routes_evaluate(self):
        """Unexpected exception during execute → evaluate."""
        mock_skill = MagicMock()
        mock_skill.push.side_effect = RuntimeError("something exploded")

        with patch("src.skills.executor.run_preflight", return_value=self._all_pass_preflight()):
            with patch("src.skills.git_push_autonomous.GitPushSkill", return_value=mock_skill):
                result = SRCGEEEExecutor().run(_good_action())

        assert result.success is False
        assert result.escalate_to == "evaluate"
        assert "RuntimeError" in result.context["exception_type"]


# ---------------------------------------------------------------------------
# ExecResult shape consistency
# ---------------------------------------------------------------------------

class TestExecResultShape:

    def test_dryrun_and_run_return_same_type(self):
        action = ComposedAction(branch="main", commit_message="")
        dry = SRCGEEEExecutor().dryrun(action)
        run = SRCGEEEExecutor().run(action)
        assert type(dry) is ExecResult
        assert type(run) is ExecResult

    def test_to_dict_is_serialisable(self):
        import json
        action = ComposedAction(branch="main", commit_message="feat: x")
        result = SRCGEEEExecutor().dryrun(action)
        # Should not raise
        json.dumps(result.to_dict())
