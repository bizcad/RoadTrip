#!/usr/bin/env python3
"""Test Phase 2c fields (updated, entry_point) with both storage backends."""

import pytest
import tempfile
from pathlib import Path
import yaml

from src.skills.registry.storage_yaml import YAMLStore
from src.skills.registry.storage_sqlite import SQLiteStore
from src.skills.registry.storage_interface import StorageConfig


class TestPhase2cStorageFields:
    """Verify updated and entry_point fields persist across backends."""
    
    @pytest.fixture
    def yaml_store(self, tmp_path):
        """Create temporary YAML store."""
        yaml_file = tmp_path / "registry.yaml"
        config = StorageConfig(
            backend_type="yaml",
            location=str(yaml_file)
        )
        return YAMLStore(config)
    
    @pytest.fixture
    def sqlite_store(self, tmp_path):
        """Create temporary SQLite store."""
        db_file = tmp_path / "registry.db"
        config = StorageConfig(
            backend_type="sqlite",
            location=str(db_file)
        )
        return SQLiteStore(config)
    
    def test_yaml_stores_entry_point(self, yaml_store):
        """YAML backend preserves entry_point field."""
        skill_data = {
            "version": "1.0.0",
            "fingerprint": "abc123",
            "author": "test",
            "entry_point": "src/skills/test_skill.py",
            "updated": "2026-02-13T12:00:00.000000Z",
            "description": "Test skill",
            "capabilities": [],
            "source_files": []
        }
        
        yaml_store.save_skill("test_skill", skill_data)
        retrieved = yaml_store.get_skill("test_skill")
        
        assert retrieved is not None
        assert retrieved["entry_point"] == "src/skills/test_skill.py"
        assert retrieved["updated"] == "2026-02-13T12:00:00.000000Z"
    
    def test_sqlite_stores_entry_point(self, sqlite_store):
        """SQLite backend preserves entry_point field."""
        skill_data = {
            "version": "1.0.0",
            "fingerprint": "def456",
            "author": "test",
            "entry_point": "src/skills/another_skill.py",
            "updated": "2026-02-13T13:00:00.000000Z",
            "description": "Another test skill",
            "capabilities": ["testing"],
            "source_files": ["src/skills/another_skill.py"]
        }
        
        sqlite_store.save_skill("another_skill", skill_data)
        retrieved = sqlite_store.get_skill("another_skill")
        
        assert retrieved is not None
        assert retrieved["entry_point"] == "src/skills/another_skill.py"
        assert retrieved["updated"] == "2026-02-13T13:00:00.000000Z"
    
    def test_both_backends_compatible(self, yaml_store, sqlite_store):
        """Both backends handle Phase 2c fields identically."""
        # Same skill data for both
        skill_data = {
            "version": "2.0.0",
            "fingerprint": "ghi789",
            "author": "unified_test",
            "entry_point": "src/skills/unified.py",
            "updated": "2026-02-13T14:00:00.000000Z",
            "description": "Unified test",
            "capabilities": ["unified", "compatible"],
            "source_files": ["src/skills/unified.py", "tests/unified.py"]
        }
        
        # Save to both
        yaml_store.save_skill("unified", skill_data)
        sqlite_store.save_skill("unified", skill_data)
        
        # Retrieve from both
        yaml_result = yaml_store.get_skill("unified")
        sqlite_result = sqlite_store.get_skill("unified")
        
        # Compare key Phase 2c fields
        assert yaml_result["entry_point"] == sqlite_result["entry_point"]
        assert yaml_result["updated"] == sqlite_result["updated"]
        assert yaml_result["version"] == sqlite_result["version"]
        assert yaml_result["fingerprint"] == sqlite_result["fingerprint"]
        assert yaml_result["author"] == sqlite_result["author"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
