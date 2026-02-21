"""数据库配置和连接管理"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON
from datetime import datetime
from typing import Optional
from uuid import uuid4
import os

# 数据库文件路径
DATABASE_PATH = os.getenv("DATABASE_PATH", "./calendar.db")
DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_PATH}"

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # 设置为 True 可以查看 SQL 日志
    future=True,
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# 声明性基类
Base = declarative_base()


class EventModel(Base):
    """事件数据库模型"""
    __tablename__ = "events"
    
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid4()))
    title = Column(String(255), nullable=False, index=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    
    # 重复事件相关字段
    is_recurring = Column(Boolean, default=False)
    parent_event_id = Column(String(36), nullable=True, index=True)
    recurrence_rule = Column(JSON, nullable=True)  # 存储重复规则 JSON
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


async def init_db():
    """初始化数据库，创建所有表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print(f"✅ 数据库初始化完成: {DATABASE_PATH}")


async def get_db() -> AsyncSession:
    """获取数据库会话（用于依赖注入）"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
