"""
fingerprint_verifier.py (WS2) - Runtime Fingerprint Verification

Verifies skill fingerprints at execution time.
- Computes current fingerprint (identical logic to WS1)
- Queries WS0 for expected fingerprint from registry
- Compares: match = allow, mismatch = reject
"""

from typing import Tuple, Optional

from .base_agent import BaseAgent
from .fingerprint_generator import FingerprintGenerator
from .registry_models import VerificationResult, AgentState


class FingerprintVerifier(BaseAgent):
    """WS2: Fingerprint Verifier - Verify skills at runtime."""
    
    def __init__(
        self,
        fingerprint_generator: FingerprintGenerator,
        registry_reader: Optional[BaseAgent] = None,
        use_mock: bool = True
    ):
        """
        Initialize fingerprint verifier.
        
        Args:
            fingerprint_generator: Reference to WS1 for computation
            registry_reader: Reference to WS0 for lookup
            use_mock: Use mock or real fingerprints
        """
        super().__init__("WS2", use_mock)
        self.generator = fingerprint_generator
        self.registry_reader = registry_reader
    
    def handle_query(self, query: str) -> VerificationResult:
        """
        Handle verification requests.
        
        Query format: "verify:{skill_name}"
        Response: VerificationResult with is_valid flag
        """
        self.transition_state(AgentState.COMPUTING, f"Verifying: {query}")
        
        try:
            if not query.startswith("verify:"):
                raise ValueError(f"Invalid query format: {query}")
            
            skill_name = query.replace("verify:", "")
            is_valid, expected, current, message = self.verify(skill_name)
            
            result = VerificationResult(
                skill_name=skill_name,
                is_valid=is_valid,
                expected_fingerprint=expected,
                current_fingerprint=current,
                message=message
            )
            
            status = "✅ VALID" if is_valid else "❌ INVALID"
            self.transition_state(AgentState.VERIFIED, f"{status}: {skill_name}")
            return result
        
        except Exception as e:
            self.error = str(e)
            self.transition_state(AgentState.ERROR, f"Verification failed: {e}")
            raise
    
    def verify(self, skill_name: str) -> Tuple[bool, str, str, str]:
        """
        Verify skill fingerprint.
        
        Returns:
            (is_valid, expected_fingerprint, current_fingerprint, message)
        """
        # Step 1: Ask WS0 for expected fingerprint
        if not self.registry_reader:
            raise RuntimeError("Registry reader not initialized")
        
        self.transition_state(AgentState.QUERYING, f"Querying WS0 for {skill_name}")
        skill_metadata = self.registry_reader.handle_query(f"get_skill:{skill_name}")
        
        if not skill_metadata:
            message = f"Skill {skill_name} not found in registry"
            self.logger.warning(f"❌ {message}")
            return False, "", "", message
        
        expected = skill_metadata.fingerprint
        
        # Step 2: Compute current fingerprint (using same logic as WS1)
        self.transition_state(AgentState.COMPUTING, f"Computing fingerprint for {skill_name}")
        current = self.generator.compute_fingerprint(skill_name, skill_metadata.version)
        
        # Step 3: Compare
        self.transition_state(AgentState.VERIFIED, f"Comparison complete")
        
        if current == expected:
            message = f"✅ {skill_name} fingerprint verified"
            self.logger.info(message)
            return True, expected, current, message
        else:
            message = f"❌ {skill_name} fingerprint mismatch!\n  Expected: {expected}\n  Current: {current}"
            self.logger.error(message)
            return False, expected, current, message
