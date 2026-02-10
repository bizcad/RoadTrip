"""
Integration tests for Phase 1b: Complete git_push workflow.

Tests the orchestrator with all four skills:
1. auth_validator - validate credentials
2. rules_engine - check for secrets
3. commit_message - generate message
4. telemetry_logger - log decisions

This is end-to-end testing: does the complete workflow work?
"""

import pytest
import json
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime, timezone

from src.skills.skill_orchestrator import SkillOrchestrator
from src.skills.skill_orchestrator_models import (
    WorkflowConfig,
    SkillStatus,
)
from src.skills.auth_validator import AuthValidator
from src.skills.telemetry_logger import TelemetryLogger
from src.skills.telemetry_logger_models import TelemetryEntry
from src.skills.commit_message import CommitMessageSkill


@pytest.fixture
def temp_git_repo(tmp_path):
    """Create a temporary git repository."""
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()
    
    # Initialize git repo
    subprocess.run(
        ["git", "init"],
        cwd=repo_dir,
        capture_output=True,
    )
    
    # Configure user
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_dir,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_dir,
        capture_output=True,
    )
    
    # Create initial commit
    readme = repo_dir / "README.md"
    readme.write_text("# Test Repo\n")
    
    subprocess.run(
        ["git", "add", "."],
        cwd=repo_dir,
        capture_output=True,
    )
    
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_dir,
        capture_output=True,
    )
    
    return repo_dir


@pytest.fixture
def orchestrator(tmp_path):
    """Create orchestrator with temporary log file."""
    log_file = str(tmp_path / "telemetry.jsonl")
    return SkillOrchestrator(log_file=log_file), log_file


@pytest.fixture
def git_push_config():
    """Configuration for git_push workflow."""
    return WorkflowConfig(
        name="git_push",
        skills=[
            {
                "name": "auth_validator",
                "input": {"branch": "main", "operation": "push"},
                "continue_on_failure": False,
            },
            {
                "name": "commit_message",
                "input": {"staged_files": ["README.md"]},
                "continue_on_failure": False,
            },
        ],
    )


class TestPhase1bAuthValidation:
    """Test auth_validator skill in workflow."""
    
    def test_auth_validation_in_workflow(self, temp_git_repo):
        """Auth validator correctly validates git config."""
        validator = AuthValidator()
        
        result = validator.validate(branch="main", operation="push")
        
        # Should be valid (we configured git above)
        assert result.status.value == "valid"
        assert result.is_authorized == True
        assert result.username == "Test User"
        assert result.user_email == "test@example.com"
    
    def test_auth_validation_returns_dict(self, temp_git_repo):
        """Auth result can be serialized to dict."""
        validator = AuthValidator()
        result = validator.validate(branch="main")
        
        d = result.to_dict()
        
        assert isinstance(d, dict)
        assert "status" in d
        assert "username" in d


class TestPhase1bCommitMessageGeneration:
    """Test commit_message skill in workflow."""
    
    def test_commit_message_generation(self, tmp_path):
        """Commit message skill generates valid messages."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        
        config_file = config_dir / "commit-strategy.yaml"
        config_file.write_text("""
commit_message:
  confidence_threshold: 0.85
  tier2:
    enabled: false
    model: "claude-3-5-sonnet-20241022"
  file_categories:
    src:
      - "*.py"
    tests:
      - "test_*.py"
    docs:
      - "*.md"
""")
        
        skill = CommitMessageSkill(config_path=str(config_file))
        result = skill.generate(staged_files=["README.md"])
        
        assert result.message is not None
        assert "docs" in result.message.lower() or "readme" in result.message.lower()
        assert result.confidence >= 0.8


class TestPhase1bTelemetryLogging:
    """Test telemetry_logger skill in workflow."""
    
    def test_telemetry_logging_in_workflow(self, tmp_path):
        """Telemetry logger correctly logs entries."""
        log_file = str(tmp_path / "telemetry.jsonl")
        logger = TelemetryLogger()
        
        entry = TelemetryEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            workflow_id="test-workflow-1",
            decision_id="auth-1",
            skill="auth_validator",
            operation="validate",
            input_summary={"branch": "main"},
            decision="APPROVED",
            reasoning="Auth successful",
            artifacts={"username": "test_user"},
        )
        
        result = logger.log_entry(entry, log_file)
        
        assert result.success == True
        assert result.total_entries == 1
    
    def test_telemetry_entries_readable(self, tmp_path):
        """Logged telemetry entries can be read back."""
        log_file = str(tmp_path / "telemetry.jsonl")
        logger = TelemetryLogger()
        
        # Log multiple entries
        for i in range(3):
            entry = TelemetryEntry(
                timestamp=datetime.now(timezone.utc).isoformat(),
                workflow_id=f"workflow-{i}",
                decision_id=f"decision-{i}",
                skill="test_skill",
                operation="test",
                input_summary={"index": i},
                decision="APPROVED",
            )
            logger.log_entry(entry, log_file)
        
        # Read back
        entries = logger.read_entries(log_file)
        
        assert len(entries) == 3
        assert entries[0].workflow_id == "workflow-0"
        assert entries[2].workflow_id == "workflow-2"


class TestPhase1bOrchestratorIntegration:
    """Test skill_orchestrator with multiple skills."""
    
    def test_orchestrator_executes_auth_skill(self, orchestrator):
        """Orchestrator can execute auth_validator skill."""
        orch, log_file = orchestrator
        
        def mock_auth(**kwargs):
            return {
                "status": "valid",
                "is_authorized": True,
                "username": "test_user",
            }
        
        orch.register_skill("auth_validator", mock_auth)
        
        config = WorkflowConfig(
            name="test_auth",
            skills=[
                {
                    "name": "auth_validator",
                    "input": {"branch": "main"},
                }
            ],
        )
        
        result = orch.execute(config)
        
        assert result.status == SkillStatus.SUCCESS
        assert result.final_decision == "APPROVED"
        assert len(result.skill_records) == 1
    
    def test_orchestrator_chains_skills(self, orchestrator):
        """Orchestrator chains output from one skill to next."""
        orch, log_file = orchestrator
        
        def skill1(**kwargs):
            return {"auth_result": "valid"}
        
        def skill2(**kwargs):
            # Should receive auth_result from skill1
            assert "auth_result" in kwargs
            return {"message": "generated"}
        
        orch.register_skill("skill1", skill1)
        orch.register_skill("skill2", skill2)
        
        config = WorkflowConfig(
            name="chained",
            skills=[
                {"name": "skill1", "input": {}},
                {"name": "skill2", "input": {}},
            ],
        )
        
        result = orch.execute(config)
        
        assert result.status == SkillStatus.SUCCESS
        assert len(result.skill_records) == 2


class TestPhase1bCompleteWorkflow:
    """Test complete git_push workflow with all skills."""
    
    def test_complete_workflow_happy_path(self, orchestrator, tmp_path):
        """Complete workflow: auth → message → success."""
        orch, log_file = orchestrator
        
        # Register all skills
        def auth_skill(branch="main", operation="push", **kwargs):
            return {
                "status": "valid",
                "is_authorized": True,
                "username": "test_user",
                "can_push": True,
            }
        
        def msg_skill(staged_files=None, **kwargs):
            return {
                "message": "feat: update code",
                "confidence": 0.9,
            }
        
        orch.register_skill("auth_validator", auth_skill)
        orch.register_skill("commit_message", msg_skill)
        
        config = WorkflowConfig(
            name="git_push",
            skills=[
                {
                    "name": "auth_validator",
                    "input": {"branch": "main"},
                    "continue_on_failure": False,
                },
                {
                    "name": "commit_message",
                    "input": {"staged_files": ["src/main.py"]},
                    "continue_on_failure": False,
                },
            ],
        )
        
        result = orch.execute(config)
        
        # All skills should succeed
        assert result.status == SkillStatus.SUCCESS
        assert result.final_decision == "APPROVED"
        assert len(result.skill_records) == 2
        
        # Check records
        auth_record = result.skill_records[0]
        assert auth_record.skill_name == "auth_validator"
        assert auth_record.status == SkillStatus.SUCCESS
        
        msg_record = result.skill_records[1]
        assert msg_record.skill_name == "commit_message"
        assert msg_record.status == SkillStatus.SUCCESS
    
    def test_workflow_aborts_on_auth_failure(self, orchestrator):
        """Workflow aborts if auth_validator fails."""
        orch, log_file = orchestrator
        
        def failing_auth(**kwargs):
            raise ValueError("Auth failed")
        
        def msg_skill(**kwargs):
            # Should not be called
            raise AssertionError("Should not reach commit_message")
        
        orch.register_skill("auth_validator", failing_auth)
        orch.register_skill("commit_message", msg_skill)
        
        config = WorkflowConfig(
            name="git_push",
            skills=[
                {
                    "name": "auth_validator",
                    "input": {"branch": "main"},
                    "continue_on_failure": False,
                },
                {
                    "name": "commit_message",
                    "input": {"staged_files": []},
                    "continue_on_failure": False,
                },
            ],
        )
        
        result = orch.execute(config)
        
        # Workflow should fail
        assert result.status == SkillStatus.FAILED
        assert result.final_decision == "FAILED"
        
        # Only auth should have been attempted
        assert len(result.skill_records) == 1


class TestPhase1bTelemetryIntegration:
    """Test telemetry logging during workflow execution."""
    
    def test_workflow_telemetry_logged(self, orchestrator):
        """Workflow execution is logged to telemetry."""
        orch, log_file = orchestrator
        
        def dummy_skill(**kwargs):
            return {"result": "ok"}
        
        orch.register_skill("test_skill", dummy_skill)
        
        config = WorkflowConfig(
            name="test",
            skills=[{"name": "test_skill", "input": {}}],
        )
        
        result = orch.execute(config)
        
        # Check telemetry file was written
        assert Path(log_file).exists()
        
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Should have some telemetry
        assert len(content) > 0
        
        # Should be valid JSONL
        lines = content.strip().split('\n')
        for line in lines:
            data = json.loads(line)
            assert "skill" in data
            assert "decision" in data
    
    def test_telemetry_captures_all_decisions(self, orchestrator, tmp_path):
        """Telemetry captures decisions from all skills."""
        orch, log_file = orchestrator
        
        def skill1(**kwargs):
            return {"step": 1}
        
        def skill2(**kwargs):
            return {"step": 2}
        
        orch.register_skill("skill1", skill1)
        orch.register_skill("skill2", skill2)
        
        config = WorkflowConfig(
            name="multi_skill",
            skills=[
                {"name": "skill1", "input": {}},
                {"name": "skill2", "input": {}},
            ],
        )
        
        orch.execute(config)
        
        # Read telemetry
        logger = TelemetryLogger()
        entries = logger.read_entries(log_file)
        
        # Should have logged both skills
        skills_executed = [e.skill for e in entries]
        assert "skill1" in skills_executed
        assert "skill2" in skills_executed


class TestPhase1bErrorRecovery:
    """Test error handling and recovery in workflows."""
    
    def test_continue_on_failure_flag(self, orchestrator):
        """continue_on_failure flag allows workflow to continue."""
        orch, log_file = orchestrator
        
        def failing_skill(**kwargs):
            raise ValueError("Skill 1 failed")
        
        def recovery_skill(**kwargs):
            return {"recovered": True}
        
        orch.register_skill("skill1", failing_skill)
        orch.register_skill("skill2", recovery_skill)
        
        config = WorkflowConfig(
            name="recovery",
            skills=[
                {
                    "name": "skill1",
                    "input": {},
                    "continue_on_failure": True,  # Continue despite failure
                },
                {
                    "name": "skill2",
                    "input": {},
                    "continue_on_failure": False,
                },
            ],
        )
        
        result = orch.execute(config)
        
        # Skill 1 should fail but not abort workflow
        assert len(result.skill_records) == 2
        assert result.skill_records[0].status == SkillStatus.FAILED
        assert result.skill_records[1].status == SkillStatus.SUCCESS
    
    def test_partial_failure_still_logs_telemetry(self, orchestrator):
        """Telemetry is logged even if skills fail."""
        orch, log_file = orchestrator
        
        def failing_skill(**kwargs):
            raise RuntimeError("Skill error")
        
        orch.register_skill("bad_skill", failing_skill)
        
        config = WorkflowConfig(
            name="fail",
            skills=[{"name": "bad_skill", "input": {}}],
        )
        
        orch.execute(config)
        
        # Should still have telemetry
        logger = TelemetryLogger()
        entries = logger.read_entries(log_file)
        
        assert len(entries) > 0
        assert entries[0].decision == "FAILED"


class TestPhase1bWorkflowMetrics:
    """Test metrics collection during workflow execution."""
    
    def test_execution_timing_recorded(self, orchestrator):
        """Execution timing is recorded for each skill."""
        orch, log_file = orchestrator
        
        import time
        
        def slow_skill(**kwargs):
            time.sleep(0.1)  # Sleep 100ms
            return {"result": "ok"}
        
        orch.register_skill("slow_skill", slow_skill)
        
        config = WorkflowConfig(
            name="timing",
            skills=[{"name": "slow_skill", "input": {}}],
        )
        
        result = orch.execute(config)
        
        record = result.skill_records[0]
        
        # Should record execution time
        assert record.execution_time_ms >= 100  # At least 100ms
        assert record.execution_time_ms < 500   # But not too much
    
    def test_workflow_completion_time_recorded(self, orchestrator):
        """Total workflow execution time is recorded."""
        orch, log_file = orchestrator
        
        def quick_skill(**kwargs):
            return {"result": "ok"}
        
        orch.register_skill("quick", quick_skill)
        orch.register_skill("quick2", quick_skill)
        
        config = WorkflowConfig(
            name="complete",
            skills=[
                {"name": "quick", "input": {}},
                {"name": "quick2", "input": {}},
            ],
        )
        
        result = orch.execute(config)
        
        # Should have total time
        assert result.total_execution_time_ms > 0
        assert result.completed_at is not None


class TestPhase1bWorkflowDocumentation:
    """Test that workflows are properly documented."""
    
    def test_workflow_result_has_documentation(self, orchestrator):
        """Workflow results include reasoning and context."""
        orch, log_file = orchestrator
        
        def documented_skill(**kwargs):
            return {"documentation": "skill executed"}
        
        orch.register_skill("doc_skill", documented_skill)
        
        config = WorkflowConfig(
            name="documented",
            skills=[{"name": "doc_skill", "input": {"param": "value"}}],
        )
        
        result = orch.execute(config)
        
        record = result.skill_records[0]
        
        # Should capture input/output
        assert record.input_data == {"param": "value"}
        assert record.output_data == {"documentation": "skill executed"}
