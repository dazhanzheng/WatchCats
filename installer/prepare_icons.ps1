# 在 Windows 构建环境中准备高质量图标
Write-Host "Preparing high-quality icons for Windows installer..."

# 确保在正确的目录
$installerDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $installerDir

# 创建 icons 目录
$iconsDir = Join-Path $installerDir "icons"
if (!(Test-Path $iconsDir)) {
    New-Item -ItemType Directory -Path $iconsDir | Out-Null
    Write-Host "Created icons directory"
}

# 安装 Pillow（如果需要）
Write-Host "Installing Pillow..."
pip install Pillow | Out-Null

# 创建 Python 脚本来生成图标
$iconScript = @'
#!/usr/bin/env python3
import os
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Installing Pillow...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "Pillow"], check=True)
    from PIL import Image

def create_ico_from_png(input_png, output_ico):
    """Create a multi-resolution ICO file from PNG"""
    # 打开源图片
    img = Image.open(input_png)
    
    # 转换为 RGBA
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # ICO 尺寸
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    # 创建各种尺寸
    icon_images = []
    for size in sizes:
        resized = img.resize(size, Image.Resampling.LANCZOS)
        if resized.mode != 'RGBA':
            resized = resized.convert('RGBA')
        icon_images.append(resized)
    
    # 保存为 ICO
    icon_images[0].save(
        output_ico,
        format='ICO',
        sizes=[img.size for img in icon_images],
        append_images=icon_images[1:]
    )
    print(f"Created ICO: {output_ico}")

# 查找 baallogo.png
script_dir = Path(__file__).parent
project_root = script_dir.parent

# 可能的图片位置
possible_paths = [
    project_root / "动作表情拆分" / "baallogo.png",
    project_root / "baal" / "resources" / "baallogo.png",
    project_root / "resources" / "baallogo.png",
]

input_png = None
for path in possible_paths:
    if path.exists():
        input_png = path
        print(f"Found source image: {input_png}")
        break

# 如果找不到源图片，创建一个默认的
if input_png is None:
    print("Source image not found, creating default icon...")
    # 创建一个简单的默认图标
    default_img = Image.new('RGBA', (256, 256), (60, 60, 60, 255))
    # 在中间画一个圆
    from PIL import ImageDraw
    draw = ImageDraw.Draw(default_img)
    draw.ellipse([64, 64, 192, 192], fill=(100, 150, 200, 255))
    input_png = script_dir / "default_icon.png"
    default_img.save(input_png)

# 生成 ICO
output_ico = script_dir / "icons" / "WatchCats.ico"
create_ico_from_png(input_png, output_ico)

# 同时生成 PNG 版本
img = Image.open(input_png)
if img.mode != 'RGBA':
    img = img.convert('RGBA')

# 256x256 PNG
png_256 = img.resize((256, 256), Image.Resampling.LANCZOS)
png_256.save(script_dir / "icons" / "WatchCats_256.png")
print("Created WatchCats_256.png")

# 512x512 PNG
png_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
png_512.save(script_dir / "icons" / "WatchCats_512.png")
print("Created WatchCats_512.png")

print("Icon generation completed!")
'@

# 保存并运行 Python 脚本
$iconScript | Out-File -FilePath "generate_icons.py" -Encoding UTF8
python generate_icons.py
Remove-Item generate_icons.py

# 检查是否成功生成
$icoPath = Join-Path $iconsDir "WatchCats.ico"
if (Test-Path $icoPath) {
    Write-Host "[OK] Icon generated successfully: $icoPath"
    $iconInfo = Get-Item $icoPath
    Write-Host "   Size: $($iconInfo.Length) bytes"
} else {
    Write-Host "[ERROR] Failed to generate icon"
    
    # 创建一个备用的空 ICO 文件
    Write-Host "Creating fallback icon..."
    
    # 使用 Python 创建一个简单的 ICO
    $fallbackScript = @'
from PIL import Image
import os
os.makedirs("icons", exist_ok=True)
img = Image.new('RGBA', (32, 32), (60, 60, 60, 255))
img.save("icons/WatchCats.ico", format='ICO')
print("Created fallback icon")
'@
    
    $fallbackScript | Out-File -FilePath "fallback_icon.py" -Encoding UTF8
    python fallback_icon.py
    Remove-Item fallback_icon.py
}

Write-Host "Icon preparation completed"