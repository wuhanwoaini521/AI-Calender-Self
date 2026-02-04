"""Base classes for Tools"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, Field
from enum import Enum


class ToolParameterType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


class ToolParameter(BaseModel):
    """Definition of a tool parameter"""
    name: str
    description: str
    type: ToolParameterType
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None
    items: Optional[Dict[str, Any]] = None  # For array type
    properties: Optional[Dict[str, Any]] = None  # For object type


class ToolResult(BaseModel):
    """Result of tool execution"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None

    @classmethod
    def ok(cls, data: Any = None, message: str = None) -> "ToolResult":
        return cls(success=True, data=data, message=message)

    @classmethod
    def error(cls, error: str, message: str = None) -> "ToolResult":
        return cls(success=False, error=error, message=message)


class Tool(ABC):
    """Base class for all tools"""
    
    # Tool metadata
    name: str
    description: str
    parameters: List[ToolParameter]
    
    def __init__(self):
        self._validate_tool()
    
    def _validate_tool(self):
        """Validate tool definition"""
        assert self.name, "Tool must have a name"
        assert self.description, "Tool must have a description"
        assert isinstance(self.parameters, list), "Parameters must be a list"
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters"""
        pass
    
    def to_openai_schema(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling schema"""
        properties = {}
        required = []
        
        for param in self.parameters:
            prop = {
                "type": param.type.value,
                "description": param.description,
            }
            if param.enum:
                prop["enum"] = param.enum
            if param.items:
                prop["items"] = param.items
            if param.properties:
                prop["properties"] = param.properties
            
            properties[param.name] = prop
            
            if param.required:
                required.append(param.name)
        
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }
    
    def to_mcp_schema(self) -> Dict[str, Any]:
        """Convert to MCP (Model Context Protocol) schema"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": {
                    param.name: {
                        "type": param.type.value,
                        "description": param.description,
                        **({"enum": param.enum} if param.enum else {}),
                        **({"items": param.items} if param.items else {}),
                        **({"properties": param.properties} if param.properties else {}),
                    }
                    for param in self.parameters
                },
                "required": [p.name for p in self.parameters if p.required],
            },
        }
    
    def validate_params(self, params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate input parameters"""
        for param in self.parameters:
            if param.required and param.name not in params:
                return False, f"Missing required parameter: {param.name}"
            
            if param.name in params and param.enum:
                if params[param.name] not in param.enum:
                    return False, f"Invalid value for {param.name}: {params[param.name]}"
        
        return True, None
