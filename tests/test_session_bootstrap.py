"""Tests for deterministic session bootstrap context loading."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.skills.session_bootstrap import SessionBootstrap


def _write_jsonl(path: Path, records: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")


def _iso(days_ago: int = 0) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()


def test_load_context_returns_empty_defaults_for_missing_file(tmp_path: Path) -> None:
    bootstrap = SessionBootstrap()

    context = bootstrap.load_context(log_file=str(tmp_path / "missing.jsonl"))

    assert context["recent_failures"] == []
    assert context["active_skills"] == []
    assert context["pending_reminders"] == []
    assert context["trip_context"]["enabled"] is False


def test_load_context_builds_recent_failures_and_active_skills(tmp_path: Path) -> None:
    log_file = tmp_path / "telemetry.jsonl"
    records = [
        {
            "timestamp": _iso(0),
            "workflow_id": "run-1",
            "skill": "git_push_autonomous",
            "operation": "push",
            "decision": "ERROR",
            "error_code": "LOCKFILE_EXISTS",
            "reasoning": "Lock file blocked push",
        },
        {
            "timestamp": _iso(1),
            "workflow_id": "run-2",
            "skill": "git_push_autonomous",
            "operation": "push",
            "decision": "APPROVED",
            "reasoning": "Push completed",
        },
        {
            "timestamp": _iso(2),
            "workflow_id": "run-3",
            "skill": "commit_message",
            "operation": "generate",
            "decision": "DENIED",
            "error_code": "EMPTY_STAGED_DIFF",
            "reasoning": "No staged files",
        },
        {
            "timestamp": _iso(40),
            "workflow_id": "run-old",
            "skill": "rules_engine",
            "operation": "validate",
            "decision": "ERROR",
            "error_code": "OLD_EVENT",
            "reasoning": "Should be out of active window",
        },
    ]
    _write_jsonl(log_file, records)

    bootstrap = SessionBootstrap()
    context = bootstrap.load_context(
        log_file=str(log_file),
        recent_days=7,
        recent_failures_limit=3,
        active_window_days=30,
        active_skills_limit=5,
    )

    failures = context["recent_failures"]
    assert len(failures) == 2
    assert failures[0]["error_code"] == "LOCKFILE_EXISTS"
    assert {row["skill"] for row in failures} == {"git_push_autonomous", "commit_message"}

    active_skills = context["active_skills"]
    assert active_skills[0]["skill"] == "git_push_autonomous"
    assert active_skills[0]["count"] == 2


def test_load_context_failure_limit_is_respected(tmp_path: Path) -> None:
    log_file = tmp_path / "telemetry.jsonl"
    records = [
        {
            "timestamp": _iso(index),
            "workflow_id": f"run-{index}",
            "skill": "git_push_autonomous",
            "operation": "push",
            "decision": "ERROR",
            "error_code": f"E{index}",
            "reasoning": "Failure",
        }
        for index in range(6)
    ]
    _write_jsonl(log_file, records)

    bootstrap = SessionBootstrap()
    context = bootstrap.load_context(
        log_file=str(log_file),
        recent_days=10,
        recent_failures_limit=3,
    )

    assert len(context["recent_failures"]) == 3
