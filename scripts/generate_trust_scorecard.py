#!/usr/bin/env python3
"""Generate trust scorecards for registered skills."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.skills.trust_scorecard import (
    MockGateProvider,
    build_trust_bundle,
    evaluate_registry,
    summarize,
)


def load_evidence_map(path: str) -> dict[str, dict[str, str]]:
    """Load JSON evidence map for trust bundle generation."""

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Evidence map must be a JSON object")

    normalized: dict[str, dict[str, str]] = {}
    for key, value in payload.items():
        if not isinstance(key, str):
            continue
        if not isinstance(value, dict):
            continue
        normalized[key] = {
            str(k): str(v)
            for k, v in value.items()
            if isinstance(k, str) and isinstance(v, str)
        }
    return normalized


def resolve_evidence_links(
    skill_name: str,
    evidence_map: dict[str, dict[str, str]] | None,
) -> dict[str, str]:
    """Resolve evidence links with global defaults and per-skill overrides."""

    if not evidence_map:
        return {}

    merged: dict[str, str] = {}
    defaults = evidence_map.get("*", {})
    if isinstance(defaults, dict):
        merged.update(defaults)

    skill_specific = evidence_map.get(skill_name, {})
    if isinstance(skill_specific, dict):
        merged.update(skill_specific)

    return merged


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate trust scorecards")
    parser.add_argument(
        "--registry",
        default="config/skills-registry.yaml",
        help="Path to skills registry yaml",
    )
    parser.add_argument(
        "--mock-profile",
        default="",
        help="Optional JSON file with mocked gate overrides",
    )
    parser.add_argument(
        "--output",
        default="logs/trust_scorecard.json",
        help="Output report path",
    )
    parser.add_argument(
        "--release-id",
        default="scaffold",
        help="Release identifier stamped into trust bundles",
    )
    parser.add_argument(
        "--manifest-dir",
        default="",
        help="Optional directory to emit per-skill trust manifest JSON files",
    )
    parser.add_argument(
        "--bundle-dir",
        default="",
        help="Deprecated alias for --manifest-dir",
    )
    parser.add_argument(
        "--manifest-evidence-map",
        default="",
        help="Optional JSON manifest map of evidence links keyed by '*' and/or skill name",
    )
    parser.add_argument(
        "--bundle-evidence-map",
        default="",
        help="Deprecated alias for --manifest-evidence-map",
    )
    args = parser.parse_args()

    overrides = {}
    if args.mock_profile:
        overrides = json.loads(Path(args.mock_profile).read_text(encoding="utf-8"))

    if args.manifest_dir and args.bundle_dir:
        raise ValueError("Use either --manifest-dir or --bundle-dir, not both")
    if args.manifest_evidence_map and args.bundle_evidence_map:
        raise ValueError("Use either --manifest-evidence-map or --bundle-evidence-map, not both")

    manifest_dir = args.manifest_dir or args.bundle_dir
    manifest_evidence_map = args.manifest_evidence_map or args.bundle_evidence_map

    evidence_map = {}
    if manifest_evidence_map:
        evidence_map = load_evidence_map(manifest_evidence_map)

    provider = MockGateProvider(overrides=overrides)
    cards = evaluate_registry(registry_path=args.registry, gate_provider=provider)
    report = {
        "summary": summarize(cards),
        "scorecards": [
            {
                **asdict(card),
                "gates": [asdict(gate) for gate in card.gates],
            }
            for card in cards
        ],
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if manifest_dir:
        bundle_dir = Path(manifest_dir)
        bundle_dir.mkdir(parents=True, exist_ok=True)
        for card in cards:
            evidence_links = resolve_evidence_links(card.skill_name, evidence_map)
            bundle = build_trust_bundle(
                scorecard=card,
                release_id=args.release_id,
                registry_path=args.registry,
                evidence_links=evidence_links,
            )
            bundle_path = bundle_dir / f"{card.skill_name}.trust-manifest.json"
            bundle_path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")

    print(f"Scorecard report: {output}")
    if manifest_dir:
        print(f"Trust manifests: {manifest_dir}")
    print(
        "Summary: "
        f"ALLOW_AUTO={report['summary'].get('ALLOW_AUTO', 0)} "
        f"MANUAL_REVIEW={report['summary'].get('MANUAL_REVIEW', 0)} "
        f"BLOCK={report['summary'].get('BLOCK', 0)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
