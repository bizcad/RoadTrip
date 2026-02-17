"""Consolidation primitives for memory self-improvement workflows."""

from .sleep_consolidator import (
    ConsolidationCandidate,
    ConsolidationPipeline,
    QuarantineLogger,
    SafetyGateValidator,
    SleepConsolidator,
)
from .guardrails import CeilingCheckResult, IrreversibleOperationGuard, MemoryCeilingError, MemoryGuardrails
from .burned_patterns import BurnedPattern, BurnedPatternRegistry

__all__ = [
    "ConsolidationCandidate",
    "SleepConsolidator",
    "SafetyGateValidator",
    "QuarantineLogger",
    "ConsolidationPipeline",
    "CeilingCheckResult",
    "MemoryCeilingError",
    "MemoryGuardrails",
    "IrreversibleOperationGuard",
    "BurnedPattern",
    "BurnedPatternRegistry",
]
