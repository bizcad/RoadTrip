"""
MCP Discovery Module

Provides tools for discovering and analyzing MCPs from the Official Registry.

Classes:
    RegistryClient - Query Official MCP Registry API
    MCPInspector - Clone and introspect MCP repositories  
    SchemaExtractor - Extract structured data from MCPs
    AuditGenerator - Generate analysis reports

Usage:
    from src.mcp.discovery import RegistryClient
    client = RegistryClient()
    servers = await client.get_servers()
"""

__version__ = "0.1.0"
__all__ = [
    "RegistryClient",
    "MCPInspector", 
    "SchemaExtractor",
    "AuditGenerator",
]

# TO BE IMPLEMENTED IN WEEK 1-3
# from .registry_client import RegistryClient
# from .mcp_inspector import MCPInspector
# from .schema_extractor import SchemaExtractor
# from .audit import AuditGenerator
