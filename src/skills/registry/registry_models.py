"""
registry_models.py - Shared Data Models for Registry System

Used by all workstreams (WS0-4) to ensure consistent interfaces.
These models define the contract between agents.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class SkillStatus(Enum):
    """Status of a skill in the registry."""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"
    SUSPENDED = "suspended"


class AgentState(Enum):
    """State of a workstream agent."""
    INIT = "init"
    QUERYING = "querying"
    COMPUTING = "computing"
    WRITING = "writing"
    VERIFIED = "verified"
    ERROR = "error"


@dataclass
class SkillMetadata:
    """Metadata for a registered skill."""
    name: str
    version: str
    fingerprint: str
    author: str
    capabilities: List[str]
    tests: int = 0
    test_coverage: float = 0.0
    status: SkillStatus = SkillStatus.ACTIVE
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    description: str = ""
    source_files: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for YAML serialization."""
        return {
            "version": self.version,
            "fingerprint": self.fingerprint,
            "author": self.author,
            "capabilities": self.capabilities,
            "tests": self.tests,
            "test_coverage": self.test_coverage,
            "status": self.status.value,
            "created": self.created,
            "description": self.description,
            "source_files": self.source_files
        }


@dataclass
class RegistryData:
    """Complete registry structure."""
    metadata: Dict[str, Any] = field(default_factory=dict)
    skills: Dict[str, SkillMetadata] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set defaults for metadata."""
        if not self.metadata:
            self.metadata = {
                "version": "1.0",
                "fingerprinting_algorithm": "sha256:16",
                "last_updated": datetime.now().isoformat()
            }


@dataclass
class FingerprintResult:
    """Result of fingerprint computation."""
    skill_name: str
    version: str
    fingerprint: str
    is_mock: bool = False
    computed_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RegistrationResult:
    """Result of skill registration."""
    skill_name: str
    version: str
    fingerprint: str
    status: str = "registered"
    message: str = ""
    registered_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class VerificationResult:
    """Result of fingerprint verification."""
    skill_name: str
    is_valid: bool
    expected_fingerprint: str
    current_fingerprint: str
    message: str = ""
    verified_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AgentQuery:
    """Record of an inter-agent query."""
    from_agent: str
    to_agent: str
    query: str
    response: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AgentStatus:
    """Status of a workstream agent."""
    agent_id: str  # "WS0", "WS1", etc.
    state: AgentState = AgentState.INIT
    last_action: str = ""
    error: Optional[str] = None
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
