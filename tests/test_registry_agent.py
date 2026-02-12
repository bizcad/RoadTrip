"""
Tests for Registry Agent (Phase 2a, Task A2).

Test structure:
- TestRegistryCRUD: Add, update, delete, read operations
- TestRegistryList: Listing all skills
- TestRegistrySearch: Semantic search (grep-based, Phase 2a Task A2b)
- TestRegistryPersistence: YAML file storage
"""

import pytest
from pathlib import Path
from datetime import datetime, timezone
import tempfile
import yaml

from src.agents.registry_agent import RegistryAgent
from src.agents.registry_models import (
    SkillRegistryEntry,
    RegistryInput,
    RegistryOperation,
    RegistryStatus,
)


@pytest.fixture
def agent(tmp_path):
    """Create RegistryAgent with temporary workspace."""
    workspace = tmp_path / "roadtrip_test"
    workspace.mkdir()
    (workspace / "data").mkdir()
    
    return RegistryAgent(workspace_root=str(workspace))


@pytest.fixture
def sample_entry():
    """Create a sample registry entry."""
    return SkillRegistryEntry(
        name="auth_validator",
        version="1.0",
        description="Validates Git credentials and user permissions",
        author="Claude",
        capabilities=["validate_auth", "check_branch"],
        test_count=12,
        test_pass_rate=1.0,
        source_file="src/skills/auth_validator.py",
        test_file="tests/test_auth_validator.py",
    )


# --- Task A2a: CRUD Operations ---

class TestRegistryCRUD:
    """Test CRUD operations (Task A2a)."""
    
    def test_add_entry(self, agent, sample_entry):
        """Add a new entry to registry."""
        input = RegistryInput(
            operation=RegistryOperation.ADD,
            entry=sample_entry,
        )
        
        result = agent.execute(input)
        
        assert result.status == RegistryStatus.SUCCESS
        assert result.count == 1
        assert result.entry.name == "auth_validator"
    
    def test_add_duplicate_fails(self, agent, sample_entry):
        """Adding same entry twice fails."""
        input1 = RegistryInput(
            operation=RegistryOperation.ADD,
            entry=sample_entry,
        )
        result1 = agent.execute(input1)
        assert result1.status == RegistryStatus.SUCCESS
        
        # Try to add again
        input2 = RegistryInput(
            operation=RegistryOperation.ADD,
            entry=sample_entry,
        )
        result2 = agent.execute(input2)
        assert result2.status == RegistryStatus.ALREADY_EXISTS
    
    def test_read_entry(self, agent, sample_entry):
        """Read an entry from registry."""
        # Add first
        add_input = RegistryInput(
            operation=RegistryOperation.ADD,
            entry=sample_entry,
        )
        agent.execute(add_input)
        
        # Read
        read_input = RegistryInput(
            operation=RegistryOperation.READ,
            skill_name="auth_validator",
        )
        result = agent.execute(read_input)
        
        assert result.status == RegistryStatus.SUCCESS
        assert result.entry.name == "auth_validator"
        assert result.entry.version == "1.0"
    
    def test_read_nonexistent(self, agent):
        """Reading nonexistent entry fails."""
        input = RegistryInput(
            operation=RegistryOperation.READ,
            skill_name="nonexistent",
        )
        
        result = agent.execute(input)
        
        assert result.status == RegistryStatus.NOT_FOUND
    
    def test_update_entry(self, agent, sample_entry):
        """Update an existing entry."""
        # Add first
        add_input = RegistryInput(
            operation=RegistryOperation.ADD,
            entry=sample_entry,
        )
        agent.execute(add_input)
        
        # Update
        sample_entry.trust_score = 0.85
        update_input = RegistryInput(
            operation=RegistryOperation.UPDATE,
            entry=sample_entry,
        )
        result = agent.execute(update_input)
        
        assert result.status == RegistryStatus.SUCCESS
        assert result.entry.trust_score == 0.85
    
    def test_delete_entry(self, agent, sample_entry):
        """Delete an entry."""
        # Add first
        add_input = RegistryInput(
            operation=RegistryOperation.ADD,
            entry=sample_entry,
        )
        agent.execute(add_input)
        
        # Delete
        delete_input = RegistryInput(
            operation=RegistryOperation.DELETE,
            skill_name="auth_validator",
        )
        result = agent.execute(delete_input)
        
        assert result.status == RegistryStatus.SUCCESS
        
        # Verify it's gone
        read_input = RegistryInput(
            operation=RegistryOperation.READ,
            skill_name="auth_validator",
        )
        result2 = agent.execute(read_input)
        assert result2.status == RegistryStatus.NOT_FOUND


# --- Task A2a: List Operations ---

class TestRegistryList:
    """Test listing all skills."""
    
    def test_list_empty(self, agent):
        """List empty registry."""
        input = RegistryInput(operation=RegistryOperation.LIST)
        result = agent.execute(input)
        
        assert result.status == RegistryStatus.SUCCESS
        assert result.count == 0
        assert len(result.entries) == 0
    
    def test_list_multiple(self, agent):
        """List multiple entries."""
        entries = [
            SkillRegistryEntry(
                name="skill1",
                version="1.0",
                description="First skill",
            ),
            SkillRegistryEntry(
                name="skill2",
                version="1.0",
                description="Second skill",
            ),
            SkillRegistryEntry(
                name="skill3",
                version="1.0",
                description="Third skill",
            ),
        ]
        
        # Add all
        for entry in entries:
            input = RegistryInput(operation=RegistryOperation.ADD, entry=entry)
            agent.execute(input)
        
        # List
        list_input = RegistryInput(operation=RegistryOperation.LIST)
        result = agent.execute(list_input)
        
        assert result.count == 3
        assert len(result.entries) == 3
        assert result.total_in_registry == 3


# --- Task A2b: Semantic Search ---

class TestRegistrySearch:
    """Test semantic search (Task A2b)."""
    
    def test_search_by_name_exact(self, agent):
        """Search for skill by exact name match."""
        # Add entries
        entries = [
            SkillRegistryEntry(
                name="auth_validator",
                version="1.0",
                description="Validates authentication",
                capabilities=["validate_auth"],
            ),
            SkillRegistryEntry(
                name="git_pusher",
                version="1.0",
                description="Pushes git commits",
                capabilities=["push_code"],
            ),
        ]
        
        for entry in entries:
            input = RegistryInput(operation=RegistryOperation.ADD, entry=entry)
            agent.execute(input)
        
        # Search
        search_input = RegistryInput(
            operation=RegistryOperation.SEARCH,
            search_query="auth_validator",
        )
        result = agent.execute(search_input)
        
        assert result.count >= 1
        # Should rank exact name match highest
        assert result.search_results[0].entry.name == "auth_validator"
    
    def test_search_by_description(self, agent):
        """Search by description substring."""
        entries = [
            SkillRegistryEntry(
                name="auth_validator",
                version="1.0",
                description="Validates Git credentials",
            ),
            SkillRegistryEntry(
                name="telemetry",
                version="1.0",
                description="Logs telemetry data",
            ),
        ]
        
        for entry in entries:
            input = RegistryInput(operation=RegistryOperation.ADD, entry=entry)
            agent.execute(input)
        
        # Search for "git"
        search_input = RegistryInput(
            operation=RegistryOperation.SEARCH,
            search_query="git",
        )
        result = agent.execute(search_input)
        
        assert result.count >= 1
        found_names = [sr.entry.name for sr in result.search_results]
        assert "auth_validator" in found_names
    
    def test_search_by_capability(self, agent):
        """Search by capability."""
        entries = [
            SkillRegistryEntry(
                name="auth_validator",
                version="1.0",
                description="Auth skill",
                capabilities=["validate_auth", "check_permissions"],
            ),
            SkillRegistryEntry(
                name="commit_message",
                version="1.0",
                description="Commit skill",
                capabilities=["generate_message"],
            ),
        ]
        
        for entry in entries:
            input = RegistryInput(operation=RegistryOperation.ADD, entry=entry)
            agent.execute(input)
        
        # Search for "auth"
        search_input = RegistryInput(
            operation=RegistryOperation.SEARCH,
            search_query="auth",
        )
        result = agent.execute(search_input)
        
        assert result.count >= 1
        found_names = [sr.entry.name for sr in result.search_results]
        assert "auth_validator" in found_names
    
    def test_search_no_results(self, agent):
        """Search with no matches."""
        entry = SkillRegistryEntry(
            name="skill",
            version="1.0",
            description="A basic skill",
        )
        
        input = RegistryInput(operation=RegistryOperation.ADD, entry=entry)
        agent.execute(input)
        
        # Search for something not there
        search_input = RegistryInput(
            operation=RegistryOperation.SEARCH,
            search_query="xyz_nonexistent_xyz",
        )
        result = agent.execute(search_input)
        
        assert result.count == 0
        assert len(result.search_results) == 0


# --- Persistence ---

class TestRegistryPersistence:
    """Test file-based storage (YAML)."""
    
    def test_entry_persisted_to_yaml(self, agent, sample_entry, tmp_path):
        """Entry saved to YAML file."""
        input = RegistryInput(
            operation=RegistryOperation.ADD,
            entry=sample_entry,
        )
        agent.execute(input)
        
        # Check YAML file exists
        yaml_file = agent.registry_dir / "auth_validator.yaml"
        assert yaml_file.exists()
        
        # Parse YAML
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
        
        assert data["name"] == "auth_validator"
        assert data["version"] == "1.0"
    
    def test_entry_roundtrip(self, agent, sample_entry):
        """Save and load: data preserved."""
        # Add
        add_input = RegistryInput(
            operation=RegistryOperation.ADD,
            entry=sample_entry,
        )
        agent.execute(add_input)
        
        # Read (loads from YAML)
        read_input = RegistryInput(
            operation=RegistryOperation.READ,
            skill_name="auth_validator",
        )
        result = agent.execute(read_input)
        
        loaded = result.entry
        assert loaded.name == sample_entry.name
        assert loaded.version == sample_entry.version
        assert loaded.description == sample_entry.description
        assert loaded.capabilities == sample_entry.capabilities
