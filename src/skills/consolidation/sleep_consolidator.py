"""Deterministic sleep consolidation pipeline.

Implements offline clustering, promotion gating, safety filtering, and quarantine
logging for memory-rule candidate generation.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


FAILURE_DECISIONS = {"DENIED", "ERROR", "FAILED", "BLOCKED"}


@dataclass
class ConsolidationCandidate:
    """Promotable consolidated pattern candidate."""

    cluster_key: str
    skill_name: str
    error_category: str
    count: int
    time_span_hours: float
    source_count: int
    first_seen: str
    last_seen: str
    synthesized_rule: str


class SleepConsolidator:
    """Builds deterministic clusters and promotion candidates."""

    def cluster_entries(self, entries: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        """Group telemetry anomalies by deterministic key."""

        clusters: dict[str, list[dict[str, Any]]] = {}

        for entry in entries:
            if not self._is_anomaly(entry):
                continue

            skill_name = str(entry.get("skill") or "unknown_skill")
            error_category = self._normalize_error_category(entry)
            cluster_key = f"{skill_name}:{error_category}"

            clusters.setdefault(cluster_key, []).append(entry)

        return clusters

    def promote_candidates(
        self,
        clusters: dict[str, list[dict[str, Any]]],
        min_count: int = 3,
        min_hours: float = 48.0,
        min_sources: int = 2,
    ) -> list[ConsolidationCandidate]:
        """Apply deterministic multi-criteria gate to clusters."""

        candidates: list[ConsolidationCandidate] = []

        for cluster_key, items in clusters.items():
            if len(items) < min_count:
                continue

            timestamps = [self._parse_timestamp(item.get("timestamp")) for item in items]
            valid_timestamps = [stamp for stamp in timestamps if stamp is not None]
            if not valid_timestamps:
                continue

            first_seen = min(valid_timestamps)
            last_seen = max(valid_timestamps)
            span_hours = (last_seen - first_seen).total_seconds() / 3600.0
            if span_hours < min_hours:
                continue

            sources = {
                str(item.get("workflow_id") or item.get("decision_id") or "unknown")
                for item in items
            }
            source_count = len(sources)
            if source_count < min_sources:
                continue

            skill_name, error_category = cluster_key.split(":", maxsplit=1)
            candidates.append(
                ConsolidationCandidate(
                    cluster_key=cluster_key,
                    skill_name=skill_name,
                    error_category=error_category,
                    count=len(items),
                    time_span_hours=round(span_hours, 2),
                    source_count=source_count,
                    first_seen=first_seen.isoformat(),
                    last_seen=last_seen.isoformat(),
                    synthesized_rule=self._synthesize_rule(skill_name, error_category, len(items)),
                )
            )

        return sorted(candidates, key=lambda item: (item.skill_name, item.error_category))

    def _is_anomaly(self, entry: dict[str, Any]) -> bool:
        decision = str(entry.get("decision", "")).upper()
        if decision in FAILURE_DECISIONS:
            return True
        return bool(entry.get("error_code") or entry.get("error_category"))

    def _normalize_error_category(self, entry: dict[str, Any]) -> str:
        raw = str(entry.get("error_code") or entry.get("error_category") or "unknown")
        value = raw.strip().lower().replace(" ", "_")
        value = re.sub(r"[^a-z0-9_\-]", "", value)
        return value or "unknown"

    def _parse_timestamp(self, value: Any) -> datetime | None:
        if not isinstance(value, str) or not value:
            return None
        candidate = value.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(candidate)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    def _synthesize_rule(self, skill_name: str, error_category: str, count: int) -> str:
        return (
            f"[{skill_name}] Repeated {error_category} observed {count} times; "
            "run deterministic pre-checks and abort if risk indicators are present."
        )


class SafetyGateValidator:
    """Semantic safety gate for consolidated rules."""

    BLOCK_PATTERNS = {
        r"rm\s+-rf": "destructive_shell_operation",
        r"delete\s+.*\.git": "git_integrity_risk",
        r"git\s+push\s+--force": "history_rewrite_risk",
        r"disable\s+.*safety": "policy_bypass_risk",
    }

    def validate_rule(self, rule: str) -> tuple[bool, str]:
        for pattern, reason in self.BLOCK_PATTERNS.items():
            if re.search(pattern, rule, flags=re.IGNORECASE):
                return False, reason
        return True, "ok"


class QuarantineLogger:
    """Append-only quarantine log writer for rejected candidates."""

    def __init__(self, log_file: str = "logs/consolidation_quarantine.jsonl") -> None:
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def write(self, candidate: ConsolidationCandidate, reason: str) -> None:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cluster_key": candidate.cluster_key,
            "skill_name": candidate.skill_name,
            "error_category": candidate.error_category,
            "count": candidate.count,
            "time_span_hours": candidate.time_span_hours,
            "source_count": candidate.source_count,
            "synthesized_rule": candidate.synthesized_rule,
            "reason": reason,
        }
        with open(self.log_file, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, separators=(",", ":")) + "\n")


class ConsolidationPipeline:
    """End-to-end deterministic consolidation processing."""

    def __init__(
        self,
        validator: SafetyGateValidator | None = None,
        quarantine_logger: QuarantineLogger | None = None,
    ) -> None:
        self.consolidator = SleepConsolidator()
        self.validator = validator or SafetyGateValidator()
        self.quarantine_logger = quarantine_logger or QuarantineLogger()

    def process(self, entries: list[dict[str, Any]]) -> dict[str, list[ConsolidationCandidate]]:
        clusters = self.consolidator.cluster_entries(entries)
        candidates = self.consolidator.promote_candidates(clusters)

        promoted: list[ConsolidationCandidate] = []
        quarantined: list[ConsolidationCandidate] = []

        for candidate in candidates:
            is_safe, reason = self.validator.validate_rule(candidate.synthesized_rule)
            if is_safe:
                promoted.append(candidate)
            else:
                quarantined.append(candidate)
                self.quarantine_logger.write(candidate, reason)

        return {
            "promoted": promoted,
            "quarantined": quarantined,
        }
