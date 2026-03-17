from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

PROJECT_ROOT = Path(r"G:\repos\AI\RoadTrip")
PPA_DIR = PROJECT_ROOT / "analysis" / "ppa"
DEFAULT_EVENTS = PPA_DIR / "session_log_events.jsonl"
DEFAULT_JSON_OUT = PPA_DIR / "ppa_decision_register.json"
DEFAULT_MD_OUT = PPA_DIR / "ppa_decision_register.md"

DECISION_CUES = [
    r"\b(decide|decision|we decided|chosen|finalized|agreed|recommend(?:ed)?)\b",
    r"\b(will do|go ahead|implemented|completed|approved)\b",
]
REJECTION_CUES = [
    r"\b(reject(?:ed|ion)?|deprioriti[sz]ed|abandon(?:ed)?|drop(?:ped)?|not doing)\b",
    r"\b(don't like|less i like|wrong direction)\b",
]
REVERSAL_CUES = [
    r"\b(instead|changed my mind|no longer|pivot|reconsider|prefer .* over)\b",
    r"\b(used to think|previously|earlier)\b",
]

TOPIC_CUES: dict[str, list[str]] = {
    "routing-and-orchestration": [r"\b(route|routing|orchestr(?:ate|ation)|path|fast-path|thinking-slow|invention-path)\b"],
    "memory-and-retrieval": [r"\b(memory|session log|retrieve|retrieval|query|index)\b"],
    "deterministic-vs-probabilistic": [r"\b(deterministic|probabilistic|trusted code|skill)\b"],
    "cost-and-pricing-policy": [r"\b(cost|pricing|budget|token|reward function|latency|time)\b"],
    "governance-and-safety": [r"\b(policy|gate|hitl|triage|zero trust|auth|governance)\b"],
}


@dataclass
class Candidate:
    event: dict[str, object]
    kind: str
    score: float
    topic: str


def load_events(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def cue_score(text: str, patterns: list[str]) -> int:
    return sum(1 for pattern in patterns if re.search(pattern, text, flags=re.I))


def infer_topic(text: str) -> str:
    best_topic = "general"
    best_score = 0
    for topic, patterns in TOPIC_CUES.items():
        score = cue_score(text, patterns)
        if score > best_score:
            best_topic = topic
            best_score = score
    return best_topic


def classify(event: dict[str, object]) -> Candidate | None:
    text = str(event.get("text", ""))
    if not text:
        return None

    d = cue_score(text, DECISION_CUES)
    r = cue_score(text, REJECTION_CUES)
    v = cue_score(text, REVERSAL_CUES)

    if max(d, r, v) == 0:
        return None

    if d >= r and d >= v:
        kind = "decision"
        score = d + (0.3 if event.get("stance") == "adopted-or-endorsed" else 0.0)
    elif r >= d and r >= v:
        kind = "rejection"
        score = r + (0.3 if event.get("stance") == "rejected-or-deprioritized" else 0.0)
    else:
        kind = "reversal"
        score = v + (0.2 if event.get("stance") == "open-question" else 0.0)

    return Candidate(event=event, kind=kind, score=score, topic=infer_topic(text))


def truncate(text: str, limit: int = 240) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def build_register(events: list[dict[str, object]]) -> dict[str, object]:
    candidates: list[Candidate] = []
    for event in events:
        candidate = classify(event)
        if candidate:
            candidates.append(candidate)

    by_kind: dict[str, list[Candidate]] = defaultdict(list)
    by_topic: Counter[str] = Counter()
    by_file: Counter[str] = Counter()

    for candidate in candidates:
        by_kind[candidate.kind].append(candidate)
        by_topic[candidate.topic] += 1
        by_file[str(candidate.event.get("source_file"))] += 1

    for rows in by_kind.values():
        rows.sort(key=lambda row: row.score, reverse=True)

    def row(candidate: Candidate) -> dict[str, object]:
        event = candidate.event
        return {
            "kind": candidate.kind,
            "topic": candidate.topic,
            "score": round(candidate.score, 3),
            "timestamp": event.get("timestamp"),
            "source_file": event.get("source_file"),
            "event_kind": event.get("event_kind"),
            "stance": event.get("stance"),
            "excerpt": truncate(str(event.get("text", ""))),
        }

    summary = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "source_event_count": len(events),
        "candidate_count": len(candidates),
        "counts_by_kind": {kind: len(rows) for kind, rows in by_kind.items()},
        "counts_by_topic": dict(by_topic.most_common()),
        "top_source_files": [{"source_file": path, "count": count} for path, count in by_file.most_common(12)],
        "top_decisions": [row(c) for c in by_kind.get("decision", [])[:20]],
        "top_rejections": [row(c) for c in by_kind.get("rejection", [])[:20]],
        "top_reversals": [row(c) for c in by_kind.get("reversal", [])[:20]],
    }
    return summary


def render_markdown(register: dict[str, object]) -> str:
    lines: list[str] = []
    lines.append("# PPA Decision Register (Second Pass)")
    lines.append("")
    lines.append(f"Generated: {register['generated_at']}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Source events scanned: {register['source_event_count']}")
    lines.append(f"- Candidate decision/rejection/reversal events: {register['candidate_count']}")
    for kind, count in register.get("counts_by_kind", {}).items():
        lines.append(f"- {kind}: {count}")
    lines.append("")

    lines.append("## Top Topics")
    lines.append("")
    for topic, count in list(register.get("counts_by_topic", {}).items())[:10]:
        lines.append(f"- {topic}: {count}")
    lines.append("")

    lines.append("## Top Decisions")
    lines.append("")
    for row in register.get("top_decisions", [])[:12]:
        lines.append(f"- [{row['timestamp']}] {row['source_file']} ({row['topic']}, score={row['score']}): {row['excerpt']}")
    lines.append("")

    lines.append("## Top Rejections")
    lines.append("")
    for row in register.get("top_rejections", [])[:12]:
        lines.append(f"- [{row['timestamp']}] {row['source_file']} ({row['topic']}, score={row['score']}): {row['excerpt']}")
    lines.append("")

    lines.append("## Top Reversals")
    lines.append("")
    for row in register.get("top_reversals", [])[:12]:
        lines.append(f"- [{row['timestamp']}] {row['source_file']} ({row['topic']}, score={row['score']}): {row['excerpt']}")
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Second-pass extractor for decisions, rejections, and reversals.")
    parser.add_argument("--events", default=str(DEFAULT_EVENTS), help="Input session event JSONL path")
    parser.add_argument("--json-out", default=str(DEFAULT_JSON_OUT), help="Output JSON register path")
    parser.add_argument("--md-out", default=str(DEFAULT_MD_OUT), help="Output markdown register path")
    args = parser.parse_args()

    events_path = Path(args.events)
    if not events_path.exists():
        raise SystemExit(f"Events file not found: {events_path}. Run: py scripts\\analyze_session_logs_for_ppa.py")

    events = load_events(events_path)
    register = build_register(events)

    json_out = Path(args.json_out)
    md_out = Path(args.md_out)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)

    json_out.write_text(json.dumps(register, indent=2, ensure_ascii=True), encoding="utf-8")
    md_out.write_text(render_markdown(register), encoding="utf-8")

    print(
        json.dumps(
            {
                "events": len(events),
                "candidate_count": register["candidate_count"],
                "json_out": str(json_out),
                "md_out": str(md_out),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
