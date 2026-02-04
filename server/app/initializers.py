"""Application initializers - Register tools and skills on startup"""

from .tools.registry import registry as tool_registry
from .skills.registry import skill_registry as skill_reg

# Import all tools
from .tools.calendar_tools import (
    CreateEventTool,
    GetEventsTool,
    UpdateEventTool,
    DeleteEventTool,
    FindFreeSlotsTool,
    DetectConflictsTool,
)
from .tools.schedule_tools import (
    GenerateScheduleTool,
    OptimizeScheduleTool,
    SuggestBreaksTool,
)

# Import all skills
from .skills.calendar_skills import (
    ScheduleManagementSkill,
    MeetingPlanningSkill,
    DailyPlanningSkill,
)


def register_tools():
    """Register all tools"""
    tools = [
        CreateEventTool,
        GetEventsTool,
        UpdateEventTool,
        DeleteEventTool,
        FindFreeSlotsTool,
        DetectConflictsTool,
        GenerateScheduleTool,
        OptimizeScheduleTool,
        SuggestBreaksTool,
    ]
    
    for tool_class in tools:
        tool_registry.register(tool_class)
    
    print(f"✅ Registered {len(tools)} tools")


def register_skills():
    """Register all skills"""
    skills = [
        ScheduleManagementSkill,
        MeetingPlanningSkill,
        DailyPlanningSkill,
    ]
    
    for skill_class in skills:
        skill_reg.register(skill_class)
    
    print(f"✅ Registered {len(skills)} skills")


def initialize():
    """Initialize application - called on startup"""
    register_tools()
    register_skills()
