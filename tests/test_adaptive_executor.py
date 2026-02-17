"""Tests for adaptive executor self-correct flow."""

from pathlib import Path

from src.skills.adaptive_executor import AdaptiveExecutor, compute_mock_fingerprint


def _write_registry(registry_path: Path, skills: dict) -> None:
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "metadata:",
        "  registry_version: '1.0'",
    ]

    if not skills:
        lines.append("skills: {}")
        registry_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    lines.append("skills:")

    for skill_name, meta in skills.items():
        lines.extend(
            [
                f"  {skill_name}:",
                f"    version: {meta['version']}",
                f"    fingerprint: {meta['fingerprint']}",
                "    author: test",
                "    capabilities:",
            ]
        )
        for cap in meta.get("capabilities", []):
            lines.append(f"    - {cap}")
        lines.extend(
            [
                "    tests: 0",
                "    test_coverage: 0.0",
                "    status: active",
                "    created: '2026-02-17T00:00:00Z'",
                "    updated: '2026-02-17T00:00:00Z'",
                f"    entry_point: {meta['entry_point']}",
                f"    description: {meta.get('description', skill_name)}",
                "    source_files: []",
            ]
        )

    registry_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_registry_empty_stops(tmp_path):
    repo_root = tmp_path
    registry_path = repo_root / "config" / "skills-registry.yaml"
    _write_registry(registry_path, skills={})

    executor = AdaptiveExecutor(
        repo_root=str(repo_root),
        registry_path="config/skills-registry.yaml",
        metrics_log_path="logs/execution_metrics.jsonl",
        use_mock_fingerprint=True,
    )

    result = executor.execute_prompt("please push the latest changes")

    assert result.success is False
    assert result.error_code == "REGISTRY_EMPTY"


def test_successful_execution_via_registry(tmp_path):
    repo_root = tmp_path
    skill_file = repo_root / "src" / "skills" / "dummy_push.py"
    skill_file.parent.mkdir(parents=True, exist_ok=True)
    skill_file.write_text(
        """
def execute(input_data):
    return {"success": True, "decision": "APPROVE", "source": "dummy"}
""".strip()
        + "\n",
        encoding="utf-8",
    )

    skill_name = "dummy_push"
    version = "1.0.0"
    fingerprint = compute_mock_fingerprint(skill_name, version)

    registry_path = repo_root / "config" / "skills-registry.yaml"
    _write_registry(
        registry_path,
        skills={
            skill_name: {
                "version": version,
                "fingerprint": fingerprint,
                "capabilities": ["push_git_commit"],
                "entry_point": "src/skills/dummy_push.py::execute",
            }
        },
    )

    executor = AdaptiveExecutor(
        repo_root=str(repo_root),
        registry_path="config/skills-registry.yaml",
        metrics_log_path="logs/execution_metrics.jsonl",
        use_mock_fingerprint=True,
    )

    result = executor.execute_prompt("please push the latest changes")

    assert result.success is True
    assert result.skill_name == "dummy_push"
    assert result.attempts == 1


def test_retry_with_fallback_skill(tmp_path):
    repo_root = tmp_path
    skills_dir = repo_root / "src" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    failing_skill = skills_dir / "git_push_autonomous.py"
    failing_skill.write_text(
        """
def execute(input_data):
    return {"success": False, "decision": "REJECT", "reason": "simulated"}
""".strip()
        + "\n",
        encoding="utf-8",
    )

    fallback_skill = skills_dir / "fallback_push.py"
    fallback_skill.write_text(
        """
def execute(input_data):
    return {"success": True, "decision": "APPROVE"}
""".strip()
        + "\n",
        encoding="utf-8",
    )

    registry_path = repo_root / "config" / "skills-registry.yaml"
    _write_registry(
        registry_path,
        skills={
            "git_push_autonomous": {
                "version": "1.0.0",
                "fingerprint": compute_mock_fingerprint("git_push_autonomous", "1.0.0"),
                "capabilities": ["push_git_commit"],
                "entry_point": "src/skills/git_push_autonomous.py::execute",
            },
            "fallback_push": {
                "version": "1.0.0",
                "fingerprint": compute_mock_fingerprint("fallback_push", "1.0.0"),
                "capabilities": ["push_git_commit"],
                "entry_point": "src/skills/fallback_push.py::execute",
            },
        },
    )

    executor = AdaptiveExecutor(
        repo_root=str(repo_root),
        registry_path="config/skills-registry.yaml",
        metrics_log_path="logs/execution_metrics.jsonl",
        use_mock_fingerprint=True,
    )

    result = executor.execute_prompt(
        "push my changes",
        max_retry_depth=1,
    )

    assert result.success is True
    assert result.skill_name == "fallback_push"
    assert result.attempts == 2
