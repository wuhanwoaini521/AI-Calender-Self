from typing import List, Optional, Dict
from datetime import datetime, timedelta, date
from app.models.calendar import CalendarEvent, CalendarEventCreate, CalendarEventUpdate, RecurrenceRule


class CalendarService:
    
    """日历服务 - 管理日历事件的业务逻辑"""
    
    def __init__(self):
        """初始化日历服务（使用内存存储）"""
        self.events: Dict[str, CalendarEvent] = {}
    
    def create_event(self, event_data: CalendarEventCreate) -> CalendarEvent:
        """创建新事件，支持重复事件

        :param event_data: 事件创建数据
        :return: 创建的事件（如果是重复事件，返回父事件）
        """
        # 创建父事件
        event = CalendarEvent(
            title=event_data.title,
            start_time=event_data.start_time,
            end_time=event_data.end_time,
            description=event_data.description,
            location=event_data.location,
            recurrence_rule=event_data.recurrence_rule
        )
        
        self.events[event.id] = event
        
        # 如果有重复规则，生成重复事件实例
        if event_data.recurrence_rule:
            event.is_recurring = True
            self._generate_recurring_instances(event, event_data.recurrence_rule)
        
        return event
    
    def _generate_recurring_instances(self, parent_event: CalendarEvent, rule: RecurrenceRule) -> List[CalendarEvent]:
        """根据重复规则生成事件实例

        :param parent_event: 父事件
        :param rule: 重复规则
        :return: 生成的实例列表
        """
        instances = []
        
        # 计算事件持续时间（用于生成实例的结束时间）
        duration = parent_event.end_time - parent_event.start_time
        
        # 确定结束日期（默认3个月后）
        end_date = rule.end_date or (parent_event.start_time.date() + timedelta(days=90))
        start_date = parent_event.start_time.date()
        
        # 星期映射
        day_map = {
            "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6
        }
        
        current_date = start_date + timedelta(days=1)  # 从第二天开始生成
        
        if rule.type == "daily":
            # 每天重复
            while current_date <= end_date:
                instance_start = datetime.combine(current_date, parent_event.start_time.time())
                instance_end = instance_start + duration
                
                instance = CalendarEvent(
                    title=parent_event.title,
                    start_time=instance_start,
                    end_time=instance_end,
                    description=parent_event.description,
                    location=parent_event.location,
                    is_recurring=True,
                    parent_event_id=parent_event.id
                )
                self.events[instance.id] = instance
                instances.append(instance)
                
                current_date += timedelta(days=1)
                
        elif rule.type == "weekly":
            # 每周重复特定几天
            if rule.days:
                target_weekdays = [day_map[d] for d in rule.days]
                
                while current_date <= end_date:
                    if current_date.weekday() in target_weekdays:
                        instance_start = datetime.combine(current_date, parent_event.start_time.time())
                        instance_end = instance_start + duration
                        
                        instance = CalendarEvent(
                            title=parent_event.title,
                            start_time=instance_start,
                            end_time=instance_end,
                            description=parent_event.description,
                            location=parent_event.location,
                            is_recurring=True,
                            parent_event_id=parent_event.id
                        )
                        self.events[instance.id] = instance
                        instances.append(instance)
                    
                    current_date += timedelta(days=1)
            else:
                # 如果没有指定具体星期几，每周同一天重复
                while current_date <= end_date:
                    instance_start = datetime.combine(current_date, parent_event.start_time.time())
                    instance_end = instance_start + duration
                    
                    instance = CalendarEvent(
                        title=parent_event.title,
                        start_time=instance_start,
                        end_time=instance_end,
                        description=parent_event.description,
                        location=parent_event.location,
                        is_recurring=True,
                        parent_event_id=parent_event.id
                    )
                    self.events[instance.id] = instance
                    instances.append(instance)
                    
                    current_date += timedelta(days=7)
                    
        elif rule.type == "monthly":
            # 每月重复
            current_year = current_date.year
            current_month = current_date.month
            day_of_month = parent_event.start_time.day
            
            while True:
                try:
                    instance_date = date(current_year, current_month, day_of_month)
                except ValueError:
                    # 处理月份天数不足的情况（如2月30日）
                    if current_month == 12:
                        current_year += 1
                        current_month = 1
                    else:
                        current_month += 1
                    continue
                
                if instance_date > end_date:
                    break
                    
                if instance_date >= current_date:
                    instance_start = datetime.combine(instance_date, parent_event.start_time.time())
                    instance_end = instance_start + duration
                    
                    instance = CalendarEvent(
                        title=parent_event.title,
                        start_time=instance_start,
                        end_time=instance_end,
                        description=parent_event.description,
                        location=parent_event.location,
                        is_recurring=True,
                        parent_event_id=parent_event.id
                    )
                    self.events[instance.id] = instance
                    instances.append(instance)
                
                # 进入下一个月
                if current_month == 12:
                    current_year += 1
                    current_month = 1
                else:
                    current_month += 1
        
        return instances

    def get_event(self, event_id: str) -> Optional[CalendarEvent]:
        """获取单个事件

        :param event_id: 事件ID
        :return: 事件对象，如果不存在则返回None
        """
        return self.events.get(event_id)
    
    def list_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        keyword: Optional[str] = None
    ) -> List[CalendarEvent]:
        """列出事件（支持筛选）

        :param start_date: 开始日期筛选, defaults to None
        :param end_date: 结束日期筛选, defaults to None
        :param keyword: 关键词搜索, defaults to None
        :return: 事件列表
        """
        
        events = list(self.events.values())
        
        # 按开始时间筛选
        if start_date:
            events = [e for e in events if e.start_time >= start_date]
        
        # 按结束时间筛选
        if end_date:
            events = [e for e in events if e.end_time <= end_date]
        
        # 关键词搜索
        if keyword:
            keyword_lower = keyword.lower()
            events = [
                e for e in events
                if (keyword_lower in e.title.lower()) or
                (e.description and keyword_lower in e.description.lower())
            ]
        
        # 按开始时间排序
        events.sort(key=lambda x: x.start_time)
        
        return events
    
    def update_event(
        self,
        event_id: str,
        update_data: CalendarEventUpdate
    ) -> Optional[CalendarEvent]:
        """更新事件

        :param event_id: 事件ID
        :param update_data: 更新数据
        :return: 更新后的事件，如果不存在则返回None
        """
        event = self.events.get(event_id)
        if not event:
            return None
        
        if update_data.title is not None:
            event.title = update_data.title
        if update_data.start_time is not None:
            event.start_time = update_data.start_time
        if update_data.end_time is not None:
            event.end_time = update_data.end_time
        if update_data.description is not None:
            event.description = update_data.description
        if update_data.location is not None:
            event.location = update_data.location
        
        event.updated_at = datetime.now()
        
        return event

    def delete_event(self, event_id: str, delete_all_instances: bool = True) -> bool:
        """删除事件，支持删除重复事件的所有实例

        :param event_id: 事件ID
        :param delete_all_instances: 如果是重复事件，是否删除所有实例
        :return: 是否删除成功
        """
        event = self.events.get(event_id)
        if not event:
            return False
        
        # 如果是父事件且有重复规则，删除所有实例
        if delete_all_instances and event.recurrence_rule:
            instance_ids = [
                eid for eid, e in self.events.items()
                if e.parent_event_id == event_id
            ]
            for instance_id in instance_ids:
                del self.events[instance_id]
        
        # 如果是重复事件的实例，且要删除所有相关实例
        if delete_all_instances and event.parent_event_id:
            parent_id = event.parent_event_id
            instance_ids = [
                eid for eid, e in self.events.items()
                if e.parent_event_id == parent_id
            ]
            # 删除父事件
            if parent_id in self.events:
                del self.events[parent_id]
            # 删除所有实例
            for instance_id in instance_ids:
                if instance_id in self.events:
                    del self.events[instance_id]
            return True
        
        del self.events[event_id]
        return True

    def get_all_events(self) -> List[CalendarEvent]:
        """获取所有事件

        :return: 返回所有事件列表
        """
        events = list(self.events.values())
        events.sort(key=lambda x: x.start_time)
        return events
             
    def get_events_by_parent(self, parent_event_id: str) -> List[CalendarEvent]:
        """获取某个父事件的所有重复实例

        :param parent_event_id: 父事件ID
        :return: 重复实例列表
        """
        return [
            e for e in self.events.values()
            if e.parent_event_id == parent_event_id
        ]
