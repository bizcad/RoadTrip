"""
Fingerprinting data models for skill identification, trust, and routing.

This module defines the data structures that will be used in:
- Phase 2a: Capability discovery and skill registry
- Phase 2b: IBAC (Intent-Based Access Control) decisions
- Phase 3+: Routing, DAG construction, adversarial testing

NOTE: These are STRUCTURE DEFINITIONS only. The telemetry that
populates them will be added in Phase 1b (ExecutionMetrics) and
Phase 2a (fingerprint computation). This file is written NOW so
Phase 2 work can proceed without surprises.

Design Philosophy:
- Fingerprints should be deterministic (same skill → same fingerprint)
- Fingerprints should be stable (minor version bumps don't change fingerprint)
- Fingerprints should be cryptographically strong (SHA256 truncated)
- All fields in fingerprints should be machine-readable and serializable
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Set, Tuple
from enum import Enum
import hashlib
import json


class CapabilityType(str, Enum):
    """Classification of what a skill does."""
    DATA_PRODUCER = "data_producer"      # Generates/acquires data
    DATA_TRANSFORMER = "data_transformer" # Processes/filters data
    DATA_VALIDATOR = "data_validator"     # Checks/verifies data
    ACTION_EXECUTOR = "action_executor"   # Performs external action
    ORCHESTRATOR = "orchestrator"         # Calls other skills
    OBSERVER = "observer"                 # Monitors/analyzes state


class ConfidenceLevel(str, Enum):
    """Confidence in skill's capability/reliability."""
    LOW = "low"           # 0.0–0.33 (unproven, experimental)
    MEDIUM = "medium"     # 0.33–0.67 (tested, some gaps)
    HIGH = "high"         # 0.67–1.0 (production-grade)


@dataclass
class Capability:
    """
    A single capability that a skill provides.
    
    Example:
        Skill "commit_message_generator" provides capability:
        - name: "generate_commit_message"
        - inputs: {"staged_files": ["str"], "style": "str"}
        - outputs: {"message": "str", "confidence": "float"}
        - cost_tokens: 100–500 (variable, depends on file count)
        - confidence_level: "high" (99.2% success rate)
    """
    
    name: str                           # "generate_commit_message"
    description: str                     # What this capability does
    capability_type: CapabilityType      # DATA_PRODUCER, ACTION_EXECUTOR, etc.
    
    inputs: Dict[str, List[str]]        # Field name -> [list of allowed types]
                                         # e.g., {"files": ["List[str]"]}
                                         # e.g., {"style": ["str", "Literal['conventional', 'angular']"]}
    
    outputs: Dict[str, str]              # Field name -> type
                                         # e.g., {"message": "str", "confidence": "float"}
    
    cost_tokens_min: int = 0             # Min tokens for this capability
    cost_tokens_max: int = 1000          # Max tokens for this capability
    cost_tokens_typical: int = 500       # Typical/expected tokens
    
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    success_rate_approximate: float = 0.95  # Historical success rate (0.0–1.0)
    
    requires_approval: bool = False      # Does this need human approval?
    approval_reason: Optional[str] = None  # Why does it require approval?
    
    security_tier: int = 0               # 0=no restrictions, 1=auth, 2=approval, 3=audit-only
    
    tags: Set[str] = field(default_factory=set)  # "git", "commit", "llm", "deterministic", etc.
    
    def to_dict(self) -> Dict:
        """Convert to serializable dict."""
        d = asdict(self)
        d['capability_type'] = self.capability_type.value
        d['confidence_level'] = self.confidence_level.value
        d['tags'] = list(self.tags)
        return d


@dataclass
class SkillMetadata:
    """
    Metadata about a skill (interface, author, version).
    
    This is the "identity card" of a skill. It should be stable
    and deterministic—the same skill code should always produce
    the same metadata fingerprint.
    """
    
    skill_name: str                      # "git_push_autonomous"
    skill_id: str                        # UUID per version (usually skill_name + version)
    author: str                          # "bizcad" | "system" | "external"
    version: str                         # "1.0.0" (SemVer)
    
    description: str                     # "Autonomously pushes commits to git with safety checks"
    documentation_url: Optional[str]     # Link to docs
    
    entry_point: str                     # "src/skills/git_push_autonomous.py::execute"
    entry_point_signature: str           # "execute(input: GitPushInput) -> ExecutionResult"
    
    capabilities: List[Capability] = field(default_factory=list)
    
    dependencies: Dict[str, str] = field(default_factory=dict)  # "requests": ">=2.28.0"
    requires_auth: bool = False
    requires_approval: bool = False
    
    created_date: str = ""               # ISO8601 timestamp
    last_updated: str = ""               # ISO8601 timestamp
    
    provenance: str = "internal"         # "internal" | "external" | "community"
    license: str = "MIT"                 # License of the skill
    
    tags: Set[str] = field(default_factory=set)  # "safety-critical", "free-tier", "async", etc.
    
    def to_dict(self) -> Dict:
        """Convert to serializable dict."""
        d = asdict(self)
        d['capabilities'] = [c.to_dict() if isinstance(c, Capability) else c for c in self.capabilities]
        d['tags'] = list(d.get('tags', []))
        d['dependencies'] = dict(self.dependencies)
        return d


@dataclass
class SkillFingerprint:
    """
    Cryptographic fingerprint of a skill (deterministic hash).
    
    The fingerprint serves as a "seal" that proves:
    1. This is the same code that previously passed security review
    2. No code has changed since fingerprint was computed
    3. The interface (inputs/outputs) matches what we tested
    
    Fingerprints are computed from:
    - Bytecode/source code hash (if available; else skip)
    - Interface specification (inputs, outputs, signature)
    - Test specification (what we tested it against)
    - Versioning (skill version, dependencies)
    
    The fingerprint is deterministic: same code → same fingerprint.
    It is stable: minor version bumps (1.0.0 → 1.0.1 bugfix) should ideally
    preserve fingerprint IF the interface doesn't change.
    """
    
    skill_id: str                        # "git_push_autonomous::1.0.0"
    fingerprint_hash: str                # SHA256(interface + tests)[0:16]
                                         # e.g., "a3f7d4e9c2b18f95"
    
    hash_algorithm: str = "sha256"       # For future algorithm upgrades
    hash_components: Dict[str, str] = field(default_factory=dict)
                                         # "interface_signature": "hash_of_inputs_outputs",
                                         # "test_spec": "hash_of_test_file",
                                         # "source_code": "hash_of_source", (optional)
                                         # "dependencies": "hash_of_requirements",
    
    computed_at: str = ""                # ISO8601 timestamp when fingerprint computed
    computed_by: str = ""                # "phase2a_fingerprinter" | "manual" | etc.
    
    metadata: Optional[SkillMetadata] = None  # The skill this fingerprint represents
    
    is_valid: bool = True                # Has this fingerprint been verified?
    verification_notes: Optional[str] = None
    
    @staticmethod
    def compute_deterministic_hash(components: Dict[str, str]) -> str:
        """
        Compute a deterministic hash from interface + tests.
        
        Input: Dict of {component_name: content}
               e.g., {"interface": "def execute(input: GitPushInput) -> ...",
                      "test_spec": "def test_success(): ..."}
        
        Output: Thirty-two character SHA256 hash (truncated to 16 for readability)
        
        This is deterministic: same components → same hash.
        """
        # Sort keys to ensure deterministic ordering
        sorted_components = sorted(components.items())
        merged = "\n".join(f"{k}:::{v}" for k, v in sorted_components)
        hash_obj = hashlib.sha256(merged.encode('utf-8'))
        return hash_obj.hexdigest()[:16]  # Truncate to 16 chars for readability


@dataclass
class SkillTrustVector:
    """
    Multi-dimensional assessment of trust in a skill.
    
    Trust is not binary (safe/unsafe). Instead, we assess trust
    across multiple dimensions:
    
    - Code Quality: Is it well-written? Does it follow conventions?
    - Security: Could it leak credentials? Modify system files?
    - Reliability: Does it consistently work? Fail gracefully?
    - Performance: Is it within acceptable latency/cost bounds?
    - Auditability: Can we understand what it's doing? Full audit trail?
    - Author Reputation: Who wrote it? Do they have history here?
    - Community Signal: How many people use it? What's the feedback?
    
    Each dimension is scored 0.0–1.0. An "untrusted" skill might be 0.2.
    A "trusted" skill might be 0.9. A "safety-critical" skill must be 0.95+.
    """
    
    skill_id: str
    
    code_quality_score: float = 0.5      # Is it well-written?
    security_score: float = 0.5          # Could it be exploited?
    reliability_score: float = 0.5       # Does it work consistently?
    performance_score: float = 0.5       # Is it fast? Cost-effective?
    auditability_score: float = 0.5      # Can we trace its execution?
    author_reputation_score: float = 0.5 # Who wrote it?
    community_signal_score: float = 0.5  # What do other operators think?
    
    overall_trust_score: float = 0.5     # Weighted average
    
    approval_count: int = 0              # How many operators have approved it?
    rejection_count: int = 0             # How many have rejected it?
    incident_count: int = 0              # How many incidents in production?
    
    notes: List[str] = field(default_factory=list)  # ["High security score due to sandboxing", ...]
    
    def compute_overall_score(self, weights: Optional[Dict[str, float]] = None) -> float:
        """
        Compute overall trust score as weighted average.
        
        Default weights: equal importance to all dimensions.
        Custom weights: can adjust for your priorities.
        """
        if weights is None:
            weights = {
                'code_quality_score': 0.15,
                'security_score': 0.25,
                'reliability_score': 0.25,
                'performance_score': 0.10,
                'auditability_score': 0.15,
                'author_reputation_score': 0.10,
                'community_signal_score': 0.0,  # Not used if no public data
            }
        
        scores = {
            'code_quality_score': self.code_quality_score,
            'security_score': self.security_score,
            'reliability_score': self.reliability_score,
            'performance_score': self.performance_score,
            'auditability_score': self.auditability_score,
            'author_reputation_score': self.author_reputation_score,
            'community_signal_score': self.community_signal_score,
        }
        
        weighted_sum = sum(scores[k] * weights.get(k, 0) for k in scores.keys())
        return min(1.0, max(0.0, weighted_sum))


@dataclass
class SkillSecurityProfile:
    """
    Security classification and restrictions for a skill.
    
    Used by IBAC (Intent-Based Access Control) to decide if
    a skill should be invoked, and with what restrictions.
    """
    
    skill_id: str
    
    # Security tier: 0 (unrestricted) to 3 (audit only, requires approval)
    security_tier: int = 0
    tier_reason: str = ""
    
    # What resources can this skill access?
    can_read_credentials: bool = False
    can_write_credentials: bool = False
    can_read_filesystem: bool = False
    can_write_filesystem: bool = False
    can_execute_external_commands: bool = False
    can_make_network_requests: bool = False
    can_modify_git_history: bool = False  # Special flag for destructive operations
    
    # Cost/quota implications
    free_tier_safe: bool = True           # Is it safe under free tier limits?
    typical_cost_tokens: int = 0          # How many tokens does it usually consume?
    maximum_cost_tokens: int = 0          # Hard limit before it fails
    
    # Approval requirements
    requires_approval: bool = False
    approval_reason: str = ""
    auto_approval_conditions: Optional[List[str]] = None  # Can auto-approve if these are met
                                                          # e.g., ["input_size < 1000", "cost < 100"]
    
    # Restrictions
    restricted_to_operators: Optional[Set[str]] = None  # Only these operators can use
    restricted_to_intents: Optional[Set[str]] = None    # Only these intent patterns
    restricted_to_hours: Optional[Tuple[int, int]] = None  # Only during these hours (24-hour)
    
    # Isolation/sandboxing
    requires_sandboxing: bool = False
    sandbox_profile: Optional[str] = None  # "strict" | "moderate" | "permissive"
    
    # Disaster recovery
    is_disaster_critical: bool = False    # Must be available even if system is degraded
    can_be_auto_retried: bool = True
    can_be_auto_rolled_back: bool = True


@dataclass
class SkillExecutionSnapshot:
    """
    A snapshot of a skill's metrics at execution time.
    
    This is different from ExecutionMetrics (which is per-execution).
    This is rolled up to a "profile" level: "What is this skill like
    in production?"
    
    Computed weekly from ExecutionMetrics JSONL logs.
    Used by fingerprinting + routing to understand skill behavior.
    """
    
    skill_id: str
    snapshot_date: str                   # ISO8601 date
    
    # Success metrics
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    success_rate: float = 0.95            # Computed: successful / total
    
    # Performance metrics
    latency_p50_ms: float = 0.0           # 50th percentile latency
    latency_p95_ms: float = 0.0           # 95th percentile latency
    latency_p99_ms: float = 0.0           # 99th percentile (worst case)
    timeout_count: int = 0                # How often did it exceed timeout?
    
    # Cost metrics
    tokens_min: int = 0                   # Minimum tokens used in any execution
    tokens_max: int = 0                   # Maximum tokens used
    tokens_mean: int = 0                  # Average tokens per execution
    cost_usd_total: float = 0.0           # Total cost for the week
    cost_usd_mean: float = 0.0            # Average cost per execution
    
    # Quality metrics
    output_quality_score: float = 0.5     # Subjective: how good are the outputs?
    error_messages: List[str] = field(default_factory=list)  # Unique error patterns seen
    
    # Anomalies
    anomalies_detected: int = 0           # How many times did this skill behave unexpectedly?
    anomaly_descriptions: List[str] = field(default_factory=list)
    
    # Drift detection
    change_from_baseline: float = 0.0     # % change in success rate vs. baseline
    concerning_trends: List[str] = field(default_factory=list)  # ["success_rate_declining_2%_per_day", ...]
    
    def to_dict(self) -> Dict:
        """Convert to serializable dict."""
        return asdict(self)


# ============================================================================
# Registry Models (for Phase 2a fingerprinting + capability discovery)
# ============================================================================

@dataclass
class SkillRegistryEntry:
    """
    A single entry in the skill registry (REGISTRY.yaml or database).
    
    This is what the orchestrator queries to find skills:
    "Find skills with capability='generate_commit_message' and confidence > 0.9"
    """
    
    metadata: SkillMetadata
    fingerprint: SkillFingerprint
    trust_vector: SkillTrustVector
    security_profile: SkillSecurityProfile
    
    execution_snapshot: Optional[SkillExecutionSnapshot] = None  # Latest weekly snapshot
    
    approved: bool = False                # Has this been approved for production?
    approval_date: Optional[str] = None
    approval_by: Optional[str] = None     # Who approved it?
    
    deprecated: bool = False              # Is this skill being phased out?
    deprecation_reason: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to serializable dict for REGISTRY.yaml."""
        return {
            'metadata': self.metadata.to_dict(),
            'fingerprint': asdict(self.fingerprint),
            'trust_vector': asdict(self.trust_vector),
            'security_profile': asdict(self.security_profile),
            'execution_snapshot': asdict(self.execution_snapshot) if self.execution_snapshot else None,
            'approved': self.approved,
            'approval_date': self.approval_date,
            'approval_by': self.approval_by,
            'deprecated': self.deprecated,
            'deprecation_reason': self.deprecation_reason,
        }


@dataclass
class CapabilityQuery:
    """
    A query to find skills matching certain capabilities.
    
    Used by orchestrator to answer questions like:
    "Find all skills that can generate commit messages with >= 0.85 confidence"
    """
    
    capability_name: str                 # "generate_commit_message"
    min_confidence: float = 0.5           # Only return skills with >= this confidence
    approved_only: bool = True            # Only return approved skills?
    deprecated_excluded: bool = True      # Exclude deprecated skills?
    
    min_reliability: Optional[float] = None  # e.g., >= 0.95 success rate
    max_cost_tokens: Optional[int] = None    # e.g., max 500 tokens per execution
    
    limit: int = 10                       # Return top N matches
    rank_by: str = "trust_score"          # Sort by confidence_level | trust_score | success_rate | cost
    
    def to_sql_where_clause(self) -> str:
        """For future: convert to SQL WHERE clause if using database."""
        pass


if __name__ == "__main__":
    # Example: Define git-push-autonomous skill with multiple capabilities
    
    cap_push = Capability(
        name="push_git_commit",
        description="Push a staged commit to remote git repository",
        capability_type=CapabilityType.ACTION_EXECUTOR,
        inputs={"branch": ["str"], "message": ["str"]},
        outputs={"success": ["bool"], "commit_hash": ["str"]},
        cost_tokens_min=10,
        cost_tokens_max=100,
        cost_tokens_typical=50,
        confidence_level=ConfidenceLevel.HIGH,
        success_rate_approximate=0.98,
        requires_approval=False,
        security_tier=2,     # Requires auth (git credentials)
        tags={"git", "destructive", "safety-critical"},
    )
    
    metadata = SkillMetadata(
        skill_name="git_push_autonomous",
        skill_id="git_push_autonomous::1.0.0",
        author="bizcad",
        version="1.0.0",
        description="Autonomously pushes commits to git with safety checks and audit trails",
        entry_point="src/skills/git_push_autonomous.py::execute",
        entry_point_signature="execute(input: GitPushInput) -> ExecutionResult",
        capabilities=[cap_push],
        requires_auth=True,
        requires_approval=False,
        created_date="2026-01-15T00:00:00Z",
        tags={"git", "safety-critical", "deterministic"},
    )
    
    fingerprint = SkillFingerprint(
        skill_id="git_push_autonomous::1.0.0",
        fingerprint_hash="a3f7d4e9c2b18f95",  # Would be computed
        hash_components={
            "interface_signature": "hash_of_inputs_outputs",
            "test_spec": "hash_of_test_file",
        },
        computed_at="2026-01-15T10:00:00Z",
        computed_by="phase2a_fingerprinter",
        metadata=metadata,
    )
    
    trust_vector = SkillTrustVector(
        skill_id="git_push_autonomous::1.0.0",
        code_quality_score=0.95,
        security_score=0.90,
        reliability_score=0.98,
        performance_score=0.85,
        auditability_score=0.95,
        author_reputation_score=0.80,
        approval_count=5,
        incident_count=0,
    )
    
    security_profile = SkillSecurityProfile(
        skill_id="git_push_autonomous::1.0.0",
        security_tier=2,
        tier_reason="Requires git credentials; destructive operations",
        can_write_filesystem=True,
        can_execute_external_commands=True,
        can_modify_git_history=True,
        requires_approval=False,
        can_be_auto_retried=False,
        can_be_auto_rolled_back=False,  # Git history is immutable
    )
    
    registry_entry = SkillRegistryEntry(
        metadata=metadata,
        fingerprint=fingerprint,
        trust_vector=trust_vector,
        security_profile=security_profile,
        approved=True,
        approval_date="2026-01-15T15:00:00Z",
        approval_by="bizcad",
    )
    
    print("Skill Registry Entry for git_push_autonomous:")
    print(json.dumps(registry_entry.to_dict(), indent=2, default=str))
