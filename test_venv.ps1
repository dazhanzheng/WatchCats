# Test script to diagnose venv issue

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " Python Virtual Environment Test" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Test 1: Python version and location
Write-Host "`n1. Python Information:" -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCmd) {
    Write-Host "Python found at: $($pythonCmd.Source)" -ForegroundColor Green
    & python --version
    
    # Check if it's a Windows Store Python
    if ($pythonCmd.Source -like "*WindowsApps*") {
        Write-Host "WARNING: This is Windows Store Python!" -ForegroundColor Red
        Write-Host "Windows Store Python often has issues with venv" -ForegroundColor Red
    }
} else {
    Write-Host "Python not found!" -ForegroundColor Red
}

# Test 2: Check Python's venv module
Write-Host "`n2. Testing venv module:" -ForegroundColor Yellow
python -c "import venv; print('venv module is available')" 2>&1

# Test 3: Check ensurepip module
Write-Host "`n3. Testing ensurepip module:" -ForegroundColor Yellow
python -c "import ensurepip; print('ensurepip is available')" 2>&1

# Test 4: Try creating venv with explicit options
Write-Host "`n4. Creating venv with different options:" -ForegroundColor Yellow

# Clean up first
if (Test-Path "test_venv") {
    Remove-Item -Path "test_venv" -Recurse -Force
}

# Method A: Standard
Write-Host "  Method A: python -m venv test_venv" -ForegroundColor Cyan
python -m venv test_venv 2>&1
Start-Sleep -Seconds 2

if (Test-Path "test_venv\Scripts\python.exe") {
    Write-Host "  ✓ Success!" -ForegroundColor Green
    Remove-Item -Path "test_venv" -Recurse -Force
} else {
    Write-Host "  ✗ Failed" -ForegroundColor Red
    
    # Method B: Without pip
    Write-Host "`n  Method B: python -m venv --without-pip test_venv" -ForegroundColor Cyan
    python -m venv --without-pip test_venv 2>&1
    Start-Sleep -Seconds 2
    
    if (Test-Path "test_venv\Scripts\python.exe") {
        Write-Host "  ✓ Success (but without pip)" -ForegroundColor Yellow
        Write-Host "  This means ensurepip might be the issue" -ForegroundColor Yellow
        
        # Try to install pip manually
        Write-Host "  Attempting to install pip manually..." -ForegroundColor Cyan
        $getPipUrl = "https://bootstrap.pypa.io/get-pip.py"
        Invoke-WebRequest -Uri $getPipUrl -OutFile "get-pip.py"
        & "test_venv\Scripts\python.exe" get-pip.py 2>&1
        
        if (Test-Path "test_venv\Scripts\pip.exe") {
            Write-Host "  ✓ Pip installed manually!" -ForegroundColor Green
        }
        
        Remove-Item -Path "test_venv" -Recurse -Force
        Remove-Item -Path "get-pip.py" -Force
    } else {
        Write-Host "  ✗ Failed even without pip" -ForegroundColor Red
    }
}

# Test 5: Try with system site packages
Write-Host "`n5. Testing with system-site-packages:" -ForegroundColor Yellow
Write-Host "  python -m venv --system-site-packages test_venv" -ForegroundColor Cyan
python -m venv --system-site-packages test_venv 2>&1
Start-Sleep -Seconds 2

if (Test-Path "test_venv\Scripts\python.exe") {
    Write-Host "  ✓ Success with system packages!" -ForegroundColor Green
    Remove-Item -Path "test_venv" -Recurse -Force
} else {
    Write-Host "  ✗ Failed" -ForegroundColor Red
}

# Test 6: Check for Python installation issues
Write-Host "`n6. Checking Python installation:" -ForegroundColor Yellow

# Check if Python is complete
$pythonDir = Split-Path (Get-Command python).Source
$venvModule = Join-Path $pythonDir "Lib\venv"
$ensurepipModule = Join-Path $pythonDir "Lib\ensurepip"

Write-Host "  Python directory: $pythonDir" -ForegroundColor Cyan
Write-Host "  venv module exists: $(Test-Path $venvModule)" -ForegroundColor Cyan
Write-Host "  ensurepip exists: $(Test-Path $ensurepipModule)" -ForegroundColor Cyan

if (Test-Path $venvModule) {
    $venvFiles = Get-ChildItem $venvModule -Recurse | Measure-Object
    Write-Host "  venv module files: $($venvFiles.Count)" -ForegroundColor Cyan
}

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host " Test Complete" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan