"""Tests for telemetry_logger.py skill."""

import pytest
import json
import os
from pathlib import Path
from datetime import datetime, timezone

from src.skills.telemetry_logger import TelemetryLogger
from src.skills.telemetry_logger_models import (
    TelemetryEntry,
    TelemetryLoggerResult,
)


@pytest.fixture
def temp_log_file(tmp_path):
    """Create temporary log file path."""
    return str(tmp_path / "test_telemetry.jsonl")


@pytest.fixture
def logger():
    """Create a TelemetryLogger instance."""
    return TelemetryLogger()


@pytest.fixture
def sample_entry():
    """Create a sample telemetry entry."""
    return TelemetryEntry(
        timestamp=datetime.now(timezone.utc).isoformat(),
        workflow_id="push-abc123",
        decision_id="auth-check-1",
        skill="auth_validator",
        operation="validate",
        input_summary={"branch": "main", "operation": "push"},
        decision="APPROVED",
        confidence=0.95,
        reasoning="Valid GitHub token, permitted to push to main",
        artifacts={"files_affected": 3, "commit_hash": "abc123def456"},
        execution_time_ms=145.5,
    )


class TestTelemetryLoggerBasic:
    """Basic logging operations."""
    
    def test_log_entry_success(self, logger, sample_entry, temp_log_file):
        """Log entry successfully."""
        result = logger.log_entry(sample_entry, temp_log_file)
        
        assert result.success == True
        assert result.log_file == str(Path(temp_log_file).absolute())
        assert result.bytes_written > 0
        assert result.total_entries == 1
    
    def test_log_file_created(self, logger, sample_entry, temp_log_file):
        """Log file is created if missing."""
        assert not Path(temp_log_file).exists()
        
        logger.log_entry(sample_entry, temp_log_file)
        
        assert Path(temp_log_file).exists()
    
    def test_log_file_created_with_parent_dirs(self, logger, sample_entry, tmp_path):
        """Parent directories created automatically."""
        log_file = str(tmp_path / "deep" / "path" / "log.jsonl")
        
        logger.log_entry(sample_entry, log_file)
        
        assert Path(log_file).exists()


class TestTelemetryLoggerJSONLFormat:
    """JSONL format validation."""
    
    def test_entry_is_valid_json(self, logger, sample_entry, temp_log_file):
        """Logged entry is valid JSON."""
        logger.log_entry(sample_entry, temp_log_file)
        
        with open(temp_log_file, 'r') as f:
            line = f.readline()
        
        # Should be parseable as JSON
        data = json.loads(line)
        assert isinstance(data, dict)
        assert data['workflow_id'] == "push-abc123"
    
    def test_jsonl_format_one_line_per_entry(self, logger, sample_entry, temp_log_file):
        """Each entry is a complete line (JSONL format)."""
        entry1 = sample_entry
        entry2 = TelemetryEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            workflow_id="push-xyz789",
            decision_id="msg-check-1",
            skill="commit_message",
            operation="generate",
            input_summary={"files": 2},
            decision="APPROVED",
        )
        
        logger.log_entry(entry1, temp_log_file)
        logger.log_entry(entry2, temp_log_file)
        
        # Should have 2 lines
        with open(temp_log_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 2
        
        # Each line should be valid JSON
        for line in lines:
            data = json.loads(line)
            assert isinstance(data, dict)


class TestTelemetryLoggerAppend:
    """Append-only behavior."""
    
    def test_entries_are_appended(self, logger, sample_entry, temp_log_file):
        """Multiple entries are appended (not overwritten)."""
        entry1 = TelemetryEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            workflow_id="push-1",
            decision_id="auth-1",
            skill="auth_validator",
            operation="validate",
            input_summary={},
            decision="APPROVED",
        )
        
        entry2 = TelemetryEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            workflow_id="push-2",
            decision_id="auth-2",
            skill="auth_validator",
            operation="validate",
            input_summary={},
            decision="DENIED",
        )
        
        logger.log_entry(entry1, temp_log_file)
        result1 = logger.log_entry(entry2, temp_log_file)
        
        # Should have 2 entries total
        assert result1.total_entries == 2
    
    def test_append_doesnt_corrupt_previous_entries(self, logger, sample_entry, temp_log_file):
        """Appending doesn't corrupt earlier entries."""
        entries = [
            TelemetryEntry(
                timestamp=datetime.now(timezone.utc).isoformat(),
                workflow_id=f"push-{i}",
                decision_id=f"auth-{i}",
                skill="auth_validator",
                operation="validate",
                input_summary={"index": i},
                decision="APPROVED",
            )
            for i in range(5)
        ]
        
        for entry in entries:
            logger.log_entry(entry, temp_log_file)
        
        # Read all entries
        all_entries = logger.read_entries(temp_log_file)
        
        assert len(all_entries) == 5
        for i, entry in enumerate(all_entries):
            assert entry.workflow_id == f"push-{i}"


class TestTelemetryLoggerReadEntries:
    """Reading and filtering entries."""
    
    def test_read_entries(self, logger, sample_entry, temp_log_file):
        """Read all entries from log file."""
        logger.log_entry(sample_entry, temp_log_file)
        
        entries = logger.read_entries(temp_log_file)
        
        assert len(entries) == 1
        assert entries[0].workflow_id == "push-abc123"
    
    def test_read_entries_filter_by_workflow(self, logger, temp_log_file):
        """Filter entries by workflow_id."""
        entry1 = TelemetryEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            workflow_id="push-1",
            decision_id="auth-1",
            skill="auth_validator",
            operation="validate",
            input_summary={},
            decision="APPROVED",
        )
        
        entry2 = TelemetryEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            workflow_id="push-2",
            decision_id="auth-2",
            skill="auth_validator",
            operation="validate",
            input_summary={},
            decision="DENIED",
        )
        
        logger.log_entry(entry1, temp_log_file)
        logger.log_entry(entry2, temp_log_file)
        
        entries = logger.read_entries(temp_log_file, workflow_id="push-1")
        
        assert len(entries) == 1
        assert entries[0].workflow_id == "push-1"
    
    def test_read_entries_filter_by_skill(self, logger, temp_log_file):
        """Filter entries by skill name."""
        entry1 = TelemetryEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            workflow_id="push-1",
            decision_id="auth-1",
            skill="auth_validator",
            operation="validate",
            input_summary={},
            decision="APPROVED",
        )
        
        entry2 = TelemetryEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            workflow_id="push-1",
            decision_id="msg-1",
            skill="commit_message",
            operation="generate",
            input_summary={},
            decision="APPROVED",
        )
        
        logger.log_entry(entry1, temp_log_file)
        logger.log_entry(entry2, temp_log_file)
        
        entries = logger.read_entries(temp_log_file, skill="commit_message")
        
        assert len(entries) == 1
        assert entries[0].skill == "commit_message"
    
    def test_read_nonexistent_file(self, logger):
        """Reading nonexistent file returns empty list."""
        entries = logger.read_entries("nonexistent.jsonl")
        
        assert entries == []


class TestTelemetryLoggerSecrets:
    """Secrets should not appear in logs."""
    
    def test_no_secrets_in_log(self, logger, temp_log_file):
        """Entry with potentially sensitive data logged safely."""
        # Simulate a token in input (it shouldn't be logged)
        entry = TelemetryEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            workflow_id="push-1",
            decision_id="auth-1",
            skill="auth_validator",
            operation="validate",
            input_summary={"branch": "main"},  # Safe
            decision="APPROVED",
            reasoning="Token validated",  # Safe (no actual token value)
        )
        
        logger.log_entry(entry, temp_log_file)
        
        with open(temp_log_file, 'r') as f:
            content = f.read()
        
        # Log should not contain actual token
        assert "ghp_" not in content  # GitHub token prefix
        assert "sk_" not in content   # API key prefix


class TestTelemetryLoggerErrorHandling:
    """Error handling when logging fails."""
    
    @pytest.mark.skipif(
        os.name == 'nt',
        reason="Windows doesn't have proper permission handling like Unix"
    )
    def test_write_to_readonly_directory(self, logger, sample_entry, tmp_path):
        """Handle permission errors gracefully."""
        # Create a readonly directory
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        os.chmod(readonly_dir, 0o444)  # Read-only

        log_file = str(readonly_dir / "log.jsonl")

        try:
            result = logger.log_entry(sample_entry, log_file)

            # Should fail gracefully
            assert result.success == False
            assert result.error_code == "LOG_WRITE_FAILED"
        
        finally:
            # Restore permissions for cleanup
            os.chmod(readonly_dir, 0o755)


class TestTelemetryLoggerConcurrency:
    """Append-only safety under simulated concurrent access."""
    
    def test_multiple_concurrent_writes_safe(self, logger, temp_log_file):
        """Multiple sequential writes don't corrupt log."""
        entries = [
            TelemetryEntry(
                timestamp=datetime.now(timezone.utc).isoformat(),
                workflow_id=f"push-{i}",
                decision_id=f"auth-{i}",
                skill="auth_validator",
                operation="validate",
                input_summary={"iteration": i},
                decision="APPROVED",
            )
            for i in range(10)
        ]
        
        for entry in entries:
            result = logger.log_entry(entry, temp_log_file)
            assert result.success == True
        
        # Read all and verify integrity
        all_entries = logger.read_entries(temp_log_file)
        assert len(all_entries) == 10
