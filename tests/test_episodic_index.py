"""Tests for deterministic episodic index retrieval."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from src.skills.episodic_index import EpisodicIndex


def _write_jsonl(path: Path, records: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def test_index_log_file_and_count_events(tmp_path: Path) -> None:
    log_file = tmp_path / "telemetry.jsonl"
    db_file = tmp_path / "telemetry_index.sqlite"

    records = [
        {
            "timestamp": _now_iso(),
            "workflow_id": "run-1",
            "skill": "git_push_autonomous",
            "operation": "push",
            "decision": "ERROR",
            "confidence": 0.4,
            "error_code": "LOCKFILE_EXISTS",
            "reasoning": "Lock file",
        },
        {
            "timestamp": _now_iso(),
            "workflow_id": "run-2",
            "skill": "commit_message",
            "operation": "generate",
            "decision": "APPROVED",
            "confidence": 0.95,
            "reasoning": "Generated message",
        },
    ]
    _write_jsonl(log_file, records)

    index = EpisodicIndex(db_path=str(db_file))
    inserted = index.index_log_file(str(log_file))

    assert inserted == 2
    assert index.count_events() == 2


def test_search_filters_by_skill_and_error_category(tmp_path: Path) -> None:
    log_file = tmp_path / "telemetry.jsonl"
    db_file = tmp_path / "telemetry_index.sqlite"

    records = [
        {
            "timestamp": _now_iso(),
            "workflow_id": "run-1",
            "skill": "git_push_autonomous",
            "operation": "push",
            "decision": "ERROR",
            "confidence": 0.3,
            "error_code": "LOCKFILE_EXISTS",
            "reasoning": "Lock file blocked push",
        },
        {
            "timestamp": _now_iso(),
            "workflow_id": "run-2",
            "skill": "git_push_autonomous",
            "operation": "push",
            "decision": "ERROR",
            "confidence": 0.2,
            "error_code": "REMOTE_DIVERGENCE",
            "reasoning": "Remote divergence",
        },
        {
            "timestamp": _now_iso(),
            "workflow_id": "run-3",
            "skill": "commit_message",
            "operation": "generate",
            "decision": "APPROVED",
            "confidence": 0.99,
            "reasoning": "Generated commit message",
        },
    ]
    _write_jsonl(log_file, records)

    index = EpisodicIndex(db_path=str(db_file))
    index.index_log_file(str(log_file))

    skill_results = index.search(skill_name="git_push_autonomous", limit=10)
    assert len(skill_results) == 2

    error_results = index.search(error_category="LOCKFILE_EXISTS", limit=10)
    assert len(error_results) == 1
    assert error_results[0]["workflow_id"] == "run-1"


def test_needs_memory_retrieval_gate() -> None:
    index = EpisodicIndex(db_path=":memory:")

    assert index.needs_memory_retrieval(explicit_request=True) is True
    assert index.needs_memory_retrieval(error_occurred=True) is True
    assert index.needs_memory_retrieval(dissonance=True) is True
    assert index.needs_memory_retrieval(confidence=0.6) is True

    assert (
        index.needs_memory_retrieval(
            explicit_request=False,
            error_occurred=False,
            dissonance=False,
            confidence=0.95,
        )
        is False
    )
