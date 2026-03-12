#!/usr/bin/env python3
"""MCP server for transcript document retrieval and ranking.

Tools:
- read_transcript_frontmatter
- list_transcript_frontmatter
- build_transcript_frontmatter_index
- rank_transcript_documents
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("transcript-retrieval")


def _resolve_path(path_value: str) -> Path:
    return Path(path_value).resolve()


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9_\-]{2,}", text.lower())


def _token_overlap_score(query: str, text: str) -> float:
    q_tokens = set(_tokenize(query))
    if not q_tokens:
        return 0.0
    t_tokens = set(_tokenize(text))
    if not t_tokens:
        return 0.0
    overlap = q_tokens.intersection(t_tokens)
    return len(overlap) / len(q_tokens)


def _extract_frontmatter(content: str) -> tuple[dict[str, Any], int]:
    if not content.startswith("---\n"):
        return {}, 0

    marker = "\n---\n"
    end_idx = content.find(marker, 4)
    if end_idx == -1:
        return {}, 0

    yaml_text = content[4:end_idx]
    parsed = yaml.safe_load(yaml_text)
    if not isinstance(parsed, dict):
        return {}, end_idx + len(marker)
    return parsed, end_idx + len(marker)


def _extract_section(content: str, heading: str) -> str:
    pattern = rf"^##\s+{re.escape(heading)}\s*$"
    match = re.search(pattern, content, flags=re.MULTILINE)
    if not match:
        return ""

    start = match.end()
    next_heading = re.search(r"^##\s+", content[start:], flags=re.MULTILINE)
    if not next_heading:
        return content[start:].strip()
    return content[start : start + next_heading.start()].strip()


def _read_transcript_doc(file_path: Path) -> dict[str, Any]:
    content = file_path.read_text(encoding="utf-8")
    frontmatter, _ = _extract_frontmatter(content)
    summary = _extract_section(content, "Summary")
    analysis = _extract_section(content, "Analysis")

    return {
        "file_path": str(file_path),
        "frontmatter": frontmatter,
        "summary": summary,
        "analysis": analysis,
    }


def _candidate_seed_score(query: str, frontmatter: dict[str, Any], file_name: str) -> float:
    fields = [
        file_name,
        str(frontmatter.get("title", "")),
        str(frontmatter.get("creator", "")),
        str(frontmatter.get("video_id", "")),
        " ".join(str(x) for x in frontmatter.get("topics_detected", []) if x),
    ]
    return _token_overlap_score(query, " ".join(fields))


@mcp.tool()
def read_transcript_frontmatter(file_path: str) -> dict[str, Any]:
    """Read only frontmatter metadata from a transcript markdown file."""
    path = _resolve_path(file_path)
    if not path.exists():
        return {"status": "error", "reason": "file_not_found", "file_path": str(path)}

    content = path.read_text(encoding="utf-8")
    frontmatter, _ = _extract_frontmatter(content)
    return {
        "status": "ok",
        "file_path": str(path),
        "frontmatter": frontmatter,
    }


@mcp.tool()
def list_transcript_frontmatter(directory: str = "analysis/Transcripts") -> dict[str, Any]:
    """List transcript files and frontmatter for fast metadata-first retrieval."""
    base = _resolve_path(directory)
    if not base.exists():
        return {"status": "error", "reason": "directory_not_found", "directory": str(base)}

    rows: list[dict[str, Any]] = []
    for file_path in sorted(base.glob("*.md")):
        try:
            doc = _read_transcript_doc(file_path)
            rows.append(
                {
                    "file_path": doc["file_path"],
                    "frontmatter": doc["frontmatter"],
                }
            )
        except Exception as exc:  # pragma: no cover
            rows.append(
                {
                    "file_path": str(file_path),
                    "error": str(exc),
                }
            )

    return {
        "status": "ok",
        "directory": str(base),
        "count": len(rows),
        "items": rows,
    }


@mcp.tool()
def build_transcript_frontmatter_index(
    directory: str = "analysis/Transcripts",
    output_file: str = "analysis/Transcripts/_frontmatter_index.yaml",
) -> dict[str, Any]:
    """Build a metadata index to support fast-thinking retrieval."""
    base = _resolve_path(directory)
    if not base.exists():
        return {"status": "error", "reason": "directory_not_found", "directory": str(base)}

    rows: list[dict[str, Any]] = []
    for file_path in sorted(base.glob("*.md")):
        try:
            doc = _read_transcript_doc(file_path)
            fm = doc.get("frontmatter", {})
            rows.append(
                {
                    "file_path": doc["file_path"],
                    "title": fm.get("title"),
                    "creator": fm.get("creator"),
                    "video_id": fm.get("video_id"),
                    "upload_date": fm.get("upload_date"),
                    "topics_detected": fm.get("topics_detected", []),
                    "transcript_segment_count": fm.get("transcript_segment_count"),
                    "retrieved_at_utc": fm.get("retrieved_at_utc"),
                }
            )
        except Exception:
            continue

    out = _resolve_path(output_file)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_directory": str(base),
        "count": len(rows),
        "items": rows,
    }
    out.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    return {
        "status": "ok",
        "output_file": str(out),
        "count": len(rows),
    }


@mcp.tool()
def rank_transcript_documents(
    query: str,
    directory: str = "analysis/Transcripts",
    top_k: int = 5,
) -> dict[str, Any]:
    """Rank transcript docs using staged scoring: seed/frontmatter/summary/analysis.

    Stages:
    1) Fast lookup seed score from filename + key frontmatter fields.
    2) Frontmatter score.
    3) Summary score.
    4) Analysis score.
    """
    base = _resolve_path(directory)
    if not base.exists():
        return {"status": "error", "reason": "directory_not_found", "directory": str(base)}

    candidates: list[dict[str, Any]] = []
    for file_path in sorted(base.glob("*.md")):
        try:
            doc = _read_transcript_doc(file_path)
            frontmatter = doc["frontmatter"]
            seed_score = _candidate_seed_score(query, frontmatter, file_path.name)

            if seed_score > 0:
                candidates.append({"doc": doc, "seed_score": seed_score})
        except Exception:
            continue

    if not candidates:
        for file_path in sorted(base.glob("*.md")):
            try:
                doc = _read_transcript_doc(file_path)
                candidates.append({"doc": doc, "seed_score": 0.0})
            except Exception:
                continue

    ranked: list[dict[str, Any]] = []
    for item in candidates:
        doc = item["doc"]
        fm = doc["frontmatter"]

        fm_text = " ".join(
            [
                str(fm.get("title", "")),
                str(fm.get("creator", "")),
                str(fm.get("video_id", "")),
                " ".join(str(x) for x in fm.get("topics_detected", []) if x),
            ]
        )
        summary_text = doc.get("summary", "")
        analysis_text = doc.get("analysis", "")

        frontmatter_score = _token_overlap_score(query, fm_text)
        summary_score = _token_overlap_score(query, summary_text)
        analysis_score = _token_overlap_score(query, analysis_text)

        final_score = (
            (0.20 * item["seed_score"])
            + (0.40 * frontmatter_score)
            + (0.25 * summary_score)
            + (0.15 * analysis_score)
        )

        ranked.append(
            {
                "file_path": doc["file_path"],
                "title": fm.get("title"),
                "creator": fm.get("creator"),
                "video_id": fm.get("video_id"),
                "scores": {
                    "seed": round(item["seed_score"], 4),
                    "frontmatter": round(frontmatter_score, 4),
                    "summary": round(summary_score, 4),
                    "analysis": round(analysis_score, 4),
                    "final": round(final_score, 4),
                },
                "summary_preview": (summary_text[:300] + "...") if len(summary_text) > 300 else summary_text,
            }
        )

    ranked.sort(key=lambda x: x["scores"]["final"], reverse=True)
    return {
        "status": "ok",
        "query": query,
        "directory": str(base),
        "candidate_count": len(ranked),
        "top_k": top_k,
        "results": ranked[: max(1, top_k)],
    }


if __name__ == "__main__":
    mcp.run()
