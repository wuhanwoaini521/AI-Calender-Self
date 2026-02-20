from fastapi import APIRouter, HTTPException, Depends, Header
from typing import List, Optional
from datetime import datetime

from app.models.calendar import CalendarEvent, CalendarEventCreate, CalendarEventUpdate
from app.models.chat import ChatRequest, ChatResponse
from app.services.calendar_service import CalendarService
from app.services.chat_service import ChatService
from app.mcp.server import MCPServer
from app.config import get_settings

# 创建路由
router = APIRouter()

# 全局日历服务实例
calendar_service = CalendarService()


def get_chat_service(api_key: Optional[str] = Header(None, alias="X-API-Key")) -> ChatService:
    """
    依赖注入：根据请求头中的 API Key 创建 ChatService
    如果没有传 API Key，使用 .env 中配置的默认 Key
    
    Args:
        api_key: 用户的 API Key（可选）
        
    Returns:
        ChatService 实例
    """
    settings = get_settings()
    
    # 优先使用请求头中的 Key，否则使用配置文件中的默认 Key
    final_api_key = api_key or settings.api_key
    
    if not final_api_key:
        raise HTTPException(
            status_code=401, 
            detail="API Key is required. Please provide X-API-Key header or configure API_KEY in .env file."
        )
    
    mcp_server = MCPServer(calendar_service)
    return ChatService(mcp_server, api_key=final_api_key)


# ==================== 对话接口 ====================

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    对话接口 - 通过自然语言操作日历
    
    可以在请求头中提供: X-API-Key: your_api_key
    如果不提供，将使用 .env 中配置的默认 API Key
    
    示例:
    - "帮我添加一个明天下午3点的会议"
    - "显示今天的所有日程"
    - "删除下周的项目评审会议"
    """
    try:
        response = await chat_service.process_message(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 日历事件 CRUD 接口 ====================

@router.post("/events", response_model=CalendarEvent)
async def create_event(event: CalendarEventCreate):
    """创建日历事件"""
    try:
        created_event = calendar_service.create_event(event)
        return created_event
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/events", response_model=List[CalendarEvent])
async def list_events(
    start_date: str = None,
    end_date: str = None,
    keyword: str = None
):
    """
    获取日历事件列表
    
    参数:
    - start_date: 开始日期（可选），ISO 8601 格式
    - end_date: 结束日期（可选），ISO 8601 格式
    - keyword: 搜索关键词（可选）
    """
    try:
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        events = calendar_service.list_events(
            start_date=start,
            end_date=end,
            keyword=keyword
        )
        return events
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/events/{event_id}", response_model=CalendarEvent)
async def get_event(event_id: str):
    """获取单个日历事件"""
    event = calendar_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.put("/events/{event_id}", response_model=CalendarEvent)
async def update_event(event_id: str, event_update: CalendarEventUpdate):
    """更新日历事件"""
    event = calendar_service.update_event(event_id, event_update)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.delete("/events/{event_id}")
async def delete_event(event_id: str):
    """删除日历事件"""
    success = calendar_service.delete_event(event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted successfully", "event_id": event_id}


# ==================== 工具和技能信息接口 ====================

@router.get("/tools")
async def get_available_tools():
    """获取可用的 MCP 工具列表"""
    from app.mcp.tools import MCPTools
    return {"tools": MCPTools.get_tool_definitions()}


@router.get("/skills")
async def get_available_skills():
    """获取可用的 Skills 列表"""
    from app.skills.loader import skill_loader
    return {
        "skills": skill_loader.get_skill_names(),
        "details": skill_loader.get_all_skills()
    }