#define MyAppName "AutoJuris IA"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "GAGC"
#define MyAppExeName "AutoJurisIA.exe"

[Setup]
AppId={{A7C2B7D1-4F2E-4B1D-9D6A-8C4E5F7A1234}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\AutoJuris IA
DefaultGroupName=AutoJuris IA

OutputDir=installer
OutputBaseFilename=AutoJuris_IA_Instalador

Compression=lzma
SolidCompression=yes

WizardStyle=modern
PrivilegesRequired=admin

ArchitecturesInstallIn64BitMode=x64


[Files]

Source: "dist\AutoJurisIA.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: ".env"; DestDir: "{app}"; Flags: ignoreversion


[Icons]

Name: "{autoprograms}\AutoJuris IA"; Filename: "{app}\AutoJurisIA.exe"

Name: "{autodesktop}\AutoJuris IA"; Filename: "{app}\AutoJurisIA.exe"


[Run]

Filename: "{app}\AutoJurisIA.exe"; \
Description: "Executar AutoJuris IA"; \
Flags: nowait postinstall skipifsilent