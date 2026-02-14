"""
MCP Discovery Module

Provides tools for discovering and analyzing MCPs from the Official Registry.

Classes:
    MCPServerRegistryClient - Query Official MCP Registry API (registry.modelcontextprotocol.io)
    MCPInspector - Clone and introspect MCP repositories  
    SchemaExtractor - Extract structured data from MCPs
    AuditGenerator - Generate analysis reports

Usage:
    from src.mcp.discovery import MCPServerRegistryClient
    client = MCPServerRegistryClient()
    servers = await client.get_servers()
"""

__version__ = "0.1.0"
__all__ = [
    "MCPServerRegistryClient",
    "MCPInspector", 
    "SchemaExtractor",
    "AuditGenerator",
]

# TO BE IMPLEMENTED IN WEEK 1-3
# from .mcp_server_registry_client import MCPServerRegistryClient
# from .mcp_inspector import MCPInspector
# from .schema_extractor import SchemaExtractor
# from .audit import AuditGenerator
