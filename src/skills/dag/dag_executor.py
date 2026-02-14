"""
dag_executor.py (Phase 3) - DAG execution engine

Executes skills in topological order with:
- Retry-3-strikes pattern (fail after 3 attempts, then STOP)
- Cascade-stop semantics (dependents skip if dependency fails)
- Execution tracking and audit trails
- Dev/Prod mode differentiation
"""

import time
import logging
from typing import Any, Dict, List, Optional

from .skill_dag import SkillDAG
from .execution_models import (
    ExecutionMode,
    ExecutionContext,
    ExecutionStatus,
    AuditTrail,
    DAGExecutionResult,
    SkillResult,
    RetryConfig
)


class DAGExecutor:
    """
    Executes skill DAG with resilience and audit trail.
    
    Behavior:
    1. Execute skills in topological order
    2. For each skill: retry up to 3 times on failure
    3. After 3 failures: STOP and skip all dependents (cascade-stop)
    4. Track all execution details in audit trail
    5. Return comprehensive execution result
    
    Usage:
        executor = DAGExecutor(dag, mode=ExecutionMode.PROD)
        executor.register_config_resolver(config_resolver)
        executor.register_external_api_selector(skill_name, api_selector)
        result = executor.execute()
        
        if result.is_successful():
            print("DAG executed successfully")
        else:
            print(f"Failed skills: {result.failed_skills}")
    """
    
    # Class-level logger
    logger = logging.getLogger(__name__)
    
    def __init__(
        self,
        dag: SkillDAG,
        mode: ExecutionMode = ExecutionMode.PROD,
        retry_config: Optional[RetryConfig] = None
    ):
        """
        Initialize executor.
        
        Args:
            dag: SkillDAG to execute
            mode: ExecutionMode.DEV or ExecutionMode.PROD
            retry_config: Retry configuration (default: 3 retries exponential backoff)
        """
        self.dag = dag
        self.mode = mode
        self.retry_config = retry_config or RetryConfig()
        self._execution_contexts: Dict[str, ExecutionContext] = {}
        self._execution_result: Optional[DAGExecutionResult] = None
        self._failed_skills: set[str] = set()
        self._skipped_skills: set[str] = set()
        self._start_time: Optional[float] = None
    
    def execute(
        self,
        inputs: Optional[Dict[str, Any]] = None,
        timeout_seconds: Optional[float] = None
    ) -> DAGExecutionResult:
        """
        Execute the DAG.
        
        Args:
            inputs: Global inputs for all skills (can be overridden per-skill)
            timeout_seconds: Max execution time (not enforced per-skill yet)
        
        Returns:
            DAGExecutionResult with all execution details
        """
        self._start_time = time.time()
        self._execution_result = DAGExecutionResult(status=ExecutionStatus.RUNNING, mode=self.mode)
        
        if self.mode == ExecutionMode.DEV:
            print(f"[EXECUTOR] Starting DAG execution in {self.mode.value.upper()} mode")
            print(f"[EXECUTOR] DAG: {self.dag}")
        
        try:
            # Ensure execution result is initialized
            assert self._execution_result is not None, "Execution result not initialized"
            
            # Get execution order
            execution_order = self.dag.topological_sort()
            
            if self.mode == ExecutionMode.DEV:
                print(f"[EXECUTOR] Execution order: {execution_order}")
            
            # Execute each skill in order
            for skill_name in execution_order:
                # Check if should skip (cascade-stop)
                if skill_name in self._skipped_skills:
                    self._mark_skipped(skill_name, "Skipped due to dependency failure")
                    continue
                
                # Execute with retry logic
                self._execute_skill_with_retry(skill_name, inputs or {})
            
            # Set final status
            if len(self._failed_skills) == 0:
                self._execution_result.status = ExecutionStatus.COMPLETED
            else:
                self._execution_result.status = ExecutionStatus.FAILED
        
        except Exception as e:
            self._execution_result.error_message = str(e)
            self._execution_result.status = ExecutionStatus.FAILED
            self.logger.error(f"DAG execution failed: {e}", exc_info=True)
        
        finally:
            # Finalize
            self._finalize_execution()
        
        return self._execution_result
    
    def _execute_skill_with_retry(self, skill_name: str, global_inputs: Dict[str, Any]) -> None:
        """
        Execute skill with retry-3-strikes pattern.
        
        Args:
            skill_name: Skill to execute
            global_inputs: Global inputs for skill
        """
        node = self.dag.get_node(skill_name)
        
        attempt = 0
        last_error = None
        
        if self.mode == ExecutionMode.DEV:
            print(f"\n[EXECUTOR] Executing: {skill_name}")
        
        while attempt < self.retry_config.max_retries:
            try:
                # Create execution context
                context = ExecutionContext(
                    skill_name=skill_name,
                    skill_version=node.skill.version,
                    skill_entry_point=getattr(node.skill, '_entry_point', ''),
                    inputs=self._resolve_inputs(skill_name, global_inputs),
                    execution_mode=self.mode,
                    retry_config=self.retry_config
                )
                
                self._execution_contexts[skill_name] = context
                
                # Execute skill
                start = time.time()
                
                if self.mode == ExecutionMode.DEV:
                    print(f"  [ATTEMPT {attempt + 1}/{self.retry_config.max_retries}]")
                
                result = node.skill.execute(context)
                elapsed_ms = int((time.time() - start) * 1000)
                
                # Handle result
                if result.status == ExecutionStatus.COMPLETED:
                    # Success!
                    skill_result = SkillResult(
                        skill_name=skill_name,
                        skill_version=result.skill_version,
                        status=ExecutionStatus.COMPLETED,
                        output=result.output,
                        retry_count=attempt,
                        execution_time_ms=elapsed_ms,
                        audit_trail=context.audit_trail.to_dict() if context.audit_trail else None
                    )
                    
                    self._execution_result.add_skill_result(skill_result)
                    
                    if self.mode == ExecutionMode.DEV:
                        print(f"  [OK] Execution completed ({elapsed_ms}ms)")
                    
                    return  # Success!
                
                else:
                    # Skill execution failed
                    last_error = result.error
                    attempt += 1
                    
                    if self.mode == ExecutionMode.DEV:
                        print(f"  [FAIL] {result.error}")
                    
                    if attempt < self.retry_config.max_retries:
                        # Retry with backoff
                        delay = self.retry_config.calculate_delay(attempt - 1)
                        if self.mode == ExecutionMode.DEV:
                            print(f"  [RETRY] Waiting {delay:.1f}s before retry {attempt + 1}...")
                        time.sleep(delay)
            
            except Exception as e:
                last_error = str(e)
                attempt += 1
                
                if self.mode == ExecutionMode.DEV:
                    print(f"  [EXCEPTION] {last_error}")
                
                if attempt < self.retry_config.max_retries:
                    delay = self.retry_config.calculate_delay(attempt - 1)
                    if self.mode == ExecutionMode.DEV:
                        print(f"  [RETRY] Waiting {delay:.1f}s before retry {attempt + 1}...")
                    time.sleep(delay)
        
        # All retries exhausted - STOP and cascade
        if self.mode == ExecutionMode.DEV:
            print(f"  [STOP] Failed after {self.retry_config.max_retries} attempts")
        
        self._failed_skills.add(skill_name)
        
        # Add failed result
        skill_result = SkillResult(
            skill_name=skill_name,
            skill_version=node.skill.version,
            status=ExecutionStatus.FAILED,
            error=last_error or "Unknown error",
            retry_count=attempt
        )
        self._execution_result.add_skill_result(skill_result)
        
        # Cascade-stop: mark all dependents as skipped
        dependents = self.dag.get_all_dependents(skill_name)
        for dependent in dependents:
            self._mark_skipped(dependent, f"Skipped due to {skill_name} failure")
    
    def _resolve_inputs(self, skill_name: str, global_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve inputs for skill.
        
        Combines:
        1. Global inputs
        2. Outputs from upstream skills (via input_mapping)
        3. Config overrides
        
        Args:
            skill_name: Target skill
            global_inputs: Global inputs
        
        Returns:
            Resolved inputs dictionary
        """
        node = self.dag.get_node(skill_name)
        inputs = global_inputs.copy()
        
        # Get outputs from dependencies
        for dep in self.dag.get_dependencies(skill_name):
            if dep in self._execution_contexts:
                context = self._execution_contexts[dep]
                
                # Apply input mapping if exists
                if node.input_mapping:
                    for src_key, dst_key in node.input_mapping.items():
                        if src_key in context.outputs:
                            inputs[dst_key] = context.outputs[src_key]
                else:
                    # No mapping - add all outputs with prefix
                    for key, value in context.outputs.items():
                        inputs[f"{dep}_{key}"] = value
        
        # Apply config overrides as inputs
        inputs.update(node.config_overrides)
        
        return inputs
    
    def _mark_skipped(self, skill_name: str, reason: str) -> None:
        """Mark skill as skipped and add result."""
        self._skipped_skills.add(skill_name)
        node = self.dag.get_node(skill_name)
        
        skill_result = SkillResult(
            skill_name=skill_name,
            skill_version=node.skill.version,
            status=ExecutionStatus.SKIPPED,
            error=reason
        )
        self._execution_result.add_skill_result(skill_result)
    
    def _finalize_execution(self) -> None:
        """Finalize execution and calculate metrics."""
        if self._start_time:
            elapsed_ms = int((time.time() - self._start_time) * 1000)
            self._execution_result.total_execution_time_ms = elapsed_ms
        
        if self.mode == ExecutionMode.DEV:
            print(f"\n[EXECUTOR] Execution complete")
            print(f"  Status: {self._execution_result.status.value}")
            print(f"  Completed: {len(self._execution_result.skill_results) - len(self._failed_skills) - len(self._skipped_skills)}")
            print(f"  Failed: {len(self._failed_skills)}")
            print(f"  Skipped: {len(self._skipped_skills)}")
            print(f"  Total time: {self._execution_result.total_execution_time_ms}ms")
    
    def get_audit_trails(self) -> Dict[str, Dict[str, Any]]:
        """Get all audit trails from execution."""
        return {
            skill_name: context.audit_trail.to_dict()
            for skill_name, context in self._execution_contexts.items()
            if context.audit_trail
        }
    
    def export_execution_summary(self) -> Dict[str, Any]:
        """Export execution summary for logging/analysis."""
        return {
            "status": self._execution_result.status.value,
            "mode": self._execution_result.mode.value,
            "total_time_ms": self._execution_result.total_execution_time_ms,
            "skills_count": len(self.dag.nodes),
            "completed_count": sum(
                1 for r in self._execution_result.skill_results
                if r.status == ExecutionStatus.COMPLETED
            ),
            "failed_count": len(self._failed_skills),
            "skipped_count": len(self._skipped_skills),
            "failed_skills": list(self._failed_skills),
            "skipped_skills": list(self._skipped_skills)
        }
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<DAGExecutor mode={self.mode.value} dag={self.dag}>"
