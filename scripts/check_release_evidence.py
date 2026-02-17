#!/usr/bin/env python3
"""Evaluate release evidence manifest and emit deterministic Go/No-Go."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.skills.release_evidence_gate import evaluate_manifest, write_json_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Check release evidence manifest")
    parser.add_argument(
        "--manifest",
        default="workflows/010-memory-for-self-improvement/release-evidence-manifest.json",
        help="Manifest JSON path",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root for path resolution",
    )
    parser.add_argument(
        "--report",
        default="workflows/010-memory-for-self-improvement/release-evidence-report.json",
        help="Output report path",
    )
    args = parser.parse_args()

    if not Path(args.manifest).exists():
        print(f"Manifest not found: {args.manifest}")
        return 2

    result = evaluate_manifest(manifest_path=args.manifest, repo_root=args.repo_root)
    write_json_report(args.report, result)

    print(f"Decision: {result.decision}")
    print(f"Report: {args.report}")

    if result.decision == "NO-GO":
        if result.missing_required_evidence:
            print("Missing required evidence:", ", ".join(result.missing_required_evidence))
        if result.missing_blocking_telemetry:
            print("Missing blocking telemetry:", ", ".join(result.missing_blocking_telemetry))
        if result.invalid_evidence_files:
            print("Invalid evidence files:", ", ".join(result.invalid_evidence_files))
        if result.invalid_telemetry_files:
            print("Invalid telemetry files:", ", ".join(result.invalid_telemetry_files))
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
