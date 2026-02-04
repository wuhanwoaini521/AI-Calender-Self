"""Tool Registry for managing all available tools"""

from typing import Dict, List, Type, Optional, Any
from .base import Tool, ToolResult


class ToolRegistry:
    """Registry for all tools"""
    
    _instance = None
    _tools: Dict[str, Tool] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, tool_class: Type[Tool]) -> Type[Tool]:
        """Register a tool class (can be used as decorator)"""
        tool = tool_class()
        self._tools[tool.name] = tool
        return tool_class
    
    def unregister(self, name: str):
        """Unregister a tool"""
        if name in self._tools:
            del self._tools[name]
    
    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self._tools.get(name)
    
    def list_tools(self) -> List[Tool]:
        """List all registered tools"""
        return list(self._tools.values())
    
    def get_schemas(self, format: str = "openai") -> List[Dict[str, Any]]:
        """Get all tool schemas in specified format"""
        tools = self.list_tools()
        if format == "openai":
            return [t.to_openai_schema() for t in tools]
        elif format == "mcp":
            return [t.to_mcp_schema() for t in tools]
        else:
            raise ValueError(f"Unknown format: {format}")
    
    async def execute(self, name: str, **params) -> ToolResult:
        """Execute a tool by name"""
        tool = self.get(name)
        if not tool:
            return ToolResult.error(f"Tool not found: {name}")
        
        # Validate parameters
        valid, error = tool.validate_params(params)
        if not valid:
            return ToolResult.error(error)
        
        # Execute tool
        try:
            result = await tool.execute(**params)
            return result
        except Exception as e:
            return ToolResult.error(f"Execution failed: {str(e)}")
    
    def clear(self):
        """Clear all registered tools"""
        self._tools.clear()


# Global registry instance
registry = ToolRegistry()
