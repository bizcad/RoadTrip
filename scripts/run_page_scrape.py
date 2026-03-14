#!/usr/bin/env python3
"""Run page scraper MCP helpers from CLI.

This script wraps mcp_server_page_scraper.py so PowerShell helpers can execute
real scrapes without inline Python snippets.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import mcp_server_page_scraper as scraper


def _parse_bool(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "t", "yes", "y"}:
        return True
    if lowered in {"0", "false", "f", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run page scraper and write markdown")
    parser.add_argument("--url", required=True, help="Source URL")
    parser.add_argument("--output", required=True, help="Destination markdown file path")
    parser.add_argument("--localize-images", type=_parse_bool, default=True)
    parser.add_argument("--prefer-raw", type=_parse_bool, default=True)
    args = parser.parse_args()

    destination = Path(args.output).resolve()
    output_dir = destination.parent

    result = scraper.scrape_page_to_markdown(
        url=args.url,
        output_dir=str(output_dir),
        localize_images=args.localize_images,
        prefer_raw_markdown=args.prefer_raw,
    )

    if result.get("status") != "ok":
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1

    generated = Path(result["output_file"]).resolve()
    if generated != destination:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(generated.read_text(encoding="utf-8"), encoding="utf-8")
        result["output_file"] = str(destination)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
