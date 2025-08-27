# Debug script for virtual environment creation issues

Write-Host "====================================" -ForegroundColor Cyan
Write-Host " Virtual Environment Debug Script" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python installations
Write-Host "1. Checking Python installations..." -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Gray

$pythonCommands = @("python", "python3", "py")
foreach ($cmd in $pythonCommands) {
    $python = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($python) {
        Write-Host "Found $cmd at: $($python.Source)" -ForegroundColor Green
        try {
            $version = & $python.Source --version 2>&1
            Write-Host "  Version: $version" -ForegroundColor Cyan
        } catch {
            Write-Host "  Could not get version" -ForegroundColor Red
        }
    } else {
        Write-Host "$cmd not found" -ForegroundColor Gray
    }
}

# 2. Check current directory
Write-Host ""
Write-Host "2. Current directory information..." -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Gray
Write-Host "Path: $pwd" -ForegroundColor Cyan
Write-Host "Contents:" -ForegroundColor Cyan
Get-ChildItem | Select-Object Name, Mode, Length | Format-Table -AutoSize

# 3. Clean up any existing venv
Write-Host ""
Write-Host "3. Cleaning up existing venv..." -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Gray

if (Test-Path "venv") {
    Write-Host "Found existing venv directory, removing..." -ForegroundColor Yellow
    try {
        Remove-Item -Path "venv" -Recurse -Force -ErrorAction Stop
        Write-Host "Removed successfully" -ForegroundColor Green
    } catch {
        Write-Host "Failed to remove: $_" -ForegroundColor Red
        # Try alternative removal
        cmd /c "rmdir /s /q venv" 2>$null
    }
    Start-Sleep -Seconds 2
}

# 4. Try different methods to create venv
Write-Host ""
Write-Host "4. Attempting to create virtual environment..." -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Gray

# Method 1: Direct python command
Write-Host "Method 1: Using 'python -m venv venv'" -ForegroundColor Cyan
try {
    $output = python -m venv venv 2>&1
    if ($output) {
        Write-Host "Output: $output" -ForegroundColor Gray
    }
    
    # Check if it worked
    if (Test-Path "venv\Scripts\python.exe") {
        Write-Host "✓ Success with Method 1!" -ForegroundColor Green
    } else {
        throw "venv\Scripts\python.exe not found"
    }
} catch {
    Write-Host "✗ Method 1 failed: $_" -ForegroundColor Red
    
    # Clean up failed attempt
    if (Test-Path "venv") {
        Remove-Item -Path "venv" -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    # Method 2: Using py launcher
    Write-Host ""
    Write-Host "Method 2: Using 'py -m venv venv'" -ForegroundColor Cyan
    try {
        $pyCmd = Get-Command py -ErrorAction SilentlyContinue
        if ($pyCmd) {
            $output = py -m venv venv 2>&1
            if ($output) {
                Write-Host "Output: $output" -ForegroundColor Gray
            }
            
            if (Test-Path "venv\Scripts\python.exe") {
                Write-Host "✓ Success with Method 2!" -ForegroundColor Green
            } else {
                throw "venv\Scripts\python.exe not found"
            }
        } else {
            Write-Host "py command not available" -ForegroundColor Gray
        }
    } catch {
        Write-Host "✗ Method 2 failed: $_" -ForegroundColor Red
        
        # Clean up failed attempt
        if (Test-Path "venv") {
            Remove-Item -Path "venv" -Recurse -Force -ErrorAction SilentlyContinue
        }
        
        # Method 3: Using full path to python
        Write-Host ""
        Write-Host "Method 3: Using full path to python.exe" -ForegroundColor Cyan
        try {
            $pythonPath = (Get-Command python -ErrorAction Stop).Source
            Write-Host "Python path: $pythonPath" -ForegroundColor Gray
            
            $process = Start-Process -FilePath $pythonPath -ArgumentList "-m", "venv", "venv" -NoNewWindow -PassThru -Wait
            
            if ($process.ExitCode -eq 0) {
                if (Test-Path "venv\Scripts\python.exe") {
                    Write-Host "✓ Success with Method 3!" -ForegroundColor Green
                } else {
                    throw "venv\Scripts\python.exe not found after successful process"
                }
            } else {
                throw "Process exited with code $($process.ExitCode)"
            }
        } catch {
            Write-Host "✗ Method 3 failed: $_" -ForegroundColor Red
        }
    }
}

# 5. Check venv structure
Write-Host ""
Write-Host "5. Checking virtual environment structure..." -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Gray

if (Test-Path "venv") {
    Write-Host "venv directory exists" -ForegroundColor Green
    
    $venvStructure = @(
        "venv\Scripts",
        "venv\Scripts\python.exe",
        "venv\Scripts\pip.exe",
        "venv\Scripts\activate.bat",
        "venv\Scripts\Activate.ps1",
        "venv\Lib",
        "venv\Include"
    )
    
    foreach ($path in $venvStructure) {
        if (Test-Path $path) {
            Write-Host "  ✓ $path" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $path (missing)" -ForegroundColor Red
        }
    }
    
    # Try to run venv python
    Write-Host ""
    Write-Host "Testing venv Python..." -ForegroundColor Cyan
    if (Test-Path "venv\Scripts\python.exe") {
        try {
            $venvVersion = & "venv\Scripts\python.exe" --version 2>&1
            Write-Host "  Version: $venvVersion" -ForegroundColor Green
            
            # Test pip
            $pipVersion = & "venv\Scripts\python.exe" -m pip --version 2>&1
            Write-Host "  Pip: $pipVersion" -ForegroundColor Green
        } catch {
            Write-Host "  Failed to execute: $_" -ForegroundColor Red
        }
    }
} else {
    Write-Host "venv directory does not exist!" -ForegroundColor Red
}

# 6. System information
Write-Host ""
Write-Host "6. System information..." -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Gray
Write-Host "Computer: $env:COMPUTERNAME" -ForegroundColor Cyan
Write-Host "User: $env:USERNAME" -ForegroundColor Cyan
Write-Host "OS: $([System.Environment]::OSVersion.VersionString)" -ForegroundColor Cyan
Write-Host "PowerShell: $($PSVersionTable.PSVersion)" -ForegroundColor Cyan

# 7. Python module check
Write-Host ""
Write-Host "7. Checking Python venv module..." -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Gray

try {
    $modules = python -c "import sys; print('\n'.join(sys.builtin_module_names))" 2>&1
    if ($modules -like "*venv*") {
        Write-Host "venv module is available" -ForegroundColor Green
    } else {
        Write-Host "venv module might not be built-in" -ForegroundColor Yellow
    }
    
    # Check if venv can be imported
    $importTest = python -c "import venv; print('venv module imported successfully')" 2>&1
    Write-Host $importTest -ForegroundColor Cyan
} catch {
    Write-Host "Could not check Python modules: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host " Debug script completed" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan