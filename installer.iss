#define AppName "Ultimate Grind Auto Clicker - Universal Roblox Edition"
#define AppVersion "1.0.0"
#define AppExe "UltimateGrindAutoClicker.exe"
[Setup]
AppId={{C1183F91-7EC1-43AA-B9D7-AE755BDE20B8}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Ultimate Grind Community
DefaultDirName={autopf}\Ultimate Grind Auto Clicker
DefaultGroupName={#AppName}
OutputDir=release
OutputBaseFilename=UltimateGrindAutoClicker-Setup-v{#AppVersion}
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
WizardStyle=modern
UninstallDisplayIcon={app}\{#AppExe}
[Files]
Source: "dist\UltimateGrindAutoClicker\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon
[Tasks]
Name: "desktopicon"; Description: "Create desktop shortcut"; GroupDescription: "Additional icons:"
[Run]
Filename: "{app}\{#AppExe}"; Description: "Launch app"; Flags: nowait postinstall skipifsilent
