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


def test_known_solution_retrieval_for_auth_failure(tmp_path):
    repo_root = tmp_path
    skills_dir = repo_root / "src" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    failing_skill = skills_dir / "git_push_autonomous.py"
    failing_skill.write_text(
        """
def execute(input_data):
    return {
        "success": False,
        "errors": ["fatal: unable to get password from user"],
    }
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
            }
        },
    )

    known_solutions = repo_root / "config" / "known-solutions.yaml"
    known_solutions.write_text(
        """
solutions:
  - id: auth-fix
    intent: git_push
    title: Fix auth
    summary: Configure non-interactive credential manager flow.
    matches:
      error_codes:
        - EXECUTION_FAILED
      message_patterns:
        - "unable to get password from user"
    steps:
      - "Set credential helper"
""".strip()
        + "\n",
        encoding="utf-8",
    )

    executor = AdaptiveExecutor(
        repo_root=str(repo_root),
        registry_path="config/skills-registry.yaml",
        metrics_log_path="logs/execution_metrics.jsonl",
        known_solutions_path="config/known-solutions.yaml",
        use_mock_fingerprint=True,
    )

    result = executor.execute_prompt("push my changes", max_retry_depth=0)

    assert result.success is False
    assert result.error_code == "EXECUTION_FAILED"
    assert result.suggested_fix is not None
    assert result.suggested_fix["id"] == "auth-fix"


def test_memory_transition_execution_via_prompt(tmp_path):
    repo_root = tmp_path
    memory_root = repo_root / "data" / "memory"
    src_entry = memory_root / "stores" / "prospective" / "entries" / "task-42"
    src_entry.mkdir(parents=True, exist_ok=True)
    (src_entry / "entry.yaml").write_text("id: task-42\n", encoding="utf-8")

    (memory_root / "manifest.yaml").write_text(
        """
schema_version: "1.0"
stores:
  - id: prospective
    promotion_targets: [working]
    expiration_targets: [episodic]
  - id: working
    promotion_targets: [episodic]
    expiration_targets: [episodic]
""".strip()
        + "\n",
        encoding="utf-8",
    )

    registry_path = repo_root / "config" / "skills-registry.yaml"
    _write_registry(
        registry_path,
        skills={
            "memory_store_transition": {
                "version": "1.0.0",
                "fingerprint": compute_mock_fingerprint("memory_store_transition", "1.0.0"),
                "capabilities": ["memory_store_transition"],
                "entry_point": "src/skills/memory_store_transition.py::execute",
            }
        },
    )

    skill_src = repo_root / "src" / "skills" / "memory_store_transition.py"
    skill_src.parent.mkdir(parents=True, exist_ok=True)
    skill_src.write_text(
        (Path(__file__).parents[1] / "src" / "skills" / "memory_store_transition.py").read_text(
            encoding="utf-8"
        ),
        encoding="utf-8",
    )

    executor = AdaptiveExecutor(
        repo_root=str(repo_root),
        registry_path="config/skills-registry.yaml",
        metrics_log_path="logs/execution_metrics.jsonl",
        use_mock_fingerprint=True,
    )

    result = executor.execute_prompt(
        "promote memory entry task-42 from prospective to working",
        max_retry_depth=0,
    )

    assert result.success is True
    assert result.skill_name == "memory_store_transition"
    assert (memory_root / "stores" / "prospective" / "entries" / "task-42").exists() is False
    assert (memory_root / "stores" / "working" / "entries" / "task-42").exists() is True


def test_list_skills_execution_via_prompt(tmp_path):
    repo_root = tmp_path
    skills_dir = repo_root / "src" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    list_skill_src = repo_root / "src" / "skills" / "registry_list.py"
    list_skill_src.write_text(
        (Path(__file__).parents[1] / "src" / "skills" / "registry_list.py").read_text(
            encoding="utf-8"
        ),
        encoding="utf-8",
    )

    registry_path = repo_root / "config" / "skills-registry.yaml"
    _write_registry(
        registry_path,
        skills={
            "registry_list": {
                "version": "1.0.0",
                "fingerprint": compute_mock_fingerprint("registry_list", "1.0.0"),
                "capabilities": ["registry_list", "list_skills"],
                "entry_point": "src/skills/registry_list.py::execute",
            },
            "dummy_skill": {
                "version": "1.0.0",
                "fingerprint": compute_mock_fingerprint("dummy_skill", "1.0.0"),
                "capabilities": ["other"],
                "entry_point": "src/skills/registry_list.py::execute",
            },
        },
    )

    executor = AdaptiveExecutor(
        repo_root=str(repo_root),
        registry_path="config/skills-registry.yaml",
        metrics_log_path="logs/execution_metrics.jsonl",
        use_mock_fingerprint=True,
    )

    result = executor.execute_prompt("Show me a list of skills", max_retry_depth=0)

    assert result.success is True
    assert result.skill_name == "registry_list"
    assert isinstance(result.output, dict)
    assert "skills" in result.output
    assert "dummy_skill" in result.output["skills"]
    assert "registry_list" in result.output["skills"]
