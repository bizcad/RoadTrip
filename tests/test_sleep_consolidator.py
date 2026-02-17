"""Tests for deterministic sleep consolidation pipeline."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.skills.consolidation.sleep_consolidator import (
    ConsolidationPipeline,
    SafetyGateValidator,
    SleepConsolidator,
)


def _entry(
    skill: str,
    error: str,
    days_ago: int,
    workflow_id: str,
    decision: str = "ERROR",
) -> dict:
    timestamp = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
    return {
        "timestamp": timestamp,
        "workflow_id": workflow_id,
        "skill": skill,
        "operation": "push",
        "decision": decision,
        "error_code": error,
        "reasoning": "Synthetic test event",
    }


def test_cluster_entries_groups_by_skill_and_error() -> None:
    consolidator = SleepConsolidator()
    entries = [
        _entry("git_push_autonomous", "LOCKFILE_EXISTS", days_ago=0, workflow_id="a"),
        _entry("git_push_autonomous", "LOCKFILE_EXISTS", days_ago=1, workflow_id="b"),
        _entry("commit_message", "EMPTY_STAGED_DIFF", days_ago=0, workflow_id="c"),
    ]

    clusters = consolidator.cluster_entries(entries)

    assert "git_push_autonomous:lockfile_exists" in clusters
    assert "commit_message:empty_staged_diff" in clusters
    assert len(clusters["git_push_autonomous:lockfile_exists"]) == 2


def test_promote_candidates_enforces_multi_criteria_gate() -> None:
    consolidator = SleepConsolidator()
    entries = [
        _entry("git_push_autonomous", "LOCKFILE_EXISTS", days_ago=0, workflow_id="w1"),
        _entry("git_push_autonomous", "LOCKFILE_EXISTS", days_ago=2, workflow_id="w2"),
        _entry("git_push_autonomous", "LOCKFILE_EXISTS", days_ago=3, workflow_id="w3"),
        _entry("git_push_autonomous", "REMOTE_DIVERGENCE", days_ago=0, workflow_id="w1"),
        _entry("git_push_autonomous", "REMOTE_DIVERGENCE", days_ago=1, workflow_id="w1"),
        _entry("git_push_autonomous", "REMOTE_DIVERGENCE", days_ago=2, workflow_id="w1"),
    ]

    clusters = consolidator.cluster_entries(entries)
    candidates = consolidator.promote_candidates(clusters, min_count=3, min_hours=48, min_sources=2)

    keys = [candidate.cluster_key for candidate in candidates]
    assert "git_push_autonomous:lockfile_exists" in keys
    assert "git_push_autonomous:remote_divergence" not in keys


def test_safety_gate_blocks_dangerous_rules() -> None:
    validator = SafetyGateValidator()

    allowed, allowed_reason = validator.validate_rule(
        "[git_push_autonomous] Repeated lockfile_exists observed 3 times; run deterministic pre-checks."
    )
    blocked, blocked_reason = validator.validate_rule(
        "Always run rm -rf on cache before push."
    )

    assert allowed is True
    assert allowed_reason == "ok"
    assert blocked is False
    assert blocked_reason == "destructive_shell_operation"


def test_pipeline_quarantines_unsafe_candidate(tmp_path: Path) -> None:
    entries = [
        _entry("git_push_autonomous", "LOCKFILE_EXISTS", days_ago=0, workflow_id="w1"),
        _entry("git_push_autonomous", "LOCKFILE_EXISTS", days_ago=2, workflow_id="w2"),
        _entry("git_push_autonomous", "LOCKFILE_EXISTS", days_ago=3, workflow_id="w3"),
    ]

    class UnsafeConsolidator(SleepConsolidator):
        def _synthesize_rule(self, skill_name: str, error_category: str, count: int) -> str:
            return "Run rm -rf before pushing."

    quarantine_file = tmp_path / "quarantine.jsonl"
    pipeline = ConsolidationPipeline()
    pipeline.consolidator = UnsafeConsolidator()
    pipeline.quarantine_logger.log_file = quarantine_file

    outcome = pipeline.process(entries)

    assert len(outcome["promoted"]) == 0
    assert len(outcome["quarantined"]) == 1
    assert quarantine_file.exists()

    with open(quarantine_file, "r", encoding="utf-8") as handle:
        row = json.loads(handle.readline())

    assert row["reason"] == "destructive_shell_operation"
