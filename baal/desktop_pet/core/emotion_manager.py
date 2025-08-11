"""
表情管理器

负责管理和加载表情图片
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional
from PyQt6.QtGui import QPixmap, QMovie
from PyQt6.QtCore import QSize
from .logger_config import get_logger


class EmotionManager:
    """表情管理器类"""
    
    # 表情标记到文件名的映射
    EMOTION_MAP = {
        "<#1>": "开心1.png",
        "<#2>": "开心2.png",
        "<#3>": "无语1.png",
        "<#4>": "无语2.png",
        "<#5>": "正常.png",
        "<#6>": "生气1.png",
        "<#7>": "生气2.png"
    }
    
    # 表情描述，用于prompt
    EMOTION_DESCRIPTIONS = """
表情标记说明（在适当时机使用）：
<#1> - 开心/愉悦
<#2> - 得意/满足
<#3> - 无语/不屑
<#4> - 鄙视/轻蔑
<#5> - 平静/正常
<#6> - 生气/愤怒
<#7> - 暴怒/极度愤怒
"""
    
    def __init__(self):
        """初始化表情管理器"""
        self.logger = get_logger('baal.desktop_pet.core.emotion_manager')
        self.logger.info("Initializing EmotionManager")
        
        # 获取正确的资源路径（支持PyInstaller打包）
        if getattr(sys, 'frozen', False):
            # 如果是打包后的应用
            base_path = Path(sys._MEIPASS)
            self.logger.debug("Running in frozen mode (PyInstaller)")
        else:
            # 如果是开发环境
            base_path = Path(__file__).parent.parent.parent.parent
            self.logger.debug("Running in development mode")
        
        # 表情文件夹路径
        self.emotion_dir = base_path / "动作表情拆分"
        self.logger.debug(f"Emotion directory: {self.emotion_dir}")
        
        # 缓存加载的表情图片
        self.emotion_pixmaps: Dict[str, QPixmap] = {}
        
        # 加载基础动画
        self.base_animation: Optional[QMovie] = None
        
        # 预加载所有资源
        try:
            self._load_resources()
            self.logger.info("EmotionManager initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize EmotionManager: {e}", exc_info=True)
            raise
    
    def _load_resources(self):
        """预加载所有表情和动画资源"""
        self.logger.info("Loading emotion resources")
        
        # 检查表情目录是否存在
        if not self.emotion_dir.exists():
            self.logger.error(f"Emotion directory does not exist: {self.emotion_dir}")
            return
            
        # 加载基础动画GIF
        gif_path = self.emotion_dir / "巴力2.gif"
        if gif_path.exists():
            try:
                self.base_animation = QMovie(str(gif_path))
                self.base_animation.setCacheMode(QMovie.CacheMode.CacheAll)
                self.logger.info(f"Successfully loaded base animation: {gif_path}")
            except Exception as e:
                self.logger.error(f"Failed to load base animation {gif_path}: {e}", exc_info=True)
        else:
            self.logger.warning(f"Base animation not found: {gif_path}")
        
        # 加载所有表情图片
        loaded_count = 0
        failed_count = 0
        
        for tag, filename in self.EMOTION_MAP.items():
            emotion_path = self.emotion_dir / filename
            if emotion_path.exists():
                try:
                    pixmap = QPixmap(str(emotion_path))
                    if not pixmap.isNull():
                        self.emotion_pixmaps[tag] = pixmap
                        self.logger.debug(f"Successfully loaded emotion {tag}: {filename}")
                        loaded_count += 1
                    else:
                        self.logger.warning(f"Failed to load emotion pixmap {tag}: {filename}")
                        failed_count += 1
                except Exception as e:
                    self.logger.error(f"Exception loading emotion {tag} ({filename}): {e}", exc_info=True)
                    failed_count += 1
            else:
                self.logger.warning(f"Emotion file not found {tag}: {emotion_path}")
                failed_count += 1
                
        self.logger.info(f"Resource loading complete: {loaded_count} emotions loaded, {failed_count} failed")
    
    def get_emotion_pixmap(self, emotion_tag: str) -> Optional[QPixmap]:
        """
        获取表情图片
        
        Args:
            emotion_tag: 表情标记，如 "<#1>"
            
        Returns:
            QPixmap 或 None
        """
        self.logger.debug(f"Requesting emotion pixmap: {emotion_tag}")
        
        pixmap = self.emotion_pixmaps.get(emotion_tag)
        if pixmap is not None:
            self.logger.debug(f"Emotion pixmap found for {emotion_tag}")
        else:
            self.logger.warning(f"Emotion pixmap not found for {emotion_tag}")
            
        return pixmap
    
    def get_base_animation(self) -> Optional[QMovie]:
        """获取基础动画"""
        if self.base_animation is not None:
            self.logger.debug("Base animation available")
        else:
            self.logger.debug("Base animation not available")
            
        return self.base_animation
    
    def extract_emotion_from_text(self, text: str) -> tuple[str, Optional[str]]:
        """
        从文本中提取表情标记
        
        Args:
            text: 包含表情标记的文本
            
        Returns:
            (清理后的文本, 最后一个表情标记)
        """
        self.logger.debug(f"Extracting emotion from text: {text[:50]}...")
        
        last_emotion = None
        clean_text = text
        emotions_found = []
        
        # 查找所有表情标记
        for emotion_tag in self.EMOTION_MAP.keys():
            if emotion_tag in text:
                last_emotion = emotion_tag
                emotions_found.append(emotion_tag)
                # 移除所有该表情标记
                clean_text = clean_text.replace(emotion_tag, "")
        
        # 清理多余的空格
        clean_text = " ".join(clean_text.split())
        
        if emotions_found:
            self.logger.info(f"Emotions found in text: {emotions_found}, using: {last_emotion}")
        else:
            self.logger.debug("No emotions found in text")
            
        self.logger.debug(f"Cleaned text: {clean_text[:50]}...")
        
        return clean_text, last_emotion
    
    def get_default_emotion(self) -> str:
        """获取默认表情标记"""
        default = "<#5>"  # 正常表情
        self.logger.debug(f"Returning default emotion: {default}")
        return default