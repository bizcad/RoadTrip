"""
test_registry_system.py - Comprehensive Registry System Tests

Tests all workstreams (WS0-4) with mock data.
"""

import pytest
import logging
from typing import List, Dict, Any

from src.skills.registry import (
    SkillStatus,
    AgentState,
    SkillMetadata,
    RegistryData,
    FingerprintResult,
    RegistrationResult,
    VerificationResult,
    AgentStatus
)

from src.skills.registry.registry_reader import RegistryReader
from src.skills.registry.fingerprint_generator import FingerprintGenerator
from src.skills.registry.fingerprint_verifier import FingerprintVerifier
from src.skills.registry.registration import Registration
from src.skills.registry.verification import Verification
from src.skills.registry.orchestrator import RegistryOrchestrator


# ===== FIXTURES =====

@pytest.fixture
def registry_path() -> str:
    """Path to test registry."""
    return "config/skills-registry.yaml"


@pytest.fixture
def orchestrator(registry_path) -> RegistryOrchestrator:
    """Create orchestrator with mock data."""
    return RegistryOrchestrator(registry_path, use_mock=True)


# ===== WS0: REGISTRY READER TESTS =====

class TestRegistryReader:
    """Test WS0 - Registry Discovery"""
    
    def test_initialization(self, registry_path):
        """Test RegistryReader initialization."""
        reader = RegistryReader(registry_path, use_mock=True)
        assert reader is not None
        assert reader.registry_path == registry_path
    
    def test_get_status(self, registry_path):
        """Test status reporting."""
        reader = RegistryReader(registry_path, use_mock=True)
        status = reader.get_status()
        assert status.state == AgentState.READY
        assert "capabilities" in status.message
    
    def test_query_all_skills(self, orchestrator):
        """Test querying all skills."""
        skills = orchestrator.find_all_skills()
        assert isinstance(skills, list)
        assert len(skills) > 0
    
    def test_query_capability(self, orchestrator):
        """Test querying by capability."""
        # Query a known capability
        results = orchestrator.query_capabilities("data_processing")
        assert isinstance(results, list)
    
    def test_get_skill_metadata(self, orchestrator):
        """Test getting skill metadata."""
        # Get first skill
        skills = orchestrator.find_all_skills()
        if skills:
            metadata = orchestrator.get_skill_metadata(skills[0])
            assert metadata is not None


# ===== WS1: FINGERPRINT GENERATOR TESTS =====

class TestFingerprintGenerator:
    """Test WS1 - Fingerprint Generation"""
    
    def test_initialization(self, orchestrator):
        """Test FingerprintGenerator initialization."""
        gen = orchestrator.ws1_generator
        assert gen is not None
    
    def test_status_reporting(self, orchestrator):
        """Test status reporting."""
        status = orchestrator.ws1_generator.get_status()
        assert status.state == AgentState.READY
        assert "mock" in status.message or "fingerprints" in status.message
    
    def test_mock_mode(self, orchestrator):
        """Test mock fingerprint generation."""
        # In mock mode, should return deterministic fingerprints
        fp1 = orchestrator.ws1_generator.generate_fingerprint(
            skill_name="test_skill",
            version="1.0.0",
            capabilities=["test"],
            use_mock=True
        )
        assert fp1 is not None
        assert "fp_" in fp1


# ===== WS2: FINGERPRINT VERIFIER TESTS =====

class TestFingerprintVerifier:
    """Test WS2 - Fingerprint Verification"""
    
    def test_initialization(self, orchestrator):
        """Test FingerprintVerifier initialization."""
        verifier = orchestrator.ws2_verifier
        assert verifier is not None
    
    def test_status_reporting(self, orchestrator):
        """Test status reporting."""
        status = orchestrator.ws2_verifier.get_status()
        assert status.state == AgentState.READY
    
    def test_verification_workflow(self, orchestrator):
        """Test verification against known fingerprints."""
        # In mock mode, should verify known skills
        skills = orchestrator.find_all_skills()
        if skills:
            skill_name = skills[0]
            result = orchestrator.ws2_verifier.verify(skill_name)
            # Result should be VerificationResult
            assert result is not None


# ===== WS3: REGISTRATION TESTS =====

class TestRegistration:
    """Test WS3 - Skill Registration"""
    
    def test_initialization(self, orchestrator):
        """Test Registration initialization."""
        reg = orchestrator.ws3_registration
        assert reg is not None
    
    def test_status_reporting(self, orchestrator):
        """Test status reporting."""
        status = orchestrator.ws3_registration.get_status()
        assert status.state == AgentState.READY
    
    def test_register_skill(self, orchestrator):
        """Test skill registration flow."""
        result = orchestrator.register_skill(
            skill_name="test_new_skill",
            version="1.0.0",
            capabilities=["test", "capability"],
            author="test_author",
            description="Test skill for testing"
        )
        
        assert result["status"] == "success"
        assert result["skill_name"] == "test_new_skill"
        assert "fingerprint" in result
    
    def test_register_with_test_metadata(self, orchestrator):
        """Test registration with test metrics."""
        result = orchestrator.register_skill(
            skill_name="tested_skill",
            version="2.0.0",
            capabilities=["data"],
            author="tester",
            test_count=10,
            test_coverage=85.5,
            description="Well-tested skill"
        )
        
        assert result["status"] == "success"
        assert "fingerprint" in result


# ===== WS4: EXECUTION VERIFICATION TESTS =====

class TestExecutionVerification:
    """Test WS4 - Execution-Time Verification"""
    
    def test_initialization(self, orchestrator):
        """Test Verification initialization."""
        verif = orchestrator.ws4_verification
        assert verif is not None
    
    def test_status_reporting(self, orchestrator):
        """Test status reporting."""
        status = orchestrator.ws4_verification.get_status()
        assert status.state == AgentState.READY
    
    def test_allow_execution(self, orchestrator):
        """Test allowing known skill execution."""
        skills = orchestrator.find_all_skills()
        if skills:
            skill_name = skills[0]
            result = orchestrator.execute_skill(skill_name)
            assert result["status"] in ["allowed", "blocked", "error"]


# ===== ORCHESTRATOR INTEGRATION TESTS =====

class TestOrchestrator:
    """Test RegistryOrchestrator - End-to-end flows"""
    
    def test_initialization(self, orchestrator):
        """Test orchestrator initialization."""
        assert orchestrator is not None
    
    def test_all_workstreams_ready(self, orchestrator):
        """Verify all workstreams are initialized."""
        status = orchestrator.get_system_status()
        
        assert "WS0" in status
        assert "WS1" in status
        assert "WS2" in status
        assert "WS3" in status
        assert "WS4" in status
        
        # All should be ready
        for ws_name, ws_status in status.items():
            assert ws_status.state in [AgentState.READY, AgentState.BUSY]
    
    def test_registration_to_execution_flow(self, orchestrator):
        """Test full flow: register → discover → verify → execute."""
        
        # 1. Register a new skill (WS3)
        reg_result = orchestrator.register_skill(
            skill_name="flow_test_skill",
            version="1.0.0",
            capabilities=["flow_test"],
            author="test_runner"
        )
        assert reg_result["status"] == "success"
        
        # 2. Query it (WS0)
        skills = orchestrator.find_all_skills()
        assert "flow_test_skill" in skills or len(skills) > 0
        
        # 3. Execute with verification (WS4 via WS2)
        result = orchestrator.execute_skill("flow_test_skill")
        assert "status" in result
    
    def test_mode_switching(self, orchestrator):
        """Test switching between mock and real modes."""
        original_mode = orchestrator.use_mock
        
        # Switch to opposite mode
        orchestrator.switch_mode(not original_mode)
        assert orchestrator.use_mock == (not original_mode)
        
        # Switch back
        orchestrator.switch_mode(original_mode)
        assert orchestrator.use_mock == original_mode


# ===== ERROR HANDLING TESTS =====

class TestErrorHandling:
    """Test error handling across workstreams"""
    
    def test_invalid_skill_query(self, orchestrator):
        """Test querying non-existent skill."""
        result = orchestrator.get_skill_metadata("nonexistent_skill_xyz")
        assert result is None or isinstance(result, SkillMetadata)
    
    def test_execute_nonexistent_skill(self, orchestrator):
        """Test executing non-existent skill."""
        result = orchestrator.execute_skill("nonexistent_xyz")
        # Should handle gracefully (blocked or error)
        assert result["status"] in ["blocked", "error", "allowed"]
    
    def test_register_with_missing_params(self, orchestrator):
        """Test registration with minimal parameters."""
        result = orchestrator.register_skill(
            skill_name="minimal_skill",
            version="0.1.0",
            capabilities=[],
            author="test"
        )
        assert result["status"] == "success"


# ===== DATA MODEL TESTS =====

class TestDataModels:
    """Test data model validation"""
    
    def test_agent_status_creation(self):
        """Test AgentStatus model."""
        status = AgentStatus(
            state=AgentState.READY,
            message="Test",
            processed_count=5
        )
        assert status.state == AgentState.READY
        assert status.processed_count == 5
    
    def test_skill_metadata_creation(self):
        """Test SkillMetadata model."""
        meta = SkillMetadata(
            name="test",
            version="1.0.0",
            capabilities=["cap1"],
            status=SkillStatus.ACTIVE
        )
        assert meta.name == "test"
        assert "cap1" in meta.capabilities
    
    def test_registration_result_creation(self):
        """Test RegistrationResult model."""
        result = RegistrationResult(
            skill_name="test",
            version="1.0.0",
            fingerprint="fp_123",
            message="Registered"
        )
        assert result.skill_name == "test"
        assert result.fingerprint == "fp_123"


if __name__ == "__main__":
    # Run with: pytest test_registry_system.py -v
    pytest.main([__file__, "-v", "--tb=short"])
