#!/usr/bin/env python3
"""
将PNG图标转换为Windows ICO格式
"""

import os
import sys

def convert_png_to_ico():
    """转换PNG到ICO格式"""
    try:
        from PIL import Image
    except ImportError:
        print("请先安装Pillow库: pip install Pillow")
        return False
    
    png_path = "baal/resources/cat.png"
    ico_path = "baal/resources/cat.ico"
    
    if not os.path.exists(png_path):
        print(f"错误: 未找到源文件 {png_path}")
        return False
    
    try:
        # 打开PNG图片
        img = Image.open(png_path)
        
        # 确保是RGBA模式
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Windows ICO需要的标准尺寸
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # 创建不同尺寸的图标
        imgs = []
        for size in sizes:
            # 使用高质量的缩放算法
            resized = img.resize(size, Image.Resampling.LANCZOS)
            imgs.append(resized)
        
        # 保存为ICO格式
        imgs[0].save(ico_path, format='ICO', sizes=sizes)
        
        print(f"成功: 图标已保存到 {ico_path}")
        print(f"包含尺寸: {', '.join([f'{w}x{h}' for w, h in sizes])}")
        return True
        
    except Exception as e:
        print(f"错误: 转换失败 - {e}")
        return False

if __name__ == "__main__":
    success = convert_png_to_ico()
    sys.exit(0 if success else 1)