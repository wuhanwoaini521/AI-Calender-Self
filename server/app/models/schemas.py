from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List, Literal
from uuid import uuid4


# ============== User Schemas ==============

class UserPreferences(BaseModel):
    theme: Literal["light", "dark"] = "light"
    timezone: str = "UTC"
    language: str = "en"
    notification_enabled: bool = True
    ai_assistant_enabled: bool = True


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    preferences: UserPreferences

    class Config:
        from_attributes = True


class UserInDB(User):
    password: str


# ============== Event Schemas ==============

class Reminder(BaseModel):
    id: str
    type: Literal["notification", "email", "sms"]
    minutes_before: int = Field(alias="minutesBefore")
    
    class Config:
        populate_by_name = True


class Attendee(BaseModel):
    id: str
    email: EmailStr
    name: Optional[str] = None
    status: Literal["pending", "accepted", "declined", "tentative"] = "pending"


class CalendarEventBase(BaseModel):
    title: str
    description: Optional[str] = ""
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")
    all_day: bool = Field(default=False, alias="allDay")
    location: Optional[str] = ""
    color: str = "#3b82f6"

    class Config:
        populate_by_name = True


class CalendarEventCreate(CalendarEventBase):
    reminders: Optional[List[dict]] = []


class CalendarEvent(CalendarEventBase):
    id: str
    user_id: str = Field(alias="userId")
    reminders: List[Reminder] = []
    attendees: List[Attendee] = []
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True


# ============== AI Schemas ==============

class AIInsight(BaseModel):
    id: str
    user_id: str
    type: Literal["suggestion", "conflict", "optimization", "reminder"]
    message: str
    related_event_ids: Optional[List[str]] = None
    created_at: datetime
    read: bool = False


class ChatMessage(BaseModel):
    id: str
    user_id: str
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime


class AIChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None


class AIChatResponse(BaseModel):
    message: str
    timestamp: datetime


# ============== Auth Schemas ==============

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    user: User
    token: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


# ============== API Response ==============

class APIResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None
