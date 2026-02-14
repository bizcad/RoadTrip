"""
MCPServerRegistryClient - Official MCP Registry Discovery

This module provides a client for querying the Official Model Context Protocol Registry
(registry.modelcontextprotocol.io) to discover available MCPs and their metadata.

Reference: https://registry.modelcontextprotocol.io
"""

import asyncio
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import urllib.request
import urllib.error
import logging

logger = logging.getLogger(__name__)


@dataclass
class MCPServerEntry:
    """Represents a single MCP server from the Official Registry"""
    
    name: str
    author: str
    homepage: Optional[str]
    repository: str
    description: str
    sources: List[str]  # URLs where this MCP can be found
    capabilities: List[str]  # e.g., ["tools", "resources", "prompts"]
    
    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    version: Optional[str] = None
    tags: List[str] = None
    
    # Derived
    priority_score: float = 0.0  # Set during ranking
    discovery_timestamp: Optional[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.discovery_timestamp is None:
            self.discovery_timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class DiscoveryStats:
    """Statistics from a discovery run"""
    total_servers: int
    servers_discovered: int
    discovery_timestamp: str
    registry_url: str
    duration_seconds: float


class MCPServerRegistryClient:
    """
    Client for discovering MCPs from the Official Model Context Protocol Registry.
    
    The Official Registry is hosted at: registry.modelcontextprotocol.io
    It serves a JSON file containing all registered MCPs.
    
    Usage:
        client = MCPServerRegistryClient()
        servers = await client.discover_all_servers()
        top_30 = client.get_top_servers(limit=30)
    """
    
    # Official registry endpoints
    REGISTRY_ROOT = "https://registry.modelcontextprotocol.io"
    REGISTRY_INDEX = f"{REGISTRY_ROOT}/servers.json"
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize the registry client.
        
        Args:
            cache_dir: Optional directory for caching registry data.
                      Defaults to ./data/mcp_cache/
        """
        self.cache_dir = cache_dir or Path("./data/mcp_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "registry_cache.json"
        
        self.servers: List[MCPServerEntry] = []
        self.stats: Optional[DiscoveryStats] = None
        self.last_error: Optional[str] = None
    
    def fetch_registry_json(self, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Fetch the registry index JSON from the Official MCP Registry.
        
        Args:
            use_cache: If True, use cached data if available and not stale
            
        Returns:
            Parsed JSON dict of registry data, or None if fetch fails
        """
        # Try cache first
        if use_cache and self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    logger.info(f"Loaded registry from cache: {self.cache_file}")
                    return cached_data
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
                pass
        
        # Fetch from remote
        try:
            logger.info(f"Fetching Official MCP Registry from: {self.REGISTRY_INDEX}")
            with urllib.request.urlopen(self.REGISTRY_INDEX, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                
            # Cache the result
            try:
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                logger.info(f"Cached registry to: {self.cache_file}")
            except Exception as e:
                logger.warning(f"Failed to cache registry: {e}")
            
            return data
            
        except urllib.error.URLError as e:
            self.last_error = f"Failed to fetch registry: {str(e)}"
            logger.error(self.last_error)
            return None
        except json.JSONDecodeError as e:
            self.last_error = f"Invalid JSON in registry response: {str(e)}"
            logger.error(self.last_error)
            return None
        except Exception as e:
            self.last_error = f"Unexpected error fetching registry: {str(e)}"
            logger.error(self.last_error)
            return None
    
    def parse_registry_data(self, registry_data: Dict[str, Any]) -> None:
        """
        Parse raw registry JSON and convert to MCPServerEntry objects.
        
        Args:
            registry_data: Raw JSON dict from Official Registry
        """
        self.servers = []
        
        # Official registry usually has servers in a "servers" key
        servers_list = registry_data.get("servers", [])
        if not servers_list:
            # Try alternative structure
            servers_list = [v for k, v in registry_data.items() if isinstance(v, dict)]
        
        for server_data in servers_list:
            try:
                # Extract required fields with safe access
                entry = MCPServerEntry(
                    name=server_data.get("name", "unknown"),
                    author=server_data.get("author", server_data.get("creator", "unknown")),
                    homepage=server_data.get("homepage"),
                    repository=server_data.get("repository", server_data.get("repo", "")),
                    description=server_data.get("description", ""),
                    sources=server_data.get("sources", []),
                    capabilities=server_data.get("capabilities", []),
                    created_at=server_data.get("created_at"),
                    updated_at=server_data.get("updated_at"),
                    version=server_data.get("version"),
                    tags=server_data.get("tags", []),
                )
                self.servers.append(entry)
                
            except Exception as e:
                logger.warning(f"Failed to parse server entry: {e}")
                continue
        
        logger.info(f"Parsed {len(self.servers)} MCP servers from registry")
    
    def score_servers(self) -> None:
        """
        Score servers based on heuristics for prioritization.
        
        Scoring factors:
        - Official registry verification (implicit)
        - Number of capabilities (more = higher score)
        - Presence of homepage (professionalism indicator)
        - Repository activity (if available)
        """
        for server in self.servers:
            score = 0.0
            
            # Capability diversity (0-40 points)
            capability_count = len(server.capabilities) if server.capabilities else 0
            score += min(40, capability_count * 10)
            
            # Homepage presence (10 points)
            if server.homepage:
                score += 10
            
            # Repository quality signals
            if server.repository:
                score += 10
                # GitHub repos get bonus
                if "github.com" in server.repository:
                    score += 5
                # Active repos (heuristic: recent updates)
                if server.updated_at:
                    score += 5
            
            # Description quality (0-15 points)
            if server.description:
                desc_length = len(server.description)
                score += min(15, (desc_length // 50))
            
            server.priority_score = score
        
        # Sort by score descending
        self.servers.sort(key=lambda s: s.priority_score, reverse=True)
        logger.info(f"Scored and ranked {len(self.servers)} servers")
    
    async def discover_all_servers(self, use_cache: bool = True) -> List[MCPServerEntry]:
        """
        Discover all servers from the Official Registry.
        
        Full workflow:
        1. Fetch registry JSON
        2. Parse into MCPServerEntry objects
        3. Score and rank
        
        Args:
            use_cache: Use cached registry data if available
            
        Returns:
            List of MCPServerEntry objects, sorted by priority
        """
        start_time = datetime.utcnow()
        
        # Fetch
        registry_data = self.fetch_registry_json(use_cache=use_cache)
        if not registry_data:
            logger.error("Failed to fetch registry data")
            return []
        
        # Parse
        self.parse_registry_data(registry_data)
        
        # Score
        self.score_servers()
        
        # Record stats
        duration = (datetime.utcnow() - start_time).total_seconds()
        self.stats = DiscoveryStats(
            total_servers=len(registry_data.get("servers", [])),
            servers_discovered=len(self.servers),
            discovery_timestamp=start_time.isoformat(),
            registry_url=self.REGISTRY_INDEX,
            duration_seconds=duration,
        )
        
        logger.info(f"Discovery complete: {len(self.servers)} servers discovered in {duration:.2f}s")
        return self.servers
    
    def get_top_servers(self, limit: int = 30) -> List[MCPServerEntry]:
        """
        Get the top N servers by priority score.
        
        Args:
            limit: Number of top servers to return (default 30)
            
        Returns:
            List of top MCPServerEntry objects
        """
        return self.servers[:limit]
    
    def export_candidates(self, filepath: Path, limit: int = 30) -> bool:
        """
        Export top servers to mcp_candidates.json file.
        
        This is the seed dataset for Week 2 introspection.
        
        Args:
            filepath: Path to export to
            limit: Number of top servers to export (default 30)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            top_servers = self.get_top_servers(limit=limit)
            candidates_data = {
                "metadata": {
                    "export_timestamp": datetime.utcnow().isoformat(),
                    "total_exported": len(top_servers),
                    "registry_url": self.REGISTRY_INDEX,
                    "ranking_method": "heuristic (capabilities, repo, homepage, descriptions)",
                },
                "servers": [s.to_dict() for s in top_servers],
            }
            
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(candidates_data, f, indent=2)
            
            logger.info(f"Exported {len(top_servers)} candidate servers to: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export candidates: {e}")
            return False
    
    def export_stats(self, filepath: Path) -> bool:
        """
        Export discovery statistics to a file.
        
        Args:
            filepath: Path to export stats to
            
        Returns:
            True if successful, False otherwise
        """
        if not self.stats:
            logger.warning("No stats available to export")
            return False
        
        try:
            stats_data = {
                "discovery_stats": asdict(self.stats),
                "server_count_by_capability": self._count_by_capability(),
                "top_10_servers": [s.to_dict() for s in self.get_top_servers(limit=10)],
            }
            
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, indent=2)
            
            logger.info(f"Exported discovery stats to: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export stats: {e}")
            return False
    
    def _count_by_capability(self) -> Dict[str, int]:
        """Count servers by capability type"""
        counts = {}
        for server in self.servers:
            for cap in server.capabilities:
                counts[cap] = counts.get(cap, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


async def main():
    """
    Simple main entry point for testing discovery.
    
    Usage: python -m mcp.discovery.mcp_server_registry_client
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    client = MCPServerRegistryClient()
    
    # Discover all servers
    servers = await client.discover_all_servers(use_cache=False)
    print(f"\n✓ Discovered {len(servers)} MCP servers")
    
    # Export top 30 as candidates
    candidates_file = Path("./data/mcp_candidates.json")
    if client.export_candidates(candidates_file):
        print(f"✓ Exported top 30 candidates to: {candidates_file}")
    
    # Export stats
    stats_file = Path("./data/mcp_discovery_stats.json")
    if client.export_stats(stats_file):
        print(f"✓ Exported discovery stats to: {stats_file}")
    
    # Show top 10
    print("\nTop 10 Most Prioritized MCPs:")
    print("-" * 80)
    for i, server in enumerate(client.get_top_servers(limit=10), 1):
        print(f"{i:2}. {server.name:30} | Score: {server.priority_score:6.1f} | Caps: {len(server.capabilities)}")


if __name__ == "__main__":
    asyncio.run(main())
