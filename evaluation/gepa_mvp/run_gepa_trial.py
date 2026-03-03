from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Optional


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def read_payload(file_path: Optional[str], text: Optional[str], label: str) -> str:
    if file_path and text:
        raise ValueError(f"Use either --{label}-file or --{label}-text, not both.")
    if file_path:
        return Path(file_path).read_text(encoding="utf-8").strip()
    if text:
        return text.strip()
    raise ValueError(f"Missing required payload: provide --{label}-file or --{label}-text.")


def default_session_log(project_root: Path) -> Path:
    day = dt.datetime.now().strftime("%Y%m%d")
    return project_root / "PromptTracking" / f"Session Log {day}.md"


def ensure_session_log_header(path: Path) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        title = f"# Session Log {dt.datetime.now().strftime('%Y-%m-%d')}\n"
        path.write_text(title, encoding="utf-8")


def format_yaml_header(payload: dict) -> str:
    order = [
        "entry_type",
        "timestamp",
        "trial_id",
        "prompt_id",
        "parent_prompt_id",
        "model",
        "response_id",
        "response_hash",
        "gepa_score",
        "pass_fail",
        "cost_usd",
        "latency_ms",
    ]
    lines = []
    for key in order:
        value = payload.get(key)
        if value is None:
            value = ""
        lines.append(f"{key}: {value}")
    return "\n".join(lines)


def append_session_entry(session_log: Path, trial: dict, prompt_text: str, response_text: str) -> None:
    ensure_session_log_header(session_log)

    heading_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    yaml_header = format_yaml_header(trial)

    block = (
        f"\n## GEPA Trial {heading_time}\n\n"
        f"```yaml\n{yaml_header}\n```\n\n"
        f"### Prompt\n"
        f"<!--Start Prompt-->\n{prompt_text}\n<!--End Prompt-->\n\n"
        f"### Response\n"
        f"<!--Start Response-->\n{response_text}\n<!--End Response-->\n"
    )

    with session_log.open("a", encoding="utf-8") as handle:
        handle.write(block)


def write_artifacts(base_dir: Path, trial: dict, prompt_text: str, response_text: str) -> None:
    artifacts_dir = base_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    day_dir = artifacts_dir / dt.datetime.now().strftime("%Y%m%d")
    day_dir.mkdir(parents=True, exist_ok=True)

    enriched = {
        **trial,
        "prompt_text": prompt_text,
        "response_text": response_text,
    }

    trial_path = day_dir / f"{trial['trial_id']}.json"
    trial_path.write_text(json.dumps(enriched, indent=2, ensure_ascii=False), encoding="utf-8")

    jsonl_path = artifacts_dir / "trials.jsonl"
    with jsonl_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(enriched, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append a GEPA trial to session logs with YAML metadata.")

    parser.add_argument("--prompt-id", required=True)
    parser.add_argument("--parent-prompt-id", default="")
    parser.add_argument("--model", required=True)
    parser.add_argument("--response-id", default="")
    parser.add_argument("--gepa-score", type=float, required=True)
    parser.add_argument("--pass-fail", choices=["pass", "fail"], required=True)
    parser.add_argument("--cost-usd", type=float, default=0.0)
    parser.add_argument("--latency-ms", type=int, default=0)

    parser.add_argument("--prompt-file")
    parser.add_argument("--prompt-text")
    parser.add_argument("--response-file")
    parser.add_argument("--response-text")

    parser.add_argument("--session-log-path")
    parser.add_argument("--project-root")

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    script_dir = Path(__file__).resolve().parent
    project_root = Path(args.project_root).resolve() if args.project_root else script_dir.parent.parent

    prompt_text = read_payload(args.prompt_file, args.prompt_text, "prompt")
    response_text = read_payload(args.response_file, args.response_text, "response")

    timestamp = utc_now().replace(microsecond=0).isoformat().replace("+00:00", "Z")
    response_hash = hashlib.sha256(response_text.encode("utf-8")).hexdigest()

    trial_id = f"{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}-{response_hash[:8]}"

    trial = {
        "entry_type": "gepa_trial",
        "timestamp": timestamp,
        "trial_id": trial_id,
        "prompt_id": args.prompt_id,
        "parent_prompt_id": args.parent_prompt_id,
        "model": args.model,
        "response_id": args.response_id,
        "response_hash": response_hash,
        "gepa_score": args.gepa_score,
        "pass_fail": args.pass_fail,
        "cost_usd": args.cost_usd,
        "latency_ms": args.latency_ms,
    }

    session_log = Path(args.session_log_path).resolve() if args.session_log_path else default_session_log(project_root)

    write_artifacts(script_dir, trial, prompt_text, response_text)
    append_session_entry(session_log, trial, prompt_text, response_text)

    print(f"GEPA trial logged: {trial_id}")
    print(f"Session log: {session_log}")
    print(f"Artifacts: {script_dir / 'artifacts'}")


if __name__ == "__main__":
    main()
