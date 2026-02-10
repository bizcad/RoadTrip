"""Tests for skill_orchestrator.py."""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from src.skills.skill_orchestrator import SkillOrchestrator
from src.skills.skill_orchestrator_models import (
    OrchestrationResult,
    SkillStatus,
    WorkflowConfig,
)


@pytest.fixture
def orchestrator(tmp_path):
    """Create orchestrator with temporary log file."""
    log_file = str(tmp_path / "telemetry.jsonl")
    return SkillOrchestrator(log_file=log_file)


@pytest.fixture
def mock_auth_skill():
    """Mock auth validator skill."""
    def validate(branch="main", operation="push", **kwargs):
        return {
            "status": "valid",
            "is_authorized": True,
            "username": "test_user",
        }
    return validate


@pytest.fixture
def mock_message_skill():
    """Mock commit message skill."""
    def generate(files=None, **kwargs):
        return {
            "message": "feat: test commit",
            "confidence": 0.9,
        }
    return generate


@pytest.fixture
def workflow_config():
    """Create a simple workflow config."""
    return WorkflowConfig(
        name="test_workflow",
        skills=[
            {
                "name": "auth_validator",
                "input": {"branch": "main"},
                "continue_on_failure": False,
            },
            {
                "name": "commit_message",
                "input": {"files": ["test.py"]},
                "continue_on_failure": False,
            },
        ],
    )


class TestSkillOrchestratorRegistration:
    """Skill registration."""
    
    def test_register_skill(self, orchestrator, mock_auth_skill):
        """Register a skill."""
        orchestrator.register_skill("auth_validator", mock_auth_skill)
        
        assert "auth_validator" in orchestrator.skill_registry
        assert orchestrator.skill_registry["auth_validator"] == mock_auth_skill
    
    def test_register_multiple_skills(self, orchestrator, mock_auth_skill, mock_message_skill):
        """Register multiple skills."""
        orchestrator.register_skill("auth_validator", mock_auth_skill)
        orchestrator.register_skill("commit_message", mock_message_skill)
        
        assert len(orchestrator.skill_registry) >= 2


class TestSkillOrchestratorExecution:
    """Workflow execution."""
    
    def test_execute_simple_workflow(self, orchestrator, mock_auth_skill, mock_message_skill, workflow_config):
        """Execute a simple two-skill workflow."""
        orchestrator.register_skill("auth_validator", mock_auth_skill)
        orchestrator.register_skill("commit_message", mock_message_skill)
        
        result = orchestrator.execute(workflow_config)
        
        assert result.workflow_name == "test_workflow"
        assert result.status == SkillStatus.SUCCESS
        assert result.final_decision == "APPROVED"
        assert len(result.skill_records) == 2
    
    def test_execute_creates_unique_workflow_id(self, orchestrator, mock_auth_skill, workflow_config):
        """Each execution gets a unique workflow ID."""
        orchestrator.register_skill("auth_validator", mock_auth_skill)
        workflow_config.skills = workflow_config.skills[:1]  # Just auth
        
        result1 = orchestrator.execute(workflow_config)
        result2 = orchestrator.execute(workflow_config)
        
        assert result1.workflow_id != result2.workflow_id
        assert result1.workflow_id.startswith("test_workflow-")


class TestSkillOrchestratorSkillFailure:
    """Handling skill failures."""
    
    def test_skill_execution_failure_aborts_workflow(self, orchestrator, workflow_config):
        """If a skill fails and continue_on_failure=False, abort."""
        def failing_skill(**kwargs):
            raise ValueError("Test error")
        
        orchestrator.register_skill("auth_validator", failing_skill)
        orchestrator.register_skill("commit_message", MagicMock())
        
        result = orchestrator.execute(workflow_config)
        
        assert result.status == SkillStatus.FAILED
        assert result.final_decision == "FAILED"
        assert result.should_rollback == True
        assert len(result.skill_records) >= 1  # At least the failing skill
    
    def test_skill_output_passed_to_next_skill(self, orchestrator, workflow_config):
        """Output of one skill becomes input to next."""
        def skill1(**kwargs):
            return {"value": 42}
        
        captured_input = {}
        def skill2(**kwargs):
            captured_input.update(kwargs)
            return {"result": "ok"}
        
        orchestrator.register_skill("auth_validator", skill1)
        orchestrator.register_skill("commit_message", skill2)
        
        result = orchestrator.execute(workflow_config)
        
        # skill2 should have received value=42 from skill1
        assert captured_input.get("value") == 42


class TestSkillOrchestratorInputMerging:
    """Input/output chaining between skills."""
    
    def test_workflow_input_merged_with_skill_input(self, orchestrator):
        """Workflow-level input merged with skill-specific input."""
        captured_input = {}
        def mock_skill(**kwargs):
            captured_input.update(kwargs)
            return {}
        
        orchestrator.register_skill("test_skill", mock_skill)
        
        config = WorkflowConfig(
            name="test",
            skills=[
                {
                    "name": "test_skill",
                    "input": {"param1": "value1"},
                }
            ],
        )
        
        orchestrator.execute(config)
        
        assert captured_input.get("param1") == "value1"


class TestSkillOrchestratorRecords:
    """Execution records."""
    
    def test_skill_record_has_timing(self, orchestrator, mock_auth_skill):
        """Skill records include execution timing."""
        orchestrator.register_skill("auth_validator", mock_auth_skill)
        
        config = WorkflowConfig(
            name="test",
            skills=[{"name": "auth_validator", "input": {}}],
        )
        
        result = orchestrator.execute(config)
        record = result.skill_records[0]
        
        assert record.execution_time_ms > 0
        assert record.completed_at is not None
    
    def test_skill_record_has_input_output(self, orchestrator, mock_auth_skill):
        """Skill records capture input and output."""
        orchestrator.register_skill("auth_validator", mock_auth_skill)
        
        config = WorkflowConfig(
            name="test",
            skills=[
                {
                    "name": "auth_validator",
                    "input": {"branch": "main", "operation": "push"},
                }
            ],
        )
        
        result = orchestrator.execute(config)
        record = result.skill_records[0]
        
        assert record.input_data == {"branch": "main", "operation": "push"}
        assert record.output_data == {
            "status": "valid",
            "is_authorized": True,
            "username": "test_user",
        }


class TestSkillOrchestratorErrorHandling:
    """Error handling and reporting."""
    
    def test_unknown_skill_returns_error(self, orchestrator):
        """Reference to unknown skill returns error."""
        config = WorkflowConfig(
            name="test",
            skills=[
                {
                    "name": "unknown_skill",
                    "input": {},
                }
            ],
        )
        
        result = orchestrator.execute(config)
        
        assert result.status == SkillStatus.FAILED
        assert "Unknown skill" in result.error_message
    
    def test_skill_exception_captured(self, orchestrator):
        """Exceptions in skills are captured."""
        def failing_skill(**kwargs):
            raise RuntimeError("Skill crashed")
        
        orchestrator.register_skill("bad_skill", failing_skill)
        
        config = WorkflowConfig(
            name="test",
            skills=[{"name": "bad_skill", "input": {}}],
        )
        
        result = orchestrator.execute(config)
        
        record = result.skill_records[0]
        assert record.status == SkillStatus.FAILED
        assert record.error_code == "RuntimeError"
        assert "Skill crashed" in record.error_message


class TestSkillOrchestratorDataclass:
    """Handling dataclass returns from skills."""
    
    def test_dataclass_result_converted_to_dict(self, orchestrator):
        """Dataclass results from skills are converted to dict."""
        from dataclasses import dataclass
        
        @dataclass
        class SkillOutput:
            status: str
            value: int
        
        def skill_returning_dataclass(**kwargs):
            return SkillOutput(status="ok", value=42)
        
        orchestrator.register_skill("test_skill", skill_returning_dataclass)
        
        config = WorkflowConfig(
            name="test",
            skills=[{"name": "test_skill", "input": {}}],
        )
        
        result = orchestrator.execute(config)
        record = result.skill_records[0]
        
        assert isinstance(record.output_data, dict)
        assert record.output_data["status"] == "ok"
        assert record.output_data["value"] == 42


class TestSkillOrchestratorWorkflowStatus:
    """Overall workflow status."""
    
    def test_workflow_success_status(self, orchestrator, mock_auth_skill, mock_message_skill):
        """All skills succeed → workflow success."""
        orchestrator.register_skill("auth_validator", mock_auth_skill)
        orchestrator.register_skill("commit_message", mock_message_skill)
        
        config = WorkflowConfig(
            name="test",
            skills=[
                {"name": "auth_validator", "input": {}},
                {"name": "commit_message", "input": {}},
            ],
        )
        
        result = orchestrator.execute(config)
        
        assert result.success() == True
        assert result.failed() == False
    
    def test_workflow_failure_status(self, orchestrator):
        """Any skill fails → workflow failure."""
        def failing_skill(**kwargs):
            raise Exception("Failed")
        
        orchestrator.register_skill("bad_skill", failing_skill)
        
        config = WorkflowConfig(
            name="test",
            skills=[{"name": "bad_skill", "input": {}}],
        )
        
        result = orchestrator.execute(config)
        
        assert result.success() == False
        assert result.failed() == True


class TestSkillOrchestratorTelemetry:
    """Telemetry logging during execution."""
    
    def test_execution_logged_to_telemetry(self, tmp_path, mock_auth_skill):
        """Executions are logged to telemetry file."""
        log_file = str(tmp_path / "telemetry.jsonl")
        orchestrator = SkillOrchestrator(log_file=log_file)
        orchestrator.register_skill("auth_validator", mock_auth_skill)
        
        config = WorkflowConfig(
            name="test",
            skills=[{"name": "auth_validator", "input": {}}],
        )
        
        orchestrator.execute(config)
        
        # Check that telemetry was written
        with open(log_file, 'r') as f:
            content = f.read()
        
        assert len(content) > 0  # Something was logged
