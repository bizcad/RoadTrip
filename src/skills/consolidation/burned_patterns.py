"""Burned-pattern registry with cooldown to prevent rollback oscillation."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path


@dataclass
class BurnedPattern:
    pattern_signature: str
    consolidation_id: str
    reason: str
    burned_at: str
    cooldown_until: str


class BurnedPatternRegistry:
    """Persistent cooldown registry for rolled-back patterns."""

    def __init__(self, registry_file: str = "logs/burned_patterns.json") -> None:
        self.registry_file = Path(registry_file)
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)

    def add(
        self,
        pattern_signature: str,
        consolidation_id: str,
        reason: str,
        cooldown_days: int = 90,
    ) -> BurnedPattern:
        now = datetime.now(timezone.utc)
        entry = BurnedPattern(
            pattern_signature=pattern_signature,
            consolidation_id=consolidation_id,
            reason=reason,
            burned_at=now.isoformat(),
            cooldown_until=(now + timedelta(days=cooldown_days)).isoformat(),
        )
        data = self._load()
        data.append(asdict(entry))
        self._save(data)
        return entry

    def is_blocked(self, pattern_signature: str) -> bool:
        now = datetime.now(timezone.utc)
        for row in self._load():
            if row.get("pattern_signature") != pattern_signature:
                continue
            cooldown_until = self._parse_iso(row.get("cooldown_until"))
            if cooldown_until and now < cooldown_until:
                return True
        return False

    def expire(self) -> int:
        now = datetime.now(timezone.utc)
        rows = self._load()
        kept: list[dict] = []
        for row in rows:
            cooldown_until = self._parse_iso(row.get("cooldown_until"))
            if cooldown_until and cooldown_until > now:
                kept.append(row)
        removed = len(rows) - len(kept)
        self._save(kept)
        return removed

    def _load(self) -> list[dict]:
        if not self.registry_file.exists():
            return []
        try:
            payload = json.loads(self.registry_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
        if isinstance(payload, list):
            return payload
        return []

    def _save(self, rows: list[dict]) -> None:
        self.registry_file.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    def _parse_iso(self, value: str | None) -> datetime | None:
        if not value:
            return None
        candidate = value.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(candidate)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
