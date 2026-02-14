"""
test_phase_3_dag.py - Unit tests for Phase 3 DAG components

Tests execution_models, skill_base, config_resolver, skill_dag, dag_builder, 
skill_loader, and dag_executor.
"""

import pytest
import time
from pathlib import Path
from datetime import datetime

from src.skills.dag import (
    ExecutionMode,
    ExecutionStatus,
    RetryConfig,
    RetryStrategy,
    AuditTrail,
    ExecutionContext,
    SkillResult,
    DAGExecutionResult,
    SkillBase,
    SkillCapability,
    ExternalAPIType,
    APISelector,
    SkillDAG,
    DAGBuilder,
    DAGExecutor,
    ConfigResolver,
    SkillConfigResolver,
    ConfigSource,
    SkillLoader,
    SkillLoaderError,
    InterfaceValidationError
)


# ============================================================================
# Fixtures
# ============================================================================

class MockSkill(SkillBase):
    """Mock skill for testing."""
    
    def __init__(self, name: str = "mock_skill", version: str = "1.0.0"):
        super().__init__(name, version)
        self.executed = False
        self.execution_count = 0
    
    def description(self) -> str:
        return "Mock skill for testing"
    
    def validate_inputs(self, inputs) -> tuple[bool, str | None]:
        return True, None
    
    def execute(self, context: ExecutionContext) -> SkillResult:
        self.executed = True
        self.execution_count += 1
        context.set_output("result", f"Output from {self.name}")
        return SkillResult(
            skill_name=self.name,
            skill_version=self.version,
            status=ExecutionStatus.COMPLETED,
            output=f"Output from {self.name}"
        )


class FailingSkill(SkillBase):
    """Skill that fails."""
    
    def __init__(self, name: str = "failing_skill"):
        super().__init__(name, "1.0.0")
        self.attempt_count = 0
    
    def description(self) -> str:
        return "Failing skill"
    
    def validate_inputs(self, inputs) -> tuple[bool, str | None]:
        return True, None
    
    def execute(self, context: ExecutionContext) -> SkillResult:
        self.attempt_count += 1
        return SkillResult(
            skill_name=self.name,
            skill_version=self.version,
            status=ExecutionStatus.FAILED,
            error=f"Intentional failure (attempt {self.attempt_count})"
        )


class ConditionalSkill(SkillBase):
    """Skill that succeeds after N failures."""
    
    def __init__(self, name: str = "conditional_skill", fail_times: int = 1):
        super().__init__(name, "1.0.0")
        self.fail_times = fail_times
        self.attempt_count = 0
    
    def description(self) -> str:
        return "Conditional skill"
    
    def validate_inputs(self, inputs) -> tuple[bool, str | None]:
        return True, None
    
    def execute(self, context: ExecutionContext) -> SkillResult:
        self.attempt_count += 1
        
        if self.attempt_count <= self.fail_times:
            return SkillResult(
                skill_name=self.name,
                skill_version=self.version,
                status=ExecutionStatus.FAILED,
                error=f"Temporary failure (attempt {self.attempt_count})"
            )
        else:
            context.set_output("success", True)
            return SkillResult(
                skill_name=self.name,
                skill_version=self.version,
                status=ExecutionStatus.COMPLETED,
                output=f"Success on attempt {self.attempt_count}"
            )


@pytest.fixture
def mock_skill():
    return MockSkill()


@pytest.fixture
def failing_skill():
    return FailingSkill()


@pytest.fixture
def conditional_skill():
    return ConditionalSkill(fail_times=1)


# ============================================================================
# Test Execution Models
# ============================================================================

class TestExecutionModels:
    """Test execution_models.py"""
    
    def test_retry_config_default(self):
        """Test RetryConfig defaults."""
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.strategy == RetryStrategy.EXPONENTIAL
        assert config.base_delay == 1.0
    
    def test_retry_config_calculate_delay_exponential(self):
        """Test exponential backoff calculation."""
        config = RetryConfig(strategy=RetryStrategy.EXPONENTIAL, base_delay=1.0)
        assert config.calculate_delay(0) == 1.0
        assert config.calculate_delay(1) == 2.0
        assert config.calculate_delay(2) == 4.0
    
    def test_retry_config_calculate_delay_linear(self):
        """Test linear backoff calculation."""
        config = RetryConfig(strategy=RetryStrategy.LINEAR, base_delay=1.0)
        assert config.calculate_delay(0) == 1.0
        assert config.calculate_delay(1) == 2.0
        assert config.calculate_delay(2) == 3.0
    
    def test_execution_context_creation(self, mock_skill):
        """Test ExecutionContext creation."""
        context = ExecutionContext(
            skill_name="test",
            skill_version="1.0.0",
            skill_entry_point="test.py",
            inputs={"key": "value"}
        )
        assert context.skill_name == "test"
        assert context.inputs == {"key": "value"}
        assert context.execution_mode == ExecutionMode.PROD
    
    def test_execution_context_set_output(self, mock_skill):
        """Test output setting."""
        context = ExecutionContext(
            skill_name="test",
            skill_version="1.0.0",
            skill_entry_point="test.py"
        )
        context.set_output("key", "value")
        assert context.outputs["key"] == "value"
    
    def test_audit_trail_creation(self):
        """Test AuditTrail creation."""
        audit = AuditTrail("test", "1.0.0")
        assert audit.skill_name == "test"
        assert audit.status == ExecutionStatus.PENDING
        assert len(audit.events) == 0
    
    def test_dag_execution_result_is_successful(self):
        """Test DAGExecutionResult success check."""
        result = DAGExecutionResult(
            status=ExecutionStatus.COMPLETED,
            mode=ExecutionMode.PROD
        )
        assert result.is_successful()
        
        result.failed_skills.append("test")
        assert not result.is_successful()


# ============================================================================
# Test Skill Base
# ============================================================================

class TestSkillBase:
    """Test skill_base.py"""
    
    def test_mock_skill_creation(self, mock_skill):
        """Test mock skill creation."""
        assert mock_skill.name == "mock_skill"
        assert mock_skill.version == "1.0.0"
        assert mock_skill.description() == "Mock skill for testing"
    
    def test_skill_execute(self, mock_skill):
        """Test skill execution."""
        context = ExecutionContext(
            skill_name="mock_skill",
            skill_version="1.0.0",
            skill_entry_point="mock.py"
        )
        
        result = mock_skill.execute(context)
        assert result.status == ExecutionStatus.COMPLETED
        assert mock_skill.executed
    
    def test_api_selector_register_provider(self):
        """Test APISelector provider registration."""
        selector = APISelector(ExternalAPIType.GITHUB)
        
        class MockProvider:
            pass
        
        provider = MockProvider()
        selector.register_provider("mock", provider)
        
        assert "mock" in selector.list_providers()
        assert selector.select_provider("mock") == provider
    
    def test_api_selector_active_provider(self):
        """Test active provider selection."""
        selector = APISelector(ExternalAPIType.GITHUB)
        
        class P1:
            pass
        class P2:
            pass
        
        selector.register_provider("p1", P1())
        selector.register_provider("p2", P2())
        selector.select_provider("p1")
        
        assert selector.active_provider == "p1"


# ============================================================================
# Test Config Resolver
# ============================================================================

class TestConfigResolver:
    """Test config_resolver.py"""
    
    def test_hardcoded_config(self):
        """Test hardcoded configuration."""
        resolver = ConfigResolver()
        resolver.register_hardcoded("key1", "value1")
        
        assert resolver.get("key1") == "value1"
        assert resolver.get_source("key1") == ConfigSource.HARDCODED
    
    def test_config_priority(self):
        """Test configuration priority (hardcoded > env > default)."""
        resolver = ConfigResolver()
        
        resolver.register_hardcoded("key", "hardcoded")
        resolver.register_defaults_batch({"key": "default"})
        
        # Hardcoded should win
        assert resolver.get("key") == "hardcoded"
    
    def test_skill_config_resolver(self):
        """Test SkillConfigResolver."""
        resolver = SkillConfigResolver()
        resolver.register_skill_hardcoded("github", "token", "abc123")
        
        token = resolver.get_skill_config("github", "token")
        assert token == "abc123"
    
    def test_missing_config_required(self):
        """Test required config key missing."""
        resolver = ConfigResolver()
        
        with pytest.raises(KeyError):
            resolver.get("missing", required=True)
    
    def test_missing_config_with_default(self):
        """Test default value for missing config."""
        resolver = ConfigResolver()
        
        value = resolver.get("missing", default="default_value")
        assert value == "default_value"


# ============================================================================
# Test Skill DAG
# ============================================================================

class TestSkillDAG:
    """Test skill_dag.py"""
    
    def test_dag_add_node(self, mock_skill):
        """Test adding node to DAG."""
        dag = SkillDAG()
        dag.add_node(mock_skill)
        
        assert "mock_skill" in dag.nodes
        assert dag.nodes["mock_skill"].skill == mock_skill
    
    def test_dag_add_edge(self, mock_skill):
        """Test adding edge to DAG."""
        dag = SkillDAG()
        skill1 = MockSkill("skill1")
        skill2 = MockSkill("skill2")
        
        dag.add_node(skill1)
        dag.add_node(skill2)
        dag.add_edge("skill1", "skill2")
        
        assert "skill2" in dag.get_dependents("skill1")
        assert "skill1" in dag.get_dependencies("skill2")
    
    def test_dag_topological_sort(self):
        """Test topological sort."""
        dag = SkillDAG()
        s1 = MockSkill("s1")
        s2 = MockSkill("s2")
        s3 = MockSkill("s3")
        
        dag.add_node(s1)
        dag.add_node(s2)
        dag.add_node(s3)
        
        dag.add_edge("s1", "s2")
        dag.add_edge("s2", "s3")
        
        order = dag.topological_sort()
        assert order == ["s1", "s2", "s3"]
    
    def test_dag_cycle_detection(self):
        """Test cycle detection."""
        dag = SkillDAG()
        s1 = MockSkill("s1")
        s2 = MockSkill("s2")
        
        dag.add_node(s1)
        dag.add_node(s2)
        
        dag.add_edge("s1", "s2")
        
        # Adding reverse edge should fail
        with pytest.raises(Exception):
            dag.add_edge("s2", "s1")
    
    def test_dag_validate(self):
        """Test DAG validation."""
        dag = SkillDAG()
        s1 = MockSkill("s1")
        s2 = MockSkill("s2")
        
        dag.add_node(s1)
        dag.add_node(s2)
        dag.add_edge("s1", "s2")
        
        is_valid, errors = dag.validate()
        assert is_valid
        assert len(errors) == 0


# ============================================================================
# Test DAG Builder
# ============================================================================

class TestDAGBuilder:
    """Test dag_builder.py"""
    
    def test_builder_fluent_api(self):
        """Test builder fluent API."""
        s1 = MockSkill("s1")
        s2 = MockSkill("s2")
        
        builder = DAGBuilder(ExecutionMode.PROD)
        builder.add_skill(s1).add_skill(s2).add_dependency("s1", "s2")
        
        dag = builder.build()
        assert len(dag.nodes) == 2
        assert len(dag.edges) == 1
    
    def test_builder_dev_mode(self):
        """Test builder dev mode."""
        builder = DAGBuilder().dev()
        assert builder.mode == ExecutionMode.DEV
    
    def test_builder_retry_config(self):
        """Test builder retry config."""
        config = RetryConfig(max_retries=5)
        builder = DAGBuilder().set_retry_config(config)
        
        assert builder.retry_config.max_retries == 5
    
    def test_builder_configure_skill(self):
        """Test skill configuration in builder."""
        s1 = MockSkill("s1")
        
        builder = DAGBuilder()
        builder.add_skill(s1).configure_skill("s1", {"timeout": 30})
        
        dag = builder.build()
        node = dag.get_node("s1")
        assert node.config_overrides["timeout"] == 30
    
    def test_builder_debug_info(self):
        """Test builder debug info."""
        s1 = MockSkill("s1")
        s2 = MockSkill("s2")
        
        builder = DAGBuilder()
        builder.add_skill(s1).add_skill(s2).add_dependency("s1", "s2")
        
        info = builder.debug_info()
        assert info["skills_count"] == 2
        assert info["edges_count"] == 1


# ============================================================================
# Test DAG Executor
# ============================================================================

class TestDAGExecutor:
    """Test dag_executor.py"""
    
    def test_executor_single_skill(self):
        """Test executor with single skill."""
        dag = SkillDAG()
        skill = MockSkill()
        dag.add_node(skill)
        
        executor = DAGExecutor(dag, mode=ExecutionMode.PROD)
        result = executor.execute()
        
        assert result.status == ExecutionStatus.COMPLETED
        assert len(result.skill_results) == 1
        assert result.skill_results[0].status == ExecutionStatus.COMPLETED
    
    def test_executor_retry_on_failure(self):
        """Test executor retries on failure."""
        dag = SkillDAG()
        skill = ConditionalSkill("test", fail_times=1)  # Fails once, then succeeds
        dag.add_node(skill)
        
        executor = DAGExecutor(dag)
        result = executor.execute()
        
        assert result.status == ExecutionStatus.COMPLETED
        assert skill.attempt_count == 2  # Failed once, then succeeded
    
    def test_executor_stops_after_3_strikes(self):
        """Test executor stops after 3 failed retry attempts."""
        dag = SkillDAG()
        skill = FailingSkill()
        dag.add_node(skill)
        
        executor = DAGExecutor(dag)
        result = executor.execute()
        
        assert result.status == ExecutionStatus.FAILED
        assert len(result.failed_skills) == 1
        assert skill.attempt_count == 3  # 3 attempts maximum
    
    def test_executor_cascade_stop(self):
        """Test cascade-stop on dependency failure."""
        dag = SkillDAG()
        failing = FailingSkill("failing")
        dependent = MockSkill("dependent")
        
        dag.add_node(failing)
        dag.add_node(dependent)
        dag.add_edge("failing", "dependent")
        
        executor = DAGExecutor(dag)
        result = executor.execute()
        
        assert result.status == ExecutionStatus.FAILED
        assert "dependent" in result.skipped_skills
        assert dependent.executed == False
    
    def test_executor_dev_mode_output(self):
        """Test executor dev mode produces output."""
        dag = SkillDAG()
        skill = MockSkill()
        dag.add_node(skill)
        
        executor = DAGExecutor(dag, mode=ExecutionMode.DEV)
        result = executor.execute()
        
        assert result.mode == ExecutionMode.DEV
        assert result.status == ExecutionStatus.COMPLETED


# ============================================================================
# Test Skill Loader
# ============================================================================

class TestSkillLoader:
    """Test skill_loader.py"""
    
    def test_loader_validate_mock_skill(self):
        """Test loader validation of mock skill."""
        loader = SkillLoader()
        skill = MockSkill()
        
        errors = loader.validate(skill)
        assert len(errors) == 0
    
    def test_loader_validate_missing_description(self):
        """Test loader detects missing description."""
        class BadSkill(SkillBase):
            def description(self):
                return ""  # Empty
            
            def validate_inputs(self, inputs):
                return True, None
            
            def execute(self, context):
                return SkillResult(
                    skill_name="bad",
                    skill_version="1.0.0",
                    status=ExecutionStatus.COMPLETED
                )
        
        loader = SkillLoader()
        skill = BadSkill("bad", "1.0.0")
        
        errors = loader.validate(skill)
        assert len(errors) > 0


# ============================================================================
# Integration Tests
# ============================================================================

class TestPhase3Integration:
    """Integration tests across Phase 3 components."""
    
    def test_full_dag_workflow(self):
        """Test complete DAG workflow."""
        # Build DAG
        s1 = MockSkill("s1")
        s2 = MockSkill("s2")
        s3 = MockSkill("s3")
        
        builder = DAGBuilder(ExecutionMode.PROD)
        builder.add_skill(s1).add_skill(s2).add_skill(s3)
        builder.add_dependency("s1", "s2")
        builder.add_dependency("s2", "s3")
        
        dag = builder.build()
        
        # Execute
        executor = DAGExecutor(dag)
        result = executor.execute()
        
        # Verify
        assert result.status == ExecutionStatus.COMPLETED
        assert len(result.failed_skills) == 0
        assert all(s.executed for s in [s1, s2, s3])
    
    def test_config_and_execution(self):
        """Test config resolution with execution."""
        resolver = SkillConfigResolver()
        resolver.register_skill_hardcoded("test", "value", "configured")
        
        dag = SkillDAG()
        skill = MockSkill()
        dag.add_node(skill)
        
        executor = DAGExecutor(dag)
        result = executor.execute()
        
        assert result.status == ExecutionStatus.COMPLETED


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
