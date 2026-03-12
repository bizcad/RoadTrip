"""Skill: capture raw 'sensations' (ideas/problems) into Prospective Memory."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


@dataclass
class SensationRequest:
    """Request to capture a new sensation into prospective memory."""

    title: str
    description: str
    provenance: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    repo_path: str = "."
    memory_root: str = "data/memory"
    actor: str = "system"


class SensationCaptureSkill:
    """Creates a structured sensation folder in the prospective store."""

    def capture(self, request: SensationRequest) -> dict[str, Any]:
        root = (Path(request.repo_path).resolve() / request.memory_root).resolve()
        store_path = root / "stores" / "prospective" / "entries"

        if not store_path.parent.exists():
            return {
                "success": False,
                "error": f"Prospective store not found at {store_path.parent}",
            }

        # Slugify title for directory name
        entry_id = re.sub(r"[^a-z0-9]+", "-", request.title.lower()).strip("-")
        entry_dir = store_path / entry_id

        if entry_dir.exists():
            # If it exists, we might want to append or version it. 
            # For now, let's just add a timestamp suffix to avoid collisions.
            entry_id = f"{entry_id}-{datetime.now().strftime('%H%M%S')}"
            entry_dir = store_path / entry_id

        entry_dir.mkdir(parents=True, exist_ok=True)

        # 1. Create sensation.md
        sensation_md = f"# Sensation: {request.title}\n\n"
        sensation_md += f"**Timestamp**: {datetime.now(timezone.utc).isoformat()}\n"
        sensation_md += f"**Actor**: {request.actor}\n"
        sensation_md += f"**Tags**: {', '.join(request.tags)}\n\n"
        sensation_md += "## Description\n"
        sensation_md += f"{request.description}\n\n"
        sensation_md += "## Initial Research Plan (Retrieve)\n"
        sensation_md += "- [ ] Search episodic logs for similar sensations.\n"
        sensation_md += "- [ ] Query NotebookLM for evidence/policy.\n"
        sensation_md += "- [ ] Cross-reference with Registry for existing skills.\n"

        (entry_dir / "sensation.md").write_text(sensation_md, encoding="utf-8")

        # 2. Create provenance_links.md
        provenance_md = "# Provenance Links\n\n"
        for link in request.provenance:
            provenance_md += f"- {link}\n"
        
        (entry_dir / "provenance_links.md").write_text(provenance_md, encoding="utf-8")

        # 3. Create metadata.yaml for tracking
        metadata = {
            "entry_id": entry_id,
            "title": request.title,
            "status": "raw_sensation",
            "salience_score": 0.5,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tags": request.tags,
            "promotion_criteria": {
                "evidence_required": 2,
                "evidence_found": 0,
                "review_required": True
            }
        }
        
        with open(entry_dir / "metadata.yaml", "w", encoding="utf-8") as f:
            yaml.safe_dump(metadata, f)

        return {
            "success": True,
            "entry_id": entry_id,
            "path": str(entry_dir.relative_to(Path(request.repo_path).resolve())),
            "message": f"Sensation '{request.title}' captured successfully."
        }


def execute(input_data: dict[str, Any]) -> dict[str, Any]:
    """Skill entry point."""
    request = SensationRequest(
        title=str(input_data.get("title", "Untitled Sensation")),
        description=str(input_data.get("description", "")),
        provenance=input_data.get("provenance", []),
        tags=input_data.get("tags", []),
        repo_path=str(input_data.get("repo_path", ".")),
        memory_root=str(input_data.get("memory_root", "data/memory")),
        actor=str(input_data.get("actor", "system"))
    )

    if not request.description:
        return {"success": False, "error": "Description is required for a sensation."}

    skill = SensationCaptureSkill()
    return skill.capture(request)
