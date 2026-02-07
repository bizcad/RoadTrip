"""Rules Engine Skill - File safety validation.

Evaluates files against pre-configured safety rules (blocklists, regex
patterns, size limits) and returns a structured decision.

Design principle: Conservative defaults. If in doubt, block.

Spec: skills/rules-engine/SKILL.md, skills/rules-engine/CLAUDE.md
Config: config/safety-rules.yaml
"""

from __future__ import annotations

import os
import re
from pathlib import Path, PurePosixPath

from src.skills.config_loader import load_safety_rules
from src.skills.models import BlockedFile, RulesResult, SafetyRulesConfig

# Paths that are always considered safe (from skills/git-push-autonomous/safety-rules.md).
# Files under these prefixes skip blocklist/pattern checks and only get size-checked.
ALLOWED_PREFIXES = (
    "src/",
    "docs/",
    "tests/",
    "config/",
    "scripts/",
    "infra/",
    "data/",
    "PromptTracking/",
    "skills/",
)

# Individual files that are always allowed, even if they match blocked patterns.
ALLOWED_FILES = {
    ".gitignore",
    ".gitattributes",
    "README.md",
    "LICENSE",
    "CLAUDE.md",
    "Cargo.toml",
    "Cargo.lock",
    "package.json",
    "package-lock.json",
    "requirements.txt",
    "pyproject.toml",
    "go.mod",
    "go.sum",
}


def _normalize_path(file_path: str) -> str:
    """Normalize a file path to forward-slash POSIX style for consistent matching."""
    return PurePosixPath(file_path.replace("\\", "/")).as_posix()


def _is_allowed(file_path: str) -> bool:
    """Check if a file is in the allowed list (safe by convention)."""
    normalized = _normalize_path(file_path)

    if normalized in ALLOWED_FILES:
        return True

    for prefix in ALLOWED_PREFIXES:
        if normalized.startswith(prefix):
            return True

    return False


def _check_explicit_blocklist(
    file_path: str, blocked_files: list[str],
) -> BlockedFile | None:
    """Check if a file matches the explicit blocklist."""
    normalized = _normalize_path(file_path)
    basename = PurePosixPath(normalized).name

    for blocked in blocked_files:
        # Match against full path or just the filename
        if normalized == blocked or basename == blocked:
            return BlockedFile(
                path=file_path,
                reason="explicit_blocklist",
                matched_rule=blocked,
            )

        # Match against path segments (e.g., ".vscode/settings.json")
        if normalized.endswith("/" + blocked) or normalized == blocked:
            return BlockedFile(
                path=file_path,
                reason="explicit_blocklist",
                matched_rule=blocked,
            )

    return None


def _check_patterns(
    file_path: str, blocked_patterns: list[str],
) -> BlockedFile | None:
    """Check if a file matches any blocked regex pattern."""
    normalized = _normalize_path(file_path)

    for pattern in blocked_patterns:
        try:
            if re.search(pattern, normalized):
                return BlockedFile(
                    path=file_path,
                    reason="pattern_match",
                    matched_rule=pattern,
                )
        except re.error:
            # Invalid pattern - skip it rather than crash
            continue

    return None


def _check_file_size(
    file_path: str, repo_root: str, max_size_mb: int,
) -> str | None:
    """Check if a file exceeds the size limit. Returns a warning string or None."""
    full_path = Path(repo_root) / file_path

    if not full_path.exists():
        # File might be deleted (git status D) - skip size check
        return None

    try:
        size_mb = full_path.stat().st_size / (1024 * 1024)
        if size_mb > max_size_mb:
            return f"{file_path}: {size_mb:.1f}MB exceeds {max_size_mb}MB limit"
    except OSError:
        return None

    return None


def evaluate(
    files: list[str],
    repo_root: str,
    config: SafetyRulesConfig | None = None,
) -> RulesResult:
    """Evaluate a list of files against safety rules.

    Args:
        files: List of file paths (relative to repo root) to evaluate.
        repo_root: Absolute path to the git repository root.
        config: Safety rules config. If None, loads from config/safety-rules.yaml.

    Returns:
        RulesResult with decision, approved/blocked files, confidence, and warnings.
    """
    if config is None:
        config_dir = Path(repo_root) / "config"
        config = load_safety_rules(config_dir)

    if not files:
        return RulesResult(
            decision="APPROVE",
            approved_files=[],
            blocked_files=[],
            confidence=0.99,
            warnings=[],
        )

    approved: list[str] = []
    blocked: list[BlockedFile] = []
    warnings: list[str] = []

    for file_path in files:
        # Step 1: Check allowed paths first (takes precedence over blocks)
        if _is_allowed(file_path):
            # Still check file size even for allowed files
            size_warning = _check_file_size(
                file_path, repo_root, config.max_file_size_mb,
            )
            if size_warning:
                warnings.append(size_warning)
            approved.append(file_path)
            continue

        # Step 2: Check explicit blocklist
        block_result = _check_explicit_blocklist(file_path, config.blocked_files)
        if block_result:
            blocked.append(block_result)
            continue

        # Step 3: Check regex patterns
        pattern_result = _check_patterns(file_path, config.blocked_patterns)
        if pattern_result:
            blocked.append(pattern_result)
            continue

        # Step 4: Check file size (warning only, not a block)
        size_warning = _check_file_size(
            file_path, repo_root, config.max_file_size_mb,
        )
        if size_warning:
            warnings.append(size_warning)

        approved.append(file_path)

    # Aggregate decision: any blocked = BLOCK_ALL (all-or-nothing)
    if blocked:
        return RulesResult(
            decision="BLOCK_ALL",
            approved_files=approved,
            blocked_files=blocked,
            confidence=1.0,
            warnings=warnings,
        )

    if warnings:
        return RulesResult(
            decision="APPROVE",
            approved_files=approved,
            blocked_files=[],
            confidence=0.95,
            warnings=warnings,
        )

    return RulesResult(
        decision="APPROVE",
        approved_files=approved,
        blocked_files=[],
        confidence=0.99,
        warnings=[],
    )
