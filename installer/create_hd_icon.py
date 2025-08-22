#!/usr/bin/env python3
"""
创建高质量 Windows ICO 图标
保留原始高分辨率，生成多尺寸图标
"""

import os
import sys
from pathlib import Path
from PIL import Image

def create_high_quality_ico(input_png, output_ico):
    """
    从高分辨率 PNG 创建包含多种尺寸的 ICO 文件
    保持最高质量，不过度压缩
    """
    # 打开原始图片
    img = Image.open(input_png)
    
    # 如果有透明通道，保留它
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Windows ICO 推荐的尺寸
    # 包含从小到大的多种尺寸，确保在不同场景下都清晰
    sizes = [
        (16, 16),    # 小图标（文件列表）
        (24, 24),    # 小图标（扩展）
        (32, 32),    # 标准图标
        (48, 48),    # 大图标
        (64, 64),    # 超大图标
        (128, 128),  # 超高清图标
        (256, 256)   # 最高清图标（Windows Vista+）
    ]
    
    # 创建多尺寸图标列表
    icon_images = []
    
    for size in sizes:
        # 使用 LANCZOS 重采样获得最佳质量
        resized = img.resize(size, Image.Resampling.LANCZOS)
        
        # 确保是 RGBA 模式
        if resized.mode != 'RGBA':
            resized = resized.convert('RGBA')
        
        icon_images.append(resized)
    
    # 保存为 ICO 文件
    # 使用最大的图像作为主图像，其余作为附加尺寸
    icon_images[0].save(
        output_ico,
        format='ICO',
        sizes=[img.size for img in icon_images],
        append_images=icon_images[1:]
    )
    
    print(f"✓ 创建高质量 ICO: {output_ico}")
    print(f"  包含尺寸: {', '.join([f'{w}x{h}' for w, h in sizes])}")

def main():
    # 获取路径
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # 输入文件
    input_png = project_root / "动作表情拆分" / "baallogo.png"
    
    # 输出文件
    output_dir = script_dir / "icons"
    output_dir.mkdir(exist_ok=True)
    
    output_ico = output_dir / "WatchCats.ico"
    
    # 检查输入文件
    if not input_png.exists():
        print(f"错误: 找不到输入文件 {input_png}")
        sys.exit(1)
    
    try:
        # 创建高质量 ICO
        create_high_quality_ico(input_png, output_ico)
        
        # 同时保存一份高清 PNG（用于其他用途）
        img = Image.open(input_png)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # 保存 256x256 的 PNG 版本
        png_256 = img.resize((256, 256), Image.Resampling.LANCZOS)
        png_256_path = output_dir / "WatchCats_256.png"
        png_256.save(png_256_path, 'PNG')
        print(f"✓ 创建高清 PNG: {png_256_path}")
        
        # 保存 512x512 的 PNG 版本（用于更高分辨率显示）
        png_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
        png_512_path = output_dir / "WatchCats_512.png"
        png_512.save(png_512_path, 'PNG')
        print(f"✓ 创建超高清 PNG: {png_512_path}")
        
        print("\n成功创建所有图标文件！")
        print(f"图标目录: {output_dir}")
        
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()