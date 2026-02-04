"""MCP Server Implementation"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from .protocol import (
    MCPRequest,
    MCPResponse,
    MCPError,
    MCPErrorCode,
    MCPServerInfo,
    MCPToolInfo,
)
from ..tools.registry import registry as tool_registry
from ..skills.registry import skill_registry


class MCPServer:
    """MCP Server for AI Calendar"""
    
    def __init__(self):
        self.info = MCPServerInfo()
    
    async def handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP request"""
        try:
            # Parse request
            mcp_request = MCPRequest(**request)
            
            # Route to appropriate handler
            method = mcp_request.method
            
            if method == "initialize":
                result = await self._handle_initialize(mcp_request.params or {})
            elif method == "tools/list":
                result = await self._handle_tools_list()
            elif method == "tools/call":
                result = await self._handle_tool_call(mcp_request.params or {})
            elif method == "resources/list":
                result = await self._handle_resources_list()
            elif method == "skills/list":
                result = await self._handle_skills_list()
            elif method == "skills/call":
                result = await self._handle_skill_call(mcp_request.params or {})
            else:
                raise MCPError(
                    MCPErrorCode.METHOD_NOT_FOUND,
                    f"Method not found: {method}"
                )
            
            return MCPResponse.success(
                id=mcp_request.id,
                result=result
            ).model_dump(exclude_none=True)
            
        except MCPError as e:
            return MCPResponse.error(
                id=request.get("id"),
                error=e
            ).model_dump(exclude_none=True)
        except Exception as e:
            return MCPResponse.error(
                id=request.get("id"),
                error=MCPError(
                    MCPErrorCode.INTERNAL_ERROR,
                    str(e)
                )
            ).model_dump(exclude_none=True)
    
    async def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request"""
        client_info = params.get("clientInfo", {})
        protocol_version = params.get("protocolVersion", "2024-11-05")
        
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": True},
                "resources": {"subscribe": True},
            },
            "serverInfo": {
                "name": self.info.name,
                "version": self.info.version,
            },
        }
    
    async def _handle_tools_list(self) -> Dict[str, Any]:
        """List available tools"""
        tools = tool_registry.list_tools()
        
        return {
            "tools": [t.to_mcp_schema() for t in tools]
        }
    
    async def _handle_tool_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            raise MCPError(
                MCPErrorCode.INVALID_PARAMS,
                "Missing tool name"
            )
        
        # Execute tool
        result = await tool_registry.execute(tool_name, **arguments)
        
        if not result.success:
            raise MCPError(
                MCPErrorCode.TOOL_EXECUTION_ERROR,
                result.error or "Tool execution failed",
                result.data
            )
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": result.message or "Success",
                }
            ],
            "data": result.data,
            "isError": False,
        }
    
    async def _handle_resources_list(self) -> Dict[str, Any]:
        """List available resources"""
        # Resources could be calendar events, user preferences, etc.
        return {
            "resources": [
                {
                    "uri": "calendar://events",
                    "name": "Calendar Events",
                    "mimeType": "application/json",
                    "description": "User's calendar events",
                },
                {
                    "uri": "calendar://insights",
                    "name": "AI Insights",
                    "mimeType": "application/json", 
                    "description": "AI-generated insights and suggestions",
                },
            ]
        }
    
    async def _handle_skills_list(self) -> Dict[str, Any]:
        """List available skills"""
        skills = skill_registry.list_skills()
        
        return {
            "skills": [s.to_dict() for s in skills]
        }
    
    async def _handle_skill_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a skill"""
        from ..skills.base import SkillContext
        
        skill_name = params.get("name")
        arguments = params.get("arguments", {})
        user_id = arguments.get("user_id")
        
        if not skill_name:
            raise MCPError(
                MCPErrorCode.INVALID_PARAMS,
                "Missing skill name"
            )
        
        # Build context
        context = SkillContext(
            user_id=user_id,
            current_date=datetime.utcnow(),
            selected_date=datetime.strptime(arguments.get("date"), "%Y-%m-%d") if "date" in arguments else None,
        )
        
        # Execute skill
        result = await skill_registry.execute(skill_name, context, **arguments)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": result.message,
                }
            ],
            "data": result.data,
            "steps": [s.model_dump() for s in result.steps],
            "isError": not result.success,
        }
    
    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """Get tools in OpenAI format"""
        return tool_registry.get_schemas(format="openai")
