"""Skill Registry for managing all available skills"""

from typing import Dict, List, Type, Optional, Any
from .base import Skill, SkillContext, SkillResult


class SkillRegistry:
    """Registry for all skills"""
    
    _instance = None
    _skills: Dict[str, Skill] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, skill_class: Type[Skill]) -> Type[Skill]:
        """Register a skill class (can be used as decorator)"""
        skill = skill_class()
        self._skills[skill.name] = skill
        return skill_class
    
    def unregister(self, name: str):
        """Unregister a skill"""
        if name in self._skills:
            del self._skills[name]
    
    def get(self, name: str) -> Optional[Skill]:
        """Get a skill by name"""
        return self._skills.get(name)
    
    def list_skills(self) -> List[Skill]:
        """List all registered skills"""
        return list(self._skills.values())
    
    def get_schemas(self) -> List[Dict[str, Any]]:
        """Get all skill schemas"""
        return [skill.to_dict() for skill in self.list_skills()]
    
    async def execute(self, name: str, context: SkillContext, **kwargs) -> SkillResult:
        """Execute a skill by name"""
        skill = self.get(name)
        if not skill:
            return SkillResult(
                success=False,
                message=f"Skill not found: {name}",
            )
        
        try:
            result = await skill.execute(context, **kwargs)
            return result
        except Exception as e:
            return SkillResult(
                success=False,
                message=f"Skill execution failed: {str(e)}",
            )
    
    def find_by_tool(self, tool_name: str) -> List[Skill]:
        """Find all skills that use a specific tool"""
        return [s for s in self.list_skills() if tool_name in s.tools]
    
    def clear(self):
        """Clear all registered skills"""
        self._skills.clear()


# Global registry instance
skill_registry = SkillRegistry()
