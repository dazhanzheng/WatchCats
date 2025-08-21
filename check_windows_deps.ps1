# Windows 依赖检查和安装脚本
# 检查并安装 Watch Cats 所需的运行时依赖

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Watch Cats 依赖检查工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# 检查 Visual C++ Redistributable
function Check-VCRedist {
    Write-Host "检查 Visual C++ Redistributable..." -ForegroundColor Yellow
    
    $vcKeys = @(
        "HKLM:\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64",
        "HKLM:\SOFTWARE\WOW6432Node\Microsoft\VisualStudio\14.0\VC\Runtimes\x64",
        "HKLM:\SOFTWARE\Classes\Installer\Dependencies\Microsoft.VS.VC_RuntimeMinimumVSU_amd64,v14"
    )
    
    $vcInstalled = $false
    foreach ($key in $vcKeys) {
        if (Test-Path $key) {
            try {
                $version = Get-ItemProperty -Path $key -Name "Version" -ErrorAction SilentlyContinue
                if ($version) {
                    Write-Host "  ✓ 找到 VC++ Redistributable: $($version.Version)" -ForegroundColor Green
                    $vcInstalled = $true
                    break
                }
            } catch {
                continue
            }
        }
    }
    
    if (-not $vcInstalled) {
        # 检查通过 DLL 文件
        $systemPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::System)
        $vcDlls = @("vcruntime140.dll", "vcruntime140_1.dll", "msvcp140.dll")
        $dllsFound = $true
        
        foreach ($dll in $vcDlls) {
            $dllPath = Join-Path $systemPath $dll
            if (-not (Test-Path $dllPath)) {
                $dllsFound = $false
                break
            }
        }
        
        if ($dllsFound) {
            Write-Host "  ✓ 找到 VC++ 运行时 DLL 文件" -ForegroundColor Green
            $vcInstalled = $true
        }
    }
    
    return $vcInstalled
}

# 安装 Visual C++ Redistributable
function Install-VCRedist {
    Write-Host ""
    Write-Host "需要安装 Visual C++ Redistributable 2015-2022" -ForegroundColor Red
    Write-Host "这是运行 Watch Cats 所必需的组件" -ForegroundColor Yellow
    Write-Host ""
    
    $downloadUrl = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
    $installerPath = "$env:TEMP\vc_redist.x64.exe"
    
    $response = Read-Host "是否自动下载并安装? (Y/N)"
    if ($response -eq 'Y' -or $response -eq 'y') {
        try {
            Write-Host "正在下载..." -ForegroundColor Yellow
            Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing
            
            Write-Host "正在安装..." -ForegroundColor Yellow
            Start-Process -FilePath $installerPath -ArgumentList "/quiet", "/norestart" -Wait
            
            Write-Host "  ✓ 安装完成" -ForegroundColor Green
            Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
            return $true
        } catch {
            Write-Host "  ✗ 自动安装失败: $_" -ForegroundColor Red
            Write-Host ""
            Write-Host "请手动下载并安装:" -ForegroundColor Yellow
            Write-Host $downloadUrl -ForegroundColor Cyan
            return $false
        }
    } else {
        Write-Host ""
        Write-Host "请手动下载并安装 Visual C++ Redistributable:" -ForegroundColor Yellow
        Write-Host $downloadUrl -ForegroundColor Cyan
        return $false
    }
}

# 检查 .NET Framework
function Check-DotNet {
    Write-Host "检查 .NET Framework..." -ForegroundColor Yellow
    
    try {
        $dotNetVersion = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full" -Name Release -ErrorAction Stop
        $release = $dotNetVersion.Release
        
        $version = switch ($release) {
            { $_ -ge 533320 } { "4.8.1" }
            { $_ -ge 528040 } { "4.8" }
            { $_ -ge 461808 } { "4.7.2" }
            { $_ -ge 461308 } { "4.7.1" }
            { $_ -ge 460798 } { "4.7" }
            { $_ -ge 394802 } { "4.6.2" }
            { $_ -ge 394254 } { "4.6.1" }
            { $_ -ge 393295 } { "4.6" }
            { $_ -ge 379893 } { "4.5.2" }
            { $_ -ge 378675 } { "4.5.1" }
            { $_ -ge 378389 } { "4.5" }
            default { "Unknown" }
        }
        
        Write-Host "  ✓ .NET Framework $version" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "  ⚠ .NET Framework 4.5+ 未找到（通常不影响运行）" -ForegroundColor Yellow
        return $true  # 不是关键依赖
    }
}

# 检查 DirectX
function Check-DirectX {
    Write-Host "检查 DirectX..." -ForegroundColor Yellow
    
    try {
        $dxdiag = Get-WmiObject Win32_VideoController | Select-Object -First 1
        if ($dxdiag) {
            Write-Host "  ✓ 显卡驱动正常: $($dxdiag.Name)" -ForegroundColor Green
            
            # 检查 d3dcompiler_47.dll
            $systemPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::System)
            $d3dPath = Join-Path $systemPath "d3dcompiler_47.dll"
            if (Test-Path $d3dPath) {
                Write-Host "  ✓ DirectX 编译器存在" -ForegroundColor Green
            } else {
                Write-Host "  ⚠ d3dcompiler_47.dll 未找到，可能影响图形渲染" -ForegroundColor Yellow
            }
            return $true
        }
    } catch {
        Write-Host "  ⚠ 无法检查 DirectX 状态" -ForegroundColor Yellow
    }
    return $true
}

# 检查 Windows 版本
function Check-WindowsVersion {
    Write-Host "检查 Windows 版本..." -ForegroundColor Yellow
    
    $os = Get-WmiObject -Class Win32_OperatingSystem
    $version = $os.Version
    $caption = $os.Caption
    
    Write-Host "  ✓ $caption" -ForegroundColor Green
    Write-Host "    版本: $version" -ForegroundColor Gray
    
    # 检查是否是 Windows 10 或更高版本
    $versionParts = $version.Split('.')
    $major = [int]$versionParts[0]
    
    if ($major -lt 10) {
        Write-Host "  ⚠ 建议使用 Windows 10 或更高版本以获得最佳体验" -ForegroundColor Yellow
    }
    
    return $true
}

# 生成诊断报告
function Generate-DiagnosticReport {
    param([string]$outputPath = "watchcats_diagnostic.txt")
    
    Write-Host ""
    Write-Host "生成诊断报告..." -ForegroundColor Yellow
    
    $report = @"
Watch Cats 诊断报告
生成时间: $(Get-Date)
========================================

系统信息:
$([System.Environment]::OSVersion)
处理器架构: $([System.Environment]::GetEnvironmentVariable("PROCESSOR_ARCHITECTURE"))

环境变量:
QT_PLUGIN_PATH: $([System.Environment]::GetEnvironmentVariable("QT_PLUGIN_PATH"))
QT_QPA_PLATFORM_PLUGIN_PATH: $([System.Environment]::GetEnvironmentVariable("QT_QPA_PLATFORM_PLUGIN_PATH"))
PATH (前100字符): $([System.Environment]::GetEnvironmentVariable("PATH").Substring(0, [Math]::Min(100, [System.Environment]::GetEnvironmentVariable("PATH").Length)))...

已安装的程序（相关）:
"@
    
    # 检查已安装的相关程序
    $programs = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | 
        Where-Object { $_.DisplayName -match "Visual C\+\+|\.NET|Python|Qt" } |
        Select-Object DisplayName, DisplayVersion
    
    foreach ($prog in $programs) {
        $report += "`n$($prog.DisplayName) - $($prog.DisplayVersion)"
    }
    
    $report | Out-File -FilePath $outputPath -Encoding UTF8
    Write-Host "  ✓ 报告已保存到: $outputPath" -ForegroundColor Green
}

# 主函数
function Main {
    $allChecks = $true
    
    # 系统检查
    Check-WindowsVersion | Out-Null
    Write-Host ""
    
    # 依赖检查
    $vcInstalled = Check-VCRedist
    if (-not $vcInstalled) {
        $allChecks = $false
        if (Test-Administrator) {
            Install-VCRedist | Out-Null
        } else {
            Write-Host ""
            Write-Host "提示: 以管理员身份运行此脚本可自动安装缺失的组件" -ForegroundColor Yellow
        }
    }
    Write-Host ""
    
    Check-DotNet | Out-Null
    Write-Host ""
    
    Check-DirectX | Out-Null
    Write-Host ""
    
    # 总结
    Write-Host "========================================" -ForegroundColor Cyan
    if ($allChecks) {
        Write-Host "✓ 所有关键依赖都已安装" -ForegroundColor Green
        Write-Host "Watch Cats 应该可以正常运行" -ForegroundColor Green
    } else {
        Write-Host "⚠ 发现缺失的依赖" -ForegroundColor Yellow
        Write-Host "请安装缺失的组件后再试" -ForegroundColor Yellow
    }
    Write-Host "========================================" -ForegroundColor Cyan
    
    # 询问是否生成诊断报告
    Write-Host ""
    $response = Read-Host "是否生成详细诊断报告? (Y/N)"
    if ($response -eq 'Y' -or $response -eq 'y') {
        Generate-DiagnosticReport
    }
    
    Write-Host ""
    Write-Host "按任意键退出..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# 运行主函数
Main