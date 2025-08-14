# Windows Debug Build Script for Baal Pet Assistant
# This script builds a debug version with console output for troubleshooting

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Baal Pet Assistant - Windows Debug Build" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "`nUpgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install requirements
Write-Host "`nInstalling requirements..." -ForegroundColor Yellow
pip install -r requirements.txt
pip install pyinstaller==6.11.1

# Test environment first
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Testing environment..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
python test_windows_env.py

# Ask if user wants to continue
Write-Host "`nDo you want to continue with the build? (Y/N)" -ForegroundColor Yellow
$response = Read-Host
if ($response -ne 'Y' -and $response -ne 'y') {
    Write-Host "Build cancelled." -ForegroundColor Red
    exit 0
}

# Convert icon
Write-Host "`nConverting icon..." -ForegroundColor Yellow
python convert_icon.py

# Clean previous builds
Write-Host "`nCleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Path "build" -Recurse -Force }
if (Test-Path "dist") { Remove-Item -Path "dist" -Recurse -Force }

# Build with PyInstaller (debug version)
Write-Host "`nBuilding debug executable..." -ForegroundColor Yellow
pyinstaller --clean --noconfirm baal_windows_debug.spec

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nBuild failed!" -ForegroundColor Red
    exit 1
}

# Check if executable was created
$exePath = "dist\WatchCats_debug.exe"
if (Test-Path $exePath) {
    $exe = Get-Item $exePath
    Write-Host "`n✓ Debug executable created successfully!" -ForegroundColor Green
    Write-Host "  Path: $($exe.FullName)" -ForegroundColor Gray
    Write-Host "  Size: $([math]::Round($exe.Length / 1MB, 2)) MB" -ForegroundColor Gray
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Testing executable..." -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "The debug version will open with a console window." -ForegroundColor Yellow
    Write-Host "Check for any error messages in the console." -ForegroundColor Yellow
    Write-Host "`nPress Enter to run the executable..." -ForegroundColor Yellow
    Read-Host
    
    # Run the executable
    Start-Process -FilePath $exePath -NoNewWindow -Wait
    
} else {
    Write-Host "`n✗ Executable not found!" -ForegroundColor Red
    Write-Host "Check the build output above for errors." -ForegroundColor Red
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Debug build complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nIf the program crashes, check the console output for error messages." -ForegroundColor Yellow
Write-Host "Once issues are fixed, rebuild with the regular baal_windows.spec" -ForegroundColor Yellow