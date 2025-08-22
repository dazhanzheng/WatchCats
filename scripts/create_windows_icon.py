"""
Create high-quality Windows ICO file with multiple resolutions
"""
import sys
from PIL import Image
import os

def create_ico(png_path, ico_path):
    """Create a Windows ICO file with multiple resolutions"""
    
    # Open the source PNG
    img = Image.open(png_path)
    
    # Ensure RGBA mode
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Define the sizes for Windows icons (16, 24, 32, 48, 64, 128, 256)
    sizes = [
        (16, 16),
        (24, 24),
        (32, 32),
        (48, 48),
        (64, 64),
        (128, 128),
        (256, 256)
    ]
    
    # Create resized versions
    icons = []
    for size in sizes:
        # Use LANCZOS for high-quality downsampling
        resized = img.resize(size, Image.Resampling.LANCZOS)
        icons.append(resized)
    
    # Save as ICO with all sizes
    # Save the largest icon first with all smaller sizes as append_images
    icons[-1].save(
        ico_path,
        format='ICO',
        sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (24, 24), (16, 16)]
    )
    
    print(f"Created {ico_path} with resolutions: {[s for s in sizes]}")

if __name__ == "__main__":
    # Create the high-quality icon
    source_png = "baal/resources/cat.png"
    output_ico = "baal/resources/watchcats.ico"
    
    if os.path.exists(source_png):
        create_ico(source_png, output_ico)
        print(f"Successfully created high-quality icon: {output_ico}")
    else:
        print(f"Error: Source file {source_png} not found")
        sys.exit(1)