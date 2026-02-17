"""E2E test: natural-language prompt routes to git-push-autonomous deterministic chain."""

from pathlib import Path
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


def test_prompt_push_latest_changes_dry_run(tmp_path, monkeypatch):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()

    _run_git(repo_path, "init")
    _run_git(repo_path, "config", "user.name", "RoadTrip Test")
    _run_git(repo_path, "config", "user.email", "roadtrip@test.local")
    _run_git(repo_path, "remote", "add", "origin", "https://github.com/bizcad/RoadTrip.git")

    config_dir = repo_path / "config"
    config_dir.mkdir()

    (config_dir / "safety-rules.yaml").write_text(
        """
blocked_files:
  - .env
blocked_patterns:
  - ".*\\\\.secrets$"
  - "(^|/)node_modules(/|$)"
max_file_size_mb: 50
allow_override: false
""".strip()
        + "\n",
        encoding="utf-8",
    )

    (config_dir / "commit-strategy.yaml").write_text(
        """
commit_message:
  confidence_threshold: 0.85
  tier2:
    enabled: false
""".strip()
        + "\n",
        encoding="utf-8",
    )

    readme = repo_path / "README.md"
    readme.write_text("# Temp Repo\n", encoding="utf-8")

    monkeypatch.setenv("GITHUB_TOKEN", "dummy-token-for-test")

    result = execute(
        {
            "prompt": "please push the latest changes",
            "repo_path": str(repo_path),
            "dry_run": True,
            "log_file": str(tmp_path / "telemetry.jsonl"),
            "commit_strategy_path": str(config_dir / "commit-strategy.yaml"),
        }
    )

    assert result["success"] is True
    assert result["decision"] == "APPROVE"
    assert result["commit"]["committed"] is True
    assert result["push"]["commit_count"] >= 1


def test_prompt_mismatch_is_skipped():
    result = execute({"prompt": "publish this blog post"})

    assert result["success"] is False
    assert result["decision"] == "SKIPPED"
