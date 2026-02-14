"""
MCP Package

Provides tools for discovering, processing, and interacting with Model Context Protocol (MCP) servers.

Modules:
    discovery - Find and analyze MCPs from Official Registry
    processing - Convert MCPs to RoadTrip skills, create persistent catalog
    interactions - Call MCPs at runtime, manage execution

Architecture:
    discovery/     → Acquisition phase (learn what MCPs look like)
    processing/    → Conversion phase (map MCPs to RoadTrip skills)
    interactions/  → Execution phase (call MCPs at runtime)

By organizing as filesystem hierarchy, we make code discovery, testing, and maintenance easy.
Python naturally organizes packages this way, and IDEs support it perfectly.

Usage:
    from src.mcp.discovery import RegistryClient
    from src.mcp.processing import CatalogBuilder
    from src.mcp.interactions import MCPClientAdapter
"""

__version__ = "0.1.0"

# Schema version from Official Registry (2025-12-11)
SCHEMA_VERSION = "2025-12-11"
REGISTRY_API_URL = "https://registry.modelcontextprotocol.io/v0.1"
REGISTRY_SCHEMA_URL = f"https://static.modelcontextprotocol.io/schemas/{SCHEMA_VERSION}/server.schema.json"
