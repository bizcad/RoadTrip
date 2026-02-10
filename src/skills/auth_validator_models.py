"""
Data models for auth-validator skill.

Defines input/output contracts for authorization decision-making.
Compatible with JSON serialization for audit logging and orchestration.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from enum import Enum
import json
from datetime import datetime, timezone


# Phase 1b: Simple auth status/method enums
class AuthStatus(str, Enum):
    """Result of authentication validation."""
    VALID = "valid"              # Auth credentials valid and authorized
    INVALID = "invalid"          # Credentials missing or incorrect
    EXPIRED = "expired"          # Token expired or key revoked
    PERMISSION_DENIED = "denied" # Valid creds but not permitted for operation
    UNREACHABLE = "unreachable"  # Can't reach auth service (network error)


class AuthMethod(str, Enum):
    """Authentication method used."""
    TOKEN = "token"              # GitHub personal access token
    SSH_KEY = "ssh_key"          # SSH key authentication
    HTTPS_CREDENTIALS = "https"  # HTTPS username/password
    UNKNOWN = "unknown"


class AuthzDecision(str, Enum):
    """Authorization decision outcomes."""
    APPROVED = "APPROVED"
    FORBIDDEN_LAYER_1 = "FORBIDDEN_LAYER_1"      # Group membership failed
    FORBIDDEN_LAYER_2 = "FORBIDDEN_LAYER_2"      # Role or MFA failed
    FORBIDDEN_LAYER_3 = "FORBIDDEN_LAYER_3"      # Tool permission failed
    FORBIDDEN_LAYER_4 = "FORBIDDEN_LAYER_4"      # Resource access failed


@dataclass
class UserIdentity:
    """Represents a user's identity context for authorization checks."""
    username: str
    groups: List[str]                  # e.g., ["engineering-team", "project-omega"]
    role: str                          # e.g., "Senior-Engineer"
    role_rank: Optional[int] = None    # Populated from config
    mfa_validated: bool = False
    mfa_method: Optional[str] = None   # e.g., "totp", "webauthn"
    session_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class Resource:
    """Represents a resource being accessed (e.g., git branch, file path)."""
    type: str                          # e.g., "git-branch", "file-path", "api-endpoint"
    name: str                          # e.g., "origin/main", "src/auth.py", "/api/users"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LayerCheckResult:
    """Result of a single layer authorization check."""
    layer: int                         # 1, 2, 3, or 4
    passed: bool
    reason: str                        # e.g., "Group membership verified"
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AuthValidationResult:
    """
    Output of auth-validator skill.
    
    Provides complete authorization decision with full audit trail.
    """
    decision: AuthzDecision
    layers_passed: List[int] = field(default_factory=list)      # [1, 2, 3]
    layers_failed: List[int] = field(default_factory=list)      # [4]
    reason: str = ""                   # User-friendly explanation
    recovery_action: Optional[str] = None  # What user should do
    confidence: float = 1.0            # 0.0-1.0 (auth is binary in Phase 1b)
    
    # Detailed layer-by-layer breakdown
    layer_details: Dict[int, LayerCheckResult] = field(default_factory=dict)
    
    # Timestamps for auditing
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # Context for logging/debugging
    context: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate decision consistency."""
        if self.decision == AuthzDecision.APPROVED:
            assert not self.layers_failed, "APPROVED decision should have no failed layers"
        else:
            assert self.layers_failed, f"{self.decision} should have failed layers"
    
    def is_approved(self) -> bool:
        """Convenience method."""
        return self.decision == AuthzDecision.APPROVED
    
    def is_forbidden(self) -> bool:
        """Convenience method."""
        return not self.is_approved()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        # Convert decision enum to string
        result["decision"] = self.decision.value
        # Convert layer details
        result["layer_details"] = {
            k: v.to_dict() for k, v in self.layer_details.items()
        }
        return result
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def __str__(self) -> str:
        """Human-readable output for console display."""
        lines = []
        
        if self.is_approved():
            lines.append("✅ Authorization Approved")
        else:
            lines.append(f"❌ Authorization Denied: {self.decision}")
            lines.append("")
            lines.append(self.reason)
            if self.recovery_action:
                lines.append("")
                lines.append("What to do:")
                lines.append(f"  {self.recovery_action}")
        
        return "\n".join(lines)


@dataclass
class AuthValidationInput:
    """
    Input contract for auth-validator skill.
    
    Specifies user, action, and target resource.
    """
    user_identity: UserIdentity
    skill_name: str                    # e.g., "git-push-autonomous"
    resource: Optional[Resource] = None  # e.g., target branch
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_identity": self.user_identity.to_dict(),
            "skill_name": self.skill_name,
            "resource": self.resource.to_dict() if self.resource else None
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


# For tests and simulation
@dataclass
class MockAuthConfig:
    """Mock configuration for unit testing."""
    user_roles: Dict[str, int]         # username -> role_rank
    skill_groups: Dict[str, List[str]]  # skill_name -> allowed_groups
    branch_permissions: Dict[str, List[int]]  # branch_name -> allowed_role_ranks
    path_permissions: Dict[str, bool]  # path -> allowed (True/False)
