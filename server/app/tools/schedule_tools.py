"""Schedule optimization tools"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from .base import Tool, ToolParameter, ToolResult, ToolParameterType
from ..models.database import db


class GenerateScheduleTool(Tool):
    """Generate an optimized schedule for tasks"""
    
    name = "generate_schedule"
    description = "Generate an optimized daily schedule for a list of tasks"
    parameters = [
        ToolParameter(
            name="user_id",
            description="ID of the user",
            type=ToolParameterType.STRING,
            required=True,
        ),
        ToolParameter(
            name="date",
            description="Date in YYYY-MM-DD format",
            type=ToolParameterType.STRING,
            required=True,
        ),
        ToolParameter(
            name="tasks",
            description="List of tasks to schedule",
            type=ToolParameterType.ARRAY,
            required=True,
            items={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "duration": {"type": "integer"},  # minutes
                    "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                },
            },
        ),
        ToolParameter(
            name="start_hour",
            description="Start of workday",
            type=ToolParameterType.INTEGER,
            required=False,
            default=9,
        ),
        ToolParameter(
            name="end_hour",
            description="End of workday",
            type=ToolParameterType.INTEGER,
            required=False,
            default=17,
        ),
    ]
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            user_id = kwargs["user_id"]
            date_str = kwargs["date"]
            tasks = kwargs["tasks"]
            start_hour = kwargs.get("start_hour", 9)
            end_hour = kwargs.get("end_hour", 17)
            
            # Get existing events
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
            day_start = target_date.replace(hour=0, minute=0)
            day_end = target_date.replace(hour=23, minute=59)
            
            existing_events = db.get_events_by_date_range(user_id, day_start, day_end)
            sorted_events = sorted(existing_events, key=lambda x: x.start_time)
            
            # Sort tasks by priority
            priority_order = {"high": 0, "medium": 1, "low": 2}
            sorted_tasks = sorted(tasks, key=lambda x: priority_order.get(x.get("priority", "medium"), 1))
            
            # Generate schedule
            schedule = []
            current_time = target_date.replace(hour=start_hour, minute=0)
            work_end = target_date.replace(hour=end_hour, minute=0)
            
            event_idx = 0
            
            for task in sorted_tasks:
                duration = task.get("duration", 60)
                task_end = current_time + timedelta(minutes=duration)
                
                # Skip past existing events
                while event_idx < len(sorted_events) and sorted_events[event_idx].end_time <= current_time:
                    event_idx += 1
                
                # Check if overlaps with next event
                if event_idx < len(sorted_events) and task_end > sorted_events[event_idx].start_time:
                    # Move current time to after this event
                    current_time = sorted_events[event_idx].end_time + timedelta(minutes=10)
                    event_idx += 1
                    continue
                
                if task_end > work_end:
                    break
                
                schedule.append({
                    "task": task["name"],
                    "start_time": current_time.strftime("%Y-%m-%d %H:%M"),
                    "end_time": task_end.strftime("%Y-%m-%d %H:%M"),
                    "duration": duration,
                    "priority": task.get("priority", "medium"),
                })
                
                current_time = task_end + timedelta(minutes=10)  # 10 min break
            
            return ToolResult.ok(
                data={
                    "schedule": schedule,
                    "date": date_str,
                    "scheduled_tasks": len(schedule),
                    "total_tasks": len(tasks),
                },
                message=f"Scheduled {len(schedule)} out of {len(tasks)} tasks"
            )
        except Exception as e:
            return ToolResult.error(f"Failed to generate schedule: {str(e)}")


class OptimizeScheduleTool(Tool):
    """Analyze and suggest optimizations for existing schedule"""
    
    name = "optimize_schedule"
    description = "Analyze schedule and suggest optimizations"
    parameters = [
        ToolParameter(
            name="user_id",
            description="ID of the user",
            type=ToolParameterType.STRING,
            required=True,
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
            date_str = kwargs["date"]
            
            # Get events
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
            day_start = target_date.replace(hour=0, minute=0)
            day_end = target_date.replace(hour=23, minute=59)
            
            events = db.get_events_by_date_range(user_id, day_start, day_end)
            sorted_events = sorted(events, key=lambda x: x.start_time)
            
            suggestions = []
            
            # Check for back-to-back meetings
            for i in range(len(sorted_events) - 1):
                current = sorted_events[i]
                next_event = sorted_events[i + 1]
                gap_minutes = (next_event.start_time - current.end_time).total_seconds() / 60
                
                if gap_minutes < 10:
                    suggestions.append({
                        "type": "buffer_time",
                        "severity": "medium",
                        "message": f"Consider adding buffer time between '{current.title}' and '{next_event.title}'",
                        "events": [current.id, next_event.id],
                    })
            
            # Check for lunch break
            has_lunch = any(
                12 <= e.start_time.hour <= 13 and 
                ("lunch" in e.title.lower() or "break" in e.title.lower())
                for e in events
            )
            if not has_lunch and len(events) > 3:
                suggestions.append({
                    "type": "lunch_break",
                    "severity": "high",
                    "message": "Consider scheduling a lunch break to maintain energy",
                })
            
            # Check for focus time
            has_focus = any(
                "focus" in e.title.lower() or "deep work" in e.title.lower()
                for e in events
            )
            if not has_focus and len(events) > 2:
                suggestions.append({
                    "type": "focus_time",
                    "severity": "medium",
                    "message": "Schedule a focus block for uninterrupted work",
                })
            
            # Check meeting load
            meetings = [e for e in events if any(word in e.title.lower() 
                        for word in ["meeting", "call", "sync", "standup"])]
            if len(meetings) > 4:
                suggestions.append({
                    "type": "meeting_load",
                    "severity": "high",
                    "message": f"You have {len(meetings)} meetings. Consider if some could be async.",
                })
            
            return ToolResult.ok(
                data={
                    "suggestions": suggestions,
                    "total_events": len(events),
                    "meetings": len(meetings),
                },
                message=f"Found {len(suggestions)} optimization suggestions"
            )
        except Exception as e:
            return ToolResult.error(f"Failed to optimize schedule: {str(e)}")


class SuggestBreaksTool(Tool):
    """Suggest optimal break times"""
    
    name = "suggest_breaks"
    description = "Suggest optimal times for breaks based on schedule"
    parameters = [
        ToolParameter(
            name="user_id",
            description="ID of the user",
            type=ToolParameterType.STRING,
            required=True,
        ),
        ToolParameter(
            name="date",
            description="Date in YYYY-MM-DD format",
            type=ToolParameterType.STRING,
            required=True,
        ),
        ToolParameter(
            name="work_duration",
            description="Maximum work duration before break (minutes)",
            type=ToolParameterType.INTEGER,
            required=False,
            default=90,
        ),
    ]
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            user_id = kwargs["user_id"]
            date_str = kwargs["date"]
            work_duration = kwargs.get("work_duration", 90)
            
            # Get events
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
            day_start = target_date.replace(hour=9, minute=0)
            day_end = target_date.replace(hour=17, minute=0)
            
            events = db.get_events_by_date_range(user_id, day_start, day_end)
            sorted_events = sorted(events, key=lambda x: x.start_time)
            
            breaks = []
            current_time = day_start
            
            for event in sorted_events:
                # Check if we need a break before this event
                if (event.start_time - current_time).total_seconds() / 60 >= work_duration:
                    suggested_break_start = current_time + timedelta(minutes=work_duration)
                    if suggested_break_start < event.start_time:
                        breaks.append({
                            "suggested_time": suggested_break_start.strftime("%H:%M"),
                            "duration_minutes": 15,
                            "reason": f"Work session exceeded {work_duration} minutes",
                        })
                
                current_time = max(current_time, event.end_time)
            
            # Check for end of day
            if (day_end - current_time).total_seconds() / 60 >= work_duration:
                breaks.append({
                    "suggested_time": "Afternoon",
                    "duration_minutes": 15,
                    "reason": "Long work session detected",
                })
            
            return ToolResult.ok(
                data={
                    "suggested_breaks": breaks,
                    "date": date_str,
                },
                message=f"Suggested {len(breaks)} break times"
            )
        except Exception as e:
            return ToolResult.error(f"Failed to suggest breaks: {str(e)}")
