"""Base classes for Skills"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime


class SkillContext(BaseModel):
    """Context passed to skills during execution"""
    user_id: str
    current_date: datetime
    selected_date: Optional[datetime] = None
    preferences: Optional[Dict[str, Any]] = None
    session_data: Dict[str, Any] = {}
    
    class Config:
        arbitrary_types_allowed = True


class SkillStep(BaseModel):
    """Represents a step in skill execution"""
    tool_name: str
    params: Dict[str, Any]
    result: Optional[Any] = None
    success: bool = True
    error: Optional[str] = None


class SkillResult(BaseModel):
    """Result of skill execution"""
    success: bool
    message: str
    data: Optional[Any] = None
    steps: List[SkillStep] = []
    suggestions: List[str] = []


class Skill(ABC):
    """Base class for all skills"""
    
    # Skill metadata
    name: str
    description: str
    tools: List[str]  # List of tool names used by this skill
    
    def __init__(self):
        self._validate_skill()
    
    def _validate_skill(self):
        """Validate skill definition"""
        assert self.name, "Skill must have a name"
        assert self.description, "Skill must have a description"
        assert isinstance(self.tools, list), "Tools must be a list"
    
    @abstractmethod
    async def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        """Execute the skill with given context and parameters"""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert skill to dictionary representation"""
        return {
            "name": self.name,
            "description": self.description,
            "tools": self.tools,
        }
