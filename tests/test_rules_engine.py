"""Tests for the rules-engine skill.

Test cases drawn from config/safety-rules.yaml built-in test cases,
plus additional edge cases for allowed paths and conservative defaults.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.skills.models import SafetyRulesConfig
from src.skills.rules_engine import evaluate


# ===================================================================
# Test cases from config/safety-rules.yaml
# ===================================================================

class TestConfigTestCases:
    """Tests matching the 6 built-in test cases in safety-rules.yaml."""

    def test_allow_normal_source_files(self, sample_config, tmp_repo):
        """Test case 1: src/main.rs, lib/utils.js -> APPROVE."""
        result = evaluate(
            files=["src/main.rs", "lib/utils.js"],
            repo_root=str(tmp_repo),
            config=sample_config,
        )
        assert result.decision == "APPROVE"
        assert "src/main.rs" in result.approved_files
        assert len(result.blocked_files) == 0

    def test_block_env_file(self, sample_config, tmp_repo):
        """Test case 2: .env -> BLOCK."""
        result = evaluate(
            files=[".env"],
            repo_root=str(tmp_repo),
            config=sample_config,
        )
        assert result.decision == "BLOCK_ALL"
        assert len(result.blocked_files) == 1
        assert result.blocked_files[0].path == ".env"

    def test_block_credentials_directory(self, sample_config, tmp_repo):
        """Test case 3: credentials/api.key -> BLOCK (pattern match)."""
        result = evaluate(
            files=["credentials/api.key"],
            repo_root=str(tmp_repo),
            config=sample_config,
        )
        assert result.decision == "BLOCK_ALL"
        assert len(result.blocked_files) == 1
        assert result.blocked_files[0].reason == "pattern_match"

    def test_block_build_artifacts(self, sample_config, tmp_repo):
        """Test case 4: dist/bundle.js -> BLOCK."""
        result = evaluate(
            files=["dist/bundle.js"],
            repo_root=str(tmp_repo),
            config=sample_config,
        )
        assert result.decision == "BLOCK_ALL"
        assert result.blocked_files[0].reason == "pattern_match"
        assert "dist" in result.blocked_files[0].matched_rule

    def test_warn_large_files_but_allow(self, sample_config, tmp_repo):
        """Test case 5: Large file (>50MB) -> APPROVE with warning."""
        # Create a file that reports as >50MB via its actual size
        large_file = tmp_repo / "video.mp4"
        # Write a small file and mock the size check via a real file
        # For a true size test we'd need 50MB+; instead test the path
        # with a normal file and verify no block occurs.
        large_file.write_bytes(b"x" * 100)

        result = evaluate(
            files=["video.mp4"],
            repo_root=str(tmp_repo),
            config=sample_config,
        )
        # File is small so no size warning, but it should still APPROVE
        # (not blocked by any pattern)
        assert result.decision == "APPROVE"

    def test_warn_truly_large_file(self, sample_config, tmp_repo):
        """Verify size warning triggers for files exceeding the limit."""
        # Use a config with a tiny size limit to trigger the warning
        tiny_limit_config = SafetyRulesConfig(
            blocked_files=sample_config.blocked_files,
            blocked_patterns=sample_config.blocked_patterns,
            max_file_size_mb=0,  # 0 MB limit -> everything triggers
        )
        small_file = tmp_repo / "video.mp4"
        small_file.write_bytes(b"x" * 1024)

        result = evaluate(
            files=["video.mp4"],
            repo_root=str(tmp_repo),
            config=tiny_limit_config,
        )
        assert result.decision == "APPROVE"
        assert len(result.warnings) == 1
        assert "video.mp4" in result.warnings[0]

    def test_allow_gitignore(self, sample_config, tmp_repo):
        """Test case 6: .gitignore -> APPROVE (allowed file)."""
        result = evaluate(
            files=[".gitignore"],
            repo_root=str(tmp_repo),
            config=sample_config,
        )
        assert result.decision == "APPROVE"
        assert ".gitignore" in result.approved_files


# ===================================================================
# Additional edge cases
# ===================================================================

class TestEdgeCases:

    def test_empty_file_list(self, sample_config, tmp_repo):
        """Empty file list -> APPROVE."""
        result = evaluate(
            files=[],
            repo_root=str(tmp_repo),
            config=sample_config,
        )
        assert result.decision == "APPROVE"
        assert result.confidence == 0.99
        assert len(result.approved_files) == 0

    def test_mixed_safe_and_unsafe_files_block_all(self, sample_config, tmp_repo):
        """Mixed safe + unsafe -> BLOCK_ALL (all-or-nothing)."""
        result = evaluate(
            files=["src/main.py", ".env", "docs/readme.md"],
            repo_root=str(tmp_repo),
            config=sample_config,
        )
        assert result.decision == "BLOCK_ALL"
        assert "src/main.py" in result.approved_files
        assert "docs/readme.md" in result.approved_files
        assert len(result.blocked_files) == 1
        assert result.blocked_files[0].path == ".env"

    def test_conservative_config_blocks_non_allowed(self, conservative_config, tmp_repo):
        """Conservative default config blocks files not in allowed paths."""
        result = evaluate(
            files=["random_file.txt"],
            repo_root=str(tmp_repo),
            config=conservative_config,
        )
        assert result.decision == "BLOCK_ALL"

    def test_conservative_config_allows_src(self, conservative_config, tmp_repo):
        """Conservative config still allows files in allowed prefixes."""
        result = evaluate(
            files=["src/app.py"],
            repo_root=str(tmp_repo),
            config=conservative_config,
        )
        assert result.decision == "APPROVE"

    def test_permissive_config_allows_everything(self, permissive_config, tmp_repo):
        """Config with no blocked patterns approves all files."""
        result = evaluate(
            files=["anything.txt", "whatever/file.xyz"],
            repo_root=str(tmp_repo),
            config=permissive_config,
        )
        assert result.decision == "APPROVE"
        assert len(result.blocked_files) == 0

    def test_blocked_confidence_is_1(self, sample_config, tmp_repo):
        """Blocked results have confidence 1.0 (certain)."""
        result = evaluate(
            files=[".env"],
            repo_root=str(tmp_repo),
            config=sample_config,
        )
        assert result.confidence == 1.0

    def test_approved_confidence_is_099(self, sample_config, tmp_repo):
        """Clean approved results have confidence 0.99."""
        result = evaluate(
            files=["src/main.py"],
            repo_root=str(tmp_repo),
            config=sample_config,
        )
        assert result.confidence == 0.99

    def test_node_modules_blocked(self, sample_config, tmp_repo):
        """node_modules/ files are blocked by pattern."""
        result = evaluate(
            files=["node_modules/express/index.js"],
            repo_root=str(tmp_repo),
            config=sample_config,
        )
        assert result.decision == "BLOCK_ALL"
        assert result.blocked_files[0].reason == "pattern_match"

    def test_key_file_blocked(self, sample_config, tmp_repo):
        """*.key files are blocked by pattern."""
        result = evaluate(
            files=["private.key"],
            repo_root=str(tmp_repo),
            config=sample_config,
        )
        assert result.decision == "BLOCK_ALL"

    def test_pem_file_blocked(self, sample_config, tmp_repo):
        """*.pem files are blocked by pattern."""
        result = evaluate(
            files=["cert.pem"],
            repo_root=str(tmp_repo),
            config=sample_config,
        )
        assert result.decision == "BLOCK_ALL"

    def test_secrets_directory_blocked(self, sample_config, tmp_repo):
        """secrets/ directory files are blocked by pattern."""
        result = evaluate(
            files=["secrets/db.yaml"],
            repo_root=str(tmp_repo),
            config=sample_config,
        )
        assert result.decision == "BLOCK_ALL"

    def test_allowed_file_readme(self, sample_config, tmp_repo):
        """README.md is in the allowed files list."""
        result = evaluate(
            files=["README.md"],
            repo_root=str(tmp_repo),
            config=sample_config,
        )
        assert result.decision == "APPROVE"

    def test_allowed_file_claude_md(self, sample_config, tmp_repo):
        """CLAUDE.md is in the allowed files list."""
        result = evaluate(
            files=["CLAUDE.md"],
            repo_root=str(tmp_repo),
            config=sample_config,
        )
        assert result.decision == "APPROVE"

    def test_deleted_file_no_size_warning(self, sample_config, tmp_repo):
        """Deleted files (not on disk) don't trigger size warnings."""
        # Don't create the file on disk
        result = evaluate(
            files=["deleted_file.txt"],
            repo_root=str(tmp_repo),
            config=sample_config,
        )
        # File isn't in allowed paths or blocklist, and pattern ^\.
        # won't match "deleted_file.txt", so it should approve
        assert result.decision == "APPROVE"
        assert len(result.warnings) == 0

    def test_gitattributes_allowed(self, sample_config, tmp_repo):
        """.gitattributes is in the allowed files list."""
        result = evaluate(
            files=[".gitattributes"],
            repo_root=str(tmp_repo),
            config=sample_config,
        )
        assert result.decision == "APPROVE"

    def test_pyproject_toml_allowed(self, sample_config, tmp_repo):
        """pyproject.toml is in the allowed files list."""
        result = evaluate(
            files=["pyproject.toml"],
            repo_root=str(tmp_repo),
            config=sample_config,
        )
        assert result.decision == "APPROVE"


# ===================================================================
# Config loader integration test
# ===================================================================

class TestConfigLoaderIntegration:

    def test_load_real_config(self, tmp_repo):
        """Load safety-rules.yaml from a temp directory."""
        import yaml

        config_dir = tmp_repo / "config"
        config_dir.mkdir()
        config_file = config_dir / "safety-rules.yaml"
        config_file.write_text(yaml.dump({
            "blocked_files": [".env"],
            "blocked_patterns": [r"^secrets/.*"],
            "max_file_size_mb": 25,
        }))

        from src.skills.config_loader import load_safety_rules
        config = load_safety_rules(config_dir)

        assert ".env" in config.blocked_files
        assert r"^secrets/.*" in config.blocked_patterns
        assert config.max_file_size_mb == 25

    def test_missing_config_returns_conservative(self, tmp_repo):
        """Missing config file returns conservative defaults."""
        from src.skills.config_loader import load_safety_rules

        config_dir = tmp_repo / "config"
        config_dir.mkdir()
        config = load_safety_rules(config_dir)

        # Conservative: pattern ".*" blocks everything
        assert ".*" in config.blocked_patterns
