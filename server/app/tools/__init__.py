"""
Tools System for AI Calendar

Tools are executable functions that the AI can call to interact with the calendar system.
Each tool has:
- name: Unique identifier
- description: What the tool does
- parameters: JSON Schema for inputs
- execute: The actual function to run
"""

from .base import Tool, ToolParameter, ToolResult
from .registry import ToolRegistry
from .calendar_tools import (
    CreateEventTool,
    GetEventsTool,
    UpdateEventTool,
    DeleteEventTool,
    FindFreeSlotsTool,
    DetectConflictsTool,
)
from .schedule_tools import (
    GenerateScheduleTool,
    OptimizeScheduleTool,
    SuggestBreaksTool,
)

__all__ = [
    # Base
    "Tool",
    "ToolParameter", 
    "ToolResult",
    "ToolRegistry",
    # Calendar Tools
    "CreateEventTool",
    "GetEventsTool",
    "UpdateEventTool",
    "DeleteEventTool",
    "FindFreeSlotsTool",
    "DetectConflictsTool",
    # Schedule Tools
    "GenerateScheduleTool",
    "OptimizeScheduleTool",
    "SuggestBreaksTool",
]
