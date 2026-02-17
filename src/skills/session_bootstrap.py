"""Session bootstrap for deterministic context loading.

Loads a minimal context payload from telemetry logs to prime each session
without dumping full history into the prompt context.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


class SessionBootstrap:
    """Builds a lightweight startup context from telemetry history."""

    FAILURE_DECISIONS = {"DENIED", "ERROR", "FAILED", "BLOCKED"}

    def load_context(
        self,
        log_file: str = "data/telemetry.jsonl",
        recent_days: int = 7,
        recent_failures_limit: int = 3,
        active_window_days: int = 30,
        active_skills_limit: int = 5,
        include_trip_context: bool = False,
    ) -> dict[str, Any]:
        """Load minimal session context from telemetry.

        Args:
            log_file: Path to telemetry JSONL file.
            recent_days: Days to look back for failures.
            recent_failures_limit: Max number of failure examples to include.
            active_window_days: Days to look back for active skills.
            active_skills_limit: Max number of active skills to include.
            include_trip_context: Placeholder switch for future trip-context logic.

        Returns:
            Dict with recent_failures, active_skills, pending_reminders, trip_context.
        """

        entries = self._read_jsonl(log_file)
        now = datetime.now(timezone.utc)

        recent_failures = self._recent_failures(
            entries=entries,
            now=now,
            lookback_days=recent_days,
            limit=recent_failures_limit,
        )

        active_skills = self._active_skills(
            entries=entries,
            now=now,
            lookback_days=active_window_days,
            limit=active_skills_limit,
        )

        return {
            "recent_failures": recent_failures,
            "active_skills": active_skills,
            "pending_reminders": [],
            "trip_context": {"enabled": include_trip_context, "data": None},
        }

    def _read_jsonl(self, log_file: str) -> list[dict[str, Any]]:
        """Read telemetry JSONL file into a list of dictionaries."""

        path = Path(log_file)
        if not path.exists():
            return []

        records: list[dict[str, Any]] = []
        with open(path, "r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(payload, dict):
                    records.append(payload)

        return records

    def _recent_failures(
        self,
        entries: list[dict[str, Any]],
        now: datetime,
        lookback_days: int,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Extract recent failure examples from telemetry."""

        cutoff = now - timedelta(days=lookback_days)
        failures: list[dict[str, Any]] = []

        for item in entries:
            timestamp = self._parse_timestamp(item.get("timestamp"))
            if timestamp is None or timestamp < cutoff:
                continue

            decision = str(item.get("decision", "")).upper()
            has_error = bool(item.get("error_code"))
            if decision not in self.FAILURE_DECISIONS and not has_error:
                continue

            failures.append(
                {
                    "timestamp": item.get("timestamp"),
                    "skill": item.get("skill"),
                    "operation": item.get("operation"),
                    "decision": item.get("decision"),
                    "error_code": item.get("error_code"),
                    "reasoning": item.get("reasoning", ""),
                }
            )

        failures.sort(key=lambda row: row.get("timestamp") or "", reverse=True)
        return failures[:limit]

    def _active_skills(
        self,
        entries: list[dict[str, Any]],
        now: datetime,
        lookback_days: int,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Compute most frequently used skills in the given window."""

        cutoff = now - timedelta(days=lookback_days)
        counter: Counter[str] = Counter()

        for item in entries:
            timestamp = self._parse_timestamp(item.get("timestamp"))
            if timestamp is None or timestamp < cutoff:
                continue

            skill_name = item.get("skill")
            if isinstance(skill_name, str) and skill_name.strip():
                counter[skill_name] += 1

        return [
            {"skill": skill_name, "count": count}
            for skill_name, count in counter.most_common(limit)
        ]

    def _parse_timestamp(self, value: Any) -> datetime | None:
        """Parse ISO timestamps; return None on invalid values."""

        if not isinstance(value, str) or not value:
            return None

        candidate = value.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(candidate)
        except ValueError:
            return None

        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
