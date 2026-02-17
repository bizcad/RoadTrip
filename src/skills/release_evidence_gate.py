"""Release evidence collection and Go/No-Go gate evaluation."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_EVIDENCE_KEYS = [
    "release_decision_record",
    "h2_validation_evidence",
    "integration_test_evidence",
    "adversarial_test_evidence",
    "performance_test_evidence",
    "security_test_evidence",
    "safety_gate_quarantine_evidence",
    "cost_telemetry_evidence",
    "memory_ceiling_pruning_evidence",
    "trust_boundary_compliance_evidence",
    "version_provenance_package",
    "irreversible_risk_evidence_package",
]

ADVISORY_EVIDENCE_KEYS = [
    "rollback_cooldown_evidence",
    "advisory_risk_acceptance_notes",
]

BLOCKING_TELEMETRY_KEYS = [
    "critical_harm_events",
    "safety_gate_effectiveness",
    "trust_boundary_compliance",
    "consolidation_spend_compliance",
    "memory_ceiling_compliance",
    "irreversible_operation_protection",
]

DEFAULT_EVIDENCE_PATHS = {
    "release_decision_record": "workflows/010-memory-for-self-improvement/release-decision.md",
    "h2_validation_evidence": "workflows/010-memory-for-self-improvement/H2-validation-evidence.md",
    "integration_test_evidence": "test_results.txt",
    "adversarial_test_evidence": "workflows/010-memory-for-self-improvement/adversarial-test-evidence.md",
    "performance_test_evidence": "workflows/010-memory-for-self-improvement/performance-test-evidence.md",
    "security_test_evidence": "workflows/010-memory-for-self-improvement/security-test-evidence.md",
    "safety_gate_quarantine_evidence": "logs/consolidation_quarantine.jsonl",
    "cost_telemetry_evidence": "logs/cost_telemetry.jsonl",
    "memory_ceiling_pruning_evidence": "logs/memory_ceiling.jsonl",
    "trust_boundary_compliance_evidence": "logs/trust_boundary_checks.jsonl",
    "version_provenance_package": "workflows/010-memory-for-self-improvement/VERSION-PROVENANCE-PACKAGE-CHECKLIST.md",
    "irreversible_risk_evidence_package": "logs/irreversible_guardrails.jsonl",
    "rollback_cooldown_evidence": "logs/burned_patterns.json",
    "advisory_risk_acceptance_notes": "workflows/010-memory-for-self-improvement/risk-acceptance-notes.md",
}

EVIDENCE_CANDIDATE_PATHS = {
    "release_decision_record": [
        "workflows/010-memory-for-self-improvement/PDR_COMPLETION_REPORT.md",
        "PHASE_3_COMPLETION_REPORT.md",
    ],
    "h2_validation_evidence": [
        "workflows/010-memory-for-self-improvement/PRD-v2.1-AMENDMENTS.md",
        "workflows/010-memory-for-self-improvement/PRD-self-improvement-engine-v2.md",
    ],
    "integration_test_evidence": [
        "tests/test_phase_3_integration.py",
        "tests/test_memory_loop_orchestrator.py",
    ],
    "adversarial_test_evidence": [
        "workflows/010-memory-for-self-improvement/design-session-adversarial-loop.md",
        "workflows/010-memory-for-self-improvement/adversarial-research-plan-codex_5_2.md",
        "workflows/010-memory-for-self-improvement/adversarial-research-plan-gemini-3.md",
    ],
    "performance_test_evidence": [
        "test_results.txt",
        "tests/test_phase_3_dag.py",
    ],
    "security_test_evidence": [
        "config/safety-rules.yaml",
        "tests/test_memory_guardrails.py",
    ],
    "safety_gate_quarantine_evidence": [
        "tests/test_sleep_consolidator.py",
        "src/skills/consolidation/sleep_consolidator.py",
    ],
    "cost_telemetry_evidence": [
        "docs/How to cut OpenClaw Costs.md",
    ],
    "memory_ceiling_pruning_evidence": [
        "tests/test_memory_guardrails.py",
        "src/skills/consolidation/guardrails.py",
    ],
    "trust_boundary_compliance_evidence": [
        "logs/registry_snapshot.json",
        "tests/test_registry_system.py",
    ],
    "version_provenance_package": [
        "tests/test_version_provenance.py",
    ],
    "irreversible_risk_evidence_package": [
        "tests/test_memory_guardrails.py",
        "src/skills/consolidation/guardrails.py",
    ],
    "rollback_cooldown_evidence": [
        "src/skills/consolidation/burned_patterns.py",
    ],
    "advisory_risk_acceptance_notes": [
        "workflows/010-memory-for-self-improvement/PDR_COMPLETION_REPORT.md",
    ],
}

DEFAULT_TELEMETRY_PATHS = {
    "critical_harm_events": "logs/safety_audit.jsonl",
    "safety_gate_effectiveness": "logs/consolidation_quarantine.jsonl",
    "trust_boundary_compliance": "logs/trust_boundary_checks.jsonl",
    "consolidation_spend_compliance": "logs/cost_telemetry.jsonl",
    "memory_ceiling_compliance": "logs/memory_ceiling.jsonl",
    "irreversible_operation_protection": "logs/irreversible_guardrails.jsonl",
}

TELEMETRY_CANDIDATE_PATHS = {
    "critical_harm_events": [
        "logs/phase2b_audit_log.json",
    ],
    "safety_gate_effectiveness": [
        "logs/phase2b_audit_summary.json",
    ],
    "trust_boundary_compliance": [
        "logs/registry_snapshot.json",
        "logs/phase2b_compliance_report.json",
    ],
    "consolidation_spend_compliance": [
        "logs/phase2b_compliance_report.json",
    ],
    "memory_ceiling_compliance": [
        "tests/test_memory_guardrails.py",
    ],
    "irreversible_operation_protection": [
        "tests/test_memory_guardrails.py",
    ],
}


@dataclass
class GateEvaluationResult:
    decision: str
    missing_required_evidence: list[str]
    missing_blocking_telemetry: list[str]
    missing_advisory_evidence: list[str]
    invalid_evidence_files: list[str]
    invalid_telemetry_files: list[str]
    checked_at: str


def build_default_manifest(repo_root: str = ".") -> dict[str, Any]:
    """Build a release-evidence manifest with discovered defaults."""

    root = Path(repo_root)
    evidence: dict[str, Any] = {}
    for key in REQUIRED_EVIDENCE_KEYS + ADVISORY_EVIDENCE_KEYS:
        relative_path, source = _discover_path(
            root=root,
            default_path=DEFAULT_EVIDENCE_PATHS[key],
            candidates=EVIDENCE_CANDIDATE_PATHS.get(key, []),
        )
        full_path = root / relative_path
        evidence[key] = {
            "path": relative_path,
            "exists": full_path.exists(),
            "source": source,
        }

    telemetry: dict[str, Any] = {}
    for key in BLOCKING_TELEMETRY_KEYS:
        relative_path, source = _discover_path(
            root=root,
            default_path=DEFAULT_TELEMETRY_PATHS[key],
            candidates=TELEMETRY_CANDIDATE_PATHS.get(key, []),
        )
        full_path = root / relative_path
        telemetry[key] = {
            "path": relative_path,
            "exists": full_path.exists(),
            "source": source,
        }

    return {
        "spec": "release-evidence-manifest/v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "release_window": {
            "start": None,
            "end": None,
        },
        "evidence": evidence,
        "telemetry": telemetry,
    }


def evaluate_manifest(manifest_path: str, repo_root: str = ".") -> GateEvaluationResult:
    """Evaluate release evidence manifest into deterministic Go/No-Go decision."""

    root = Path(repo_root)
    payload = json.loads(Path(manifest_path).read_text(encoding="utf-8"))

    evidence_map = payload.get("evidence") or {}
    telemetry_map = payload.get("telemetry") or {}

    missing_required_evidence: list[str] = []
    invalid_evidence_files: list[str] = []
    for key in REQUIRED_EVIDENCE_KEYS:
        entry = evidence_map.get(key) or {}
        path = str(entry.get("path") or "").strip()
        if not path:
            missing_required_evidence.append(key)
            continue

        full_path = root / path
        if not full_path.exists():
            missing_required_evidence.append(key)
            continue

        if not _is_non_empty(full_path):
            invalid_evidence_files.append(key)

    missing_advisory_evidence: list[str] = []
    for key in ADVISORY_EVIDENCE_KEYS:
        entry = evidence_map.get(key) or {}
        path = str(entry.get("path") or "").strip()
        if not path:
            missing_advisory_evidence.append(key)
            continue
        if not (root / path).exists():
            missing_advisory_evidence.append(key)

    missing_blocking_telemetry: list[str] = []
    invalid_telemetry_files: list[str] = []
    for key in BLOCKING_TELEMETRY_KEYS:
        entry = telemetry_map.get(key) or {}
        path = str(entry.get("path") or "").strip()
        if not path:
            missing_blocking_telemetry.append(key)
            continue

        full_path = root / path
        if not full_path.exists():
            missing_blocking_telemetry.append(key)
            continue

        valid, has_records = _validate_telemetry_file(full_path)
        if not valid:
            invalid_telemetry_files.append(key)
        elif not has_records:
            missing_blocking_telemetry.append(key)

    decision = "GO"
    if (
        missing_required_evidence
        or invalid_evidence_files
        or missing_blocking_telemetry
        or invalid_telemetry_files
    ):
        decision = "NO-GO"

    return GateEvaluationResult(
        decision=decision,
        missing_required_evidence=sorted(missing_required_evidence),
        missing_blocking_telemetry=sorted(missing_blocking_telemetry),
        missing_advisory_evidence=sorted(missing_advisory_evidence),
        invalid_evidence_files=sorted(invalid_evidence_files),
        invalid_telemetry_files=sorted(invalid_telemetry_files),
        checked_at=datetime.now(timezone.utc).isoformat(),
    )


def write_json_report(output_path: str, result: GateEvaluationResult) -> None:
    """Write GateEvaluationResult to JSON report file."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")


def _is_non_empty(path: Path) -> bool:
    return path.exists() and path.stat().st_size > 0


def _validate_telemetry_file(path: Path) -> tuple[bool, bool]:
    suffix = path.suffix.lower()

    if suffix == ".jsonl":
        has_any = False
        with open(path, "r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if not stripped:
                    continue
                has_any = True
                try:
                    payload = json.loads(stripped)
                except json.JSONDecodeError:
                    return False, False
                if not isinstance(payload, dict):
                    return False, False
        return True, has_any

    if suffix == ".json":
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return False, False

        if isinstance(payload, list):
            return True, len(payload) > 0
        if isinstance(payload, dict):
            return True, len(payload) > 0
        return False, False

    # For markdown/txt or unknown files, non-empty counts as telemetry present.
    return True, _is_non_empty(path)


def _discover_path(root: Path, default_path: str, candidates: list[str]) -> tuple[str, str]:
    preferred = [default_path, *candidates]
    for item in preferred:
        if (root / item).exists():
            if item == default_path:
                return item, "default"
            return item, "fallback"
    return default_path, "missing"
