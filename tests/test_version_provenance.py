"""Tests for version provenance verification and manifest hashing."""

from __future__ import annotations

from pathlib import Path

from src.skills.registry.version_provenance import VersionProvenanceVerifier


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_verify_skill_directory_with_matching_versions(tmp_path: Path) -> None:
    skill_dir = tmp_path / "git-push-autonomous"

    _write(
        skill_dir / "SKILL.md",
        """---
name: git-push-autonomous
version: specs-v1.0
---

# Skill
""",
    )

    _write(
        skill_dir / "CLAUDE.md",
        """# Logic
**Specs Version**: v1.0
""",
    )

    verifier = VersionProvenanceVerifier()
    result = verifier.verify_skill_directory(str(skill_dir))

    assert result.valid is True
    assert result.skill_version == "specs-v1.0"
    assert result.claude_version == "v1.0"
    assert result.normalized_skill_version == "1.0"
    assert result.normalized_claude_version == "1.0"
    assert result.manifest_hash is not None
    assert len(result.manifest_inputs) == 2


def test_verify_skill_directory_fails_on_mismatch(tmp_path: Path) -> None:
    skill_dir = tmp_path / "commit-message"

    _write(
        skill_dir / "SKILL.md",
        """---
name: commit-message
version: specs-v1.1
---

# Skill
""",
    )

    _write(
        skill_dir / "CLAUDE.md",
        """# Logic
**Specs Version**: v2.0
""",
    )

    verifier = VersionProvenanceVerifier()
    result = verifier.verify_skill_directory(str(skill_dir))

    assert result.valid is False
    assert any("Version mismatch" in err for err in result.errors)


def test_verify_skill_directory_fails_when_skill_version_missing(tmp_path: Path) -> None:
    skill_dir = tmp_path / "rules-engine"

    _write(skill_dir / "SKILL.md", "# Missing front matter\n")

    verifier = VersionProvenanceVerifier()
    result = verifier.verify_skill_directory(str(skill_dir))

    assert result.valid is False
    assert "SKILL.md missing front matter version" in result.errors


def test_manifest_hash_is_deterministic_and_sorted() -> None:
    verifier = VersionProvenanceVerifier()

    a = [
        "skills/git-push-autonomous/CLAUDE.md",
        "skills/git-push-autonomous/SKILL.md",
    ]
    b = list(reversed(a))

    hash_a = verifier.compute_manifest_hash(a)
    hash_b = verifier.compute_manifest_hash(b)

    assert hash_a == hash_b


def test_verify_real_repo_skill_directory() -> None:
    verifier = VersionProvenanceVerifier()
    result = verifier.verify_skill_directory("skills/git-push-autonomous")

    assert result.valid is True
    assert result.skill_version is not None
    assert result.manifest_hash is not None
