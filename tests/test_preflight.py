"""
test_preflight.py

Tests for preflight.py — read-only precondition checks for git-push-autonomous.

Coverage:
- Each check individually (pass and fail cases)
- Short-circuit: first failure stops remaining checks
- run_preflight() full pass
- run_preflight() fails at each position
- Unknown check name detection (for triage routing)
"""

import os
import pytest
from unittest.mock import patch, MagicMock

try:
    from src.skills.preflight import (
        run_preflight, PreflightResult, PreflightCheck, CheckName,
        _check_commit_message, _check_token_set,
        _check_branch_exists, _check_fast_forward,
    )
except ImportError:
    from preflight import (
        run_preflight, PreflightResult, PreflightCheck, CheckName,
        _check_commit_message, _check_token_set,
        _check_branch_exists, _check_fast_forward,
    )


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

class TestCheckCommitMessage:

    def test_pass(self):
        r = _check_commit_message("feat: add preflight")
        assert r.ok is True
        assert r.reason == ""

    def test_fail_empty(self):
        r = _check_commit_message("")
        assert r.ok is False
        assert "empty" in r.reason

    def test_fail_whitespace(self):
        r = _check_commit_message("   ")
        assert r.ok is False

    def test_name(self):
        r = _check_commit_message("anything")
        assert r.name == CheckName.COMMIT_MESSAGE


class TestCheckTokenSet:

    def test_pass(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_abc123"}):
            r = _check_token_set()
        assert r.ok is True

    def test_fail_missing(self):
        env = {k: v for k, v in os.environ.items() if k != "GITHUB_TOKEN"}
        with patch.dict(os.environ, env, clear=True):
            r = _check_token_set()
        assert r.ok is False
        assert "GITHUB_TOKEN" in r.reason

    def test_fail_empty_string(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": ""}):
            r = _check_token_set()
        assert r.ok is False

    def test_fail_whitespace_only(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "   "}):
            r = _check_token_set()
        assert r.ok is False

    def test_name(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "tok"}):
            r = _check_token_set()
        assert r.name == CheckName.TOKEN_SET


class TestCheckBranchExists:

    def test_pass(self):
        mock = MagicMock()
        mock.returncode = 0
        mock.stdout = "abc123 refs/heads/main\n"
        with patch("subprocess.run", return_value=mock):
            r = _check_branch_exists("main")
        assert r.ok is True

    def test_fail_no_output(self):
        mock = MagicMock()
        mock.returncode = 0
        mock.stdout = ""
        with patch("subprocess.run", return_value=mock):
            r = _check_branch_exists("main")
        assert r.ok is False
        assert "main" in r.reason

    def test_name(self):
        mock = MagicMock()
        mock.returncode = 0
        mock.stdout = "abc refs/heads/main\n"
        with patch("subprocess.run", return_value=mock):
            r = _check_branch_exists("main")
        assert r.name == CheckName.BRANCH_EXISTS


class TestCheckFastForward:

    def test_pass_no_divergence(self):
        def fake_run(cmd, **kwargs):
            m = MagicMock()
            if "HEAD..origin/main" in " ".join(cmd):
                m.returncode = 0
                m.stdout = "0\n"
            else:
                m.returncode = 0
                m.stdout = "2\n"
            return m
        with patch("subprocess.run", side_effect=fake_run):
            r = _check_fast_forward("main")
        assert r.ok is True

    def test_fail_diverged(self):
        def fake_run(cmd, **kwargs):
            m = MagicMock()
            if "HEAD..origin/main" in " ".join(cmd):
                m.returncode = 0
                m.stdout = "3\n"   # remote has 3 commits local doesn't
            else:
                m.returncode = 0
                m.stdout = "1\n"
            return m
        with patch("subprocess.run", side_effect=fake_run):
            r = _check_fast_forward("main")
        assert r.ok is False
        assert "3" in r.reason

    def test_pass_remote_ref_not_fetched(self):
        mock = MagicMock()
        mock.returncode = 128   # ref not found locally
        with patch("subprocess.run", return_value=mock):
            r = _check_fast_forward("main")
        assert r.ok is True   # graceful skip


# ---------------------------------------------------------------------------
# run_preflight: short-circuit behaviour
# ---------------------------------------------------------------------------

class TestRunPreflightShortCircuit:

    def _good_subprocess(self, *args, **kwargs):
        """Stub that makes all subprocess checks pass."""
        m = MagicMock()
        m.returncode = 0
        m.stdout = "abc123 refs/heads/main\n0\n"
        return m

    def test_short_circuit_at_commit_message(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "tok"}):
            result = run_preflight(commit_message="", branch="main")
        assert result.ready is False
        assert len(result.checks) == 1
        assert result.first_failure.name == CheckName.COMMIT_MESSAGE

    def test_short_circuit_at_token(self):
        env = {k: v for k, v in os.environ.items() if k != "GITHUB_TOKEN"}
        with patch.dict(os.environ, env, clear=True):
            result = run_preflight(commit_message="feat: x", branch="main")
        assert result.ready is False
        assert len(result.checks) == 2
        assert result.first_failure.name == CheckName.TOKEN_SET

    def test_short_circuit_at_remote(self):
        mock = MagicMock()
        mock.returncode = 1
        mock.stderr = "connection refused"
        with patch.dict(os.environ, {"GITHUB_TOKEN": "tok"}):
            with patch("subprocess.run", return_value=mock):
                result = run_preflight(commit_message="feat: x", branch="main")
        assert result.ready is False
        assert result.first_failure.name == CheckName.REMOTE_REACHABLE
        # branch and fast-forward checks never ran
        ran_names = [c.name for c in result.checks]
        assert CheckName.BRANCH_EXISTS not in ran_names
        assert CheckName.FAST_FORWARD not in ran_names

    def test_all_pass(self):
        def fake_run(cmd, **kwargs):
            m = MagicMock()
            m.returncode = 0
            m.stderr = ""
            # rev-list returns a count; ls-remote returns a ref line
            if "rev-list" in cmd:
                m.stdout = "0\n"
            else:
                m.stdout = "abc123 refs/heads/main\n"
            return m
        with patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_tok"}):
            with patch("subprocess.run", side_effect=fake_run):
                result = run_preflight(commit_message="feat: add x", branch="main")
        assert result.ready is True
        assert result.first_failure is None
        assert len(result.checks) == 5


# ---------------------------------------------------------------------------
# Closed vocabulary: unknown check names route to Evaluate
# ---------------------------------------------------------------------------

class TestClosedVocabulary:

    def test_all_check_names_are_known(self):
        """Every check produced by run_preflight must be in CheckName."""
        known = set(c.value for c in CheckName)

        def fake_run(cmd, **kwargs):
            m = MagicMock()
            m.returncode = 0
            m.stdout = "abc refs/heads/main\n0\n"
            m.stderr = ""
            return m

        with patch.dict(os.environ, {"GITHUB_TOKEN": "tok"}):
            with patch("subprocess.run", side_effect=fake_run):
                result = run_preflight(commit_message="feat: x", branch="main")

        for check in result.checks:
            assert check.name in known, f"unknown check name: {check.name}"

    def test_unknown_name_detection(self):
        """Simulate triage routing: unknown name → evaluate."""
        known = set(c.value for c in CheckName)
        unknown_check = PreflightCheck(name="new_thing", ok=False, reason="novel")
        assert unknown_check.name not in known
