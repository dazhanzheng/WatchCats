#!/bin/bash

# 创建巴利logo的icns图标文件

echo "🎨 Creating Baal logo icons..."

# 源文件
LOGO_SOURCE="动作表情拆分/巴利 logo.png"
LOGO_PNG="baal/resources/baal_logo.png"
LOGO_ICNS="baal/resources/baal_logo.icns"
LOGO_ICO="baal/resources/baal_logo.ico"

# 检查源文件
if [ ! -f "$LOGO_SOURCE" ]; then
    echo "❌ Error: Logo source not found: $LOGO_SOURCE"
    exit 1
fi

# 复制到resources目录（如果还没有）
if [ ! -f "$LOGO_PNG" ]; then
    echo "📋 Copying logo to resources..."
    cp "$LOGO_SOURCE" "$LOGO_PNG"
fi

# 创建macOS icns文件
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Creating macOS icns icon..."
    
    # 创建iconset目录
    mkdir -p baal_logo.iconset
    
    # 生成各种尺寸
    echo "  Generating icon sizes..."
    sips -z 16 16     "$LOGO_PNG" --out baal_logo.iconset/icon_16x16.png
    sips -z 32 32     "$LOGO_PNG" --out baal_logo.iconset/icon_16x16@2x.png
    sips -z 32 32     "$LOGO_PNG" --out baal_logo.iconset/icon_32x32.png
    sips -z 64 64     "$LOGO_PNG" --out baal_logo.iconset/icon_32x32@2x.png
    sips -z 128 128   "$LOGO_PNG" --out baal_logo.iconset/icon_128x128.png
    sips -z 256 256   "$LOGO_PNG" --out baal_logo.iconset/icon_128x128@2x.png
    sips -z 256 256   "$LOGO_PNG" --out baal_logo.iconset/icon_256x256.png
    sips -z 512 512   "$LOGO_PNG" --out baal_logo.iconset/icon_256x256@2x.png
    sips -z 512 512   "$LOGO_PNG" --out baal_logo.iconset/icon_512x512.png
    sips -z 1024 1024 "$LOGO_PNG" --out baal_logo.iconset/icon_512x512@2x.png
    
    # 转换为icns
    echo "  Converting to icns..."
    iconutil -c icns baal_logo.iconset -o "$LOGO_ICNS"
    
    # 清理临时文件
    rm -rf baal_logo.iconset
    
    if [ -f "$LOGO_ICNS" ]; then
        echo "✅ macOS icon created: $LOGO_ICNS"
    else
        echo "❌ Failed to create icns"
        exit 1
    fi
fi

# 创建Windows ico文件（使用Python）
echo "🪟 Creating Windows ico icon..."
python3 << EOF
from PIL import Image
import os

try:
    # 打开logo
    img = Image.open("$LOGO_PNG")
    
    # 确保是RGBA模式
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Windows ICO需要的尺寸
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    # 创建不同尺寸
    imgs = []
    for size in sizes:
        resized = img.resize(size, Image.Resampling.LANCZOS)
        imgs.append(resized)
    
    # 保存为ICO
    imgs[0].save("$LOGO_ICO", format='ICO', sizes=sizes)
    print("✅ Windows icon created: $LOGO_ICO")
    
except Exception as e:
    print(f"❌ Failed to create ico: {e}")
EOF

# 更新其他图标文件（兼容性）
echo "🔄 Updating compatibility icons..."
cp "$LOGO_ICNS" "baal/resources/cat.icns" 2>/dev/null || true
cp "$LOGO_ICNS" "baal/resources/watch_cats.icns" 2>/dev/null || true
cp "$LOGO_ICO" "baal/resources/cat.ico" 2>/dev/null || true

echo ""
echo "📊 Icon files created:"
ls -la baal/resources/*.icns 2>/dev/null
ls -la baal/resources/*.ico 2>/dev/null
echo ""
echo "✨ Done! Baal logo icons are ready for use."