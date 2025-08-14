# Windows Build Instructions for Baal Pet Assistant

## Prerequisites

1. **Python 3.9** (exactly this version for best compatibility)
2. **Visual C++ Redistributable 2015-2022** (required for PyQt6)
   - Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
3. **Git** (for cloning the repository)

## Build Steps

### 1. Prepare Environment

```powershell
# Clone repository
git clone https://github.com/your-repo/baal-standalone.git
cd baal-standalone

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
pip install pyinstaller==6.11.1
```

### 2. Test Environment

```powershell
# Run environment test
python test_windows_env.py
```

If any tests fail, resolve the issues before proceeding.

### 3. Fix Path Issues (if needed)

```powershell
# Fix unicode path issues
python fix_paths_windows.py
```

### 4. Build Executable

#### For Debugging (with console)
```powershell
.\build_windows_debug.bat
```

#### For Production (no console)
```powershell
# Convert icon
python convert_icon.py

# Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

# Build with PyInstaller
pyinstaller --clean --noconfirm baal_windows.spec
```

### 5. Test Executable

```powershell
# Run the executable
.\dist\WatchCats.exe

# If it crashes, check the debug version
.\dist\WatchCats_Debug.exe
```

## Troubleshooting

### Immediate Crash on Startup

1. **Run debug version** to see console output
2. **Check baal_debug.log** for detailed error information
3. **Common causes:**
   - Missing Visual C++ Redistributable
   - Qt platform plugin not found
   - Path encoding issues with Chinese characters
   - Missing hidden imports

### "Failed to execute script" Error

1. **Verify all dependencies** are installed:
   ```powershell
   pip list
   ```

2. **Check for missing DLLs** using Dependency Walker

3. **Try building with console=True** to see errors

### Qt Platform Plugin Error

1. **Ensure PyQt6 is properly installed:**
   ```powershell
   pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip
   pip install PyQt6==6.5.3
   ```

2. **Check Qt plugins are included** in the build

### Icon Issues

1. **Ensure icon exists:**
   ```powershell
   dir baal\resources\*.ico
   ```

2. **If missing, run:**
   ```powershell
   python convert_icon.py
   ```

## Build Artifacts

After successful build, you should have:

- `dist/WatchCats.exe` - Main executable
- `dist/WatchCats_Debug.exe` - Debug version (if built)
- `baal_debug.log` - Debug log (created on first run)

## Distribution

For distribution, package the entire `dist` folder contents, including:
- The .exe file
- Any .dll files
- The _internal folder (if present)

Create a ZIP archive:
```powershell
Compress-Archive -Path dist\* -DestinationPath BaalPetAssistant-Windows.zip
```

## Notes

- The app requires internet connection for AI features
- First run will prompt for API key configuration
- Configuration is saved to `%APPDATA%\BaalPet\config.json`
- Logs are saved to `%APPDATA%\BaalPet\logs\`