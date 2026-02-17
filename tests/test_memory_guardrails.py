"""Tests for WS-C guardrails: ceiling enforcement, irreversible checks, cooldown registry."""

from __future__ import annotations

from pathlib import Path

from src.skills.consolidation.burned_patterns import BurnedPatternRegistry
from src.skills.consolidation.guardrails import IrreversibleOperationGuard, MemoryCeilingError, MemoryGuardrails


def _write_lines(path: Path, count: int, auto_from: int = 0) -> None:
    rows = []
    for index in range(count):
        if index >= auto_from:
            rows.append(f"- [AUTO] rule {index}\n")
        else:
            rows.append(f"- manual rule {index}\n")
    path.write_text("".join(rows), encoding="utf-8")


def test_memory_guardrails_ok_when_under_soft_limit(tmp_path: Path) -> None:
    memory_file = tmp_path / "MEMORY.md"
    _write_lines(memory_file, 10)

    guard = MemoryGuardrails(soft_limit=20, hard_limit=30, prune_target=15)
    result = guard.evaluate(str(memory_file))

    assert result.state == "ok"
    assert result.line_count == 10


def test_memory_guardrails_prunes_auto_rules_at_soft_limit(tmp_path: Path) -> None:
    memory_file = tmp_path / "MEMORY.md"
    _write_lines(memory_file, count=12, auto_from=6)

    guard = MemoryGuardrails(soft_limit=8, hard_limit=20, prune_target=7)
    result = guard.enforce(str(memory_file))

    assert result.state == "ok"
    assert result.pruned_lines > 0
    assert result.line_count <= 8


def test_memory_guardrails_raises_when_hard_limit_cannot_be_remediated(tmp_path: Path) -> None:
    memory_file = tmp_path / "MEMORY.md"
    _write_lines(memory_file, count=15, auto_from=99)

    guard = MemoryGuardrails(soft_limit=8, hard_limit=10, prune_target=7)

    try:
        guard.enforce(str(memory_file))
        raised = False
    except MemoryCeilingError:
        raised = True

    assert raised is True


def test_irreversible_operation_guard_blocks_without_safeguards() -> None:
    guard = IrreversibleOperationGuard()

    result = guard.evaluate("git push --force origin main", preauthorized=False)

    assert result["decision"] == "BLOCK"
    assert result["allowed"] is False


def test_irreversible_operation_guard_escalates_when_preauthorized_with_safeguards() -> None:
    guard = IrreversibleOperationGuard()

    result = guard.evaluate(
        "Remove-Item logs/archive.txt",
        preauthorized=True,
        has_dry_run=True,
        rollback_available=False,
    )

    assert result["decision"] == "ESCALATE"
    assert result["allowed"] is True


def test_burned_pattern_registry_blocks_until_expired(tmp_path: Path) -> None:
    registry_file = tmp_path / "burned_patterns.json"
    registry = BurnedPatternRegistry(str(registry_file))

    registry.add(
        pattern_signature="git_push:lockfile_exists",
        consolidation_id="sleep_001",
        reason="rollback_after_bad_rule",
        cooldown_days=1,
    )

    assert registry.is_blocked("git_push:lockfile_exists") is True


def test_burned_pattern_registry_expire_removes_stale_entries(tmp_path: Path) -> None:
    registry_file = tmp_path / "burned_patterns.json"
    registry = BurnedPatternRegistry(str(registry_file))

    registry.add(
        pattern_signature="pattern:recent",
        consolidation_id="sleep_001",
        reason="test",
        cooldown_days=1,
    )

    # Insert an already-expired row directly for deterministic expiry test.
    registry_file.write_text(
        """[
  {
    \"pattern_signature\": \"pattern:expired\",
    \"consolidation_id\": \"sleep_000\",
    \"reason\": \"old\",
    \"burned_at\": \"2020-01-01T00:00:00+00:00\",
    \"cooldown_until\": \"2020-01-02T00:00:00+00:00\"
  },
  {
    \"pattern_signature\": \"pattern:recent\",
    \"consolidation_id\": \"sleep_001\",
    \"reason\": \"test\",
    \"burned_at\": \"2099-01-01T00:00:00+00:00\",
    \"cooldown_until\": \"2099-01-02T00:00:00+00:00\"
  }
]
""",
        encoding="utf-8",
    )

    removed = registry.expire()

    assert removed == 1
    assert registry.is_blocked("pattern:expired") is False
    assert registry.is_blocked("pattern:recent") is True
