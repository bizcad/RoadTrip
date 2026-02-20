from pathlib import Path

from src.skills.memory_store_transition import execute


def _write_manifest(root: Path) -> None:
    (root / "manifest.yaml").write_text(
        """
schema_version: "1.0"
stores:
  - id: prospective
    promotion_targets: [working]
    expiration_targets: [episodic]
  - id: working
    promotion_targets: [episodic]
    expiration_targets: [episodic]
  - id: episodic
    promotion_targets: [semantic]
    expiration_targets: [long_term]
  - id: semantic
    promotion_targets: [long_term]
    expiration_targets: [long_term]
  - id: long_term
    promotion_targets: []
    expiration_targets: []
""".strip()
        + "\n",
        encoding="utf-8",
    )


def test_transition_moves_entry_folder(tmp_path):
    memory_root = tmp_path / "data" / "memory"
    src = memory_root / "stores" / "prospective" / "entries" / "task-1"
    src.mkdir(parents=True, exist_ok=True)
    (src / "entry.yaml").write_text("id: task-1\n", encoding="utf-8")
    _write_manifest(memory_root)

    result = execute(
        {
            "repo_path": str(tmp_path),
            "memory_root": "data/memory",
            "entry_id": "task-1",
            "from_store": "prospective",
            "to_store": "working",
            "reason": "activated",
            "actor": "test",
        }
    )

    assert result["success"] is True
    assert (memory_root / "stores" / "prospective" / "entries" / "task-1").exists() is False
    assert (memory_root / "stores" / "working" / "entries" / "task-1").exists() is True


def test_transition_rejects_not_allowed_path(tmp_path):
    memory_root = tmp_path / "data" / "memory"
    src = memory_root / "stores" / "prospective" / "entries" / "task-2"
    src.mkdir(parents=True, exist_ok=True)
    _write_manifest(memory_root)

    result = execute(
        {
            "repo_path": str(tmp_path),
            "memory_root": "data/memory",
            "entry_id": "task-2",
            "from_store": "prospective",
            "to_store": "long_term",
            "reason": "invalid jump",
        }
    )

    assert result["success"] is False
    assert result["error_code"] == "TRANSITION_NOT_ALLOWED"
    assert (memory_root / "stores" / "prospective" / "entries" / "task-2").exists() is True


def test_transition_dry_run_does_not_move(tmp_path):
    memory_root = tmp_path / "data" / "memory"
    src = memory_root / "stores" / "prospective" / "entries" / "task-3"
    src.mkdir(parents=True, exist_ok=True)
    _write_manifest(memory_root)

    result = execute(
        {
            "repo_path": str(tmp_path),
            "memory_root": "data/memory",
            "entry_id": "task-3",
            "from_store": "prospective",
            "to_store": "working",
            "dry_run": True,
        }
    )

    assert result["success"] is True
    assert result["moved"] is False
    assert (memory_root / "stores" / "prospective" / "entries" / "task-3").exists() is True
    assert (memory_root / "stores" / "working" / "entries" / "task-3").exists() is False
