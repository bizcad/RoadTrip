"""
skill_scanner.py - SKILL.md Metadata Scanner

Reads all SKILL.md files in the skills/ directory, parses their metadata
frontmatter, and builds AgentSkill-compatible dicts for discovery announcements.

Key design decisions:
- Fingerprint is SHA-256 of SKILL.md content WITH the fingerprint line excluded
  (avoids self-referential hash instability)
- Returns structured dicts matching rockbot's AgentSkill schema
  {id, name, description, tags, examples}
- Emits warnings for missing/stale fingerprints; does not block on mismatch
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


@dataclass
class ScannedSkill:
    """Parsed skill from SKILL.md frontmatter."""
    name: str
    description: str
    version: str
    tags: list[str]
    examples: list[str]
    entry_point: str
    runtime: str
    trust_level: str
    fingerprint_stored: str
    fingerprint_actual: str
    fingerprint_ok: bool
    skill_dir: str

    def to_agent_skill(self) -> dict[str, Any]:
        """Return dict matching rockbot AgentSkill schema."""
        return {
            "id": self.name,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "examples": self.examples,
        }


@dataclass
class ScanResult:
    skills: list[ScannedSkill] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_FINGERPRINT_LINE_RE = re.compile(r"^\s*fingerprint:.*$", re.MULTILINE)


def _compute_fingerprint(raw_bytes: bytes) -> str:
    """SHA-256 of SKILL.md content with fingerprint line excluded."""
    text = raw_bytes.decode("utf-8", errors="replace")
    stripped = _FINGERPRINT_LINE_RE.sub("", text)
    return hashlib.sha256(stripped.encode("utf-8")).hexdigest()[:16]


def _parse_frontmatter(raw_bytes: bytes) -> dict[str, Any] | None:
    """Extract YAML frontmatter from SKILL.md bytes."""
    text = raw_bytes.decode("utf-8", errors="replace")
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return None
    fm_text = m.group(1)
    if _YAML_AVAILABLE:
        return yaml.safe_load(fm_text) or {}
    # Minimal fallback: key: value lines only
    result: dict[str, Any] = {}
    for line in fm_text.splitlines():
        if ":" in line and not line.strip().startswith("-"):
            k, _, v = line.partition(":")
            result[k.strip()] = v.strip()
    return result


def scan_skills(skills_root: str | Path = "skills") -> ScanResult:
    """
    Scan all SKILL.md files under skills_root.

    Args:
        skills_root: Path to the skills/ directory (default: "skills")

    Returns:
        ScanResult with parsed skills, errors, and warnings
    """
    root = Path(skills_root)
    result = ScanResult()

    if not root.exists():
        result.errors.append(f"skills_root not found: {root.resolve()}")
        return result

    for skill_md in sorted(root.glob("*/SKILL.md")):
        skill_dir = skill_md.parent.name
        try:
            raw = skill_md.read_bytes()
            fm = _parse_frontmatter(raw)

            if not fm:
                result.errors.append(f"{skill_dir}: no YAML frontmatter found")
                continue

            name = fm.get("name") or skill_dir
            description = fm.get("description", "")
            meta = fm.get("metadata", {}) or {}

            version = str(meta.get("version", "0.0.0"))
            tags = list(meta.get("tags", []))
            examples = list(meta.get("examples", []))
            entry_point = str(meta.get("entry_point", ""))
            runtime = str(meta.get("runtime", "unknown"))
            trust_level = str(meta.get("trust_level", "unknown"))
            fingerprint_stored = str(meta.get("fingerprint", ""))
            fingerprint_actual = _compute_fingerprint(raw)
            fingerprint_ok = fingerprint_stored == fingerprint_actual

            if not fingerprint_stored:
                result.warnings.append(f"{skill_dir}: no fingerprint stored")
            elif not fingerprint_ok:
                result.warnings.append(
                    f"{skill_dir}: fingerprint mismatch "
                    f"(stored={fingerprint_stored!r} actual={fingerprint_actual!r})"
                )

            if not examples:
                result.warnings.append(f"{skill_dir}: no examples — discovery will be lexical-only")

            skill = ScannedSkill(
                name=name,
                description=description,
                version=version,
                tags=tags,
                examples=examples,
                entry_point=entry_point,
                runtime=runtime,
                trust_level=trust_level,
                fingerprint_stored=fingerprint_stored,
                fingerprint_actual=fingerprint_actual,
                fingerprint_ok=fingerprint_ok,
                skill_dir=skill_dir,
            )
            result.skills.append(skill)

        except Exception as exc:
            result.errors.append(f"{skill_dir}: {exc}")

    return result


def stamp_fingerprints(skills_root: str | Path = "skills") -> dict[str, str]:
    """
    Recompute and write fingerprints for all SKILL.md files.

    Returns dict of {skill_dir: new_fingerprint}.
    Safe to call repeatedly — idempotent because fingerprint line is excluded.
    """
    root = Path(skills_root)
    updated: dict[str, str] = {}

    for skill_md in sorted(root.glob("*/SKILL.md")):
        skill_dir = skill_md.parent.name
        raw = skill_md.read_bytes()
        actual = _compute_fingerprint(raw)

        text = raw.decode("utf-8", errors="replace")
        if _FINGERPRINT_LINE_RE.search(text):
            new_text = _FINGERPRINT_LINE_RE.sub(
                f'  fingerprint: "{actual}"', text
            )
        else:
            # No fingerprint line — skip (not a metadata-enabled SKILL.md)
            continue

        skill_md.write_bytes(new_text.encode("utf-8"))
        updated[skill_dir] = actual

    return updated


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "stamp":
        updated = stamp_fingerprints()
        for skill_dir, fp in updated.items():
            print(f"  {skill_dir}: {fp}")
        print(f"Stamped {len(updated)} skills.")
        sys.exit(0)

    result = scan_skills()

    if result.errors:
        print("ERRORS:")
        for e in result.errors:
            print(f"  {e}")

    if result.warnings:
        print("WARNINGS:")
        for w in result.warnings:
            print(f"  {w}")

    print(f"\nSkills ({len(result.skills)}):")
    for s in result.skills:
        fp_status = "OK" if s.fingerprint_ok else "STALE"
        print(f"  [{fp_status}] {s.name} v{s.version} ({s.runtime}) — {len(s.examples)} examples")
