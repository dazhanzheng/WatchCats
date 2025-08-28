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
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加任务:"; Flags: unchecked
Name: "startup"; Description: "开机自动启动"; GroupDescription: "附加任务:"; Flags: unchecked

[Files]
Source: "..\dist\Watch Cats\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Watch Cats"; Filename: "{app}\Watch Cats.exe"
Name: "{group}\卸载 Watch Cats"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Watch Cats"; Filename: "{app}\Watch Cats.exe"; Tasks: desktopicon
Name: "{userstartup}\Watch Cats"; Filename: "{app}\Watch Cats.exe"; Tasks: startup

[Run]
Filename: "{app}\Watch Cats.exe"; Description: "运行 Watch Cats"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
Type: filesandordirs; Name: "{userappdata}\BaalPet"
