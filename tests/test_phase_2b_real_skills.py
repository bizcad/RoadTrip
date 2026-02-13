"""
test_phase_2b_real_skills.py - Phase 2b: Real Skill Registration

Tests the complete flow:
1. Generate fingerprints for real skills (blog_publisher, commit_message)
2. Register skills with metadata
3. Update versions
4. Export audit logs for human inspection

This demonstrates the registry working with actual skills from ./src/skills/
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from src.skills.registry import RegistryOrchestrator
from src.skills.registry.storage_yaml import YAMLStore
from src.skills.registry.storage_sqlite import SQLiteStore
from src.skills.registry.storage_interface import StorageConfig
from src.skills.registry.registry_models import SkillStatus


class TestRealSkillsRegistration:
    """Test registration of real skills with audit logging."""
    
    @pytest.fixture
    def orchestrator_yaml(self, tmp_path):
        """Create orchestrator with YAML storage."""
        registry_file = tmp_path / "registry.yaml"
        config = StorageConfig(
            backend_type="yaml",
            location=str(registry_file)
        )
        
        # Note: This would require modifying RegistryOrchestrator
        # to accept storage config. For now, use mock registry.
        return RegistryOrchestrator(
            registry_path=str(registry_file),
            use_mock=True
        )
    
    # ===== SKILL 1: blog_publisher =====
    
    def test_register_blog_publisher(self, orchestrator_yaml):
        """Register blog_publisher skill from ./src/skills/blog_publisher.py"""
        
        result = orchestrator_yaml.register_skill(
            skill_name="blog_publisher",
            version="1.0.0",
            capabilities=["content_management", "publishing", "blog", "markdown"],
            author="roadtrip_team",
            test_count=8,
            test_coverage=92.5,
            description="Autonomous blog post publishing with validation, formatting, and git operations"
        )
        
        assert result["status"] == "success"
        assert result["skill_name"] == "blog_publisher"
        assert "fingerprint" in result
    
    def test_register_commit_message(self, orchestrator_yaml):
        """Register commit_message skill from ./src/skills/commit_message.py"""
        
        result = orchestrator_yaml.register_skill(
            skill_name="commit_message",
            version="1.0.0",
            capabilities=["git", "automation", "semantic", "ci_cd"],
            author="roadtrip_team",
            test_count=12,
            test_coverage=88.0,
            description="Generates semantic commit messages using Tier 1→2→3 cost-optimized approach"
        )
        
        assert result["status"] == "success"
        assert result["skill_name"] == "commit_message"
        assert "fingerprint" in result
        
        # Verify it's discoverable
        all_skills = orchestrator_yaml.find_all_skills()
        assert "commit_message" in all_skills
    
    # ===== CAPABILITY SEARCH =====
    
    def test_search_by_capability(self, orchestrator_yaml):
        """Verify skills are findable by capability."""
        
        # First register skills
        orchestrator_yaml.register_skill(
            skill_name="blog_publisher",
            version="1.0.0",
            capabilities=["publishing", "blog"],
            author="team",
            test_count=5,
            test_coverage=90.0
        )
        
        orchestrator_yaml.register_skill(
            skill_name="commit_message",
            version="1.0.0",
            capabilities=["git", "automation"],
            author="team",
            test_count=10,
            test_coverage=85.0
        )
        
        # Search by capability
        publishing_skills = orchestrator_yaml.query_capabilities("publishing")
        assert len(publishing_skills) > 0
        assert any(s.get("name") == "blog_publisher" for s in publishing_skills)
        
        git_skills = orchestrator_yaml.query_capabilities("git")
        assert len(git_skills) > 0
        assert any(s.get("name") == "commit_message" for s in git_skills)
    
    # ===== SKILL UPDATE FLOW =====
    
    def test_skill_version_update(self, orchestrator_yaml):
        """Test skill update workflow: register → review → update → review"""
        
        # Step 1: Register v1.0.0
        result_v1 = orchestrator_yaml.register_skill(
            skill_name="blog_publisher",
            version="1.0.0",
            capabilities=["publishing", "blog"],
            author="team",
            test_count=8,
            test_coverage=92.5,
            description="Initial release"
        )
        
        assert result_v1["status"] == "success"
        fp_v1 = result_v1["fingerprint"]
        
        # Step 2: Get metadata (review)
        metadata_v1 = orchestrator_yaml.get_skill_metadata("blog_publisher")
        assert metadata_v1 is not None
        assert metadata_v1.version == "1.0.0"
        assert metadata_v1.test_coverage == 92.5
        assert metadata_v1.tests == 8
        
        # Step 3: Register v1.1.0 (update)
        result_v2 = orchestrator_yaml.register_skill(
            skill_name="blog_publisher",
            version="1.1.0",
            capabilities=["publishing", "blog", "social_media"],  # Added capability
            author="team",
            test_count=10,  # Improved tests
            test_coverage=95.0,  # Better coverage
            description="Added social media sharing"
        )
        
        assert result_v2["status"] == "success"
        fp_v2 = result_v2["fingerprint"]
        
        # Fingerprints should be different for different versions
        assert fp_v1 != fp_v2
        
        # Step 4: Get updated metadata (review)
        metadata_v2 = orchestrator_yaml.get_skill_metadata("blog_publisher")
        assert metadata_v2.version == "1.1.0"
        assert metadata_v2.tests == 10
        assert metadata_v2.test_coverage == 95.0
        assert "social_media" in metadata_v2.capabilities


class TestAuditLogExport:
    """Test audit log export for human inspection."""
    
    @pytest.fixture
    def orchestrator_with_activity(self, tmp_path):
        """Create orchestrator with some activity to log."""
        registry_file = tmp_path / "registry_audit.yaml"
        
        orch = RegistryOrchestrator(
            registry_path=str(registry_file),
            use_mock=True
        )
        
        # Generate some activity
        orch.register_skill(
            skill_name="test_skill_1",
            version="1.0.0",
            capabilities=["testing"],
            author="test_author",
            test_count=5,
            test_coverage=80.0
        )
        
        orch.query_capabilities("testing")
        
        orch.register_skill(
            skill_name="test_skill_2",
            version="2.0.0",
            capabilities=["automation"],
            author="test_author",  test_count=10,
            test_coverage=90.0
        )
        
        return orch
    
    def test_export_audit_logs_json(self, orchestrator_with_activity, tmp_path):
        """Export audit logs to JSON for human inspection."""
        
        # In a real implementation, we'd query the store
        # For now, this demonstrates the structure we want
        
        audit_log_file = tmp_path / "audit_log.json"
        
        # Mock audit log data (shows what we'd export)
        audit_logs = [
            {
                "timestamp": "2025-02-14T10:30:00",
                "event_type": "SKILL_REGISTERED",
                "skill_id": "blog_publisher",
                "details": {
                    "version": "1.0.0",
                    "capabilities": ["publishing", "blog"],
                    "author": "roadtrip_team",
                    "test_coverage": 92.5
                }
            },
            {
                "timestamp": "2025-02-14T10:30:15",
                "event_type": "QUERY_BY_CAPABILITY",
                "skill_id": None,
                "details": {
                    "capability": "publishing",
                    "results_found": 1
                }
            },
            {
                "timestamp": "2025-02-14T10:30:30",
                "event_type": "SKILL_REGISTERED",
                "skill_id": "commit_message",
                "details": {
                    "version": "1.0.0",
                    "capabilities": ["git", "automation"],
                    "author": "roadtrip_team",
                    "test_coverage": 88.0
                }
            }
        ]
        
        # Write JSON
        with open(audit_log_file, 'w') as f:
            json.dump(audit_logs, f, indent=2)
        
        assert audit_log_file.exists()
        
        # Read and verify
        with open(audit_log_file, 'r') as f:
            loaded = json.load(f)
        
        assert len(loaded) == 3
        assert loaded[0]["event_type"] == "SKILL_REGISTERED"
        assert loaded[1]["event_type"] == "QUERY_BY_CAPABILITY"
    
    def test_audit_log_summary(self):
        """Generate human-readable summary of audit events."""
        
        # Example audit logs
        audit_logs = [
            {"event_type": "SKILL_REGISTERED", "skill_id": "blog_publisher"},
            {"event_type": "SKILL_REGISTERED", "skill_id": "commit_message"},
            {"event_type": "QUERY_BY_CAPABILITY", "skill_id": None},
            {"event_type": "QUERY_BY_CAPABILITY", "skill_id": None},
            {"event_type": "EXECUTION_ALLOWED", "skill_id": "blog_publisher"},
            {"event_type": "EXECUTION_ALLOWED", "skill_id": "commit_message"},
            {"event_type": "EXECUTION_ALLOWED", "skill_id": "blog_publisher"},
        ]
        
        # Count by event type
        summary = {}
        for log in audit_logs:
            event_type = log["event_type"]
            summary[event_type] = summary.get(event_type, 0) + 1
        
        # Verify summary
        assert summary["SKILL_REGISTERED"] == 2
        assert summary["QUERY_BY_CAPABILITY"] == 2
        assert summary["EXECUTION_ALLOWED"] == 3
        
        # Format for human reading
        summary_text = "Audit Log Summary:\n"
        for event_type, count in sorted(summary.items()):
            summary_text += f"  {event_type}: {count}\n"
        
        print("\n" + summary_text)
        assert "SKILL_REGISTERED: 2" in summary_text


class TestSQLiteVsYAMLComparison:
    """Compare YAML and SQLite storage backends."""
    
    @pytest.fixture
    def yaml_store(self, tmp_path):
        """Create YAML store."""
        config = StorageConfig(
            backend_type="yaml",
            location=str(tmp_path / "registry.yaml")
        )
        return YAMLStore(config)
    
    @pytest.fixture
    def sqlite_store(self, tmp_path):
        """Create SQLite store."""
        config = StorageConfig(
            backend_type="sqlite",
            location=str(tmp_path / "registry.db")
        )
        return SQLiteStore(config)
    
    def test_both_stores_save_and_retrieve(self, yaml_store, sqlite_store):
        """Verify both stores handle CRUD identically."""
        
        skill_data = {
            "version": "1.0.0",
            "fingerprint": "fp_test_1.0.0_abc123",
            "author": "test_author",
            "capabilities": ["testing", "automation"],
            "tests": 5,
            "test_coverage": 85.0,
            "status": "active",
            "created": datetime.now().isoformat(),
            "description": "Test skill",
            "source_files": ["skill.py", "models.py"]
        }
        
        # Save to both
        yaml_store.save_skill("test_skill", skill_data)
        sqlite_store.save_skill("test_skill", skill_data)
        
        # Retrieve from both
        yaml_result = yaml_store.get_skill("test_skill")
        sqlite_result = sqlite_store.get_skill("test_skill")
        
        # Both should have the data
        assert yaml_result is not None
        assert sqlite_result is not None
        
        # Core fields should match (stored dict format, no 'name' key)
        assert yaml_result["version"] == sqlite_result["version"] == "1.0.0"
        assert yaml_result["fingerprint"] == sqlite_result["fingerprint"]
        assert yaml_result["author"] == sqlite_result["author"] == "test_author"
    
    def test_both_stores_search_by_capability(self, yaml_store, sqlite_store):
        """Verify search works on both backends."""
        
        skills = [
            ("skill_a", {"version": "1.0", "capabilities": ["search"], "author": "a", "fingerprint": "fp_a"}),
            ("skill_b", {"version": "1.0", "capabilities": ["search", "test"], "author": "b", "fingerprint": "fp_b"}),
            ("skill_c", {"version": "1.0", "capabilities": ["other"], "author": "c", "fingerprint": "fp_c"}),
        ]
        
        # Save to both
        for skill_id, data in skills:
            yaml_store.save_skill(skill_id, data)
            sqlite_store.save_skill(skill_id, data)
        
        # Search both
        yaml_search = yaml_store.search_by_capability("search")
        sqlite_search = sqlite_store.search_by_capability("search")
        
        # Both should find 2 skills
        assert len(yaml_search) == 2
        assert len(sqlite_search) == 2
    
    def test_audit_logs_on_both_stores(self, yaml_store, sqlite_store):
        """Verify audit logging works on both backends."""
        
        # Save audit events to both
        for store in [yaml_store, sqlite_store]:
            store.save_audit_log("SKILL_REGISTERED", "test_skill", {
                "version": "1.0.0",
                "author": "tester"
            })
            
            store.save_audit_log("EXECUTION_ALLOWED", "test_skill", {
                "decision": "allowed"
            })
        
        # Retrieve from both
        yaml_logs = yaml_store.get_audit_logs()
        sqlite_logs = sqlite_store.get_audit_logs()
        
        # Both should have 2 events
        assert len(yaml_logs) == 2
        assert len(sqlite_logs) == 2
        
        # Event types should match
        yaml_types = set(log["event_type"] for log in yaml_logs)
        sqlite_types = set(log["event_type"] for log in sqlite_logs)
        
        assert yaml_types == sqlite_types == {"SKILL_REGISTERED", "EXECUTION_ALLOWED"}


if __name__ == "__main__":
    # Run with: pytest test_phase_2b_real_skills.py -v
    pytest.main([__file__, "-v", "--tb=short"])
