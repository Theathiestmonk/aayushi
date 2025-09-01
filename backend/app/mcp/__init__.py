"""
MCP (Model Context Protocol) Module for AI Dietitian
Provides standardized tool interfaces for AI agents to access external services
"""

from .mcp_server import MCPServer, mcp_server
from .mcp_client import MCPClient
from .tool_registry import ToolRegistry, tool_registry
from .schemas import MCPTool, MCPCall, MCPResponse, ToolExecutionResult
from .exceptions import MCPError, ToolNotFoundError, InvalidParametersError

__version__ = "1.0.0"
__all__ = [
    "MCPServer",
    "mcp_server", 
    "MCPClient",
    "ToolRegistry",
    "tool_registry",
    "MCPTool",
    "MCPCall", 
    "MCPResponse",
    "ToolExecutionResult",
    "MCPError",
    "ToolNotFoundError",
    "InvalidParametersError"
]




