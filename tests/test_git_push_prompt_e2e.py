"""E2E test: natural-language prompt routes to git-push-autonomous deterministic chain."""

from pathlib import Path
from unittest.mock import MagicMock, patch
import subprocess

from src.skills.git_push_autonomous import execute


def _run_git(repo_path: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=str(repo_path),
        capture_output=True,
        text=True,
        check=False,
    )


def _make_repo(tmp_path):
    """Set up a minimal git repo with one uncommitted file."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()

    _run_git(repo_path, "init")
    _run_git(repo_path, "config", "user.name", "RoadTrip Test")
    _run_git(repo_path, "config", "user.email", "roadtrip@test.local")
    _run_git(repo_path, "remote", "add", "origin", "https://github.com/bizcad/RoadTrip.git")

    config_dir = repo_path / "config"
    config_dir.mkdir()
    (config_dir / "safety-rules.yaml").write_text(
        "blocked_files:\n  - .env\nblocked_patterns: []\nmax_file_size_mb: 50\nallow_override: false\n",
        encoding="utf-8",
    )
    (config_dir / "commit-strategy.yaml").write_text(
        "commit_message:\n  confidence_threshold: 0.85\n  tier2:\n    enabled: false\n",
        encoding="utf-8",
    )
    (repo_path / "README.md").write_text("# Temp Repo\n", encoding="utf-8")
    return repo_path, config_dir


def _preflight_pass_stub(cmd, **kwargs):
    """Stub all git subprocess calls in preflight so no real network needed."""
    m = MagicMock()
    m.returncode = 0
    m.stderr = ""
    m.stdout = "abc123 refs/heads/main\n" if "rev-list" not in cmd else "0\n"
    return m


def test_prompt_push_latest_changes_dry_run(tmp_path, monkeypatch):
    """Full pipeline: prompt → auth → rules → commit → preflight → dryrun success."""
    repo_path, config_dir = _make_repo(tmp_path)
    monkeypatch.setenv("GITHUB_TOKEN", "dummy-token-for-test")

    with patch("src.skills.preflight.subprocess.run", side_effect=_preflight_pass_stub):
        result = execute(
            {
                "prompt": "please push the latest changes",
                "repo_path": str(repo_path),
                "dry_run": True,
                "log_file": str(tmp_path / "telemetry.jsonl"),
                "commit_strategy_path": str(config_dir / "commit-strategy.yaml"),
            }
        )

    assert result["success"] is True, result.get("errors")
    assert result["decision"] == "APPROVE"
    assert result["commit"]["committed"] is True
    # executor result is now under "exec" key
    assert result["exec"]["result"]["preflight"] == "pass"
    assert result["exec"]["result"]["dry_run"] is True


def test_prompt_push_token_missing_escalates_triage(tmp_path, monkeypatch):
    """Missing token → preflight fails → escalate_to=triage in result."""
    repo_path, config_dir = _make_repo(tmp_path)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    result = execute(
        {
            "prompt": "push my changes",
            "repo_path": str(repo_path),
            "dry_run": True,
            "log_file": str(tmp_path / "telemetry.jsonl"),
            "commit_strategy_path": str(config_dir / "commit-strategy.yaml"),
        }
    )

    assert result["success"] is False
    assert result.get("escalate_to") == "triage"
    assert "GITHUB_TOKEN" in str(result.get("errors", ""))


def test_prompt_mismatch_is_skipped():
    result = execute({"prompt": "publish this blog post"})

    assert result["success"] is False
    assert result["decision"] == "SKIPPED"
