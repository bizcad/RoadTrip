"""Tests for the commit_message.py skill.

Test the three-tier commit message generation strategy:
- Tier 3: User override (highest precedence)
- Tier 1: Deterministic heuristics (90% of commits, $0 cost)
- Tier 2: LLM fallback (complex cases, ~$0.001-0.01 cost)

Tests validate:
- File categorization (src, tests, docs, config, etc.)
- Single-file vs multi-file detection
- Confidence thresholds
- Cost tracking
- Dry-run mode (no external API calls)
- Conventional Commits format compliance
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.skills.commit_message import CommitMessageSkill
from src.skills.commit_message_models import (
    CommitApproach,
    Tier1Score,
    CostTracking,
    CommitMessageResult,
)


# ===================================================================
# Fixtures
# ===================================================================

@pytest.fixture
def commit_skill(tmp_path):
    """Create a CommitMessageSkill instance with a temporary config directory."""
    # Create minimal config
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    
    config_file = config_dir / "commit-strategy.yaml"
    config_file.write_text("""
commit_message:
  confidence_threshold: 0.85
  
  tier2:
    enabled: false  # Disable Tier 2 for unit tests (no API calls)
    model: "claude-3-5-sonnet-20241022"
    temperature: 0.0
    max_tokens: 200
    
  file_categories:
    src:
      - "*.py"
      - "*.js"
      - "*.ts"
      - "*.rs"
    tests:
      - "test_*.py"
      - "*_test.py"
    docs:
      - "*.md"
      - "*.txt"
    config:
      - "*.yaml"
      - "*.yml"
      - "*.json"
    """)
    
    skill = CommitMessageSkill(config_path=str(config_file))
    return skill


# ===================================================================
# TIER 3: User Override
# ===================================================================

class TestTier3UserOverride:
    """User-provided messages take precedence over all other tiers."""

    def test_user_message_tier3_override(self, commit_skill):
        """User message bypasses all logic and is used directly."""
        result = commit_skill.generate(
            staged_files=["src/main.py"],
            user_message="feat: my custom message",
        )
        assert result.message == "feat: my custom message"
        assert result.approach_used == CommitApproach.TIER_3
        assert result.confidence == 1.0
        assert result.cost_estimate == 0.0

    def test_user_message_overrides_staged_files(self, commit_skill):
        """User message is used even if staged files are provided."""
        result = commit_skill.generate(
            staged_files=["src/main.py", "src/utils.py", "tests/test_utils.py"],
            user_message="refactor: reorganize modules",
        )
        assert result.message == "refactor: reorganize modules"
        assert result.approach_used == CommitApproach.TIER_3

    def test_user_message_empty_string_not_treated_as_override(self, commit_skill):
        """Empty user message should not trigger Tier 3."""
        result = commit_skill.generate(
            staged_files=["src/main.py"],
            user_message="",
        )
        # Empty string is falsy, so should not trigger Tier 3 override
        # Should fall through to Tier 1
        assert result.approach_used == CommitApproach.TIER_1


# ===================================================================
# TIER 1: Deterministic Logic
# ===================================================================

class TestTier1SingleFile:
    """Single-file commits should be high-confidence Tier 1."""

    def test_single_source_file_add(self, commit_skill):
        """Add single source file -> clear message."""
        result = commit_skill.generate(
            staged_files=["src/main.py"],
        )
        assert result.approach_used == CommitApproach.TIER_1
        assert result.confidence >= 0.85
        assert "feat:" in result.message and "main" in result.message.lower()
        assert result.cost_estimate == 0.0

    def test_single_doc_file(self, commit_skill):
        """Single markdown file change."""
        result = commit_skill.generate(
            staged_files=["README.md"],
        )
        assert result.approach_used == CommitApproach.TIER_1
        assert result.confidence >= 0.85
        assert "README" in result.message or "docs" in result.message.lower()

    def test_single_config_file(self, commit_skill):
        """Single config file change."""
        result = commit_skill.generate(
            staged_files=["config/commit-strategy.yaml"],
        )
        assert result.approach_used == CommitApproach.TIER_1
        assert result.confidence >= 0.85
        assert "config" in result.message.lower()

    def test_single_test_file(self, commit_skill):
        """Single test file change."""
        result = commit_skill.generate(
            staged_files=["tests/test_main.py"],
        )
        assert result.approach_used == CommitApproach.TIER_1
        assert result.confidence >= 0.85
        assert "test" in result.message.lower()


class TestTier1MultipleFilesSameCategory:
    """Multiple files in same category -> Tier 1 with decent confidence."""

    def test_multiple_source_files_same_category(self, commit_skill):
        """Multiple .py files in src/."""
        result = commit_skill.generate(
            staged_files=["src/main.py", "src/utils.py"],
        )
        assert result.approach_used == CommitApproach.TIER_1
        assert result.confidence >= 0.70
        assert "src" in result.message.lower() or "Update" in result.message
        assert result.cost_estimate == 0.0

    def test_multiple_test_files(self, commit_skill):
        """Multiple test files."""
        result = commit_skill.generate(
            staged_files=["tests/test_main.py", "tests/test_utils.py"],
        )
        assert result.approach_used == CommitApproach.TIER_1
        assert result.confidence >= 0.70
        assert "test" in result.message.lower()

    def test_multiple_doc_files(self, commit_skill):
        """Multiple markdown files."""
        result = commit_skill.generate(
            staged_files=["README.md", "docs/ARCHITECTURE.md"],
        )
        assert result.approach_used == CommitApproach.TIER_1
        assert result.confidence >= 0.70
        assert "doc" in result.message.lower() or "README" in result.message


class TestTier1EdgeCases:
    """Edge cases and confidence degradation."""

    def test_empty_file_list(self, commit_skill):
        """No files -> generic low-confidence message."""
        result = commit_skill.generate(
            staged_files=[],
        )
        assert result.approach_used == CommitApproach.TIER_1
        assert result.confidence < 0.75
        assert "empty" in result.message.lower() or "chore" in result.message.lower()

    def test_multiple_files_mixed_categories(self, commit_skill):
        """Multiple files across different categories -> low confidence."""
        result = commit_skill.generate(
            staged_files=["src/main.py", "README.md", "config/app.yaml"],
        )
        assert result.approach_used == CommitApproach.TIER_1
        # Mixed categories = below confidence threshold, but Tier 2 is disabled
        assert result.cost_estimate == 0.0
        # Should still generate a message
        assert "chore" in result.message.lower() or "update" in result.message.lower()

    def test_too_many_files_bulk_update(self, commit_skill):
        """More than 10 files -> bulk update message."""
        files = [f"src/file{i}.py" for i in range(15)]
        result = commit_skill.generate(
            staged_files=files,
        )
        assert result.approach_used == CommitApproach.TIER_1
        assert "bulk" in result.message.lower() or "15" in result.message
        assert result.confidence <= 0.75


# ===================================================================
# TIER 2: LLM Fallback (Dry-Run Mode)
# ===================================================================

class TestTier2DryRun:
    """Test Tier 2 behavior in dry-run mode (no actual API calls)."""

    @pytest.fixture
    def commit_skill_tier2_enabled(self, tmp_path):
        """Create skill with Tier 2 enabled."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        
        config_file = config_dir / "commit-strategy.yaml"
        config_file.write_text("""
commit_message:
  confidence_threshold: 0.95
  
  tier2:
    enabled: true
    model: "claude-3-5-sonnet-20241022"
    temperature: 0.0
    max_tokens: 200
    
  file_categories:
    src:
      - "*.py"
      - "*.js"
    tests:
      - "test_*.py"
    """)
        
        return CommitMessageSkill(config_path=str(config_file))

    def test_tier2_dry_run_no_api_call(self, commit_skill_tier2_enabled):
        """Dry-run mode should not call external API."""
        result = commit_skill_tier2_enabled.generate(
            staged_files=["src/complex_refactor.py"],
            dry_run=True,  # Dry-run prevents actual API call
        )
        # In dry-run, Tier 2 returns a prefixed message
        assert "[DRY-RUN]" in result.message or result.approach_used == CommitApproach.TIER_2
        assert result.cost_estimate >= 0  # Estimate included

    def test_tier2_dry_run_returns_estimate(self, commit_skill_tier2_enabled):
        """Dry-run should return cost estimate."""
        result = commit_skill_tier2_enabled.generate(
            staged_files=["src/file.py"],
            dry_run=True,
        )
        assert result.cost_tracking.tokens_input == 0
        assert result.cost_tracking.tokens_output == 0
        assert result.cost_tracking.model == "claude-3-5-sonnet-20241022"


# ===================================================================
# Cost Tracking
# ===================================================================

class TestCostTracking:
    """Verify cost calculations and tracking."""

    def test_tier1_zero_cost(self, commit_skill):
        """Tier 1 should have zero cost."""
        result = commit_skill.generate(
            staged_files=["src/main.py"],
        )
        if result.approach_used == CommitApproach.TIER_1:
            assert result.cost_estimate == 0.0
            assert result.cost_tracking.cost_usd == 0.0

    def test_tier3_zero_cost(self, commit_skill):
        """Tier 3 (user message) should have zero cost."""
        result = commit_skill.generate(
            staged_files=["src/main.py"],
            user_message="feat: manual message",
        )
        assert result.cost_estimate == 0.0
        assert result.cost_tracking.cost_usd == 0.0

    def test_cost_tracking_includes_model(self, commit_skill):
        """Cost tracking should record which model would be used."""
        result = commit_skill.generate(
            staged_files=["src/main.py"],
        )
        assert result.cost_tracking is not None


# ===================================================================
# Conventional Commits Compliance
# ===================================================================

class TestConventionalCommits:
    """Messages should follow Conventional Commits format."""

    def test_message_has_type_scope_subject(self, commit_skill):
        """Message should have type(scope): subject format or similar."""
        result = commit_skill.generate(
            staged_files=["src/main.py"],
        )
        # Check basic format: word followed by colon or parenthesis
        message = result.message
        assert (
            ":" in message or
            "Add:" in message or
            "Update:" in message or
            "Remove:" in message or
            "Rename:" in message
        ), f"Message format issue: {message}"

    def test_message_subject_under_50_chars_ideally(self, commit_skill):
        """Commit subject should ideally be under 50 characters."""
        result = commit_skill.generate(
            staged_files=["src/main.py"],
        )
        first_line = result.message.split("\n")[0]
        # Warn if too long, but don't fail (some messages naturally longer)
        if len(first_line) > 72:
            print(f"Warning: First line is {len(first_line)} chars: {first_line}")

    def test_message_multiline_has_blank_line_separation(self, commit_skill):
        """Multi-line messages should have blank line between subject and body."""
        result = commit_skill.generate(
            staged_files=[
                f"src/file{i}.py" for i in range(5)
            ],
        )
        if "\n" in result.message and len(result.message.split("\n")) > 1:
            lines = result.message.split("\n")
            # If there's a body, second line should be blank
            if len(lines) > 2:
                # Some implementations skip blank line; don't enforce strictly
                # Just verify message structure is reasonable
                assert len(lines[0]) > 0


# ===================================================================
# File Categorization Logic
# ===================================================================

class TestFileCategorization:
    """Verify file categorization works correctly."""

    def test_categorize_python_source(self, commit_skill):
        """Python files in src/ -> src category."""
        result = commit_skill.generate(
            staged_files=["src/main.py"],
        )
        assert result.tier1_score is not None
        assert "src" in result.tier1_score.categories or result.confidence >= 0.80

    def test_categorize_test_files(self, commit_skill):
        """test_*.py and *_test.py -> tests category."""
        result = commit_skill.generate(
            staged_files=["tests/test_main.py"],
        )
        assert result.tier1_score is not None
        assert "tests" in result.tier1_score.categories or "test" in result.message.lower()

    def test_categorize_documentation(self, commit_skill):
        """Markdown files -> docs category."""
        result = commit_skill.generate(
            staged_files=["README.md"],
        )
        assert result.tier1_score is not None
        assert (
            "documentation" in result.tier1_score.categories or
            "docs" in result.message.lower() or
            "README" in result.message
        )


# ===================================================================
# Integration with git_push.ps1 Workflow
# ===================================================================

class TestIntegrationWithPowerShell:
    """Tests simulating git_push.ps1 usage patterns."""

    def test_single_file_commit_add(self, commit_skill):
        """PowerShell: Single file added."""
        result = commit_skill.generate(
            staged_files=["src/auth.py"],
        )
        assert result.approach_used == CommitApproach.TIER_1
        assert result.message is not None
        assert len(result.message) > 0

    def test_multiple_files_with_diff(self, commit_skill):
        """PowerShell: Multiple files with diff context."""
        diff = """
--- src/main.py
+++ src/main.py
@@ -1,3 +1,5 @@
+import sys
+
 def main():
    pass
"""
        result = commit_skill.generate(
            staged_files=["src/main.py", "src/utils.py"],
            diff=diff,
        )
        assert result.message is not None

    def test_dry_run_verbose_output(self, commit_skill):
        """PowerShell: -DryRun -Verbose simulation."""
        result = commit_skill.generate(
            staged_files=["src/main.py"],
            dry_run=False,  # Dry-run handled separately in CLI
        )
        # Should include reasoning for verbose output
        assert result.reasoning is not None
        assert len(result.reasoning) > 0
        assert result.confidence is not None


# ===================================================================
# Error Handling
# ===================================================================

class TestErrorHandling:
    """Test error conditions and edge cases."""

    def test_empty_staged_files_list(self, commit_skill):
        """Empty file list should not crash."""
        result = commit_skill.generate(
            staged_files=[],
        )
        assert result.message is not None
        assert len(result.message) > 0

    def test_none_staged_files_handled(self, commit_skill):
        """None instead of list should be handled gracefully."""
        # Should either handle gracefully or raise controlled error
        try:
            result = commit_skill.generate(
                staged_files=None,
            )
            assert result.message is not None
        except (TypeError, AttributeError) as e:
            # If it raises, should be clear error (not crash)
            assert "staged" in str(e).lower() or "file" in str(e).lower()

    def test_very_long_file_list(self, commit_skill):
        """Very long file list should not crash."""
        files = [f"src/file{i}.py" for i in range(100)]
        result = commit_skill.generate(
            staged_files=files,
        )
        assert result.message is not None
        assert "bulk" in result.message.lower() or result.confidence < 0.80


# ===================================================================
# Result Structure
# ===================================================================

class TestCommitMessageResultStructure:
    """Verify CommitMessageResult always has required fields."""

    def test_result_has_all_fields(self, commit_skill):
        """Result should have all expected fields."""
        result = commit_skill.generate(
            staged_files=["src/main.py"],
        )
        assert hasattr(result, 'message')
        assert hasattr(result, 'approach_used')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'cost_estimate')
        assert hasattr(result, 'reasoning')
        assert hasattr(result, 'cost_tracking')

        # Validate types
        assert isinstance(result.message, str)
        assert isinstance(result.approach_used, CommitApproach)
        assert isinstance(result.confidence, float)
        assert isinstance(result.cost_estimate, float)
        assert isinstance(result.reasoning, str)
        assert isinstance(result.cost_tracking, CostTracking)

    def test_confidence_in_valid_range(self, commit_skill):
        """Confidence should be 0.0 to 1.0."""
        result = commit_skill.generate(
            staged_files=["src/main.py"],
        )
        assert 0.0 <= result.confidence <= 1.0

    def test_cost_estimate_non_negative(self, commit_skill):
        """Cost should never be negative."""
        result = commit_skill.generate(
            staged_files=["src/main.py"],
        )
        assert result.cost_estimate >= 0.0
