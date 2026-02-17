"""SQLite-based episodic index for telemetry retrieval.

Provides deterministic retrieval over historical telemetry records with
lightweight gating rules to avoid unnecessary context expansion.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


class EpisodicIndex:
    """Deterministic telemetry index and retrieval helper."""

    def __init__(self, db_path: str = "data/telemetry_index.sqlite") -> None:
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS telemetry_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    skill_name TEXT,
                    operation TEXT,
                    workflow_id TEXT,
                    decision TEXT,
                    confidence REAL,
                    error_category TEXT,
                    reasoning TEXT,
                    raw_json TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_telemetry_events_skill_time
                ON telemetry_events(skill_name, timestamp)
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_telemetry_events_error_time
                ON telemetry_events(error_category, timestamp)
                """
            )

    def index_log_file(self, log_file: str = "data/telemetry.jsonl") -> int:
        """Index telemetry entries from a JSONL log file.

        Returns:
            Number of records inserted.
        """

        path = Path(log_file)
        if not path.exists():
            return 0

        inserted = 0
        with self._connect() as conn:
            with open(path, "r", encoding="utf-8") as handle:
                for raw_line in handle:
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        payload = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    if not isinstance(payload, dict):
                        continue

                    conn.execute(
                        """
                        INSERT INTO telemetry_events(
                            timestamp,
                            skill_name,
                            operation,
                            workflow_id,
                            decision,
                            confidence,
                            error_category,
                            reasoning,
                            raw_json
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            payload.get("timestamp"),
                            payload.get("skill"),
                            payload.get("operation"),
                            payload.get("workflow_id"),
                            payload.get("decision"),
                            self._safe_float(payload.get("confidence")),
                            payload.get("error_code") or payload.get("error_category"),
                            payload.get("reasoning"),
                            json.dumps(payload, separators=(",", ":")),
                        ),
                    )
                    inserted += 1

        return inserted

    def needs_memory_retrieval(
        self,
        explicit_request: bool = False,
        error_occurred: bool = False,
        confidence: float = 1.0,
        dissonance: bool = False,
        threshold: float = 0.85,
    ) -> bool:
        """Deterministic retrieval gate.

        Returns True when retrieval should run.
        """

        return bool(
            explicit_request
            or error_occurred
            or dissonance
            or confidence < threshold
        )

    def search(
        self,
        query: str = "",
        skill_name: str | None = None,
        error_category: str | None = None,
        time_window_days: int | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Search indexed telemetry with deterministic filters."""

        clauses: list[str] = []
        params: list[Any] = []

        if skill_name:
            clauses.append("skill_name = ?")
            params.append(skill_name)

        if error_category:
            clauses.append("error_category = ?")
            params.append(error_category)

        if query:
            clauses.append("(reasoning LIKE ? OR operation LIKE ? OR raw_json LIKE ?)")
            wildcard = f"%{query}%"
            params.extend([wildcard, wildcard, wildcard])

        if time_window_days is not None:
            cutoff = datetime.now(timezone.utc) - timedelta(days=time_window_days)
            clauses.append("timestamp >= ?")
            params.append(cutoff.isoformat())

        where_clause = ""
        if clauses:
            where_clause = "WHERE " + " AND ".join(clauses)

        sql = f"""
            SELECT timestamp, skill_name, operation, workflow_id,
                   decision, confidence, error_category, reasoning, raw_json
            FROM telemetry_events
            {where_clause}
            ORDER BY timestamp DESC
            LIMIT ?
        """
        params.append(max(1, limit))

        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()

        return [
            {
                "timestamp": row["timestamp"],
                "skill_name": row["skill_name"],
                "operation": row["operation"],
                "workflow_id": row["workflow_id"],
                "decision": row["decision"],
                "confidence": row["confidence"],
                "error_category": row["error_category"],
                "reasoning": row["reasoning"],
                "raw_json": row["raw_json"],
            }
            for row in rows
        ]

    def count_events(self) -> int:
        """Return total indexed event count."""

        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) as count FROM telemetry_events").fetchone()
        return int(row["count"])

    def _safe_float(self, value: Any) -> float:
        """Convert value to float with safe fallback."""

        try:
            if value is None:
                return 0.0
            return float(value)
        except (TypeError, ValueError):
            return 0.0
