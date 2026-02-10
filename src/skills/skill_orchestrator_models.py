"""
Data models for skill_orchestrator.

Generic orchestrator that chains multiple skills into a workflow.
Follows interface pattern: same calling convention, different skill chains.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional
from enum import Enum
from datetime import datetime, timezone


class SkillStatus(str, Enum):
    """Status of a single skill execution."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class SkillExecutionRecord:
    """Record of one skill's execution in a workflow."""
    skill_name: str                         # e.g., "auth_validator"
    status: SkillStatus                     # Success, failed, skipped, etc.
    input_data: Dict[str, Any]              # What we passed in
    output_data: Dict[str, Any]             # What it returned
    
    execution_time_ms: float = 0.0          # How long it took
    error_code: Optional[str] = None        # If failed, error code
    error_message: Optional[str] = None     # If failed, error details
    
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None


@dataclass
class OrchestrationResult:
    """
    Output of skill orchestrator.
    
    Complete execution record: which skills ran, in what order, what happened.
    """
    workflow_id: str                        # Unique ID for this workflow run
    workflow_name: str                      # e.g., "git_push", "blog_publish"
    status: SkillStatus                     # Overall status
    
    # Execution records
    skill_records: List[SkillExecutionRecord] = field(default_factory=list)
    
    # Overall result
    final_output: Dict[str, Any] = field(default_factory=dict)  # Final result data
    final_decision: str = ""                # Overall decision: APPROVED, DENIED, ERROR, etc.
    
    # Error handling
    error_code: Optional[str] = None        # If workflow failed, why?
    error_message: Optional[str] = None     # Safe error message
    should_rollback: bool = False           # Should we undo what we did?
    
    # Telemetry
    total_execution_time_ms: float = 0.0
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    
    def success(self) -> bool:
        """Was workflow successful?"""
        return self.status == SkillStatus.SUCCESS
    
    def failed(self) -> bool:
        """Did workflow fail?"""
        return self.status == SkillStatus.FAILED


@dataclass
class WorkflowConfig:
    """Configuration for a workflow."""
    name: str                               # e.g., "git_push", "blog_publish"
    skills: List[Dict[str, Any]] = field(default_factory=list)  # List of skill configs
    
    # Each skill config is a dict:
    # {
    #     "name": "auth_validator",
    #     "input": {"branch": "main", "operation": "push"},
    #     "continue_on_failure": False,  # Stop if this skill fails?
    #     "timeout_seconds": 30,
    # }
