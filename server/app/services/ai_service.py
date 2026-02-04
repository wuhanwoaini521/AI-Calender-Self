from datetime import datetime
from typing import List, Dict, Any, Optional
from ..models.database import db
from ..models.schemas import CalendarEvent


class AIService:
    """AI Assistant Service for calendar operations"""
    
    @staticmethod
    def generate_response(message: str, context: Optional[Dict] = None) -> str:
        """Generate AI response based on user message and context"""
        message_lower = message.lower()
        events = context.get("events", []) if context else []
        current_date = context.get("current_date", datetime.now().strftime("%Y-%m-%d")) if context else datetime.now().strftime("%Y-%m-%d")
        
        # Schedule-related queries
        if any(word in message_lower for word in ["schedule", "plan", "busy", "today"]):
            return AIService._handle_schedule_query(events)
        
        # Conflict detection
        if any(word in message_lower for word in ["conflict", "overlap", "collision"]):
            return AIService._handle_conflict_query(events)
        
        # Free time queries
        if any(word in message_lower for word in ["free time", "available", "when am i free"]):
            return AIService._handle_free_time_query(events, current_date)
        
        # Productivity tips
        if any(word in message_lower for word in ["productivity", "focus", "efficient", "tips"]):
            return AIService._handle_productivity_query()
        
        # Meeting optimization
        if any(word in message_lower for word in ["meeting", "call", "conference"]):
            return AIService._handle_meeting_query()
        
        # Morning routine
        if any(word in message_lower for word in ["morning", "start day", "good morning"]):
            return AIService._handle_morning_query()
        
        # Evening wrap-up
        if any(word in message_lower for word in ["evening", "end day", "tomorrow", "wrap up"]):
            return AIService._handle_evening_query()
        
        # Default response
        return (
            "I'm here to help with your calendar! I can help you:\n"
            "• Check your schedule\n"
            "• Find free time slots\n"
            "• Detect scheduling conflicts\n"
            "• Suggest productivity tips\n"
            "• Optimize your meetings\n\n"
            "What would you like to know?"
        )
    
    @staticmethod
    def _handle_schedule_query(events: List[CalendarEvent]) -> str:
        if not events:
            return "You have a free schedule! This would be a great time to focus on deep work or take a break. 🌟"
        
        event_list = []
        for e in events[:5]:
            start = e.start_time.strftime("%I:%M %p")
            event_list.append(f"• {e.title} at {start}")
        
        more = f" and {len(events) - 5} more" if len(events) > 5 else ""
        return (
            f"You have {len(events)} events scheduled today:{more}\n\n"
            + "\n".join(event_list) +
            "\n\nWould you like me to suggest any optimizations?"
        )
    
    @staticmethod
    def _handle_conflict_query(events: List[CalendarEvent]) -> str:
        conflicts = AIService._find_conflicts(events)
        if conflicts:
            conflict_list = []
            for c in conflicts:
                conflict_list.append(f"• '{c['event1'].title}' overlaps with '{c['event2'].title}'")
            return (
                f"⚠️ I found {len(conflicts)} scheduling conflict(s):\n\n"
                + "\n".join(conflict_list) +
                "\n\nConsider rescheduling one of these events."
            )
        return "✅ Great news! No scheduling conflicts detected for this period."
    
    @staticmethod
    def _handle_free_time_query(events: List[CalendarEvent], date_str: str) -> str:
        from datetime import datetime, time
        
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        day_start = datetime.combine(date, time(9, 0))  # 9 AM
        day_end = datetime.combine(date, time(17, 0))   # 5 PM
        
        # Sort events by start time
        sorted_events = sorted(events, key=lambda x: x.start_time)
        
        free_slots = []
        current_time = day_start
        
        for event in sorted_events:
            if event.start_time > current_time:
                free_slots.append({
                    "start": current_time.strftime("%I:%M %p"),
                    "end": event.start_time.strftime("%I:%M %p")
                })
            current_time = max(current_time, event.end_time)
        
        if current_time < day_end:
            free_slots.append({
                "start": current_time.strftime("%I:%M %p"),
                "end": day_end.strftime("%I:%M %p")
            })
        
        if free_slots:
            slot_text = "\n".join([f"• {s['start']} - {s['end']}" for s in free_slots])
            return f"Your available time slots:\n\n{slot_text}"
        
        return "Your day is quite packed! Consider rescheduling some non-essential tasks. 📅"
    
    @staticmethod
    def _handle_productivity_query() -> str:
        return (
            "Here are some productivity tips:\n\n"
            "1️⃣ **Time Blocking** - Block specific times for deep work\n"
            "2️⃣ **Pomodoro Technique** - Work 25 min, rest 5 min\n"
            "3️⃣ **Eat the Frog** - Do the hardest task first\n"
            "4️⃣ **Batch Similar Tasks** - Group related activities\n"
            "5️⃣ **Take Breaks** - Rest every 90 minutes\n\n"
            "Would you like me to help schedule focus time?"
        )
    
    @staticmethod
    def _handle_meeting_query() -> str:
        return (
            "For efficient meetings:\n\n"
            "✅ Set a clear agenda beforehand\n"
            "✅ Keep meetings under 30 minutes when possible\n"
            "✅ Schedule 5-10 min buffer time between meetings\n"
            "✅ Consider async updates for status meetings\n"
            "✅ End with clear action items\n\n"
            "Need help optimizing your meeting schedule?"
        )
    
    @staticmethod
    def _handle_morning_query() -> str:
        return (
            "Good morning! 🌅 Here's a great way to start:\n\n"
            "1. Review your top 3 priorities for today\n"
            "2. Check for any urgent messages\n"
            "3. Block focus time before meetings begin\n"
            "4. Take a moment to plan your breaks\n\n"
            "Have a productive day!"
        )
    
    @staticmethod
    def _handle_evening_query() -> str:
        return (
            "Before ending your day:\n\n"
            "📋 Review completed tasks\n"
            "🔄 Reschedule unfinished items\n"
            "🎯 Set tomorrow's top priorities\n"
            "🧹 Clear your workspace\n\n"
            "Rest well for tomorrow! 🌙"
        )
    
    @staticmethod
    def _find_conflicts(events: List[CalendarEvent]) -> List[Dict]:
        """Find overlapping events"""
        sorted_events = sorted(events, key=lambda x: x.start_time)
        conflicts = []
        
        for i in range(len(sorted_events) - 1):
            current = sorted_events[i]
            next_event = sorted_events[i + 1]
            
            if current.end_time > next_event.start_time:
                conflicts.append({
                    "event1": current,
                    "event2": next_event
                })
        
        return conflicts
    
    @staticmethod
    def generate_suggestions(user_id: str, date: datetime) -> List[str]:
        """Generate smart suggestions for the user"""
        suggestions = []
        events = db.get_events_by_date_range(
            user_id,
            date.replace(hour=0, minute=0),
            date.replace(hour=23, minute=59)
        )
        
        if not events:
            return ["Your day is clear! Consider scheduling focus time or taking a break."]
        
        sorted_events = sorted(events, key=lambda x: x.start_time)
        
        # Check for back-to-back meetings
        for i in range(len(sorted_events) - 1):
            current = sorted_events[i]
            next_event = sorted_events[i + 1]
            gap_minutes = (next_event.start_time - current.end_time).total_seconds() / 60
            
            if gap_minutes < 15:
                suggestions.append(
                    f"Consider adding buffer time between '{current.title}' and '{next_event.title}'"
                )
        
        # Check for lunch break
        has_lunch = any(
            12 <= e.start_time.hour <= 13 and "lunch" in e.title.lower()
            for e in events
        )
        if not has_lunch and len(events) > 3:
            suggestions.append("Consider blocking time for lunch to maintain energy levels 🍽️")
        
        # Check for focus time
        has_focus = any(
            "focus" in e.title.lower() or "deep work" in e.title.lower()
            for e in events
        )
        if not has_focus and len(events) > 2:
            suggestions.append("Schedule a focus block for uninterrupted work on important tasks 🎯")
        
        # Check for too many meetings
        meetings = [e for e in events if any(word in e.title.lower() for word in ["meeting", "call", "sync"])]
        if len(meetings) > 4:
            suggestions.append("You have many meetings today. Consider if some could be async 📧")
        
        return suggestions if suggestions else ["Your schedule looks well-balanced! 👍"]
    
    @staticmethod
    def generate_schedule(
        tasks: List[Dict[str, Any]], 
        date: datetime,
        existing_events: List[CalendarEvent],
        include_breaks: bool = True
    ) -> List[Dict]:
        """Generate an optimized schedule for tasks"""
        schedule = []
        current_time = date.replace(hour=9, minute=0)  # Start at 9 AM
        work_end = date.replace(hour=17, minute=0)     # End at 5 PM
        
        # Sort existing events
        sorted_events = sorted(existing_events, key=lambda x: x.start_time)
        
        for task in tasks:
            duration = task.get("duration", 60)  # Default 60 minutes
            task_end = current_time + __import__('datetime').timedelta(minutes=duration)
            
            if task_end > work_end:
                break
            
            # Check for conflicts
            has_conflict = any(
                current_time < e.end_time and task_end > e.start_time
                for e in sorted_events
            )
            
            if not has_conflict:
                schedule.append({
                    "task": task["name"],
                    "start_time": current_time.strftime("%Y-%m-%d %H:%M"),
                    "end_time": task_end.strftime("%Y-%m-%d %H:%M"),
                    "duration": duration
                })
                current_time = task_end
                
                # Add break
                if include_breaks:
                    current_time += __import__('datetime').timedelta(minutes=10)
        
        return schedule


ai_service = AIService()
