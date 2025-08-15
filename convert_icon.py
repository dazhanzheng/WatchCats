#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert PNG icon to ICO format for Windows
"""

import os
import sys
from PIL import Image

# Fix encoding issues on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def convert_png_to_ico(png_path, ico_path):
    """Convert PNG image to ICO format with multiple sizes"""
    try:
        # Open the PNG image
        img = Image.open(png_path)
        
        # Convert RGBA to RGB if necessary (ICO doesn't always handle transparency well)
        if img.mode == 'RGBA':
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Create multiple sizes for the ICO file
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # Save as ICO with multiple sizes
        img.save(ico_path, format='ICO', sizes=icon_sizes)
        print(f"Successfully converted {png_path} to {ico_path}")
        return True
        
    except Exception as e:
        print(f"Error converting icon: {e}")
        return False

def main():
    """Main function to convert icon"""
    # Define paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try different possible icon locations
    possible_icons = [
        os.path.join(script_dir, "baal", "resources", "baallogo.png"),  # Primary icon
        os.path.join(script_dir, "baal", "resources", "baal_logo.png"),  # Alternative name
        os.path.join(script_dir, "baal", "resources", "app_icon.png"),
        os.path.join(script_dir, "baal", "resources", "icon.png"),
    ]
    
    # Find the first existing icon
    png_path = None
    for icon_path in possible_icons:
        if os.path.exists(icon_path):
            png_path = icon_path
            # Use repr() to safely print paths with unicode characters
            print(f"Found icon at: {repr(png_path)}")
            break
    
    if not png_path:
        print("Warning: No PNG icon found, skipping icon conversion")
        # Create a simple default icon if none exists
        try:
            # Create a simple 256x256 black cat icon
            img = Image.new('RGB', (256, 256), color='black')
            ico_path = os.path.join(script_dir, "baal", "resources", "app_icon.ico")
            os.makedirs(os.path.dirname(ico_path), exist_ok=True)
            img.save(ico_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
            print("Created default black icon")
        except Exception as e:
            print(f"Could not create default icon: {e}")
        return 0  # Don't fail the build
    
    # Output path
    ico_path = os.path.join(script_dir, "baal", "resources", "app_icon.ico")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(ico_path), exist_ok=True)
    
    # Convert the icon
    if convert_png_to_ico(png_path, ico_path):
        return 0
    else:
        # Don't fail the build if icon conversion fails
        print("Warning: Icon conversion failed, continuing without icon")
        return 0

if __name__ == "__main__":
    sys.exit(main())