"""Skill: list registered skills from config/skills-registry.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def execute(input_data: dict[str, Any]) -> dict[str, Any]:
    """Return a sorted list of registered skills and basic metadata counts."""

    repo_path = str(input_data.get("repo_path", "."))
    registry_path = str(input_data.get("registry_path", "config/skills-registry.yaml"))

    path = Path(repo_path).resolve() / registry_path
    if not path.exists():
        return {
            "success": False,
            "decision": "REJECT",
            "error_code": "REGISTRY_NOT_FOUND",
            "error": f"Registry not found: {path}",
        }

    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    skills_map = payload.get("skills") or {}
    if not isinstance(skills_map, dict):
        skills_map = {}

    skills = sorted(str(name) for name in skills_map.keys())
    meta = payload.get("metadata") or {}

    return {
        "success": True,
        "decision": "APPROVE",
        "registry_path": registry_path,
        "skills": skills,
        "total_skills": len(skills),
        "metadata": {
            "registry_version": meta.get("registry_version"),
            "last_scanned": meta.get("last_scanned"),
        },
    }
