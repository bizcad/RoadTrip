"""Tests for trust scorecard with mocked gates."""

from __future__ import annotations

from pathlib import Path

from src.skills.trust_scorecard import (
    MockGateProvider,
    build_trust_bundle,
    evaluate_registry,
    evaluate_skill,
    summarize,
)


def test_evaluate_skill_allow_auto_when_all_blocking_pass():
    provider = MockGateProvider()
    metadata = {
        "fingerprint": "abc123",
        "version": "1.0.0",
        "status": "active",
        "test_coverage": 85.0,
        "capabilities": ["publish"],
        "author": "roadtrip_team",
    }

    card = evaluate_skill("blog_publisher", metadata, provider)

    assert card.decision == "ALLOW_AUTO"
    assert card.blocking_failures == []
    assert card.score == card.max_score


def test_evaluate_skill_block_when_mocked_blocking_gate_fails():
    provider = MockGateProvider(
        overrides={
            "blog_publisher": {
                "security_review_passed": {
                    "passed": False,
                    "reason": "mock security failure",
                }
            }
        }
    )
    metadata = {
        "fingerprint": "abc123",
        "version": "1.0.0",
        "status": "active",
        "test_coverage": 85.0,
        "capabilities": ["publish"],
        "author": "roadtrip_team",
    }

    card = evaluate_skill("blog_publisher", metadata, provider)

    assert card.decision == "BLOCK"
    assert "security_review_passed" in card.blocking_failures


def test_evaluate_registry_and_summary(tmp_path: Path):
    registry = tmp_path / "skills-registry.yaml"
    registry.write_text(
        """
skills:
  safe_skill:
    version: 1.0.0
    fingerprint: fff111
    author: roadtrip
    capabilities: [a]
    status: active
    test_coverage: 90.0
  weak_skill:
    version: 1.0.0
    fingerprint: fff222
    author: unknown
    capabilities: []
    status: active
    test_coverage: 20.0
""".strip(),
        encoding="utf-8",
    )

    cards = evaluate_registry(registry_path=str(registry), gate_provider=MockGateProvider())
    summary = summarize(cards)

    assert len(cards) == 2
    assert summary["ALLOW_AUTO"] == 1
    assert summary["BLOCK"] == 1


def test_build_trust_bundle_schema():
    provider = MockGateProvider()
    metadata = {
        "fingerprint": "abc123",
        "version": "1.0.0",
        "status": "active",
        "test_coverage": 85.0,
        "capabilities": ["publish"],
        "author": "roadtrip_team",
    }
    card = evaluate_skill("blog_publisher", metadata, provider)

    bundle = build_trust_bundle(
        scorecard=card,
        release_id="r1",
        registry_path="config/skills-registry.yaml",
        evidence_links={"test_evidence": "tests/test_blog_publisher.py"},
    )

    assert bundle["schema"] == "roadtrip-trust-bundle/v1"
    assert bundle["skill"]["name"] == "blog_publisher"
    assert bundle["decision"]["status"] in {"ALLOW_AUTO", "MANUAL_REVIEW", "BLOCK"}
    assert isinstance(bundle["gate_results"], list)
    assert bundle["evidence"]["test_evidence"] == "tests/test_blog_publisher.py"
