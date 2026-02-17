"""Deterministic guardrails for memory safety and irreversible operations."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class CeilingCheckResult:
    """Result of MEMORY.md ceiling evaluation."""

    state: str  # ok | soft_limit | hard_limit
    line_count: int
    soft_limit: int
    hard_limit: int
    pruned_lines: int = 0


class MemoryCeilingError(RuntimeError):
    """Raised when hard ceiling is exceeded and cannot be remediated."""


class MemoryGuardrails:
    """Ceiling checks and deterministic pruning for memory artifacts."""

    def __init__(
        self,
        soft_limit: int = 450,
        hard_limit: int = 500,
        prune_target: int = 400,
        auto_rule_prefix: str = "- [AUTO]",
    ) -> None:
        self.soft_limit = soft_limit
        self.hard_limit = hard_limit
        self.prune_target = prune_target
        self.auto_rule_prefix = auto_rule_prefix

    def evaluate(self, memory_path: str = "MEMORY.md") -> CeilingCheckResult:
        """Evaluate current line count without mutation."""

        path = Path(memory_path)
        line_count = self._line_count(path)

        if line_count > self.hard_limit:
            return CeilingCheckResult("hard_limit", line_count, self.soft_limit, self.hard_limit)
        if line_count > self.soft_limit:
            return CeilingCheckResult("soft_limit", line_count, self.soft_limit, self.hard_limit)
        return CeilingCheckResult("ok", line_count, self.soft_limit, self.hard_limit)

    def enforce(self, memory_path: str = "MEMORY.md") -> CeilingCheckResult:
        """Enforce ceiling policy with deterministic pruning when needed."""

        path = Path(memory_path)
        initial = self.evaluate(memory_path)
        if initial.state == "ok":
            return initial

        pruned = self._prune_auto_rules(path)
        updated = self.evaluate(memory_path)
        updated.pruned_lines = pruned

        if updated.state == "hard_limit":
            raise MemoryCeilingError(
                f"{memory_path} remains above hard limit after pruning: "
                f"{updated.line_count}/{self.hard_limit}"
            )

        return updated

    def _line_count(self, path: Path) -> int:
        if not path.exists():
            return 0
        with open(path, "r", encoding="utf-8") as handle:
            return sum(1 for _ in handle)

    def _prune_auto_rules(self, path: Path) -> int:
        """Prune oldest auto-generated rules until prune_target is reached."""

        if not path.exists():
            return 0

        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        if len(lines) <= self.prune_target:
            return 0

        removable_indexes = [
            index for index, line in enumerate(lines)
            if line.lstrip().startswith(self.auto_rule_prefix)
        ]

        pruned = 0
        while len(lines) > self.prune_target and removable_indexes:
            index = removable_indexes.pop(0)
            if index >= len(lines):
                continue
            del lines[index]
            pruned += 1
            removable_indexes = [i - 1 if i > index else i for i in removable_indexes]

        path.write_text("".join(lines), encoding="utf-8")
        return pruned


class IrreversibleOperationGuard:
    """Blocks high-risk irreversible operations unless explicitly authorized."""

    BLOCK_PATTERNS = {
        r"\brm\b": "destructive_delete",
        r"\bdel\b": "destructive_delete",
        r"\bremove-item\b": "destructive_delete",
        r"git\s+push\s+--force": "history_rewrite",
        r"git\s+reset\s+--hard": "hard_reset",
        r"drop\s+database": "irreversible_data_loss",
    }

    def evaluate(
        self,
        operation_text: str,
        preauthorized: bool = False,
        has_dry_run: bool = False,
        rollback_available: bool = False,
    ) -> dict[str, Any]:
        """Evaluate whether operation can proceed deterministically."""

        operation = operation_text or ""
        for pattern, risk_code in self.BLOCK_PATTERNS.items():
            if re.search(pattern, operation, flags=re.IGNORECASE):
                if preauthorized and (has_dry_run or rollback_available):
                    return {
                        "decision": "ESCALATE",
                        "allowed": True,
                        "risk_code": risk_code,
                        "reason": "preauthorized irreversible operation with safeguards",
                    }
                return {
                    "decision": "BLOCK",
                    "allowed": False,
                    "risk_code": risk_code,
                    "reason": "irreversible operation missing required safeguards",
                }

        return {
            "decision": "ALLOW",
            "allowed": True,
            "risk_code": None,
            "reason": "operation not classified as irreversible-risk",
        }
