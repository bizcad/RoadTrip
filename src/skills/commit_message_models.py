"""
Data models for commit-message skill.

Defines input/output contracts for cost-optimized commit message generation.
Supports Tier 1 (deterministic), Tier 2 (LLM), and Tier 3 (user override).
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from enum import Enum
import json
from datetime import datetime, timezone


class CommitApproach(str, Enum):
    """Which tier generated the commit message."""
    TIER_1 = "tier1"          # Deterministic heuristics ($0)
    TIER_2 = "tier2"          # LLM fallback (~$0.001-0.01)
    TIER_3 = "tier3"          # User override ($0)


@dataclass
class Tier1Score:
    """
    Scoring details for Tier 1 (deterministic) evaluation.
    Used to explain why Tier 1 was chosen or why Tier 2 was needed.
    """
    file_count: int
    categories: List[str]                   # e.g., ["src", "tests"]
    single_category: bool                   # All files in one category?
    pattern_match: str                      # Pattern matched, e.g., "feat: {action}"
    message: str                            # The generated message
    confidence: float                       # 0.0-1.0 confidence in this message
    reasoning: str = ""                     # Human explanation
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CostTracking:
    """
    Tracks financial cost of Tier 2 (LLM) calls.
    """
    model: Optional[str]                    # e.g., "claude-3-5-sonnet-20241022"
    tokens_input: int = 0                   # Input tokens consumed
    tokens_output: int = 0                  # Output tokens consumed
    cost_usd: float = 0.0                  # $ spent on this call
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CommitMessageResult:
    """
    Output of commit-message skill.
    
    Provides generated message with full cost/confidence context.
    """
    message: str                            # The actual commit message
    approach_used: CommitApproach
    confidence: float                       # 0.0-1.0 (how sure we are)
    cost_estimate: float                    # $ spent (0.0 for Tier 1/3, >0 for Tier 2)
    reasoning: str                          # Why this message was chosen
    
    # Tier 1 details (if approach is Tier 1)
    tier1_score: Optional[Tier1Score] = None
    
    # Tier 2 details (if approach is Tier 2)
    cost_tracking: Optional[CostTracking] = None
    
    # Timestamps for auditing
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Context for logging
    context: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate approach consistency."""
        if self.approach_used == CommitApproach.TIER_1:
            assert self.cost_estimate == 0.0, "Tier 1 should have $0 cost"
            assert self.tier1_score is not None, "Tier 1 should have scoring details"
        
        if self.approach_used == CommitApproach.TIER_2:
            assert self.cost_estimate > 0.0, "Tier 2 should track cost > $0"
            assert self.cost_tracking is not None, "Tier 2 should have cost details"
        
        if self.approach_used == CommitApproach.TIER_3:
            assert self.cost_estimate == 0.0, "Tier 3 override should have $0 cost"
    
    def is_tier1(self) -> bool:
        return self.approach_used == CommitApproach.TIER_1
    
    def is_tier2(self) -> bool:
        return self.approach_used == CommitApproach.TIER_2
    
    def is_tier3(self) -> bool:
        return self.approach_used == CommitApproach.TIER_3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        result["approach_used"] = self.approach_used.value
        if self.tier1_score:
            result["tier1_score"] = self.tier1_score.to_dict()
        if self.cost_tracking:
            result["cost_tracking"] = self.cost_tracking.to_dict()
        return result
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class CommitMessageInput:
    """
    Input contract for commit-message skill.
    """
    staged_files: List[str]                 # Files staged for commit
    diff: Optional[str] = None              # Unified diff of changes
    strategy: str = "hybrid"                # hybrid|deterministic|ai
    confidence_threshold: float = 0.85      # Use Tier 2 if Tier 1 < this
    min_confidence_accept: float = 0.75     # Request user input if Tier 2 < this
    user_message: Optional[str] = None      # User override (Tier 3)
    
    def has_user_override(self) -> bool:
        """Does user want to skip Tier 1 and 2?"""
        return self.user_message is not None and len(self.user_message) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class ConventionalCommit:
    """
    Structured representation of a Conventional Commit.
    
    Format: type(scope): subject
            body
            footer
    
    See: https://www.conventionalcommits.org/
    """
    type: str                               # feat, fix, refactor, docs, test, chore, perf, ci
    scope: Optional[str] = None             # e.g., "auth", "cache"
    subject: str = ""                       # Imperative, no period, < 72 chars
    body: Optional[str] = None              # Explanation of WHY (optional)
    footers: Dict[str, str] = field(default_factory=dict)  # e.g., {"Closes": "GH-1234"}
    
    def to_conventional_string(self) -> str:
        """Format as conventional commit string."""
        lines = []
        
        # Subject line
        if self.scope:
            lines.append(f"{self.type}({self.scope}): {self.subject}")
        else:
            lines.append(f"{self.type}: {self.subject}")
        
        # Body
        if self.body:
            lines.append("")  # Blank line before body
            lines.append(self.body)
        
        # Footers
        if self.footers:
            lines.append("")  # Blank line before footers
            for key, value in self.footers.items():
                lines.append(f"{key}: {value}")
        
        return "\n".join(lines)
    
    @classmethod
    def from_string(cls, message: str) -> "ConventionalCommit":
        """Parse conventional commit from string."""
        lines = message.strip().split("\n")
        
        if not lines:
            raise ValueError("Empty commit message")
        
        # Parse subject line
        subject_line = lines[0]
        
        # Extract type and scope
        if "(" in subject_line and ")" in subject_line:
            type_scope, subject = subject_line.split(":", 1)
            type_part, scope = type_scope.split("(", 1)
            scope = scope.rstrip(")")
            commit_type = type_part.strip()
        else:
            type_part, subject = subject_line.split(":", 1)
            commit_type = type_part.strip()
            scope = None
        
        subject = subject.strip()
        
        # Parse body and footers
        body = None
        footers = {}
        
        if len(lines) > 2:
            # Skip blank line after subject
            body_section = "\n".join(lines[2:]).strip()
            
            # Check if there are footers
            footer_lines = []
            body_lines = []
            in_footers = False
            
            for line in body_section.split("\n"):
                if ": " in line and not line.startswith(" "):
                    in_footers = True
                    footer_lines.append(line)
                elif in_footers:
                    footer_lines.append(line)
                else:
                    body_lines.append(line)
            
            if body_lines:
                body = "\n".join(body_lines).strip()
            
            # Parse footers
            for footer_line in footer_lines:
                if ": " in footer_line:
                    key, value = footer_line.split(": ", 1)
                    footers[key] = value.strip()
        
        return cls(
            type=commit_type,
            scope=scope,
            subject=subject,
            body=body,
            footers=footers
        )


# For tests and cost estimation
@dataclass
class CostEstimate:
    """Pre-call cost estimate for Tier 2 LLM invocation."""
    model: str                              # e.g., "claude-3-5-sonnet-20241022"
    avg_input_tokens: int                   # Typical input tokens
    avg_output_tokens: int                  # Typical output tokens
    cost_per_1m_input: float                # List price per 1M input
    cost_per_1m_output: float               # List price per 1M output
    
    def estimate_cost(self) -> float:
        """Estimate cost for typical commit message call."""
        input_cost = (self.avg_input_tokens / 1_000_000) * self.cost_per_1m_input
        output_cost = (self.avg_output_tokens / 1_000_000) * self.cost_per_1m_output
        return input_cost + output_cost


# Pricing constants (as of 2026-02-07)
CLAUDE_SONNET_PRICING = CostEstimate(
    model="claude-3-5-sonnet-20241022",
    avg_input_tokens=300,       # Typical diff + context
    avg_output_tokens=50,       # Typical message
    cost_per_1m_input=0.003,   # $0.003 per 1M input tokens
    cost_per_1m_output=0.015,  # $0.015 per 1M output tokens
)
