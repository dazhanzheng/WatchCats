#!/usr/bin/env python3
"""
创建高质量 Windows ICO 文件
使用 baallogo.png 作为源文件生成包含多个分辨率的图标
"""

import sys
import os
from pathlib import Path
from PIL import Image

def create_high_quality_ico(source_png, output_ico):
    """
    创建包含多个分辨率的高质量 Windows ICO 文件
    
    Windows 需要的标准图标尺寸：
    - 16x16: 任务栏、窗口标题栏
    - 32x32: 桌面快捷方式（小图标视图）
    - 48x48: Windows XP 风格
    - 64x64: 中等图标
    - 128x128: 大图标视图
    - 256x256: 超大图标视图（Windows Vista+）
    """
    
    print(f"Creating high-quality ICO from: {source_png}")
    
    # 打开源图像
    img = Image.open(source_png)
    
    # 确保是 RGBA 模式
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # 定义所有需要的尺寸
    icon_sizes = [
        (16, 16),
        (24, 24),
        (32, 32),
        (48, 48),
        (64, 64),
        (128, 128),
        (256, 256)
    ]
    
    # 创建不同尺寸的图标
    icons = []
    for size in icon_sizes:
        # 使用 LANCZOS 重采样获得最佳质量
        resized = img.resize(size, Image.Resampling.LANCZOS)
        icons.append(resized)
        print(f"  Generated {size[0]}x{size[1]} icon")
    
    # 保存为 ICO 文件
    # 保存所有尺寸到一个 ICO 文件中
    icons[0].save(
        output_ico,
        format='ICO',
        sizes=icon_sizes,
        append_images=icons[1:]
    )
    
    # 验证文件大小
    file_size = os.path.getsize(output_ico)
    print(f"Created {output_ico}")
    print(f"File size: {file_size:,} bytes")
    
    # 如果文件太小，说明可能只包含了一个分辨率
    if file_size < 50000:  # 小于 50KB 可能有问题
        print("Warning: ICO file seems too small, may not contain all resolutions")
        print("Trying alternative method...")
        
        # 尝试另一种方法：直接保存最大的图标并让 PIL 处理
        img.save(
            output_ico,
            format='ICO',
            sizes=icon_sizes
        )
        
        new_size = os.path.getsize(output_ico)
        print(f"New file size: {new_size:,} bytes")
    
    return True

def main():
    """主函数"""
    script_dir = Path(__file__).parent.parent
    
    # 使用 baallogo.png 作为源文件
    source_files = [
        script_dir / "baal" / "resources" / "baallogo.png",
        script_dir / "动作表情拆分" / "baallogo.png",
        script_dir / "baal" / "resources" / "baal_logo.png",
    ]
    
    # 找到第一个存在的源文件
    source_png = None
    for file in source_files:
        if file.exists():
            source_png = file
            print(f"Using source file: {source_png}")
            break
    
    if not source_png:
        print("Error: No source PNG file found!")
        return 1
    
    # 输出文件路径
    output_ico = script_dir / "baal" / "resources" / "watchcats_hq.ico"
    
    # 创建高质量图标
    if create_high_quality_ico(source_png, output_ico):
        print("\n✅ Success! High-quality multi-resolution icon created.")
        print(f"📍 Location: {output_ico}")
        
        # 同时创建其他必要的 ICO 文件
        additional_icos = [
            script_dir / "baal" / "resources" / "app_icon.ico",
            script_dir / "baal" / "resources" / "cat.ico",
        ]
        
        for ico_path in additional_icos:
            try:
                import shutil
                shutil.copy2(output_ico, ico_path)
                print(f"📋 Copied to: {ico_path}")
            except Exception as e:
                print(f"⚠️  Failed to copy to {ico_path}: {e}")
        
        return 0
    else:
        print("\n❌ Failed to create icon")
        return 1

if __name__ == "__main__":
    sys.exit(main())