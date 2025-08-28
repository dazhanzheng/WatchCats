; Inno Setup Script for Watch Cats Desktop Pet

[Setup]
AppName=Watch Cats
AppVersion=1.0.0
AppPublisher=Watch Cats Team
AppPublisherURL=https://github.com/dazhanzheng/WatchCats
AppSupportURL=https://github.com/dazhanzheng/WatchCats/issues
DefaultDirName={autopf}\WatchCats
DefaultGroupName=Watch Cats
OutputDir=..\Output
OutputBaseFilename=WatchCats-Setup
Compression=lzma2/max
SolidCompression=yes
SetupIconFile=..\baal\resources\watchcats_hq.ico
UninstallDisplayIcon={app}\Watch Cats.exe
WizardStyle=modern
PrivilegesRequired=admin
DisableProgramGroupPage=yes
ShowLanguageDialog=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create desktop shortcut"; GroupDescription: "Additional tasks:"; Flags: unchecked
Name: "startup"; Description: "Launch at Windows startup"; GroupDescription: "Additional tasks:"; Flags: unchecked

[Files]
Source: "..\dist\Watch Cats\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Watch Cats"; Filename: "{app}\Watch Cats.exe"
Name: "{group}\Uninstall Watch Cats"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Watch Cats"; Filename: "{app}\Watch Cats.exe"; Tasks: desktopicon
Name: "{userstartup}\Watch Cats"; Filename: "{app}\Watch Cats.exe"; Tasks: startup

[Run]
Filename: "{app}\Watch Cats.exe"; Description: "Launch Watch Cats"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
Type: filesandordirs; Name: "{userappdata}\BaalPet"

[Code]
function InitializeSetup(): Boolean;
var
  ErrorCode: Integer;
  UninstallString: String;
begin
  Result := True;
  
  // Check if already installed
  if RegQueryStringValue(HKLM, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppName")}_is1', 'UninstallString', UninstallString) then
  begin
    if MsgBox('Watch Cats is already installed. Do you want to uninstall the old version first?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      Exec(UninstallString, '/SILENT', '', SW_SHOW, ewWaitUntilTerminated, ErrorCode);
    end;
  end;
end;