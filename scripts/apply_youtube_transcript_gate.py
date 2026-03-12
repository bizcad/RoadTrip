#!/usr/bin/env python3
"""
apply_youtube_transcript_gate.py - Wire transcript fast-fail into prospective memory.

This script applies the YouTube transcript availability gate to a prospective memory
entry folder and updates metadata/provenance deterministically.

Behavior:
- transcript_available -> metadata status becomes "retrieve_passed"
- no_transcript_available -> metadata status becomes "retrieve_rejected_no_transcript"
- error -> metadata status becomes "retrieve_error"

No ASR fallback is attempted.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from check_youtube_transcript_availability import (
    check_transcript_availability,
    extract_video_id,
    parse_languages,
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def save_yaml(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def first_url_from_text(text: str) -> Optional[str]:
    m = re.search(r"https?://[^\s)]+", text)
    return m.group(0) if m else None


def detect_youtube_url(entry_dir: Path, metadata: Dict[str, Any]) -> Optional[str]:
    # 1) Preferred explicit fields in metadata.
    for key in ("youtube_url", "url", "source_url"):
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    # 2) Scan common entry markdown files.
    for name in ("sensation.md", "research_report.md", "provenance_links.md"):
        p = entry_dir / name
        if p.exists():
            found = first_url_from_text(p.read_text(encoding="utf-8"))
            if found and ("youtube.com" in found.lower() or "youtu.be" in found.lower()):
                return found

    return None


def append_provenance_note(entry_dir: Path, note: str) -> None:
    path = entry_dir / "provenance_links.md"
    stamp = utc_now_iso()
    line = f"- [{stamp}] {note}\n"

    if not path.exists():
        path.write_text("# Provenance Links\n\n" + line, encoding="utf-8")
        return

    content = path.read_text(encoding="utf-8")
    if line.strip() in content:
        return
    path.write_text(content.rstrip() + "\n" + line, encoding="utf-8")


def apply_gate(
    entry_dir: Path,
    url: Optional[str],
    languages_csv: str,
    write: bool,
) -> Dict[str, Any]:
    metadata_path = entry_dir / "metadata.yaml"
    metadata = load_yaml(metadata_path)

    resolved_url = url or detect_youtube_url(entry_dir, metadata)
    if not resolved_url:
        result = {
            "success": False,
            "entry_dir": str(entry_dir),
            "status": "retrieve_error",
            "reason": "youtube_url_not_found",
            "message": "No YouTube URL found in args or entry metadata/files.",
        }
        if write:
            metadata["status"] = "retrieve_error"
            metadata["updated_at"] = utc_now_iso()
            metadata["youtube_retrieval"] = {
                "status": "error",
                "reason": "youtube_url_not_found",
            }
            save_yaml(metadata_path, metadata)
            append_provenance_note(entry_dir, "YouTube transcript gate failed: youtube_url_not_found")
        return result

    video_id = extract_video_id(resolved_url)
    if not video_id:
        result = {
            "success": False,
            "entry_dir": str(entry_dir),
            "status": "retrieve_error",
            "reason": "invalid_youtube_url",
            "url": resolved_url,
        }
        if write:
            metadata["status"] = "retrieve_error"
            metadata["updated_at"] = utc_now_iso()
            metadata["youtube_url"] = resolved_url
            metadata["youtube_retrieval"] = {
                "status": "error",
                "reason": "invalid_youtube_url",
            }
            save_yaml(metadata_path, metadata)
            append_provenance_note(entry_dir, f"YouTube transcript gate failed: invalid URL ({resolved_url})")
        return result

    payload = check_transcript_availability(video_id, parse_languages(languages_csv))
    status = payload.get("status", "error")

    mapped_status = {
        "transcript_available": "retrieve_passed",
        "no_transcript_available": "retrieve_rejected_no_transcript",
        "error": "retrieve_error",
    }.get(status, "retrieve_error")

    result: Dict[str, Any] = {
        "success": status in {"transcript_available", "no_transcript_available"},
        "entry_dir": str(entry_dir),
        "status": mapped_status,
        "url": resolved_url,
        "video_id": video_id,
        "gate": payload,
    }

    if write:
        metadata["status"] = mapped_status
        metadata["updated_at"] = utc_now_iso()
        metadata["youtube_url"] = resolved_url
        metadata["youtube_retrieval"] = payload
        save_yaml(metadata_path, metadata)

        if status == "transcript_available":
            append_provenance_note(entry_dir, f"YouTube transcript gate passed for {resolved_url}")
        elif status == "no_transcript_available":
            append_provenance_note(entry_dir, f"YouTube transcript gate rejected: no transcript available for {resolved_url}")
        else:
            append_provenance_note(entry_dir, f"YouTube transcript gate errored for {resolved_url}: {payload.get('reason')}")

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply YouTube transcript fast-fail gate to a prospective memory entry."
    )
    parser.add_argument(
        "entry_dir",
        help="Path to prospective entry directory (contains metadata.yaml)",
    )
    parser.add_argument(
        "--url",
        default="",
        help="Optional YouTube URL override. If omitted, tries metadata/files.",
    )
    parser.add_argument(
        "--languages",
        default="en,en-US,en-GB",
        help="Comma-separated preferred language codes.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute result without writing metadata/provenance updates.",
    )

    args = parser.parse_args()

    entry_dir = Path(args.entry_dir).resolve()
    if not entry_dir.exists() or not entry_dir.is_dir():
        print(
            json.dumps(
                {
                    "success": False,
                    "status": "retrieve_error",
                    "reason": "entry_dir_not_found",
                    "entry_dir": str(entry_dir),
                },
                indent=2,
            )
        )
        return 1

    result = apply_gate(
        entry_dir=entry_dir,
        url=args.url.strip() or None,
        languages_csv=args.languages,
        write=not args.dry_run,
    )

    print(json.dumps(result, indent=2))

    status = result.get("status", "retrieve_error")
    if status == "retrieve_passed":
        return 0
    if status == "retrieve_rejected_no_transcript":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
