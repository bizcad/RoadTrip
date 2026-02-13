"""
fingerprint_generator.py (WS1) - Fingerprint Computation

Computes deterministic fingerprints for skills.
- Use MOCK mode: SHA256(skill_name:version) for initial development
- Use REAL mode: SHA256(source files + tests + version) for production
- Both modes produce identical results if files don't change
"""

import hashlib
from typing import Optional
from pathlib import Path

from .base_agent import BaseAgent
from .registry_models import FingerprintResult, AgentState


class FingerprintGenerator(BaseAgent):
    """WS1: Fingerprint Generator - Compute skill fingerprints."""
    
    def __init__(self, use_mock: bool = True, registry_reader: Optional[BaseAgent] = None):
        """
        Initialize fingerprint generator.
        
        Args:
            use_mock: If True, use deterministic mock hashes; if False, hash actual files
            registry_reader: Reference to WS0 for consistency checks
        """
        super().__init__("WS1", use_mock)
        self.registry_reader = registry_reader
        self.mock_cache = {}  # Cache of computed mock hashes
    
    def handle_query(self, query: str) -> FingerprintResult:
        """
        Handle fingerprint requests from other agents.
        
        Query format: "compute:{skill_name}:{version}"
        Response: FingerprintResult with fingerprint value
        """
        self.transition_state(AgentState.COMPUTING, f"Computing: {query}")
        
        try:
            if not query.startswith("compute:"):
                raise ValueError(f"Invalid query format: {query}")
            
            parts = query.replace("compute:", "").split(":")
            if len(parts) != 2:
                raise ValueError(f"Expected format 'compute:skill_name:version'")
            
            skill_name, version = parts
            fingerprint = self.compute_fingerprint(skill_name, version)
            
            result = FingerprintResult(
                skill_name=skill_name,
                version=version,
                fingerprint=fingerprint,
                is_mock=self.use_mock
            )
            
            self.transition_state(AgentState.VERIFIED, f"Computed: {fingerprint}")
            return result
        
        except Exception as e:
            self.error = str(e)
            self.transition_state(AgentState.ERROR, f"Computation failed: {e}")
            raise
    
    def compute_fingerprint(self, skill_name: str, version: str) -> str:
        """
        Compute fingerprint for a skill.
        
        Mock: SHA256(skill_name:version) - deterministic, fast
        Real: SHA256(source + tests + version) - production-ready
        """
        if self.use_mock:
            return self._compute_mock_fingerprint(skill_name, version)
        else:
            return self._compute_real_fingerprint(skill_name, version)
    
    def _compute_mock_fingerprint(self, skill_name: str, version: str) -> str:
        """
        Compute mock fingerprint (deterministic, no files needed).
        
        Used during development/testing. Same input always → same output.
        """
        key = f"{skill_name}:{version}"
        
        # Check cache
        if key in self.mock_cache:
            self.logger.debug(f"Cache hit: {key}")
            return self.mock_cache[key]
        
        # Compute
        hash_input = key.encode()
        fingerprint = hashlib.sha256(hash_input).hexdigest()[:16]
        
        # Cache
        self.mock_cache[key] = fingerprint
        self.logger.info(f"Mock fingerprint computed: {skill_name}:{version} → {fingerprint}")
        
        return fingerprint
    
    def _compute_real_fingerprint(self, skill_name: str, version: str) -> str:
        """
        Compute real fingerprint by hashing actual skill files.
        
        Hashes:
        - src/skills/{skill_name}.py (main)
        - src/skills/{skill_name}_models.py (if exists)
        - tests/test_{skill_name}.py (tests)
        - "version:{version}" (version marker)
        """
        source_file = Path(f"src/skills/{skill_name}.py")
        models_file = Path(f"src/skills/{skill_name}_models.py")
        test_file = Path(f"tests/test_{skill_name}.py")
        
        # Validate files exist
        if not source_file.exists():
            raise FileNotFoundError(f"Skill source not found: {source_file}")
        if not test_file.exists():
            raise FileNotFoundError(f"Skill tests not found: {test_file}")
        
        # Read files
        hash_input = ""
        hash_input += source_file.read_text()
        
        if models_file.exists():
            hash_input += models_file.read_text()
        
        hash_input += test_file.read_text()
        hash_input += f"version:{version}"
        
        # Compute hash
        fingerprint = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        self.logger.info(f"Real fingerprint computed: {skill_name}:{version} → {fingerprint}")
        
        return fingerprint
    
    def switch_mode(self, use_mock: bool):
        """
        Switch between mock and real modes.
        
        Used during release: Start with mock, transition to real.
        """
        self.use_mock = use_mock
        mode = "MOCK" if use_mock else "REAL"
        self.logger.info(f"Switched to {mode} mode")
