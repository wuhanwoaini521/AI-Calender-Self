from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime
from typing import List, Optional
from ..models.schemas import CalendarEvent, CalendarEventCreate, APIResponse
from ..models.database import db
from ..routers.auth import get_current_user
from dateutil import parser

router = APIRouter(prefix="/events", tags=["Events"])


def parse_datetime(dt_str: str) -> datetime:
    """Parse datetime string to datetime object"""
    try:
        return parser.isoparse(dt_str)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid datetime format: {dt_str}"
        )


@router.post("/", response_model=APIResponse)
async def create_event(
    event: CalendarEventCreate,
    current_user = Depends(get_current_user)
):
    # Validate times
    if event.end_time <= event.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    
    # Create event
    new_event = db.create_event(
        user_id=current_user.id,
        title=event.title,
        start_time=event.start_time,
        end_time=event.end_time,
        description=event.description,
        all_day=event.all_day,
        location=event.location,
        color=event.color,
        reminders=event.reminders
    )
    
    return APIResponse(
        success=True,
        data={"event": new_event.model_dump(by_alias=True)}
    )


@router.get("/", response_model=APIResponse)
async def get_events(
    view: Optional[str] = Query(None, description="View type: month, week, day"),
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    current_user = Depends(get_current_user)
):
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
        
        from datetime import timedelta
        
        if view == "day":
            start = target_date.replace(hour=0, minute=0, second=0)
            end = target_date.replace(hour=23, minute=59, second=59)
        elif view == "week":
            from datetime import timedelta
            start = target_date - timedelta(days=target_date.weekday())
            start = start.replace(hour=0, minute=0, second=0)
            end = start + timedelta(days=6)
            end = end.replace(hour=23, minute=59, second=59)
        elif view == "month":
            from dateutil.relativedelta import relativedelta
            start = target_date.replace(day=1, hour=0, minute=0, second=0)
            end = (start + relativedelta(months=1)) - timedelta(seconds=1)
        else:
            # Default: get all events
            events = db.get_events_by_user(current_user.id)
            return APIResponse(success=True, data={"events": [e.model_dump(by_alias=True) for e in events]})
        
        events = db.get_events_by_date_range(current_user.id, start, end)
    else:
        events = db.get_events_by_user(current_user.id)
    
    return APIResponse(
        success=True,
        data={"events": [e.model_dump(by_alias=True) for e in events]}
    )


@router.get("/upcoming", response_model=APIResponse)
async def get_upcoming_events(
    limit: int = Query(5, ge=1, le=20),
    current_user = Depends(get_current_user)
):
    events = db.get_upcoming_events(current_user.id, limit)
    return APIResponse(
        success=True,
        data={"events": [e.model_dump(by_alias=True) for e in events]}
    )


@router.get("/{event_id}", response_model=APIResponse)
async def get_event(
    event_id: str,
    current_user = Depends(get_current_user)
):
    event = db.get_event_by_id(event_id)
    
    if not event or event.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return APIResponse(
        success=True,
        data={"event": event.model_dump(by_alias=True)}
    )


@router.put("/{event_id}", response_model=APIResponse)
async def update_event(
    event_id: str,
    event_update: CalendarEventCreate,
    current_user = Depends(get_current_user)
):
    # Check event exists and belongs to user
    existing = db.get_event_by_id(event_id)
    if not existing or existing.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Validate times if provided
    if event_update.end_time <= event_update.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    
    # Build update dict
    updates = {
        "title": event_update.title,
        "description": event_update.description,
        "start_time": event_update.start_time,
        "end_time": event_update.end_time,
        "all_day": event_update.all_day,
        "location": event_update.location,
        "color": event_update.color,
    }
    
    # Handle reminders
    if event_update.reminders:
        from ..models.schemas import Reminder
        updates["reminders"] = [
            Reminder(
                id=__import__('uuid').uuid4(),
                type=r.get("type", "notification"),
                minutes_before=r.get("minutes_before") or r.get("minutesBefore", 15)
            )
            for r in event_update.reminders
        ]
    
    updated_event = db.update_event(event_id, **updates)
    
    return APIResponse(
        success=True,
        data={"event": updated_event.model_dump(by_alias=True)}
    )


@router.delete("/{event_id}", response_model=APIResponse)
async def delete_event(
    event_id: str,
    current_user = Depends(get_current_user)
):
    # Check event exists and belongs to user
    existing = db.get_event_by_id(event_id)
    if not existing or existing.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    db.delete_event(event_id)
    
    return APIResponse(
        success=True,
        message="Event deleted successfully"
    )
