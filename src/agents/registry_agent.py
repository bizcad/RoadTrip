#!/usr/bin/env python3
"""
Registry Agent (Phase 2a, Workstream A).

Maintains a centralized catalog of skills with their fingerprints, metadata, and trust scores.

Responsibilities:
1. CRUD operations on SkillRegistryEntry objects
2. Store entries in file-based registry (YAML/JSON files in data/skill-registry/)
3. Enable semantic search over skill names, descriptions, capabilities
4. Serve as source of truth for Phase 2b (Verifier) and orchestrator

Key properties:
- Persistent storage: data/skill-registry/{skill_name}.yaml
- No external dependencies; pure file I/O + regex
- Supports concurrent reads (file-based is safe for most cases)
- Searchable by name, description, capability

Usage (CLI):
    python -m src.agents.registry_agent --list
    python -m src.agents.registry_agent --search "auth"
    python -m src.agents.registry_agent --detail auth_validator

Usage (import):
    from src.agents.registry_agent import RegistryAgent
    agent = RegistryAgent()
    result = agent.execute(RegistryInput(...))
"""

import sys
import json
import yaml
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import argparse
import re

try:
    from .registry_models import (
        SkillRegistryEntry,
        RegistryInput,
        RegistryResult,
        RegistryOperation,
        RegistryStatus,
        SearchResult,
    )
except ImportError:
    from registry_models import (
        SkillRegistryEntry,
        RegistryInput,
        RegistryResult,
        RegistryOperation,
        RegistryStatus,
        SearchResult,
    )


class RegistryAgent:
    """
    Agent that maintains the skill registry.
    
    Phase 2a Task A2a (Skill Catalog):
    - Load/save SkillRegistryEntry to YAML files
    - CRUD operations
    - Maintain index of all skills
    
    Phase 2a Task A2b (Semantic Search):
    - Search by name (exact), description (substring), capabilities (contains)
    - Return ranked results (simple grep + BM25 optional)
    
    Interface:
        execute(input: RegistryInput) -> RegistryResult
    """
    
    def __init__(self, workspace_root: str = None):
        """
        Initialize Registry Agent.
        
        Args:
            workspace_root: Root of RoadTrip repo
        """
        if workspace_root is None:
            workspace_root = Path(__file__).parent.parent.parent
        
        self.workspace_root = Path(workspace_root)
        self.registry_dir = self.workspace_root / "data" / "skill-registry"
        self.index_file = self.registry_dir / "index.yaml"
        
        # Create registry directory if missing
        self.registry_dir.mkdir(parents=True, exist_ok=True)
    
    def execute(self, input: RegistryInput) -> RegistryResult:
        """
        Execute a registry operation.
        
        Args:
            input: RegistryInput with operation, entry, search query, etc.
        
        Returns:
            RegistryResult with status and operation-specific results
        """
        
        result = RegistryResult(
            status=RegistryStatus.SUCCESS,
            operation=input.operation,
        )
        
        try:
            if input.operation == RegistryOperation.ADD:
                return self._add_entry(input.entry, result)
            elif input.operation == RegistryOperation.UPDATE:
                return self._update_entry(input.entry, result)
            elif input.operation == RegistryOperation.DELETE:
                return self._delete_entry(input.skill_name, result)
            elif input.operation == RegistryOperation.READ:
                return self._read_entry(input.skill_name, result)
            elif input.operation == RegistryOperation.LIST:
                return self._list_entries(result)
            elif input.operation == RegistryOperation.SEARCH:
                return self._search_entries(
                    input.search_query,
                    input.search_fields,
                    input.limit,
                    result
                )
            else:
                result.status = RegistryStatus.INVALID_INPUT
                result.error = f"Unknown operation: {input.operation}"
                return result
        
        except Exception as e:
            result.status = RegistryStatus.FAILED
            result.error = str(e)
            result.details = {"exception": type(e).__name__}
            return result
    
    # --- CRUD Operations ---
    
    def _add_entry(self, entry: SkillRegistryEntry, result: RegistryResult) -> RegistryResult:
        """Add a new entry."""
        entry_path = self.registry_dir / f"{entry.name}.yaml"
        
        if entry_path.exists():
            result.status = RegistryStatus.ALREADY_EXISTS
            result.error = f"Skill '{entry.name}' already in registry"
            return result
        
        # Save entry as YAML
        self._save_entry(entry)
        result.entry = entry
        result.count = 1
        
        return result
    
    def _update_entry(self, entry: SkillRegistryEntry, result: RegistryResult) -> RegistryResult:
        """Update existing entry."""
        entry_path = self.registry_dir / f"{entry.name}.yaml"
        
        if not entry_path.exists():
            result.status = RegistryStatus.NOT_FOUND
            result.error = f"Skill '{entry.name}' not found"
            return result
        
        # Update timestamps
        entry.last_updated = datetime.now(timezone.utc)
        
        # Save entry
        self._save_entry(entry)
        result.entry = entry
        result.count = 1
        
        return result
    
    def _delete_entry(self, skill_name: str, result: RegistryResult) -> RegistryResult:
        """Delete entry."""
        entry_path = self.registry_dir / f"{skill_name}.yaml"
        
        if not entry_path.exists():
            result.status = RegistryStatus.NOT_FOUND
            result.error = f"Skill '{skill_name}' not found"
            return result
        
        entry_path.unlink()
        result.count = 1
        
        return result
    
    def _read_entry(self, skill_name: str, result: RegistryResult) -> RegistryResult:
        """Read one entry."""
        entry = self._load_entry(skill_name)
        
        if entry is None:
            result.status = RegistryStatus.NOT_FOUND
            result.error = f"Skill '{skill_name}' not found"
            return result
        
        result.entry = entry
        result.count = 1
        
        return result
    
    def _list_entries(self, result: RegistryResult) -> RegistryResult:
        """List all entries."""
        entries = []
        
        for yaml_file in sorted(self.registry_dir.glob("*.yaml")):
            if yaml_file.name == "index.yaml":
                continue
            
            skill_name = yaml_file.stem
            entry = self._load_entry(skill_name)
            if entry:
                entries.append(entry)
        
        result.entries = entries
        result.count = len(entries)
        result.total_in_registry = len(entries)
        
        return result
    
    # --- Search ---
    
    def _search_entries(
        self,
        query: str,
        fields: List[str],
        limit: int,
        result: RegistryResult
    ) -> RegistryResult:
        """
        Search for skills by query.
        
        Phase 2a Task A2b (Semantic Search):
        - Simple grep-based approach (no ML)
        - Search across name, description, capabilities
        - Return ranked by relevance (simple heuristic)
        """
        
        if not query:
            result.status = RegistryStatus.INVALID_INPUT
            result.error = "Search query is empty"
            return result
        
        # Load all entries
        entries = []
        for yaml_file in self.registry_dir.glob("*.yaml"):
            if yaml_file.name == "index.yaml":
                continue
            skill_name = yaml_file.stem
            entry = self._load_entry(skill_name)
            if entry:
                entries.append(entry)
        
        # Score each entry by relevance
        search_results = []
        query_lower = query.lower()
        
        for entry in entries:
            relevance = self._compute_relevance(entry, query_lower, fields)
            if relevance > 0:
                search_results.append(SearchResult(entry=entry, relevance=relevance))
        
        # Sort by relevance (descending) + limit
        search_results.sort(key=lambda x: x.relevance, reverse=True)
        search_results = search_results[:limit]
        
        result.search_results = search_results
        result.count = len(search_results)
        result.total_in_registry = len(entries)
        
        return result
    
    def _compute_relevance(self, entry: SkillRegistryEntry, query: str, fields: List[str]) -> float:
        """
        Compute relevance score for search result.
        
        Simple heuristic:
        - Exact name match: 1.0
        - Substring in field: 0.5
        - No match: 0.0
        """
        
        # Exact name match
        if query == entry.name.lower():
            return 1.0
        
        # Substring match (simple grep)
        for field in fields:
            if field == "name":
                if query in entry.name.lower():
                    return 0.9
            elif field == "description":
                if query in entry.description.lower():
                    return 0.6
            elif field == "capabilities":
                if any(query in cap.lower() for cap in entry.capabilities):
                    return 0.7
        
        return 0.0
    
    # --- Storage (File I/O) ---
    
    def _save_entry(self, entry: SkillRegistryEntry) -> None:
        """Save entry as YAML file."""
        entry_path = self.registry_dir / f"{entry.name}.yaml"
        
        # Convert to dict for YAML serialization
        data = {
            "name": entry.name,
            "version": entry.version,
            "description": entry.description,
            "author": entry.author,
            "capabilities": entry.capabilities,
            "test_count": entry.test_count,
            "test_pass_rate": entry.test_pass_rate,
            "test_coverage": entry.test_coverage,
            "trusted": entry.trusted,
            "trust_score": entry.trust_score,
            "active": entry.active,
            "deprecated": entry.deprecated,
            "source_file": entry.source_file,
            "test_file": entry.test_file,
            # Timestamps
            "created_at": entry.created_at.isoformat(),
            "last_updated": entry.last_updated.isoformat(),
            "last_fingerprinted": entry.last_fingerprinted.isoformat() if entry.last_fingerprinted else None,
            "last_verified": entry.last_verified.isoformat() if entry.last_verified else None,
        }
        
        # Include fingerprint if present
        if entry.fingerprint:
            data["fingerprint"] = {
                "code_hash": entry.fingerprint.code_hash,
                "capabilities_hash": entry.fingerprint.capabilities_hash,
                "test_metadata_hash": entry.fingerprint.test_metadata_hash,
                "signed": entry.fingerprint.signed,
                "signature": entry.fingerprint.signature,
            }
        
        with open(entry_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False)
    
    def _load_entry(self, skill_name: str) -> Optional[SkillRegistryEntry]:
        """Load entry from YAML file."""
        entry_path = self.registry_dir / f"{skill_name}.yaml"
        
        if not entry_path.exists():
            return None
        
        try:
            with open(entry_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Parse timestamps
            created_at = datetime.fromisoformat(data.get("created_at", datetime.now(timezone.utc).isoformat()))
            last_updated = datetime.fromisoformat(data.get("last_updated", datetime.now(timezone.utc).isoformat()))
            
            last_fp = data.get("last_fingerprinted")
            last_fingerprinted = datetime.fromisoformat(last_fp) if last_fp else None
            
            last_ver = data.get("last_verified")
            last_verified = datetime.fromisoformat(last_ver) if last_ver else None
            
            entry = SkillRegistryEntry(
                name=data.get("name", ""),
                version=data.get("version", ""),
                description=data.get("description", ""),
                author=data.get("author"),
                capabilities=data.get("capabilities", []),
                test_count=data.get("test_count", 0),
                test_pass_rate=data.get("test_pass_rate", 0.0),
                test_coverage=data.get("test_coverage"),
                trusted=data.get("trusted", False),
                trust_score=data.get("trust_score", 0.0),
                active=data.get("active", True),
                deprecated=data.get("deprecated", False),
                source_file=data.get("source_file"),
                test_file=data.get("test_file"),
                created_at=created_at,
                last_updated=last_updated,
                last_fingerprinted=last_fingerprinted,
                last_verified=last_verified,
            )
            
            return entry
        
        except Exception as e:
            print(f"Error loading {entry_path}: {e}", file=sys.stderr)
            return None


# --- CLI Entry Point ---

def main():
    """CLI for registry operations."""
    parser = argparse.ArgumentParser(description="Registry Agent (Phase 2a)")
    parser.add_argument('--list', action='store_true', help='List all skills')
    parser.add_argument('--search', help='Search for skills')
    parser.add_argument('--detail', help='Show details of one skill')
    parser.add_argument('--limit', type=int, default=10, help='Max search results')
    
    args = parser.parse_args()
    
    agent = RegistryAgent()
    
    if args.list:
        result = agent.execute(RegistryInput(operation=RegistryOperation.LIST))
        print(f"Skills in registry: {result.count}")
        for entry in result.entries:
            status = "✓" if entry.active else "✗"
            print(f"  {status} {entry.name} v{entry.version}")
    
    elif args.search:
        result = agent.execute(RegistryInput(
            operation=RegistryOperation.SEARCH,
            search_query=args.search,
            limit=args.limit,
        ))
        print(f"Found {result.count} skills matching '{args.search}':")
        for sr in result.search_results:
            print(f"  {sr.entry.name}: {sr.entry.description} (relevance: {sr.relevance:.2f})")
    
    elif args.detail:
        result = agent.execute(RegistryInput(
            operation=RegistryOperation.READ,
            skill_name=args.detail,
        ))
        if result.status == RegistryStatus.SUCCESS:
            entry = result.entry
            print(f"Skill: {entry.name} v{entry.version}")
            print(f"  Description: {entry.description}")
            print(f"  Capabilities: {', '.join(entry.capabilities)}")
            print(f"  Tests: {entry.test_count} ({entry.test_pass_rate*100:.0f}% pass rate)")
            print(f"  Trusted: {entry.trusted} (score: {entry.trust_score:.2f})")
        else:
            print(f"Error: {result.error}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
