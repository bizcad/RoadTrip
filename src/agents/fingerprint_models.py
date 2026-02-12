"""
Data models for Fingerprint Agent (Phase 2a).

Defines:
- SkillFingerprint: Cryptographic attestation of a skill
- FingerprintInput/FingerprintResult: Agent I/O
- TrustScore events: Emitted when fingerprints generated or tests pass
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from enum import Enum


class FingerprintStatus(str, Enum):
    """Status of fingerprinting operation."""
    SUCCESS = "success"
    FAILED = "failed"
    INVALID_SKILL = "invalid_skill"
    NO_TESTS = "no_tests"
    HASH_MISMATCH = "hash_mismatch"


@dataclass
class SkillFingerprint:
    """
    Cryptographic fingerprint of a skill.
    
    Includes:
    - Deterministic hash of code + capabilities + test metadata
    - Self-signed attestation from fingerprint authority
    - Timestamp and versioning info
    """
    
    # Hashes (deterministic, content-addressed)
    code_hash: str                          # SHA256 of skill Python source
    capabilities_hash: str                  # SHA256 of capabilities.json (what skill can do)
    test_metadata_hash: str                 # SHA256 of test count + pass rate + coverage
    
    # Version info
    skill_name: str                         # e.g., "auth_validator"
    skill_version: str                      # e.g., "1.0" from package version
    
    # Test metadata embedded in fingerprint
    test_count: int = 0                     # Number of tests
    test_pass_rate: float = 0.0             # Percentage of tests passing
    test_coverage: Optional[float] = None   # % code coverage (optional)
    
    # Signature
    signature: Optional[str] = None         # RSA-2048 signature of composite hash
    signed: bool = False                    # True if signature generated
    signer_key_id: str = "fingerprint-authority-v1"  # Which key signed this
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    signed_at: Optional[datetime] = None
    
    # Metadata
    fingerprint_algorithm: str = "sha256"
    signature_algorithm: str = "rsa-2048"
    
    def composite_hash(self) -> str:
        """
        Combined hash of all components (deterministic).
        Used as input to signing.
        """
        # Order matters for determinism
        combined = f"{self.code_hash}:{self.capabilities_hash}:{self.test_metadata_hash}"
        return combined


@dataclass
class FingerprintInput:
    """Input to Fingerprint Agent."""
    
    skill_name: str                         # e.g., "auth_validator"
    skill_version: str                      # e.g., "1.0"
    skill_path: str                         # Path to skill file (e.g., src/skills/auth_validator.py)
    test_path: Optional[str] = None         # Path to test file (e.g., tests/test_auth_validator.py)
    sign: bool = True                       # Generate signature?
    force_rehash: bool = False              # Recompute hashes even if cached?


@dataclass
class FingerprintResult:
    """Output from Fingerprint Agent."""
    
    status: FingerprintStatus
    skill_name: str
    fingerprint: Optional[SkillFingerprint] = None
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Optional: diagnostic info
    code_hash_computed: Optional[str] = None
    capabilities_found: bool = False
    tests_found: bool = False


@dataclass
class SkillFingerprintedEvent:
    """
    Event emitted when a skill is fingerprinted.
    Written to data/skill-events.jsonl for Phase 2b to read.
    """
    
    event_type: str = "skill_fingerprinted"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    skill_name: str = ""
    fingerprint_hash: str = ""              # composite_hash() value
    signed: bool = False
    signer_key_id: str = ""
    
    # Correlation for auditing
    workflow_id: Optional[str] = None       # If fingerprinting part of larger workflow


@dataclass
class SkillTestPassedEvent:
    """
    Event emitted when skill tests pass (successful fingerprinting prerequisite).
    """
    
    event_type: str = "skill_test_passed"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    skill_name: str = ""
    test_count: int = 0
    test_pass_rate: float = 0.0
    coverage: Optional[float] = None
    
    # Correlation
    workflow_id: Optional[str] = None
