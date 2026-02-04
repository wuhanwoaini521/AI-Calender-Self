from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime
from typing import Optional, List
from ..models.schemas import AIChatRequest, AIChatResponse, APIResponse
from ..models.database import db
from ..routers.auth import get_current_user
from ..services.ai_service import ai_service
from dateutil import parser

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


@router.post("/chat", response_model=APIResponse)
async def chat(
    request: AIChatRequest,
    current_user = Depends(get_current_user)
):
    """Chat with AI assistant"""
    if not request.message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message is required"
        )
    
    # Save user message
    db.create_chat_message(
        user_id=current_user.id,
        role="user",
        content=request.message
    )
    
    # Get user's events for context
    events = []
    if request.context and request.context.get("selectedDate"):
        try:
            selected_date = parser.parse(request.context["selectedDate"])
            events = db.get_events_by_date_range(
                current_user.id,
                selected_date.replace(hour=0, minute=0),
                selected_date.replace(hour=23, minute=59)
            )
        except:
            pass
    else:
        events = db.get_events_by_user(current_user.id)[:10]
    
    # Generate AI response
    ai_response = ai_service.generate_response(
        request.message,
        {
            "currentDate": request.context.get("currentDate") if request.context else datetime.now().strftime("%Y-%m-%d"),
            "selectedDate": request.context.get("selectedDate") if request.context else None,
            "events": events
        }
    )
    
    # Save AI response
    db.create_chat_message(
        user_id=current_user.id,
        role="assistant",
        content=ai_response
    )
    
    return APIResponse(
        success=True,
        data={
            "message": ai_response,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@router.get("/insights", response_model=APIResponse)
async def get_insights(
    unread_only: bool = Query(False),
    current_user = Depends(get_current_user)
):
    """Get AI insights for user"""
    insights = db.get_insights_by_user(current_user.id, unread_only)
    return APIResponse(
        success=True,
        data={"insights": [i.model_dump() for i in insights]}
    )


@router.put("/insights/{insight_id}/read", response_model=APIResponse)
async def mark_insight_as_read(
    insight_id: str,
    current_user = Depends(get_current_user)
):
    """Mark an insight as read"""
    insight = db.mark_insight_as_read(insight_id)
    
    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight not found"
        )
    
    return APIResponse(
        success=True,
        data={"insight": insight.model_dump()}
    )


@router.get("/suggestions", response_model=APIResponse)
async def get_suggestions(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    current_user = Depends(get_current_user)
):
    """Get AI suggestions for the day"""
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    else:
        target_date = datetime.now()
    
    suggestions = ai_service.generate_suggestions(current_user.id, target_date)
    
    return APIResponse(
        success=True,
        data={"suggestions": suggestions}
    )


@router.post("/schedule", response_model=APIResponse)
async def generate_schedule(
    tasks: List[dict],
    date: Optional[str] = None,
    preferences: Optional[dict] = None,
    current_user = Depends(get_current_user)
):
    """Generate an optimized schedule for tasks"""
    if not tasks or not isinstance(tasks, list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tasks array is required"
        )
    
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    else:
        target_date = datetime.now()
    
    # Get existing events for the day
    existing_events = db.get_events_by_date_range(
        current_user.id,
        target_date.replace(hour=0, minute=0),
        target_date.replace(hour=23, minute=59)
    )
    
    include_breaks = preferences.get("includeBreaks", True) if preferences else True
    
    schedule = ai_service.generate_schedule(
        tasks,
        target_date,
        existing_events,
        include_breaks
    )
    
    return APIResponse(
        success=True,
        data={
            "schedule": schedule,
            "message": f"Generated schedule with {len(schedule)} tasks"
        }
    )
