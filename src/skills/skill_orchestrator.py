#!/usr/bin/env python3
"""
skill_orchestrator.py

Generic orchestrator that chains multiple skills into workflows.
Implements the Interface pattern: same calling convention, different skill chains.

Orchestration flow:
1. Load workflow config (which skills, in order)
2. Execute each skill in sequence
3. Check result of each skill
4. If skill fails: decide to continue or abort
5. Pass output of one skill to input of next
6. Log telemetry for each decision
7. Return final result

Usage:
    from src.skills.skill_orchestrator import SkillOrchestrator
    orchestrator = SkillOrchestrator()
    result = orchestrator.execute(workflow_config)
"""

import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Callable, Optional

from .skill_orchestrator_models import (
    OrchestrationResult,
    SkillExecutionRecord,
    SkillStatus,
    WorkflowConfig,
)
from .telemetry_logger import TelemetryLogger
from .telemetry_logger_models import TelemetryEntry


class SkillOrchestrator:
    """Orchestrates execution of skill chains."""

    def __init__(self, log_file: str = "data/telemetry.jsonl"):
        """
        Initialize orchestrator.
        
        Args:
            log_file: Path to telemetry log file
        """
        self.log_file = log_file
        self.logger = TelemetryLogger()
        self.skill_registry: Dict[str, Callable] = {}
        self._register_default_skills()
    
    def _register_default_skills(self):
        """Register built-in skills."""
        # These will be loaded dynamically from src/skills/*.py
        # For now, just register the skills we've created
        pass
    
    def register_skill(self, name: str, skill_callable: Callable):
        """
        Register a skill.
        
        Args:
            name: Skill name (e.g., "auth_validator")
            skill_callable: Callable that executes the skill
        """
        self.skill_registry[name] = skill_callable
    
    def execute(self, workflow_config: WorkflowConfig) -> OrchestrationResult:
        """
        Execute a workflow.
        
        Args:
            workflow_config: WorkflowConfig with skill list
        
        Returns:
            OrchestrationResult with full execution record
        """
        
        workflow_id = f"{workflow_config.name}-{str(uuid.uuid4())[:8]}"
        result = OrchestrationResult(
            workflow_id=workflow_id,
            workflow_name=workflow_config.name,
            status=SkillStatus.IN_PROGRESS,
        )
        
        start_time = time.time()
        current_input = {}
        
        # Execute each skill in sequence
        for i, skill_config in enumerate(workflow_config.skills):
            skill_name = skill_config.get("name")
            skill_input = skill_config.get("input", {})
            continue_on_failure = skill_config.get("continue_on_failure", False)
            
            # Merge previous output with current input
            merged_input = {**current_input, **skill_input}
            
            # Execute skill
            skill_record = self._execute_skill(
                skill_name=skill_name,
                skill_input=merged_input,
                workflow_id=workflow_id,
            )
            
            result.skill_records.append(skill_record)
            
            # Log to telemetry
            self._log_skill_execution(skill_record, workflow_id, skill_name)
            
            # Check if skill succeeded
            if skill_record.status == SkillStatus.FAILED:
                if not continue_on_failure:
                    # Abort workflow
                    result.status = SkillStatus.FAILED
                    result.error_code = skill_record.error_code
                    result.error_message = f"Workflow aborted at skill '{skill_name}': {skill_record.error_message}"
                    result.should_rollback = True
                    break
                # else: continue despite failure
            
            # Pass output to next skill
            if skill_record.status == SkillStatus.SUCCESS:
                current_input = skill_record.output_data
        
        # Determine final status
        if result.status != SkillStatus.FAILED:
            # Check if all skills succeeded
            failed_skills = [s for s in result.skill_records if s.status == SkillStatus.FAILED]
            if failed_skills:
                result.status = SkillStatus.FAILED
                result.final_decision = "FAILED"
            else:
                result.status = SkillStatus.SUCCESS
                result.final_decision = "APPROVED"
                result.final_output = current_input
        else:
            # Workflow was already marked as failed
            result.final_decision = "FAILED"
        
        # Record completion time
        end_time = time.time()
        result.total_execution_time_ms = (end_time - start_time) * 1000
        result.completed_at = datetime.now(timezone.utc).isoformat()
        
        return result
    
    def _execute_skill(
        self,
        skill_name: str,
        skill_input: Dict[str, Any],
        workflow_id: str,
    ) -> SkillExecutionRecord:
        """
        Execute a single skill.
        
        Args:
            skill_name: Name of skill to execute
            skill_input: Input data for skill
            workflow_id: Workflow ID for context
        
        Returns:
            SkillExecutionRecord with result
        """
        
        record = SkillExecutionRecord(
            skill_name=skill_name,
            status=SkillStatus.PENDING,
            input_data=skill_input,
            output_data={},
        )
        
        start_time = time.time()
        
        try:
            # Look up skill in registry
            if skill_name not in self.skill_registry:
                raise ValueError(f"Unknown skill: {skill_name}")
            
            skill_callable = self.skill_registry[skill_name]
            
            # Execute skill (must return dict)
            output = skill_callable(**skill_input)
            
            # Handle both dataclass and dict returns
            if hasattr(output, '__dataclass_fields__'):
                import dataclasses
                output = dataclasses.asdict(output)
            
            record.status = SkillStatus.SUCCESS
            record.output_data = output if isinstance(output, dict) else {"result": output}
        
        except Exception as e:
            record.status = SkillStatus.FAILED
            record.error_code = type(e).__name__
            record.error_message = str(e)
        
        finally:
            end_time = time.time()
            record.execution_time_ms = (end_time - start_time) * 1000
            record.completed_at = datetime.now(timezone.utc).isoformat()
        
        return record
    
    def _log_skill_execution(
        self,
        record: SkillExecutionRecord,
        workflow_id: str,
        skill_name: str,
    ):
        """Log skill execution to telemetry."""
        
        entry = TelemetryEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            workflow_id=workflow_id,
            decision_id=f"{skill_name}-{record.started_at}",
            skill=skill_name,
            operation="execute",
            input_summary=record.input_data,
            decision=record.status.value.upper(),
            reasoning=record.error_message or "Skill executed successfully",
            artifacts=record.output_data,
            execution_time_ms=record.execution_time_ms,
            error_code=record.error_code,
            error_message=record.error_message,
        )
        
        self.logger.log_entry(entry, self.log_file)
