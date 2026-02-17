"""Adaptive execution with registry-first lookup, bounded self-correction, and metrics logging."""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from src.skills.registry.fingerprint_generator import FingerprintGenerator
from src.skills.registry.fingerprint_verifier import FingerprintVerifier
from src.skills.registry.registry_reader import RegistryReader
from src.skills.registry.verification import Verification


@dataclass
class AdaptiveExecutionResult:
    """Result returned by adaptive executor."""

    success: bool
    decision: str
    intent: str
    workflow_id: str
    skill_name: Optional[str] = None
    attempts: int = 0
    output: Optional[dict] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class AdaptiveExecutor:
    """Registry-first adaptive executor with one-step self-correct retry."""

    def __init__(
        self,
        repo_root: str = ".",
        registry_path: str = "config/skills-registry.yaml",
        metrics_log_path: str = "logs/execution_metrics.jsonl",
        use_mock_fingerprint: bool = True,
    ):
        self.repo_root = Path(repo_root).resolve()
        self.registry_path = self.repo_root / registry_path
        self.metrics_log_path = self.repo_root / metrics_log_path
        self.use_mock_fingerprint = use_mock_fingerprint

    def execute_prompt(
        self,
        prompt: str,
        context: Optional[dict] = None,
        max_retry_depth: int = 1,
    ) -> AdaptiveExecutionResult:
        """Execute prompt via semantic intent + registry lookup + bounded retry."""
        workflow_id = f"adaptive-{uuid.uuid4().hex[:10]}"
        context = context or {}

        self._log_event(workflow_id, "DIRECTIVE_RECEIVED", {"prompt": prompt})

        intent = self._semantic_intent(prompt)
        if intent == "unknown":
            self._log_event(
                workflow_id,
                "STOP_UNKNOWN_INTENT",
                {"prompt": prompt, "reason": "No deterministic intent mapping"},
            )
            return AdaptiveExecutionResult(
                success=False,
                decision="STOP",
                intent="unknown",
                workflow_id=workflow_id,
                error_code="UNKNOWN_INTENT",
                error_message="Prompt did not match supported deterministic intents.",
            )

        registry_reader = RegistryReader(
            registry_path=str(self.registry_path),
            use_mock=self.use_mock_fingerprint,
        )
        registry = registry_reader.read_registry()
        if not registry or not registry.skills:
            self._log_event(workflow_id, "STOP_REGISTRY_EMPTY", {"intent": intent})
            return AdaptiveExecutionResult(
                success=False,
                decision="STOP",
                intent=intent,
                workflow_id=workflow_id,
                error_code="REGISTRY_EMPTY",
                error_message="Registry is empty; no certified skills available.",
            )

        self._log_event(
            workflow_id,
            "REGISTRY_LOADED",
            {"intent": intent, "skills": len(registry.skills)},
        )

        excluded: set[str] = set()
        attempt_limit = max(1, max_retry_depth + 1)

        for attempt_idx in range(attempt_limit):
            attempt_number = attempt_idx + 1
            resolution = self._resolve_skill(intent, registry_reader, excluded)
            if not resolution:
                self._log_event(
                    workflow_id,
                    "STOP_NO_SOLUTION",
                    {"intent": intent, "attempt": attempt_number},
                )
                return AdaptiveExecutionResult(
                    success=False,
                    decision="STOP",
                    intent=intent,
                    workflow_id=workflow_id,
                    attempts=attempt_number - 1,
                    error_code="NO_SOLUTION",
                    error_message="No registry skill or fallback resolved this intent.",
                )

            skill_name, metadata = resolution
            excluded.add(skill_name)
            self._log_event(
                workflow_id,
                "SOLUTION_FOUND",
                {
                    "intent": intent,
                    "attempt": attempt_number,
                    "skill": skill_name,
                    "entry_point": metadata.entry_point,
                },
            )

            allowed, fingerprint_message = self._enforce_fingerprint(skill_name, registry_reader)
            self._log_event(
                workflow_id,
                "FINGERPRINT_CHECK",
                {
                    "skill": skill_name,
                    "allowed": allowed,
                    "message": fingerprint_message,
                    "attempt": attempt_number,
                },
            )

            if not allowed:
                if attempt_number >= attempt_limit:
                    return AdaptiveExecutionResult(
                        success=False,
                        decision="STOP",
                        intent=intent,
                        workflow_id=workflow_id,
                        attempts=attempt_number,
                        skill_name=skill_name,
                        error_code="FINGERPRINT_MISMATCH",
                        error_message=fingerprint_message,
                    )
                continue

            skill_callable = self._load_skill_callable(metadata.entry_point)
            if not skill_callable:
                self._log_event(
                    workflow_id,
                    "EXECUTION_ERROR",
                    {
                        "skill": skill_name,
                        "attempt": attempt_number,
                        "reason": "Entry point missing callable",
                    },
                )
                if attempt_number >= attempt_limit:
                    return AdaptiveExecutionResult(
                        success=False,
                        decision="STOP",
                        intent=intent,
                        workflow_id=workflow_id,
                        attempts=attempt_number,
                        skill_name=skill_name,
                        error_code="ENTRYPOINT_INVALID",
                        error_message=f"Skill {skill_name} has no callable entry point.",
                    )
                continue

            skill_input = self._build_skill_input(intent, prompt, context)

            try:
                output = self._invoke_skill(skill_callable, skill_input)
            except Exception as exc:
                self._log_event(
                    workflow_id,
                    "EXECUTION_EXCEPTION",
                    {
                        "skill": skill_name,
                        "attempt": attempt_number,
                        "exception": str(exc),
                    },
                )
                if attempt_number >= attempt_limit:
                    return AdaptiveExecutionResult(
                        success=False,
                        decision="STOP",
                        intent=intent,
                        workflow_id=workflow_id,
                        attempts=attempt_number,
                        skill_name=skill_name,
                        error_code="EXECUTION_EXCEPTION",
                        error_message=str(exc),
                    )
                continue

            success = self._is_success(output)
            if success:
                self._log_event(
                    workflow_id,
                    "EXECUTION_SUCCESS",
                    {
                        "skill": skill_name,
                        "attempt": attempt_number,
                    },
                )
                return AdaptiveExecutionResult(
                    success=True,
                    decision="EXECUTED",
                    intent=intent,
                    workflow_id=workflow_id,
                    skill_name=skill_name,
                    attempts=attempt_number,
                    output=output if isinstance(output, dict) else {"result": output},
                )

            self._log_event(
                workflow_id,
                "EXECUTION_FAILED",
                {
                    "skill": skill_name,
                    "attempt": attempt_number,
                    "output": output,
                },
            )

            if attempt_number >= attempt_limit:
                return AdaptiveExecutionResult(
                    success=False,
                    decision="STOP",
                    intent=intent,
                    workflow_id=workflow_id,
                    attempts=attempt_number,
                    skill_name=skill_name,
                    error_code="EXECUTION_FAILED",
                    error_message="Skill execution failed and retry depth exhausted.",
                    output=output if isinstance(output, dict) else {"result": output},
                )

        return AdaptiveExecutionResult(
            success=False,
            decision="STOP",
            intent=intent,
            workflow_id=workflow_id,
            error_code="UNREACHABLE",
            error_message="Execution ended unexpectedly.",
        )

    def _semantic_intent(self, prompt: str) -> str:
        normalized = (prompt or "").strip().lower()
        if not normalized:
            return "unknown"

        push_patterns = (
            r"\bpush\s+my\s+changes\b",
            r"\bpush\s+changes\b",
            r"\bpush\s+the\s+latest\s+changes\b",
            r"\bplease\s+push\s+the\s+latest\s+changes\b",
            r"\bgit\s+push\b",
        )
        if any(re.search(pattern, normalized) for pattern in push_patterns):
            return "git_push"

        return "unknown"

    def _resolve_skill(
        self,
        intent: str,
        registry_reader: RegistryReader,
        excluded: set[str],
    ) -> Optional[tuple[str, Any]]:
        registry = registry_reader.read_registry()
        if registry is None:
            return None

        candidates: list[tuple[str, Any]] = []

        for skill_name, metadata in registry.skills.items():
            if skill_name in excluded:
                continue
            status = str(getattr(metadata, "status", "")).lower()
            if "deprecated" in status or "suspended" in status:
                continue

            capabilities = [str(c).lower() for c in (metadata.capabilities or [])]
            if intent == "git_push":
                if skill_name == "git_push_autonomous":
                    candidates.insert(0, (skill_name, metadata))
                    continue
                if "push_git_commit" in capabilities or "git_push" in capabilities:
                    candidates.append((skill_name, metadata))

        if candidates:
            return candidates[0]

        return None

    def _enforce_fingerprint(self, skill_name: str, registry_reader: RegistryReader) -> tuple[bool, str]:
        generator = FingerprintGenerator(
            use_mock=self.use_mock_fingerprint,
            registry_reader=registry_reader,
        )
        verifier = FingerprintVerifier(
            fingerprint_generator=generator,
            registry_reader=registry_reader,
            use_mock=self.use_mock_fingerprint,
        )
        enforcer = Verification(fingerprint_verifier=verifier, use_mock=self.use_mock_fingerprint)
        return enforcer.enforce(skill_name)

    def _load_skill_callable(self, entry_point: str) -> Optional[Callable[..., Any]]:
        if not entry_point:
            return None

        module_path = entry_point.split("::", 1)[0]
        function_name = entry_point.split("::", 1)[1] if "::" in entry_point else "execute"

        path = Path(module_path)
        if not path.is_absolute():
            path = self.repo_root / path
        if not path.exists():
            return None

        module_name = f"adaptive_skill_{path.stem}_{uuid.uuid4().hex[:8]}"
        spec = importlib.util.spec_from_file_location(module_name, str(path))
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return getattr(module, function_name, None)

    def _build_skill_input(self, intent: str, prompt: str, context: dict) -> dict:
        payload = dict(context)
        payload.setdefault("prompt", prompt)
        payload.setdefault("repo_path", str(self.repo_root))

        if intent == "git_push":
            payload.setdefault("branch", "main")
            payload.setdefault("remote", "origin")

        return payload

    def _invoke_skill(self, skill_callable: Callable[..., Any], skill_input: dict) -> Any:
        signature = inspect.signature(skill_callable)
        if len(signature.parameters) == 1:
            return skill_callable(skill_input)

        return skill_callable(**skill_input)

    def _is_success(self, output: Any) -> bool:
        if isinstance(output, dict):
            if "success" in output:
                return bool(output["success"])
            if "status" in output:
                return str(output["status"]).lower() in {"success", "ok", "approved", "valid"}
        return bool(output)

    def _log_event(self, workflow_id: str, event_type: str, payload: dict) -> None:
        self.metrics_log_path.parent.mkdir(parents=True, exist_ok=True)
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "workflow_id": workflow_id,
            "event_type": event_type,
            "payload": payload,
        }
        with open(self.metrics_log_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(event) + "\n")


def compute_mock_fingerprint(skill_name: str, version: str) -> str:
    """Helper for tests/bootstrapping mock-mode fingerprint values."""
    return hashlib.sha256(f"{skill_name}:{version}".encode()).hexdigest()[:16]
