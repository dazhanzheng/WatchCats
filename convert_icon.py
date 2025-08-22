#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert PNG icon to ICO format for Windows
"""

import os
import sys
from PIL import Image, ImageDraw

# Fix encoding issues on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def create_rounded_rectangle_mask(size, radius):
    """Create a mask for rounded rectangle"""
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    
    # Draw the rounded rectangle
    draw.rounded_rectangle(
        [(0, 0), (size[0]-1, size[1]-1)],
        radius=radius,
        fill=255
    )
    
    return mask

def convert_png_to_ico(png_path, ico_path):
    """Convert PNG image to ICO format with multiple sizes, full coverage and rounded corners"""
    try:
        # Open the PNG image
        img = Image.open(png_path)
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Create multiple sizes for the ICO file
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # Process each size
        icons = []
        for size in icon_sizes:
            # Create a new image with the target size
            resized = img.resize(size, Image.Resampling.LANCZOS)
            
            # Create rounded corners for larger sizes (32x32 and above)
            if size[0] >= 32:
                # Calculate radius based on size (about 15% of the size)
                radius = int(size[0] * 0.15)
                
                # Create a rounded rectangle mask
                mask = create_rounded_rectangle_mask(size, radius)
                
                # Create output image with transparent background
                output = Image.new('RGBA', size, (0, 0, 0, 0))
                
                # Apply the rounded mask
                output.paste(resized, (0, 0))
                output.putalpha(mask)
                
                # Create final image with white background for ICO compatibility
                final = Image.new('RGB', size, (255, 255, 255))
                final.paste(output, (0, 0), output)
                
                icons.append(final)
            else:
                # For small sizes (16x16), keep sharp corners for clarity
                if resized.mode == 'RGBA':
                    # Convert RGBA to RGB with white background
                    background = Image.new('RGB', size, (255, 255, 255))
                    background.paste(resized, mask=resized.split()[3])
                    icons.append(background)
                else:
                    icons.append(resized)
        
        # Save as ICO with multiple sizes
        icons[0].save(ico_path, format='ICO', sizes=icon_sizes, append_images=icons[1:])
        print(f"Successfully converted {png_path} to {ico_path} with rounded corners")
        return True
        
    except Exception as e:
        print(f"Error converting icon: {e}")
        # Fallback to simple conversion if rounded rectangle fails
        try:
            img = Image.open(png_path)
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(ico_path, format='ICO', sizes=icon_sizes)
            print(f"Converted using fallback method (no rounded corners)")
            return True
        except:
            return False

def main():
    """Main function to convert icon"""
    # Define paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try different possible icon locations - prioritize baallogo.png for clarity
    possible_icons = [
        os.path.join(script_dir, "baal", "resources", "baallogo.png"),  # Primary icon - 512x512 clear logo
        os.path.join(script_dir, "动作表情拆分", "baallogo.png"),  # Alternative location
        os.path.join(script_dir, "baal", "resources", "cat.png"),  # WatchCats cat icon
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
    
    # Output path - create high-quality icon for WatchCats
    ico_path = os.path.join(script_dir, "baal", "resources", "watchcats_hq.ico")
    
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