"""
storage_interface.py - Abstract Storage Layer

Defines pluggable storage interface for registry persistence.
Supports YAML, SQLite, SQL Server, CockroachDB, Snowflake, etc.

Design philosophy:
- YAML for development (filesystem-based, zero ops)
- SQLite for single-service production (file-based, zero ops)
- SQL Server/CockroachDB/Snowflake for distributed scenarios
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class StorageConfig:
    """Configuration for storage backends."""
    backend_type: str  # "yaml", "sqlite", "sqlserver", "cockroach", "snowflake"
    location: str  # filepath for yaml/sqlite, connection string for others
    read_only: bool = False
    timeout_seconds: int = 30


class RegistryStore(ABC):
    """Abstract interface for registry persistence.
    
    All implementations must support:
    - Create/read/update/delete capabilities
    - Full-text search on skill capabilities
    - Consistency guarantees
    
    Implementation strategy:
    - Start with YAML (dev) + SQLite (single-service prod)
    - Add SQL Server/CockroachDB for distributed scenarios
    - Free tier priority (YAML, SQLite, CockroachDB free tier)
    """
    
    @abstractmethod
    def save_skill(self, skill_id: str, skill_data: Dict[str, Any]) -> None:
        """Save or update a skill.
        
        Args:
            skill_id: Unique skill identifier
            skill_data: Skill metadata dict
        """
        pass
    
    @abstractmethod
    def get_skill(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a skill by ID.
        
        Args:
            skill_id: Unique skill identifier
            
        Returns:
            Skill data dict or None if not found
        """
        pass
    
    @abstractmethod
    def get_all_skills(self) -> List[str]:
        """Get all skill IDs in registry.
        
        Returns:
            List of skill names
        """
        pass
    
    @abstractmethod
    def delete_skill(self, skill_id: str) -> bool:
        """Delete a skill.
        
        Args:
            skill_id: Unique skill identifier
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def search_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        """Find skills by capability (full-text search).
        
        Args:
            capability: Capability name or pattern
            
        Returns:
            List of skill metadata dicts matching capability
        """
        pass
    
    @abstractmethod
    def search_by_author(self, author: str) -> List[Dict[str, Any]]:
        """Find skills by author.
        
        Args:
            author: Author name
            
        Returns:
            List of skill metadata dicts by author
        """
        pass
    
    @abstractmethod
    def save_fingerprint(self, skill_id: str, version: str, fingerprint: str) -> None:
        """Save fingerprint.
        
        Used by WS1 and WS3 for fingerprint storage.
        """
        pass
    
    @abstractmethod
    def get_fingerprint(self, skill_id: str, version: str) -> Optional[str]:
        """Get fingerprint for skill version.
        
        Used by WS2 and WS4 for verification.
        """
        pass
    
    @abstractmethod
    def save_audit_log(self, event_type: str, skill_id: str, 
                      details: Dict[str, Any]) -> None:
        """Save audit event for telemetry analysis.
        
        Used for:
        - Registration events (WS3)
        - Verification events (WS2, WS4)
        - Execution decisions (WS4)
        
        Args:
            event_type: "REGISTERED", "VERIFIED", "ALLOWED", "BLOCKED", etc.
            skill_id: Skill involved
            details: Event-specific data
        """
        pass
    
    @abstractmethod
    def get_audit_logs(self, skill_id: Optional[str] = None,
                       event_type: Optional[str] = None,
                       since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Retrieve audit logs for analysis.
        
        Args:
            skill_id: Filter by skill (None = all)
            event_type: Filter by event type (None = all)
            since: Filter by timestamp (None = all)
            
        Returns:
            List of audit event dicts
        """
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Verify storage backend is accessible.
        
        Returns:
            True if healthy, False otherwise
        """
        pass
