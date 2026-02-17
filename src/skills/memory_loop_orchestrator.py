"""WS-E integration orchestrator for self-improvement memory workflows."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from .consolidation import (
    BurnedPatternRegistry,
    ConsolidationCandidate,
    ConsolidationPipeline,
    IrreversibleOperationGuard,
    MemoryCeilingError,
    MemoryGuardrails,
    QuarantineLogger,
)
from .episodic_index import EpisodicIndex
from .registry import VersionProvenanceResult, VersionProvenanceVerifier
from .session_bootstrap import SessionBootstrap


@dataclass
class ProvenanceSummary:
    all_valid: bool
    results: list[VersionProvenanceResult]


@dataclass
class MemoryLoopResult:
    decision: str
    reason: str
    operation_guard: dict[str, Any]
    ceiling_state: str
    ceiling_line_count: int
    indexed_count: int
    retrieval_needed: bool
    retrieved_count: int
    bootstrap_context: dict[str, Any]
    promoted: list[dict[str, Any]]
    quarantined: list[dict[str, Any]]
    blocked_by_cooldown: list[dict[str, Any]]
    provenance: ProvenanceSummary


class MemoryLoopOrchestrator:
    """Coordinates WS-A/B/C/D modules into one deterministic runtime loop."""

    def __init__(
        self,
        telemetry_log: str = "data/telemetry.jsonl",
        index_db: str = "data/telemetry_index.sqlite",
        memory_file: str = "MEMORY.md",
        quarantine_log: str = "logs/consolidation_quarantine.jsonl",
        burned_registry_file: str = "logs/burned_patterns.json",
    ) -> None:
        self.telemetry_log = telemetry_log
        self.memory_file = memory_file
        self.bootstrap = SessionBootstrap()
        self.index = EpisodicIndex(db_path=index_db)
        self.consolidation = ConsolidationPipeline(
            quarantine_logger=QuarantineLogger(log_file=quarantine_log)
        )
        self.memory_guardrails = MemoryGuardrails()
        self.operation_guard = IrreversibleOperationGuard()
        self.burned_registry = BurnedPatternRegistry(registry_file=burned_registry_file)
        self.provenance_verifier = VersionProvenanceVerifier()

    def run_cycle(
        self,
        operation_text: str = "",
        skill_dirs: list[str] | None = None,
        explicit_request: bool = False,
        error_occurred: bool = False,
        confidence: float = 1.0,
        dissonance: bool = False,
        query: str = "",
        preauthorized: bool = False,
        has_dry_run: bool = False,
        rollback_available: bool = False,
    ) -> MemoryLoopResult:
        """Run a full deterministic memory self-improvement cycle."""

        try:
            ceiling = self.memory_guardrails.enforce(self.memory_file)
        except MemoryCeilingError as exc:
            block_result = self.operation_guard.evaluate("")
            return MemoryLoopResult(
                decision="BLOCK",
                reason=str(exc),
                operation_guard=block_result,
                ceiling_state="hard_limit",
                ceiling_line_count=0,
                indexed_count=0,
                retrieval_needed=False,
                retrieved_count=0,
                bootstrap_context={
                    "recent_failures": [],
                    "active_skills": [],
                    "pending_reminders": [],
                    "trip_context": {"enabled": False, "data": None},
                },
                promoted=[],
                quarantined=[],
                blocked_by_cooldown=[],
                provenance=ProvenanceSummary(all_valid=False, results=[]),
            )

        operation_guard = self.operation_guard.evaluate(
            operation_text=operation_text,
            preauthorized=preauthorized,
            has_dry_run=has_dry_run,
            rollback_available=rollback_available,
        )
        if operation_guard["decision"] == "BLOCK":
            return MemoryLoopResult(
                decision="BLOCK",
                reason=operation_guard["reason"],
                operation_guard=operation_guard,
                ceiling_state=ceiling.state,
                ceiling_line_count=ceiling.line_count,
                indexed_count=0,
                retrieval_needed=False,
                retrieved_count=0,
                bootstrap_context={
                    "recent_failures": [],
                    "active_skills": [],
                    "pending_reminders": [],
                    "trip_context": {"enabled": False, "data": None},
                },
                promoted=[],
                quarantined=[],
                blocked_by_cooldown=[],
                provenance=ProvenanceSummary(all_valid=False, results=[]),
            )

        bootstrap_context = self.bootstrap.load_context(log_file=self.telemetry_log)
        indexed_count = self.index.index_log_file(log_file=self.telemetry_log)

        retrieval_needed = self.index.needs_memory_retrieval(
            explicit_request=explicit_request,
            error_occurred=error_occurred,
            confidence=confidence,
            dissonance=dissonance,
        )

        retrieved = self.index.search(query=query, limit=20) if retrieval_needed else []
        retrieved_events = [self._to_event(row) for row in retrieved]

        consolidation_outcome = self.consolidation.process(retrieved_events)
        promoted_candidates: list[ConsolidationCandidate] = list(
            consolidation_outcome.get("promoted", [])
        )
        quarantined_candidates: list[ConsolidationCandidate] = list(
            consolidation_outcome.get("quarantined", [])
        )

        cooled: list[ConsolidationCandidate] = []
        active_promoted: list[ConsolidationCandidate] = []
        for candidate in promoted_candidates:
            if self.burned_registry.is_blocked(candidate.cluster_key):
                cooled.append(candidate)
            else:
                active_promoted.append(candidate)

        provenance = self._verify_provenance(skill_dirs or [])

        final_decision = operation_guard["decision"]
        final_reason = operation_guard["reason"]
        if not provenance.all_valid:
            final_decision = "BLOCK"
            final_reason = "version provenance verification failed"

        return MemoryLoopResult(
            decision=final_decision,
            reason=final_reason,
            operation_guard=operation_guard,
            ceiling_state=ceiling.state,
            ceiling_line_count=ceiling.line_count,
            indexed_count=indexed_count,
            retrieval_needed=retrieval_needed,
            retrieved_count=len(retrieved_events),
            bootstrap_context=bootstrap_context,
            promoted=[asdict(item) for item in active_promoted],
            quarantined=[asdict(item) for item in quarantined_candidates],
            blocked_by_cooldown=[asdict(item) for item in cooled],
            provenance=provenance,
        )

    def _verify_provenance(self, skill_dirs: list[str]) -> ProvenanceSummary:
        results: list[VersionProvenanceResult] = []
        all_valid = True

        for skill_dir in skill_dirs:
            result = self.provenance_verifier.verify_skill_directory(skill_dir)
            results.append(result)
            if not result.valid:
                all_valid = False

        return ProvenanceSummary(all_valid=all_valid, results=results)

    def _to_event(self, row: dict[str, Any]) -> dict[str, Any]:
        raw_json = row.get("raw_json")
        if isinstance(raw_json, str) and raw_json.strip():
            try:
                payload = json.loads(raw_json)
                if isinstance(payload, dict):
                    return payload
            except json.JSONDecodeError:
                pass

        return {
            "timestamp": row.get("timestamp"),
            "skill": row.get("skill_name"),
            "operation": row.get("operation"),
            "workflow_id": row.get("workflow_id"),
            "decision": row.get("decision"),
            "confidence": row.get("confidence"),
            "error_code": row.get("error_category"),
            "reasoning": row.get("reasoning"),
        }


def run_memory_loop(**kwargs: Any) -> dict[str, Any]:
    """Execute memory loop and return dict-shaped output for workflow chaining."""

    orchestrator = MemoryLoopOrchestrator(
        telemetry_log=kwargs.get("telemetry_log", "data/telemetry.jsonl"),
        index_db=kwargs.get("index_db", "data/telemetry_index.sqlite"),
        memory_file=kwargs.get("memory_file", "MEMORY.md"),
        quarantine_log=kwargs.get("quarantine_log", "logs/consolidation_quarantine.jsonl"),
        burned_registry_file=kwargs.get("burned_registry_file", "logs/burned_patterns.json"),
    )
    result = orchestrator.run_cycle(
        operation_text=kwargs.get("operation_text", ""),
        skill_dirs=kwargs.get("skill_dirs", []),
        explicit_request=kwargs.get("explicit_request", False),
        error_occurred=kwargs.get("error_occurred", False),
        confidence=kwargs.get("confidence", 1.0),
        dissonance=kwargs.get("dissonance", False),
        query=kwargs.get("query", ""),
        preauthorized=kwargs.get("preauthorized", False),
        has_dry_run=kwargs.get("has_dry_run", False),
        rollback_available=kwargs.get("rollback_available", False),
    )

    payload = asdict(result)
    payload["provenance"]["results"] = [asdict(item) for item in result.provenance.results]
    return payload
