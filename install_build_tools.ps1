# Install Microsoft Visual C++ Build Tools for PyQt6-sip compilation
Write-Host "================================================" -ForegroundColor Cyan
Write-Host " Installing Build Tools for Python Packages" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠ Warning: Not running as Administrator" -ForegroundColor Yellow
    Write-Host "Some installations may require admin privileges" -ForegroundColor Yellow
    Write-Host ""
}

# Option 1: Install Visual Studio Build Tools (Recommended)
Write-Host "Option 1: Visual Studio Build Tools (Recommended)" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Gray
Write-Host ""
Write-Host "Download and install from:" -ForegroundColor Yellow
Write-Host "https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Cyan
Write-Host ""
Write-Host "During installation, select:" -ForegroundColor Yellow
Write-Host "  • Desktop development with C++" -ForegroundColor Gray
Write-Host "  • MSVC v143 - VS 2022 C++ x64/x86 build tools" -ForegroundColor Gray
Write-Host "  • Windows SDK" -ForegroundColor Gray
Write-Host ""

# Option 2: Use pre-compiled wheels
Write-Host "Option 2: Use Pre-compiled Wheels (Alternative)" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Gray
Write-Host ""
Write-Host "Instead of compiling, download pre-compiled wheels:" -ForegroundColor Yellow
Write-Host ""

# Check Python version
$pythonVersion = python --version 2>&1
Write-Host "Your Python: $pythonVersion" -ForegroundColor Cyan

# Determine wheel URL based on Python version
if ($pythonVersion -match "3\.13") {
    Write-Host "For Python 3.13, you need PyQt6-sip wheel for cp313" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Try downloading from:" -ForegroundColor Yellow
    Write-Host "https://pypi.org/project/PyQt6-sip/#files" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Look for: PyQt6_sip-13.6.0-cp313-cp313-win_amd64.whl" -ForegroundColor Gray
} elseif ($pythonVersion -match "3\.12") {
    Write-Host "For Python 3.12, download:" -ForegroundColor Yellow
    Write-Host "PyQt6_sip-13.6.0-cp312-cp312-win_amd64.whl" -ForegroundColor Gray
} elseif ($pythonVersion -match "3\.11") {
    Write-Host "For Python 3.11, download:" -ForegroundColor Yellow
    Write-Host "PyQt6_sip-13.6.0-cp311-cp311-win_amd64.whl" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Option 3: Workaround - Skip PyQt6-sip" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Gray
Write-Host ""
Write-Host "If PyQt6-sip is causing issues, you can try:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Install PyQt6 without sip:" -ForegroundColor Gray
Write-Host "   pip install PyQt6 PyQt6-Qt6 --no-deps" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Or use an older version that has pre-compiled wheels:" -ForegroundColor Gray
Write-Host "   pip install PyQt6==6.4.2" -ForegroundColor Cyan
Write-Host ""

# Check for existing Visual Studio installations
Write-Host "Checking for existing Visual Studio installations..." -ForegroundColor Yellow
$vsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (Test-Path $vsWhere) {
    Write-Host "Visual Studio installations found:" -ForegroundColor Green
    & $vsWhere -all -products * -property displayName
} else {
    Write-Host "No Visual Studio installations found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host " Quick Fix for CI/CD" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "For immediate CI/CD fix, run:" -ForegroundColor Yellow
Write-Host ""
Write-Host "pip install PyQt6==6.5.3 PyQt6-Qt6==6.5.3 --only-binary :all:" -ForegroundColor Cyan
Write-Host "pip install PyQt6-sip --prefer-binary" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will try to use only pre-compiled wheels" -ForegroundColor Gray