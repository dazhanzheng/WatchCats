# Windows 本地构建测试脚本
# 用于在 DNF-DELLWORKSTA 或其他 Windows 机器上测试构建流程

param(
    [string]$BuildType = "exe",  # exe, installer, or both
    [switch]$SkipClean,
    [switch]$SkipTests,
    [switch]$KeepVenv
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Baal Desktop Pet - Windows Build Test" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Build Type: $BuildType" -ForegroundColor Yellow
Write-Host "Machine: $env:COMPUTERNAME" -ForegroundColor Yellow
Write-Host "User: $env:USERNAME" -ForegroundColor Yellow
Write-Host "Time: $(Get-Date)" -ForegroundColor Yellow
Write-Host ""

# 检查 Python
Write-Host "Checking Python installation..." -ForegroundColor Green
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Error "Python not found! Please install Python 3.9 or later."
    exit 1
}

# 设置工作目录
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot
Write-Host "Working directory: $projectRoot" -ForegroundColor Green

# 清理旧文件
if (-not $SkipClean) {
    Write-Host "`nCleaning old build files..." -ForegroundColor Green
    Remove-Item -Path "build", "dist" -Recurse -Force -ErrorAction SilentlyContinue
    
    if (-not $KeepVenv -and (Test-Path "venv")) {
        Write-Host "Removing old virtual environment..." -ForegroundColor Yellow
        Remove-Item -Path "venv" -Recurse -Force
    }
}

# 创建虚拟环境
if (-not (Test-Path "venv")) {
    Write-Host "`nCreating virtual environment..." -ForegroundColor Green
    python -m venv venv
    
    if (-not $?) {
        Write-Error "Failed to create virtual environment!"
        exit 1
    }
}

# 激活虚拟环境并安装依赖
Write-Host "`nActivating virtual environment..." -ForegroundColor Green
& .\venv\Scripts\Activate.ps1

Write-Host "Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip --quiet

Write-Host "Installing dependencies..." -ForegroundColor Green
pip install -r requirements.txt --quiet

if (-not $?) {
    Write-Error "Failed to install dependencies!"
    exit 1
}

# 运行测试（可选）
if (-not $SkipTests) {
    Write-Host "`nRunning tests..." -ForegroundColor Green
    python -m pytest tests/ -v 2>$null
    
    if ($?) {
        Write-Host "Tests passed!" -ForegroundColor Green
    } else {
        Write-Warning "Some tests failed, but continuing build..."
    }
}

# 准备资源文件
Write-Host "`nPreparing build assets..." -ForegroundColor Green

# 检查图标文件
$iconPath = "baal\resources\baal.ico"
if (-not (Test-Path $iconPath)) {
    Write-Warning "Icon file not found at $iconPath"
    
    # 尝试从 PNG 创建 ICO（如果有 PNG）
    $pngPath = "baal\resources\baal.png"
    if (Test-Path $pngPath) {
        Write-Host "Attempting to create ICO from PNG..." -ForegroundColor Yellow
        # 这里可以使用 ImageMagick 或其他工具
        # magick convert $pngPath -define icon:auto-resize=256,128,96,64,48,32,16 $iconPath
    }
}

# PyInstaller 构建
if ($BuildType -eq "exe" -or $BuildType -eq "both") {
    Write-Host "`nBuilding executable with PyInstaller..." -ForegroundColor Green
    
    # 检查 spec 文件
    $specFile = if (Test-Path "baal_windows.spec") { 
        "baal_windows.spec" 
    } else { 
        "baal.spec" 
    }
    
    Write-Host "Using spec file: $specFile" -ForegroundColor Yellow
    
    # 运行 PyInstaller
    pyinstaller --clean --noconfirm $specFile
    
    if (-not $?) {
        Write-Error "PyInstaller build failed!"
        exit 1
    }
    
    # 检查输出
    $exeFiles = Get-ChildItem -Path "dist" -Filter "*.exe"
    if ($exeFiles) {
        Write-Host "`nBuild successful!" -ForegroundColor Green
        foreach ($exe in $exeFiles) {
            $sizeMB = [math]::Round($exe.Length / 1MB, 2)
            Write-Host "  - $($exe.Name) ($sizeMB MB)" -ForegroundColor Cyan
        }
    } else {
        Write-Error "No executable found in dist folder!"
        exit 1
    }
    
    # 测试运行
    Write-Host "`nTesting executable..." -ForegroundColor Green
    $testExe = $exeFiles[0].FullName
    
    try {
        # 尝试获取版本信息
        & $testExe --version 2>$null
        if ($?) {
            Write-Host "Executable test passed!" -ForegroundColor Green
        }
    } catch {
        Write-Warning "Could not test executable (this is normal for GUI apps)"
    }
}

# 创建安装程序
if ($BuildType -eq "installer" -or $BuildType -eq "both") {
    Write-Host "`nCreating installer with Inno Setup..." -ForegroundColor Green
    
    # 查找 Inno Setup
    $innoSetupPaths = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles}\Inno Setup 6\ISCC.exe",
        "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    )
    
    $iscc = $null
    foreach ($path in $innoSetupPaths) {
        if (Test-Path $path) {
            $iscc = $path
            break
        }
    }
    
    if ($iscc) {
        Write-Host "Found Inno Setup at: $iscc" -ForegroundColor Green
        
        # 检查或创建安装脚本
        $issPath = "installer\windows\baal_setup.iss"
        if (-not (Test-Path $issPath)) {
            Write-Host "Creating installer script..." -ForegroundColor Yellow
            New-Item -ItemType Directory -Force -Path "installer\windows" | Out-Null
            
            # 创建基本的 ISS 文件
            $issContent = @"
[Setup]
AppName=Baal Desktop Pet
AppVersion=1.0.0
AppPublisher=Your Name
DefaultDirName={autopf}\BaalDesktopPet
DefaultGroupName=Baal Desktop Pet
UninstallDisplayIcon={app}\BaalDesktopPet.exe
OutputDir=..\..\dist
OutputBaseFilename=BaalDesktopPetSetup
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "..\..\dist\BaalDesktopPet.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Baal Desktop Pet"; Filename: "{app}\BaalDesktopPet.exe"
Name: "{group}\{cm:UninstallProgram,Baal Desktop Pet}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Baal Desktop Pet"; Filename: "{app}\BaalDesktopPet.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Run]
Filename: "{app}\BaalDesktopPet.exe"; Description: "{cm:LaunchProgram,Baal Desktop Pet}"; Flags: nowait postinstall skipifsilent
"@
            $issContent | Out-File -FilePath $issPath -Encoding UTF8
        }
        
        # 编译安装程序
        & $iscc /Q $issPath
        
        if ($?) {
            $setupFile = Get-ChildItem -Path "dist" -Filter "*Setup.exe" | Select-Object -First 1
            if ($setupFile) {
                $sizeMB = [math]::Round($setupFile.Length / 1MB, 2)
                Write-Host "`nInstaller created successfully!" -ForegroundColor Green
                Write-Host "  - $($setupFile.Name) ($sizeMB MB)" -ForegroundColor Cyan
            }
        } else {
            Write-Warning "Failed to create installer"
        }
    } else {
        Write-Warning "Inno Setup not found. Skipping installer creation."
        Write-Host "Download from: https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
    }
}

# 创建发布包
Write-Host "`nCreating release package..." -ForegroundColor Green
$releaseDir = "release"
New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null

# 复制文件
if (Test-Path "dist\*.exe") {
    Copy-Item -Path "dist\*.exe" -Destination $releaseDir
}

# 创建 ZIP 包
$zipPath = "$releaseDir\BaalDesktopPet-Windows-$(Get-Date -Format 'yyyyMMdd').zip"
Compress-Archive -Path "dist\*" -DestinationPath $zipPath -Force

Write-Host "`nRelease package created:" -ForegroundColor Green
Write-Host "  - $zipPath" -ForegroundColor Cyan

# 完成
Write-Host "`n============================================" -ForegroundColor Green
Write-Host " Build completed successfully!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Build artifacts:" -ForegroundColor Yellow
Get-ChildItem -Path $releaseDir | ForEach-Object {
    $sizeMB = [math]::Round($_.Length / 1MB, 2)
    Write-Host "  - $($_.Name) ($sizeMB MB)"
}

Write-Host "`nTo test the application:" -ForegroundColor Cyan
Write-Host "  .\dist\BaalDesktopPet.exe" -ForegroundColor White
Write-Host ""