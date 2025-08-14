#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
资源管理器 - 统一处理资源文件路径
解决打包后资源文件找不到的问题
"""

import os
import sys
from pathlib import Path
from typing import Optional, Union

class ResourceManager:
    """统一的资源管理器"""
    
    _instance = None
    _base_path = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """初始化资源基础路径"""
        if getattr(sys, 'frozen', False):
            # 运行在打包后的环境
            self._base_path = Path(sys._MEIPASS)
            print(f"[ResourceManager] Running in frozen mode, base path: {self._base_path}")
        else:
            # 运行在开发环境
            # 向上查找项目根目录（包含 run_desktop_pet.py 的目录）
            current = Path(__file__).resolve()
            while current.parent != current:
                if (current / 'run_desktop_pet.py').exists():
                    self._base_path = current
                    break
                current = current.parent
            
            if self._base_path is None:
                # 使用默认路径
                self._base_path = Path(__file__).parent.parent.parent.parent
            
            print(f"[ResourceManager] Running in development mode, base path: {self._base_path}")
    
    def get_resource_path(self, relative_path: Union[str, Path]) -> Path:
        """
        获取资源文件的绝对路径
        
        Args:
            relative_path: 相对于项目根目录的路径
            
        Returns:
            资源文件的绝对路径
        """
        resource_path = self._base_path / relative_path
        
        # 在 Windows 上处理路径分隔符
        if sys.platform == 'win32':
            resource_path = Path(str(resource_path).replace('/', '\\'))
        
        if not resource_path.exists():
            print(f"[ResourceManager] Warning: Resource not found: {resource_path}")
            # 尝试其他可能的位置
            alternatives = [
                self._base_path / 'baal' / relative_path,
                self._base_path / 'dist' / relative_path,
                Path.cwd() / relative_path,
            ]
            for alt in alternatives:
                if alt.exists():
                    print(f"[ResourceManager] Found alternative: {alt}")
                    return alt
        
        return resource_path
    
    def get_emotion_image(self, emotion: str) -> Optional[Path]:
        """获取表情图片路径"""
        # 尝试多个可能的文件名格式
        possible_names = [
            f"巴力-{emotion}.png",
            f"巴力_{emotion}.png",
            f"baal_{emotion}.png",
            f"{emotion}.png",
        ]
        
        for name in possible_names:
            path = self.get_resource_path(f"动作表情拆分/{name}")
            if path.exists():
                return path
        
        print(f"[ResourceManager] Warning: Emotion image not found for: {emotion}")
        return None
    
    def get_base_animation(self) -> Optional[Path]:
        """获取基础动画 GIF"""
        gif_path = self.get_resource_path("动作表情拆分/巴力2.gif")
        if not gif_path.exists():
            # 尝试其他可能的名称
            alternatives = [
                "动作表情拆分/巴力.gif",
                "动作表情拆分/baal.gif",
                "动作表情拆分/animation.gif",
            ]
            for alt in alternatives:
                alt_path = self.get_resource_path(alt)
                if alt_path.exists():
                    return alt_path
        return gif_path if gif_path.exists() else None
    
    def get_icon(self) -> Optional[Path]:
        """获取应用图标"""
        # 根据平台选择图标格式
        if sys.platform == 'win32':
            icon_paths = [
                "baal/resources/app_icon.ico",
                "baal/resources/cat.ico",
                "resources/app_icon.ico",
            ]
        else:
            icon_paths = [
                "baal/resources/cat.png",
                "baal/resources/icon.png",
                "resources/cat.png",
            ]
        
        for icon_path in icon_paths:
            path = self.get_resource_path(icon_path)
            if path.exists():
                return path
        
        return None
    
    def verify_resources(self) -> bool:
        """验证所有必要的资源是否存在"""
        required_resources = [
            "动作表情拆分",  # 表情目录
            "baal/resources",  # 资源目录
        ]
        
        missing = []
        for resource in required_resources:
            path = self.get_resource_path(resource)
            if not path.exists():
                missing.append(resource)
                print(f"[ResourceManager] Missing required resource: {resource}")
        
        if missing:
            print(f"[ResourceManager] Missing resources: {missing}")
            return False
        
        print("[ResourceManager] All required resources verified")
        return True
    
    @classmethod
    def get_instance(cls) -> 'ResourceManager':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


# 便捷函数
def get_resource_path(relative_path: Union[str, Path]) -> Path:
    """获取资源路径的便捷函数"""
    return ResourceManager.get_instance().get_resource_path(relative_path)

def get_emotion_image(emotion: str) -> Optional[Path]:
    """获取表情图片的便捷函数"""
    return ResourceManager.get_instance().get_emotion_image(emotion)

def get_base_animation() -> Optional[Path]:
    """获取基础动画的便捷函数"""
    return ResourceManager.get_instance().get_base_animation()

def get_icon() -> Optional[Path]:
    """获取应用图标的便捷函数"""
    return ResourceManager.get_instance().get_icon()

def verify_resources() -> bool:
    """验证资源的便捷函数"""
    return ResourceManager.get_instance().verify_resources()