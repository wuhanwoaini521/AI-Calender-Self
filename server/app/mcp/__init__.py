"""
MCP (Model Context Protocol) Support

MCP is an open protocol that standardizes how AI models interact with external tools and data.
This module provides MCP-compliant interfaces for the calendar system.

Reference: https://modelcontextprotocol.io
"""

from .server import MCPServer
from .protocol import (
    MCPRequest,
    MCPResponse,
    MCPError,
    MCPCapability,
)

__all__ = [
    "MCPServer",
    "MCPRequest",
    "MCPResponse", 
    "MCPError",
    "MCPCapability",
]
