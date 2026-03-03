from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

PROJECTS = [Path(r"G:\repos\AI\RoadTrip"), Path(r"G:\repos\AI\ControlPlane")]
OUTPUT_DIR = Path(r"G:\repos\AI\RoadTrip\analysis\idea_extraction")
INCLUDE_EXTS = {".md", ".txt"}
EXCLUDE_DIRS = {".git", "bin", "obj", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}

IDEA_RE = re.compile(
    r"\b(idea|plan|should|could|need to|next step|todo|build|create|implement|improve|automate|evaluate|design|spec|workflow|system|problem|challenge|approach|proposal|option|consider|we can|goal|priority|roadmap)\b",
    re.IGNORECASE,
)

STOPWORDS = {
    "the","a","an","and","or","but","if","then","else","for","to","of","in","on","at","by","with","from",
    "is","are","was","were","be","been","being","it","this","that","these","those","as","we","you","i",
    "our","your","their","they","them","his","her","not","do","does","did","can","could","would","should",
    "may","might","will","into","over","under","about","after","before","during","than",
}


def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDE_DIRS for part in path.parts)


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"(?m)^\s*\d{1,2}:\d{2}(?::\d{2})?\s*[-–—]?\s*", "", text)
    text = re.sub(r"(?m)^\s*\[\d{1,2}:\d{2}(?::\d{2})?\]\s*", "", text)
    text = re.sub(r"(?m)^\s*\d{2}:\d{2}:\d{2}[,.]\d{3}\s*-->.*$", "", text)
    text = re.sub(r"(?m)^\s*<!--.*?-->\s*$", "", text)
    return text


def tokenize(text: str) -> list[str]:
    clean = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    clean = re.sub(r"\s+", " ", clean).strip()
    if not clean:
        return []
    return [t for t in clean.split(" ") if len(t) >= 3 and t not in STOPWORDS]


def get_theme(text: str) -> str:
    t = text.lower()
    if re.search(r"\b(memory|context|session|transcript|knowledge|state)\b", t):
        return "memory-and-context"
    if re.search(r"\b(agent|workflow|automation|pipeline|tool|mcp|skill)\b", t):
        return "agent-workflow"
    if re.search(r"\b(spec|architecture|design|system|component|interface)\b", t):
        return "architecture-and-spec"
    if re.search(r"\b(test|evaluation|metric|quality|validate|benchmark)\b", t):
        return "evaluation-and-quality"
    if re.search(r"\b(ui|dashboard|xaml|window|view|ux)\b", t):
        return "ui-and-experience"
    if re.search(r"\b(road trip|flight|itinerary|travel|route|hotel|airport)\b", t):
        return "travel-domain"
    return "general"


def get_intent(text: str) -> str:
    t = text.lower()
    if re.search(r"\b(decide|decision|finalize|agreed|chosen)\b", t):
        return "decision"
    if re.search(r"\b(question|should we|how do we|what if|unknown|unclear)\b", t):
        return "question"
    if re.search(r"\b(problem|risk|issue|blocker|constraint|limitation)\b", t):
        return "problem"
    return "idea"


def idea_key(tokens: Iterable[str]) -> str:
    head = list(tokens)[:14]
    return " ".join(head)


def priority_score(text: str, mentions: int, source_count: int) -> float:
    impact = 2
    if re.search(r"\b(architecture|system|platform|pipeline|automation|spec|evaluation)\b", text, re.I):
        impact = 4
    if re.search(r"\b(core|critical|foundational|must)\b", text, re.I):
        impact = 5

    urgency = 2
    if re.search(r"\b(next|todo|need to|should|priority|urgent|blocker)\b", text, re.I):
        urgency = 4

    signal = min(5, 1 + ((mentions + source_count + 2) // 3))
    return round((impact * 0.45) + (urgency * 0.25) + (signal * 0.30), 2)


def main() -> None:
    candidates = []
    files_scanned = 0

    for project in PROJECTS:
        if not project.exists():
            continue
        for file in project.rglob("*"):
            if not file.is_file():
                continue
            if file.suffix.lower() not in INCLUDE_EXTS:
                continue
            if is_excluded(file):
                continue

            files_scanned += 1
            try:
                raw = file.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if not raw.strip():
                continue

            text = normalize_text(raw)
            chunks = re.split(r"\n\s*\n", text)
            chunk_cap = 0
            for chunk in chunks:
                if chunk_cap >= 100:
                    break
                chunk = re.sub(r"\s+", " ", chunk).strip()
                if len(chunk) < 35 or len(chunk) > 1200:
                    continue
                if not IDEA_RE.search(chunk):
                    continue

                tokens = tokenize(chunk)
                if len(tokens) < 6:
                    continue

                key = idea_key(tokens)
                if not key:
                    continue

                conf = 0.55
                if re.search(r"\b(need to|should|must|next|todo|plan|we can|build|implement|priority)\b", chunk, re.I):
                    conf += 0.20
                if re.search(r"\b(architecture|spec|workflow|evaluation|automation|memory|context)\b", chunk, re.I):
                    conf += 0.15
                conf = min(conf, 0.95)

                proj_name = "RoadTrip" if str(file).lower().startswith(str(PROJECTS[0]).lower()) else "ControlPlane"

                candidates.append(
                    {
                        "idea_key": key,
                        "excerpt": chunk,
                        "project": proj_name,
                        "file_path": str(file),
                        "file_name": file.name,
                        "ext": file.suffix.lower(),
                        "theme": get_theme(chunk),
                        "intent": get_intent(chunk),
                        "confidence": round(conf, 2),
                    }
                )
                chunk_cap += 1

    buckets: dict[str, dict] = {}
    for c in candidates:
        key = c["idea_key"]
        if key not in buckets:
            buckets[key] = {
                "canonical": c["excerpt"],
                "mentions": 0,
                "sources": set(),
                "theme_counts": Counter(),
                "intent_counts": Counter(),
                "evidences": [],
            }
        b = buckets[key]
        b["mentions"] += 1
        b["sources"].add(c["file_path"])
        b["theme_counts"][c["theme"]] += 1
        b["intent_counts"][c["intent"]] += 1
        b["evidences"].append(c)
        if len(c["excerpt"]) > len(b["canonical"]):
            b["canonical"] = c["excerpt"]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    idea_register = []
    idea_evidence = []

    for idx, (k, b) in enumerate(buckets.items(), start=1):
        idea_id = f"IDEA-{idx:04d}"
        theme = b["theme_counts"].most_common(1)[0][0] if b["theme_counts"] else "general"
        intent = b["intent_counts"].most_common(1)[0][0] if b["intent_counts"] else "idea"
        mentions = b["mentions"]
        source_count = len(b["sources"])
        prio = priority_score(b["canonical"], mentions, source_count)
        status = "implemented" if re.search(r"\b(done|completed|shipped|resolved)\b", b["canonical"], re.I) else "open"
        sample_sources = " | ".join(list(b["sources"])[:3])

        idea_register.append(
            {
                "idea_id": idea_id,
                "idea_text": b["canonical"],
                "theme": theme,
                "intent": intent,
                "priority_score": prio,
                "status": status,
                "mentions": mentions,
                "source_count": source_count,
                "sample_sources": sample_sources,
            }
        )

        for ev in b["evidences"]:
            idea_evidence.append({"idea_id": idea_id, **{k2: ev[k2] for k2 in ["project", "file_path", "file_name", "ext", "confidence", "theme", "intent", "excerpt"]}})

    idea_register.sort(key=lambda x: (x["priority_score"], x["mentions"]), reverse=True)
    idea_evidence.sort(key=lambda x: (x["idea_id"], -x["confidence"]))

    theme_group = defaultdict(list)
    for row in idea_register:
        theme_group[row["theme"]].append(row)
    idea_themes = []
    for theme, rows in sorted(theme_group.items(), key=lambda kv: len(kv[1]), reverse=True):
        avg = round(sum(r["priority_score"] for r in rows) / len(rows), 2)
        idea_themes.append({"theme": theme, "idea_count": len(rows), "avg_priority": avg})

    def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    write_csv(
        OUTPUT_DIR / "idea_register.csv",
        idea_register,
        ["idea_id", "idea_text", "theme", "intent", "priority_score", "status", "mentions", "source_count", "sample_sources"],
    )
    write_csv(
        OUTPUT_DIR / "idea_evidence.csv",
        idea_evidence,
        ["idea_id", "project", "file_path", "file_name", "ext", "confidence", "theme", "intent", "excerpt"],
    )
    write_csv(OUTPUT_DIR / "idea_themes.csv", idea_themes, ["theme", "idea_count", "avg_priority"])
    write_csv(
        OUTPUT_DIR / "run_summary.csv",
        [
            {
                "projects": "; ".join(str(p) for p in PROJECTS),
                "files_scanned": files_scanned,
                "candidates_found": len(candidates),
                "idea_clusters": len(idea_register),
                "output_dir": str(OUTPUT_DIR),
            }
        ],
        ["projects", "files_scanned", "candidates_found", "idea_clusters", "output_dir"],
    )

    print("Completed two-pass extraction")
    print(OUTPUT_DIR / "idea_register.csv")
    print(OUTPUT_DIR / "idea_evidence.csv")
    print(OUTPUT_DIR / "idea_themes.csv")
    print(OUTPUT_DIR / "run_summary.csv")


if __name__ == "__main__":
    main()
