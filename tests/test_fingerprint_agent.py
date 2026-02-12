"""
Tests for Fingerprint Agent (Phase 2a, Task A1).

Test structure:
- TestFingerprintCrypto: Hash generation and determinism
- TestFingerprintSigning: RSA signature generation (stub for A1b)
- TestFingerprintIntegration: End-to-end fingerprinting of Phase 1b skills
- TestFingerprintEvents: Event emission (SkillFingerprintedEvent, etc.)
"""

import pytest
from pathlib import Path
from datetime import datetime, timezone
import tempfile
import json

from src.agents.fingerprint_agent import FingerprintAgent
from src.agents.fingerprint_models import (
    FingerprintInput,
    FingerprintStatus,
    SkillFingerprint,
)


@pytest.fixture
def agent():
    """Create a FingerprintAgent instance."""
    return FingerprintAgent()


@pytest.fixture
def temp_workspace(tmp_path):
    """Create a minimal temporary workspace for testing."""
    workspace = tmp_path / "roadtrip_test"
    workspace.mkdir()
    
    (workspace / "src" / "skills").mkdir(parents=True)
    (workspace / "tests").mkdir()
    (workspace / "data").mkdir()
    
    return workspace


@pytest.fixture
def agent_with_temp_workspace(temp_workspace):
    """Create agent with temporary workspace."""
    return FingerprintAgent(workspace_root=str(temp_workspace))


# --- Task A1a: Crypto Attestation ---

class TestFingerprintCrypto:
    """Test cryptographic hash generation (Task A1a)."""
    
    def test_hash_content_deterministic(self, agent):
        """Same content → same hash (determinism property)."""
        content = "def validate(x): return x > 0"
        hash1 = agent._hash_content(content)
        hash2 = agent._hash_content(content)
        
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex digest
    
    def test_hash_different_content(self, agent):
        """Different content → different hash."""
        hash1 = agent._hash_content("code1")
        hash2 = agent._hash_content("code2")
        
        assert hash1 != hash2
    
    def test_fingerprint_idempotent(self, agent_with_temp_workspace, temp_workspace):
        """Fingerprinting same skill twice → same hashes."""
        # Create test skill file
        skill_file = temp_workspace / "src" / "skills" / "test_skill.py"
        skill_file.write_text("def test(): pass")
        
        # Create test file
        test_file = temp_workspace / "tests" / "test_test_skill.py"
        test_file.write_text("def test_basic(): pass")
        
        agent = agent_with_temp_workspace
        
        # Fingerprint twice
        input1 = FingerprintInput(
            skill_name="test_skill",
            skill_version="1.0",
            skill_path=str(skill_file),
            test_path=str(test_file),
            sign=False,
        )
        result1 = agent.fingerprint(input1)
        
        input2 = FingerprintInput(
            skill_name="test_skill",
            skill_version="1.0",
            skill_path=str(skill_file),
            test_path=str(test_file),
            sign=False,
        )
        result2 = agent.fingerprint(input2)
        
        # Should have same hashes
        assert result1.fingerprint.code_hash == result2.fingerprint.code_hash
        assert result1.fingerprint.capabilities_hash == result2.fingerprint.capabilities_hash
        assert result1.fingerprint.test_metadata_hash == result2.fingerprint.test_metadata_hash


# --- Task A1b: Self-Signed Authority ---

class TestFingerprintSigning:
    """Test RSA signing (Task A1b) — stub phase."""
    
    def test_fingerprint_signing_placeholder(self, agent_with_temp_workspace, temp_workspace):
        """Test fingerprint signing (placeholder for A1b)."""
        # Create files
        skill_file = temp_workspace / "src" / "skills" / "auth_test.py"
        skill_file.write_text("def validate(): pass")
        
        test_file = temp_workspace / "tests" / "test_auth_test.py"
        test_file.write_text("def test_basic(): pass")
        
        agent = agent_with_temp_workspace
        
        input = FingerprintInput(
            skill_name="auth_test",
            skill_version="1.0",
            skill_path=str(skill_file),
            test_path=str(test_file),
            sign=True,  # Request signing
        )
        
        result = agent.fingerprint(input)
        
        # Should succeed
        assert result.status == FingerprintStatus.SUCCESS
        assert result.fingerprint is not None
        assert result.fingerprint.signed == True
        assert result.fingerprint.signature is not None


# --- Task A1c: Integration Tests ---

class TestFingerprintIntegration:
    """End-to-end fingerprinting tests (Task A1c)."""
    
    def test_fingerprint_missing_skill(self, agent):
        """Fingerprint fails if skill file missing."""
        input = FingerprintInput(
            skill_name="nonexistent",
            skill_version="1.0",
            skill_path="src/skills/nonexistent.py",
        )
        
        result = agent.fingerprint(input)
        
        assert result.status == FingerprintStatus.INVALID_SKILL
        assert result.error is not None
    
    def test_fingerprint_missing_tests(self, agent_with_temp_workspace, temp_workspace):
        """Fingerprint fails if test file missing."""
        # Create skill but no test
        skill_file = temp_workspace / "src" / "skills" / "lonely.py"
        skill_file.write_text("def lonely(): pass")
        
        agent = agent_with_temp_workspace
        
        input = FingerprintInput(
            skill_name="lonely",
            skill_version="1.0",
            skill_path=str(skill_file),
            # No test_path specified, will auto-resolve and fail
        )
        
        result = agent.fingerprint(input)
        
        assert result.status == FingerprintStatus.NO_TESTS
        assert result.error is not None


# --- Event Infrastructure ---

class TestFingerprintEvents:
    """Test event emission (Phase 2a)."""
    
    def test_events_file_created(self, agent_with_temp_workspace, temp_workspace):
        """Events written to data/skill-events.jsonl."""
        # Create files
        skill_file = temp_workspace / "src" / "skills" / "eventtest.py"
        skill_file.write_text("def eventtest(): pass")
        
        test_file = temp_workspace / "tests" / "test_eventtest.py"
        test_file.write_text("def test_x(): pass")
        
        agent = agent_with_temp_workspace
        
        input = FingerprintInput(
            skill_name="eventtest",
            skill_version="1.0",
            skill_path=str(skill_file),
            test_path=str(test_file),
        )
        
        result = agent.fingerprint(input)
        
        # Check events file exists
        events_file = temp_workspace / "data" / "skill-events.jsonl"
        assert events_file.exists()
        
        # Should have at least 2 events (fingerprinted + test_passed)
        lines = events_file.read_text().strip().split('\n')
        assert len(lines) >= 2
        
        # Parse events
        events = [json.loads(line) for line in lines if line]
        event_types = [e["event_type"] for e in events]
        
        assert "skill_fingerprinted" in event_types
        assert "skill_test_passed" in event_types


# --- Phase 1b Skills Integration ---

class TestFingerprintPhase1bSkills:
    """Test fingerprinting actual Phase 1b skills (if they exist)."""
    
    @pytest.mark.skipif(
        not Path("src/skills/auth_validator.py").exists(),
        reason="Phase 1b skills not found"
    )
    def test_fingerprint_auth_validator(self, agent):
        """Fingerprint auth_validator skill."""
        input = FingerprintInput(
            skill_name="auth_validator",
            skill_version="1.0",
            skill_path="src/skills/auth_validator.py",
            test_path="tests/test_auth_validator.py",
        )
        
        result = agent.fingerprint(input)
        
        assert result.status == FingerprintStatus.SUCCESS
        assert result.fingerprint is not None
        assert result.fingerprint.skill_name == "auth_validator"
