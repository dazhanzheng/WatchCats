; Inno Setup Script for WatchCats
; Creates a Windows installer with runtime dependency checks

#define MyAppName "WatchCats"
#define MyAppNameEN "WatchCats"
#define MyAppVersion "0.1.3"
#define MyAppPublisher "WatchCats Project"
#define MyAppURL "https://github.com/dazhanzheng/WatchCats"
#define MyAppExeName "WatchCats.exe"

[Setup]
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
; SetupIconFile is optional - comment out if icon doesn't exist
; SetupIconFile=installer\icons\WatchCats.ico
AppMutex={#MyAppNameEN}Mutex
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\{#MyAppExeName}
ShowLanguageDialog=yes
LanguageDetectionMethod=uilanguage
DisableWelcomePage=no
DisableDirPage=no
DisableReadyPage=no
DisableFinishedPage=no
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} 安装程序
VersionInfoTextVersion={#MyAppVersion}
VersionInfoCopyright=Copyright (C) 2025 {#MyAppPublisher}
MinVersion=10.0.17763
LicenseFile=LICENSE.txt

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
; Chinese language file is optional - only use if available
; Name: "chinese"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[CustomMessages]
; Default English messages
LaunchProgram=Launch {#MyAppName}
CreateDesktopIcon=Create a &desktop shortcut
InstallVCRedist=Installing Visual C++ Runtime...
CheckingDependencies=Checking system dependencies...
ConfiguringApp=Configuring application...
StartupIcon=Start automatically at Windows startup
StartupIconDesc=Configure {#MyAppName} to start automatically

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startupicon"; Description: "{cm:StartupIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; 主程序
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; 图标文件 (如果存在)
Source: "installer\icons\WatchCats.ico"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "baal\resources\icon.ico"; DestDir: "{app}"; DestName: "WatchCats.ico"; Flags: ignoreversion skipifsourcedoesntexist

; PyInstaller 生成的内部文件
Source: "dist\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

; 资源文件
Source: "baal\resources\*"; DestDir: "{app}\baal\resources"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist
Source: "动作表情拆分\*"; DestDir: "{app}\动作表情拆分"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist
Source: "baal\references\*"; DestDir: "{app}\baal\references"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

[Dirs]
; 创建用户数据目录
Name: "{localappdata}\{#MyAppNameEN}"
Name: "{localappdata}\{#MyAppNameEN}\logs"
Name: "{localappdata}\{#MyAppNameEN}\data"

[Icons]
; Start menu shortcuts
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\WatchCats.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop shortcut
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\WatchCats.ico"; IconIndex: 0

[Registry]
; 开机自启动
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppNameEN}"; ValueData: """{app}\{#MyAppExeName}"""; Tasks: startupicon; Flags: uninsdeletevalue

; 应用设置
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppNameEN}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppNameEN}"; ValueType: string; ValueName: "ConfigPath"; ValueData: "{localappdata}\{#MyAppNameEN}"
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppNameEN}"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"

[Run]
; 安装后运行
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram}"; Flags: nowait postinstall skipifsilent

[Code]
// 初始化设置
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

// 安装步骤变化时的操作
procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigPath: String;
  QtConfPath: String;
  QtConfContent: String;
begin
  if CurStep = ssPostInstall then
  begin
    // 创建 qt.conf 文件（解决 Qt 插件路径问题）
    QtConfPath := ExpandConstant('{app}\qt.conf');
    QtConfContent := '[Paths]' + #13#10 +
                     'Prefix = _internal/PyQt6/Qt6' + #13#10 +
                     'Plugins = _internal/PyQt6/Qt6/plugins' + #13#10;
    SaveStringToFile(QtConfPath, QtConfContent, False);
    
    // 创建默认配置文件（如果不存在）
    ConfigPath := ExpandConstant('{localappdata}\{#MyAppNameEN}\config.json');
    if not FileExists(ConfigPath) then
    begin
      ForceDirectories(ExtractFilePath(ConfigPath));
      SaveStringToFile(ConfigPath, '{' + #13#10 +
                                  '  "version": "' + '{#MyAppVersion}' + '",' + #13#10 +
                                  '  "first_run": true,' + #13#10 +
                                  '  "language": "zh_CN",' + #13#10 +
                                  '  "api_key": "6be4b0c1-8e71-4530-908a-cbe4b48a9a07",' + #13#10 +
                                  '  "base_url": "https://ark.cn-beijing.volces.com/api/v3",' + #13#10 +
                                  '  "model": "doubao-seed-1-6-flash-250715"' + #13#10 +
                                  '}', False);
    end;
  end;
end;

// 数据迁移函数
procedure MigrateOldData();
var
  OldConfigPath: String;
  NewConfigPath: String;
  ResultCode: Integer;
begin
  // 定义旧版本路径 (BaalPet in Roaming)
  OldConfigPath := ExpandConstant('{userappdata}\BaalPet');
  // 定义新版本路径 (WatchCats in Local)  
  NewConfigPath := ExpandConstant('{localappdata}\WatchCats');
  
  // 检查旧版本目录是否存在
  if not DirExists(OldConfigPath) then
  begin
    Exit;
  end;
  
  // 确保新目录存在
  if not ForceDirectories(NewConfigPath) then
  begin
    Exit;
  end;
  
  // 迁移文件
  if FileExists(OldConfigPath + '\config.json') and not FileExists(NewConfigPath + '\config.json') then
  begin
    FileCopy(OldConfigPath + '\config.json', NewConfigPath + '\config.json', False);
  end;
  
  if FileExists(OldConfigPath + '\chat_history.json') and not FileExists(NewConfigPath + '\conversation_history.json') then
  begin
    FileCopy(OldConfigPath + '\chat_history.json', NewConfigPath + '\conversation_history.json', False);
  end;
  
  if FileExists(OldConfigPath + '\conversation_history.json') and not FileExists(NewConfigPath + '\conversation_history.json') then
  begin
    FileCopy(OldConfigPath + '\conversation_history.json', NewConfigPath + '\conversation_history.json', False);
  end;
  
  if FileExists(OldConfigPath + '\schedules.json') and not FileExists(NewConfigPath + '\schedules.json') then
  begin
    FileCopy(OldConfigPath + '\schedules.json', NewConfigPath + '\schedules.json', False);
  end;
  
  if FileExists(OldConfigPath + '\goals.json') and not FileExists(NewConfigPath + '\supervision.json') then
  begin
    FileCopy(OldConfigPath + '\goals.json', NewConfigPath + '\supervision.json', False);
  end;
  
  if FileExists(OldConfigPath + '\supervision.json') and not FileExists(NewConfigPath + '\supervision.json') then
  begin
    FileCopy(OldConfigPath + '\supervision.json', NewConfigPath + '\supervision.json', False);
  end;
end;

// 安装前的准备
function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  NeedsRestart := False;
  Result := '';
  
  // 执行数据迁移
  MigrateOldData();
end;