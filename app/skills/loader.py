import os
from pathlib import Path
from typing import Dict, Optional


class SkillLoader:
    """Skills 加载器 - 加载和管理 SKILL.md 文件"""
    
    def __init__(self, skills_dir: str='app/skills'):
        """
        初始化 Skills 加载器
        Args:
            skills_dir: Skills 目录路径
        """
        self.skills_dir = Path(skills_dir)
        self.skills: Dict[str, str] = {}
        self._load_all_skills()
    
    
    def _load_all_skills(self):
        """加载所有 SKILL.md文件"""
        if not self.skills_dir.exists():
            print("Warning: Skills directory {self.skills_dir} does not exist.")
            return 
        
        # 遍历所有子目录寻找SKILL.md 文件
        
        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    skill_name = skill_dir.name
                    self.skills[skill_name] = self._load_skill_file(skill_file)
                    print(f"Loaded skill: {skill_name}")
    
    def _load_skill_file(self, file_path: Path) -> str:
        """
        加载单个 SKILL.md 文件
        Args:
            file_path: SKILL.md 文件路径
        
        Returns:
            文件内容
        """ 
        
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    
    def get_skill(self, skill_name: str) -> Optional[str]:
        """
        获取指定 Skill 的内容
        
        Args:
            skill_name: Skill 名称
        Returns:
            Skill 内容，如果不存在则返回None
        """
        return self.skills.get(skill_name)

    def get_all_skills(self) -> Dict[str, str]:
        """
        获取所有 Skills 的内容
        
        Returns:
            包含所有 Skill 内容的字典，键为 Skill 名称，值为 Skill 内容
        """
        return self.skills
    
    def get_skill_names(self) -> list:
        """获取所有Skill名称"""
        return list(self.skills.keys())
    
    def get_combined_skills(self) -> str:
        """
        获取所有 SKills 的组合内容
        
        Returns:
            组合后的 Skill文档
        """
        combined = "# Available Skills\n\n"
        for skill_name, skill_content in self.skills.items():
            combined += f"## Skill: {skill_name}\n\n"
            combined += skill_content
            combined += "\n\n---\n\n"
        return combined
    

# 全局Skills 加载器实例
skill_loader = SkillLoader()
