; Mod 管家 — 安装程序脚本 (Inno Setup 6)
; 编译: ISCC.exe setup.iss
; 特性: 普通权限安装(无 UAC)、自动创建快捷方式、装完自动启动、首次启动自动检测 XXMI 路径

#define MyAppName "Mod 管家"
; 目录名与英文名: 新版统一叫 Mod Manager, 安装时会把旧的目录/快捷方式清理掉
#define MyAppNameEn "Mod Manager"
#define MyAppVersion "1.5.72"
#define MyAppExeName "Mod-Manager.exe"
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
OutputBaseFilename=Mod-Manager-Setup-{#MyAppVersion}
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
chs.WelcomeLabel2=这将安装 [name/ver] 到你的电脑。%n%n安装完成后无需任何配置: 程序会在首次启动时自动检测本机 XXMI 的安装位置, 检测不到时也可以在界面里手动填写。%n%n建议先关闭正在运行的游戏与 XXMI Launcher。
chs.FinishedLabelNoIcons=安装完成!%n%n「[name]」已装到本机。%n%n请通过桌面快捷方式启动(会弹 UAC, 点【是】)。首次启动会自动检测 XXMI 安装目录, 无需手动配置。
chs.FinishedLabel=安装完成!%n%n「[name]」已装到本机。%n%n请通过桌面快捷方式启动(会弹 UAC, 点【是】)。首次启动会自动检测 XXMI 安装目录, 无需手动配置。

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式(&D)"; GroupDescription: "附加任务:"; Flags: checkedonce
Name: "quicklaunchicon"; Description: "创建快速启动栏快捷方式(&Q)"; GroupDescription: "附加任务:"; Flags: unchecked

[Files]
; onedir 打包产物在 dist\Mod-Manager\ 文件夹(内含 exe + _internal)
; 把文件夹内容扁平拷进 {app}, exe 最终落在 {app}\Mod-Manager.exe
Source: "..\dist\Mod-Manager\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "XXMI 各游戏的模组管理器 - 浏览/切换/方案/仓库"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; Comment: "XXMI 各游戏的模组管理器"
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; 注意: exe 带管理员清单(requireAdministrator), 安装器普通权限下不能直接 CreateProcess 启动它
; (会报 740)。所以这里不提供「安装后立即运行」, 请用户从桌面/开始菜单快捷方式启动(会正常弹 UAC)。

[UninstallDelete]
; 卸载只删程序本体, 不动用户数据 (%USERPROFILE%\.mod-manager 的配置/方案/操作日志会保留)
Type: filesandordirs; Name: "{app}"

[Code]
// v1.5.72: 装完刷新 Windows 图标缓存。
// 为什么需要: exe 换了新图标, 但资源管理器还在显示缓存里的旧图标
// (用户实测"快捷方式咋没变"), 手动清得重启 explorer。
//
// 做法: 调系统自带的 ie4uinit.exe 重建图标缓存。
// ⚠️ 曾经想直接删 %LOCALAPPDATA%\Microsoft\Windows\Explorer\iconcache_*.db,
// 但 Inno 的 Pascal 脚本里没有 SetFileAttributes/FileSetAttr 这号函数,
// 编译过不去 —— 所以改走外部命令这条路。
procedure RefreshIconCache();
var
  ResultCode: Integer;
begin
  Exec(ExpandConstant('{sys}\ie4uinit.exe'), '-show',
       '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

// v1.5.72: 从 "ZZMI Mod Manager" 改名为 "Mod Manager"。
// 老用户装在 {autopf}\ZZMI Mod Manager, 新装会落到 Mod Manager ——
// 不清理就会在机器上留两套。这里在安装前把旧目录整个删掉。
// ⚠️ 只删程序目录, 用户数据在 %USERPROFILE%\.mod-manager, 一个字节都不动。
procedure CleanOldInstall();
var
  OldDir: String;
begin
  OldDir := ExpandConstant('{autopf}\ZZMI Mod Manager');
  if DirExists(OldDir) then
  begin
    DelTree(OldDir, True, True, True);
  end;
  // 旧名字的快捷方式(开始菜单 / 桌面)也一并收走
  DeleteFile(ExpandConstant('{autoprograms}\ZZMI Mod 管家.lnk'));
  DeleteFile(ExpandConstant('{autodesktop}\ZZMI Mod 管家.lnk'));
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
    CleanOldInstall();
  if CurStep = ssPostInstall then
    RefreshIconCache();
end;

