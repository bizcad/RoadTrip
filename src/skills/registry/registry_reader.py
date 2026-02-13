"""
registry_reader.py (WS0) - Foundational Registry Reader

Provides single source of truth for all other agents.
- Reads config/skills-registry.yaml
- Responds to queries from WS1-4
- Ensures consistency across system
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

from .base_agent import BaseAgent
from .registry_models import SkillMetadata, RegistryData, AgentState


class RegistryReader(BaseAgent):
    """WS0: Registry Reader - Single source of truth."""
    
    def __init__(self, registry_path: str = "config/skills-registry.yaml", use_mock: bool = True):
        """
        Initialize registry reader.
        
        Args:
            registry_path: Path to skills-registry.yaml
            use_mock: If True, load mock registry; if False, load actual
        """
        super().__init__("WS0", use_mock)
        self.registry_path = Path(registry_path)
        self._registry: Optional[RegistryData] = None
        
        # Load registry on init
        self.transition_state(AgentState.INIT, "Loading registry")
        self._load_registry()
    
    def _load_registry(self):
        """Load registry from YAML file."""
        try:
            if self.registry_path.exists():
                with open(self.registry_path, 'r') as f:
                    data = yaml.safe_load(f) or {}
                
                # Parse into RegistryData
                self._registry = self._parse_registry(data)
                self.logger.info(f"✅ Loaded registry: {len(self._registry.skills)} skills")
            else:
                # Create empty registry
                self._registry = RegistryData()
                self.logger.warning(f"Registry not found at {self.registry_path}; using empty")
            
            self.transition_state(AgentState.VERIFIED, "Registry loaded")
        except Exception as e:
            self.error = str(e)
            self.transition_state(AgentState.ERROR, f"Failed to load registry: {e}")
            raise
    
    def _parse_registry(self, data: Dict[str, Any]) -> RegistryData:
        """Parse raw YAML dict into RegistryData."""
        registry = RegistryData()
        registry.metadata = data.get("metadata", {})
        
        # Parse skills
        skills_data = data.get("skills", {})
        for skill_name, skill_metadata in skills_data.items():
            if isinstance(skill_metadata, dict):
                metadata = SkillMetadata(
                    name=skill_name,
                    version=skill_metadata.get("version", "1.0.0"),
                    fingerprint=skill_metadata.get("fingerprint", ""),
                    author=skill_metadata.get("author", "unknown"),
                    capabilities=skill_metadata.get("capabilities", []),
                    tests=skill_metadata.get("tests", 0),
                    test_coverage=skill_metadata.get("test_coverage", 0.0),
                    created=skill_metadata.get("created", ""),
                    description=skill_metadata.get("description", ""),
                    source_files=skill_metadata.get("source_files", [])
                )
                registry.skills[skill_name] = metadata
        
        return registry
    
    def handle_query(self, query: str) -> Any:
        """
        Handle queries from other agents.
        
        Supports:
        - "get_all_skills" → list of skill names
        - "get_fingerprint:{skill_name}" → fingerprint value
        - "get_skill:{skill_name}" → full metadata
        - "query_capabilities:{capability}" → skills with capability
        """
        self.transition_state(AgentState.QUERYING, f"Query: {query[:30]}")
        
        try:
            if query == "get_all_skills":
                result = list(self._registry.skills.keys())
            
            elif query.startswith("get_fingerprint:"):
                skill_name = query.replace("get_fingerprint:", "")
                if skill_name in self._registry.skills:
                    result = self._registry.skills[skill_name].fingerprint
                else:
                    result = None
            
            elif query.startswith("get_skill:"):
                skill_name = query.replace("get_skill:", "")
                if skill_name in self._registry.skills:
                    result = self._registry.skills[skill_name]
                else:
                    result = None
            
            elif query.startswith("query_capabilities:"):
                capability = query.replace("query_capabilities:", "")
                result = [
                    {
                        "name": name,
                        "fingerprint": metadata.fingerprint,
                        "version": metadata.version
                    }
                    for name, metadata in self._registry.skills.items()
                    if capability in metadata.capabilities
                ]
            
            else:
                result = None
                self.logger.warning(f"Unknown query: {query}")
            
            self.transition_state(AgentState.VERIFIED, "Query handled")
            return result
        
        except Exception as e:
            self.error = str(e)
            self.transition_state(AgentState.ERROR, f"Query failed: {e}")
            raise
    
    def read_registry(self) -> RegistryData:
        """Get current registry state."""
        return self._registry
    
    def write_registry(self, registry: RegistryData):
        """Write updated registry to YAML file."""
        self.transition_state(AgentState.WRITING, f"Writing registry to {self.registry_path}")
        
        try:
            # Convert to dict
            data = {
                "metadata": registry.metadata,
                "skills": {
                    name: metadata.to_dict()
                    for name, metadata in registry.skills.items()
                }
            }
            
            # Write YAML
            with open(self.registry_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            # Reload to verify
            self._load_registry()
            self.logger.info(f"✅ Registry written: {len(registry.skills)} skills")
        
        except Exception as e:
            self.error = str(e)
            self.transition_state(AgentState.ERROR, f"Write failed: {e}")
            raise
