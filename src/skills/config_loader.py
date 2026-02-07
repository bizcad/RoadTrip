"""Load and parse YAML configuration files for the skills framework.

Resolves paths relative to the git repository root. Falls back to
conservative defaults (block everything) when config files are missing.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

from src.skills.models import SafetyRulesConfig

# Conservative default: block everything when config is missing.
_DEFAULT_SAFETY_CONFIG = SafetyRulesConfig(
    blocked_files=[],
    blocked_patterns=[".*"],  # Match everything
    max_file_size_mb=0,
    allow_override=False,
)


def get_repo_root() -> Path:
    """Detect the git repository root directory."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    raise RuntimeError("Not inside a git repository or git is not installed.")


def load_safety_rules(config_dir: Path | None = None) -> SafetyRulesConfig:
    """Load safety rules from config/safety-rules.yaml.

    Args:
        config_dir: Path to the config directory. If None, auto-detects
                    from the git repo root.

    Returns:
        SafetyRulesConfig with parsed rules, or conservative defaults
        if the config file is missing.
    """
    if config_dir is None:
        config_dir = get_repo_root() / "config"

    config_path = config_dir / "safety-rules.yaml"

    if not config_path.exists():
        return SafetyRulesConfig(
            blocked_files=[],
            blocked_patterns=[".*"],
            max_file_size_mb=0,
            allow_override=False,
        )

    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        return _DEFAULT_SAFETY_CONFIG

    return SafetyRulesConfig(
        blocked_files=data.get("blocked_files", []),
        blocked_patterns=data.get("blocked_patterns", []),
        max_file_size_mb=data.get("max_file_size_mb", 50),
        allow_override=data.get("allow_override", False),
    )
