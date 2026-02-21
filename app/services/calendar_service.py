from typing import List, Optional, Dict
from datetime import datetime, timedelta, date
from uuid import uuid4
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calendar import CalendarEvent, CalendarEventCreate, CalendarEventUpdate, RecurrenceRule
from app.database import EventModel, AsyncSessionLocal


class CalendarService:
    
    """日历服务 - 管理日历事件的业务逻辑（使用 SQLite 数据库）"""
    
    def __init__(self):
        """初始化日历服务"""
        pass
    
    async def _get_session(self) -> AsyncSession:
        """获取数据库会话"""
        return AsyncSessionLocal()
    
    def _to_model(self, event_data: CalendarEventCreate) -> EventModel:
        """将 Pydantic 模型转换为数据库模型"""
        recurrence_rule_dict = None
        if event_data.recurrence_rule:
            # 将 date 对象转换为字符串以便 JSON 序列化
            rule_dict = event_data.recurrence_rule.model_dump()
            if rule_dict.get('end_date') and isinstance(rule_dict['end_date'], date):
                rule_dict['end_date'] = rule_dict['end_date'].isoformat()
            recurrence_rule_dict = rule_dict
        
        return EventModel(
            id=str(uuid4()),
            title=event_data.title,
            start_time=event_data.start_time,
            end_time=event_data.end_time,
            description=event_data.description,
            location=event_data.location,
            recurrence_rule=recurrence_rule_dict,
        )
    
    def _to_pydantic(self, db_event: EventModel) -> CalendarEvent:
        """将数据库模型转换为 Pydantic 模型"""
        return CalendarEvent(
            id=db_event.id,
            title=db_event.title,
            start_time=db_event.start_time,
            end_time=db_event.end_time,
            description=db_event.description,
            location=db_event.location,
            is_recurring=db_event.is_recurring,
            parent_event_id=db_event.parent_event_id,
            recurrence_rule=RecurrenceRule(**db_event.recurrence_rule) if db_event.recurrence_rule else None,
            created_at=db_event.created_at,
            updated_at=db_event.updated_at,
        )
    
    async def create_event(self, event_data: CalendarEventCreate) -> CalendarEvent:
        """创建新事件，支持重复事件

        :param event_data: 事件创建数据
        :return: 创建的事件（如果是重复事件，返回父事件）
        """
        async with await self._get_session() as session:
            # 创建父事件
            db_event = self._to_model(event_data)
            db_event.is_recurring = event_data.recurrence_rule is not None
            
            session.add(db_event)
            await session.commit()
            await session.refresh(db_event)
            
            # 如果有重复规则，生成重复事件实例
            if event_data.recurrence_rule:
                await self._generate_recurring_instances(db_event, event_data.recurrence_rule, session)
                await session.commit()
            
            return self._to_pydantic(db_event)
    
    async def _generate_recurring_instances(
        self, 
        parent_event: EventModel, 
        rule: RecurrenceRule,
        session: AsyncSession
    ) -> List[EventModel]:
        """根据重复规则生成事件实例

        :param parent_event: 父事件
        :param rule: 重复规则
        :param session: 数据库会话
        :return: 生成的实例列表
        """
        instances = []
        
        # 计算事件持续时间
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
                
                instance = EventModel(
                    id=str(uuid4()),
                    title=parent_event.title,
                    start_time=instance_start,
                    end_time=instance_end,
                    description=parent_event.description,
                    location=parent_event.location,
                    is_recurring=True,
                    parent_event_id=parent_event.id,
                )
                session.add(instance)
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
                        
                        instance = EventModel(
                            id=str(uuid4()),
                            title=parent_event.title,
                            start_time=instance_start,
                            end_time=instance_end,
                            description=parent_event.description,
                            location=parent_event.location,
                            is_recurring=True,
                            parent_event_id=parent_event.id,
                        )
                        session.add(instance)
                        instances.append(instance)
                    
                    current_date += timedelta(days=1)
            else:
                # 如果没有指定具体星期几，每周同一天重复
                while current_date <= end_date:
                    instance_start = datetime.combine(current_date, parent_event.start_time.time())
                    instance_end = instance_start + duration
                    
                    instance = EventModel(
                        id=str(uuid4()),
                        title=parent_event.title,
                        start_time=instance_start,
                        end_time=instance_end,
                        description=parent_event.description,
                        location=parent_event.location,
                        is_recurring=True,
                        parent_event_id=parent_event.id,
                    )
                    session.add(instance)
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
                    
                    instance = EventModel(
                        id=str(uuid4()),
                        title=parent_event.title,
                        start_time=instance_start,
                        end_time=instance_end,
                        description=parent_event.description,
                        location=parent_event.location,
                        is_recurring=True,
                        parent_event_id=parent_event.id,
                    )
                    session.add(instance)
                    instances.append(instance)
                
                # 进入下一个月
                if current_month == 12:
                    current_year += 1
                    current_month = 1
                else:
                    current_month += 1
        
        return instances

    async def get_event(self, event_id: str) -> Optional[CalendarEvent]:
        """获取单个事件

        :param event_id: 事件ID
        :return: 事件对象，如果不存在则返回None
        """
        async with await self._get_session() as session:
            result = await session.execute(
                select(EventModel).where(EventModel.id == event_id)
            )
            db_event = result.scalar_one_or_none()
            return self._to_pydantic(db_event) if db_event else None
    
    async def list_events(
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
        async with await self._get_session() as session:
            query = select(EventModel)
            
            # 按开始时间筛选
            if start_date:
                query = query.where(EventModel.start_time >= start_date)
            
            # 按结束时间筛选
            if end_date:
                query = query.where(EventModel.end_time <= end_date)
            
            # 关键词搜索
            if keyword:
                keyword_lower = f"%{keyword.lower()}%"
                query = query.where(
                    or_(
                        func.lower(EventModel.title).like(keyword_lower),
                        func.lower(EventModel.description).like(keyword_lower)
                    )
                )
            
            # 按开始时间排序
            query = query.order_by(EventModel.start_time)
            
            result = await session.execute(query)
            db_events = result.scalars().all()
            
            return [self._to_pydantic(e) for e in db_events]
    
    async def update_event(
        self,
        event_id: str,
        update_data: CalendarEventUpdate
    ) -> Optional[CalendarEvent]:
        """更新事件

        :param event_id: 事件ID
        :param update_data: 更新数据
        :return: 更新后的事件，如果不存在则返回None
        """
        async with await self._get_session() as session:
            result = await session.execute(
                select(EventModel).where(EventModel.id == event_id)
            )
            db_event = result.scalar_one_or_none()
            
            if not db_event:
                return None
            
            # 更新字段
            if update_data.title is not None:
                db_event.title = update_data.title
            if update_data.start_time is not None:
                db_event.start_time = update_data.start_time
            if update_data.end_time is not None:
                db_event.end_time = update_data.end_time
            if update_data.description is not None:
                db_event.description = update_data.description
            if update_data.location is not None:
                db_event.location = update_data.location
            
            db_event.updated_at = datetime.now()
            
            await session.commit()
            await session.refresh(db_event)
            
            return self._to_pydantic(db_event)

    async def delete_event(self, event_id: str, delete_all_instances: bool = True) -> bool:
        """删除事件，支持删除重复事件的所有实例

        :param event_id: 事件ID
        :param delete_all_instances: 如果是重复事件，是否删除所有实例
        :return: 是否删除成功
        """
        async with await self._get_session() as session:
            result = await session.execute(
                select(EventModel).where(EventModel.id == event_id)
            )
            event = result.scalar_one_or_none()
            
            if not event:
                return False
            
            # 如果是父事件且有重复规则，删除所有实例
            if delete_all_instances and event.recurrence_rule:
                await session.execute(
                    EventModel.__table__.delete().where(
                        EventModel.parent_event_id == event_id
                    )
                )
            
            # 如果是重复事件的实例，且要删除所有相关实例
            if delete_all_instances and event.parent_event_id:
                parent_id = event.parent_event_id
                # 删除父事件
                await session.execute(
                    EventModel.__table__.delete().where(EventModel.id == parent_id)
                )
                # 删除所有实例
                await session.execute(
                    EventModel.__table__.delete().where(
                        EventModel.parent_event_id == parent_id
                    )
                )
                await session.commit()
                return True
            
            await session.delete(event)
            await session.commit()
            return True

    async def get_all_events(self) -> List[CalendarEvent]:
        """获取所有事件

        :return: 返回所有事件列表
        """
        return await self.list_events()
             
    async def get_events_by_parent(self, parent_event_id: str) -> List[CalendarEvent]:
        """获取某个父事件的所有重复实例

        :param parent_event_id: 父事件ID
        :return: 重复实例列表
        """
        async with await self._get_session() as session:
            result = await session.execute(
                select(EventModel)
                .where(EventModel.parent_event_id == parent_event_id)
                .order_by(EventModel.start_time)
            )
            db_events = result.scalars().all()
            return [self._to_pydantic(e) for e in db_events]
