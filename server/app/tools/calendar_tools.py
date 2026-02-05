"""Calendar-related tools"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import uuid4
from .base import Tool, ToolParameter, ToolResult, ToolParameterType
from ..models.database import db
from ..models.schemas import CalendarEvent, Reminder


class CreateEventTool(Tool):
    """创建新日历事件"""
    
    name = "create_event"
    description = "创建一个新的日历事件/会议/日程，包含标题、开始时间、结束时间和可选的提醒"
    parameters = [
        ToolParameter(
            name="user_id",
            description="创建事件的用户ID",
            type=ToolParameterType.STRING,
            required=True,
        ),
        ToolParameter(
            name="title",
            description="事件标题，例如：会议、约会、聚餐",
            type=ToolParameterType.STRING,
            required=True,
        ),
        ToolParameter(
            name="start_time",
            description="开始时间，ISO 8601格式，例如：2026-02-05T11:00:00",
            type=ToolParameterType.STRING,
            required=True,
        ),
        ToolParameter(
            name="end_time",
            description="结束时间，ISO 8601格式，例如：2026-02-05T12:00:00",
            type=ToolParameterType.STRING,
            required=True,
        ),
        ToolParameter(
            name="description",
            description="Optional description of the event",
            type=ToolParameterType.STRING,
            required=False,
            default="",
        ),
        ToolParameter(
            name="all_day",
            description="Whether this is an all-day event",
            type=ToolParameterType.BOOLEAN,
            required=False,
            default=False,
        ),
        ToolParameter(
            name="location",
            description="Optional location of the event",
            type=ToolParameterType.STRING,
            required=False,
            default="",
        ),
        ToolParameter(
            name="color",
            description="Color for the event (hex format, e.g., #3b82f6)",
            type=ToolParameterType.STRING,
            required=False,
            default="#3b82f6",
        ),
        ToolParameter(
            name="reminders",
            description="List of reminders with type and minutes_before",
            type=ToolParameterType.ARRAY,
            required=False,
            default=[],
            items={
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["notification", "email"]},
                    "minutes_before": {"type": "integer"},
                },
            },
        ),
    ]
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            # Parse times
            start_time = datetime.fromisoformat(kwargs["start_time"].replace("Z", "+00:00"))
            end_time = datetime.fromisoformat(kwargs["end_time"].replace("Z", "+00:00"))
            
            # Validate time range
            if end_time <= start_time:
                return ToolResult.error("End time must be after start time")
            
            # Create event
            event = db.create_event(
                user_id=kwargs["user_id"],
                title=kwargs["title"],
                start_time=start_time,
                end_time=end_time,
                description=kwargs.get("description", ""),
                all_day=kwargs.get("all_day", False),
                location=kwargs.get("location", ""),
                color=kwargs.get("color", "#3b82f6"),
                reminders=kwargs.get("reminders", []),
            )
            
            return ToolResult.ok(
                data=event.model_dump(by_alias=True, mode='json'),
                message=f"Event '{kwargs['title']}' created successfully"
            )
        except Exception as e:
            return ToolResult.error(f"Failed to create event: {str(e)}")


class GetEventsTool(Tool):
    """Get calendar events for a date range"""
    
    name = "get_events"
    description = "Retrieve calendar events for a specific date range or view"
    parameters = [
        ToolParameter(
            name="user_id",
            description="ID of the user",
            type=ToolParameterType.STRING,
            required=True,
        ),
        ToolParameter(
            name="view",
            description="View type: day, week, or month",
            type=ToolParameterType.STRING,
            required=False,
            default="day",
            enum=["day", "week", "month"],
        ),
        ToolParameter(
            name="date",
            description="Date in YYYY-MM-DD format",
            type=ToolParameterType.STRING,
            required=True,
        ),
    ]
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            user_id = kwargs["user_id"]
            view = kwargs.get("view", "day")
            date_str = kwargs["date"]
            
            # Parse date
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            # Calculate date range based on view
            if view == "day":
                start = target_date.replace(hour=0, minute=0, second=0)
                end = target_date.replace(hour=23, minute=59, second=59)
            elif view == "week":
                start = target_date - timedelta(days=target_date.weekday())
                start = start.replace(hour=0, minute=0, second=0)
                end = start + timedelta(days=6)
                end = end.replace(hour=23, minute=59, second=59)
            elif view == "month":
                from dateutil.relativedelta import relativedelta
                start = target_date.replace(day=1, hour=0, minute=0, second=0)
                end = (start + relativedelta(months=1)) - timedelta(seconds=1)
            else:
                return ToolResult.error(f"Invalid view: {view}")
            
            # Get events
            events = db.get_events_by_date_range(user_id, start, end)
            
            return ToolResult.ok(
                data={
                    "events": [e.model_dump(by_alias=True, mode='json') for e in events],
                    "count": len(events),
                    "view": view,
                    "date": date_str,
                },
                message=f"Found {len(events)} events"
            )
        except Exception as e:
            return ToolResult.error(f"Failed to get events: {str(e)}")


class UpdateEventTool(Tool):
    """Update an existing calendar event"""
    
    name = "update_event"
    description = "Update an existing calendar event"
    parameters = [
        ToolParameter(
            name="user_id",
            description="ID of the user",
            type=ToolParameterType.STRING,
            required=True,
        ),
        ToolParameter(
            name="event_id",
            description="ID of the event to update",
            type=ToolParameterType.STRING,
            required=True,
        ),
        ToolParameter(
            name="title",
            description="New title for the event",
            type=ToolParameterType.STRING,
            required=False,
        ),
        ToolParameter(
            name="start_time",
            description="New start time in ISO 8601 format",
            type=ToolParameterType.STRING,
            required=False,
        ),
        ToolParameter(
            name="end_time",
            description="New end time in ISO 8601 format",
            type=ToolParameterType.STRING,
            required=False,
        ),
        ToolParameter(
            name="description",
            description="New description",
            type=ToolParameterType.STRING,
            required=False,
        ),
    ]
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            user_id = kwargs["user_id"]
            event_id = kwargs["event_id"]
            
            # Check event exists and belongs to user
            event = db.get_event_by_id(event_id)
            if not event or event.user_id != user_id:
                return ToolResult.error("Event not found or access denied")
            
            # Build updates
            updates = {}
            if "title" in kwargs:
                updates["title"] = kwargs["title"]
            if "description" in kwargs:
                updates["description"] = kwargs["description"]
            if "start_time" in kwargs:
                updates["start_time"] = datetime.fromisoformat(kwargs["start_time"].replace("Z", "+00:00"))
            if "end_time" in kwargs:
                updates["end_time"] = datetime.fromisoformat(kwargs["end_time"].replace("Z", "+00:00"))
            
            # Update event
            updated = db.update_event(event_id, **updates)
            
            return ToolResult.ok(
                data=updated.model_dump(by_alias=True, mode='json'),
                message="Event updated successfully"
            )
        except Exception as e:
            return ToolResult.error(f"Failed to update event: {str(e)}")


class DeleteEventTool(Tool):
    """Delete a calendar event"""
    
    name = "delete_event"
    description = "Delete a calendar event by ID"
    parameters = [
        ToolParameter(
            name="user_id",
            description="ID of the user",
            type=ToolParameterType.STRING,
            required=True,
        ),
        ToolParameter(
            name="event_id",
            description="ID of the event to delete",
            type=ToolParameterType.STRING,
            required=True,
        ),
    ]
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            user_id = kwargs["user_id"]
            event_id = kwargs["event_id"]
            
            # Check event exists and belongs to user
            event = db.get_event_by_id(event_id)
            if not event or event.user_id != user_id:
                return ToolResult.error("Event not found or access denied")
            
            # Delete event
            db.delete_event(event_id)
            
            return ToolResult.ok(message="Event deleted successfully")
        except Exception as e:
            return ToolResult.error(f"Failed to delete event: {str(e)}")


class FindFreeSlotsTool(Tool):
    """Find free time slots in a day"""
    
    name = "find_free_slots"
    description = "Find available time slots for a specific date"
    parameters = [
        ToolParameter(
            name="user_id",
            description="ID of the user",
            type=ToolParameterType.STRING,
            required=True,
        ),
        ToolParameter(
            name="date",
            description="Date to check in YYYY-MM-DD format",
            type=ToolParameterType.STRING,
            required=True,
        ),
        ToolParameter(
            name="duration_minutes",
            description="Required duration in minutes",
            type=ToolParameterType.INTEGER,
            required=False,
            default=60,
        ),
        ToolParameter(
            name="start_hour",
            description="Start of workday (default 9)",
            type=ToolParameterType.INTEGER,
            required=False,
            default=9,
        ),
        ToolParameter(
            name="end_hour",
            description="End of workday (default 17)",
            type=ToolParameterType.INTEGER,
            required=False,
            default=17,
        ),
    ]
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            user_id = kwargs["user_id"]
            date_str = kwargs["date"]
            duration = kwargs.get("duration_minutes", 60)
            start_hour = kwargs.get("start_hour", 9)
            end_hour = kwargs.get("end_hour", 17)
            
            # Get events for the day
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
            start = target_date.replace(hour=0, minute=0)
            end = target_date.replace(hour=23, minute=59)
            
            events = db.get_events_by_date_range(user_id, start, end)
            sorted_events = sorted(events, key=lambda x: x.start_time)
            
            # Find free slots
            work_start = target_date.replace(hour=start_hour, minute=0)
            work_end = target_date.replace(hour=end_hour, minute=0)
            
            free_slots = []
            current_time = work_start
            
            for event in sorted_events:
                if event.start_time > current_time:
                    slot_duration = (event.start_time - current_time).total_seconds() / 60
                    if slot_duration >= duration:
                        free_slots.append({
                            "start": current_time.strftime("%H:%M"),
                            "end": event.start_time.strftime("%H:%M"),
                            "duration_minutes": int(slot_duration),
                        })
                current_time = max(current_time, event.end_time)
            
            # Check for slot after last event
            if current_time < work_end:
                slot_duration = (work_end - current_time).total_seconds() / 60
                if slot_duration >= duration:
                    free_slots.append({
                        "start": current_time.strftime("%H:%M"),
                        "end": work_end.strftime("%H:%M"),
                        "duration_minutes": int(slot_duration),
                    })
            
            return ToolResult.ok(
                data={
                    "free_slots": free_slots,
                    "date": date_str,
                    "requested_duration": duration,
                },
                message=f"Found {len(free_slots)} available time slots"
            )
        except Exception as e:
            return ToolResult.error(f"Failed to find free slots: {str(e)}")


class DetectConflictsTool(Tool):
    """Detect scheduling conflicts"""
    
    name = "detect_conflicts"
    description = "Detect scheduling conflicts for upcoming events"
    parameters = [
        ToolParameter(
            name="user_id",
            description="ID of the user",
            type=ToolParameterType.STRING,
            required=True,
        ),
        ToolParameter(
            name="days",
            description="Number of days to check ahead",
            type=ToolParameterType.INTEGER,
            required=False,
            default=7,
        ),
    ]
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            user_id = kwargs["user_id"]
            days = kwargs.get("days", 7)
            
            # Get events for the period
            now = datetime.utcnow()
            end = now + timedelta(days=days)
            
            events = db.get_events_by_date_range(user_id, now, end)
            sorted_events = sorted(events, key=lambda x: x.start_time)
            
            # Find conflicts
            conflicts = []
            for i in range(len(sorted_events) - 1):
                current = sorted_events[i]
                next_event = sorted_events[i + 1]
                
                if current.end_time > next_event.start_time:
                    conflicts.append({
                        "event1": {
                            "id": current.id,
                            "title": current.title,
                            "start": current.start_time.isoformat(),
                            "end": current.end_time.isoformat(),
                        },
                        "event2": {
                            "id": next_event.id,
                            "title": next_event.title,
                            "start": next_event.start_time.isoformat(),
                            "end": next_event.end_time.isoformat(),
                        },
                        "overlap_minutes": int(
                            (min(current.end_time, next_event.end_time) - 
                             max(current.start_time, next_event.start_time)).total_seconds() / 60
                        ),
                    })
            
            return ToolResult.ok(
                data={
                    "conflicts": conflicts,
                    "count": len(conflicts),
                    "checked_events": len(events),
                },
                message=f"Found {len(conflicts)} scheduling conflicts" if conflicts else "No conflicts found"
            )
        except Exception as e:
            return ToolResult.error(f"Failed to detect conflicts: {str(e)}")
