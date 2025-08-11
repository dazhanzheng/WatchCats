#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create a simple DMG background image
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_dmg_background():
    """Create a simple DMG background image"""
    
    # Image dimensions (600x400 as specified in DMG settings)
    width, height = 600, 400
    
    # Create a gradient background
    img = Image.new('RGB', (width, height), '#f0f0f0')
    draw = ImageDraw.Draw(img)
    
    # Draw a gradient
    for i in range(height):
        color_value = 240 - int(20 * (i / height))  # Subtle gradient
        color = (color_value, color_value, color_value + 5)
        draw.rectangle([(0, i), (width, i + 1)], fill=color)
    
    # Add text instructions
    try:
        # Try to use a system font
        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except:
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw arrow (simple lines)
    arrow_start = (250, 190)
    arrow_end = (350, 190)
    draw.line([arrow_start, arrow_end], fill='#666666', width=3)
    draw.polygon([
        (arrow_end[0] - 10, arrow_end[1] - 10),
        (arrow_end[0], arrow_end[1]),
        (arrow_end[0] - 10, arrow_end[1] + 10)
    ], fill='#666666')
    
    # Add text
    text = "Drag to Install"
    bbox = draw.textbbox((0, 0), text, font=font_large)
    text_width = bbox[2] - bbox[0]
    text_x = (width - text_width) // 2
    draw.text((text_x, 100), text, fill='#333333', font=font_large)
    
    # Add small instruction text
    instruction = "Drag the app icon to the Applications folder"
    bbox = draw.textbbox((0, 0), instruction, font=font_small)
    text_width = bbox[2] - bbox[0]
    text_x = (width - text_width) // 2
    draw.text((text_x, 280), instruction, fill='#666666', font=font_small)
    
    # Save the image
    output_path = 'installer/dmg_background.png'
    img.save(output_path, 'PNG')
    print(f"DMG background created: {output_path}")
    return True

if __name__ == "__main__":
    try:
        create_dmg_background()
    except ImportError:
        print("Please install Pillow: pip install Pillow")
        # Create a simple placeholder file
        import struct
        # Create a minimal 1x1 PNG
        with open('installer/dmg_background.png', 'wb') as f:
            # PNG header and minimal IHDR, IDAT, IEND chunks
            f.write(b'\x89PNG\r\n\x1a\n')
            f.write(b'\x00\x00\x00\rIHDR\x00\x00\x02X\x00\x00\x01\x90\x08\x02\x00\x00\x00')
            f.write(struct.pack('>I', 0))  # CRC placeholder
        print("Created placeholder dmg_background.png")