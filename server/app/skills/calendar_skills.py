"""Calendar-related skills that combine multiple tools"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from .base import Skill, SkillContext, SkillResult, SkillStep
from ..tools.registry import registry as tool_registry


class ScheduleManagementSkill(Skill):
    """Manage schedule - view, optimize, and suggest improvements"""
    
    name = "schedule_management"
    description = "View your schedule, find conflicts, discover free slots, and get optimization suggestions"
    tools = ["get_events", "detect_conflicts", "find_free_slots", "optimize_schedule"]
    
    async def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        """Execute schedule management skill"""
        user_id = context.user_id
        date_str = kwargs.get("date") or context.selected_date.strftime("%Y-%m-%d") if context.selected_date else context.current_date.strftime("%Y-%m-%d")
        
        steps = []
        
        # Step 1: Get events
        events_result = await tool_registry.execute(
            "get_events",
            user_id=user_id,
            date=date_str,
            view="day",
        )
        steps.append(SkillStep(
            tool_name="get_events",
            params={"user_id": user_id, "date": date_str, "view": "day"},
            result=events_result.data,
            success=events_result.success,
        ))
        
        if not events_result.success:
            return SkillResult(
                success=False,
                message="Failed to retrieve schedule",
                steps=steps,
            )
        
        events = events_result.data.get("events", [])
        
        # Step 2: Detect conflicts
        conflicts_result = await tool_registry.execute(
            "detect_conflicts",
            user_id=user_id,
            days=1,
        )
        steps.append(SkillStep(
            tool_name="detect_conflicts",
            params={"user_id": user_id, "days": 1},
            result=conflicts_result.data,
            success=conflicts_result.success,
        ))
        
        conflicts = conflicts_result.data.get("conflicts", []) if conflicts_result.success else []
        
        # Step 3: Optimize schedule
        optimize_result = await tool_registry.execute(
            "optimize_schedule",
            user_id=user_id,
            date=date_str,
        )
        steps.append(SkillStep(
            tool_name="optimize_schedule",
            params={"user_id": user_id, "date": date_str},
            result=optimize_result.data,
            success=optimize_result.success,
        ))
        
        suggestions = optimize_result.data.get("suggestions", []) if optimize_result.success else []
        
        # Build response
        message_parts = []
        
        # Schedule summary
        if events:
            message_parts.append(f"You have {len(events)} events today:")
            for i, event in enumerate(events[:5], 1):
                start = event.get("startTime", "")[11:16] if len(event.get("startTime", "")) > 16 else ""
                message_parts.append(f"  {i}. {event.get('title')} at {start}")
            if len(events) > 5:
                message_parts.append(f"  ... and {len(events) - 5} more")
        else:
            message_parts.append("Your schedule is clear today!")
        
        # Conflicts
        if conflicts:
            message_parts.append(f"\n⚠️ Found {len(conflicts)} conflict(s):")
            for c in conflicts[:3]:
                message_parts.append(f"  • '{c['event1']['title']}' overlaps with '{c['event2']['title']}'")
        
        # Suggestions
        if suggestions:
            message_parts.append(f"\n💡 Suggestions:")
            for s in suggestions[:3]:
                message_parts.append(f"  • {s.get('message', '')}")
        
        return SkillResult(
            success=True,
            message="\n".join(message_parts),
            data={
                "events": events,
                "conflicts": conflicts,
                "suggestions": suggestions,
            },
            steps=steps,
        )


class MeetingPlanningSkill(Skill):
    """Plan and schedule meetings"""
    
    name = "meeting_planning"
    description = "Find optimal meeting times and schedule meetings with participants"
    tools = ["find_free_slots", "create_event", "detect_conflicts"]
    
    async def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        """Execute meeting planning skill"""
        user_id = context.user_id
        date_str = kwargs.get("date", context.current_date.strftime("%Y-%m-%d"))
        duration = kwargs.get("duration_minutes", 60)
        meeting_title = kwargs.get("title", "Meeting")
        
        steps = []
        
        # Step 1: Find free slots
        slots_result = await tool_registry.execute(
            "find_free_slots",
            user_id=user_id,
            date=date_str,
            duration_minutes=duration,
        )
        steps.append(SkillStep(
            tool_name="find_free_slots",
            params={"user_id": user_id, "date": date_str, "duration_minutes": duration},
            result=slots_result.data,
            success=slots_result.success,
        ))
        
        if not slots_result.success:
            return SkillResult(
                success=False,
                message="Failed to find available times",
                steps=steps,
            )
        
        free_slots = slots_result.data.get("free_slots", [])
        
        # Step 2: Check for conflicts on that day
        conflicts_result = await tool_registry.execute(
            "detect_conflicts",
            user_id=user_id,
            days=1,
        )
        steps.append(SkillStep(
            tool_name="detect_conflicts",
            params={"user_id": user_id, "days": 1},
            result=conflicts_result.data,
            success=conflicts_result.success,
        ))
        
        # Build response
        message_parts = []
        
        if free_slots:
            message_parts.append(f"Found {len(free_slots)} available time slots for a {duration}-minute meeting:")
            for i, slot in enumerate(free_slots[:5], 1):
                message_parts.append(f"  {i}. {slot['start']} - {slot['end']} ({slot['duration_minutes']} min available)")
            
            # Suggest best slot (first long enough one)
            best_slot = next((s for s in free_slots if s['duration_minutes'] >= duration), None)
            if best_slot:
                message_parts.append(f"\n✅ Recommended: {best_slot['start']} (gives you buffer time)")
        else:
            message_parts.append("No available slots found for this day. Consider a different date.")
        
        # Check if user wants to schedule
        auto_schedule = kwargs.get("auto_schedule", False)
        if auto_schedule and free_slots:
            best_slot = free_slots[0]
            start_time = datetime.strptime(f"{date_str}T{best_slot['start']}", "%Y-%m-%dT%H:%M")
            end_time = start_time + timedelta(minutes=duration)
            
            create_result = await tool_registry.execute(
                "create_event",
                user_id=user_id,
                title=meeting_title,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                reminders=[{"type": "notification", "minutes_before": 15}],
            )
            steps.append(SkillStep(
                tool_name="create_event",
                params={"user_id": user_id, "title": meeting_title},
                result=create_result.data,
                success=create_result.success,
            ))
            
            if create_result.success:
                message_parts.append(f"\n✅ Meeting '{meeting_title}' scheduled for {best_slot['start']}")
        
        return SkillResult(
            success=True,
            message="\n".join(message_parts),
            data={
                "free_slots": free_slots,
                "recommended_slot": best_slot if free_slots else None,
            },
            steps=steps,
        )


class DailyPlanningSkill(Skill):
    """Daily planning and task scheduling"""
    
    name = "daily_planning"
    description = "Plan your day by scheduling tasks around existing events with optimal breaks"
    tools = ["get_events", "generate_schedule", "suggest_breaks", "create_event"]
    
    async def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        """Execute daily planning skill"""
        user_id = context.user_id
        date_str = kwargs.get("date", context.current_date.strftime("%Y-%m-%d"))
        tasks = kwargs.get("tasks", [])
        
        steps = []
        
        # Step 1: Get existing events
        events_result = await tool_registry.execute(
            "get_events",
            user_id=user_id,
            date=date_str,
            view="day",
        )
        steps.append(SkillStep(
            tool_name="get_events",
            params={"user_id": user_id, "date": date_str},
            result=events_result.data,
            success=events_result.success,
        ))
        
        existing_events = events_result.data.get("events", []) if events_result.success else []
        
        # Step 2: Generate schedule for tasks
        if tasks:
            schedule_result = await tool_registry.execute(
                "generate_schedule",
                user_id=user_id,
                date=date_str,
                tasks=tasks,
            )
            steps.append(SkillStep(
                tool_name="generate_schedule",
                params={"user_id": user_id, "date": date_str, "tasks": tasks},
                result=schedule_result.data,
                success=schedule_result.success,
            ))
            
            scheduled_tasks = schedule_result.data.get("schedule", []) if schedule_result.success else []
        else:
            scheduled_tasks = []
        
        # Step 3: Suggest breaks
        breaks_result = await tool_registry.execute(
            "suggest_breaks",
            user_id=user_id,
            date=date_str,
        )
        steps.append(SkillStep(
            tool_name="suggest_breaks",
            params={"user_id": user_id, "date": date_str},
            result=breaks_result.data,
            success=breaks_result.success,
        ))
        
        suggested_breaks = breaks_result.data.get("suggested_breaks", []) if breaks_result.success else []
        
        # Build response
        message_parts = []
        
        # Existing events
        if existing_events:
            message_parts.append(f"📅 You have {len(existing_events)} existing events today")
        
        # Scheduled tasks
        if scheduled_tasks:
            message_parts.append(f"\n✅ Scheduled {len(scheduled_tasks)} tasks:")
            for task in scheduled_tasks:
                message_parts.append(f"  • {task['task']}: {task['start_time'][11:16]} - {task['end_time'][11:16]}")
        elif tasks:
            message_parts.append("\n⚠️ Could not schedule all tasks. Consider extending work hours or moving some to tomorrow.")
        
        # Break suggestions
        if suggested_breaks:
            message_parts.append(f"\n☕ Suggested breaks:")
            for b in suggested_breaks:
                message_parts.append(f"  • {b['suggested_time']} - {b['duration_minutes']} min ({b['reason']})")
        
        # Summary
        total_items = len(existing_events) + len(scheduled_tasks)
        message_parts.append(f"\n📊 Day summary: {total_items} items scheduled")
        
        return SkillResult(
            success=True,
            message="\n".join(message_parts),
            data={
                "existing_events": existing_events,
                "scheduled_tasks": scheduled_tasks,
                "suggested_breaks": suggested_breaks,
            },
            steps=steps,
        )
