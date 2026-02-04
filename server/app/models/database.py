from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import uuid4
from .schemas import (
    User, UserInDB, UserPreferences, CalendarEvent, 
    Reminder, AIInsight, ChatMessage
)
from dateutil.relativedelta import relativedelta


class Database:
    def __init__(self):
        self.users: Dict[str, UserInDB] = {}
        self.events: Dict[str, CalendarEvent] = {}
        self.insights: Dict[str, AIInsight] = {}
        self.chat_messages: Dict[str, ChatMessage] = {}
        self.email_index: Dict[str, str] = {}  # email -> user_id
    
    # ========== User Operations ==========
    
    def create_user(self, email: str, password: str, name: str) -> UserInDB:
        user_id = str(uuid4())
        now = datetime.utcnow()
        
        user = UserInDB(
            id=user_id,
            email=email,
            password=password,
            name=name,
            created_at=now,
            updated_at=now,
            preferences=UserPreferences()
        )
        
        self.users[user_id] = user
        self.email_index[email] = user_id
        return user
    
    def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        return self.users.get(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        user_id = self.email_index.get(email)
        return self.users.get(user_id) if user_id else None
    
    def update_user(self, user_id: str, **updates) -> Optional[UserInDB]:
        user = self.users.get(user_id)
        if not user:
            return None
        
        update_data = {k: v for k, v in updates.items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        updated_user = user.model_copy(update=update_data)
        self.users[user_id] = updated_user
        return updated_user
    
    # ========== Event Operations ==========
    
    def _normalize_datetime(self, dt: datetime) -> datetime:
        """Normalize datetime to naive UTC"""
        if dt.tzinfo:
            return dt.replace(tzinfo=None)
        return dt

    def create_event(
        self, 
        user_id: str, 
        title: str, 
        start_time: datetime, 
        end_time: datetime,
        **kwargs
    ) -> CalendarEvent:
        event_id = str(uuid4())
        now = datetime.utcnow()
        
        # Normalize datetime to avoid timezone issues
        start_time = self._normalize_datetime(start_time)
        end_time = self._normalize_datetime(end_time)
        
        reminders = kwargs.get("reminders", [])
        reminder_objects = [
            Reminder(
                id=str(uuid4()),
                type=r.get("type", "notification"),
                minutes_before=r.get("minutes_before") or r.get("minutesBefore", 15)
            )
            for r in reminders
        ]
        
        event = CalendarEvent(
            id=event_id,
            user_id=user_id,
            title=title,
            start_time=start_time,
            end_time=end_time,
            description=kwargs.get("description", ""),
            all_day=kwargs.get("all_day", False),
            location=kwargs.get("location", ""),
            color=kwargs.get("color", "#3b82f6"),
            reminders=reminder_objects,
            attendees=[],
            created_at=now,
            updated_at=now
        )
        
        self.events[event_id] = event
        return event
    
    def get_event_by_id(self, event_id: str) -> Optional[CalendarEvent]:
        return self.events.get(event_id)
    
    def get_events_by_user(self, user_id: str) -> List[CalendarEvent]:
        return sorted(
            [e for e in self.events.values() if e.user_id == user_id],
            key=lambda x: x.start_time
        )
    
    def get_events_by_date_range(
        self, 
        user_id: str, 
        start: datetime, 
        end: datetime
    ) -> List[CalendarEvent]:
        events = []
        for event in self.events.values():
            if event.user_id != user_id:
                continue
            # Normalize datetimes to handle timezone-aware vs naive comparison
            event_start = event.start_time.replace(tzinfo=None) if event.start_time.tzinfo else event.start_time
            event_end = event.end_time.replace(tzinfo=None) if event.end_time.tzinfo else event.end_time
            query_start = start.replace(tzinfo=None) if start.tzinfo else start
            query_end = end.replace(tzinfo=None) if end.tzinfo else end
            # Check if event overlaps with range
            if (event_start <= query_end and event_end >= query_start):
                events.append(event)
        return sorted(events, key=lambda x: x.start_time)
    
    def update_event(self, event_id: str, **updates) -> Optional[CalendarEvent]:
        event = self.events.get(event_id)
        if not event:
            return None
        
        update_data = {k: v for k, v in updates.items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        updated_event = event.model_copy(update=update_data)
        self.events[event_id] = updated_event
        return updated_event
    
    def delete_event(self, event_id: str) -> bool:
        if event_id in self.events:
            del self.events[event_id]
            return True
        return False
    
    def get_upcoming_events(self, user_id: str, limit: int = 5) -> List[CalendarEvent]:
        now = datetime.utcnow()
        events = [
            e for e in self.events.values() 
            if e.user_id == user_id and e.start_time > now
        ]
        return sorted(events, key=lambda x: x.start_time)[:limit]
    
    # ========== AI Insights Operations ==========
    
    def create_insight(
        self, 
        user_id: str, 
        type: str, 
        message: str,
        related_event_ids: Optional[List[str]] = None
    ) -> AIInsight:
        insight = AIInsight(
            id=str(uuid4()),
            user_id=user_id,
            type=type,
            message=message,
            related_event_ids=related_event_ids or [],
            created_at=datetime.utcnow(),
            read=False
        )
        self.insights[insight.id] = insight
        return insight
    
    def get_insights_by_user(
        self, 
        user_id: str, 
        unread_only: bool = False
    ) -> List[AIInsight]:
        insights = [
            i for i in self.insights.values() 
            if i.user_id == user_id
        ]
        if unread_only:
            insights = [i for i in insights if not i.read]
        return sorted(insights, key=lambda x: x.created_at, reverse=True)
    
    def mark_insight_as_read(self, insight_id: str) -> Optional[AIInsight]:
        insight = self.insights.get(insight_id)
        if insight:
            updated = insight.model_copy(update={"read": True})
            self.insights[insight_id] = updated
            return updated
        return None
    
    # ========== Chat Message Operations ==========
    
    def create_chat_message(
        self, 
        user_id: str, 
        role: str, 
        content: str
    ) -> ChatMessage:
        message = ChatMessage(
            id=str(uuid4()),
            user_id=user_id,
            role=role,
            content=content,
            timestamp=datetime.utcnow()
        )
        self.chat_messages[message.id] = message
        return message
    
    def get_chat_messages_by_user(
        self, 
        user_id: str, 
        limit: int = 50
    ) -> List[ChatMessage]:
        messages = [
            m for m in self.chat_messages.values() 
            if m.user_id == user_id
        ]
        return sorted(messages, key=lambda x: x.timestamp)[-limit:]
    
    # ========== Utility ==========
    
    def clear(self):
        self.users.clear()
        self.events.clear()
        self.insights.clear()
        self.chat_messages.clear()
        self.email_index.clear()


# Global database instance
db = Database()
