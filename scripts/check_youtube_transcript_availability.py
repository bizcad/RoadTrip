#!/usr/bin/env python3
"""
check_youtube_transcript_availability.py - Fast-fail YouTube transcript precheck.

Given a YouTube URL or video ID, this script checks whether a transcript/captions
track is available. It is deterministic-first: if no transcript is available,
it exits immediately with `no_transcript_available` and does not attempt ASR.

Exit codes:
- 0: transcript_available
- 2: no_transcript_available
- 1: error
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse


def utc_now_iso() -> str:
    """Return current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


def extract_video_id(value: str) -> Optional[str]:
    """Extract a YouTube video ID from URL or pass through a valid raw ID."""
    candidate = value.strip()
    if not candidate:
        return None

    # Direct video ID path.
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", candidate):
        return candidate

    parsed = urlparse(candidate)
    host = (parsed.netloc or "").lower()
    path = (parsed.path or "").strip("/")

    if host in {"youtu.be", "www.youtu.be"}:
        short_id = path.split("/")[0]
        if re.fullmatch(r"[A-Za-z0-9_-]{11}", short_id):
            return short_id

    if "youtube.com" in host:
        query = parse_qs(parsed.query or "")
        watch_id = (query.get("v") or [None])[0]
        if watch_id and re.fullmatch(r"[A-Za-z0-9_-]{11}", watch_id):
            return watch_id

        # Support /embed/{id}, /shorts/{id}, /live/{id}
        parts = [p for p in path.split("/") if p]
        if len(parts) >= 2 and parts[0] in {"embed", "shorts", "live"}:
            if re.fullmatch(r"[A-Za-z0-9_-]{11}", parts[1]):
                return parts[1]

    return None


def parse_languages(raw_languages: str) -> List[str]:
    """Parse language CSV into an ordered list, defaulting to English variants."""
    if not raw_languages.strip():
        return ["en", "en-US", "en-GB"]

    langs: List[str] = []
    for token in raw_languages.split(","):
        lang = token.strip()
        if lang and lang not in langs:
            langs.append(lang)
    return langs or ["en", "en-US", "en-GB"]


def result_payload(
    status: str,
    video_id: Optional[str],
    source: str,
    reason: str,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a standard machine-friendly result payload."""
    payload: Dict[str, Any] = {
        "status": status,
        "video_id": video_id,
        "source": source,
        "reason": reason,
        "checked_at": utc_now_iso(),
    }
    if details:
        payload["details"] = details
    return payload


def check_transcript_availability(video_id: str, languages: List[str]) -> Dict[str, Any]:
    """Check transcript availability via youtube-transcript-api with fast-fail semantics."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi  # type: ignore
    except Exception as exc:
        return result_payload(
            status="error",
            video_id=video_id,
            source="youtube-transcript-api",
            reason="dependency_missing",
            details={
                "error": str(exc),
                "install_hint": "py -m pip install youtube-transcript-api",
            },
        )

    known_no_transcript = {
        "NoTranscriptFound",
        "TranscriptsDisabled",
        "VideoUnavailable",
        "CouldNotRetrieveTranscript",
    }

    try:
        api_instance = YouTubeTranscriptApi()

        list_method = getattr(YouTubeTranscriptApi, "list_transcripts", None)
        if not callable(list_method):
            list_method = getattr(api_instance, "list", None)

        if callable(list_method):
            transcript_list = list_method(video_id)
            available_tracks = list(transcript_list)

            if not available_tracks:
                return result_payload(
                    status="no_transcript_available",
                    video_id=video_id,
                    source="youtube-transcript-api",
                    reason="no_tracks_returned",
                )

            selected = None
            find_method = getattr(transcript_list, "find_transcript", None)
            if callable(find_method):
                try:
                    selected = find_method(languages)
                except Exception:
                    selected = None

            if selected is None:
                selected = available_tracks[0]

            fetched = []
            fetch_track_method = getattr(selected, "fetch", None)
            if callable(fetch_track_method):
                fetched = fetch_track_method()
            else:
                # Newer API exposes fetch on the API instance.
                fetch_video_method = getattr(api_instance, "fetch", None)
                if callable(fetch_video_method):
                    fetched = fetch_video_method(video_id, languages=tuple(languages))

            segment_count = len(fetched) if hasattr(fetched, "__len__") else 0

            is_timed = False
            if segment_count > 0:
                first = fetched[0]
                if isinstance(first, dict):
                    is_timed = "start" in first and ("duration" in first or "dur" in first)
                else:
                    is_timed = hasattr(first, "start") and hasattr(first, "duration")

            language_code = getattr(selected, "language_code", None)
            is_generated = getattr(selected, "is_generated", None)

            return result_payload(
                status="transcript_available",
                video_id=video_id,
                source="youtube-transcript-api",
                reason="track_found",
                details={
                    "language_requested": languages,
                    "language_selected": language_code,
                    "is_generated": is_generated,
                    "segment_count": segment_count,
                    "timed_transcript_detected": is_timed,
                },
            )

        # Fallback path for API variants that expose get_transcript only.
        get_method = getattr(YouTubeTranscriptApi, "get_transcript", None)
        if not callable(get_method):
            # Newer API compatibility.
            get_method = getattr(api_instance, "fetch", None)
        if callable(get_method):
            fetched = get_method(video_id, languages=tuple(languages))
            segment_count = len(fetched) if hasattr(fetched, "__len__") else 0

            if segment_count == 0:
                return result_payload(
                    status="no_transcript_available",
                    video_id=video_id,
                    source="youtube-transcript-api",
                    reason="empty_transcript",
                )

            first = fetched[0]
            if isinstance(first, dict):
                is_timed = "start" in first
            else:
                is_timed = hasattr(first, "start")
            return result_payload(
                status="transcript_available",
                video_id=video_id,
                source="youtube-transcript-api",
                reason="segments_fetched",
                details={
                    "language_requested": languages,
                    "segment_count": segment_count,
                    "timed_transcript_detected": is_timed,
                },
            )

        return result_payload(
            status="error",
            video_id=video_id,
            source="youtube-transcript-api",
            reason="unsupported_library_api",
        )

    except Exception as exc:
        name = exc.__class__.__name__
        if name in known_no_transcript:
            return result_payload(
                status="no_transcript_available",
                video_id=video_id,
                source="youtube-transcript-api",
                reason=name,
                details={"error": str(exc)},
            )

        return result_payload(
            status="error",
            video_id=video_id,
            source="youtube-transcript-api",
            reason=name,
            details={"error": str(exc)},
        )


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Fast-fail check for YouTube transcript availability."
    )
    parser.add_argument(
        "input",
        help="YouTube URL or raw video ID",
    )
    parser.add_argument(
        "--languages",
        default="en,en-US,en-GB",
        help="Comma-separated preferred language codes (default: en,en-US,en-GB)",
    )
    parser.add_argument(
        "--status-only",
        action="store_true",
        help="Print only the status token for pipeline branching.",
    )

    args = parser.parse_args()

    video_id = extract_video_id(args.input)
    if not video_id:
        payload = result_payload(
            status="error",
            video_id=None,
            source="input",
            reason="invalid_youtube_url_or_id",
            details={"input": args.input},
        )
        if args.status_only:
            print(payload["status"])
        else:
            print(json.dumps(payload, indent=2))
        return 1

    payload = check_transcript_availability(video_id, parse_languages(args.languages))

    if args.status_only:
        print(payload["status"])
    else:
        print(json.dumps(payload, indent=2))

    if payload["status"] == "transcript_available":
        return 0
    if payload["status"] == "no_transcript_available":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
