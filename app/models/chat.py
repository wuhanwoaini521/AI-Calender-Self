from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ChatMessage(BaseModel):
    """聊天消息模型"""
    
    role: str = Field(..., description="消息角色: user or assistant")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    """聊天请求模型"""
    
    message: str = Field(..., description="用户消息")
    conversation_history: Optional[List[ChatMessage]] = Field(
        default_factory=list,
        description="对话历史"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "帮我添加一个明天下午3点的会议",
                "conversation_history": []
            }
        }


class ChatResponse(BaseModel):
    """聊天响应模型"""
    
    message: str = Field(..., description="助手回复")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        None, 
        description="执行的工具调用"
    )
    events_modified: Optional[List[str]] = Field(
        None, 
        description="修改的事件ID列表"
    )
