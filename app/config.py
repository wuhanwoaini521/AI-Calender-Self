from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # API 配置
    api_key: Optional[str] = None
    api_base_url: str = "https://api.moonshot.cn/v1"
    
    # Application
    app_name: str = "Calendar MCP Backend"
    debug: bool = True
    
    # Model
    model: str = "moonshot-v1-8k"  # 可选: moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = 'ignore'


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()