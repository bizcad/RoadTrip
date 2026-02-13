"""
orchestrator.py - Registry System Orchestrator

Coordinates all workstreams (WS0-4) and provides high-level API.
- Initializes all agents
- Handles skill registration flow
- Handles skill execution flow with verification
- Manages state and logging
"""

import logging
from typing import Dict, Any, List, Optional

from .registry_reader import RegistryReader
from .fingerprint_generator import FingerprintGenerator
from .fingerprint_verifier import FingerprintVerifier
from .registration import Registration
from .verification import Verification
from .registry_models import SkillMetadata, AgentStatus
from .storage_interface import StorageConfig, RegistryStore


class RegistryOrchestrator:
    """High-level orchestrator for registry system."""
    
    def __init__(
        self,
        registry_path: str = "config/skills-registry.yaml",
        use_mock: bool = True,
        storage_config: Optional[StorageConfig] = None
    ):
        """
        Initialize orchestrator with all workstreams.
        
        Args:
            registry_path: Path to skills registry (used if storage_config not provided)
            use_mock: Use mock fingerprints (True) or real (False)
            storage_config: Optional StorageConfig for pluggable backend
        """
        self.registry_path = registry_path
        self.use_mock = use_mock
        
        # Use provided storage config or default to YAML
        if storage_config is None:
            storage_config = StorageConfig(
                backend_type="yaml",
                location=registry_path
            )
        
        self.storage_config = storage_config
        
        # Initialize workstreams
        self.ws0_reader = RegistryReader(registry_path, use_mock)
        self.ws1_generator = FingerprintGenerator(use_mock, self.ws0_reader)
        self.ws2_verifier = FingerprintVerifier(self.ws1_generator, self.ws0_reader, use_mock)
        self.ws3_registration = Registration(self.ws1_generator, self.ws0_reader, use_mock)
        self.ws4_verification = Verification(self.ws2_verifier, use_mock)
        
        self.logger = logging.getLogger("Orchestrator")
        self.logger.info("✅ Registry orchestrator initialized")
    
    # ===== REGISTRATION FLOW =====
    
    def register_skill(
        self,
        skill_name: str,
        version: str,
        capabilities: List[str],
        author: str,
        test_count: int = 0,
        test_coverage: float = 0.0,
        description: str = "",
        entry_point: str = ""
    ) -> Dict[str, Any]:
        """
        Register a skill (WS3 flow).
        
        Args:
            skill_name: Skill name
            version: Version number
            capabilities: List of capabilities
            author: Author name
            test_count: Number of tests
            test_coverage: Test coverage percentage
            description: Skill description
            entry_point: Path to main .py file
            
        Returns:
            Result dict with registration status
        """
        self.logger.info(f"🔄 Registering skill: {skill_name}:{version}")
        
        try:
            result = self.ws3_registration.register_skill(
                skill_name=skill_name,
                version=version,
                capabilities=capabilities,
                author=author,
                test_count=test_count,
                test_coverage=test_coverage,
                description=description,
                entry_point=entry_point
            )
            
            self.logger.info(f"✅ Registration complete: {skill_name}")
            return {
                "status": "success",
                "skill_name": result.skill_name,
                "version": result.version,
                "fingerprint": result.fingerprint,
                "message": result.message
            }
        
        except Exception as e:
            self.logger.error(f"❌ Registration failed: {e}")
            return {
                "status": "error",
                "skill_name": skill_name,
                "error": str(e)
            }
    
    # ===== DISCOVERY FLOW (WS0) =====
    
    def query_capabilities(self, capability: str) -> List[SkillMetadata]:
        """
        Find skills with a given capability.
        
        Args:
            capability: Capability name to search for
            
        Returns:
            List of matching skills
        """
        self.logger.info(f"🔍 Querying capability: {capability}")
        return self.ws0_reader.handle_query(f"query_capabilities:{capability}")
    
    def find_all_skills(self) -> List[str]:
        """Get all registered skill names."""
        return self.ws0_reader.handle_query("get_all_skills")
    
    def get_skill_metadata(self, skill_name: str) -> Optional[SkillMetadata]:
        """Get metadata for a skill."""
        return self.ws0_reader.handle_query(f"get_skill:{skill_name}")
    
    # ===== EXECUTION FLOW (WS2 + WS4) =====
    
    def execute_skill(self, skill_name: str) -> Dict[str, Any]:
        """
        Execute skill with fingerprint verification (WS2 + WS4 flow).
        
        Args:
            skill_name: Skill to execute
            
        Returns:
            Result dict with execution status
        """
        self.logger.info(f"🚀 Executing skill: {skill_name}")
        
        try:
            # Step 1: Verify fingerprint (WS4 enforces via WS2)
            is_allowed, message = self.ws4_verification.enforce(skill_name)
            
            if not is_allowed:
                self.logger.error(f"❌ Execution blocked: {message}")
                return {
                    "status": "blocked",
                    "skill_name": skill_name,
                    "reason": message
                }
            
            # Step 2: Execute (in real system, would call actual skill)
            self.logger.info(f"✅ Execution allowed: {skill_name}")
            return {
                "status": "allowed",
                "skill_name": skill_name,
                "message": f"Skill {skill_name} verified and ready to execute"
            }
        
        except Exception as e:
            self.logger.error(f"❌ Execution error: {e}")
            return {
                "status": "error",
                "skill_name": skill_name,
                "error": str(e)
            }
    
    # ===== SYSTEM STATUS =====
    
    def get_system_status(self) -> Dict[str, AgentStatus]:
        """Get status of all workstreams."""
        return {
            "WS0": self.ws0_reader.get_status(),
            "WS1": self.ws1_generator.get_status(),
            "WS2": self.ws2_verifier.get_status(),
            "WS3": self.ws3_registration.get_status(),
            "WS4": self.ws4_verification.get_status()
        }
    
    def switch_mode(self, use_mock: bool):
        """
        Switch between mock and real fingerprints.
        
        Used for mock → real transition.
        """
        self.logger.info(f"🔄 Switching to {'MOCK' if use_mock else 'REAL'} mode")
        self.use_mock = use_mock
        self.ws1_generator.switch_mode(use_mock)
        self.ws2_verifier.use_mock = use_mock
        self.ws3_registration.use_mock = use_mock
        self.ws4_verification.use_mock = use_mock
