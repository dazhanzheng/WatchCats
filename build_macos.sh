#!/bin/bash

# Baal Pet Assistant macOS Build Script

echo "======================================"
echo "Baal Pet Assistant macOS Build Script"
echo "======================================"

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: This script must be run on macOS"
    exit 1
fi

# Check Python version
python3 --version || {
    echo "Error: Python 3 is not installed"
    echo "Install it with: brew install python3"
    exit 1
}

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install pyinstaller==6.11.1
pip install dmgbuild
pip install pillow

# Create icons if needed
echo "Preparing icons..."
if [ ! -f "baal/resources/cat.icns" ]; then
    echo "Creating icns file from PNG..."
    
    # Create iconset directory
    mkdir -p cat.iconset
    
    # Generate different sizes
    sips -z 16 16     baal/resources/cat.png --out cat.iconset/icon_16x16.png
    sips -z 32 32     baal/resources/cat.png --out cat.iconset/icon_16x16@2x.png
    sips -z 32 32     baal/resources/cat.png --out cat.iconset/icon_32x32.png
    sips -z 64 64     baal/resources/cat.png --out cat.iconset/icon_32x32@2x.png
    sips -z 128 128   baal/resources/cat.png --out cat.iconset/icon_128x128.png
    sips -z 256 256   baal/resources/cat.png --out cat.iconset/icon_128x128@2x.png
    sips -z 256 256   baal/resources/cat.png --out cat.iconset/icon_256x256.png
    sips -z 512 512   baal/resources/cat.png --out cat.iconset/icon_256x256@2x.png
    sips -z 512 512   baal/resources/cat.png --out cat.iconset/icon_512x512.png
    sips -z 1024 1024 baal/resources/cat.png --out cat.iconset/icon_512x512@2x.png
    
    # Convert to icns
    iconutil -c icns cat.iconset -o baal/resources/cat.icns
    
    # Clean up
    rm -rf cat.iconset
    
    echo "✓ Icon created successfully"
fi

# Copy to watch_cats.icns if needed
if [ ! -f "baal/resources/watch_cats.icns" ]; then
    cp baal/resources/cat.icns baal/resources/watch_cats.icns
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Build with PyInstaller
echo "Building application..."
if [ -f "baal_macos.spec" ]; then
    pyinstaller --clean --noconfirm baal_macos.spec
else
    echo "Using default spec file..."
    pyinstaller --clean --noconfirm baal.spec
fi

# Check if build was successful
if [ -d "dist/Baal Pet Assistant.app" ]; then
    APP_NAME="Baal Pet Assistant"
elif [ -d "dist/Watch Cats.app" ]; then
    APP_NAME="Watch Cats"
else
    echo "✗ Build failed! No app bundle found in dist/"
    exit 1
fi

echo "✓ App bundle created: dist/$APP_NAME.app"

# Create DMG
echo "Creating DMG installer..."

# Method 1: Try using create-dmg if available
if command -v create-dmg &> /dev/null; then
    echo "Using create-dmg..."
    create-dmg \
        --volname "$APP_NAME" \
        --volicon "baal/resources/cat.icns" \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --icon "$APP_NAME.app" 150 190 \
        --hide-extension "$APP_NAME.app" \
        --app-drop-link 450 190 \
        "dist/$APP_NAME.dmg" \
        "dist/$APP_NAME.app"
        
# Method 2: Try using dmgbuild if available
elif python -c "import dmgbuild" 2>/dev/null; then
    echo "Using dmgbuild..."
    dmgbuild -s installer/dmg_settings.py -D app="dist/$APP_NAME.app" "$APP_NAME" "dist/$APP_NAME.dmg"
    
# Method 3: Fallback to hdiutil
else
    echo "Using hdiutil (basic DMG)..."
    hdiutil create -volname "$APP_NAME" -srcfolder "dist/$APP_NAME.app" -ov -format UDZO "dist/$APP_NAME.dmg"
fi

# Check if DMG was created
if [ -f "dist/$APP_NAME.dmg" ]; then
    DMG_SIZE=$(du -h "dist/$APP_NAME.dmg" | cut -f1)
    echo ""
    echo "======================================"
    echo "✓ Build Successful!"
    echo "======================================"
    echo "App Bundle: dist/$APP_NAME.app"
    echo "DMG Installer: dist/$APP_NAME.dmg ($DMG_SIZE)"
    echo ""
    echo "To install:"
    echo "1. Open dist/$APP_NAME.dmg"
    echo "2. Drag $APP_NAME to Applications folder"
    echo "3. First run: Right-click and select 'Open'"
    echo ""
    
    # Optional: Open the DMG
    read -p "Open DMG now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open "dist/$APP_NAME.dmg"
    fi
else
    echo "✗ DMG creation failed!"
    exit 1
fi