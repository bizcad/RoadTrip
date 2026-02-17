"""Integration tests for WS-E memory loop orchestrator."""

from __future__ import annotations

import json
from pathlib import Path

from src.skills.memory_loop_orchestrator import MemoryLoopOrchestrator


def _write_telemetry(path: Path) -> None:
    rows = [
        {
            "timestamp": "2026-01-01T00:00:00+00:00",
            "skill": "auth_validator",
            "operation": "push",
            "workflow_id": "wf-1",
            "decision": "FAILED",
            "confidence": 0.2,
            "error_code": "token_expired",
            "reasoning": "token expired",
        },
        {
            "timestamp": "2026-01-03T02:00:00+00:00",
            "skill": "auth_validator",
            "operation": "push",
            "workflow_id": "wf-2",
            "decision": "FAILED",
            "confidence": 0.3,
            "error_code": "token_expired",
            "reasoning": "token expired again",
        },
        {
            "timestamp": "2026-01-03T12:00:00+00:00",
            "skill": "auth_validator",
            "operation": "push",
            "workflow_id": "wf-3",
            "decision": "FAILED",
            "confidence": 0.4,
            "error_code": "token_expired",
            "reasoning": "token expired third time",
        },
        {
            "timestamp": "2026-01-04T00:00:00+00:00",
            "skill": "commit_message",
            "operation": "generate",
            "workflow_id": "wf-4",
            "decision": "APPROVED",
            "confidence": 0.9,
            "reasoning": "normal run",
        },
    ]
    with open(path, "w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def _write_memory(path: Path, line_count: int = 20) -> None:
    path.write_text("".join(["line\n" for _ in range(line_count)]), encoding="utf-8")


def _write_skill_dir(root: Path, skill_version: str, claude_version: str) -> str:
    root.mkdir(parents=True, exist_ok=True)
    (root / "SKILL.md").write_text(
        f"---\nversion: {skill_version}\n---\n\n# Skill\n",
        encoding="utf-8",
    )
    (root / "CLAUDE.md").write_text(
        f"**Specs Version**: {claude_version}\n",
        encoding="utf-8",
    )
    return str(root)


def _make_orchestrator(tmp_path: Path) -> tuple[MemoryLoopOrchestrator, Path, Path, Path]:
    telemetry = tmp_path / "telemetry.jsonl"
    memory = tmp_path / "MEMORY.md"
    index_db = tmp_path / "telemetry.sqlite"
    quarantine = tmp_path / "quarantine.jsonl"
    burned = tmp_path / "burned.json"

    _write_telemetry(telemetry)
    _write_memory(memory)

    orchestrator = MemoryLoopOrchestrator(
        telemetry_log=str(telemetry),
        index_db=str(index_db),
        memory_file=str(memory),
        quarantine_log=str(quarantine),
        burned_registry_file=str(burned),
    )
    return orchestrator, telemetry, memory, burned


def test_run_cycle_happy_path_promotes_candidate(tmp_path: Path):
    orchestrator, _, _, _ = _make_orchestrator(tmp_path)
    skill_dir = _write_skill_dir(tmp_path / "skill_ok", "specs-v1.0", "v1.0")

    result = orchestrator.run_cycle(
        operation_text="git status",
        skill_dirs=[skill_dir],
        explicit_request=True,
        query="token_expired",
    )

    assert result.decision == "ALLOW"
    assert result.indexed_count == 4
    assert result.retrieval_needed is True
    assert result.retrieved_count >= 3
    assert len(result.promoted) == 1
    assert result.promoted[0]["cluster_key"] == "auth_validator:token_expired"
    assert result.provenance.all_valid is True


def test_run_cycle_blocks_when_operation_is_irreversible(tmp_path: Path):
    orchestrator, _, _, _ = _make_orchestrator(tmp_path)

    result = orchestrator.run_cycle(operation_text="rm -rf logs")

    assert result.decision == "BLOCK"
    assert result.operation_guard["risk_code"] == "destructive_delete"
    assert result.indexed_count == 0
    assert result.retrieval_needed is False


def test_run_cycle_blocks_on_provenance_mismatch(tmp_path: Path):
    orchestrator, _, _, _ = _make_orchestrator(tmp_path)
    skill_dir = _write_skill_dir(tmp_path / "skill_bad", "specs-v1.1", "v1.0")

    result = orchestrator.run_cycle(
        operation_text="git status",
        skill_dirs=[skill_dir],
        explicit_request=True,
        query="token_expired",
    )

    assert result.decision == "BLOCK"
    assert result.reason == "version provenance verification failed"
    assert result.provenance.all_valid is False
    assert len(result.provenance.results) == 1


def test_run_cycle_respects_burned_pattern_cooldown(tmp_path: Path):
    orchestrator, _, _, _ = _make_orchestrator(tmp_path)
    skill_dir = _write_skill_dir(tmp_path / "skill_ok", "specs-v1.0", "v1.0")

    orchestrator.burned_registry.add(
        pattern_signature="auth_validator:token_expired",
        consolidation_id="cons-1",
        reason="rollback due to bad impact",
        cooldown_days=90,
    )

    result = orchestrator.run_cycle(
        operation_text="git status",
        skill_dirs=[skill_dir],
        explicit_request=True,
        query="token_expired",
    )

    assert result.decision == "ALLOW"
    assert len(result.promoted) == 0
    assert len(result.blocked_by_cooldown) == 1
    assert result.blocked_by_cooldown[0]["cluster_key"] == "auth_validator:token_expired"
