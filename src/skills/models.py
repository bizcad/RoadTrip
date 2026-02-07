"""Shared data models for the RoadTrip Skills Framework.

Defines typed dataclasses for skill inputs/outputs following the contracts
documented in skills/git-push-autonomous/CLAUDE.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Rules Engine models
# ---------------------------------------------------------------------------

@dataclass
class BlockedFile:
    """A file that failed safety validation."""
    path: str
    reason: str         # "explicit_blocklist" | "pattern_match"
    matched_rule: str   # The specific rule/pattern that triggered


@dataclass
class RulesResult:
    """Aggregate result from the rules-engine skill."""
    decision: str                            # "APPROVE" | "BLOCK_ALL"
    approved_files: list[str] = field(default_factory=list)
    blocked_files: list[BlockedFile] = field(default_factory=list)
    confidence: float = 0.99
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Config models
# ---------------------------------------------------------------------------

@dataclass
class SafetyRulesConfig:
    """Parsed representation of config/safety-rules.yaml."""
    blocked_files: list[str] = field(default_factory=list)
    blocked_patterns: list[str] = field(default_factory=list)
    max_file_size_mb: int = 50
    allow_override: bool = False


# ---------------------------------------------------------------------------
# Auth Validator models (stub for Phase 1b)
# ---------------------------------------------------------------------------

@dataclass
class AuthResult:
    """Result from the auth-validator skill."""
    decision: str       # "PASS" | "FAIL"
    reason: str = ""
    confidence: float = 0.0
    details: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Telemetry Logger models (stub for Phase 1b)
# ---------------------------------------------------------------------------

@dataclass
class StepResult:
    """A single step in an orchestrator decision flow."""
    step: int
    name: str
    status: str         # "PASS" | "FAIL"
    confidence: float = 0.0


@dataclass
class TelemetryEntry:
    """A complete decision log entry."""
    timestamp: str
    log_id: str
    orchestrator: str
    decision: str       # "APPROVED" | "BLOCKED" | "ERROR"
    confidence: float = 0.0
    steps: list[StepResult] = field(default_factory=list)
    context: dict = field(default_factory=dict)
    result: dict = field(default_factory=dict)
