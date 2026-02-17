"""Trust scorecard engine for skills and MCP acquisition gating."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class GateResult:
    gate_name: str
    passed: bool
    blocking: bool
    score_weight: int
    reason: str = ""


@dataclass
class TrustScorecard:
    skill_name: str
    decision: str
    score: int
    max_score: int
    blocking_failures: list[str]
    gates: list[GateResult]


class MockGateProvider:
    """Mock gate provider for deterministic testing and early scaffolding.

    Overrides format:
    {
        "skill_name": {
            "fingerprint_verified": {"passed": False, "reason": "mismatch"},
            "author_reputation": {"passed": True}
        }
    }
    """

    DEFAULT_GATES = [
        {"name": "fingerprint_verified", "blocking": True, "weight": 25},
        {"name": "version_provenance_verified", "blocking": True, "weight": 20},
        {"name": "security_review_passed", "blocking": True, "weight": 20},
        {"name": "test_coverage_minimum", "blocking": True, "weight": 15},
        {"name": "capability_fit", "blocking": False, "weight": 10},
        {"name": "author_reputation", "blocking": False, "weight": 10},
    ]

    def __init__(self, overrides: dict[str, dict[str, dict[str, Any]]] | None = None) -> None:
        self.overrides = overrides or {}

    def evaluate(self, skill_name: str, metadata: dict[str, Any]) -> list[GateResult]:
        skill_overrides = self.overrides.get(skill_name, {})
        results: list[GateResult] = []

        for gate in self.DEFAULT_GATES:
            gate_name = gate["name"]
            blocking = bool(gate["blocking"])
            weight = int(gate["weight"])

            passed, reason = self._default_gate_outcome(gate_name, metadata)

            override = skill_overrides.get(gate_name)
            if isinstance(override, dict):
                if "passed" in override:
                    passed = bool(override["passed"])
                if "reason" in override and isinstance(override["reason"], str):
                    reason = override["reason"]

            results.append(
                GateResult(
                    gate_name=gate_name,
                    passed=passed,
                    blocking=blocking,
                    score_weight=weight,
                    reason=reason,
                )
            )

        return results

    def _default_gate_outcome(self, gate_name: str, metadata: dict[str, Any]) -> tuple[bool, str]:
        if gate_name == "fingerprint_verified":
            value = bool(metadata.get("fingerprint"))
            return value, "fingerprint present" if value else "missing fingerprint"

        if gate_name == "version_provenance_verified":
            version = str(metadata.get("version") or "").strip()
            value = bool(version)
            return value, "version metadata present" if value else "missing version metadata"

        if gate_name == "security_review_passed":
            status = str(metadata.get("status") or "active").lower()
            value = status != "suspended"
            return value, "status acceptable" if value else "skill status is suspended"

        if gate_name == "test_coverage_minimum":
            coverage = float(metadata.get("test_coverage") or 0.0)
            value = coverage >= 70.0
            return value, f"coverage={coverage:.1f}%"

        if gate_name == "capability_fit":
            capabilities = metadata.get("capabilities") or []
            value = len(capabilities) > 0
            return value, "capabilities declared" if value else "no capabilities declared"

        if gate_name == "author_reputation":
            author = str(metadata.get("author") or "").strip().lower()
            value = bool(author and author != "unknown")
            return value, "author identified" if value else "author is unknown"

        return False, "unknown gate"


def evaluate_skill(skill_name: str, metadata: dict[str, Any], gate_provider: MockGateProvider) -> TrustScorecard:
    """Evaluate one skill into a trust decision."""

    gate_results = gate_provider.evaluate(skill_name, metadata)

    max_score = sum(item.score_weight for item in gate_results)
    score = sum(item.score_weight for item in gate_results if item.passed)

    blocking_failures = [item.gate_name for item in gate_results if item.blocking and not item.passed]

    if blocking_failures:
        decision = "BLOCK"
    elif score >= 80:
        decision = "ALLOW_AUTO"
    else:
        decision = "MANUAL_REVIEW"

    return TrustScorecard(
        skill_name=skill_name,
        decision=decision,
        score=score,
        max_score=max_score,
        blocking_failures=blocking_failures,
        gates=gate_results,
    )


def evaluate_registry(
    registry_path: str = "config/skills-registry.yaml",
    gate_provider: MockGateProvider | None = None,
) -> list[TrustScorecard]:
    """Evaluate all registry skills into trust scorecards."""

    provider = gate_provider or MockGateProvider()
    skills = _load_registry_skills(registry_path)
    scorecards = [
        evaluate_skill(skill_name=name, metadata=metadata, gate_provider=provider)
        for name, metadata in sorted(skills.items(), key=lambda pair: pair[0])
    ]
    return scorecards


def summarize(scorecards: list[TrustScorecard]) -> dict[str, int]:
    """Build decision summary counts."""

    buckets = {"ALLOW_AUTO": 0, "MANUAL_REVIEW": 0, "BLOCK": 0}
    for card in scorecards:
        buckets[card.decision] = buckets.get(card.decision, 0) + 1
    return buckets


def _load_registry_skills(registry_path: str) -> dict[str, dict[str, Any]]:
    path = Path(registry_path)
    if not path.exists():
        return {}

    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    skills = payload.get("skills")
    if isinstance(skills, dict):
        return {name: metadata for name, metadata in skills.items() if isinstance(metadata, dict)}
    return {}
