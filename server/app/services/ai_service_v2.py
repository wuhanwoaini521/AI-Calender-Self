"""
AI Service v2 - With Function Calling / Tools / MCP Support

This service integrates with OpenAI-compatible APIs and supports:
- Tool calling (Function Calling)
- Skills (multi-step tool orchestration)
- MCP (Model Context Protocol)
"""

import json
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime, timedelta
from openai import AsyncOpenAI

from ..tools.registry import registry as tool_registry
from ..skills.registry import skill_registry, SkillContext
from ..mcp.server import MCPServer
from ..core.config import get_settings


class AIServiceV2:
    """AI Service with Function Calling and MCP support"""
    
    def __init__(self):
        settings = get_settings()
        
        # Initialize OpenAI client (supports OpenRouter, etc.)
        self.client = AsyncOpenAI(
            base_url=settings.OPENAI_BASE_URL,
            api_key=settings.OPENAI_API_KEY,
        )
        self.model = settings.OPENAI_MODEL
        self.mcp_server = MCPServer()
        
        # System prompt for the AI
        self.system_prompt = """你是AI日历助手，帮助用户管理日程。

你有以下工具可用，必须根据用户意图调用相应工具：
- create_event: 创建新的日历事件/会议/日程
- get_events: 查询指定日期范围的日程
- update_event: 更新已有事件
- delete_event: 删除事件
- find_free_slots: 查找空闲时间段
- detect_conflicts: 检测日程冲突
- generate_schedule: 生成优化日程
- optimize_schedule: 分析并建议日程优化
- suggest_breaks: 建议休息时间

强制规则（必须遵守）：
1. 当用户说"开会"、"有个会"、"创建事件"等包含时间表达的请求时，必须调用 create_event 工具，不要只回复文字。
2. 时间解析规则：
   - "明天" = 当前日期 + 1天
   - "今天" = 当前日期
   - "后天" = 当前日期 + 2天
   - "下午三点" = 15:00
   - "上午九点" = 09:00
   - "12点" = 12:00
   - "晚上8点" = 20:00
3. 默认会议时长60分钟（1小时）

示例调用：
用户："明天下午三点开会"
调用参数：
- title: "会议"
- start_time: "2026-02-06T15:00:00"
- end_time: "2026-02-06T16:00:00"

日期格式：YYYY-MM-DD
时间格式：HH:MM (24小时制，ISO 8601格式)
"""
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        user_id: str,
        context: Optional[Dict[str, Any]] = None,
        use_tools: bool = True,
    ) -> AsyncGenerator[str, None]:
        """
        Chat with function calling support
        
        Yields text chunks or tool results as they arrive
        """
        # Build messages
        chat_messages = [
            {"role": "system", "content": self.system_prompt},
            *messages,
        ]
        
        # Add context if available
        if context:
            context_str = self._format_context(context)
            chat_messages.insert(1, {
                "role": "system",
                "content": f"Current context:\n{context_str}"
            })
        
        # Get available tools
        tools = self.mcp_server.get_openai_tools() if use_tools else None
        print(f"[DEBUG] Available tools: {[t['function']['name'] for t in (tools or [])]}")
        print(f"[DEBUG] Messages: {chat_messages}")
        
        # Call LLM
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=chat_messages,
            tools=tools,
            tool_choice="auto" if use_tools else None,
            stream=True,
        )
        
        # Process streaming response
        current_tool_calls = {}
        
        async for chunk in response:
            delta = chunk.choices[0].delta
            
            # Handle content
            if delta.content:
                yield json.dumps({"type": "text", "content": delta.content})
            
            # Handle tool calls
            if delta.tool_calls:
                print(f"[DEBUG] Tool call delta: {delta.tool_calls}")
                for tc in delta.tool_calls:
                    index = tc.index
                    
                    if index not in current_tool_calls:
                        current_tool_calls[index] = {
                            "id": tc.id,
                            "function": {"name": "", "arguments": ""},
                        }
                    
                    if tc.function.name:
                        current_tool_calls[index]["function"]["name"] = tc.function.name
                        print(f"[DEBUG] Tool name: {tc.function.name}")
                    
                    if tc.function.arguments:
                        current_tool_calls[index]["function"]["arguments"] += tc.function.arguments
        
        # Execute tool calls
        tool_results = []
        print(f"[DEBUG] Current tool calls: {current_tool_calls}")
        if current_tool_calls:
            for tc in current_tool_calls.values():
                tool_name = tc["function"]["name"]
                try:
                    arguments = json.loads(tc["function"]["arguments"])
                except json.JSONDecodeError:
                    arguments = {}
                
                # Add user_id to arguments
                arguments["user_id"] = user_id
                
                # Execute tool
                result = await tool_registry.execute(tool_name, **arguments)
                
                # Store result for later
                tool_results.append({
                    "tool": tool_name,
                    "result": result,
                })
                
                # Yield tool result
                yield json.dumps({
                    "type": "tool_call",
                    "tool": tool_name,
                    "success": result.success,
                    "result": result.data if result.success else {"error": result.error},
                    "message": result.message,
                })
            
            # After tool execution, continue the conversation with results
            # Add assistant message with tool calls
            assistant_msg = {"role": "assistant", "content": None, "tool_calls": []}
            for i, tc in enumerate(current_tool_calls.values()):
                assistant_msg["tool_calls"].append({
                    "id": tc.get("id", f"call_{i}"),
                    "type": "function",
                    "function": tc["function"],
                })
            chat_messages.append(assistant_msg)
            
            # Add tool results
            for i, tr in enumerate(tool_results):
                tc_id = list(current_tool_calls.values())[i].get("id", f"call_{i}")
                chat_messages.append({
                    "role": "tool",
                    "tool_call_id": tc_id,
                    "content": json.dumps({
                        "success": tr["result"].success,
                        "message": tr["result"].message,
                        "data": tr["result"].data if tr["result"].success else {"error": tr["result"].error},
                    }, ensure_ascii=False),
                })
            
            # Get final response from AI
            final_response = await self.client.chat.completions.create(
                model=self.model,
                messages=chat_messages,
                stream=True,
            )
            
            async for chunk in final_response:
                if chunk.choices[0].delta.content:
                    yield json.dumps({"type": "text", "content": chunk.choices[0].delta.content})
    
    async def chat_with_skills(
        self,
        messages: List[Dict[str, str]],
        user_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Chat with skill detection and execution
        
        The AI can choose to use high-level skills for complex tasks
        """
        # First, determine if we should use a skill
        user_message = messages[-1]["content"] if messages else ""
        intent = await self._detect_intent(user_message)
        print(f"[DEBUG] Intent detection for '{user_message}': {intent}")
        
        # 检测是否是创建事件请求
        if self._is_create_event_intent(user_message):
            print(f"[DEBUG] Detected create event intent")
            async for chunk in self._handle_create_event(messages, user_message, user_id, context):
                yield chunk
            return
        
        if intent["use_skill"] and intent["skill"]:
            # Execute skill directly
            skill_context = SkillContext(
                user_id=user_id,
                current_date=datetime.utcnow(),
                selected_date=datetime.strptime(context.get("selected_date"), "%Y-%m-%d") if context and "selected_date" in context else None,
            )
            
            # Yield skill start
            yield json.dumps({
                "type": "skill_start",
                "skill": intent["skill"],
            })
            
            # Execute skill
            result = await skill_registry.execute(
                intent["skill"],
                skill_context,
                **intent.get("params", {}),
            )
            
            # Yield skill result
            yield json.dumps({
                "type": "skill_result",
                "skill": intent["skill"],
                "success": result.success,
                "message": result.message,
                "data": result.data,
                "steps": [s.model_dump(mode='json') for s in result.steps],
            })
            
            # Generate natural language response
            nl_response = await self._generate_nl_response(
                messages,
                result.message,
                context,
            )
            
            async for chunk in nl_response:
                yield chunk
        else:
            # Fall back to regular tool-based chat
            async for chunk in self.chat(messages, user_id, context, use_tools=True):
                yield chunk
    
    def _is_create_event_intent(self, message: str) -> bool:
        """检测是否是创建事件的意图"""
        message_lower = message.lower()
        event_keywords = ["会议", "meeting", "会", "日程", "事件", "event", "appointment", "约会"]
        time_keywords = ["点", "明天", "今天", "后天", "上午", "下午", "晚上", "早上"]
        
        has_event = any(word in message_lower for word in event_keywords)
        has_time = any(word in message_lower for word in time_keywords)
        
        return has_event and has_time
    
    async def _handle_create_event(
        self,
        messages: List[Dict[str, str]],
        user_message: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[str, None]:
        """处理创建事件请求 - 使用LLM解析"""
        from ..tools.registry import registry as tool_registry
        
        # 获取当前日期（支持驼峰和下划线两种命名）
        current_date = None
        if context:
            current_date = context.get("current_date") or context.get("currentDate")
        if not current_date:
            current_date = datetime.utcnow().strftime("%Y-%m-%d")
        print(f"[DEBUG] Current date: {current_date}, context: {context}")
        
        # 计算明天的日期
        today = datetime.strptime(current_date, "%Y-%m-%d")
        tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # 让 AI 解析时间参数
        parse_prompt = f"""解析用户的自然语言时间表达，提取事件信息。

当前日期：{current_date}
明天日期：{tomorrow}
用户输入："{user_message}"

规则：
1. 日期：
   - 如果提到"明天"，使用日期 {tomorrow}
   - 如果提到"今天"，使用日期 {current_date}
   - 如果提到"后天"，使用日期 {(today + timedelta(days=2)).strftime("%Y-%m-%d")}

2. 时间转换：
   - "下午三点" 或 "下午3点" = 15:00
   - "上午九点" 或 "上午9点" = 09:00
   - "12点" = 12:00
   - "晚上8点" = 20:00

3. 时长默认60分钟

必须返回有效的日期时间格式，示例：
{{"title": "会议", "start_time": "{tomorrow}T15:00:00", "end_time": "{tomorrow}T16:00:00"}}

只输出JSON，不要任何其他文字。"""

        try:
            print(f"[DEBUG] Calling LLM for time parsing...")
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是时间解析助手，只输出JSON格式的结果。"},
                    {"role": "user", "content": parse_prompt},
                ],
                timeout=10,  # 添加 10 秒超时
            )
            print(f"[DEBUG] LLM call completed")
            
            content = response.choices[0].message.content
            print(f"[DEBUG] LLM response: {content}")
            
            # 提取JSON部分
            import re
            json_match = re.search(r'\{[^}]*\}', content, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
            else:
                parsed = json.loads(content)
            
            print(f"[DEBUG] Parsed event: {parsed}")
            
            # 验证必要字段，如果 AI 返回空值，使用规则解析作为备用
            if not parsed.get("start_time") or not parsed.get("end_time"):
                print(f"[DEBUG] AI returned empty time, using fallback parser")
                parsed = self._parse_event_request(user_message, current_date)
                print(f"[DEBUG] Fallback parsed: {parsed}")
            
            # 调用创建事件工具
            result = await tool_registry.execute(
                "create_event",
                user_id=user_id,
                title=parsed.get("title", "新事件"),
                start_time=parsed["start_time"],
                end_time=parsed["end_time"],
            )
            
            # 输出工具调用结果
            yield json.dumps({
                "type": "tool_call",
                "tool": "create_event",
                "success": result.success,
                "result": result.data if result.success else {"error": result.error},
                "message": result.message,
            })
            
            # 生成自然语言回复
            if result.success:
                response_text = f"✅ 已为您创建事件：{parsed.get('title')}\n📅 时间：{parsed.get('start_time')} 至 {parsed.get('end_time')}"
            else:
                response_text = f"❌ 创建事件失败：{result.error}"
            
            yield json.dumps({"type": "text", "content": response_text})
            
        except Exception as e:
            print(f"[DEBUG] Error in _handle_create_event: {e}")
            yield json.dumps({"type": "text", "content": f"创建事件时出错：{str(e)}"})
    
    async def _detect_intent(self, message: str) -> Dict[str, Any]:
        """Detect user intent to determine if we should use a skill"""
        message_lower = message.lower()
        
        # Check for skill triggers
        if any(word in message_lower for word in ["我的日程", "schedule", "今天有什么", "今天安排"]):
            return {
                "use_skill": True,
                "skill": "schedule_management",
                "params": {},
            }
        
        # 检测创建事件的意图 - 包含时间+会议/事件/活动的表达
        create_keywords = ["创建", "新建", "添加", "安排", "schedule", "create", "add", "book"]
        event_keywords = ["会议", "meeting", "会", "event", "活动", "日程", "事情", "约会", "appointment"]
        time_keywords = ["点", "号", "号", "明天", "今天", "后天", "下午", "上午", "晚上", "早上", 
                        "am", "pm", "morning", "afternoon", "evening", "tomorrow", "today"]
        
        has_create = any(word in message_lower for word in create_keywords)
        has_event = any(word in message_lower for word in event_keywords)
        has_time = any(word in message_lower for word in time_keywords)
        
        # 如果包含事件关键词+时间，认为是创建事件（让AI用工具调用决定）
        if has_event and has_time:
            # 使用工具调用直接创建，不走技能路由
            return {"use_skill": False}
        
        # 仅查找空闲时间/规划会议时间，不创建
        if any(word in message_lower for word in ["什么时候有空", "find time", "约时间", "available", "有空"]):
            return {
                "use_skill": True,
                "skill": "meeting_planning",
                "params": {},
            }
        
        if any(word in message_lower for word in ["计划", "plan", "安排任务", "daily plan"]):
            return {
                "use_skill": True,
                "skill": "daily_planning",
                "params": {},
            }
        
        return {"use_skill": False}
    
    def _parse_event_request(self, message: str, current_date: str) -> Dict[str, str]:
        """使用规则解析事件请求（作为AI解析的备用）"""
        import re
        
        message_lower = message.lower()
        
        # 解析日期
        target_date = datetime.strptime(current_date, "%Y-%m-%d")
        if "明天" in message:
            target_date += timedelta(days=1)
        elif "后天" in message:
            target_date += timedelta(days=2)
        
        # 解析时间
        hour = 9
        minute = 0
        
        # 匹配时间
        time_patterns = [
            (r'(\d+):(\d+)', lambda m: (int(m.group(1)), int(m.group(2)))),
            (r'(\d+)点(\d+)分', lambda m: (int(m.group(1)), int(m.group(2)))),
            (r'(\d+)点', lambda m: (int(m.group(1)), 0)),
        ]
        
        for pattern, extractor in time_patterns:
            match = re.search(pattern, message)
            if match:
                hour, minute = extractor(match)
                break
        
        # 处理上午/下午/晚上
        if "下午" in message and hour < 12:
            hour += 12
        elif "晚上" in message and hour < 12:
            hour += 12
        elif "上午" in message and hour > 12:
            hour -= 12
        
        hour = max(0, min(23, hour))
        minute = max(0, min(59, minute))
        
        start_dt = target_date.replace(hour=hour, minute=minute)
        end_dt = start_dt + timedelta(minutes=60)
        
        # 提取标题
        title = "会议"
        if "约会" in message:
            title = "约会"
        elif "聚餐" in message:
            title = "聚餐"
        elif "活动" in message:
            title = "活动"
        
        return {
            "title": title,
            "start_time": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "end_time": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
        }
    
    async def _generate_nl_response(
        self,
        messages: List[Dict[str, str]],
        skill_result: str,
        context: Optional[Dict[str, Any]],
    ) -> AsyncGenerator[str, None]:
        """Generate natural language response based on skill result"""
        prompt = f"""Based on the following skill execution result, provide a helpful natural language response:

User message: {messages[-1]['content'] if messages else ''}

Skill result: {skill_result}

Respond in a helpful, conversational manner."""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful calendar assistant."},
                {"role": "user", "content": prompt},
            ],
            stream=True,
        )
        
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield json.dumps({
                    "type": "text",
                    "content": chunk.choices[0].delta.content,
                })
    
    async def mcp_handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request"""
        return await self.mcp_server.handle(request)
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context for the AI"""
        parts = []
        
        if "current_date" in context:
            current_date = context['current_date']
            parts.append(f"Current date: {current_date}")
            # Add day of week info
            try:
                dt = datetime.strptime(current_date, "%Y-%m-%d")
                weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                parts.append(f"Today is: {weekdays[dt.weekday()]}")
            except:
                pass
        
        if "selected_date" in context:
            parts.append(f"Selected date: {context['selected_date']}")
        
        if "events" in context and context["events"]:
            parts.append(f"Number of existing events: {len(context['events'])}")
            for event in context["events"][:5]:
                parts.append(f"  - {event.get('title', 'Untitled')} at {event.get('startTime', 'unknown')}")
        
        # Add timezone info
        parts.append("Timezone: UTC")
        
        return "\n".join(parts)
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools"""
        return [t.to_dict() for t in tool_registry.list_tools()]
    
    def get_available_skills(self) -> List[Dict[str, Any]]:
        """Get list of available skills"""
        return [s.to_dict() for s in skill_registry.list_skills()]


# Global instance
ai_service_v2 = AIServiceV2()
