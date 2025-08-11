#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert PNG icon to Windows ICO format
"""

import os
import sys
import io

# Force UTF-8 encoding for stdout
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def convert_png_to_ico():
    """Convert PNG to ICO format"""
    try:
        from PIL import Image
    except ImportError:
        print("Error: Please install Pillow library: pip install Pillow")
        return False
    
    png_path = "baal/resources/cat.png"
    ico_path = "baal/resources/cat.ico"
    
    if not os.path.exists(png_path):
        print(f"Error: Source file not found: {png_path}")
        return False
    
    try:
        # Open PNG image
        img = Image.open(png_path)
        
        # Ensure RGBA mode
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Standard sizes for Windows ICO
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # Create different sized icons
        imgs = []
        for size in sizes:
            # Use high quality resampling
            resized = img.resize(size, Image.Resampling.LANCZOS)
            imgs.append(resized)
        
        # Save as ICO format
        imgs[0].save(ico_path, format='ICO', sizes=sizes)
        
        print(f"Success: Icon saved to {ico_path}")
        print(f"Sizes included: {', '.join([f'{w}x{h}' for w, h in sizes])}")
        return True
        
    except Exception as e:
        print(f"Error: Conversion failed - {e}")
        return False

if __name__ == "__main__":
    success = convert_png_to_ico()
    sys.exit(0 if success else 1)