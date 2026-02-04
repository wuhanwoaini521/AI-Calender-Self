"""
AI Service v2 - With Function Calling / Tools / MCP Support

This service integrates with OpenAI-compatible APIs and supports:
- Tool calling (Function Calling)
- Skills (multi-step tool orchestration)
- MCP (Model Context Protocol)
"""

import json
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
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
        self.system_prompt = """You are an AI calendar assistant. You help users manage their schedules efficiently.

You have access to the following tools:
- create_event: Create a new calendar event
- get_events: Retrieve events for a specific date range
- update_event: Update an existing event
- delete_event: Delete an event
- find_free_slots: Find available time slots
- detect_conflicts: Detect scheduling conflicts
- generate_schedule: Generate an optimized daily schedule
- optimize_schedule: Analyze and suggest schedule optimizations
- suggest_breaks: Suggest optimal break times

You also have access to high-level skills that combine multiple tools:
- schedule_management: View schedule, find conflicts, get optimization suggestions
- meeting_planning: Find optimal meeting times and schedule meetings
- daily_planning: Plan your day with tasks and breaks

When responding:
1. Be helpful and concise
2. Use tools when appropriate - don't just tell users what they could do, do it for them
3. Ask for clarification if needed
4. Provide actionable insights and suggestions
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
                for tc in delta.tool_calls:
                    index = tc.index
                    
                    if index not in current_tool_calls:
                        current_tool_calls[index] = {
                            "id": tc.id,
                            "function": {"name": "", "arguments": ""},
                        }
                    
                    if tc.function.name:
                        current_tool_calls[index]["function"]["name"] = tc.function.name
                    
                    if tc.function.arguments:
                        current_tool_calls[index]["function"]["arguments"] += tc.function.arguments
        
        # Execute tool calls
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
                
                # Yield tool result
                yield json.dumps({
                    "type": "tool_call",
                    "tool": tool_name,
                    "success": result.success,
                    "result": result.data if result.success else {"error": result.error},
                    "message": result.message,
                })
    
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
        intent = await self._detect_intent(messages[-1]["content"] if messages else "")
        
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
                "steps": [s.model_dump() for s in result.steps],
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
        
        if any(word in message_lower for word in ["会议", "meeting", "开会", "约时间"]):
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
            parts.append(f"Current date: {context['current_date']}")
        
        if "selected_date" in context:
            parts.append(f"Selected date: {context['selected_date']}")
        
        if "events" in context and context["events"]:
            parts.append(f"Number of events: {len(context['events'])}")
            for event in context["events"][:5]:
                parts.append(f"  - {event.get('title', 'Untitled')} at {event.get('startTime', 'unknown')}")
        
        return "\n".join(parts)
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools"""
        return [t.to_dict() for t in tool_registry.list_tools()]
    
    def get_available_skills(self) -> List[Dict[str, Any]]:
        """Get list of available skills"""
        return [s.to_dict() for s in skill_registry.list_skills()]


# Global instance
ai_service_v2 = AIServiceV2()
