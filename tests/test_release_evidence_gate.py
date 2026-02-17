"""Tests for release evidence gating automation."""

from __future__ import annotations

import json
from pathlib import Path

from src.skills.release_evidence_gate import (
    ADVISORY_EVIDENCE_KEYS,
    BLOCKING_TELEMETRY_KEYS,
    REQUIRED_EVIDENCE_KEYS,
    build_default_manifest,
    evaluate_manifest,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_build_default_manifest_contains_all_required_keys(tmp_path: Path):
    manifest = build_default_manifest(repo_root=str(tmp_path))

    assert sorted(manifest["evidence"].keys()) == sorted(
        REQUIRED_EVIDENCE_KEYS + ADVISORY_EVIDENCE_KEYS
    )
    assert sorted(manifest["telemetry"].keys()) == sorted(BLOCKING_TELEMETRY_KEYS)


def test_build_default_manifest_uses_existing_fallback_candidates(tmp_path: Path):
    _write(
        tmp_path / "workflows/010-memory-for-self-improvement/PDR_COMPLETION_REPORT.md",
        "report",
    )
    _write(tmp_path / "logs/phase2b_audit_log.json", "[]")

    manifest = build_default_manifest(repo_root=str(tmp_path))

    assert manifest["evidence"]["release_decision_record"]["exists"] is True
    assert manifest["evidence"]["release_decision_record"]["source"] == "fallback"
    assert (
        manifest["evidence"]["release_decision_record"]["path"]
        == "workflows/010-memory-for-self-improvement/PDR_COMPLETION_REPORT.md"
    )

    assert manifest["telemetry"]["critical_harm_events"]["exists"] is True
    assert manifest["telemetry"]["critical_harm_events"]["source"] == "fallback"
    assert manifest["telemetry"]["critical_harm_events"]["path"] == "logs/phase2b_audit_log.json"


def test_evaluate_manifest_no_go_when_required_evidence_missing(tmp_path: Path):
    manifest_path = tmp_path / "manifest.json"
    manifest = {
        "evidence": {
            "release_decision_record": {"path": "missing.md"},
        },
        "telemetry": {},
    }
    _write(manifest_path, json.dumps(manifest))

    result = evaluate_manifest(str(manifest_path), repo_root=str(tmp_path))

    assert result.decision == "NO-GO"
    assert "release_decision_record" in result.missing_required_evidence


def test_evaluate_manifest_go_when_all_required_artifacts_exist(tmp_path: Path):
    evidence_paths = {
        key: f"evidence/{key}.md"
        for key in REQUIRED_EVIDENCE_KEYS + ADVISORY_EVIDENCE_KEYS
    }
    telemetry_paths = {
        key: f"telemetry/{key}.jsonl"
        for key in BLOCKING_TELEMETRY_KEYS
    }

    for path in evidence_paths.values():
        _write(tmp_path / path, "ok")

    telemetry_line = json.dumps({"timestamp": "2026-02-16T00:00:00+00:00", "decision": "OK"})
    for path in telemetry_paths.values():
        _write(tmp_path / path, telemetry_line + "\n")

    manifest = {
        "evidence": {key: {"path": path} for key, path in evidence_paths.items()},
        "telemetry": {key: {"path": path} for key, path in telemetry_paths.items()},
    }
    manifest_path = tmp_path / "manifest.json"
    _write(manifest_path, json.dumps(manifest))

    result = evaluate_manifest(str(manifest_path), repo_root=str(tmp_path))

    assert result.decision == "GO"
    assert result.missing_required_evidence == []
    assert result.missing_blocking_telemetry == []
    assert result.invalid_telemetry_files == []


def test_evaluate_manifest_no_go_when_telemetry_invalid(tmp_path: Path):
    manifest_path = tmp_path / "manifest.json"

    evidence = {}
    for key in REQUIRED_EVIDENCE_KEYS + ADVISORY_EVIDENCE_KEYS:
        path = tmp_path / f"evidence/{key}.md"
        _write(path, "ok")
        evidence[key] = {"path": str(path.relative_to(tmp_path)).replace("\\", "/")}

    telemetry = {}
    for key in BLOCKING_TELEMETRY_KEYS:
        path = tmp_path / f"telemetry/{key}.jsonl"
        _write(path, "not-json\n")
        telemetry[key] = {"path": str(path.relative_to(tmp_path)).replace("\\", "/")}

    _write(manifest_path, json.dumps({"evidence": evidence, "telemetry": telemetry}))

    result = evaluate_manifest(str(manifest_path), repo_root=str(tmp_path))

    assert result.decision == "NO-GO"
    assert sorted(result.invalid_telemetry_files) == sorted(BLOCKING_TELEMETRY_KEYS)
