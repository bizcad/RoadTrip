"""Tests for Orchestrator fallback and known-solution recovery behavior."""

from pathlib import Path

from src.orchestrator import Orchestrator


def _write_registry(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "skills:",
                "  git_push_autonomous:",
                "    version: 1.0.0",
                "    description: Primary push skill",
                "    interface: \"execute(input_data: dict) -> dict\"",
                "    status: active",
                "    file: git_push_autonomous.py",
                "  fallback_push:",
                "    version: 1.0.0",
                "    description: Fallback push skill",
                "    interface: \"execute(input_data: dict) -> dict\"",
                "    status: active",
                "    file: fallback_push.py",
                "metadata:",
                "  ready_skills: 2",
                "  discovered_skills: 0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _write_known_solutions(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "solutions:",
                "  - id: auth-fix",
                "    intent: git_push",
                "    title: Fix auth prompt issue",
                "    summary: Configure non-interactive PAT credentials.",
                "    matches:",
                "      error_codes:",
                "        - EXECUTION_FAILED",
                "      message_patterns:",
                "        - \"unable to get password from user\"",
                "    steps:",
                "      - \"Configure credential helper\"",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_run_skill_retries_with_fallback(tmp_path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    (skills_dir / "git_push_autonomous.py").write_text(
        """
def execute(input_data):
    return {"success": False, "reason": "primary failed"}
""".strip()
        + "\n",
        encoding="utf-8",
    )

    (skills_dir / "fallback_push.py").write_text(
        """
def execute(input_data):
    return {"success": True, "decision": "APPROVE"}
""".strip()
        + "\n",
        encoding="utf-8",
    )

    registry = tmp_path / "config" / "skills-registry.yaml"
    _write_registry(registry)

    known = tmp_path / "config" / "known-solutions.yaml"
    _write_known_solutions(known)

    orchestrator = Orchestrator(
        skills_dir=str(skills_dir),
        registry_file=str(registry),
        known_solutions_file=str(known),
        metrics_log_file=str(tmp_path / "logs" / "metrics.jsonl"),
    )

    result = orchestrator.run_skill(
        "git_push_autonomous",
        {"prompt": "push my changes"},
        max_retries=1,
    )

    assert result.status == "SUCCESS"
    assert result.skill_name == "fallback_push"


def test_run_skill_returns_known_solution_on_terminal_failure(tmp_path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    (skills_dir / "git_push_autonomous.py").write_text(
        """
def execute(input_data):
    return {"success": False, "errors": ["fatal: unable to get password from user"]}
""".strip()
        + "\n",
        encoding="utf-8",
    )

    registry = tmp_path / "config" / "skills-registry.yaml"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(
        "\n".join(
            [
                "skills:",
                "  git_push_autonomous:",
                "    version: 1.0.0",
                "    description: Primary push skill",
                "    interface: \"execute(input_data: dict) -> dict\"",
                "    status: active",
                "    file: git_push_autonomous.py",
                "metadata:",
                "  ready_skills: 1",
                "  discovered_skills: 0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    known = tmp_path / "config" / "known-solutions.yaml"
    _write_known_solutions(known)

    orchestrator = Orchestrator(
        skills_dir=str(skills_dir),
        registry_file=str(registry),
        known_solutions_file=str(known),
        metrics_log_file=str(tmp_path / "logs" / "metrics.jsonl"),
    )

    result = orchestrator.run_skill(
        "git_push_autonomous",
        {"prompt": "push my changes"},
        max_retries=0,
    )

    assert result.status == "FAILED"
    assert result.metadata is not None
    assert result.metadata.get("known_solution") is not None
    assert result.metadata["known_solution"]["id"] == "auth-fix"
