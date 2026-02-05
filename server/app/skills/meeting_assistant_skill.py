"""Meeting Assistant Skill - 智能会议安排助手"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from .base import Skill, SkillContext, SkillResult, SkillStep
from ..tools.registry import registry as tool_registry


class SmartMeetingScheduleSkill(Skill):
    """
    智能会议安排 Skill
    
    组合多个 Tools 完成复杂任务：
    1. 查找空闲时间
    2. 检测冲突
    3. 创建会议事件
    4. 发送提醒邮件
    """
    
    name = "smart_meeting_schedule"
    description = "智能安排会议：自动查找空闲时间、检测冲突、创建事件并发送提醒"
    
    # 声明这个 Skill 会用到的 Tools
    tools = [
        "get_events",
        "find_free_slots",
        "detect_conflicts",
        "create_event",
        "send_reminder_email",
        "send_notification",
    ]
    
    async def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        """
        执行智能会议安排
        
        kwargs 参数：
        - title: 会议标题
        - date: 日期 (YYYY-MM-DD)
        - duration_minutes: 会议时长（分钟）
        - attendees: 参会人员邮箱列表
        """
        user_id = context.user_id
        title = kwargs.get("title", "新会议")
        date_str = kwargs.get("date", context.current_date.strftime("%Y-%m-%d"))
        duration = kwargs.get("duration_minutes", 60)
        attendees = kwargs.get("attendees", [])
        
        steps = []
        
        # ===== Step 1: 获取当天已有事件 =====
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
                message="无法获取当日日程",
                steps=steps,
            )
        
        existing_events = events_result.data.get("events", [])
        
        # ===== Step 2: 查找空闲时间 =====
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
        
        if not slots_result.success or not slots_result.data.get("free_slots"):
            return SkillResult(
                success=False,
                message=f"{date_str} 没有足够时长的空闲时间",
                data={"existing_events": existing_events},
                steps=steps,
            )
        
        # 选择第一个空闲时间段
        best_slot = slots_result.data["free_slots"][0]
        
        # ===== Step 3: 创建会议事件 =====
        # 构造 ISO 8601 格式时间
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
        start_time_str = f"{date_str}T{best_slot['start']}:00"
        end_time_str = f"{date_str}T{best_slot['end']}:00"
        
        create_result = await tool_registry.execute(
            "create_event",
            user_id=user_id,
            title=title,
            start_time=start_time_str,
            end_time=end_time_str,
            description=f"由智能助手安排的会议，参会人员: {', '.join(attendees)}" if attendees else "",
        )
        steps.append(SkillStep(
            tool_name="create_event",
            params={"user_id": user_id, "title": title, "start_time": start_time_str, "end_time": end_time_str},
            result=create_result.data,
            success=create_result.success,
        ))
        
        if not create_result.success:
            return SkillResult(
                success=False,
                message="创建会议事件失败",
                data={"free_slot": best_slot},
                steps=steps,
            )
        
        event_id = create_result.data.get("id")
        
        # ===== Step 4: 发送提醒邮件（如果有参会人员） =====
        if attendees:
            for email in attendees:
                email_result = await tool_registry.execute(
                    "send_reminder_email",
                    user_id=user_id,
                    event_id=event_id,
                    email=email,
                    subject=f"会议邀请: {title}",
                )
                steps.append(SkillStep(
                    tool_name="send_reminder_email",
                    params={"user_id": user_id, "event_id": event_id, "email": email},
                    result=email_result.data,
                    success=email_result.success,
                ))
        
        # ===== Step 5: 发送应用内通知 =====
        notif_result = await tool_registry.execute(
            "send_notification",
            user_id=user_id,
            message=f"会议 '{title}' 已安排在 {date_str} {best_slot['start']}",
            type="success",
        )
        steps.append(SkillStep(
            tool_name="send_notification",
            params={"user_id": user_id, "message": f"会议已安排"},
            result=notif_result.data,
            success=notif_result.success,
        ))
        
        # 构建成功响应
        message_parts = [
            f"✅ 会议 '{title}' 已成功安排！",
            f"📅 日期: {date_str}",
            f"🕐 时间: {best_slot['start']} - {best_slot['end']}",
        ]
        
        if attendees:
            message_parts.append(f"📧 邀请已发送至: {', '.join(attendees)}")
        
        return SkillResult(
            success=True,
            message="\n".join(message_parts),
            data={
                "event": create_result.data,
                "free_slot": best_slot,
                "attendees": attendees,
            },
            steps=steps,
        )
