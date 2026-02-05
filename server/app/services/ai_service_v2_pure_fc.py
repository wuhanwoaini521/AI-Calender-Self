"""
AI Service v2 - Pure Function Calling Version
完全依赖 LLM 的 Function Calling 能力
"""

import json
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
from openai import AsyncOpenAI

from ..tools.registry import registry as tool_registry
from ..mcp.server import MCPServer
from ..core.config import get_settings


class AIServiceV2PureFC:
    """
    AI Service - 纯 Function Calling 版本
    
    特点：
    1. 不预检测意图
    2. 完全依赖 LLM 决定调用哪个工具
    3. 支持多轮工具调用（工具结果返回给 LLM 继续决策）
    """
    
    def __init__(self):
        settings = get_settings()
        
        self.client = AsyncOpenAI(
            base_url=settings.OPENAI_BASE_URL,
            api_key=settings.OPENAI_API_KEY,
        )
        self.model = settings.OPENAI_MODEL
        self.mcp_server = MCPServer()
        
        # 更简洁的系统提示 - 工具描述已经在 tools schema 中
        self.system_prompt = """你是AI日历助手。根据用户请求，选择合适的工具执行。

重要规则：
1. 当用户想创建/安排/添加事件时，调用 create_event 工具
2. 当用户想查询日程时，调用 get_events 工具
3. 当用户想查找空闲时间时，调用 find_free_slots 工具
4. 时间格式使用 ISO 8601 (YYYY-MM-DDTHH:MM:SS)

当前日期会在上下文提供，注意处理"明天"、"今天"等相对时间。"""
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        user_id: str,
        context: Optional[Dict[str, Any]] = None,
        max_tool_rounds: int = 3,  # 最多工具调用轮数，防止无限循环
    ) -> AsyncGenerator[str, None]:
        """
        Chat with pure function calling
        
        流程：
        1. 发送消息给 LLM（带 tools）
        2. 如果 LLM 调用工具，执行并返回结果
        3. 重复直到 LLM 不再调用工具或达到最大轮数
        4. 返回最终回复
        """
        # 构建消息
        chat_messages = [
            {"role": "system", "content": self.system_prompt},
        ]
        
        # 添加上下文
        if context:
            context_str = self._format_context(context)
            chat_messages.append({
                "role": "system",
                "content": f"Context:\n{context_str}"
            })
        
        # 添加用户消息
        chat_messages.extend(messages)
        
        # 获取工具
        tools = self.mcp_server.get_openai_tools()
        
        # 多轮工具调用
        for round_num in range(max_tool_rounds):
            print(f"[DEBUG] Round {round_num + 1}: Sending {len(chat_messages)} messages to LLM")
            
            # 调用 LLM（非流式，因为要判断是否有工具调用）
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=chat_messages,
                tools=tools,
                tool_choice="auto",
            )
            
            message = response.choices[0].message
            
            # 情况 1: LLM 想调用工具
            if message.tool_calls:
                print(f"[DEBUG] LLM wants to call {len(message.tool_calls)} tool(s)")
                
                # 添加 assistant 的 tool_calls 到消息历史
                chat_messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            }
                        }
                        for tc in message.tool_calls
                    ]
                })
                
                # 执行每个工具调用
                for tc in message.tool_calls:
                    tool_name = tc.function.name
                    try:
                        arguments = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        arguments = {}
                    
                    # 添加 user_id
                    arguments["user_id"] = user_id
                    
                    print(f"[DEBUG] Executing tool: {tool_name} with args: {arguments}")
                    
                    # 执行工具
                    result = await tool_registry.execute(tool_name, **arguments)
                    
                    # 输出工具调用结果（给前端）
                    yield json.dumps({
                        "type": "tool_call",
                        "tool": tool_name,
                        "success": result.success,
                        "result": result.data if result.success else {"error": result.error},
                        "message": result.message,
                    })
                    
                    # 添加工具结果到消息历史
                    chat_messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps({
                            "success": result.success,
                            "message": result.message,
                            "data": result.data if result.success else {"error": result.error},
                        }, ensure_ascii=False),
                    })
                
                # 继续下一轮
                continue
            
            # 情况 2: LLM 直接回复，没有工具调用
            else:
                print(f"[DEBUG] LLM responded without tool calls")
                content = message.content or "好的"
                yield json.dumps({"type": "text", "content": content})
                break
        
        else:
            # 达到最大轮数，强制结束
            yield json.dumps({"type": "text", "content": "（已达到最大工具调用次数，对话结束）"})
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context for the AI"""
        parts = []
        
        if "current_date" in context:
            parts.append(f"Today: {context['current_date']}")
        
        if "selected_date" in context:
            parts.append(f"Selected: {context['selected_date']}")
        
        return "\n".join(parts)


# 使用方式
ai_service_v2_pure_fc = AIServiceV2PureFC()
