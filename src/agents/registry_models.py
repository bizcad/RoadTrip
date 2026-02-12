"""
Data models for Registry Agent (Phase 2a).

Defines:
- SkillRegistryEntry: Catalog entry for one skill
- RegistryInput/RegistryResult: Agent I/O
- Search queries and results
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from enum import Enum

# Import fingerprint models
try:
    from .fingerprint_models import SkillFingerprint
except ImportError:
    from fingerprint_models import SkillFingerprint


class RegistryOperation(str, Enum):
    """Supported registry operations."""
    ADD = "add"
    UPDATE = "update"
    DELETE = "delete"
    READ = "read"
    LIST = "list"
    SEARCH = "search"


class RegistryStatus(str, Enum):
    """Status of registry operation."""
    SUCCESS = "success"
    FAILED = "failed"
    NOT_FOUND = "not_found"
    ALREADY_EXISTS = "already_exists"
    INVALID_INPUT = "invalid_input"


@dataclass
class SkillRegistryEntry:
    """
    Catalog entry for one skill.
    
    Combines skill metadata + fingerprint + test results + trust info.
    """
    
    # Identity
    name: str                               # e.g., "auth_validator"
    version: str                            # e.g., "1.0"
    
    # Description
    description: str = ""                   # Human-readable description
    author: Optional[str] = None            # Creator/maintainer
    
    # Fingerprint
    fingerprint: Optional[SkillFingerprint] = None
    
    # Capabilities (what can this skill do?)
    capabilities: List[str] = field(default_factory=list)  # e.g., ["validate_auth", "check_branch"]
    
    # Test results (materialized at time of fingerprinting)
    test_count: int = 0
    test_pass_rate: float = 0.0
    test_coverage: Optional[float] = None
    last_test_run: Optional[datetime] = None
    
    # Trust/Status
    trusted: bool = False                   # Set by Phase 2b Verifier Agent
    trust_score: float = 0.0                # 0.0-1.0, set by Phase 2b
    last_verified: Optional[datetime] = None
    
    # Lifecycle
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_fingerprinted: Optional[datetime] = None
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Status
    active: bool = True                     # Can this skill be executed?
    deprecated: bool = False                # Is this version deprecated?
    deprecation_reason: Optional[str] = None
    
    # Links
    source_file: Optional[str] = None       # Path to .py file (e.g., src/skills/auth_validator.py)
    test_file: Optional[str] = None         # Path to test file
    documentation_url: Optional[str] = None


@dataclass
class RegistryInput:
    """Input to Registry Agent."""
    
    operation: RegistryOperation
    entry: Optional[SkillRegistryEntry] = None  # For add/update
    skill_name: Optional[str] = None            # For read/delete
    search_query: Optional[str] = None          # For search
    
    # Search options
    search_fields: List[str] = field(default_factory=lambda: ["name", "description", "capabilities"])
    limit: int = 10                         # Max results


@dataclass
class SearchResult:
    """One search result (skill + relevance score)."""
    entry: SkillRegistryEntry
    relevance: float                        # 0.0-1.0, relevance score


@dataclass
class RegistryResult:
    """Output from Registry Agent."""
    
    status: RegistryStatus
    operation: RegistryOperation
    
    # Results depend on operation
    entry: Optional[SkillRegistryEntry] = None      # For read
    entries: List[SkillRegistryEntry] = field(default_factory=list)  # For list
    search_results: List[SearchResult] = field(default_factory=list)  # For search
    
    # Error info
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    count: int = 0                          # Number of entries returned/affected
    total_in_registry: int = 0              # Total skills in registry
