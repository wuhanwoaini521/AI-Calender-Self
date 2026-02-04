"""AI Router v2 - With Tools / Skills / MCP Support"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
import asyncio

from ..routers.auth import get_current_user
from ..models.schemas import APIResponse
from ..services.ai_service_v2 import ai_service_v2
from ..tools.registry import registry as tool_registry
from ..skills.registry import skill_registry, SkillContext
from datetime import datetime

router = APIRouter(prefix="/ai/v2", tags=["AI v2"])


class ChatRequest(BaseModel):
    """Chat request"""
    message: str
    history: Optional[List[Dict[str, str]]] = []
    context: Optional[Dict[str, Any]] = None
    use_skills: bool = True


class ChatResponse(BaseModel):
    """Chat response chunk"""
    type: str  # "text", "tool_call", "skill_start", "skill_result"
    content: Optional[str] = None
    tool: Optional[str] = None
    skill: Optional[str] = None
    success: Optional[bool] = None
    result: Optional[Any] = None
    message: Optional[str] = None
    data: Optional[Any] = None
    steps: Optional[List[Dict]] = None


class ToolCallRequest(BaseModel):
    """Direct tool call request"""
    tool: str
    params: Dict[str, Any]


class SkillCallRequest(BaseModel):
    """Direct skill call request"""
    skill: str
    params: Optional[Dict[str, Any]] = {}


class MCPRequest(BaseModel):
    """MCP protocol request"""
    request: Dict[str, Any]


@router.post("/chat", response_model=None)
async def chat(
    req: ChatRequest,
    current_user = Depends(get_current_user),
):
    """
    Chat with AI assistant with tool calling support
    
    Returns a streaming response with text and tool call results
    """
    messages = (req.history or []) + [{"role": "user", "content": req.message}]
    
    async def event_generator():
        try:
            if req.use_skills:
                async for chunk in ai_service_v2.chat_with_skills(
                    messages=messages,
                    user_id=current_user.id,
                    context=req.context,
                ):
                    yield f"data: {chunk}\n\n"
            else:
                async for chunk in ai_service_v2.chat(
                    messages=messages,
                    user_id=current_user.id,
                    context=req.context,
                    use_tools=True,
                ):
                    yield f"data: {chunk}\n\n"
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )


@router.post("/tools/call")
async def call_tool(
    req: ToolCallRequest,
    current_user = Depends(get_current_user),
):
    """Call a tool directly"""
    # Add user_id to params
    params = {**req.params, "user_id": current_user.id}
    
    result = await tool_registry.execute(req.tool, **params)
    
    return APIResponse(
        success=result.success,
        message=result.message,
        data=result.data,
    )


@router.get("/tools")
async def list_tools(
    current_user = Depends(get_current_user),
):
    """List available tools"""
    tools = ai_service_v2.get_available_tools()
    return APIResponse(
        success=True,
        data={"tools": tools},
    )


@router.post("/skills/call")
async def call_skill(
    req: SkillCallRequest,
    current_user = Depends(get_current_user),
):
    """Call a skill directly"""
    context = SkillContext(
        user_id=current_user.id,
        current_date=datetime.utcnow(),
    )
    
    params = {**req.params, "user_id": current_user.id}
    
    result = await skill_registry.execute(req.skill, context, **params)
    
    return APIResponse(
        success=result.success,
        message=result.message,
        data={
            "data": result.data,
            "steps": [s.model_dump() for s in result.steps],
        },
    )


@router.get("/skills")
async def list_skills(
    current_user = Depends(get_current_user),
):
    """List available skills"""
    skills = ai_service_v2.get_available_skills()
    return APIResponse(
        success=True,
        data={"skills": skills},
    )


@router.post("/mcp")
async def mcp_endpoint(
    req: MCPRequest,
):
    """MCP protocol endpoint"""
    response = await ai_service_v2.mcp_handle(req.request)
    return response


# Legacy compatibility routes
@router.post("/insights")
async def get_insights(
    current_user = Depends(get_current_user),
):
    """Get AI insights for the user (legacy)"""
    from ..services.ai_service import ai_service
    
    insights = ai_service.generate_suggestions(
        current_user.id,
        datetime.utcnow()
    )
    
    return APIResponse(
        success=True,
        data={"insights": insights},
    )
