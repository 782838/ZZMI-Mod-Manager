; ZZMI Mod 管家 — 安装程序脚本 (Inno Setup 6)
; 编译: ISCC.exe setup.iss
; 特性: 普通权限安装(无 UAC)、自动创建快捷方式、装完自动启动、首次启动自动检测 ZZMI 路径

#define MyAppName "ZZMI Mod 管家"
#define MyAppNameEn "ZZMI Mod Manager"
#define MyAppVersion "1.5.26"
#define MyAppExeName "ZZMI-Mod-Manager.exe"
#define MyAppId "{{8F3D6C21-9A47-4E5B-B0D2-77A1C3E9F504}"

[Setup]
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppNameEn}
DefaultDirName={autopf}\{#MyAppNameEn}
DirExistsWarning=no
AppendDefaultDirName=no
DisableProgramGroupPage=yes
DisableDirPage=no
; —— 普通用户权限, 全程不弹 UAC ——
PrivilegesRequired=lowest
OutputDir=..\安装包
OutputBaseFilename=ZZMI-Mod-Manager-Setup-{#MyAppVersion}
SetupIconFile=app.ico
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=no
ShowLanguageDialog=no

[Languages]
Name: "chs"; MessagesFile: "ChineseSimplified.isl"

[Messages]
chs.WelcomeLabel2=这将安装 [name/ver] 到你的电脑。%n%n安装完成后无需任何配置: 程序会在首次启动时自动检测本机 ZZMI 的安装位置, 检测不到时也可以在界面里手动填写。%n%n建议先关闭正在运行的绝区零与 XXMI Launcher。
chs.FinishedLabelNoIcons=安装完成!%n%n「[name]」已装到本机。%n%n请通过桌面快捷方式启动(会弹 UAC, 点【是】)。首次启动会自动检测 ZZMI 路径, 无需手动配置。
chs.FinishedLabel=安装完成!%n%n「[name]」已装到本机。%n%n请通过桌面快捷方式启动(会弹 UAC, 点【是】)。首次启动会自动检测 ZZMI 路径, 无需手动配置。

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式(&D)"; GroupDescription: "附加任务:"; Flags: checkedonce
Name: "quicklaunchicon"; Description: "创建快速启动栏快捷方式(&Q)"; GroupDescription: "附加任务:"; Flags: unchecked

[Files]
Source: "..\ZZMI-Mod-Manager.exe"; DestDir: "{app}"; DestName: "{#MyAppExeName}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "绝区零 ZZMI 模组管理器 - 浏览/切换/方案/仓库"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; Comment: "绝区零 ZZMI 模组管理器"
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; 注意: exe 带管理员清单(requireAdministrator), 安装器普通权限下不能直接 CreateProcess 启动它
; (会报 740)。所以这里不提供「安装后立即运行」, 请用户从桌面/开始菜单快捷方式启动(会正常弹 UAC)。

[UninstallDelete]
; 卸载只删程序本体, 不动用户数据 (%USERPROFILE%\.zzmi-manager 的配置/方案/操作日志会保留)
Type: filesandordirs; Name: "{app}"
