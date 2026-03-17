#!/usr/bin/env python3
"""MCP server for YouTube transcript extraction.

Tools:
- check_transcript
- extract_brief
- extract_transcript_only
"""

from __future__ import annotations

import importlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from scripts.check_youtube_transcript_availability import (  # pylint: disable=import-error
    check_transcript_availability,
    extract_video_id,
    parse_languages,
)
from scripts.extract_youtube_debate_brief import (  # pylint: disable=import-error
    build_document_stem,
    build_analysis_section,
    fetch_transcript_segments,
    fetch_video_metadata,
    frontmatter_block,
    infer_topics,
    sanitize_slug,
    split_sentences,
    summarize_transcript,
    transcript_to_markdown_lines,
    utc_now_iso,
    write_brief,
)

mcp = FastMCP("youtube-transcript")

DEFAULT_TRANSCRIPTS_DIR = str((Path(__file__).resolve().parent / "analysis" / "Transcripts").resolve())


def _resolve_path(path_value: str) -> Path:
    return Path(path_value).resolve()


def _ensure_suffix(stem: str, suffix: str, max_len: int = 120) -> str:
    """Ensure a slug ends with a suffix even after truncation."""
    if stem.endswith(suffix):
        return stem
    base = stem
    if len(base) + len(suffix) > max_len:
        base = base[: max_len - len(suffix)].rstrip("-")
    return f"{base}{suffix}"


def _safe_unlink(path: Path) -> bool:
    if not path.exists():
        return False
    path.unlink()
    return True


def _try_refresh_frontmatter_index() -> dict[str, Any] | None:
    """Best-effort refresh of retrieval index without hard coupling this server.

    Returns None when retrieval server module is unavailable.
    """
    try:
        mod = importlib.import_module("mcp_server_transcript_retrieval")
        return mod.build_transcript_frontmatter_index()  # type: ignore[attr-defined]
    except Exception:
        return None




@mcp.tool()
def check_transcript(url_or_video_id: str, languages_csv: str = "en,en-US,en-GB") -> dict[str, Any]:
    """Check if a YouTube transcript exists. Returns transcript_available/no_transcript_available/error."""
    video_id = extract_video_id(url_or_video_id)
    if not video_id:
        return {
            "status": "error",
            "reason": "invalid_youtube_input",
            "input": url_or_video_id,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

    languages = parse_languages(languages_csv)
    return check_transcript_availability(video_id, languages)


@mcp.tool()
def extract_brief(
    url_or_video_id: str,
    output_dir: str = DEFAULT_TRANSCRIPTS_DIR,
    languages_csv: str = "en,en-US,en-GB",
    cleanup_transcript_only: bool = True,
    refresh_index: bool = True,
) -> dict[str, Any]:
    """Extract transcript and generate full brief with frontmatter + Transcription + Summary + Analysis."""
    video_id = extract_video_id(url_or_video_id)
    if not video_id:
        return {"status": "error", "reason": "invalid_youtube_input", "input": url_or_video_id}

    languages = parse_languages(languages_csv)
    availability = check_transcript_availability(video_id, languages)
    if availability.get("status") != "transcript_available":
        return availability

    metadata = fetch_video_metadata(video_id)
    segments, transcript_details = fetch_transcript_segments(video_id, languages)
    if not segments:
        return {
            "status": "no_transcript_available",
            "reason": "empty_transcript_after_fetch",
            "video_id": video_id,
        }

    full_text = " ".join(seg.text for seg in segments)
    sentences = split_sentences(full_text)
    topics = infer_topics(full_text)

    title = metadata.get("title") or f"YouTube-{video_id}"
    creator = metadata.get("creator") or "Unknown"
    file_stem = build_document_stem(
        creator=creator,
        upload_date=str(metadata.get("upload_date") or ""),
        title=title,
    )
    transcript_stem = _ensure_suffix(file_stem, "-transcript")
    output_base = _resolve_path(output_dir)

    out_path = write_brief(
        output_dir=output_base,
        file_stem=file_stem,
        frontmatter={
            "source_type": "youtube_video",
            "video_url": metadata.get("watch_url"),
            "video_id": video_id,
            "title": title,
            "creator": creator,
            "upload_date": metadata.get("upload_date") or "",
            "retrieved_at_utc": utc_now_iso(),
            "transcript_available": True,
            "transcript_language_requested": languages,
            "transcript_language_selected": transcript_details.get("language_selected"),
            "transcript_is_generated": transcript_details.get("is_generated"),
            "transcript_segment_count": transcript_details.get("segment_count", len(segments)),
            "video_duration_seconds": metadata.get("duration_seconds"),
            "topics_detected": topics,
            "generator_mcp_server": "mcp_server_youtube_transcript.py",
        },
        transcription_lines=transcript_to_markdown_lines(segments),
        summary_lines=summarize_transcript(sentences, len(segments)),
        analysis_lines=build_analysis_section(sentences, topics),
    )

    deleted_transcript_file = None
    if cleanup_transcript_only:
        transcript_path = output_base / f"{transcript_stem}.md"
        if _safe_unlink(transcript_path):
            deleted_transcript_file = str(transcript_path)

    refreshed_index = None
    if refresh_index:
        refreshed_index = _try_refresh_frontmatter_index()

    return {
        "status": "ok",
        "video_id": video_id,
        "output_file": str(out_path),
        "segment_count": len(segments),
        "title": title,
        "creator": creator,
        "deleted_transcript_file": deleted_transcript_file,
        "index_refresh": refreshed_index,
    }


@mcp.tool()
def extract_transcript_only(
    url_or_video_id: str,
    output_dir: str = DEFAULT_TRANSCRIPTS_DIR,
    languages_csv: str = "en,en-US,en-GB",
) -> dict[str, Any]:
    """Extract transcript only into a markdown file with frontmatter + Transcription section."""
    video_id = extract_video_id(url_or_video_id)
    if not video_id:
        return {"status": "error", "reason": "invalid_youtube_input", "input": url_or_video_id}

    languages = parse_languages(languages_csv)
    availability = check_transcript_availability(video_id, languages)
    if availability.get("status") != "transcript_available":
        return availability

    metadata = fetch_video_metadata(video_id)
    segments, transcript_details = fetch_transcript_segments(video_id, languages)
    if not segments:
        return {
            "status": "no_transcript_available",
            "reason": "empty_transcript_after_fetch",
            "video_id": video_id,
        }

    title = metadata.get("title") or f"YouTube-{video_id}"
    creator = metadata.get("creator") or "Unknown"
    file_stem = build_document_stem(
        creator=creator,
        upload_date=str(metadata.get("upload_date") or ""),
        title=title,
    )
    file_stem = _ensure_suffix(file_stem, "-transcript")

    frontmatter = {
        "source_type": "youtube_video",
        "video_url": metadata.get("watch_url"),
        "video_id": video_id,
        "title": title,
        "creator": creator,
        "upload_date": metadata.get("upload_date") or "",
        "retrieved_at_utc": utc_now_iso(),
        "transcript_available": True,
        "transcript_language_requested": languages,
        "transcript_language_selected": transcript_details.get("language_selected"),
        "transcript_is_generated": transcript_details.get("is_generated"),
        "transcript_segment_count": transcript_details.get("segment_count", len(segments)),
        "video_duration_seconds": metadata.get("duration_seconds"),
        "generator_mcp_server": "mcp_server_youtube_transcript.py",
    }

    output_path = _resolve_path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    out_file = output_path / f"{file_stem}.md"

    text = "\n".join(
        [
            frontmatter_block(frontmatter),
            "",
            "# YouTube Transcript",
            "",
            "## Transcription",
            *transcript_to_markdown_lines(segments),
            "",
        ]
    )
    out_file.write_text(text, encoding="utf-8")

    return {
        "status": "ok",
        "video_id": video_id,
        "output_file": str(out_file),
        "segment_count": len(segments),
        "title": title,
        "creator": creator,
    }


if __name__ == "__main__":
    mcp.run()
