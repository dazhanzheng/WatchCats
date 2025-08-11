; Inno Setup 安装脚本 - Baal宠物助手
; 官网: https://jrsoftware.org/isinfo.php

#define MyAppName "Baal宠物助手"
#define MyAppNameEN "BaalPetAssistant"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "Baal Project"
#define MyAppURL "https://github.com/yourusername/baal-standalone"
#define MyAppExeName "Baal宠物助手.exe"
#define MyAppAssocName "Baal Configuration"
#define MyAppAssocExt ".baal"

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
OutputBaseFilename={#MyAppNameEN}Setup
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

; 版本信息
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} 安装程序
VersionInfoTextVersion={#MyAppVersion}
VersionInfoCopyright=Copyright (C) 2025 {#MyAppPublisher}

; Windows版本要求
MinVersion=10.0.17763

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
chinesesimplified.LaunchProgram=运行 {#MyAppName}
chinesesimplified.CreateDesktopIcon=创建桌面快捷方式(&D)
chinesesimplified.CreateQuickLaunchIcon=创建快速启动栏图标(&Q)
english.LaunchProgram=Launch {#MyAppName}
english.CreateDesktopIcon=Create a &desktop shortcut
english.CreateQuickLaunchIcon=Create a &Quick Launch shortcut

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsWindows64
Name: "startupicon"; Description: "开机自动启动"; GroupDescription: "其他选项:"; Flags: unchecked

[Files]
; 主程序
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; 资源文件（如果PyInstaller没有打包进exe）
Source: "..\baal\resources\*"; DestDir: "{app}\baal\resources"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\动作表情拆分\*"; DestDir: "{app}\动作表情拆分"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\baal\references\*"; DestDir: "{app}\baal\references"; Flags: ignoreversion recursesubdirs createallsubdirs

; 配置文件模板（可选）
Source: "config_template.json"; DestDir: "{app}"; Flags: ignoreversion; Check: FileExists(ExpandConstant('{#SourcePath}\config_template.json'))

; README文档
Source: "..\BUILD_WINDOWS.md"; DestDir: "{app}"; DestName: "README.txt"; Flags: ignoreversion

[Dirs]
; 创建用户数据目录
Name: "{userappdata}\{#MyAppNameEN}"
Name: "{userappdata}\{#MyAppNameEN}\logs"
Name: "{userappdata}\{#MyAppNameEN}\data"

[Icons]
; 开始菜单
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{group}\用户手册"; Filename: "{app}\README.txt"
Name: "{group}\配置文件夹"; Filename: "{userappdata}\{#MyAppNameEN}"

; 桌面图标
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; 快速启动栏
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

; 开机启动
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
// 检查.NET Framework或其他依赖
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  
  // 检查是否已安装
  if RegKeyExists(HKEY_CURRENT_USER, 'Software\{#MyAppPublisher}\{#MyAppNameEN}') then
  begin
    if MsgBox('检测到已安装旧版本，是否继续安装？', mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
    end;
  end;
  
  // 检查Visual C++ Redistributable（如果需要）
  if not RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64') then
  begin
    if MsgBox('未检测到 Visual C++ Redistributable 2015-2022。' + #13#10 + 
              '程序可能无法正常运行。是否继续安装？', mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
    end;
  end;
end;

// 卸载前确认
function InitializeUninstall(): Boolean;
begin
  Result := MsgBox('确定要卸载 {#MyAppName} 吗？' + #13#10 + 
                   '注意：用户数据和设置将被保留。', 
                   mbConfirmation, MB_YESNO) = IDYES;
end;

// 安装完成后的操作
procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigPath: String;
begin
  if CurStep = ssPostInstall then
  begin
    // 创建默认配置文件（如果不存在）
    ConfigPath := ExpandConstant('{userappdata}\{#MyAppNameEN}\config.json');
    if not FileExists(ConfigPath) then
    begin
      // 这里可以创建默认配置
      SaveStringToFile(ConfigPath, '{"version": "' + '{#MyAppVersion}' + '"}', False);
    end;
  end;
end;