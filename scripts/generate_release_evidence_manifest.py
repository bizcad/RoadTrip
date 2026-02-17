#!/usr/bin/env python3
"""Generate release evidence manifest from known defaults."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.skills.release_evidence_gate import build_default_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate release evidence manifest")
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root path used to discover default evidence files",
    )
    parser.add_argument(
        "--output",
        default="workflows/010-memory-for-self-improvement/release-evidence-manifest.json",
        help="Output manifest JSON path",
    )
    args = parser.parse_args()

    manifest = build_default_manifest(repo_root=args.repo_root)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Generated manifest: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
