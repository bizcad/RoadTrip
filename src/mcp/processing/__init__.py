"""
MCP Processing Module

Provides tools for converting MCPs to RoadTrip skills and creating persistent catalog.

Classes:
    CatalogBuilder - Create and manage SQLite catalog
    MCPToSkillConverter - Convert MCP metadata to RoadTrip SkillMetadata
    SkillFingerprinter - Create deterministic fingerprint from MCP
    MCPValidator - Security and safety validation

Usage:
    from src.mcp.processing import CatalogBuilder
    catalog = CatalogBuilder("./mcp_catalog.sqlite")
    await catalog.initialize_schema()
"""

__version__ = "0.1.0"
__all__ = [
    "CatalogBuilder",
    "MCPToSkillConverter",
    "SkillFingerprinter", 
    "MCPValidator",
]

# TO BE IMPLEMENTED IN WEEK 3-5
# from .catalog_builder import CatalogBuilder
# from .mcp_to_skill import MCPToSkillConverter
# from .fingerprinter import SkillFingerprinter
# from .validator import MCPValidator
