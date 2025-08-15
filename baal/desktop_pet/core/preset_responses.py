"""
预设反应管理器

管理巴利在不同场景下的预设反应，与人设系统对齐
使用集中的预设对话配置
"""

from typing import Dict, List
from .persona_manager import PersonaLevel
from .preset_dialogues import PresetDialogues
import random


class PresetResponseManager:
    """预设反应管理器 - 作为PresetDialogues的兼容性接口"""
    
    def __init__(self):
        """初始化预设反应管理器"""
        pass
    
    @classmethod
    def get_response(cls, persona_level: PersonaLevel, scenario: str) -> str:
        """
        获取特定场景的预设反应
        
        Args:
            persona_level: 当前人设档位
            scenario: 场景标识符
            
        Returns:
            对应的预设反应文本
        """
        # 使用新的集中配置
        return PresetDialogues.get_dialogue(persona_level, "system", scenario)
    
    @classmethod
    def _get_default_response(cls, persona_level: PersonaLevel, scenario: str) -> str:
        """
        获取默认反应（当没有预设时）
        
        Args:
            persona_level: 当前人设档位
            scenario: 场景标识符
            
        Returns:
            默认反应文本
        """
        # 使用新的集中配置
        return PresetDialogues.get_dialogue(persona_level, "default", "default")
    
    @classmethod
    def get_supervision_reminder(cls, persona_level: PersonaLevel, deviation_level: str) -> str:
        """
        获取监督模式提醒（根据偏离程度）
        
        Args:
            persona_level: 当前人设档位
            deviation_level: 偏离程度 ("严重", "中度", "轻微")
            
        Returns:
            监督提醒文本
        """
        # 使用新的集中配置
        return PresetDialogues.get_dialogue(persona_level, "supervision", deviation_level)