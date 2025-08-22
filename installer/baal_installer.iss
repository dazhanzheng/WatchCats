; Inno Setup Script for WatchCats
; Creates a traditional Windows installer with runtime dependency checks
; 创建传统的Windows安装程序，自动安装运行时依赖

#define MyAppName "WatchCats"
#define MyAppNameEN "WatchCats"
#define MyAppVersion "0.1.3"
#define MyAppPublisher "WatchCats Project"
#define MyAppURL "https://github.com/dazhanzheng/WatchCats"
#define MyAppExeName "WatchCats.exe"
#define MyAppAssocExt ".watchcats"
#define MyAppAssocName "WatchCatsFile"

[Setup]
; 应用信息
AppId={{E7B2A9F1-3C4D-5E6F-8A9B-1C2D3E4F5A6B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppNameEN}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=WatchCats-Setup
SetupIconFile=..\baal\resources\cat.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\{#MyAppExeName}

; 界面设置
ShowLanguageDialog=auto
LanguageDetectionMethod=uilanguage
; Wizard images (generated during build)
WizardImageFile=installer_wizard.bmp
WizardSmallImageFile=installer_small.bmp
DisableWelcomePage=no
DisableDirPage=no
DisableReadyPage=no
DisableFinishedPage=no

; 版本信息
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} 安装程序
VersionInfoTextVersion={#MyAppVersion}
VersionInfoCopyright=Copyright (C) 2025 {#MyAppPublisher}

; Windows版本要求
MinVersion=10.0.17763

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
; English messages
english.LaunchProgram=Launch {#MyAppName}
english.CreateDesktopIcon=Create a &desktop shortcut
english.CreateQuickLaunchIcon=Create a &Quick Launch shortcut
english.InstallVCRedist=Installing Visual C++ Runtime...
english.CheckingDependencies=Checking system dependencies...
english.ConfiguringApp=Configuring application...

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsWindows64
Name: "startupicon"; Description: "Start automatically at Windows startup"; GroupDescription: "Additional options:"; Flags: unchecked

[Files]
; 主程序
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; PyInstaller 生成的内部文件（可能在 _internal 或直接在 dist 目录）
; 使用 skipifsourcedoesntexist 标志使其成为可选项
Source: "..\dist\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist
Source: "..\dist\*.dll"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "..\dist\*.pyd"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; Qt 平台插件（从多个可能的位置尝试）
Source: "..\dist\_internal\PyQt6\Qt6\plugins\platforms\*"; DestDir: "{app}\_internal\PyQt6\Qt6\plugins\platforms"; Flags: ignoreversion recursesubdirs skipifsourcedoesntexist
Source: "..\dist\PyQt6\Qt6\plugins\platforms\*"; DestDir: "{app}\PyQt6\Qt6\plugins\platforms"; Flags: ignoreversion recursesubdirs skipifsourcedoesntexist
Source: "..\dist\_internal\PyQt6\Qt6\plugins\imageformats\*"; DestDir: "{app}\_internal\PyQt6\Qt6\plugins\imageformats"; Flags: ignoreversion recursesubdirs skipifsourcedoesntexist
Source: "..\dist\PyQt6\Qt6\plugins\imageformats\*"; DestDir: "{app}\PyQt6\Qt6\plugins\imageformats"; Flags: ignoreversion recursesubdirs skipifsourcedoesntexist
Source: "..\dist\_internal\PyQt6\Qt6\plugins\styles\*"; DestDir: "{app}\_internal\PyQt6\Qt6\plugins\styles"; Flags: ignoreversion recursesubdirs skipifsourcedoesntexist
Source: "..\dist\PyQt6\Qt6\plugins\styles\*"; DestDir: "{app}\PyQt6\Qt6\plugins\styles"; Flags: ignoreversion recursesubdirs skipifsourcedoesntexist

; 资源文件
Source: "..\baal\resources\*"; DestDir: "{app}\baal\resources"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\动作表情拆分\*"; DestDir: "{app}\动作表情拆分"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\baal\references\*"; DestDir: "{app}\baal\references"; Flags: ignoreversion recursesubdirs createallsubdirs

; Visual C++ Redistributable installers
Source: "vcredist\vc_redist.x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: not VCRedist64Installed
Source: "vcredist\vc_redist.x86.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: not VCRedist32Installed

; 配置文件模板
Source: "config_template.json"; DestDir: "{app}"; Flags: ignoreversion; Check: FileExists(ExpandConstant('{#SourcePath}\config_template.json'))

; 用户手册（不包含 README.txt）
Source: "..\USER_MANUAL.md"; DestDir: "{app}"; DestName: "用户手册.txt"; Flags: ignoreversion; Check: FileExists(ExpandConstant('{#SourcePath}\..\USER_MANUAL.md'))

[Dirs]
; 创建用户数据目录
Name: "{userappdata}\{#MyAppNameEN}"
Name: "{userappdata}\{#MyAppNameEN}\logs"
Name: "{userappdata}\{#MyAppNameEN}\data"

[Icons]
; Start menu shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{group}\User Manual"; Filename: "{app}\README.txt"
Name: "{group}\Configuration Folder"; Filename: "{userappdata}\{#MyAppNameEN}"

; Desktop shortcut
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; Quick Launch shortcut
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

; Startup shortcut
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon; Parameters: "--minimized"

[Registry]
; 文件关联（可选）
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocName}"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocName}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocName}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocName}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: "{#MyAppAssocExt}"; ValueData: ""

; 应用设置
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppNameEN}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppNameEN}"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"

[Run]
; 安装后运行
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 删除用户数据（可选，谨慎使用）
; Type: filesandordirs; Name: "{userappdata}\{#MyAppNameEN}"

[Code]
// 检查 Visual C++ Redistributable 是否已安装
function VCRedist64Installed(): Boolean;
begin
  Result := RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64') or
            RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Classes\Installer\Dependencies\VC,redist.x64,amd64,14.40,bundle');
end;

function VCRedist32Installed(): Boolean;
begin
  Result := RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x86') or
            RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Classes\Installer\Dependencies\VC,redist.x86,x86,14.40,bundle');
end;

// 检查目录是否存在
function DirExists(const DirName: String): Boolean;
begin
  Result := DirectoryExists(DirName);
end;

// 检查文件是否存在
function FileExists(const FileName: String): Boolean;
begin
  Result := FileExists(FileName);
end;

// 初始化设置
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
  Message: String;
begin
  Result := True;
  
  // 检查是否已安装旧版本
  if RegKeyExists(HKEY_CURRENT_USER, 'Software\{#MyAppPublisher}\{#MyAppNameEN}') then
  begin
    Message := 'Previous version detected. Continue with installation?';
      
    if MsgBox(Message, mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
      Exit;
    end;
  end;
  
  // 检查 Visual C++ Redistributable
  if not VCRedist64Installed() then
  begin
    Message := 'Visual C++ Redistributable not detected.' + #13#10 + 'The installer will install the required runtime.';
      
    MsgBox(Message, mbInformation, MB_OK);
  end;
end;

// 安装运行库
procedure InstallVCRedist();
var
  ResultCode: Integer;
  StatusText: String;
begin
  StatusText := CustomMessage('InstallVCRedist');
    
  WizardForm.StatusLabel.Caption := StatusText;
  WizardForm.ProgressGauge.Style := npbstMarquee;
  
  // 安装 64 位运行库
  if not VCRedist64Installed() and FileExists(ExpandConstant('{tmp}\vc_redist.x64.exe')) then
  begin
    Exec(ExpandConstant('{tmp}\vc_redist.x64.exe'), '/quiet /norestart', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
  
  // 安装 32 位运行库（某些依赖可能需要）
  if not VCRedist32Installed() and FileExists(ExpandConstant('{tmp}\vc_redist.x86.exe')) then
  begin
    Exec(ExpandConstant('{tmp}\vc_redist.x86.exe'), '/quiet /norestart', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
  
  WizardForm.ProgressGauge.Style := npbstNormal;
end;

// Uninstall confirmation
function InitializeUninstall(): Boolean;
begin
  Result := MsgBox('Are you sure you want to uninstall {#MyAppName}?' + #13#10 + 
                   'Note: User data and settings will be preserved.', 
                   mbConfirmation, MB_YESNO) = IDYES;
end;

// 安装步骤变化时的操作
procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigPath: String;
  QtConfPath: String;
  QtConfContent: String;
  StatusText: String;
begin
  if CurStep = ssInstall then
  begin
    // 在文件复制前安装运行库
    InstallVCRedist();
  end
  else if CurStep = ssPostInstall then
  begin
    // 配置应用程序
    StatusText := CustomMessage('ConfiguringApp');
    WizardForm.StatusLabel.Caption := StatusText;
    
    // 创建 qt.conf 文件（解决 Qt 插件路径问题）
    QtConfPath := ExpandConstant('{app}\qt.conf');
    QtConfContent := '[Paths]' + #13#10 +
                     'Prefix = _internal/PyQt6/Qt6' + #13#10 +
                     'Plugins = _internal/PyQt6/Qt6/plugins' + #13#10 +
                     'Libraries = _internal/PyQt6/Qt6/lib' + #13#10;
    SaveStringToFile(QtConfPath, QtConfContent, False);
    
    // 创建默认配置文件（如果不存在）
    ConfigPath := ExpandConstant('{userappdata}\{#MyAppNameEN}\config.json');
    if not FileExists(ConfigPath) then
    begin
      ForceDirectories(ExtractFilePath(ConfigPath));
      SaveStringToFile(ConfigPath, '{' + #13#10 +
                                  '  "version": "' + '{#MyAppVersion}' + '",' + #13#10 +
                                  '  "first_run": true,' + #13#10 +
                                  '  "language": "zh_CN"' + #13#10 +
                                  '}', False);
    end;
    
    // 设置环境变量（Qt 插件路径）
    SetEnvironmentVariable('QT_PLUGIN_PATH', ExpandConstant('{app}\_internal\PyQt6\Qt6\plugins'));
    SetEnvironmentVariable('QT_QPA_PLATFORM_PLUGIN_PATH', ExpandConstant('{app}\_internal\PyQt6\Qt6\plugins\platforms'));
  end;
end;

// 卸载前的操作
function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  NeedsRestart := False;
  Result := '';
  
  // 检查程序是否正在运行
  if CheckForMutexes('{#MyAppNameEN}Mutex') then
  begin
    Result := 'The application is currently running. Please close it before continuing.';
  end;
end;