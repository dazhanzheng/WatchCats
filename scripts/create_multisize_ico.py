#!/usr/bin/env python3
"""
Create a multi-resolution Windows ICO file
Uses Pillow to create proper Windows icons with multiple embedded sizes
"""

import sys
import os
from PIL import Image

def create_multi_resolution_ico(source_png, output_ico):
    """Create a Windows ICO with multiple resolutions for crisp display"""
    
    # Load source image
    img = Image.open(source_png)
    
    # Convert to RGBA if needed
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Windows icon sizes - from small to large
    # Including all standard sizes for best quality
    icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    # Create list of resized images
    ico_images = []
    for size in icon_sizes:
        # Create a new image with the target size
        resized = img.resize(size, Image.Resampling.LANCZOS)
        ico_images.append(resized)
    
    # Save as ICO - Pillow will embed all sizes
    # We save from the first image and append the rest
    ico_images[0].save(
        output_ico,
        format='ICO',
        append_images=ico_images[1:],
        sizes=icon_sizes
    )
    
    print(f"Created {output_ico}")
    print(f"Embedded sizes: {icon_sizes}")
    
    # Verify file was created
    if os.path.exists(output_ico):
        file_size = os.path.getsize(output_ico)
        print(f"File size: {file_size:,} bytes")
        return True
    return False

if __name__ == "__main__":
    source = "baal/resources/cat.png"
    output = "baal/resources/watchcats_hq.ico"
    
    if not os.path.exists(source):
        print(f"Error: Source file {source} not found")
        sys.exit(1)
    
    if create_multi_resolution_ico(source, output):
        print("Success! High-quality multi-resolution icon created.")
    else:
        print("Failed to create icon file")
        sys.exit(1)