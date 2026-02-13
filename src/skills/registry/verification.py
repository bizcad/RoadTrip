"""
verification.py (WS4) - Fingerprint Enforcement

Enforces fingerprint verification at skill execution time.
- Uses WS2 to verify
- Blocks execution if fingerprint mismatch
- Logs all decisions for audit trail
"""

import logging
from typing import Tuple

from .base_agent import BaseAgent
from .fingerprint_verifier import FingerprintVerifier
from .registry_models import AgentState


class Verification(BaseAgent):
    """WS4: Verification - Enforce fingerprint checks at execution."""
    
    def __init__(self, fingerprint_verifier: FingerprintVerifier, use_mock: bool = True):
        """
        Initialize verification agent.
        
        Args:
            fingerprint_verifier: Reference to WS2
            use_mock: Use mock or real fingerprints
        """
        super().__init__("WS4", use_mock)
        self.verifier = fingerprint_verifier
        self.audit_log = []  # Log of all verification decisions
    
    def handle_query(self, query: str) -> Tuple[bool, str]:
        """
        Handle enforcement requests.
        
        Query format: "enforce:{skill_name}"
        Response: (is_allowed, message)
        """
        self.transition_state(AgentState.COMPUTING, f"Enforcing: {query}")
        
        try:
            if not query.startswith("enforce:"):
                raise ValueError(f"Invalid query format: {query}")
            
            skill_name = query.replace("enforce:", "")
            is_allowed, message = self.enforce(skill_name)
            
            self.transition_state(AgentState.VERIFIED, f"Decision: {'ALLOW' if is_allowed else 'REJECT'}")
            return is_allowed, message
        
        except Exception as e:
            self.error = str(e)
            self.transition_state(AgentState.ERROR, f"Enforcement failed: {e}")
            raise
    
    def enforce(self, skill_name: str) -> Tuple[bool, str]:
        """
        Enforce fingerprint verification.
        
        Returns:
            (is_allowed, message)
            
        Raises:
            RuntimeError if fingerprint mismatch (skill modified)
        """
        self.transition_state(AgentState.QUERYING, f"Verifying {skill_name} via WS2")
        
        # Ask WS2 to verify
        verification_result = self.verifier.handle_query(f"verify:{skill_name}")
        
        # Log decision
        self.audit_log.append({
            "timestamp": verification_result.verified_at,
            "skill_name": skill_name,
            "decision": "ALLOW" if verification_result.is_valid else "REJECT",
            "fingerprint": verification_result.current_fingerprint,
            "expected": verification_result.expected_fingerprint,
            "message": verification_result.message
        })
        
        if verification_result.is_valid:
            self.logger.info(f"✅ ALLOW: {skill_name} verified")
            return True, f"✅ {skill_name} passed fingerprint verification"
        else:
            message = f"❌ REJECT: {skill_name} fingerprint mismatch!"
            self.logger.error(message)
            self.logger.error(f"  Expected: {verification_result.expected_fingerprint}")
            self.logger.error(f"  Current:  {verification_result.current_fingerprint}")
            
            return False, message
    
    def get_audit_log(self) -> list:
        """Get audit log of all verification decisions."""
        return self.audit_log
