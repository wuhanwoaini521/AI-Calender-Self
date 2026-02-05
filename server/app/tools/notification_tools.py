"""Notification-related tools"""

from typing import List, Optional
from .base import Tool, ToolParameter, ToolResult, ToolParameterType


class SendReminderEmailTool(Tool):
    """发送日程提醒邮件"""
    
    name = "send_reminder_email"
    description = "向用户发送日程提醒邮件，用于会议前提醒"
    parameters = [
        ToolParameter(
            name="user_id",
            description="接收邮件的用户ID",
            type=ToolParameterType.STRING,
            required=True,
        ),
        ToolParameter(
            name="event_id",
            description="要提醒的事件ID",
            type=ToolParameterType.STRING,
            required=True,
        ),
        ToolParameter(
            name="email",
            description="接收邮件的邮箱地址",
            type=ToolParameterType.STRING,
            required=True,
        ),
        ToolParameter(
            name="subject",
            description="邮件主题",
            type=ToolParameterType.STRING,
            required=False,
            default="日程提醒",
        ),
    ]
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            user_id = kwargs["user_id"]
            event_id = kwargs["event_id"]
            email = kwargs["email"]
            subject = kwargs.get("subject", "日程提醒")
            
            # 这里实现实际的邮件发送逻辑
            # 例如调用 SMTP 服务或邮件 API
            print(f"[SendReminderEmail] 发送邮件到 {email}: {subject}")
            
            # 模拟发送成功
            return ToolResult.ok(
                data={
                    "email": email,
                    "event_id": event_id,
                    "sent_at": "2026-02-05T10:00:00",
                },
                message=f"提醒邮件已发送至 {email}"
            )
        except Exception as e:
            return ToolResult.error(f"发送邮件失败: {str(e)}")


class SendNotificationTool(Tool):
    """发送应用内通知"""
    
    name = "send_notification"
    description = "向用户发送应用内通知消息"
    parameters = [
        ToolParameter(
            name="user_id",
            description="接收通知的用户ID",
            type=ToolParameterType.STRING,
            required=True,
        ),
        ToolParameter(
            name="message",
            description="通知内容",
            type=ToolParameterType.STRING,
            required=True,
        ),
        ToolParameter(
            name="type",
            description="通知类型",
            type=ToolParameterType.STRING,
            required=False,
            default="info",
            enum=["info", "warning", "success", "error"],
        ),
    ]
    
    async def execute(self, **kwargs) -> ToolResult:
        try:
            user_id = kwargs["user_id"]
            message = kwargs["message"]
            notif_type = kwargs.get("type", "info")
            
            # 这里可以存储到数据库或推送到前端
            print(f"[SendNotification] 用户 {user_id}: {message}")
            
            return ToolResult.ok(
                data={
                    "user_id": user_id,
                    "message": message,
                    "type": notif_type,
                },
                message="通知已发送"
            )
        except Exception as e:
            return ToolResult.error(f"发送通知失败: {str(e)}")
