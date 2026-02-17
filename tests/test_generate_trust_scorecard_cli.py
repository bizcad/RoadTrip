"""Tests for trust scorecard CLI evidence-map behavior."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.generate_trust_scorecard import load_evidence_map, resolve_evidence_links


def test_load_evidence_map_normalizes_dict(tmp_path: Path):
    payload = {
        "*": {"test_evidence": "tests/all.txt"},
        "blog_publisher": {"security_evidence": "security/blog.json"},
    }
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    loaded = load_evidence_map(str(path))

    assert loaded["*"]["test_evidence"] == "tests/all.txt"
    assert loaded["blog_publisher"]["security_evidence"] == "security/blog.json"


def test_resolve_evidence_links_merges_default_and_skill_overrides():
    evidence_map = {
        "*": {
            "test_evidence": "tests/default.txt",
            "notes": "default note",
        },
        "blog_publisher": {
            "test_evidence": "tests/blog.txt",
            "security_evidence": "security/blog.json",
        },
    }

    resolved = resolve_evidence_links("blog_publisher", evidence_map)

    assert resolved["test_evidence"] == "tests/blog.txt"
    assert resolved["security_evidence"] == "security/blog.json"
    assert resolved["notes"] == "default note"


def test_resolve_evidence_links_defaults_only_for_unknown_skill():
    evidence_map = {
        "*": {
            "test_evidence": "tests/default.txt",
        },
    }

    resolved = resolve_evidence_links("unknown_skill", evidence_map)

    assert resolved["test_evidence"] == "tests/default.txt"
