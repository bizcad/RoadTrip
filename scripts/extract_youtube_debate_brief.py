#!/usr/bin/env python3
"""
Extract a YouTube transcript (if available) into a debate-ready markdown brief.

Output format:
- YAML frontmatter with source metadata
- ## Transcription
- ## Summary
- ## Analysis

If no transcript exists, the script exits with code 2 and does not write output.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Any, Iterable, List, Optional
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

try:
    # Script execution path: py scripts/extract_youtube_debate_brief.py ...
    from check_youtube_transcript_availability import (
        check_transcript_availability,
        extract_video_id,
        parse_languages,
    )
except ModuleNotFoundError:
    # Module import path: from scripts.extract_youtube_debate_brief import ...
    from scripts.check_youtube_transcript_availability import (
        check_transcript_availability,
        extract_video_id,
        parse_languages,
    )


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "has",
    "have",
    "he",
    "her",
    "his",
    "i",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "just",
    "my",
    "not",
    "of",
    "on",
    "or",
    "our",
    "out",
    "that",
    "the",
    "their",
    "them",
    "there",
    "they",
    "this",
    "to",
    "was",
    "we",
    "what",
    "when",
    "which",
    "who",
    "with",
    "you",
    "your",
}


@dataclass
class Segment:
    start: float
    duration: float
    text: str


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def http_get_text(url: str) -> str:
    req = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        },
    )
    with urlopen(req, timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")


def sanitize_slug(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-")
    cleaned = re.sub(r"-+", "-", cleaned)
    return cleaned[:120] if cleaned else "youtube-transcript"


def _presenter_token(creator: str, max_len: int = 16) -> str:
    token = sanitize_slug(creator).lower()
    return token[:max_len] if token else "unknown"


def _date_token(upload_date: str) -> str:
    # upload_date is expected like 2026-03-08T10:00:00-08:00.
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", (upload_date or "").strip())
    if m:
        return f"{m.group(1)}{m.group(2)}{m.group(3)}"
    return datetime.now(timezone.utc).strftime("%Y%m%d")


def _topic_token(title: str, max_len: int = 30) -> str:
    words = re.findall(r"[A-Za-z0-9]+", (title or "").lower())
    # Keep high-signal words only, then truncate to fit deterministic 30-char budget.
    filtered = [w for w in words if w not in STOPWORDS and len(w) > 2]
    basis = "-".join(filtered) if filtered else "-".join(words)
    topic = sanitize_slug(basis).lower()
    if not topic:
        topic = "transcript"
    return topic[:max_len].rstrip("-")


def build_document_stem(
    *,
    creator: str,
    upload_date: str,
    title: str,
    suffix: str = "",
) -> str:
    """Build short deterministic filename stem: presenter-yyyymmdd-topic30(+suffix)."""
    presenter = _presenter_token(creator)
    date_part = _date_token(upload_date)
    topic = _topic_token(title, max_len=30)
    return f"{presenter}-{date_part}-{topic}{suffix}"


def seconds_to_hms(seconds: float) -> str:
    total = max(0, int(seconds))
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def fetch_video_metadata(video_id: str) -> dict[str, Any]:
    watch_url = f"https://www.youtube.com/watch?v={video_id}"

    # Fast metadata endpoint for title + creator.
    oembed_url = (
        "https://www.youtube.com/oembed?url="
        + quote_plus(watch_url)
        + "&format=json"
    )
    title = "Unknown"
    creator = "Unknown"
    try:
        oembed_raw = http_get_text(oembed_url)
        oembed = json.loads(oembed_raw)
        title = str(oembed.get("title") or title)
        creator = str(oembed.get("author_name") or creator)
    except Exception:
        pass

    upload_date = ""
    duration_seconds = None
    try:
        html = http_get_text(watch_url)
        date_match = re.search(r'"uploadDate"\s*:\s*"([^"]+)"', html)
        if date_match:
            upload_date = date_match.group(1)

        # ISO 8601 duration (PT#H#M#S)
        dur_match = re.search(r'"duration"\s*:\s*"(PT[^"]+)"', html)
        if dur_match:
            duration_seconds = parse_iso8601_duration(dur_match.group(1))
    except Exception:
        pass

    return {
        "watch_url": watch_url,
        "title": unescape(title),
        "creator": unescape(creator),
        "upload_date": upload_date,
        "duration_seconds": duration_seconds,
    }


def parse_iso8601_duration(value: str) -> Optional[int]:
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", value)
    if not m:
        return None
    h = int(m.group(1) or 0)
    mins = int(m.group(2) or 0)
    secs = int(m.group(3) or 0)
    return h * 3600 + mins * 60 + secs


def fetch_transcript_segments(video_id: str, languages: List[str]) -> tuple[list[Segment], dict[str, Any]]:
    from youtube_transcript_api import YouTubeTranscriptApi  # type: ignore

    api_instance = YouTubeTranscriptApi()

    list_method = getattr(YouTubeTranscriptApi, "list_transcripts", None)
    if not callable(list_method):
        list_method = getattr(api_instance, "list", None)

    selected_language = None
    is_generated = None
    raw_segments: Iterable[Any] = []

    if callable(list_method):
        transcript_list = list_method(video_id)
        tracks = list(transcript_list)
        if not tracks:
            return [], {"reason": "no_tracks_returned"}

        selected = None
        find_method = getattr(transcript_list, "find_transcript", None)
        if callable(find_method):
            try:
                selected = find_method(languages)
            except Exception:
                selected = None

        if selected is None:
            selected = tracks[0]

        selected_language = getattr(selected, "language_code", None)
        is_generated = getattr(selected, "is_generated", None)
        raw_segments = selected.fetch()
    else:
        fetch_method = getattr(api_instance, "fetch", None)
        if callable(fetch_method):
            raw_segments = fetch_method(video_id, languages=tuple(languages))
        else:
            get_method = getattr(YouTubeTranscriptApi, "get_transcript", None)
            if not callable(get_method):
                raise RuntimeError("youtube_transcript_api unsupported version")
            raw_segments = get_method(video_id, languages=languages)

    segments: list[Segment] = []
    for item in raw_segments:
        if isinstance(item, dict):
            text = str(item.get("text") or "").replace("\n", " ").strip()
            start = float(item.get("start") or 0.0)
            duration = float(item.get("duration") or 0.0)
        else:
            text = str(getattr(item, "text", "")).replace("\n", " ").strip()
            start = float(getattr(item, "start", 0.0) or 0.0)
            duration = float(getattr(item, "duration", 0.0) or 0.0)
        if text:
            segments.append(Segment(start=start, duration=duration, text=text))

    details = {
        "language_selected": selected_language,
        "is_generated": is_generated,
        "segment_count": len(segments),
    }
    return segments, details


def transcript_to_markdown_lines(segments: list[Segment]) -> list[str]:
    lines: list[str] = []
    for seg in segments:
        lines.append(f"- [{seconds_to_hms(seg.start)}] {seg.text}")
    return lines


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def sentence_has_substance(sentence: str) -> bool:
    lowered = sentence.lower().strip()
    if len(lowered) < 50:
        return False
    if lowered in {"i am sorry.", "thank you.", "let me know what you think in the comments."}:
        return False
    weak_starts = (
        "like and subscribe",
        "thanks for watching",
        "until next time",
        "let me know",
    )
    return not lowered.startswith(weak_starts)


def infer_topics(text: str, top_n: int = 10) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text.lower())
    filtered = [w for w in words if w not in STOPWORDS]
    counts = Counter(filtered)
    return [w for w, _ in counts.most_common(top_n)]


def summarize_transcript(sentences: list[str], segment_count: int) -> list[str]:
    if not sentences:
        return ["Transcript is empty or could not be segmented into sentences."]

    candidates = [s for s in sentences if sentence_has_substance(s)]
    if not candidates:
        candidates = sentences

    picks: list[str] = []
    seen = set()
    for sentence in candidates:
        normalized = re.sub(r"\W+", "", sentence.lower())
        if normalized in seen:
            continue
        seen.add(normalized)
        picks.append(sentence)
        if len(picks) == 6:
            break

    summary = [
        f"Transcript length: approximately {segment_count} caption segments.",
        "Core points detected:",
    ]
    summary.extend([f"- {p}" for p in picks])
    return summary


def extract_question_answer_pairs(sentences: list[str]) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for idx, sentence in enumerate(sentences):
        if "?" not in sentence:
            continue
        answer = ""
        if idx + 1 < len(sentences):
            answer = sentences[idx + 1]
        if idx + 2 < len(sentences) and len(answer) < 60:
            answer = (answer + " " + sentences[idx + 2]).strip()
        if answer:
            pairs.append((sentence, answer))
    return pairs[:12]


def extract_claim_candidates(sentences: list[str], limit: int = 8) -> list[str]:
    cue_words = (
        "best",
        "better",
        "worse",
        "always",
        "never",
        "proved",
        "state-of-the-art",
        "benchmark",
        "price",
        "cost",
        "improved",
    )
    claims: list[str] = []
    for sentence in sentences:
        lower = sentence.lower()
        if len(sentence) < 60:
            continue
        if any(cue in lower for cue in cue_words):
            claims.append(sentence)
        if len(claims) >= limit:
            break
    return claims


def build_analysis_section(sentences: list[str], topics: list[str]) -> list[str]:
    qa_pairs = extract_question_answer_pairs(sentences)
    claim_candidates = extract_claim_candidates(sentences)
    lines: list[str] = []

    lines.append("### Presenter Questions and Implied Answers")
    if qa_pairs:
        for q, a in qa_pairs:
            lines.append(f"- Question: {q}")
            lines.append(f"  Implied answer: {a}")
    else:
        lines.append("- No explicit question marks were detected in transcript punctuation.")
        lines.append("- Suggested cross-exam questions based on recurring claims:")
        for t in topics[:6]:
            lines.append(f"  - What evidence supports the claim related to '{t}'?")

    lines.append("")
    lines.append("### Claims to Pressure-Test")
    if claim_candidates:
        for claim in claim_candidates:
            lines.append(f"- Claim: {claim}")
            lines.append("  Challenge question: What independent evidence would falsify this claim?")
    else:
        lines.append("- No strong claim sentences detected with current heuristics.")

    lines.append("")
    lines.append("### Potential Weaknesses to Challenge")
    lines.append("- Evidence quality: Are key claims backed by data, or mostly anecdotal?")
    lines.append("- Selection bias: Were only favorable examples highlighted?")
    lines.append("- Confounding factors: Could alternative explanations fit the same outcomes?")
    lines.append("- Over-generalization: Are narrow observations being framed as universal truths?")
    lines.append("- Incentives: Are sponsorships or channel incentives shaping conclusions?")

    lines.append("")
    lines.append("### Research Prompt Ingredients for SRCGEEE Retrieve")
    lines.append("- Exact claim text to verify (quote with timestamp)")
    lines.append("- Required evidence type (peer-reviewed study, benchmark, public dataset, docs)")
    lines.append("- Time window for evidence freshness")
    lines.append("- Counter-position to test against")
    lines.append("- Failure criteria that would falsify the claim")
    lines.append("- Confidence rubric (high/medium/low) with reasons")

    return lines


def frontmatter_block(data: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        elif value is None:
            lines.append(f"{key}: null")
        elif isinstance(value, bool):
            lines.append(f"{key}: {'true' if value else 'false'}")
        elif isinstance(value, (int, float)):
            lines.append(f"{key}: {value}")
        else:
            text = str(value).replace("\n", " ").strip()
            if any(ch in text for ch in [":", "#", "[", "]", "{"]):
                lines.append(f"{key}: \"{text.replace('"', '\\"')}\"")
            else:
                lines.append(f"{key}: {text}")
    lines.append("---")
    return "\n".join(lines)


def write_brief(
    output_dir: Path,
    file_stem: str,
    frontmatter: dict[str, Any],
    transcription_lines: list[str],
    summary_lines: list[str],
    analysis_lines: list[str],
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{file_stem}.md"

    parts = [
        frontmatter_block(frontmatter),
        "",
        "# YouTube Transcript Brief",
        "",
        "## Transcription",
        *transcription_lines,
        "",
        "## Summary",
        *summary_lines,
        "",
        "## Analysis",
        *analysis_lines,
        "",
    ]
    out_path.write_text("\n".join(parts), encoding="utf-8")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract a YouTube transcript to markdown brief.")
    parser.add_argument("url", help="YouTube URL or video ID")
    parser.add_argument(
        "--output-dir",
        default="analysis/Transcripts",
        help="Output directory for markdown files",
    )
    parser.add_argument(
        "--languages",
        default="en,en-US,en-GB",
        help="Preferred language codes in order",
    )
    args = parser.parse_args()

    video_id = extract_video_id(args.url)
    if not video_id:
        print(json.dumps({"status": "error", "reason": "invalid_youtube_input"}, indent=2))
        return 1

    languages = parse_languages(args.languages)
    availability = check_transcript_availability(video_id, languages)
    if availability.get("status") == "no_transcript_available":
        print(json.dumps(availability, indent=2))
        return 2
    if availability.get("status") != "transcript_available":
        print(json.dumps(availability, indent=2))
        return 1

    metadata = fetch_video_metadata(video_id)

    try:
        segments, transcript_details = fetch_transcript_segments(video_id, languages)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "error",
                    "reason": "transcript_fetch_failed",
                    "video_id": video_id,
                    "error": str(exc),
                },
                indent=2,
            )
        )
        return 1

    if not segments:
        print(
            json.dumps(
                {
                    "status": "no_transcript_available",
                    "video_id": video_id,
                    "reason": "empty_transcript_after_fetch",
                },
                indent=2,
            )
        )
        return 2

    full_text = " ".join(seg.text for seg in segments)
    sentences = split_sentences(full_text)
    topics = infer_topics(full_text)

    transcription_lines = transcript_to_markdown_lines(segments)
    summary_lines = summarize_transcript(sentences, len(segments))
    analysis_lines = build_analysis_section(sentences, topics)

    title = metadata.get("title") or f"YouTube-{video_id}"
    creator = metadata.get("creator") or "Unknown"
    file_stem = build_document_stem(
        creator=creator,
        upload_date=str(metadata.get("upload_date") or ""),
        title=title,
    )

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
        "topics_detected": topics,
        "generator_script": "scripts/extract_youtube_debate_brief.py",
    }

    out_path = write_brief(
        output_dir=Path(args.output_dir),
        file_stem=file_stem,
        frontmatter=frontmatter,
        transcription_lines=transcription_lines,
        summary_lines=summary_lines,
        analysis_lines=analysis_lines,
    )

    print(
        json.dumps(
            {
                "status": "ok",
                "video_id": video_id,
                "output_file": str(out_path),
                "title": title,
                "creator": creator,
                "segment_count": len(segments),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
