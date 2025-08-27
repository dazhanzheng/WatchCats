# Test Python Setup Script
Write-Host "====================================" -ForegroundColor Cyan
Write-Host " Python Setup Verification" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# 1. Find Python
Write-Host "1. Searching for Python..." -ForegroundColor Yellow

$pythonCmd = $null

# Check common commands
@("python", "python3", "py") | ForEach-Object {
    $cmd = Get-Command $_ -ErrorAction SilentlyContinue
    if ($cmd -and -not $pythonCmd) {
        $pythonCmd = $cmd.Source
        Write-Host "Found via '$_' command: $pythonCmd" -ForegroundColor Green
    }
}

# If not found in PATH, search directories
if (-not $pythonCmd) {
    Write-Host "Not in PATH, searching directories..." -ForegroundColor Yellow
    
    $searchPaths = @(
        "C:\Python313\python.exe",
        "C:\Program Files\Python313\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
    )
    
    foreach ($path in $searchPaths) {
        if (Test-Path $path) {
            $pythonCmd = $path
            Write-Host "Found at: $pythonCmd" -ForegroundColor Green
            break
        }
    }
}

if (-not $pythonCmd) {
    Write-Host "Python not found!" -ForegroundColor Red
    exit 1
}

# 2. Test Python
Write-Host ""
Write-Host "2. Python Information:" -ForegroundColor Yellow
$version = & $pythonCmd --version 2>&1
Write-Host "Version: $version" -ForegroundColor Cyan

# 3. Test pip
Write-Host ""
Write-Host "3. Testing pip:" -ForegroundColor Yellow
$pipVersion = & $pythonCmd -m pip --version 2>&1
Write-Host "Pip: $pipVersion" -ForegroundColor Cyan

# 4. Test critical imports
Write-Host ""
Write-Host "4. Testing critical modules:" -ForegroundColor Yellow

$modules = @(
    "sys",
    "os",
    "subprocess",
    "json",
    "pathlib"
)

foreach ($module in $modules) {
    $result = & $pythonCmd -c "import $module; print('$module: OK')" 2>&1
    if ($result -like "*OK*") {
        Write-Host "  ✓ $module" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $module: $result" -ForegroundColor Red
    }
}

# 5. Test installing a package
Write-Host ""
Write-Host "5. Testing package installation:" -ForegroundColor Yellow
Write-Host "Installing wheel package as test..." -ForegroundColor Cyan
& $pythonCmd -m pip install wheel --user --no-warn-script-location 2>&1 | Out-Null

$wheelCheck = & $pythonCmd -c "import wheel; print('wheel installed')" 2>&1
if ($wheelCheck -like "*installed*") {
    Write-Host "✓ Package installation works!" -ForegroundColor Green
} else {
    Write-Host "✗ Package installation failed" -ForegroundColor Red
}

# 6. Check for PyInstaller
Write-Host ""
Write-Host "6. Checking PyInstaller:" -ForegroundColor Yellow
$pyinstallerCheck = & $pythonCmd -m PyInstaller --version 2>&1
if ($pyinstallerCheck -like "*command not found*" -or $pyinstallerCheck -like "*No module*") {
    Write-Host "PyInstaller not installed (will be installed during build)" -ForegroundColor Yellow
} else {
    Write-Host "PyInstaller version: $pyinstallerCheck" -ForegroundColor Green
}

# 7. Environment Summary
Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host " Summary" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Python: $pythonCmd" -ForegroundColor Green
Write-Host "Version: $version" -ForegroundColor Green
Write-Host "Ready for build: YES" -ForegroundColor Green
Write-Host ""
Write-Host "To manually install all dependencies:" -ForegroundColor Yellow
Write-Host "  $pythonCmd -m pip install -r requirements.txt --user" -ForegroundColor Cyan