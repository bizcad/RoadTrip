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
EVENT_INDEX_PATH = PPA_DIR / "session_log_events.jsonl"
SUMMARY_PATH = PPA_DIR / "ppa_approach_summary.json"
LEARNING_LOG_PATH = PPA_DIR / "ppa_learning_log.jsonl"
TRIAGE_DIR = PPA_DIR / "triage_packets"
PROSPECTIVE_MEMORY_QUEUE_PATH = PPA_DIR / "prospective_memory_queue.jsonl"
CONTRACT_VERSION = "ppa-v0"

FAST_PATH = "fast-path"
THINKING_SLOW_PATH = "thinking-slow-path"
INVENTION_PATH = "invention-path"

COMPLETED_ANSWER = "completed_answer"
COMPLETED_NON_ANSWER = "completed_non_answer"
COMPLETED_ESCALATION = "completed_escalation"
COMPLETED_DEFERRED_WORK = "completed_deferred_work"

REQUEST_CLASSES = [
    "chat-question",
    "memory-query",
    "known-skill-execution",
    "assistance-request",
    "invention-request",
]


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how", "i", "if",
    "in", "is", "it", "its", "me", "my", "of", "on", "or", "our", "so", "that", "the",
    "their", "them", "there", "these", "they", "this", "to", "was", "we", "what", "when",
    "where", "which", "who", "why", "with", "you", "your", "can", "could", "should", "would",
}


@dataclass
class ScoredEvent:
    score: float
    event: dict[str, object]


@dataclass
class AttemptResult:
    mode: str
    path: str
    evidence: list[ScoredEvent]
    answer: dict[str, object]


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def append_jsonl(path: Path, row: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def utc_now() -> datetime:
    return datetime.now(UTC)


def iso_utc_now() -> str:
    return utc_now().isoformat(timespec="seconds").replace("+00:00", "Z")


def build_question_id() -> str:
    return utc_now().strftime("q_%Y%m%dT%H%M%S%fZ")


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", text.lower())
    return [token for token in tokens if token not in STOPWORDS]


def normalize_question(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def classify_request_class(question: str, skill: str) -> str:
    lowered = question.lower()

    if skill == "echo":
        return "known-skill-execution"
    if skill == "assistance-request":
        return "assistance-request"

    if re.search(r"\b(help|assist|assistance|waiting on|blocked on|defer|async|await)\b", lowered):
        return "assistance-request"
    if re.search(r"\b(invent|new skill|research|triage|prototype|design)\b", lowered):
        return "invention-request"
    if re.search(r"\b(memory|session log|decision|rejected|reversal|what did we decide)\b", lowered):
        return "memory-query"
    if re.search(r"\b(run|execute|call skill|apply patch|build)\b", lowered):
        return "known-skill-execution"
    return "chat-question"


def sense_request(question: str, skill: str) -> dict[str, object]:
    normalized_question = normalize_question(question)
    tokens = tokenize(normalized_question)
    request_class = classify_request_class(normalized_question, skill)
    asks_clarification = False
    clarification_questions: list[str] = []

    if skill == "memory-search" and len(tokens) < 3:
        asks_clarification = True
        clarification_questions = [
            "What specific decision, design, or topic should PPA search for in memory?",
            "Do you want prior decisions, rejected ideas, or current open questions?",
        ]

    if skill == "echo":
        intent = "echo-input"
    elif asks_clarification:
        intent = "clarify-memory-query"
    else:
        intent = "retrieve-roadtrip-memory"

    return {
        "normalized_question": normalized_question,
        "token_count": len(tokens),
        "tokens": tokens[:12],
        "skill_requested": skill,
        "request_class": request_class,
        "intent": intent,
        "asks_clarification": asks_clarification,
        "clarification_questions": clarification_questions,
        "desired_completion": "evidence-backed answer or evidence-backed non-answer",
    }


def make_stage(name: str, status: str, **details: object) -> dict[str, object]:
    return {"stage": name, "status": status, **details}


def summarize_evidence(item: ScoredEvent) -> dict[str, object]:
    return {
        "score": round(item.score, 3),
        "source_file": item.event.get("source_file"),
        "timestamp": item.event.get("timestamp"),
        "event_kind": item.event.get("event_kind"),
        "approaches": item.event.get("approaches"),
        "stance": item.event.get("stance"),
        "text": item.event.get("text"),
    }


def get_learning_weights(path: Path) -> dict[str, float]:
    weights = defaultdict(float)
    if not path.exists():
        return weights
    for row in load_jsonl(path):
        if row.get("feedback") != "helpful":
            continue
        for source in row.get("sources", []):
            weights[str(source)] += 0.15
    return weights


def base_overlap_score(query_terms: list[str], text: str) -> float:
    if not query_terms:
        return 0.0
    tokens = tokenize(text)
    if not tokens:
        return 0.0
    counter = Counter(tokens)
    return sum(min(counter.get(term, 0), 3) for term in query_terms)


def recency_bonus(timestamp: str | None) -> float:
    if not timestamp:
        return 0.0
    try:
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
    except ValueError:
        return 0.0
    days = max(1, (datetime.now(UTC) - dt).days)
    if days <= 7:
        return 1.25
    if days <= 30:
        return 0.8
    if days <= 90:
        return 0.35
    return 0.0


def score_events(
    events: list[dict[str, object]],
    query: str,
    approach_hints: list[str],
    learning_weights: dict[str, float],
    mode: str,
) -> list[ScoredEvent]:
    query_terms = tokenize(query)
    scored: list[ScoredEvent] = []
    for event in events:
        text = str(event.get("text", ""))
        if not text:
            continue

        overlap_score = base_overlap_score(query_terms, text)
        score = overlap_score
        event_approaches = set(event.get("approaches", []))
        matched_approaches = event_approaches.intersection(approach_hints)

        # Slow paths may widen evidence, but they must still be grounded in either
        # lexical overlap or an approach-family hint inferred from the question.
        if overlap_score <= 0 and not matched_approaches:
            continue

        if approach_hints:
            score += 1.3 * len(matched_approaches)

        stance = str(event.get("stance", ""))
        if stance == "adopted-or-endorsed":
            score += 0.9
        elif stance == "open-question":
            score += 0.25

        source_file = str(event.get("source_file", ""))
        score += learning_weights.get(source_file, 0.0)
        score += recency_bonus(event.get("timestamp"))

        if mode == "slow":
            if event.get("event_kind") == "prompt":
                score += 0.15
        elif mode == "slower":
            score += 0.2  # include wider evidence window

        if score > 0:
            scored.append(ScoredEvent(score=score, event=event))

    scored.sort(key=lambda item: item.score, reverse=True)
    return scored


def infer_approach_hints(query: str, summary: dict[str, object]) -> list[str]:
    query_tokens = set(tokenize(query))
    hints: list[str] = []
    for row in summary.get("approaches", []):
        approach = row.get("approach")
        keywords = set(row.get("keywords", []))
        if approach and keywords and query_tokens.intersection(keywords):
            hints.append(str(approach))
    # Keep hints stable and compact
    return hints[:4]


def format_evidence_row(event: dict[str, object], score: float) -> str:
    text = str(event.get("text", "")).strip().replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    if len(text) > 220:
        text = text[:217].rstrip() + "..."
    return (
        f"- [{event.get('timestamp')}] {event.get('source_file')} "
        f"({event.get('event_kind')}, score={score:.2f}, stance={event.get('stance')}): {text}"
    )


def compose_answer(question: str, mode: str, evidence: list[ScoredEvent], summary: dict[str, object]) -> dict[str, object]:
    evidence = evidence[:6]
    if not evidence:
        return {
            "completion": False,
            "mode": mode,
            "answer": "No direct evidence found in current memory index.",
            "evidence": [],
            "confidence": "low",
            "recommended_action": "ask-clarifying-question-or-escalate",
        }

    approach_votes = Counter()
    for item in evidence:
        for approach in item.event.get("approaches", []):
            approach_votes[str(approach)] += 1
    top_approaches = [name for name, _ in approach_votes.most_common(3)]

    likely_principles = []
    for row in summary.get("principles", [])[:5]:
        likely_principles.append(str(row.get("principle")))

    confidence = "high" if len(evidence) >= 4 and evidence[0].score >= 3.5 else "medium"
    if evidence[0].score < 2.0:
        confidence = "low"

    synthesis_lines = [
        "Grounded read from RoadTrip memory:",
        f"- Dominant approach lanes: {', '.join(top_approaches) if top_approaches else 'general'}",
        f"- Likely stable principles: {', '.join(likely_principles[:3]) if likely_principles else 'none inferred'}",
        "- Recommended action: implement a thin vertical slice with deterministic retrieval + evidence-backed answer + optional triage escalation.",
        "Evidence:",
    ]
    synthesis_lines.extend(format_evidence_row(item.event, item.score) for item in evidence)

    return {
        "completion": confidence != "low",
        "mode": mode,
        "confidence": confidence,
        "question": question,
        "answer": "\n".join(synthesis_lines),
        "top_approaches": top_approaches,
        "evidence": [item.event for item in evidence],
        "scores": [round(item.score, 3) for item in evidence],
        "recommended_action": "return-grounded-answer" if confidence != "low" else "escalate-or-clarify",
    }


def create_triage_packet(question: str, attempted_modes: list[str], evidence: list[ScoredEvent]) -> Path:
    TRIAGE_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    packet_path = TRIAGE_DIR / f"triage_{stamp}.json"
    packet = {
        "created_at": iso_utc_now(),
        "question": question,
        "attempted_modes": attempted_modes,
        "reason": "insufficient confidence after fast and slow passes",
        "evidence": [
            {
                "score": round(item.score, 3),
                "source_file": item.event.get("source_file"),
                "timestamp": item.event.get("timestamp"),
                "event_kind": item.event.get("event_kind"),
                "approaches": item.event.get("approaches"),
                "stance": item.event.get("stance"),
                "text": item.event.get("text"),
            }
            for item in evidence[:12]
        ],
        "next_actions": [
            "Run deeper research pass on referenced topics",
            "Ask triage/expert agent with this packet",
            "Request HITL clarification if decision is high risk",
        ],
    }
    packet_path.write_text(json.dumps(packet, indent=2, ensure_ascii=True), encoding="utf-8")
    return packet_path


def compose_clarification_answer(sense: dict[str, object]) -> dict[str, object]:
    lines = [
        "Need clarification before retrieval can be trusted.",
        "Questions:",
    ]
    lines.extend(f"- {question}" for question in sense["clarification_questions"])
    return {
        "completion": True,
        "mode": "clarify",
        "confidence": "high",
        "question": sense["normalized_question"],
        "answer": "\n".join(lines),
        "top_approaches": ["clarification"],
        "evidence": [],
        "scores": [],
        "recommended_action": "await-user-clarification",
    }


def attempt_memory_answer(
    question: str,
    summary: dict[str, object],
    events: list[dict[str, object]],
    learning_weights: dict[str, float],
    approach_hints: list[str],
    mode: str,
    path: str,
) -> AttemptResult:
    scored = score_events(events, question, approach_hints, learning_weights, mode=mode)
    answer = compose_answer(question, mode, scored, summary)
    return AttemptResult(mode=mode, path=path, evidence=scored, answer=answer)


def finalize_package(
    question_id: str,
    question: str,
    skill: str,
    request_class: str,
    answer_text: str,
    sense_stage: dict[str, object],
    retrieve_stage: dict[str, object],
    compose_stage: dict[str, object],
    gate_stage: dict[str, object],
    execute_stage: dict[str, object],
    evaluate_stage: dict[str, object],
    evolve_stage: dict[str, object],
    *,
    mode: str,
    path: str,
    confidence: str,
    completion_state: str,
    completion: bool,
    top_approaches: list[str],
    evidence: list[dict[str, object]],
    scores: list[float],
    triage_packet: str | None = None,
    deferred_work: dict[str, object] | None = None,
) -> dict[str, object]:
    package = {
        "contract_version": CONTRACT_VERSION,
        "question_id": question_id,
        "skill": skill,
        "request_class": request_class,
        "question": question,
        "mode": mode,
        "path": path,
        "confidence": confidence,
        "completion": completion,
        "completion_state": completion_state,
        "answer": answer_text,
        "top_approaches": top_approaches,
        "evidence": evidence,
        "scores": scores,
        "triage_packet": triage_packet,
        "deferred_work": deferred_work,
        "completion_package": {
            "request": {
                "question_id": question_id,
                "received_at": iso_utc_now(),
                "question": question,
                "skill": skill,
                "request_class": request_class,
            },
            "sense": sense_stage,
            "retrieve": retrieve_stage,
            "compose": compose_stage,
            "gate": gate_stage,
            "execute": execute_stage,
            "evaluate": evaluate_stage,
            "evolve": evolve_stage,
        },
    }
    return package


def make_learning_row(question_id: str, question: str, skill: str, package: dict[str, object]) -> dict[str, object]:
    return {
        "recorded_at": iso_utc_now(),
        "question_id": question_id,
        "question": question,
        "request_class": package.get("request_class"),
        "mode": package.get("mode"),
        "path": package.get("path"),
        "skill": skill,
        "confidence": package.get("confidence"),
        "completion_state": package.get("completion_state"),
        "escalated": package.get("completion_state") == COMPLETED_ESCALATION,
        "sources": sorted({str(item.get("source_file")) for item in package.get("evidence", [])}),
    }


def run_echo_skill(question_id: str, question: str, skill: str) -> dict[str, object]:
    """Deterministic starter skill: echo input exactly (RockBot-style smoke test)."""
    sense = sense_request(question, skill)
    return finalize_package(
        question_id,
        question,
        skill,
        str(sense.get("request_class")),
        f"Echo: {question}",
        make_stage("sense", "completed", **sense),
        make_stage("retrieve", "skipped", reason="echo skill does not retrieve memory"),
        make_stage("compose", "completed", selected_skill="echo", selected_path=FAST_PATH, strategy="deterministic-echo"),
        make_stage("gate", "passed", policy="pass-through"),
        make_stage("execute", "completed", executor="echo", artifacts=[]),
        make_stage("evaluate", "completed", completion_state=COMPLETED_ANSWER, outcome="answer-returned"),
        make_stage("evolve", "completed", learning_action="log-run-only"),
        mode="fast",
        path=FAST_PATH,
        confidence="high",
        completion_state=COMPLETED_ANSWER,
        completion=True,
        top_approaches=["echo"],
        evidence=[],
        scores=[],
    )


def run_assistance_request(question_id: str, question: str, skill: str) -> dict[str, object]:
    """Queue deferred work for asynchronous completion by a helper bot/agent."""
    sense = sense_request(question, skill)
    deferred_item = {
        "queued_at": iso_utc_now(),
        "question_id": question_id,
        "request_class": "assistance-request",
        "status": "queued",
        "question": question,
        "depends_on": "external-assistant-or-bot",
        "completion_target": "complete-original-request-after-async-result",
    }
    append_jsonl(PROSPECTIVE_MEMORY_QUEUE_PATH, deferred_item)

    answer = (
        "Deferred work queued for asynchronous assistance.\n"
        "- Completion status: completed_deferred_work\n"
        f"- Queue file: {PROSPECTIVE_MEMORY_QUEUE_PATH}\n"
        "- Next step: wait for external response, then resume original request"
    )

    return finalize_package(
        question_id,
        question,
        skill,
        str(sense.get("request_class")),
        answer,
        make_stage("sense", "completed", **sense),
        make_stage("retrieve", "skipped", reason="assistance request does not require retrieval"),
        make_stage("compose", "completed", selected_skill="assistance-request", selected_path=FAST_PATH, strategy="queue-deferred-work"),
        make_stage("gate", "passed", policy="pass-through"),
        make_stage("execute", "completed", executor="deferred-work-queue", artifacts=[str(PROSPECTIVE_MEMORY_QUEUE_PATH)]),
        make_stage("evaluate", "completed", completion_state=COMPLETED_DEFERRED_WORK, outcome="deferred-work-queued"),
        make_stage("evolve", "completed", learning_action="log-deferred-work-request"),
        mode="deferred",
        path=FAST_PATH,
        confidence="high",
        completion_state=COMPLETED_DEFERRED_WORK,
        completion=True,
        top_approaches=["assistance-request"],
        evidence=[],
        scores=[],
        deferred_work=deferred_item,
    )


def run_memory_search(
    question_id: str,
    question: str,
    skill: str,
    summary: dict[str, object],
    events: list[dict[str, object]],
    learning_weights: dict[str, float],
) -> dict[str, object]:
    sense = sense_request(question, skill)
    sense_stage = make_stage("sense", "completed", **sense)

    if sense["asks_clarification"]:
        clarification = compose_clarification_answer(sense)
        return finalize_package(
            question_id,
            question,
            skill,
            str(sense.get("request_class")),
            clarification["answer"],
            sense_stage,
            make_stage("retrieve", "skipped", reason="clarification required before trusted retrieval"),
            make_stage("compose", "completed", selected_skill="clarification", selected_path=FAST_PATH, strategy="ask-bounded-questions"),
            make_stage("gate", "passed", policy="pass-through"),
            make_stage("execute", "completed", executor="clarification", artifacts=[]),
            make_stage("evaluate", "completed", completion_state=COMPLETED_NON_ANSWER, outcome="clarifying-questions-returned"),
            make_stage("evolve", "completed", learning_action="log-clarification-needed"),
            mode="clarify",
            path=FAST_PATH,
            confidence="high",
            completion_state=COMPLETED_NON_ANSWER,
            completion=True,
            top_approaches=clarification["top_approaches"],
            evidence=[],
            scores=[],
        )

    approach_hints = infer_approach_hints(question, summary)
    attempts = [
        attempt_memory_answer(question, summary, events, learning_weights, approach_hints, mode="fast", path=FAST_PATH),
        attempt_memory_answer(question, summary, events, learning_weights, approach_hints, mode="slow", path=THINKING_SLOW_PATH),
    ]

    for attempt in attempts:
        if attempt.answer["completion"]:
            evidence_rows = [summarize_evidence(item) for item in attempt.evidence[:6]]
            return finalize_package(
                question_id,
                question,
                skill,
                str(sense.get("request_class")),
                attempt.answer["answer"],
                sense_stage,
                make_stage(
                    "retrieve",
                    "completed",
                    approach_hints=approach_hints,
                    attempts=[
                        {
                            "mode": prior.mode,
                            "path": prior.path,
                            "evidence_count": len(prior.evidence),
                            "confidence": prior.answer.get("confidence"),
                        }
                        for prior in attempts
                        if prior.mode == attempt.mode or prior.mode == "fast"
                    ],
                    selected_mode=attempt.mode,
                    selected_evidence_count=len(evidence_rows),
                ),
                make_stage("compose", "completed", selected_skill="memory-search", selected_path=attempt.path, strategy=f"{attempt.mode}-retrieval"),
                make_stage("gate", "passed", policy="pass-through"),
                make_stage("execute", "completed", executor="memory-search", artifacts=[]),
                make_stage("evaluate", "completed", completion_state=COMPLETED_ANSWER, outcome="grounded-answer-returned"),
                make_stage("evolve", "completed", learning_action="log-retrieval-sources"),
                mode=attempt.mode,
                path=attempt.path,
                confidence=str(attempt.answer.get("confidence")),
                completion_state=COMPLETED_ANSWER,
                completion=True,
                top_approaches=list(attempt.answer.get("top_approaches", [])),
                evidence=evidence_rows,
                scores=list(attempt.answer.get("scores", [])),
            )

    invention_attempt = attempt_memory_answer(question, summary, events, learning_weights, approach_hints, mode="slower", path=INVENTION_PATH)
    packet_path = create_triage_packet(question, [attempt.mode for attempt in attempts], invention_attempt.evidence)
    answer_text = invention_attempt.answer["answer"] + (
        "\n- Escalation: fast and thinking-slow retrieval were insufficient, so an invention-path triage packet was generated."
        f"\n- Triage packet: {packet_path}"
    )
    return finalize_package(
        question_id,
        question,
        skill,
        str(sense.get("request_class")),
        answer_text,
        sense_stage,
        make_stage(
            "retrieve",
            "completed",
            approach_hints=approach_hints,
            attempts=[
                {
                    "mode": attempt.mode,
                    "path": attempt.path,
                    "evidence_count": len(attempt.evidence),
                    "confidence": attempt.answer.get("confidence"),
                }
                for attempt in [*attempts, invention_attempt]
            ],
            selected_mode="slower",
            selected_evidence_count=min(12, len(invention_attempt.evidence)),
        ),
        make_stage("compose", "completed", selected_skill="triage-packet", selected_path=INVENTION_PATH, strategy="escalate-capability-gap"),
        make_stage("gate", "passed", policy="pass-through"),
        make_stage("execute", "completed", executor="triage-packet", artifacts=[str(packet_path)]),
        make_stage("evaluate", "completed", completion_state=COMPLETED_ESCALATION, outcome="triage-packet-generated"),
        make_stage("evolve", "completed", learning_action="log-escalation-and-packet"),
        mode="slower",
        path=INVENTION_PATH,
        confidence=str(invention_attempt.answer.get("confidence")),
        completion_state=COMPLETED_ESCALATION,
        completion=True,
        top_approaches=list(invention_attempt.answer.get("top_approaches", [])),
        evidence=[summarize_evidence(item) for item in invention_attempt.evidence[:12]],
        scores=list(invention_attempt.answer.get("scores", [])),
        triage_packet=str(packet_path),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ask RoadTrip memory and execute fast/slow/slower completion loop.")
    parser.add_argument("question", nargs="?", help="Question to ask memory index")
    parser.add_argument("--skill", choices=["memory-search", "echo", "assistance-request"], default="memory-search", help="Skill to run (memory-search, echo, or assistance-request)")
    parser.add_argument("--events", default=str(EVENT_INDEX_PATH), help="Path to session_log_events.jsonl")
    parser.add_argument("--summary", default=str(SUMMARY_PATH), help="Path to ppa_approach_summary.json")
    parser.add_argument("--feedback", choices=["helpful", "not-helpful"], help="Record feedback for a previous question")
    parser.add_argument("--question-id", help="Question id for feedback")
    parser.add_argument("--note", default="", help="Optional note for feedback")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.feedback:
        if not args.question_id:
            raise SystemExit("--question-id is required when using --feedback")
        append_jsonl(
            LEARNING_LOG_PATH,
            {
                "recorded_at": iso_utc_now(),
                "question_id": args.question_id,
                "feedback": args.feedback,
                "note": args.note,
                "sources": [],
            },
        )
        print(f"Recorded feedback for {args.question_id}: {args.feedback}")
        return

    if not args.question:
        raise SystemExit("Provide a question, for example: py scripts\\ppa_ask.py \"what did we decide about memory?\"")

    question = normalize_question(args.question)
    question_id = build_question_id()

    if args.skill == "echo":
        output = run_echo_skill(question_id, question, args.skill)
    elif args.skill == "assistance-request":
        output = run_assistance_request(question_id, question, args.skill)
    else:
        events_path = Path(args.events)
        summary_path = Path(args.summary)
        if not events_path.exists() or not summary_path.exists():
            raise SystemExit("Memory index missing. Run: py scripts\\analyze_session_logs_for_ppa.py")

        events = load_jsonl(events_path)
        summary = load_json(summary_path)
        learning_weights = get_learning_weights(LEARNING_LOG_PATH)
        output = run_memory_search(question_id, question, args.skill, summary, events, learning_weights)

    append_jsonl(LEARNING_LOG_PATH, make_learning_row(question_id, question, args.skill, output))

    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=True))
    else:
        print(f"question_id: {question_id}")
        print(
            " | ".join(
                [
                    f"skill: {output.get('skill')}",
                    f"request_class: {output.get('request_class')}",
                    f"mode: {output.get('mode')}",
                    f"path: {output.get('path')}",
                    f"confidence: {output.get('confidence')}",
                    f"completion: {output.get('completion')}",
                    f"state: {output.get('completion_state')}",
                ]
            )
        )
        if output.get("triage_packet"):
            print(f"triage_packet: {output.get('triage_packet')}")
        print()
        print(output.get("answer", ""))
        print()
        print(f"feedback command: py scripts\\ppa_ask.py --feedback helpful --question-id {question_id} --note \"optional note\"")


if __name__ == "__main__":
    main()
