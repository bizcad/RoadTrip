"""
Data models for telemetry_logger skill.

Defines schema for immutable, machine-readable audit logs (JSONL format).
Each line is a complete JSON object representing one decision/action.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import json


@dataclass
class TelemetryEntry:
    """
    Single telemetry log entry (one line in JSONL).
    
    Immutable record of a decision or action in the workflow.
    Safe to log (no secrets, no sensitive PII beyond username).
    """
    timestamp: str                          # ISO 8601 UTC timestamp
    workflow_id: str                        # e.g., "push-abc123" (unique per run)
    decision_id: str                        # e.g., "auth-check-1" (unique per decision)
    skill: str                              # Which skill made this decision (auth_validator, rules_engine, commit_message)
    operation: str                          # What operation (validate, generate, push, etc.)
    
    # Input summary (no secrets)
    input_summary: Dict[str, Any]           # e.g., {"branch": "main", "files": 3}
    
    # Decision outcome
    decision: str                           # APPROVED, DENIED, ERROR, etc.
    confidence: float = 1.0                 # 0.0-1.0 (how sure are we?)
    reasoning: str = ""                     # Why this decision
    
    # Artifacts (safe to log)
    artifacts: Dict[str, Any] = field(default_factory=dict)  # e.g., {"files_affected": 3, "commit_hash": "abc123"}
    
    # Performance
    execution_time_ms: float = 0.0          # Milliseconds to execute
    
    # Guidance
    human_review_required: bool = False     # Should human review this?
    suggested_action: Optional[str] = None  # e.g., "Retry with updated credentials"
    
    # Error details (only if decision failed)
    error_code: Optional[str] = None        # e.g., "INVALID_TOKEN"
    error_message: Optional[str] = None     # Safe error message (no secrets)
    
    def to_json_line(self) -> str:
        """Convert to JSONL format (single line)."""
        return json.dumps(asdict(self), separators=(',', ':'))
    
    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'TelemetryEntry':
        """Create from dictionary."""
        return TelemetryEntry(**d)


@dataclass
class TelemetryLoggerInput:
    """Input to telemetry_logger skill."""
    entry: TelemetryEntry                   # The entry to log
    log_file: str = "data/telemetry.jsonl"  # Where to write
    append_mode: bool = True                # Append vs overwrite


@dataclass
class TelemetryLoggerResult:
    """Output of telemetry_logger skill."""
    success: bool                           # Was log written successfully?
    log_file: str                           # Path to log file
    bytes_written: int = 0                  # Bytes appended
    total_entries: int = 0                  # Total entries in log after write
    reasoning: str = ""                     # Why success/failure
    
    # Optional error details
    error_code: Optional[str] = None
    error_message: Optional[str] = None
