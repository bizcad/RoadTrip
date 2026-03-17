from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_INDEX = Path(r"G:\repos\AI\RoadTrip\analysis\ppa\session_log_events.jsonl")


def load_rows(path: Path) -> list[dict[str, object]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def score_row(row: dict[str, object], query_terms: list[str]) -> int:
    haystack = str(row.get("text", "")).lower()
    score = 0
    for term in query_terms:
        score += haystack.count(term)
    return score


def truncate(text: str, limit: int = 240) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def main() -> None:
    parser = argparse.ArgumentParser(description="Query the PPA session-log event index.")
    parser.add_argument("query", nargs="?", default="", help="Free-text query string.")
    parser.add_argument("--index", default=str(DEFAULT_INDEX), help="Path to session_log_events.jsonl")
    parser.add_argument("--approach", help="Filter by approach tag")
    parser.add_argument("--stance", help="Filter by stance")
    parser.add_argument("--kind", choices=["prompt", "response"], help="Filter by event kind")
    parser.add_argument("--limit", type=int, default=12, help="Maximum matches to print")
    args = parser.parse_args()

    index_path = Path(args.index)
    if not index_path.exists():
        raise SystemExit(f"Index file not found: {index_path}. Run `py scripts\\analyze_session_logs_for_ppa.py` first.")

    rows = load_rows(index_path)
    filtered = []
    query_terms = [term.lower() for term in args.query.split() if term.strip()]

    for row in rows:
        if args.approach and args.approach not in row.get("approaches", []):
            continue
        if args.stance and args.stance != row.get("stance"):
            continue
        if args.kind and args.kind != row.get("event_kind"):
            continue
        score = score_row(row, query_terms) if query_terms else 1
        if score <= 0:
            continue
        filtered.append((score, row))

    filtered.sort(key=lambda item: (item[0], item[1].get("timestamp") or ""), reverse=True)

    for score, row in filtered[: args.limit]:
        print(f"[{row.get('timestamp')}] {row.get('source_file')} | {row.get('event_kind')} | score={score}")
        print(f"approaches={','.join(row.get('approaches', []))} | stance={row.get('stance')}")
        print(truncate(str(row.get("text", ""))))
        print()

    if not filtered:
        print("No matches found.")


if __name__ == "__main__":
    main()