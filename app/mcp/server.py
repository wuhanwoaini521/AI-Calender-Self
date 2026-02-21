from typing import Dict, Any, Optional, List
from datetime import datetime, date
from app.models.calendar import CalendarEvent, CalendarEventCreate, CalendarEventUpdate, RecurrenceRule


class MCPServer:
    """MCP 服务器 - 实际执行工具调用的服务"""
    
    def __init__(self, calendar_service):
        """
        初始化 MCP 服务器
        Args:
            calendar_service: 日历服务实例
        """
        self.calendar_service = calendar_service
    
    
    async def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行工具调用
        
        Args:
            tool_name: 工具名称
            tool_input: 工具输入参数
        Returns:
            工具执行结果
        """
        try:
            if tool_name == "create_event":
                return await self._create_event(tool_input)
            elif tool_name == "list_events":
                return await self._list_events(tool_input)
            elif tool_name == "update_event":
                return await self._update_event(tool_input)
            elif tool_name == "delete_event":
                return await self._delete_event(tool_input)
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _create_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """创建事件，支持重复事件"""
        try:
            # 处理重复规则
            recurrence_rule = None
            if "recurrence_rule" in params and params["recurrence_rule"]:
                rule_data = params["recurrence_rule"]
                end_date = None
                if "end_date" in rule_data and rule_data["end_date"]:
                    # 支持日期格式或完整的ISO格式
                    end_date_str = rule_data["end_date"]
                    try:
                        end_date = date.fromisoformat(end_date_str)
                    except ValueError:
                        # 尝试解析完整日期时间
                        end_date = datetime.fromisoformat(end_date_str).date()
                
                recurrence_rule = RecurrenceRule(
                    type=rule_data["type"],
                    days=rule_data.get("days"),
                    end_date=end_date
                )
            
            event_data = CalendarEventCreate(
                title=params["title"],
                start_time=datetime.fromisoformat(params["start_time"]),
                end_time=datetime.fromisoformat(params["end_time"]),
                description=params.get("description"),
                location=params.get("location"),
                recurrence_rule=recurrence_rule
            )
            
            event = await self.calendar_service.create_event(event_data)
            
            # 构建返回消息
            if event.recurrence_rule:
                instances = await self.calendar_service.get_events_by_parent(event.id)
                message = f"成功创建重复事件: {event.title}，共生成 {len(instances) + 1} 个实例"
            else:
                message = f"成功创建事件: {event.title}"
            
            return {
                "success": True,
                "event": event.model_dump(mode="json"),
                "message": message
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"创建事件失败: {str(e)}"
            }
    
    async def _list_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """列出事件"""
        try:
            start_date = None
            end_date = None
            keyword = params.get("keyword")
            
            if "start_date" in params and params["start_date"]:
                # 支持纯日期格式（自动转为当天开始时间）
                start_str = params["start_date"]
                if len(start_str) == 10:  # YYYY-MM-DD
                    start_str += "T00:00:00"
                start_date = datetime.fromisoformat(start_str)
            
            if "end_date" in params and params["end_date"]:
                # 支持纯日期格式（自动转为当天结束时间）
                end_str = params["end_date"]
                if len(end_str) == 10:  # YYYY-MM-DD
                    end_str += "T23:59:59"
                end_date = datetime.fromisoformat(end_str)
            
            events = await self.calendar_service.list_events(
                start_date=start_date,
                end_date=end_date,
                keyword=keyword
            )
            
            return {
                "success": True,
                "events": [e.model_dump(mode="json") for e in events],
                "count": len(events),
                "message": f"找到 {len(events)} 个事件"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"查询事件失败：{str(e)}"
            }
    
    async def _update_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """更新事件"""
        try:
            event_id = params["event_id"]
            
            update_data = CalendarEventUpdate()
            if "title" in params:
                update_data.title = params["title"]
            if "start_time" in params:
                update_data.start_time = datetime.fromisoformat(params["start_time"])
            if "end_time" in params:
                update_data.end_time = datetime.fromisoformat(params["end_time"])
            if "description" in params:
                update_data.description = params["description"]
            if "location" in params:
                update_data.location = params["location"]
            
            event = await self.calendar_service.update_event(event_id, update_data)
            
            if event:
                return {
                    "success": True,
                    "event": event.model_dump(mode="json"),
                    "message": f"成功更新事件：{event.title}"
                }
            else:
                return {
                    "success": False,
                    "error": f"未找到ID为 {event_id} 的事件"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"更新事件失败：{str(e)}"
            }
    
    async def _delete_event(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """删除事件，支持删除重复事件的所有实例"""
        try:
            event_id = params["event_id"]
            delete_all = params.get("delete_all_instances", True)
            
            # 获取事件信息用于确认
            event = await self.calendar_service.get_event(event_id)
            if not event:
                return {
                    "success": False,
                    "error": f"未找到ID为 {event_id} 的事件"
                }
            
            # 保存事件信息用于返回
            event_data = event.model_dump(mode="json")
            
            success = await self.calendar_service.delete_event(event_id, delete_all_instances=delete_all)
            
            if success:
                if event.parent_event_id:
                    if delete_all:
                        message = f"成功删除重复事件及其所有实例: {event.title}"
                    else:
                        message = f"成功删除重复事件的单个实例: {event.title}"
                elif event.recurrence_rule:
                    message = f"成功删除重复事件及其所有实例: {event.title}"
                else:
                    message = f"成功删除事件: {event.title}"
                
                return {
                    "success": True,
                    "message": message,
                    "event": event_data
                }
            else:
                return {
                    "success": False,
                    "error": f"删除事件失败"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"删除事件失败：{str(e)}"
            }