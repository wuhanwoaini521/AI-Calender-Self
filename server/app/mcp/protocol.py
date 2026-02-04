"""MCP Protocol Definitions"""

from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field
from enum import Enum


class MCPErrorCode(str, Enum):
    """MCP error codes"""
    PARSE_ERROR = "-32700"
    INVALID_REQUEST = "-32600"
    METHOD_NOT_FOUND = "-32601"
    INVALID_PARAMS = "-32602"
    INTERNAL_ERROR = "-32603"
    TOOL_NOT_FOUND = "-32001"
    TOOL_EXECUTION_ERROR = "-32002"


class MCPError(Exception):
    """MCP error exception"""
    def __init__(self, code: MCPErrorCode, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        error = {
            "code": self.code.value if isinstance(self.code, MCPErrorCode) else self.code,
            "message": self.message,
        }
        if self.data:
            error["data"] = self.data
        return error


class MCPRequest(BaseModel):
    """MCP request"""
    jsonrpc: Literal["2.0"] = "2.0"
    id: Optional[str] = None
    method: str
    params: Optional[Dict[str, Any]] = None
    
    # MCP-specific metadata
    meta: Optional[Dict[str, Any]] = Field(default=None, alias="_meta")
    
    class Config:
        populate_by_name = True


class MCPResponse(BaseModel):
    """MCP response"""
    jsonrpc: Literal["2.0"] = "2.0"
    id: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    
    # MCP-specific metadata
    meta: Optional[Dict[str, Any]] = Field(default=None, alias="_meta")
    
    class Config:
        populate_by_name = True
    
    @classmethod
    def success(cls, id: str, result: Any, meta: Optional[Dict] = None) -> "MCPResponse":
        return cls(id=id, result=result, meta=meta)
    
    @classmethod
    def error(cls, id: str, error: MCPError, meta: Optional[Dict] = None) -> "MCPResponse":
        return cls(id=id, error=error.to_dict(), meta=meta)


class MCPToolInfo(BaseModel):
    """Tool information in MCP format"""
    name: str
    description: str
    inputSchema: Dict[str, Any]


class MCPCapability(BaseModel):
    """MCP capability"""
    name: str
    version: str


class MCPServerInfo(BaseModel):
    """MCP server information"""
    name: str = "AI Calendar MCP Server"
    version: str = "1.0.0"
    capabilities: List[MCPCapability] = [
        MCPCapability(name="tools", version="1.0.0"),
        MCPCapability(name="resources", version="1.0.0"),
    ]
