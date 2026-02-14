"""
execution_models.py (Phase 3) - Execution models for DAG execution

Defines retry logic, execution modes, and audit trail structures.
- RetryConfig: 3-strikes pattern (baseball rules)
- ExecutionMode: Dev (debug visibility) vs Prod (fluid piping)
- AuditTrail: Execution timeline, outputs, errors
- ExecutionContext: Skill execution state
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, ConfigDict


class ExecutionMode(str, Enum):
    """Execution mode for DAG."""
    DEV = "dev"      # Show intermediate outputs for debugging
    PROD = "prod"    # Fluid piping, no intermediate visibility


class RetryStrategy(str, Enum):
    """Retry strategy for failed skills."""
    EXPONENTIAL = "exponential"  # 2^n backoff
    LINEAR = "linear"            # n * base_delay
    FIXED = "fixed"              # constant delay


@dataclass
class RetryConfig:
    """
    Retry configuration (3-strikes pattern).
    
    Attributes:
        max_retries: Maximum number of retry attempts (default 3, baseball rules)
        strategy: Backoff strategy (exponential, linear, fixed)
        base_delay: Base delay in seconds between retries
        max_delay: Maximum delay in seconds (for exponential backoff)
    """
    max_retries: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    base_delay: float = 1.0
    max_delay: float = 30.0
    enable_logging: bool = True
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt (0-indexed)."""
        if self.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.base_delay * (2 ** attempt)
        elif self.strategy == RetryStrategy.LINEAR:
            delay = self.base_delay * (attempt + 1)
        else:  # FIXED
            delay = self.base_delay
        
        return min(delay, self.max_delay)


class ExecutionStatus(str, Enum):
    """Execution status of a skill."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"
    SKIPPED = "skipped"


@dataclass
class ExecutionEvent:
    """Single execution event in audit trail."""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    event_type: str = ""  # 'start', 'end', 'retry', 'error', 'output'
    message: str = ""
    data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "message": self.message,
            "data": self.data
        }


@dataclass
class AuditTrail:
    """
    Audit trail for skill execution.
    
    Tracks execution timeline, intermediate outputs, and errors.
    """
    skill_name: str
    skill_version: str
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None
    status: ExecutionStatus = ExecutionStatus.PENDING
    events: List[ExecutionEvent] = field(default_factory=list)
    final_output: Optional[Any] = None
    errors: List[str] = field(default_factory=list)
    retry_count: int = 0
    
    def add_event(
        self,
        event_type: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add execution event to trail."""
        event = ExecutionEvent(
            event_type=event_type,
            message=message,
            data=data
        )
        self.events.append(event)
    
    def add_error(self, error_msg: str) -> None:
        """Add error to trail."""
        self.errors.append(error_msg)
        self.add_event("error", error_msg)
    
    def set_final_output(self, output: Any) -> None:
        """Set final output."""
        self.final_output = output
        self.add_event("output", "Execution completed", {"output_type": str(type(output))})
    
    def set_complete(self) -> None:
        """Mark execution as complete."""
        self.end_time = datetime.now().isoformat()
        self.status = ExecutionStatus.COMPLETED
    
    def set_failed(self) -> None:
        """Mark execution as failed."""
        self.end_time = datetime.now().isoformat()
        self.status = ExecutionStatus.FAILED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "skill_name": self.skill_name,
            "skill_version": self.skill_version,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "status": self.status.value,
            "retry_count": self.retry_count,
            "events": [e.to_dict() for e in self.events],
            "final_output_type": str(type(self.final_output)) if self.final_output else None,
            "error_count": len(self.errors),
            "errors": self.errors
        }


@dataclass
class ExecutionContext:
    """
    Execution context for a skill in the DAG.
    
    Tracks inputs, outputs, errors, and audit trail during execution.
    """
    skill_name: str
    skill_version: str
    skill_entry_point: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    audit_trail: Optional[AuditTrail] = None
    execution_mode: ExecutionMode = ExecutionMode.PROD
    retry_config: Optional[RetryConfig] = None
    
    def __post_init__(self):
        """Initialize audit trail."""
        if self.audit_trail is None:
            self.audit_trail = AuditTrail(
                skill_name=self.skill_name,
                skill_version=self.skill_version
            )
        if self.retry_config is None:
            self.retry_config = RetryConfig()
    
    def log_debug(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Log debug message (shown in dev mode)."""
        if self.execution_mode == ExecutionMode.DEV:
            print(f"[DEBUG] {message}")
            if data:
                print(f"  Data: {data}")
        self.audit_trail.add_event("debug", message, data)
    
    def log_info(self, message: str) -> None:
        """Log info message."""
        self.audit_trail.add_event("info", message)
    
    def log_error(self, message: str) -> None:
        """Log error message."""
        self.audit_trail.add_error(message)
    
    def set_output(self, key: str, value: Any) -> None:
        """Set output value."""
        self.outputs[key] = value
        if self.execution_mode == ExecutionMode.DEV:
            print(f"[OUTPUT] {key} = {type(value).__name__}")
    
    def get_input(self, key: str, default: Any = None) -> Any:
        """Get input value."""
        return self.inputs.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "skill_name": self.skill_name,
            "skill_version": self.skill_version,
            "skill_entry_point": self.skill_entry_point,
            "execution_mode": self.execution_mode.value,
            "inputs": {k: str(v)[:50] for k, v in self.inputs.items()},  # Truncate for display
            "outputs": {k: str(v)[:50] for k, v in self.outputs.items()},
            "audit_trail": self.audit_trail.to_dict() if self.audit_trail else None
        }


class SkillResult(BaseModel):
    """Result from skill execution."""
    skill_name: str
    skill_version: str
    status: ExecutionStatus
    output: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0
    execution_time_ms: int = 0
    audit_trail: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(use_enum_values=True)


class DAGExecutionResult(BaseModel):
    """Result from DAG execution."""
    status: ExecutionStatus
    mode: ExecutionMode
    skill_results: List[SkillResult] = Field(default_factory=list)
    total_execution_time_ms: int = 0
    failed_skills: List[str] = Field(default_factory=list)
    skipped_skills: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None
    
    model_config = ConfigDict(use_enum_values=True)
    
    def add_skill_result(self, result: SkillResult) -> None:
        """Add skill result to execution result."""
        self.skill_results.append(result)
        
        if result.status == ExecutionStatus.FAILED:
            self.failed_skills.append(result.skill_name)
        elif result.status == ExecutionStatus.SKIPPED:
            self.skipped_skills.append(result.skill_name)
    
    def is_successful(self) -> bool:
        """Check if execution was successful."""
        return self.status == ExecutionStatus.COMPLETED and len(self.failed_skills) == 0
