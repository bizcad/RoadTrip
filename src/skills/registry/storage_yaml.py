"""
storage_yaml.py - YAML-based Registry Storage

Implements RegistryStore using local YAML files.
Perfect for development - no external dependencies, filesystem-based.

Format: config/skills-registry.yaml

Structure:
  registry:
    metadata:
      version: "1.0"
      created: ISO timestamp
    skills:
      skill_name:
        version: "1.0.0"
        fingerprint: "abc123"
        author: "author_name"
        capabilities: [cap1, cap2]
        tests: 10
        test_coverage: 85.5
        status: "active"
        created: ISO timestamp
        description: "..."
        source_files: [...]
  fingerprints:
    skill_name:
      1.0.0: "fp_..."
      2.0.0: "fp_..."
  audit:
    - timestamp: ISO timestamp
      event_type: "REGISTERED"
      skill_id: "skill_name"
      details: {...}
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from .storage_interface import RegistryStore, StorageConfig


class YAMLStore(RegistryStore):
    """YAML-based storage backend for registry."""
    
    def __init__(self, config: StorageConfig):
        """Initialize YAML store.
        
        Args:
            config: StorageConfig with location (filepath)
        """
        self.filepath = Path(config.location)
        self.read_only = config.read_only
        self.logger = logging.getLogger("YAMLStore")
        
        # Ensure directory exists
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or create empty registry
        self._data = self._load_file()
        self.logger.info(f"✅ YAML store initialized: {self.filepath}")
    
    def _load_file(self) -> Dict[str, Any]:
        """Load YAML file or create default structure."""
        if self.filepath.exists():
            try:
                with open(self.filepath, 'r') as f:
                    data = yaml.safe_load(f) or {}
                return data
            except Exception as e:
                self.logger.error(f"Failed to load YAML: {e}")
                return self._default_structure()
        else:
            return self._default_structure()
    
    def _default_structure(self) -> Dict[str, Any]:
        """Create default empty registry structure."""
        return {
            "registry": {
                "metadata": {
                    "version": "1.0",
                    "created": datetime.now().isoformat()
                },
                "skills": {}
            },
            "fingerprints": {},
            "audit": []
        }
    
    def _save_file(self) -> None:
        """Write data to YAML file."""
        if self.read_only:
            self.logger.warning("Store is read-only, skipping write")
            return
        
        try:
            with open(self.filepath, 'w') as f:
                yaml.dump(self._data, f, default_flow_style=False, sort_keys=False)
            self.logger.debug(f"✅ YAML saved to {self.filepath}")
        except Exception as e:
            self.logger.error(f"Failed to save YAML: {e}")
            raise
    
    # ===== SKILL CRUD =====
    
    def save_skill(self, skill_id: str, skill_data: Dict[str, Any]) -> None:
        """Save or update skill."""
        if not self._ensure_skills_dict():
            return
        
        self._data["registry"]["skills"][skill_id] = skill_data
        self._save_file()
        self.logger.info(f"✅ Saved skill: {skill_id}")
    
    def get_skill(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve skill by ID."""
        skills = self._data.get("registry", {}).get("skills", {})
        return skills.get(skill_id)
    
    def get_all_skills(self) -> List[str]:
        """Get all skill IDs."""
        skills = self._data.get("registry", {}).get("skills", {})
        return list(skills.keys())
    
    def delete_skill(self, skill_id: str) -> bool:
        """Delete a skill."""
        if not self._ensure_skills_dict():
            return False
        
        skills = self._data["registry"]["skills"]
        if skill_id in skills:
            del skills[skill_id]
            self._save_file()
            self.logger.info(f"✅ Deleted skill: {skill_id}")
            return True
        
        return False
    
    # ===== SEARCH =====
    
    def search_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        """Find skills by capability (case-insensitive substring match)."""
        results = []
        skills = self._data.get("registry", {}).get("skills", {})
        
        for skill_id, skill_data in skills.items():
            caps = skill_data.get("capabilities", [])
            if any(capability.lower() in cap.lower() for cap in caps):
                results.append({"skill_id": skill_id, **skill_data})
        
        return results
    
    def search_by_author(self, author: str) -> List[Dict[str, Any]]:
        """Find skills by author."""
        results = []
        skills = self._data.get("registry", {}).get("skills", {})
        
        for skill_id, skill_data in skills.items():
            if skill_data.get("author", "").lower() == author.lower():
                results.append({"skill_id": skill_id, **skill_data})
        
        return results
    
    # ===== FINGERPRINTS =====
    
    def save_fingerprint(self, skill_id: str, version: str, fingerprint: str) -> None:
        """Save fingerprint for skill version."""
        if "fingerprints" not in self._data:
            self._data["fingerprints"] = {}
        
        if skill_id not in self._data["fingerprints"]:
            self._data["fingerprints"][skill_id] = {}
        
        self._data["fingerprints"][skill_id][version] = fingerprint
        self._save_file()
        self.logger.debug(f"✅ Saved fingerprint: {skill_id}:{version}")
    
    def get_fingerprint(self, skill_id: str, version: str) -> Optional[str]:
        """Get fingerprint for skill version."""
        fps = self._data.get("fingerprints", {})
        return fps.get(skill_id, {}).get(version)
    
    # ===== AUDIT LOG =====
    
    def save_audit_log(self, event_type: str, skill_id: str,
                      details: Dict[str, Any]) -> None:
        """Save audit event."""
        if "audit" not in self._data:
            self._data["audit"] = []
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "skill_id": skill_id,
            "details": details
        }
        
        self._data["audit"].append(event)
        self._save_file()
        self.logger.debug(f"✅ Audit logged: {event_type} for {skill_id}")
    
    def get_audit_logs(self, skill_id: Optional[str] = None,
                      event_type: Optional[str] = None,
                      since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Retrieve audit logs."""
        logs = self._data.get("audit", [])
        
        # Filter by skill_id
        if skill_id:
            logs = [log for log in logs if log.get("skill_id") == skill_id]
        
        # Filter by event_type
        if event_type:
            logs = [log for log in logs if log.get("event_type") == event_type]
        
        # Filter by timestamp
        if since:
            since_iso = since.isoformat()
            logs = [log for log in logs if log.get("timestamp", "") >= since_iso]
        
        return logs
    
    # ===== HEALTH =====
    
    def health_check(self) -> bool:
        """Verify storage is accessible."""
        try:
            # Try to read
            _ = self._load_file()
            
            # Try to write (if not read-only)
            if not self.read_only:
                self._save_file()
            
            self.logger.debug("✅ Health check passed")
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    # ===== HELPERS =====
    
    def _ensure_skills_dict(self) -> bool:
        """Ensure registry.skills dict exists."""
        if "registry" not in self._data:
            self._data["registry"] = {}
        if "skills" not in self._data["registry"]:
            self._data["registry"]["skills"] = {}
        return True
