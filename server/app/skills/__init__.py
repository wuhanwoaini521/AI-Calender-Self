"""
Skills System for AI Calendar

Skills are higher-level capabilities that combine multiple tools to accomplish
complex tasks. Each skill has:
- name: Unique identifier
- description: What the skill does
- tools: List of tools used by this skill
- execute: Orchestration logic
"""

from .base import Skill, SkillContext, SkillResult
from .registry import SkillRegistry
from .calendar_skills import (
    ScheduleManagementSkill,
    MeetingPlanningSkill,
    DailyPlanningSkill,
)

__all__ = [
    # Base
    "Skill",
    "SkillContext",
    "SkillResult",
    "SkillRegistry",
    # Calendar Skills
    "ScheduleManagementSkill",
    "MeetingPlanningSkill",
    "DailyPlanningSkill",
]
