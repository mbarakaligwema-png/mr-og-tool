; Script generated for MR OG TOOL
; Use Inno Setup Compiler (free) to compile this script

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{A3B4C5D6-E7F8-9012-3456-7890ABCDEF12}
AppName=MR OG TOOL
AppVersion=1.0
AppPublisher=MR OG
DefaultDirName={autopf}\MR_OG_TOOL
DisableProgramGroupPage=yes
; The [Icons] section below relies on this
OutputBaseFilename=MR_OG_TOOL_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=C:\Users\mbara\Documents\MR_OG_TOOL\assets\logo.ico
DisableDirPage=no
UsePreviousAppDir=yes

[InstallDelete]
; Clean up old desktop shortcut if it exists
Type: files; Name: "{autodesktop}\MR_OG_TOOL.lnk"
Type: files; Name: "{autodesktop}\MR OG TOOL.lnk"

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; IMPORTANT: Run 'build.bat' FIRST to generate the dist/MR_OG_TOOL.exe
Source: "C:\Users\mbara\Documents\MR_OG_TOOL\dist\MR_OG_TOOL.exe"; DestDir: "{app}"; Flags: ignoreversion
; Include assets folder
Source: "C:\Users\mbara\Documents\MR_OG_TOOL\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
; Include config (optional, maybe improved to be created on first run)
Source: "C:\Users\mbara\Documents\MR_OG_TOOL\config_clean.json"; DestName: "config.json"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\MR_OG_TOOL"; Filename: "{app}\MR_OG_TOOL.exe"; IconFilename: "{app}\assets\logo.ico"
Name: "{autodesktop}\MR_OG_TOOL"; Filename: "{app}\MR_OG_TOOL.exe"; Tasks: desktopicon; IconFilename: "{app}\assets\logo.ico"

[Run]
Filename: "{app}\MR_OG_TOOL.exe"; Description: "{cm:LaunchProgram,MR OG TOOL}"; Flags: nowait postinstall skipifsilent
