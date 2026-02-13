"""
storage_sqlite.py - SQLite Registry Storage

Implements RegistryStore using SQLite database.
Perfect for single-service production - zero ops, file-based persistence.

Database schema:
  skills
    - id (PRIMARY KEY)
    - name (UNIQUE)
    - version
    - fingerprint
    - author
    - capabilities (JSON)
    - tests (INT)
    - test_coverage (REAL)
    - status (VARCHAR)
    - created (TIMESTAMP)
    - description (TEXT)
    - source_files (JSON)
    - entry_point (TEXT) - Path to .py file
    - updated (TIMESTAMP) - Last modification time
  
  fingerprints
    - id (PRIMARY KEY)
    - skill_id (FK skills.id)
    - version
    - fingerprint
    - created (TIMESTAMP)
  
  audit_logs
    - id (PRIMARY KEY)
    - timestamp (TIMESTAMP)
    - event_type (VARCHAR)
    - skill_id (VARCHAR)
    - details (JSON)
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .storage_interface import RegistryStore, StorageConfig


class SQLiteStore(RegistryStore):
    """SQLite-based storage backend for registry."""
    
    def __init__(self, config: StorageConfig):
        """Initialize SQLite store.
        
        Args:
            config: StorageConfig with location (filepath)
        """
        self.filepath = Path(config.location)
        self.read_only = config.read_only
        self.logger = logging.getLogger("SQLiteStore")
        
        # Ensure directory exists
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_db()
        self.logger.info(f"✅ SQLite store initialized: {self.filepath}")
    
    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(str(self.filepath))
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def _init_db(self) -> None:
        """Create tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Skills table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    version TEXT NOT NULL,
                    fingerprint TEXT NOT NULL,
                    author TEXT,
                    capabilities TEXT,  -- JSON array
                    tests INTEGER DEFAULT 0,
                    test_coverage REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'active',
                    created TEXT,
                    description TEXT,
                    source_files TEXT,  -- JSON array
                    entry_point TEXT,  -- Path to skill entry point (.py file)
                    updated TEXT DEFAULT CURRENT_TIMESTAMP  -- ISO timestamp, updated on modification
                )
            """)
            
            # Fingerprints table (versioned fingerprints)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fingerprints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    skill_id TEXT NOT NULL,
                    version TEXT NOT NULL,
                    fingerprint TEXT NOT NULL,
                    created TEXT,
                    UNIQUE(skill_id, version)
                )
            """)
            
            # Audit logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    skill_id TEXT,
                    details TEXT  -- JSON
                )
            """)
            
            # Create index on skill names for fast lookup
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_skills_name 
                ON skills(name)
            """)
            
            # Create index on capabilities for search
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_event_type 
                ON audit_logs(event_type)
            """)
            
            conn.commit()
            self.logger.debug("✅ Database schema initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
        finally:
            conn.close()
    
    # ===== SKILL CRUD =====
    
    def save_skill(self, skill_id: str, skill_data: Dict[str, Any]) -> None:
        """Save or update skill."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Convert lists to JSON
            capabilities = json.dumps(skill_data.get("capabilities", []))
            source_files = json.dumps(skill_data.get("source_files", []))
            
            cursor.execute("""
                INSERT OR REPLACE INTO skills 
                (name, version, fingerprint, author, capabilities, tests,
                 test_coverage, status, created, description, source_files, entry_point, updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                skill_id,
                skill_data.get("version", "1.0.0"),
                skill_data.get("fingerprint", ""),
                skill_data.get("author", "unknown"),
                capabilities,
                skill_data.get("tests", 0),
                skill_data.get("test_coverage", 0.0),
                skill_data.get("status", "active"),
                skill_data.get("created", datetime.now().isoformat()),
                skill_data.get("description", ""),
                source_files,
                skill_data.get("entry_point", ""),
                skill_data.get("updated", datetime.now().isoformat())
            ))
            
            conn.commit()
            self.logger.info(f"Saved skill: {skill_id}")
        except Exception as e:
            self.logger.error(f"Failed to save skill: {e}")
            raise
        finally:
            conn.close()
    
    def get_skill(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve skill by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM skills WHERE name = ?", (skill_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_dict(row)
            return None
        finally:
            conn.close()
    
    def get_all_skills(self) -> List[str]:
        """Get all skill IDs."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT name FROM skills ORDER BY name")
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def delete_skill(self, skill_id: str) -> bool:
        """Delete a skill."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM skills WHERE name = ?", (skill_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                self.logger.info(f"✅ Deleted skill: {skill_id}")
                return True
            return False
        finally:
            conn.close()
    
    # ===== SEARCH =====
    
    def search_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        """Find skills by capability (JSON search)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM skills ORDER BY name")
            results = []
            
            for row in cursor.fetchall():
                skill_dict = self._row_to_dict(row)
                caps = skill_dict.get("capabilities", [])
                if any(capability.lower() in cap.lower() for cap in caps):
                    results.append(skill_dict)
            
            return results
        finally:
            conn.close()
    
    def search_by_author(self, author: str) -> List[Dict[str, Any]]:
        """Find skills by author."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT * FROM skills WHERE LOWER(author) = ? ORDER BY name",
                (author.lower(),)
            )
            return [self._row_to_dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    # ===== FINGERPRINTS =====
    
    def save_fingerprint(self, skill_id: str, version: str, fingerprint: str) -> None:
        """Save fingerprint for skill version."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO fingerprints 
                (skill_id, version, fingerprint, created)
                VALUES (?, ?, ?, ?)
            """, (skill_id, version, fingerprint, datetime.now().isoformat()))
            
            conn.commit()
            self.logger.debug(f"✅ Saved fingerprint: {skill_id}:{version}")
        finally:
            conn.close()
    
    def get_fingerprint(self, skill_id: str, version: str) -> Optional[str]:
        """Get fingerprint for skill version."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT fingerprint FROM fingerprints WHERE skill_id = ? AND version = ?",
                (skill_id, version)
            )
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            conn.close()
    
    # ===== AUDIT LOG =====
    
    def save_audit_log(self, event_type: str, skill_id: str,
                      details: Dict[str, Any]) -> None:
        """Save audit event."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO audit_logs 
                (timestamp, event_type, skill_id, details)
                VALUES (?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                event_type,
                skill_id,
                json.dumps(details)
            ))
            
            conn.commit()
            self.logger.debug(f"✅ Audit logged: {event_type} for {skill_id}")
        finally:
            conn.close()
    
    def get_audit_logs(self, skill_id: Optional[str] = None,
                      event_type: Optional[str] = None,
                      since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Retrieve audit logs."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            query = "SELECT * FROM audit_logs WHERE 1=1"
            params = []
            
            if skill_id:
                query += " AND skill_id = ?"
                params.append(skill_id)
            
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)
            
            if since:
                query += " AND timestamp >= ?"
                params.append(since.isoformat())
            
            query += " ORDER BY timestamp DESC"
            
            cursor.execute(query, params)
            return [self._row_to_dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    # ===== HEALTH =====
    
    def health_check(self) -> bool:
        """Verify storage is accessible."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM skills")
            conn.close()
            
            self.logger.debug("✅ Health check passed")
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    # ===== HELPERS =====
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert database row to dict, parsing JSON fields."""
        data = dict(row)
        
        # Parse JSON fields
        if "capabilities" in data and isinstance(data["capabilities"], str):
            data["capabilities"] = json.loads(data["capabilities"])
        if "source_files" in data and isinstance(data["source_files"], str):
            data["source_files"] = json.loads(data["source_files"])
        if "details" in data and isinstance(data["details"], str):
            data["details"] = json.loads(data["details"])
        
        return data
