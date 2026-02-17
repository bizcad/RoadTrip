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

from src.skills.trust_scorecard import MockGateProvider, evaluate_registry, summarize


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
    args = parser.parse_args()

    overrides = {}
    if args.mock_profile:
        overrides = json.loads(Path(args.mock_profile).read_text(encoding="utf-8"))

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

    print(f"Scorecard report: {output}")
    print(
        "Summary: "
        f"ALLOW_AUTO={report['summary'].get('ALLOW_AUTO', 0)} "
        f"MANUAL_REVIEW={report['summary'].get('MANUAL_REVIEW', 0)} "
        f"BLOCK={report['summary'].get('BLOCK', 0)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
