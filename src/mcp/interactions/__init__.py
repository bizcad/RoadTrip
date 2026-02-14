"""
MCP Interactions Module

Provides runtime interfaces for calling MCPs and managing their execution.

Classes:
    MCPClientAdapter - Call MCP tools at runtime
    TransportHandler - Handle stdio/sse/http communication
    EnvironmentInjector - Inject credentials safely
    MCPErrorHandler - Handle MCP errors gracefully

Usage:
    from src.mcp.interactions import MCPClientAdapter
    adapter = MCPClientAdapter(mcp_metadata, config)
    result = await adapter.call_tool("tool_name", {"arg": "value"})
"""

__version__ = "0.1.0"
__all__ = [
    "MCPClientAdapter",
    "TransportHandler",
    "EnvironmentInjector",
    "MCPErrorHandler",
]

# TO BE IMPLEMENTED IN WEEK 5-6
# from .mcp_client_adapter import MCPClientAdapter
# from .transport_handler import TransportHandler
# from .environment_injector import EnvironmentInjector
# from .error_handler import MCPErrorHandler
