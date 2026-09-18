# ZZMI Mod Manager · ZZMI Mod 管家

A local mod manager for **Zenless Zone Zero** (ZZMI / XXMI Launcher).
It turns "rename folders by hand" into a few clicks.

绝区零 **ZZMI / XXMI Launcher** 的 Mod 管理界面。把「进文件夹手动改名」变成点几下鼠标。

> 📖 **Language / 语言**：English first, Chinese below. 英文在前，中文在后（本项目主要面向中文用户）。

---

# English

## ⚠️ Disclaimer — read first

This project is a **local file management utility only**. It does not modify game binaries,
inject the game process, tamper with game memory, and it ships **no game or mod assets**.

*Zenless Zone Zero* is developed by HoYoverse. This project is **not affiliated with,
endorsed, or authorized by HoYoverse**. The game's terms of service **do not allow modding**;
using mods may result in an **account ban**. **All risks and consequences are borne by the user.**

Provided for personal learning and research only; commercial use and repackaged distribution
are prohibited. Full text: [DISCLAIMER.md](DISCLAIMER.md).

## Features

- **Zero configuration** — auto-detects your ZZMI install, Mods folder, launcher and game path
- **Native-feeling window** — opened via Edge/Chrome `--app`, no address bar
- **Proxy-proof** — forces a direct connection to `127.0.0.1` (system proxies often break localhost)
- **Character grouping** — infers the character from the mod name (editable); see all outfits at a glance
- **Component / variant toggles** — parses mutually-overriding `.ini` files into variant groups
- **Variant hints (read-only)** — for in-game key-cycled variants (`$menu = 0,1` + `type = cycle`),
  shows how many variants exist and **which key combo cycles them in game** — e.g. `Ctrl+Alt+Y+6`
  (in 3DMigoto, a space in `key =` means `+`, so the whole line is one chord).
  **Read-only: your `.ini` files are never modified.**
- **Global hotkey** — customizable (default `F9`); show/hide the manager even while the game is running
- **Runs as administrator** — UAC prompt on launch, so the hotkey works while the game has focus
- **Never deletes anything** — "disable" only adds a `DISABLED_` prefix; fully undoable
- **Fully local** — listens on `127.0.0.1` with a one-time token; no network, no telemetry

## Download

Go to **[Releases](../../releases)** and grab either:

- `ZZMI-Mod-Manager-Setup-<ver>.exe` — installer (installs without UAC; elevates at runtime)
- `ZZMI-Mod-Manager.exe` — portable (copy anywhere and run)

No Python required. **Run as administrator** (click *Yes* on the UAC prompt).
If you use the installer, launch it from the **desktop shortcut**, not the "Run now" checkbox.

## Quick start

1. Launch, wait for auto-detection (green path = found).
2. If not found: click the red hint (or ⚙ Settings) → fill in the ZZMI path → *Save & Rescan*.
3. The ZZMI path is the folder containing `Resources\Bin\XXMI Launcher.exe` and `ZZMI\`.
4. Press **F10** in game to reload mods; **F6** temporarily toggles all costume mods.

## How enable/disable works

3DMigoto's `d3dx.ini` loads everything under `Mods` recursively but skips `DISABLED*`:

```ini
[Include]
include_recursive = Mods
exclude_recursive = DISABLED*
```

So disabling = renaming:

```
Mods\...\Anby
Mods\...\DISABLED_Anby     <- disabled
```

Not a single byte is deleted. Every action is journaled (`~/.zzmi-manager/journal.jsonl`),
so Undo always works.

## Keys / data

- Hotkey: configurable, default **F9**
- Data folder: `%USERPROFILE%\.zzmi-manager\` (config, journal, thumbnail cache)
- Env vars: `ZZMI_MANAGER_DATA`, `ZZMI_NO_BROWSER=1`

## Development

```bat
pyinstaller --noconfirm --onefile --name ZZMI-Mod-Manager --add-data "ui.html;." zzmi_manager.py
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\setup.iss
```

Tests run against sandbox folders only (never your real mods):
`tests\test_core.py`, `test_http.py`, `test_exe.py`, `ui_check.py`.

---

# 中文

## ⚠️ 免责声明（务必先读）

本项目仅为**本地文件管理工具**，不修改游戏本体、不注入游戏进程、不篡改游戏内存，
**不内置任何游戏或模组资源**。

《绝区零》为米哈游旗下游戏，本项目与米哈游**无任何关联、未获授权**。
绝区零用户协议**不支持使用模组**，使用模组存在**账号封禁风险**，
**一切后果由使用者本人自行承担**。仅用于个人技术学习研究，禁止商用与分发整合包。
完整声明见 [DISCLAIMER.md](DISCLAIMER.md)。

## 功能

- **零配置**：启动后自动在本机找到你的 ZZMI 安装位置、Mods 目录、启动器、游戏路径
- **独立窗口**：用 Edge/Chrome 的 App 模式打开，看起来就是个软件，没有地址栏
- **自动绕过代理**：很多人 127.0.0.1 被系统代理拦截导致"点了没反应"，这个程序强制直连，绕开这个坑
- **按角色分类**：自动从 mod 名识别角色（可手改），一个角色几套 mod 一眼看清
- **部件 / 变体开关**：自动解析 mod 里互相覆盖的 ini，归成"变体组"一键切换（如 长剑/短剑、贴图 A/B）
- **变体提示（只读）**：解析 ini 里 `$menu = 0,1` + `type = cycle` 这类游戏内按键循环的变体，
  显示**有几个变体、游戏内按哪个组合键切换**（如 `Ctrl+Alt+Y+6`，空格即 +），并给出中文名
  （上装 / 下装 / 菜单…）。**只读，绝不修改你的 ini**
- **全局快捷键**：可自定义（默认 `F9`），绝区零运行时按下即可呼出 / 隐藏管理器窗口
- **管理员权限运行**：启动时弹 UAC，提权后游戏在前台也能正常收快捷键
- **不删文件**：所有"禁用"只是给文件夹名加 `DISABLED_` 前缀，随时可撤销
- **纯本地**：只监听 `127.0.0.1`，带一次性令牌，不联网不上传

## 下载

到 [Releases](../../releases) 页面下载 `ZZMI-Mod-Manager-Setup-<版本>.exe`（安装版）
或 `ZZMI-Mod-Manager.exe`（免安装版），无需 Python 环境。

装完请**从桌面快捷方式启动**（安装完成页的「立即运行」已移除），弹 UAC 点「是」以管理员运行。

## 一、怎么启动

**双击 `启动ZZMI管家.bat`**（需要 Python 3.8+，安装时勾选 "Add python.exe to PATH"）
或 **双击 `ZZMI-Mod-Manager.exe`**（免安装版，推荐，不需要 Python）。

启动后：

1. 会弹出一个**独立窗口**（不是浏览器标签页），那就是管理界面
2. 屏幕上会有一个**黑色控制台窗口**——那是服务本体，**关掉它 = 退出程序**
   （也可以在界面「⚙ 设置」最下面点「⏻ 退出」）

> 首次运行会用几秒钟生成预览缩略图，左上角会显示还剩多少张，生成完就是秒开。

## 二、换电脑后第一次用

1. 双击启动，等它自动找 ZZMI
2. 找到了：顶部显示绿色路径，直接能用
3. 没找到：点顶部红色提示（或 ⚙ 设置）→ 填 ZZMI 路径 → 「保存并扫描」

**"ZZMI 路径"填哪一层？** 含有 `Resources\Bin\XXMI Launcher.exe` 和 `ZZMI` 子目录的那一层：

```
D:\Mods                          <- 填这一层
├── Resources\Bin\XXMI Launcher.exe
├── XXMI Launcher Config.json
└── ZZMI\
    ├── d3dx.ini
    └── Mods\                   <- 你的 mod 都在这里
```

默认安装位置通常是 `C:\Users\你的名字\AppData\Roaming\XXMI Launcher`。
不确定就点「🔍 自动查找」。

## 三、界面功能

| 位置 | 功能 |
| --- | --- |
| 顶栏「▶ 启动游戏」 | 用 `XXMI Launcher.exe --nogui --xxmi ZZMI` 直接拉起游戏。**会弹 UAC 授权窗口，点「是」游戏才会启动** |
| 顶栏「↶ 撤销」 | 撤销上一步改名／搬运 |
| 顶栏「⟳ 重新扫描」 | 外部改动过 mod 目录后刷新 |
| 顶栏「🗄 仓库」 | 管理 Mods 外面那些不加载的 mod（见下） |
| 左侧「角色」 | **按角色分组**，`×2` 表示这个角色有多套 mod |
| 卡片「只留这套」 | **同角色只留这一套**，其它自动禁用（换皮肤最常用） |
| 详情抽屉 | 改角色名、看 ini、**看变体提示**、逐个子目录单独开关 |
| 卡片开关 | 启用/禁用 |
| 搜索框 | 按 mod 名／角色／路径搜，按 `/` 聚焦 |
| 冲突标签 | 两条已启用 mod 改了同一个游戏对象 |

### 角色分类（重点）

程序会自动从 mod 名字里把角色名剥出来，例如 `角色A-服装` → 角色A、`角色B 泳装` / `角色B皮肤` → 角色B（×2）。（示例为虚构，工具不会上传你的任何 mod 列表。）
识别错了没关系：打开该 mod 的「详情」，第一行就是「角色」，改完点「保存角色」即可（会记在配置里）。

## 四、它是怎么"启用/禁用"的

ZZMI 底层是 3DMigoto，官方 `d3dx.ini`：

```ini
[Include]
include = Core\ZZMI\main.ini
include_recursive = Mods
exclude_recursive = DISABLED*
```

即：Mods 下所有 `.ini` 会被递归加载，但**任何以 `DISABLED` 开头的文件夹或文件都会被忽略**。
所以「禁用」就是改名，**一个字节都不会删**。每次操作都记进日志，`撤销`永远可用。

> **游戏里按 F10** 立即重载 mod（不用重启游戏）；**F6** 临时开关所有服装 mod。
> 注意：游戏开着的时候，个别文件可能被占用导致改名失败——提示"文件被占用"就先关游戏再切。

## 五、「仓库」是什么

很多人把 mod 放在 `Mods` 外面（自己建的一些分类文件夹），这些不会被加载。
「🗄 仓库」面板会列出这些目录，想用哪套点「启用 → 移入 Mods」，用不上了再搬回去。

## 六、如果界面点了没反应（重要！）

界面靠本地小服务器驱动。**最常见原因是系统代理把 127.0.0.1 也拦截了**
（Clash / v2rayN / 迅雷 / 加速器都可能这样），表现为界面能显示但点开关没反应、图片加载不出来。

解决办法（按推荐顺序）：

1. **用本程序打开的独立窗口**——它强制绕过代理（`--proxy-server=direct://`）
2. 在代理软件里把 `127.0.0.1` 和 `localhost` 加入「直连 / 绕过」列表
3. 确认那个黑色控制台窗口还开着（关掉它程序就退出了）

## 七、数据存在哪

`%USERPROFILE%\.zzmi-manager\`：

| 文件 | 内容 |
| --- | --- |
| `config.json` | 你填的 ZZMI 路径、主题、手动指定的角色、呼出键 |
| `presets.json` | 「方案」 |
| `journal.jsonl` | 操作日志（撤销靠它） |
| `thumbs\` | 预览缩略图缓存（可整个删掉，会自动重建） |

想彻底重置就把 `.zzmi-manager` 删掉（**不影响你的 mod**）。

## 八、常见问题

**Q：点了启动游戏没反应？** 检查 XXMI Launcher / 游戏是否已在运行；启动游戏需要管理员权限（弹 UAC 要点「是」）。

**Q：界面白屏 / 一直转圈？** 见第六节（多半是代理）。

**Q：某个 mod 开了没效果？** 游戏里按 F10；有些 mod 需要游戏内按键切换变体（详情面板会告诉你按哪个键）；
打开「详情」看是否有子目录被单独禁用（卡片上会显示 `◑ 部分禁用`）。

**Q：呼出键没反应？** 默认 F9；如果没效果，在设置里换一个键，并确认程序是以管理员身份运行的。

**Q：会误删我的 mod 吗？** 不会。没有删除功能，只有重命名和移动，全部可撤销。

## 九、给开发者

```
zzmi-manager/
├── zzmi_manager.py   后端（纯标准库 + 可选 Pillow）
├── ui.html           前端（内联 CSS/JS，零外部资源）
├── bg.jpg            界面背景图
├── 启动ZZMI管家.bat
├── ZZMI-Mod-Manager.exe
├── installer/        Inno Setup 安装脚本（setup.iss）
├── 安装包/           编译产物 ZZMI-Mod-Manager-Setup-*.exe
├── screenshots/
└── tests/            test_core / test_http / test_exe / ui_check
```

重编安装包：

```bat
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\setup.iss
```

打包：

```bat
pip install pillow pyinstaller
pyinstaller --noconfirm --onefile --name ZZMI-Mod-Manager --add-data "ui.html;." --add-data "bg.jpg;." zzmi_manager.py
```

环境变量：`ZZMI_MANAGER_DATA`（自定义数据目录）、`ZZMI_NO_BROWSER=1`（不自动开窗口）。

验证（全部使用沙箱目录，不碰真实 mod）：

```bat
cd tests
python test_core.py     & 核心逻辑（扫描/粒度/角色/启停/撤销/越界）
python test_http.py     & HTTP 层（令牌/接口/搬运/方案）
python test_exe.py      & 打包后的 exe
python ui_check.py      & 无头浏览器渲染 + 截图
```

接口（都要 `?t=<token>`）：

```
GET  /api/state /api/detail?id= /api/library /api/autodetect /thumb?p= /bg.jpg
POST /api/toggle /api/scope /api/dir_toggle /api/set_char /api/preset
POST /api/move /api/rename /api/undo /api/config /api/rescan /api/launch /api/quit
```
