from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List, Literal
from uuid import uuid4


class RecurrenceRule(BaseModel):
    """重复规则模型"""
    
    type: Literal["daily", "weekly", "monthly"] = Field(..., description="重复类型: daily-每天, weekly-每周, monthly-每月")
    days: Optional[List[Literal["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]]] = Field(
        None, description="每周重复的星期几（仅weekly类型使用）"
    )
    end_date: Optional[date] = Field(None, description="重复结束日期，默认为3个月后")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "weekly",
                "days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
                "end_date": "2024-06-30"
            }
        }


class CalendarEvent(BaseModel):
    """日历事件模型"""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(..., description="事件标题")
    start_time: datetime = Field(..., description="事件开始时间")
    end_time: datetime = Field(..., description="事件结束时间")
    description: Optional[str] = Field(None, description="事件描述")
    location: Optional[str] = Field(None, description="事件地点")
    # 重复事件相关字段
    is_recurring: bool = Field(default=False, description="是否是重复事件的一部分")
    parent_event_id: Optional[str] = Field(None, description="父事件ID（如果是重复事件的实例）")
    recurrence_rule: Optional[RecurrenceRule] = Field(None, description="重复规则（仅父事件有）")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "团队会议",
                "start_time": "2023-10-15T09:00:00",
                "end_time": "2023-10-15T10:00:00",
                "description": "讨论项目进展和下一步计划",
                "location": "会议室A",
                "is_recurring": False
            }
        }
    
    
class CalendarEventCreate(BaseModel):
    """创建事件请求模型"""
    
    title: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    location: Optional[str] = None
    # 重复事件支持
    recurrence_rule: Optional[RecurrenceRule] = None


class CalendarEventUpdate(BaseModel):
    """更新事件请求模型"""
    
    title: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    description: Optional[str] = None
    location: Optional[str] = None


class RecurringEventCreate(BaseModel):
    """创建重复事件的专用模型"""
    
    title: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    location: Optional[str] = None
    recurrence_type: Literal["daily", "weekly", "monthly"] = Field(..., description="重复类型")
    recurrence_days: Optional[List[str]] = Field(None, description="每周重复的星期几")
    recurrence_end_date: Optional[date] = Field(None, description="重复结束日期")
