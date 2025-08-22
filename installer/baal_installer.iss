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
; 高质量图标文件（构建时必须生成）
SetupIconFile=icons\WatchCats.ico
; 用于检测应用程序是否运行
AppMutex={#MyAppNameEN}Mutex
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\{#MyAppExeName}

; 界面设置
ShowLanguageDialog=yes
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
Name: "chinese"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
; Chinese messages
chinese.LaunchProgram=启动 {#MyAppName}
chinese.CreateDesktopIcon=创建桌面快捷方式(&D)
chinese.CreateQuickLaunchIcon=创建快速启动栏快捷方式(&Q)
chinese.InstallVCRedist=正在安装 Visual C++ 运行库...
chinese.CheckingDependencies=正在检查系统依赖项...
chinese.ConfiguringApp=正在配置应用程序...
chinese.StartupIcon=开机自动启动
chinese.StartupIconDesc=设置 {#MyAppName} 开机自动启动

; English messages
english.LaunchProgram=Launch {#MyAppName}
english.CreateDesktopIcon=Create a &desktop shortcut
english.CreateQuickLaunchIcon=Create a &Quick Launch shortcut
english.InstallVCRedist=Installing Visual C++ Runtime...
english.CheckingDependencies=Checking system dependencies...
english.ConfiguringApp=Configuring application...
english.StartupIcon=Start automatically at Windows startup
english.StartupIconDesc=Configure {#MyAppName} to start automatically

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsWin64
Name: "startupicon"; Description: "{cm:StartupIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; 主程序
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; 高质量图标文件（必须存在）
Source: "icons\WatchCats.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "icons\WatchCats_256.png"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "icons\WatchCats_512.png"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

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
Source: "config_template.json"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; 用户手册（不包含 README.txt）
Source: "..\USER_MANUAL.md"; DestDir: "{app}"; DestName: "用户手册.txt"; Flags: ignoreversion skipifsourcedoesntexist

[Dirs]
; 创建用户数据目录（使用 LOCALAPPDATA）
Name: "{localappdata}\{#MyAppNameEN}"
Name: "{localappdata}\{#MyAppNameEN}\logs"
Name: "{localappdata}\{#MyAppNameEN}\data"

[Icons]
; Start menu shortcuts - 使用高质量图标
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\WatchCats.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{group}\User Manual"; Filename: "{app}\用户手册.txt"; IconFilename: "{app}\WatchCats.ico"
Name: "{group}\Configuration Folder"; Filename: "{userappdata}\{#MyAppNameEN}"; IconFilename: "{app}\WatchCats.ico"

; Desktop shortcut - 使用高质量图标
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\WatchCats.ico"; IconIndex: 0

; Quick Launch shortcut - 使用高质量图标
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon; IconFilename: "{app}\WatchCats.ico"

; Startup shortcut (removed - using registry instead)

[Registry]
; 开机自启动（与应用内部的 AutostartManager 保持一致）
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppNameEN}"; ValueData: """{app}\{#MyAppExeName}"""; Tasks: startupicon; Flags: uninsdeletevalue

; 文件关联（可选）
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocName}"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocName}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocName}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocName}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: "{#MyAppAssocExt}"; ValueData: ""

; 应用设置
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppNameEN}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppNameEN}"; ValueType: string; ValueName: "ConfigPath"; ValueData: "{localappdata}\{#MyAppNameEN}"
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

// 注意: DirExists 和 FileExists 是 Inno Setup 的内置函数，不需要自定义

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
    if GetUILanguage = $0804 then // 中文
      Message := '检测到已安装旧版本。是否继续安装？'
    else
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
    if GetUILanguage = $0804 then // 中文
      Message := '未检测到 Visual C++ 运行库。' + #13#10 + '安装程序将自动安装所需的运行库。'
    else
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
  if not VCRedist64Installed() then
  begin
    Exec(ExpandConstant('{tmp}\vc_redist.x64.exe'), '/quiet /norestart', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
  
  // 安装 32 位运行库（某些依赖可能需要）
  if not VCRedist32Installed() then
  begin
    Exec(ExpandConstant('{tmp}\vc_redist.x86.exe'), '/quiet /norestart', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
  
  WizardForm.ProgressGauge.Style := npbstNormal;
end;

// Uninstall confirmation
function InitializeUninstall(): Boolean;
var
  Msg: String;
begin
  // 根据系统语言选择消息
  if GetUILanguage = $0804 then // 中文
    Msg := '您确定要卸载 {#MyAppName} 吗？' + #13#10 + 
           '注意：用户数据和设置将被保留。'
  else
    Msg := 'Are you sure you want to uninstall {#MyAppName}?' + #13#10 + 
           'Note: User data and settings will be preserved.';
  
  Result := MsgBox(Msg, mbConfirmation, MB_YESNO) = IDYES;
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
    // 使用 LOCALAPPDATA 保存配置（不会漫游到其他设备）
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
    
    // 创建启动批处理文件，设置环境变量
    // SetEnvironmentVariable 不是 Inno Setup 的标准函数
    SaveStringToFile(
      ExpandConstant('{app}\start_with_env.bat'),
      '@echo off' + #13#10 +
      'set QT_PLUGIN_PATH=%~dp0_internal\PyQt6\Qt6\plugins' + #13#10 +
      'set QT_QPA_PLATFORM_PLUGIN_PATH=%~dp0_internal\PyQt6\Qt6\plugins\platforms' + #13#10 +
      'start "" "%~dp0{#MyAppExeName}"' + #13#10,
      False
    );
  end;
end;

// 安全复制文件的函数 - 增强版，使用多种方法
function SafeCopyFile(const SourceFile, DestFile: String): Boolean;
var
  ErrorCode: Integer;
  TempCmd: String;
begin
  Result := False;
  
  // 记录源文件和目标文件
  Log('SafeCopyFile: Source = ' + SourceFile);
  Log('SafeCopyFile: Dest = ' + DestFile);
  
  // 检查源文件是否存在
  if not FileExists(SourceFile) then
  begin
    Log('SafeCopyFile: Source file does not exist!');
    Exit;
  end;
  
  try
    // 确保目标目录存在
    if not ForceDirectories(ExtractFilePath(DestFile)) then
    begin
      Log('SafeCopyFile: Failed to create target directory');
    end;
    
    // 方法1: 尝试 FileCopy
    Log('SafeCopyFile: Trying method 1 - FileCopy');
    Result := FileCopy(SourceFile, DestFile, False);
    
    if Result then
    begin
      Log('SafeCopyFile: Method 1 succeeded');
      Exit;
    end;
    
    // 方法2: 使用 copy 命令
    if not Result then
    begin
      Log('SafeCopyFile: Trying method 2 - copy command');
      TempCmd := '/C copy /Y "' + SourceFile + '" "' + DestFile + '"';
      if Exec('cmd.exe', TempCmd, '', SW_HIDE, ewWaitUntilTerminated, ErrorCode) then
      begin
        Result := (ErrorCode = 0) and FileExists(DestFile);
        if Result then
        begin
          Log('SafeCopyFile: Method 2 succeeded');
          Exit;
        end
        else
        begin
          Log('SafeCopyFile: Method 2 failed with error code: ' + IntToStr(ErrorCode));
        end;
      end;
    end;
    
    // 方法3: 使用 xcopy 命令
    if not Result then
    begin
      Log('SafeCopyFile: Trying method 3 - xcopy command');
      TempCmd := '"' + SourceFile + '" "' + DestFile + '*" /Y /Q';
      if Exec('xcopy.exe', TempCmd, '', SW_HIDE, ewWaitUntilTerminated, ErrorCode) then
      begin
        Result := (ErrorCode = 0) and FileExists(DestFile);
        if Result then
        begin
          Log('SafeCopyFile: Method 3 succeeded');
        end
        else
        begin
          Log('SafeCopyFile: Method 3 failed with error code: ' + IntToStr(ErrorCode));
        end;
      end;
    end;
    
    // 方法4: 使用 PowerShell
    if not Result then
    begin
      Log('SafeCopyFile: Trying method 4 - PowerShell');
      TempCmd := '-Command "Copy-Item -Path ''' + SourceFile + ''' -Destination ''' + DestFile + ''' -Force"';
      if Exec('powershell.exe', TempCmd, '', SW_HIDE, ewWaitUntilTerminated, ErrorCode) then
      begin
        Result := (ErrorCode = 0) and FileExists(DestFile);
        if Result then
        begin
          Log('SafeCopyFile: Method 4 succeeded');
        end
        else
        begin
          Log('SafeCopyFile: Method 4 failed with error code: ' + IntToStr(ErrorCode));
        end;
      end;
    end;
    
  except
    // Inno Setup Pascal Script 不支持 on E: Exception do 语法
    Log('SafeCopyFile: Exception occurred');
    Result := False;
  end;
  
  if not Result then
  begin
    Log('SafeCopyFile: All methods failed!');
  end;
end;

// 更新config.json中的model字段
procedure UpdateConfigModel(ConfigPath: String);
var
  ConfigContent: AnsiString;
  UpdatedContent: String;
  ModelPos, ColonPos, QuotePos, EndQuotePos: Integer;
  TempStr: String;
begin
  try
    // 读取文件内容
    if LoadStringFromFile(ConfigPath, ConfigContent) then
    begin
      UpdatedContent := ConfigContent;
      
      // 查找 "model" 字段
      ModelPos := Pos('"model"', UpdatedContent);
      if ModelPos > 0 then
      begin
        // 从model位置开始查找冒号
        TempStr := Copy(UpdatedContent, ModelPos, Length(UpdatedContent) - ModelPos + 1);
        ColonPos := Pos(':', TempStr);
        if ColonPos > 0 then
        begin
          // 找到值的开始引号
          TempStr := Copy(TempStr, ColonPos, Length(TempStr) - ColonPos + 1);
          QuotePos := Pos('"', TempStr);
          if QuotePos > 0 then
          begin
            // 计算绝对位置
            QuotePos := ModelPos + ColonPos + QuotePos - 2;
            
            // 找到结束引号
            TempStr := Copy(UpdatedContent, QuotePos + 1, Length(UpdatedContent) - QuotePos);
            EndQuotePos := Pos('"', TempStr);
            if EndQuotePos > 0 then
            begin
              // 删除旧值
              Delete(UpdatedContent, QuotePos + 1, EndQuotePos - 1);
              // 插入新值
              Insert('doubao-seed-1-6-flash-250715', UpdatedContent, QuotePos + 1);
              
              // 保存更新后的内容
              if SaveStringToFile(ConfigPath, AnsiString(UpdatedContent), False) then
              begin
                Log('UpdateConfigModel: Successfully updated model to doubao-seed-1-6-flash-250715');
              end
              else
              begin
                Log('UpdateConfigModel: Failed to save updated config');
              end;
            end;
          end;
        end;
      end
      else
      begin
        Log('UpdateConfigModel: model field not found in config');
      end;
    end;
  except
    Log('UpdateConfigModel: Error updating config file');
  end;
end;

// 改进的数据迁移函数
procedure MigrateOldDataSafe();
var
  OldConfigPath: String;
  NewConfigPath: String;
  OldMemoryPath: String;
  NewMemoryPath: String;
  ResultCode: Integer;
  StatusText: String;
  FilesCopied: Integer;
  FailedFiles: String;
  MsgText: String;
  LineBreak: String;
begin
  // 定义换行符
  LineBreak := Chr(13) + Chr(10);
  
  // 定义旧版本路径 (BaalPet in Roaming)
  OldConfigPath := ExpandConstant('{userappdata}\BaalPet');
  // 定义新版本路径 (WatchCats in Local)  
  NewConfigPath := ExpandConstant('{localappdata}\WatchCats');
  
  // 记录到日志
  Log('Migration: Old path = ' + OldConfigPath);
  Log('Migration: New path = ' + NewConfigPath);
  
  // 检查旧版本目录是否存在
  if not DirExists(OldConfigPath) then
  begin
    Log('Migration: Old directory not found, skipping migration');
    Exit;
  end;
  
  StatusText := '检测到旧版本数据，正在迁移...';
  if GetUILanguage <> $0804 then
    StatusText := 'Old version data detected, migrating...';
    
  WizardForm.StatusLabel.Caption := StatusText;
  WizardForm.ProgressGauge.Style := npbstMarquee;
  
  // 确保新目录存在
  if not ForceDirectories(NewConfigPath) then
  begin
    Log('Migration: Failed to create new directory');
    MsgText := '无法创建目录: ' + NewConfigPath + LineBreak +
               '请检查权限或手动创建目录后重试。';
    if GetUILanguage <> $0804 then
      MsgText := 'Cannot create directory: ' + NewConfigPath + LineBreak +
                 'Please check permissions or create directory manually.';
    MsgBox(MsgText, mbError, MB_OK);
    Exit;
  end;
  
  FilesCopied := 0;
  FailedFiles := '';
  
  // 迁移 config.json
  if FileExists(OldConfigPath + '\config.json') then
  begin
    Log('Migration: Found config.json');
    if not FileExists(NewConfigPath + '\config.json') then
    begin
      if SafeCopyFile(OldConfigPath + '\config.json', NewConfigPath + '\config.json') then
      begin
        FilesCopied := FilesCopied + 1;
        Log('Migration: Successfully copied config.json');
        // 更新model字段
        UpdateConfigModel(NewConfigPath + '\config.json');
      end
      else
      begin
        FailedFiles := FailedFiles + 'config.json, ';
        Log('Migration: Failed to copy config.json');
      end;
    end
    else
    begin
      Log('Migration: config.json already exists in new location');
      // 也更新已存在文件的model字段
      UpdateConfigModel(NewConfigPath + '\config.json');
    end;
  end;
  
  // 迁移 chat_history.json 到新的 conversation_history.json
  if FileExists(OldConfigPath + '\chat_history.json') then
  begin
    Log('Migration: Found chat_history.json');
    // 新版本使用 conversation_history.json
    if not FileExists(NewConfigPath + '\conversation_history.json') then
    begin
      // 注意：文件名改变了
      if SafeCopyFile(OldConfigPath + '\chat_history.json', NewConfigPath + '\conversation_history.json') then
      begin
        FilesCopied := FilesCopied + 1;
        Log('Migration: Successfully copied chat_history.json as conversation_history.json');
      end
      else
      begin
        FailedFiles := FailedFiles + 'chat_history.json, ';
        Log('Migration: Failed to copy chat_history.json');
      end;
    end
    else
    begin
      Log('Migration: conversation_history.json already exists in new location');
    end;
  end;
  
  // 也检查是否有旧的 conversation_history.json
  if FileExists(OldConfigPath + '\conversation_history.json') then
  begin
    Log('Migration: Found conversation_history.json');
    if not FileExists(NewConfigPath + '\conversation_history.json') then
    begin
      if SafeCopyFile(OldConfigPath + '\conversation_history.json', NewConfigPath + '\conversation_history.json') then
      begin
        FilesCopied := FilesCopied + 1;
        Log('Migration: Successfully copied conversation_history.json');
      end
      else
      begin
        FailedFiles := FailedFiles + 'conversation_history.json, ';
        Log('Migration: Failed to copy conversation_history.json');
      end;
    end;
  end;
  
  // 迁移 schedules.json
  if FileExists(OldConfigPath + '\schedules.json') then
  begin
    if not FileExists(NewConfigPath + '\schedules.json') then
    begin
      if SafeCopyFile(OldConfigPath + '\schedules.json', NewConfigPath + '\schedules.json') then
      begin
        FilesCopied := FilesCopied + 1;
      end
      else
      begin
        FailedFiles := FailedFiles + 'schedules.json, ';
      end;
    end;
  end;
  
  // 迁移 goals.json 到 supervision.json (新版本的监督文件)
  if FileExists(OldConfigPath + '\goals.json') then
  begin
    Log('Migration: Found goals.json');
    if not FileExists(NewConfigPath + '\supervision.json') then
    begin
      // 注意：文件名改变了，从 goals.json 到 supervision.json
      if SafeCopyFile(OldConfigPath + '\goals.json', NewConfigPath + '\supervision.json') then
      begin
        FilesCopied := FilesCopied + 1;
        Log('Migration: Successfully copied goals.json as supervision.json');
      end
      else
      begin
        FailedFiles := FailedFiles + 'goals.json, ';
        Log('Migration: Failed to copy goals.json');
      end;
    end
    else
    begin
      Log('Migration: supervision.json already exists in new location');
    end;
  end;
  
  // 也检查 supervision_config.json
  if FileExists(OldConfigPath + '\supervision_config.json') then
  begin
    Log('Migration: Found supervision_config.json');
    if not FileExists(NewConfigPath + '\supervision.json') then
    begin
      if SafeCopyFile(OldConfigPath + '\supervision_config.json', NewConfigPath + '\supervision.json') then
      begin
        FilesCopied := FilesCopied + 1;
        Log('Migration: Successfully copied supervision_config.json as supervision.json');
      end
      else
      begin
        FailedFiles := FailedFiles + 'supervision_config.json, ';
        Log('Migration: Failed to copy supervision_config.json');
      end;
    end;
  end;
  
  // 直接检查 supervision.json (如果旧版本已经使用这个名称)
  if FileExists(OldConfigPath + '\supervision.json') then
  begin
    Log('Migration: Found supervision.json');
    if not FileExists(NewConfigPath + '\supervision.json') then
    begin
      if SafeCopyFile(OldConfigPath + '\supervision.json', NewConfigPath + '\supervision.json') then
      begin
        FilesCopied := FilesCopied + 1;
        Log('Migration: Successfully copied supervision.json');
      end
      else
      begin
        FailedFiles := FailedFiles + 'supervision.json, ';
        Log('Migration: Failed to copy supervision.json');
      end;
    end;
  end;
  
  // 迁移 memory 文件夹
  OldMemoryPath := OldConfigPath + '\memory';
  NewMemoryPath := NewConfigPath + '\memory';
  
  if DirExists(OldMemoryPath) then
  begin
    Log('Migration: Found memory folder');
    if not DirExists(NewMemoryPath) then
    begin
      ForceDirectories(NewMemoryPath);
      // 使用 xcopy 复制整个文件夹
      if Exec('xcopy.exe', '"' + OldMemoryPath + '\*.*" "' + NewMemoryPath + '\" /E /Y /I', 
              '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
      begin
        if ResultCode = 0 then
        begin
          FilesCopied := FilesCopied + 1;
          Log('Migration: Successfully copied memory folder');
        end
        else
        begin
          FailedFiles := FailedFiles + 'memory folder, ';
          Log('Migration: Failed to copy memory folder, error code: ' + IntToStr(ResultCode));
        end;
      end;
    end;
  end;
  
  WizardForm.ProgressGauge.Style := npbstNormal;
  
  // 显示结果
  if FilesCopied > 0 then
  begin
    if FailedFiles <> '' then
    begin
      // 部分成功
      MsgText := '数据迁移部分成功！' + LineBreak + 
                 '成功迁移: ' + IntToStr(FilesCopied) + ' 个项目' + LineBreak +
                 '失败项目: ' + FailedFiles + LineBreak + LineBreak +
                 '请手动复制失败的文件：' + LineBreak +
                 '从: ' + OldConfigPath + LineBreak +
                 '到: ' + NewConfigPath;
      if GetUILanguage <> $0804 then
        MsgText := 'Partial migration success!' + LineBreak +
                   'Migrated: ' + IntToStr(FilesCopied) + ' items' + LineBreak +
                   'Failed: ' + FailedFiles + LineBreak + LineBreak +
                   'Please manually copy failed files:' + LineBreak +
                   'From: ' + OldConfigPath + LineBreak +
                   'To: ' + NewConfigPath;
      MsgBox(MsgText, mbInformation, MB_OK);
    end
    else
    begin
      // 完全成功
      MsgText := '数据迁移成功！' + LineBreak + 
                 '成功迁移 ' + IntToStr(FilesCopied) + ' 个项目。' + LineBreak + LineBreak +
                 '旧版本数据保留在：' + LineBreak + 
                 OldConfigPath + LineBreak + LineBreak +
                 '建议：确认新版本正常运行后，您可以手动删除旧数据文件夹。';
      if GetUILanguage <> $0804 then
        MsgText := 'Migration successful!' + LineBreak +
                   'Migrated ' + IntToStr(FilesCopied) + ' items.' + LineBreak + LineBreak +
                   'Old data preserved at:' + LineBreak +
                   OldConfigPath + LineBreak + LineBreak +
                   'Recommendation: You can manually delete the old folder after confirming everything works.';
      MsgBox(MsgText, mbInformation, MB_OK);
    end;
  end
  else if FailedFiles <> '' then
  begin
    // 完全失败
    MsgText := '数据迁移失败！' + LineBreak + LineBreak +
               '可能的原因：' + LineBreak +
               '1. 权限不足 - 请以管理员身份运行安装程序' + LineBreak +
               '2. 文件被占用 - 请关闭所有相关程序' + LineBreak + LineBreak +
               '请手动复制文件夹：' + LineBreak +
               '从: ' + OldConfigPath + LineBreak +
               '到: ' + NewConfigPath;
    if GetUILanguage <> $0804 then
      MsgText := 'Migration failed!' + LineBreak + LineBreak +
                 'Possible reasons:' + LineBreak +
                 '1. Insufficient permissions - Run installer as administrator' + LineBreak +
                 '2. Files in use - Close all related programs' + LineBreak + LineBreak +
                 'Please manually copy folder:' + LineBreak +
                 'From: ' + OldConfigPath + LineBreak +
                 'To: ' + NewConfigPath;
    MsgBox(MsgText, mbError, MB_OK);
  end;
  
  Log('Migration: Completed with ' + IntToStr(FilesCopied) + ' files copied');
end;

// 旧的迁移函数 - 调用改进版本
procedure MigrateOldData();
begin
  MigrateOldDataSafe();
end;

// 卸载前的操作
function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  NeedsRestart := False;
  Result := '';
  
  // 执行数据迁移
  MigrateOldData();
  
  // AppMutex 在 [Setup] 中已经配置，Inno Setup 会自动检查
  // 如果需要手动检查，可以使用 CheckForMutexes 函数
  // 但需要确保应用程序实际创建了这个 mutex
end;