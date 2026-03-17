from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(r"G:\repos\AI\RoadTrip")
PROMPT_TRACKING_DIR = PROJECT_ROOT / "PromptTracking"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "analysis" / "ppa"
UNIFIED_AUTH_SPEC = PROJECT_ROOT / "analysis" / "unified-auth" / "ClaudeCode" / "unified-auth-spec-v0.2.md"
NOTEBOOKLM_NOTE = Path(r"G:\repos\AI\scratchpad\Google NotebookLM.md")


APPROACH_PATTERNS: dict[str, list[str]] = {
    "personal-assistant-product": [
        r"\bpersonal assistant\b",
        r"\bppa\b",
        r"\bpurushottama\b",
        r"\bassistant application\b",
        r"\bhelpful assistant\b",
    ],
    "identity-auth-governance": [
        r"\bauth(?:entication|orization)?\b",
        r"\brbac\b",
        r"\bspicedb\b",
        r"\bzanzibar\b",
        r"\bpolicy\b",
        r"\bprincipal\b",
        r"\bdelegation\b",
        r"\bdecision receipt\b",
        r"\bzero trust\b",
    ],
    "deterministic-execution-safety": [
        r"\bdeterministic\b",
        r"\btrusted\b",
        r"\bgate\b",
        r"\bhitl\b",
        r"\benforce\b",
        r"\bsafety\b",
        r"\bprobabilistic\b",
        r"\bguard\b",
    ],
    "memory-and-retrieval": [
        r"\bmemory\b",
        r"\bsession log\b",
        r"\bsession logs\b",
        r"\bcontext\b",
        r"\bnotebooklm\b",
        r"\brag\b",
        r"\bretriev(?:e|al)\b",
        r"\bquery\b",
        r"\btranscript\b",
    ],
    "agent-orchestration": [
        r"\bagent\b",
        r"\borchestr(?:ate|ation)\b",
        r"\bworkflow\b",
        r"\btool\b",
        r"\bmcp\b",
        r"\bskill\b",
        r"\bsrcgeee\b",
        r"\bcompose\b",
        r"\bexecute\b",
    ],
    "knowledge-ingestion": [
        r"\bscrape\b",
        r"\bpage scraper\b",
        r"\byoutube\b",
        r"\btranscript\b",
        r"\binterview\b",
        r"\bsource guide\b",
        r"\bdocs\b",
    ],
    "device-and-runtime": [
        r"\blinux phone\b",
        r"\bdevice\b",
        r"\bon-device\b",
        r"\blocal model\b",
        r"\bhost\b",
        r"\bruntime\b",
        r"\bmac\b",
        r"\bllm\b",
    ],
    "developer-workflow": [
        r"\bgpush\b",
        r"\bprofile\b",
        r"\bscript\b",
        r"\btest\b",
        r"\bbuild\b",
        r"\bcommit\b",
        r"\brepo\b",
    ],
}

PRINCIPLE_CUES = {
    "deterministic code over model-side execution": [r"deterministic code", r"deterministic executor", r"AI figures out what to do, code does the work"],
    "humans, agents, and code are first-class principals": [r"first-class security principals", r"humans, agents, and code"],
    "zero-trust with explicit delegation": [r"zero trust", r"delegation", r"least privilege", r"default deny"],
    "retrieval should be grounded in your own artifacts": [r"session log", r"notebooklm", r"grounded strictly", r"quasi-rag", r"retrieve"],
    "agent systems need deterministic gates before execution": [r"gate", r"hitl", r"enforceable", r"policy decision point", r"policy enforcement point"],
}

ACCEPT_CUES = [
    r"\bgood idea\b",
    r"\bright place\b",
    r"\bprefer\b",
    r"\bshould\b",
    r"\byes\b",
    r"\bimplemented\b",
    r"\bcompleted\b",
    r"\bworks?\b",
    r"\bwill do\b",
]
REJECT_CUES = [
    r"\bdon't like\b",
    r"\bless i like\b",
    r"\bnot working out\b",
    r"\bremoved\b",
    r"\bdeleted\b",
    r"\brejected\b",
    r"\babandon\b",
    r"\bdeprioriti[sz]ed\b",
]
QUESTION_CUES = [r"\?$", r"\bwhat if\b", r"\bhow do\b", r"\bshould we\b", r"\bi wonder\b", r"\bthinking about\b"]

TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_-]{2,}")
STOPWORDS = {
    "the", "and", "for", "that", "with", "this", "from", "have", "would", "there",
    "about", "into", "when", "your", "they", "their", "what", "where", "which",
    "should", "could", "because", "were", "been", "will", "then", "them", "also",
    "just", "like", "into", "over", "after", "before", "using", "used", "need",
    "roadtrip", "session", "prompt", "response", "file", "lines", "read", "ran",
    "https", "http", "com", "repos", "repo", "github", "skills", "files", "path",
    "line", "lines", "code", "output", "command", "commands", "generated", "tool",
    "tools", "file_path", "file_paths", "workspace", "markdown", "docs", "copilot",
    "claude", "vscode", "local", "start", "end", "true", "false",
}

FOCUS_ORDER = [
    "personal-assistant-product",
    "memory-and-retrieval",
    "deterministic-execution-safety",
    "identity-auth-governance",
    "agent-orchestration",
    "knowledge-ingestion",
    "device-and-runtime",
    "developer-workflow",
    "general",
]


@dataclass
class Event:
    source_file: str
    event_kind: str
    timestamp: str | None
    text: str
    pair_index: int | None
    approaches: list[str]
    stance: str


def iter_session_log_paths(prompt_tracking_dir: Path) -> list[Path]:
    return sorted(prompt_tracking_dir.glob("Session Log *.md"))


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"<!--Start (Prompt|Response)-->", "", text)
    text = re.sub(r"<!--End (Prompt|Response)-->", "", text)
    text = re.sub(r"!?\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"file:///\S+", " ", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[A-Za-z]:\\[^\s\"]+", " ", text)
    text = re.sub(r"`{3}.*?`{3}", " ", text, flags=re.S)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_blocks(path: Path) -> list[Event]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    pattern = re.compile(
        r"# (?P<kind>Prompt|Response): \((?P<timestamp>[^)]+)\)\s*\n(?P<body>.*?)(?=\n# (?:Prompt|Response): \(|\Z)",
        re.S,
    )
    events: list[Event] = []
    pair_index = 0
    for match in pattern.finditer(text):
        kind = match.group("kind").lower()
        body = clean_text(match.group("body"))
        if not body:
            continue
        if kind == "prompt":
            pair_index += 1
        approaches = classify_approaches(body)
        stance = classify_stance(body)
        events.append(
            Event(
                source_file=path.name,
                event_kind=kind,
                timestamp=match.group("timestamp"),
                text=body,
                pair_index=pair_index if pair_index else None,
                approaches=approaches,
                stance=stance,
            )
        )
    return events


def classify_approaches(text: str) -> list[str]:
    hits: list[str] = []
    lowered = text.lower()
    for approach, patterns in APPROACH_PATTERNS.items():
        if any(re.search(pattern, lowered, re.I) for pattern in patterns):
            hits.append(approach)
    return hits or ["general"]


def classify_stance(text: str) -> str:
    lowered = text.lower()
    if any(re.search(pattern, lowered, re.I) for pattern in REJECT_CUES):
        return "rejected-or-deprioritized"
    if any(re.search(pattern, lowered, re.I) for pattern in ACCEPT_CUES):
        return "adopted-or-endorsed"
    if any(re.search(pattern, lowered, re.I) for pattern in QUESTION_CUES):
        return "open-question"
    return "exploration"


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text) if token.lower() not in STOPWORDS]


def extract_keywords(texts: Iterable[str], limit: int = 10) -> list[str]:
    counter = Counter()
    for text in texts:
        counter.update(tokenize(text))
    return [word for word, _ in counter.most_common(limit)]


def summarize_reference_doc(path: Path, title: str) -> dict[str, object] | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="ignore")
    headings = re.findall(r"^#{1,3}\s+(.+)$", text, flags=re.M)[:12]
    principle_hits = []
    lowered = text.lower()
    for principle, cues in PRINCIPLE_CUES.items():
        hit_count = sum(1 for cue in cues if re.search(cue, lowered, re.I))
        if hit_count:
            principle_hits.append({"principle": principle, "hits": hit_count})
    return {
        "title": title,
        "path": str(path),
        "headings": headings,
        "principles": principle_hits,
    }


def build_summary(events: list[Event], references: list[dict[str, object]]) -> tuple[dict[str, object], str]:
    by_approach: dict[str, list[Event]] = defaultdict(list)
    by_stance: Counter[str] = Counter()
    monthly_counts: Counter[str] = Counter()
    rejected_examples: list[dict[str, str]] = []

    for event in events:
        by_stance[event.stance] += 1
        if event.timestamp:
            try:
                month = datetime.strptime(event.timestamp, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m")
                monthly_counts[month] += 1
            except ValueError:
                pass
        for approach in event.approaches:
            by_approach[approach].append(event)
        if event.stance == "rejected-or-deprioritized" and len(rejected_examples) < 12:
            rejected_examples.append(
                {
                    "source_file": event.source_file,
                    "timestamp": event.timestamp or "",
                    "excerpt": truncate(event.text, 220),
                }
            )

    approach_row_map = {}
    for approach, approach_events in sorted(by_approach.items(), key=lambda item: len(item[1]), reverse=True):
        keywords = extract_keywords([event.text for event in approach_events])
        stances = Counter(event.stance for event in approach_events)
        first_seen = min((event.timestamp for event in approach_events if event.timestamp), default=None)
        last_seen = max((event.timestamp for event in approach_events if event.timestamp), default=None)
        exemplar = next((event for event in approach_events if event.event_kind == "prompt"), approach_events[0])
        approach_row_map[approach] = {
            "approach": approach,
            "event_count": len(approach_events),
            "prompt_count": sum(1 for event in approach_events if event.event_kind == "prompt"),
            "response_count": sum(1 for event in approach_events if event.event_kind == "response"),
            "stances": dict(stances),
            "keywords": keywords,
            "first_seen": first_seen,
            "last_seen": last_seen,
            "example": truncate(exemplar.text, 280),
        }

    approach_rows = []
    for approach in FOCUS_ORDER:
        if approach in approach_row_map:
            approach_rows.append(approach_row_map.pop(approach))
    approach_rows.extend(sorted(approach_row_map.values(), key=lambda row: row["event_count"], reverse=True))

    principle_rows = []
    session_corpus = "\n".join(event.text for event in events)
    for principle, cues in PRINCIPLE_CUES.items():
        hit_count = sum(1 for cue in cues if re.search(cue, session_corpus, re.I))
        if hit_count:
            principle_rows.append({"principle": principle, "hits": hit_count})
    principle_rows.sort(key=lambda row: row["hits"], reverse=True)

    summary = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "event_count": len(events),
        "source_file_count": len({event.source_file for event in events}),
        "stances": dict(by_stance),
        "monthly_counts": dict(sorted(monthly_counts.items())),
        "approaches": approach_rows,
        "principles": principle_rows,
        "rejected_examples": rejected_examples,
        "references": references,
    }
    return summary, render_markdown(summary)


def render_markdown(summary: dict[str, object]) -> str:
    lines: list[str] = []
    lines.append("# PPA Session Log Approach Summary")
    lines.append("")
    lines.append(f"Generated: {summary['generated_at']}")
    lines.append("")
    lines.append("## Overview")
    lines.append("")
    lines.append(f"- Parsed {summary['event_count']} prompt/response events across {summary['source_file_count']} session log files.")
    for stance, count in summary["stances"].items():
        lines.append(f"- {stance}: {count}")
    lines.append("")
    lines.append("## What PPA Currently Looks Like")
    lines.append("")
    top_approaches = [row for row in summary["approaches"] if row["approach"] != "general"][:5]
    for row in top_approaches:
        keywords = ", ".join(row["keywords"][:6]) if row["keywords"] else "n/a"
        lines.append(f"- {row['approach']}: {row['event_count']} events, dominant signals: {keywords}")
    lines.append("")
    lines.append("## Likely Enduring Principles")
    lines.append("")
    for row in summary["principles"][:8]:
        lines.append(f"- {row['principle']} ({row['hits']} matching cue groups)")
    lines.append("")
    lines.append("## Approach Families")
    lines.append("")
    for row in summary["approaches"][:8]:
        lines.append(f"### {row['approach']}")
        lines.append("")
        lines.append(f"- Event count: {row['event_count']}")
        lines.append(f"- First seen: {row['first_seen'] or 'unknown'}")
        lines.append(f"- Last seen: {row['last_seen'] or 'unknown'}")
        lines.append(f"- Stances: {json.dumps(row['stances'], sort_keys=True)}")
        lines.append(f"- Keywords: {', '.join(row['keywords'][:10])}")
        lines.append(f"- Example: {row['example']}")
        lines.append("")
    lines.append("## Rejected or Deprioritized Signals")
    lines.append("")
    if summary["rejected_examples"]:
        for row in summary["rejected_examples"][:10]:
            lines.append(f"- {row['timestamp']} in {row['source_file']}: {row['excerpt']}")
    else:
        lines.append("- No deterministic reject/deprioritize cues found in the parsed events.")
    lines.append("")
    lines.append("## Reference Anchors")
    lines.append("")
    for ref in summary["references"]:
        headings = "; ".join(ref["headings"][:6])
        lines.append(f"- {ref['title']}: {headings}")
    lines.append("")
    lines.append("## Recommended Next Outputs")
    lines.append("")
    lines.append("- Build a queryable JSONL event index for session-log prompts and responses.")
    lines.append("- Add a second-pass principle extractor focused on decisions, rejections, and stable heuristics.")
    lines.append("- Define a PPA repo seed spec with three initial lanes: memory/retrieval, agent governance, deterministic execution.")
    lines.append("")
    return "\n".join(lines) + "\n"


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def write_jsonl(path: Path, rows: Iterable[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify and summarize RoadTrip session logs for PPA planning.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for summary outputs.")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    events: list[Event] = []
    for path in iter_session_log_paths(PROMPT_TRACKING_DIR):
        events.extend(parse_blocks(path))

    references = []
    for item in [
        summarize_reference_doc(UNIFIED_AUTH_SPEC, "Unified Auth Spec v0.2"),
        summarize_reference_doc(NOTEBOOKLM_NOTE, "NotebookLM Note"),
    ]:
        if item:
            references.append(item)

    summary, markdown = build_summary(events, references)

    events_jsonl = output_dir / "session_log_events.jsonl"
    summary_json = output_dir / "ppa_approach_summary.json"
    summary_md = output_dir / "ppa_approach_summary.md"

    write_jsonl(
        events_jsonl,
        [
            {
                "source_file": event.source_file,
                "event_kind": event.event_kind,
                "timestamp": event.timestamp,
                "pair_index": event.pair_index,
                "approaches": event.approaches,
                "stance": event.stance,
                "text": event.text,
            }
            for event in events
        ],
    )
    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=True), encoding="utf-8")
    summary_md.write_text(markdown, encoding="utf-8")

    print(json.dumps({
        "event_count": len(events),
        "summary_md": str(summary_md),
        "summary_json": str(summary_json),
        "events_jsonl": str(events_jsonl),
    }, indent=2))


if __name__ == "__main__":
    main()