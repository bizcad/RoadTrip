"""Version provenance verification for trusted skill artifacts.

Deterministically validates version metadata consistency between SKILL.md,
CLAUDE.md, and fingerprint/provenance input manifests.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class VersionProvenanceResult:
    """Outcome of version provenance verification."""

    skill_path: str
    valid: bool
    skill_version: str | None = None
    claude_version: str | None = None
    normalized_skill_version: str | None = None
    normalized_claude_version: str | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    manifest_hash: str | None = None
    manifest_inputs: list[str] = field(default_factory=list)


class VersionProvenanceVerifier:
    """Verifies version metadata and builds a deterministic manifest hash."""

    FRONT_MATTER_REGEX = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    SPECS_VERSION_REGEX = re.compile(r"^\*\*Specs Version\*\*:\s*(.+?)\s*$", re.MULTILINE)

    def verify_skill_directory(self, skill_dir: str) -> VersionProvenanceResult:
        """Validate version provenance for one skill directory."""

        base = Path(skill_dir)
        skill_md = base / "SKILL.md"
        claude_md = base / "CLAUDE.md"

        result = VersionProvenanceResult(skill_path=str(base), valid=True)

        if not skill_md.exists():
            result.valid = False
            result.errors.append("Missing SKILL.md")
            return result

        skill_version = self._extract_skill_version(skill_md)
        if not skill_version:
            result.valid = False
            result.errors.append("SKILL.md missing front matter version")
            return result

        result.skill_version = skill_version
        result.normalized_skill_version = self._normalize_version(skill_version)

        if claude_md.exists():
            claude_version, source = self._extract_claude_version(claude_md)
            if claude_version:
                result.claude_version = claude_version
                result.normalized_claude_version = self._normalize_version(claude_version)
                if result.normalized_skill_version != result.normalized_claude_version:
                    result.valid = False
                    result.errors.append(
                        f"Version mismatch SKILL({skill_version}) vs CLAUDE({claude_version})"
                    )
                if source != "front_matter":
                    result.warnings.append(
                        "CLAUDE.md version sourced from 'Specs Version' line; front matter version recommended"
                    )
            else:
                result.warnings.append("CLAUDE.md missing version metadata")
        else:
            result.warnings.append("CLAUDE.md missing (allowed, but traceability reduced)")

        manifest = self.build_manifest_inputs(skill_md=skill_md, claude_md=claude_md if claude_md.exists() else None)
        result.manifest_inputs = manifest
        result.manifest_hash = self.compute_manifest_hash(manifest)

        return result

    def build_manifest_inputs(self, skill_md: Path, claude_md: Path | None = None) -> list[str]:
        """Build deterministic fingerprint input list."""

        inputs = [str(skill_md.as_posix())]
        if claude_md is not None:
            inputs.append(str(claude_md.as_posix()))
        return sorted(inputs)

    def compute_manifest_hash(self, manifest_inputs: list[str]) -> str:
        """Compute deterministic hash for provenance input list."""

        payload = "\n".join(sorted(manifest_inputs))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

    def _extract_skill_version(self, skill_md: Path) -> str | None:
        """Read version from SKILL.md YAML front matter."""

        text = skill_md.read_text(encoding="utf-8")
        front_matter = self._extract_front_matter(text)
        if not isinstance(front_matter, dict):
            return None
        value = front_matter.get("version")
        if isinstance(value, str) and value.strip():
            return value.strip()
        return None

    def _extract_claude_version(self, claude_md: Path) -> tuple[str | None, str | None]:
        """Read CLAUDE version from front matter or Specs Version heading."""

        text = claude_md.read_text(encoding="utf-8")

        front_matter = self._extract_front_matter(text)
        if isinstance(front_matter, dict):
            value = front_matter.get("version")
            if isinstance(value, str) and value.strip():
                return value.strip(), "front_matter"

        match = self.SPECS_VERSION_REGEX.search(text)
        if match:
            return match.group(1).strip(), "specs_heading"

        return None, None

    def _extract_front_matter(self, markdown_text: str) -> dict[str, Any] | None:
        match = self.FRONT_MATTER_REGEX.match(markdown_text)
        if not match:
            return None
        try:
            payload = yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            return None
        if isinstance(payload, dict):
            return payload
        return None

    def _normalize_version(self, value: str) -> str:
        """Normalize version tokens to compare semantically equivalent labels."""

        normalized = value.strip().lower()
        normalized = normalized.replace("specs-", "")
        normalized = normalized.lstrip("v")
        return normalized
