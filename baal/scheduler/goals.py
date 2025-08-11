"""
用户目标管理模块
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import os
from pathlib import Path


@dataclass
class Goal:
    """目标数据模型
    
    Attributes:
        title: 目标标题
        description: 目标详细描述
        type: 目标类型（'short_term' 或 'long_term'）
        priority: 优先级（1-5，5最高）
        created_at: 创建时间
        deadline: 截止日期（可选）
        is_active: 是否激活
        progress: 进度百分比（0-100）
        metadata: 额外的元数据
    """
    
    title: str
    description: str
    type: str  # 'short_term' or 'long_term'
    priority: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    is_active: bool = True
    progress: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（用于序列化）"""
        return {
            'title': self.title,
            'description': self.description,
            'type': self.type,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'is_active': self.is_active,
            'progress': self.progress,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Goal':
        """从字典创建实例（用于反序列化）"""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('deadline'):
            data['deadline'] = datetime.fromisoformat(data['deadline'])
        
        return cls(**data)


class GoalsManager:
    """目标管理器
    
    管理用户的长期和短期目标
    """
    
    def __init__(self):
        """初始化目标管理器"""
        self.config_dir = Path.home() / '.baal_pet'
        self.goals_file = self.config_dir / 'goals.json'
        self.goals: List[Goal] = []
        self.load_goals()
    
    def load_goals(self):
        """从文件加载目标"""
        if self.goals_file.exists():
            try:
                with open(self.goals_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.goals = [Goal.from_dict(g) for g in data.get('goals', [])]
            except Exception as e:
                print(f"加载目标失败: {e}")
                self.goals = []
        else:
            self.goals = []
            self._create_default_goals()
    
    def save_goals(self):
        """保存目标到文件"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            data = {
                'goals': [g.to_dict() for g in self.goals],
                'updated_at': datetime.now().isoformat()
            }
            with open(self.goals_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存目标失败: {e}")
    
    def _create_default_goals(self):
        """创建默认目标示例"""
        # 可以创建一些示例目标，用户可以修改
        pass
    
    def add_goal(self, goal: Goal) -> bool:
        """添加新目标"""
        self.goals.append(goal)
        self.save_goals()
        return True
    
    def update_goal(self, index: int, goal: Goal) -> bool:
        """更新目标"""
        if 0 <= index < len(self.goals):
            self.goals[index] = goal
            self.save_goals()
            return True
        return False
    
    def delete_goal(self, index: int) -> bool:
        """删除目标"""
        if 0 <= index < len(self.goals):
            del self.goals[index]
            self.save_goals()
            return True
        return False
    
    def get_active_goals(self) -> List[Goal]:
        """获取所有激活的目标"""
        return [g for g in self.goals if g.is_active]
    
    def get_short_term_goals(self) -> List[Goal]:
        """获取短期目标"""
        return [g for g in self.goals if g.type == 'short_term' and g.is_active]
    
    def get_long_term_goals(self) -> List[Goal]:
        """获取长期目标"""
        return [g for g in self.goals if g.type == 'long_term' and g.is_active]
    
    def get_goals_summary(self) -> str:
        """获取目标摘要（用于提供给LLM）"""
        short_term = self.get_short_term_goals()
        long_term = self.get_long_term_goals()
        
        summary = []
        
        if long_term:
            summary.append("长期目标：")
            for g in sorted(long_term, key=lambda x: x.priority, reverse=True)[:3]:
                summary.append(f"- {g.title} (优先级:{g.priority}, 进度:{g.progress:.0f}%)")
        
        if short_term:
            summary.append("\n短期目标：")
            for g in sorted(short_term, key=lambda x: x.priority, reverse=True)[:5]:
                deadline_str = f", 截止:{g.deadline.strftime('%Y-%m-%d')}" if g.deadline else ""
                summary.append(f"- {g.title} (优先级:{g.priority}, 进度:{g.progress:.0f}%{deadline_str})")
        
        return '\n'.join(summary) if summary else "暂无设定目标"