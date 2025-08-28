; Inno Setup Script for Baal Pet Assistant

#define MyAppName "Baal Pet Assistant"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Baal Project"
#define MyAppExeName "Baal宠物助手.exe"
#define MyAppURL "https://github.com/yourusername/baal-standalone"

[Setup]
AppId={{B4D5F8E2-3C9A-4B7D-8E1F-2A3C5D6E7F90}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
; 如果没有 LICENSE 文件，注释掉上面这行
OutputDir=Output
OutputBaseFilename=BaalPetAssistant_Setup
SetupIconFile=baal\resources\icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\{#MyAppExeName}
DisableDirPage=no
DisableProgramGroupPage=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "dist\Baal宠物助手\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; 包含所有依赖文件和资源
Source: "dist\Baal宠物助手\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
Type: filesandordirs; Name: "{userappdata}\BaalPet"

[Code]
function InitializeSetup(): Boolean;
var
  ErrorCode: Integer;
begin
  Result := True;
  
  // 检查是否已经在运行
  if FileExists(ExpandConstant('{userappdata}\BaalPet\lock.pid')) then
  begin
    if MsgBox('检测到 Baal Pet Assistant 可能正在运行。' + #13#10 + 
              '请先关闭程序再继续安装。' + #13#10 + #13#10 +
              '是否继续安装？', mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
    end;
  end;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
begin
  // 尝试结束可能正在运行的进程
  Exec('taskkill', '/F /IM Baal宠物助手.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Result := '';
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
begin
  if CurUninstallStep = usUninstall then
  begin
    // 卸载时确保程序已关闭
    Exec('taskkill', '/F /IM Baal宠物助手.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    
    // 询问是否删除用户数据
    if MsgBox('是否删除用户配置和数据？', mbConfirmation, MB_YESNO) = IDYES then
    begin
      DelTree(ExpandConstant('{userappdata}\BaalPet'), True, True, True);
    end;
  end;
end;