#!/usr/bin/env python3
"""
telemetry_logger.py

Logs all decisions and outcomes in immutable JSONL format.
Enables audit trails, learning feedback, and forensic analysis.

Deterministic skill: append-only, safe for concurrent writes.
No external API calls; pure file I/O.

Usage:
    python telemetry_logger.py --log-file data/telemetry.jsonl --workflow-id push-123 --skill auth_validator --decision APPROVED
    from src.skills.telemetry_logger import TelemetryLogger
    result = TelemetryLogger().log_entry(entry)
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from .telemetry_logger_models import (
    TelemetryEntry,
    TelemetryLoggerInput,
    TelemetryLoggerResult,
)


class TelemetryLogger:
    """Logs telemetry entries to JSONL file."""

    def log_entry(
        self,
        entry: TelemetryEntry,
        log_file: str = "data/telemetry.jsonl",
    ) -> TelemetryLoggerResult:
        """
        Log a telemetry entry.
        
        Args:
            entry: TelemetryEntry to log
            log_file: Path to JSONL log file
        
        Returns:
            TelemetryLoggerResult with status and file info
        """
        
        log_path = Path(log_file)
        
        try:
            # Ensure directory exists
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Append entry as single JSON line
            json_line = entry.to_json_line()
            
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json_line + '\n')
            
            # Count total entries
            total_entries = self._count_entries(log_path)
            
            return TelemetryLoggerResult(
                success=True,
                log_file=str(log_path.absolute()),
                bytes_written=len(json_line) + 1,  # +1 for newline
                total_entries=total_entries,
                reasoning=f"Logged {entry.skill}/{entry.operation} decision: {entry.decision}",
            )
        
        except Exception as e:
            return TelemetryLoggerResult(
                success=False,
                log_file=str(log_path.absolute()),
                bytes_written=0,
                total_entries=0,
                reasoning=f"Failed to log telemetry entry.",
                error_code="LOG_WRITE_FAILED",
                error_message=str(e),
            )
    
    def _count_entries(self, log_path: Path) -> int:
        """Count total lines (entries) in JSONL file."""
        if not log_path.exists():
            return 0
        
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f)
        except Exception:
            return 0
    
    def read_entries(
        self,
        log_file: str = "data/telemetry.jsonl",
        workflow_id: Optional[str] = None,
        skill: Optional[str] = None,
    ) -> list[TelemetryEntry]:
        """
        Read telemetry entries from log file.
        
        Args:
            log_file: Path to JSONL log file
            workflow_id: Filter by workflow_id (optional)
            skill: Filter by skill name (optional)
        
        Returns:
            List of TelemetryEntry objects
        """
        
        log_path = Path(log_file)
        
        if not log_path.exists():
            return []
        
        entries = []
        
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        entry = TelemetryEntry.from_dict(data)
                        
                        # Apply filters
                        if workflow_id and entry.workflow_id != workflow_id:
                            continue
                        if skill and entry.skill != skill:
                            continue
                        
                        entries.append(entry)
                    
                    except json.JSONDecodeError:
                        # Skip malformed lines
                        continue
        
        except Exception:
            pass
        
        return entries
