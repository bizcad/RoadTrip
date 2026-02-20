"""Skill: transition memory entry folders between store types using manifest rules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import shutil

import yaml


@dataclass
class MemoryTransitionRequest:
    """Request to move one memory entry folder from one store to another."""

    entry_id: str
    from_store: str
    to_store: str
    reason: str = ""
    actor: str = "system"
    repo_path: str = "."
    memory_root: str = "data/memory"
    dry_run: bool = False


class MemoryStoreTransitionSkill:
    """Validates transition rules from manifest and moves entry folders."""

    def transition(self, request: MemoryTransitionRequest) -> dict[str, Any]:
        root = (Path(request.repo_path).resolve() / request.memory_root).resolve()
        manifest_path = root / "manifest.yaml"

        if not manifest_path.exists():
            return {
                "success": False,
                "decision": "REJECT",
                "error_code": "MANIFEST_NOT_FOUND",
                "error": f"Memory manifest missing at {manifest_path}",
            }

        manifest = self._load_manifest(manifest_path)
        store_map = {
            str(item.get("id", "")): item
            for item in manifest.get("stores", [])
            if isinstance(item, dict)
        }

        from_meta = store_map.get(request.from_store)
        to_meta = store_map.get(request.to_store)
        if from_meta is None or to_meta is None:
            return {
                "success": False,
                "decision": "REJECT",
                "error_code": "INVALID_STORE",
                "error": "from_store or to_store not defined in manifest",
            }

        allowed_transitions = [str(value) for value in from_meta.get("allowed_transitions", [])]
        if allowed_transitions:
            allowed = set(allowed_transitions)
        else:
            allowed_targets = [str(value) for value in from_meta.get("promotion_targets", [])]
            expiration_targets = [str(value) for value in from_meta.get("expiration_targets", [])]
            allowed = set(allowed_targets + expiration_targets)

        if request.to_store not in allowed:
            return {
                "success": False,
                "decision": "REJECT",
                "error_code": "TRANSITION_NOT_ALLOWED",
                "error": f"Transition {request.from_store} -> {request.to_store} is not allowed by manifest",
            }

        src = root / "stores" / request.from_store / "entries" / request.entry_id
        dst_parent = root / "stores" / request.to_store / "entries"
        dst = dst_parent / request.entry_id

        if not src.exists():
            return {
                "success": False,
                "decision": "REJECT",
                "error_code": "ENTRY_NOT_FOUND",
                "error": f"Entry folder not found: {src}",
            }

        if dst.exists():
            return {
                "success": False,
                "decision": "REJECT",
                "error_code": "ENTRY_ALREADY_EXISTS",
                "error": f"Destination already exists: {dst}",
            }

        transition_record = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "entry_id": request.entry_id,
            "from_store": request.from_store,
            "to_store": request.to_store,
            "reason": request.reason,
            "actor": request.actor,
            "dry_run": request.dry_run,
        }

        if not request.dry_run:
            dst_parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            self._append_transition_log(root / "transitions.jsonl", transition_record)

        return {
            "success": True,
            "decision": "APPROVE",
            "entry_id": request.entry_id,
            "from_store": request.from_store,
            "to_store": request.to_store,
            "moved": not request.dry_run,
            "dry_run": request.dry_run,
        }

    def _load_manifest(self, manifest_path: Path) -> dict[str, Any]:
        with open(manifest_path, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        if not isinstance(data, dict):
            return {}
        return data

    def _append_transition_log(self, log_path: Path, record: dict[str, Any]) -> None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")


def execute(input_data: dict[str, Any]) -> dict[str, Any]:
    """Skill entry point for adaptive executor/orchestrator."""
    request = MemoryTransitionRequest(
        entry_id=str(input_data.get("entry_id", "")).strip(),
        from_store=str(input_data.get("from_store", "")).strip(),
        to_store=str(input_data.get("to_store", "")).strip(),
        reason=str(input_data.get("reason", "")).strip(),
        actor=str(input_data.get("actor", "system")).strip() or "system",
        repo_path=str(input_data.get("repo_path", ".")),
        memory_root=str(input_data.get("memory_root", "data/memory")),
        dry_run=bool(input_data.get("dry_run", False)),
    )

    if not request.entry_id or not request.from_store or not request.to_store:
        return {
            "success": False,
            "decision": "REJECT",
            "error_code": "INVALID_INPUT",
            "error": "entry_id, from_store, and to_store are required",
        }

    skill = MemoryStoreTransitionSkill()
    return skill.transition(request)
