from typing import List, Dict, Any
from openai import OpenAI
from app.config import get_settings
from app.models.chat import ChatMessage, ChatRequest, ChatResponse
from app.mcp.tools import MCPTools
from app.mcp.server import MCPServer
from app.skills.loader import skill_loader


class ChatService:
    """对话服务 - 处理与 AI API 的交互"""
    
    def __init__(self, mcp_server: MCPServer, api_key: str):
        """
        初始化对话服务
        
        Args:
            mcp_server: MCP 服务器实例
            api_key: API Key（必需）
        """
        if not api_key:
            raise ValueError("API Key is required")
        
        settings = get_settings()
        
        self.api_key = api_key
        # 使用 OpenAI 客户端连接 Kimi API
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=settings.api_base_url
        )
        self.model = settings.model
        self.mcp_server = mcp_server
        self.tools = self._convert_tools_to_openai_format(MCPTools.get_tool_definitions())
        
        # 加载 Skills
        self.system_prompt = self._build_system_prompt()
    
    def _convert_tools_to_openai_format(self, anthropic_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        将 Anthropic 工具格式转换为 OpenAI 格式
        
        Args:
            anthropic_tools: Anthropic 格式的工具定义
            
        Returns:
            OpenAI 格式的工具定义
        """
        openai_tools = []
        for tool in anthropic_tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"]
                }
            })
        return openai_tools
    
    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        from datetime import datetime, timedelta
        
        now = datetime.now()
        today = now.date()
        tomorrow = today + timedelta(days=1)
        day_after_tomorrow = today + timedelta(days=2)
        
        # 计算本周和下周的日期
        weekday = today.weekday()  # 周一=0, 周日=6
        monday_this_week = today - timedelta(days=weekday)
        friday_this_week = monday_this_week + timedelta(days=4)
        monday_next_week = monday_this_week + timedelta(days=7)
        friday_next_week = monday_next_week + timedelta(days=4)
        
        base_prompt = f"""你是一个智能日历助手，帮助用户管理他们的日程安排。

你可以通过以下工具来操作日历：
- create_event: 创建新事件（支持单次事件或重复事件）
- list_events: 查询事件列表
- update_event: 更新已有事件
- delete_event: 删除事件

当前日期时间参考：
- 今天: {today.isoformat()} ({['周一','周二','周三','周四','周五','周六','周日'][today.weekday()]})
- 明天: {tomorrow.isoformat()} ({['周一','周二','周三','周四','周五','周六','周日'][tomorrow.weekday()]})
- 后天: {day_after_tomorrow.isoformat()} ({['周一','周二','周三','周四','周五','周六','周日'][day_after_tomorrow.weekday()]})
- 本周一: {monday_this_week.isoformat()}
- 本周五: {friday_this_week.isoformat()}
- 下周一: {monday_next_week.isoformat()}
- 下周五: {friday_next_week.isoformat()}

相对时间转换指南：
- "今天" = {today.isoformat()}
- "明天" = {tomorrow.isoformat()}
- "后天" = {day_after_tomorrow.isoformat()}
- "大后天" = {(today + timedelta(days=3)).isoformat()}
- "下周X" = 下周一 + X天 (X为周一到周日的偏移)
- "晚上X点" = 使用24小时制，晚上6点 = 18:00
- "下午X点" = 使用24小时制，下午3点 = 15:00
- "早上X点" = 使用24小时制，早上9点 = 09:00

重复事件支持：
- 当用户要求创建"每周"、"每天"、"每月"等重复事件时，使用 recurrence_rule 参数
- recurrence_type: "daily"(每天), "weekly"(每周), "monthly"(每月)
- recurrence_days: 对于每周重复，指定具体星期几，如 ["monday", "tuesday", "friday"]
- recurrence_end_date: 重复事件的结束日期（可选，默认3个月后）
- 系统会自动生成多个独立的事件实例

重要提示：
1. 始终将相对时间转换为 ISO 8601 格式的具体日期时间（例如：2024-03-20T14:00:00）
2. 如果用户没有指定结束时间，默认事件持续1小时
3. 对于重复事件，recurrence_days 使用英文小写: monday, tuesday, wednesday, thursday, friday, saturday, sunday
4. 在创建、更新或删除事件后，向用户确认操作结果
5. 用友好、专业的语气与用户交流

"""
        
        # 添加 Skills 文档
        calendar_skill = skill_loader.get_skill("calendar")
        if calendar_skill:
            base_prompt += f"\n\n## Calendar Skill Documentation\n\n{calendar_skill}"
        
        return base_prompt
    
    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """
        处理用户消息
        
        Args:
            request: 聊天请求
            
        Returns:
            聊天响应
        """
        # 构建消息历史
        messages = self._build_messages(request)
        
        # 调用 Kimi API
        tool_calls = []
        events_modified = []
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools,
            tool_choice="auto"
        )
        
        # 处理响应
        assistant_message = ""
        response_message = response.choices[0].message
        
        # 处理工具调用
        if response_message.tool_calls:
            # 添加助手消息到历史
            messages.append({
                "role": "assistant",
                "content": response_message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in response_message.tool_calls
                ]
            })
            
            # 执行所有工具调用
            for tool_call in response_message.tool_calls:
                import json
                
                tool_name = tool_call.function.name
                tool_input = json.loads(tool_call.function.arguments)
                
                # 记录工具调用
                tool_calls.append({
                    "name": tool_name,
                    "input": tool_input
                })
                
                # 执行工具
                result = await self.mcp_server.execute_tool(tool_name, tool_input)
                
                # 记录修改的事件
                if result.get("success") and "event" in result:
                    events_modified.append(result["event"]["id"])
                
                # 添加工具结果
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": json.dumps(result, ensure_ascii=False)
                })
            
            # 继续对话获取最终回复
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            
            assistant_message = final_response.choices[0].message.content or ""
        else:
            assistant_message = response_message.content or ""
        
        return ChatResponse(
            message=assistant_message,
            tool_calls=tool_calls if tool_calls else None,
            events_modified=events_modified if events_modified else None
        )
    
    def _build_messages(self, request: ChatRequest) -> List[Dict[str, Any]]:
        """
        构建消息列表
        
        Args:
            request: 聊天请求
            
        Returns:
            消息列表
        """
        messages = []
        
        # 添加系统消息
        messages.append({
            "role": "system",
            "content": self.system_prompt
        })
        
        # 添加历史消息
        for msg in request.conversation_history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # 添加当前消息（包含当前时间信息）
        from datetime import datetime
        current_time = datetime.now().isoformat()
        
        user_message = f"[当前时间: {current_time}]\n\n{request.message}"
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages