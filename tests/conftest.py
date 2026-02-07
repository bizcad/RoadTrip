"""Shared fixtures for the RoadTrip skills test suite."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from src.skills.models import SafetyRulesConfig


@pytest.fixture
def sample_config() -> SafetyRulesConfig:
    """A realistic safety rules config matching config/safety-rules.yaml."""
    return SafetyRulesConfig(
        blocked_files=[
            ".env",
            ".env.local",
            ".secrets",
            "credentials.json",
            "aws-credentials",
            ".private_key",
            ".vscode/settings.json",
            ".idea",
            ".DS_Store",
            "Thumbs.db",
        ],
        blocked_patterns=[
            r"^\.",
            r"^credentials/.*",
            r"^secrets/.*",
            r".*\.key$",
            r".*\.pem$",
            r".*\.pkcs12$",
            r".*\.p12$",
            r"tmp.*\.log$",
            r".*\.tmp$",
            r"^node_modules/.*",
            r"^dist/.*",
            r"^build/.*",
            r"^venv/.*",
            r"^__pycache__/.*",
            r".*\.db$",
            r".*\.sqlite$",
            r".*\.sqlite3$",
        ],
        max_file_size_mb=50,
        allow_override=False,
    )


@pytest.fixture
def tmp_repo(tmp_path: Path) -> Path:
    """Create a temporary directory acting as a repo root."""
    return tmp_path


@pytest.fixture
def conservative_config() -> SafetyRulesConfig:
    """Conservative default config that blocks everything."""
    return SafetyRulesConfig(
        blocked_files=[],
        blocked_patterns=[".*"],
        max_file_size_mb=0,
        allow_override=False,
    )


@pytest.fixture
def permissive_config() -> SafetyRulesConfig:
    """Config with no blocked patterns (allows everything)."""
    return SafetyRulesConfig(
        blocked_files=[],
        blocked_patterns=[],
        max_file_size_mb=50,
        allow_override=False,
    )
