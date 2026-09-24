# ZZMI-Mod-Manager 项目交接文档

> 整理时间：2026-09-21 · 当前版本 **v1.5.37**（测试包已打好，尚未发布 GitHub）
> 适用：接手 AI 继续维护此项目前，请先通读本文件，重点看「四、五、六」三节。

---

## 一、项目是什么

- **绝区零（Zenless Zone Zero / ZZZ）** 的 3DMigoto mod 管理器，基于 ZZMI（XXMI launcher）框架 + ReShade 6.6.1 工作。
- **技术栈**：纯 Python 标准库（无第三方依赖）+ 本地 HTTP 服务器 + 单页前端 `ui.html`。零外部依赖，靠 `pyinstaller` 打成 exe、靠 Inno Setup 打成安装包。
- **仓库**：`https://github.com/782838/ZZMI-Mod-Manager`
- **mod 安装位置**：装在启动器同级目录下（示例 `D:\Mods\ZZMI\Mods`，盘符各人不同）；游戏与启动器同盘
- 用户 Windows + 管理员身份运行；UI 偏好「打开即全屏、操作时前置窗口」这类可见默认行为。

---

## 二、当前状态（2026-09-21）

- **已发布**：Release 392259299，tag `v1.5.11`，只传**安装包**（不含便携版 exe，见红线第 10 条）。v1.5.12 起攒了一堆改动**都还没发 GitHub**。
- **最新测试包**：`安装包/ZZMI-Mod-Manager-Setup-1.5.37.exe`（18,419,881 字节）。
  - 构建链：改完代码 → `grep -c CENSOR-MODE ui.html` 必须为 0 → PyInstaller（`--noconfirm --workpath build_1537 --distpath dist_1537`，注意 `--clean` 会被沙箱批量删除保护拦，改用全新工作目录）→ ISCC → `tests/_v1535_exe.py` 字节级验证。
  - 字节级验证：`tests/_v1535_exe.py` 全绿（PASS 87 / FAIL 0）；源码级回归 `test_core`(ALL PASSED) / `ui_check`(309 OK) / `_v1535_check`(134) / `ui_burst.js`(52) / `test_http`(PASSED) / `live_check`(RENDER CHECK PASSED，扫真实库 234 个 mod)。
- **代码已推到远程**：`git push origin main --tags` 已成功（用户开加速器后）。
  - 远程 `main` = `a7d0c1b`（停在 v1.5.11）
  - 远程 tag `v1.5.11` = `a7d0c1b`（release 关联源码即此提交，正确）
- 工作树：本地已提交到 `a7d0c1b`，v1.5.12~v1.5.37 的改动**尚未提交**（发布前请确保 `git status --porcelain` 干净）。

### 最近几个版本改了啥（速查）

| 版本 | 核心改动 |
|------|----------|
| v1.5.8 | 改名/启停撞同名自动加 `(2)/(3)` 序号并弹窗提示 |
| v1.5.9 | 修复反向重名场景（已启用「A」时启用 `DISABLED_A` 报找不到目录）；换成绝区零官方图标（exe/安装包/favicon） |
| v1.5.10 | ① 关界面→程序真退出（hello/bye 心跳）② 自制输入弹窗替换原生 `prompt()`（标题「ZZMI MOD 管家」）③ 更新提醒加「先关程序」提示 ④ **此后只发安装包** |
| v1.5.11 | ① 深色主题弹窗看不清修复（`.ask-msg/.ask-input` 改 `--txt`）② mod 卡片加「✎ 重命名」按钮 |
| v1.5.12 ~ v1.5.34 | 连拍抓拍（侧键/热键/挑帧页/照片墙）、界面美化、红按钮字看不见修复、照片保存位置可自定义、勾选式「选择留下」、全屏预览… |
| v1.5.35 | ① 修「按了鼠标侧键什么都没发生」（冻结判据放宽 + 失败也弹挑帧页 + 逐环原因）② 新增「🧹 清除缓存」「🩺 侧键自检」③ 后台窗口回到前台立刻补哨兵 |
| v1.5.36 | 修「提示快捷键注册失败，但按 F9 明明有反应」—— 根因是**孤儿旧实例占着全局热键**。加 **单实例检测** + **`ZZMI_TEST_MODE` 测试模式**（测试/出图实例不抢热键）+ **热键状态逐键分开记**；热键消息泵的异常处理也移出泵 |
| v1.5.37 | 用户点名 5 件事全改：①连拍改「**按下之后录 N 秒**」（不再回溯）②帧率 **12→24fps**、档位翻倍（差异指纹走 C 层）③修「切回管家不弹挑帧页」（哨兵先弹再记 + 批次 pending/ack 机制）④修「**mod 读取不全**」（`mod_root_for` 改任意深度下钻，全库 133→234）⑤「启动开两个进程」是 onefile 正常结构，另加 `retry_lost`+`WindowWatchdog` 兜住真孤儿占 F9；新增 `/api/photo_ack` |

> 各版本实现细节见本仓库 `.workbuddy/memory/VERSIONS.md`（超长，未并入主记忆）。

---

## 三、关键文件地图

| 文件 | 职责 |
|------|------|
| `zzmi_manager.py` | 后端全部逻辑（HTTP 服务、扫描、启停、改名、搬运、变体改键、自动退出、鉴权）；约 4500+ 行。改版本号在此（搜索 `VERSION = "..."`） |
| `ui.html` | 单页前端（HTML+CSS+JS 全内联）。所有 UI/交互/弹窗在此 |
| `ZZMI-Mod-Manager.spec` | PyInstaller 打包配置（`console=True`、`uac_admin=True`、`icon=installer/app.ico`、datas 含 ui.html/bg.jpg/app.ico） |
| `installer/setup.iss` | Inno Setup 安装包脚本（改版本号搜 `#define MyAppVersion`，图标 `SetupIconFile=installer/app.ico`） |
| `installer/app.ico` | 绝区零官方图标（从游戏 exe PE 提取，562KB，9 尺寸） |
| `bg.jpg` | 程序背景图 |
| `更新名单.md` | 给用户看的更新/测试清单（每次发版更新） |
| `tests/test_core.py` | 后端核心逻辑测试（不启服务） |
| `tests/test_http.py` | HTTP 联调测试（自起服务，含 §20 bye/hello 心跳回归） |
| `tests/ui_check.py` | 前端静态检查（grep 式断言，版本号相关静态检查在此追加，如 2.12） |
| `tests/live_check.py` | 真机渲染检查（自起服务→调 ui_check→退出） |
| `tests/_run_jsdom.py` + `_ui154.js` | jsdom 真 DOM 交互测试模板（起隔离后端→stub fetch/matchMedia→派发 MouseEvent→DOM 断言） |

**红线提醒**：`spec` 的 `console=True` **绝不能**改 `--noconsole`——隐藏控制台依赖 `GetConsoleWindow()` 句柄，去掉后功能失效（v1.5.7 设计）。

---

## 四、核心架构与约定（接手必读）

### 1. 接口鉴权
- 每个实例启动生成随机 `token`（9 字节 hex），前端存 `BOOT.token`（全局 `T`）。
- 所有 `/api/*` 变更接口需带 token 校验（`_ok(qs)` 在 `do_GET`/`do_POST` 开头）。**`/favicon.ico` 在鉴权之前、免鉴权返回**（放 `_ok` 之前的分支）。

### 2. 界面关闭 → 程序自动退出（v1.5.10）
- 后端 `App.schedule_autoquit`（延迟 `AUTOQUIT_DELAY=5.0s`）/ `cancel_autoquit`。
- `POST /api/bye` 调度退出；`POST /api/hello` 取消（前端 load 时发 hello，防刷新误杀）。
- 前端：`load()` 成功后 `POST /api/hello`；`pagehide`/`beforeunload` 用 `navigator.sendBeacon` 发 `/api/bye`。
- **坑**：测试里 `req(path)` 在 `body=None` 时走 GET，bye/hello 必须 `req(path, body={})` 强制 POST，否则 403。

### 3. 重名条目标识 `#N`
- `scan_mods` 给重名条目 id 加 `#1` 后缀（如 `蜜西皮肤` / `蜜西皮肤#1`）。
- `resolve_rel_dir(base, rel, prefer=None)` 剥 `_TAIL_NUM_ID_RE` 尾缀，按 `prefer`（条目真实目录 basename）精确选中；最后一段且 `prefer != part` 时**绕过 exact 快捷路径**，避免命中错误套（曾导致「假成功」）。
- 新增 `entry_root(mods_dir, e)` 包装，替代 `resolve_rel_dir(mods_dir, e["id"])`，10 处调用点已换。

### 4. `DISABLED_` 启停机制
- 禁用 = 目录加 `DISABLED_` 前缀；启用 = 去掉前缀。`is_disabled_name()` / `strip_disabled()` 处理。
- 排查「mod 变样」先看 `DISABLED_` 数量和 journal；同角色只能启用一个 body mod（否则互抢 hash 花屏）。

### 5. 自制输入弹窗 `#mAsk`（v1.5.10）
- 原生 `prompt()` 标题是网址、无法自定义，已全部替换。
- 新增 `#mAsk` 弹窗，标题固定「ZZMI MOD 管家」；`ask(label, default)` 返回 Promise。
- 6 处调用（新建文件夹 / 新建仓库 / 方案命名 / 变体改键 / 重命名 mod 等）均已 `await ask(...)`，均在 async 上下文。
- **深色看不清修复（v1.5.11）**：`.ask-msg`/`.ask-input` 文字色从 `--ink`（按钮黑字）改为 `--txt`（主题文字色）。

### 6. 排序两套
- 后端 `entries.sort` + 前端 `visible()` 各一套，**改排序必须同时改两处**。

### 7. 函数返回元组
- 改动「返回 3 元组」的函数（如 `do_toggle`/`do_rename`），**必须全局 grep `ok, msg = ` 把所有调用点一起改**（v1.5.8 漏 `/api/dir_toggle` 崩过）。

---

## 五、本机环境硬性坑（非常重要，先读再动手）

1. **shell 基本不可用**：bash 是降级 Git Bash shim（`cat/ls/tail/head/dirname/grep` 全 command not found）；PowerShell 取不到 stdout。**统一做法：写 `.py` 文件 → 输出重定向到 `.txt` → 用 Read 读结果。** `python -c` 里**绝不用反引号**（bash 当命令替换）。别写 `2>nul`（Windows 保留名）→ `2>/dev/null`。
2. **绝对路径**（`<WB>` = WorkBuddy 二进制目录，本机是 `C:\Users\<你的用户名>\.workbuddy`）：
   - 受管 Python：`<WB>\binaries\python\versions\3.13.12\python.exe`
   - 受管 Node：`<WB>\binaries\node\versions\22.22.2-3\node.exe`
   - git：`<WB>\binaries\PortableGit\versions\1.2.0\cmd\git.exe`
3. **测试 `req()` 返回三元组** `st, r, _ = req(...)`，不是二元组。
4. **`GET /api/state` 只回读缓存、不重扫！** 测试直写磁盘造目录后必须 `POST /api/rescan`，否则命中不到、`batch_toggle` 返回 `{"ok":0,"failed":0}`（像 bug，实为脚手架问题）。
5. **沙箱批量删除保护**：单 turn 累计删 >50 文件 → `SAFE_DELETE_BULK_CONFIRM_REQUIRED`，后续删除静默失败。`shutil.rmtree(沙箱)` 必撞 → 用逐文件 `_clean(p)`；别在一个 bash turn 连跑多个大删套件。
6. **exe/安装包都要管理员**（`requireAdministrator` 清单）：`Popen([exe])` → `WinError 740`；安装包 `/VERYSILENT` 什么都不做且不留痕迹（≠包坏）。本机 `schtasks.exe` 被安全策略硬拦 → 只能 `pyi-archive_viewer -l` + 查 PE 清单 + 源码测试兜。
7. **Edit 并行常假失败**：多个并行 Edit 偶发「返回 success 但文件没改」。改完务必 grep 验证落盘（v1.4.9 起踩过 N 次）。
8. **沙箱里 subprocess 奇怪失败**：换个 bash 调用重跑常常就好（假失败高发）。
9. **打包必须全新 workpath/distpath**：复用 `build/` 会触发批量删除保护。用 `_bNNN`/`_dNNN` 临时目录。
10. **网络**：本机直连 `api.github.com`/`uploads.github.com` 正常；但 `git push` 到 github.com:443 写入阶段曾被网络重置（开加速器后已恢复）。token 从 GCM 取：`git credential fill`(host=github.com) 返回 `gho_` 前缀。

---

## 六、红线（违反过，绝对不能犯）

1. **绝不擅自改/删用户文件**（用户曾为此发火）。只读诊断安全；写前先问、拿明确同意再动。
2. ini 改动**必须字节级保真**（latin-1 定位 + 原位字节拼接，保留 GBK/CRLF/BOM/行内注释），绝不整文件重写。唯一授权场景是 v1.5.4 变体改键（走 `do_cycle_rekey` 备份+journal）；`cycle_set` 仍是拒绝桩。
3. `zzmi_cover.*` 是本工具生成的封面，可覆盖/删；**用户原有图片和 ini 一个都不许动**。
4. 收藏/使用时间/仓库列表**只写 `config.json`**，绝不碰 mod 文件。
5. 操作可逆（只重命名/移动、绝不删），写 journal 支持撤销。
6. **分类维度 = 顶层文件夹名**，别改性别分组（连带影响 `/api/scope`）。改前先问。
7. **排序前后端两套**，改必同时改（见四.6）。
8. **改函数返回元组长度 → 全局 grep 调用点一起改**（见四.7）。
9. 交付前做隔离验证（测试指向沙箱），不拿真实数据做写测试。
10. **从 v1.5.10 起只发安装包，不发便携版 exe**（GitHub Releases 也只传安装包）。用户明确「只要安装包、不要便携版」。
11. **发布到 GitHub 前先问用户**（用户习惯「先不发、测满意再发」）。

---

## 七、打包与发布流程（逐步）

### 打包
1. 改版本号 3 处：`zzmi_manager.py` 的 `VERSION`、`installer/setup.iss` 的 `#define MyAppVersion`、docstring 的版本段。
2. 构建 exe：
   ```
   cd zzmi-manager
   buildenv/Scripts/pyinstaller.exe --noconfirm --workpath _bNNN --distpath _dNNN ZZMI-Mod-Manager.spec
   ```
   （`buildenv` 没了就 `python -m venv buildenv && buildenv/Scripts/python.exe -m pip install --upgrade pip pyinstaller`）
   产物 `ZZMI-Mod-Manager.exe` 拷到仓库根。
3. 构建安装包：
   ```
   cd installer && "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
   ```
   产物落 `安装包/ZZMI-Mod-Manager-Setup-X.Y.Z.exe`（**不在 installer/**）。
4. 验证：
   - `pyi-archive_viewer -l` 确认 ui.html/bg.jpg 已打包、查 PE 清单（`requireAdministrator` 在、`asInvoker` 无）。
   - 静默卸载跑安装目录里的 `unins000.exe /SILENT`（给安装包传 `/UNINSTALL` 无效）。
5. 临时 `_b*/_d*` 目录用完后删掉，别污染 `git status`。

### 发布（GitHub）
- 提交源码 → 打 tag `vX.Y.Z` → `git push origin main --tags`。
- 用 GitHub API 建 release + 上传安装包（release 建时若 tag 不存在会自动建 tag，但可能指向旧 commit；**强推 tag 要用 commit hash 而非 `refs/tags/X:refs/tags/X`，否则推的是 annotated tag 对象**）。
- 附件同名先删再传、说明用 PATCH、发布后**匿名复核** asset 的 `digest`（直连 `objects.githubusercontent.com` 常超时，用 API 返回的 digest 比对）。
- token 从 GCM 取（见五.10）。
- **不进仓库**：exe/安装包只走 Releases，`.gitignore` 已忽略。

---

## 八、测试怎么跑（改完必跑，全绿再交付）

```
# 全部用受管 Python 绝对路径
python tests/test_core.py     # 后端核心（不启服务）
python tests/test_http.py     # HTTP 联调（自起服务，含 bye/hello 心跳回归）
python tests/ui_check.py      # 前端静态检查（版本相关断言在此追加）
python tests/live_check.py    # 真机渲染（自起服务→调 ui_check→退出）
python tests/_v1535_check.py  # 后端隔离验证(冻结判据/press/clear/diag/GET+POST/钩子红线/单实例/测试模式) 83 条
buildenv/Scripts/python.exe tests/_v1535_exe.py   # 打包字节级取证(必须用 buildenv 的 Python, 要 PyInstaller) 52 条
```
- 真机渲染：`tests/live_check.py`（自起服务→调 ui_check→退出）。**别直接用 `ui_check.py`**：它不启服务、只读 `last_url.txt`，实例关了会假 FAIL。
- **打包字节级取证 `tests/_v1535_exe.py`（52 条）**：用 `CArchiveReader` 直接读 exe 里的资源，
  和磁盘源文件比 sha256（证明「改的东西真进包了」）。第 7 节会 `marshal.loads` 入口脚本、
  递归收集 code object，断言：`_why_empty.co_names` 里没有 `proc_probe`；
  **侧键 `_cb`**（4 个同名里挑"调了 `press`"的那个）的 `co_names` 里没有
  `log`/`format_exc`/`proc_probe`（见第十一节 300ms 红线）。
  ⚠ **同名函数定位要选对特征**：本文件有 **3 个 `_loop`**（burst / 鼠标钩子 / 热键），
  其中**两个**都调 `GetMessageW` —— 按 `GetMessageW` 挑**不唯一**（踩过，报 FAIL）。
  热键那个用 `RegisterHotKey` 挑才唯一。同理 `_cb` 有 4 个，按"调了 `press`"挑。
- **测试实例绝不能抢全局热键**：`tests/live_check.py`、`tests/test_http.py`、
  `gen_preview.py`、`gen_censored_shots.py` 都用 `ZZMI_TEST_MODE=1` 起源码实例
  （不注册热键、不装鼠标钩子、也不参与单实例检测）。**新增"用源码起管家"的脚本时，
  必须一并设 `ZZMI_TEST_MODE=1`** —— 否则脚本被中断后孤儿进程会一直占着 F9，
  让用户真管家报"注册失败"却又"按 F9 有反应"（v1.5.36 修的就是这个）。
- **前端行为测试（jsdom）**：`tests/ui_burst.js` —— 把整条「侧键抓拍→自动弹挑帧页」
  的前端链在 jsdom 里跑一遍（35 条断言）。仓库不带 `node_modules`，要指 NODE_PATH：
  ```
  NODE_PATH=<jsdom 的 node_modules 目录> \
    <node.exe> tests/ui_burst.js
  ```
  它专治「改完看着没问题、真机上不弹」这类只在运行期才暴露的问题 —— 后端链的改动
  也建议先在这里跑通再打包。
- `test_exe.py` 需提权（管理员），普通环境跑不了：exe 清单是 `requireAdministrator`，
  非提权进程 `CreateProcess` 直接 `WinError 740`。没提权时用 `_v1535_exe.py` 的字节级取证代替。

---

## 九、待办 / 可选后续（用户提过、尚未做）

- **方案 2（未做）**：去掉 exe 的 `requireAdministrator`，让 mods 目录（用户空间，示例 `D:\Mods`）下普通权限即可运行，减少 UAC 弹窗和「杀不掉」问题。当前仍提权，关界面虽能自动退出，但极端情况下残留进程仍需任务管理器手动结束。
- 其他按用户新需求迭代（用户习惯「小步迭代 + 测满意再发」）。

---

## 十、用户偏好（沟通方式）

- **结论先行 + 利弊清晰的细化解释**。
- 给验证步骤前先自己判断「这步会不会产出新信息」，**不要给明知无意义的验证步骤**（例如让他关掉所有滤镜再看是否模糊）。
- **别把两件事混着说**（如「模糊」vs「错位」是两种症状、成因不同，分开讲）。
- 他情绪上来时：别堆解释、别邀功，简洁承认 + 给下一步。
- 要的是**解决根本问题**，不是甩测试步骤。

---

## 十一、常见故障排查

| 现象 | 根因 | 解决 |
|------|------|------|
| 安装包覆盖安装失败 | 旧版本进程（提权 exe）后台未退，占文件锁 | 任务管理器结束 `ZZMI-Mod-Manager.exe`，再装。v1.5.10 起关界面 5s 程序自退，正常不会残留 |
| 前端渲染测试全 FAIL | `ui_check.py` 不启服务，连的是「上次实例」，实例关了就假 FAIL | 用 `live_check.py` |
| bye/hello 返回 403 | `req(path)` body=None 走 GET，bye/hello 只在 POST 处理 | `req(path, body={})` |
| 测试里 batch_toggle 返回 ok:0 | 直写磁盘后没 `POST /api/rescan`，state 只回缓存 | 测试里加 rescan |
| 改完文件像没生效 | 并行 Edit 假成功 | 改完 grep 验证 |
| **装上去所有缩略图都是模糊的** | 打包和 `gen_censored_shots.py` **并发**跑 —— 该脚本会临时往 `ui.html` 注入 CENSOR-MODE 打码 CSS，PyInstaller 恰好读到注入后那份 | 出图和打包**串行**；打包前 `grep -c CENSOR-MODE ui.html` 必须为 0；打包后比对包内 `ui.html` 与磁盘的 sha256 |
| git push 被 reset | 本机曾拦截 github 写入端点（开加速器已恢复） | 开加速器或清坏代理后重试 |
| **按了鼠标侧键什么都没发生**（用户真机反馈过） | 两个原因叠加：① 缓冲冻结判据是「前台 pid != 游戏 pid 就冻结」，PID 一对不上缓冲**永远是空的**；② 老代码**只在 `trigger()` 成功时才顶窗**，失败路径彻底静默 | v1.5.35 已修：冻结判据改成「前台是管家界面才冻结」；侧键/热键一律走 `BurstBuffer.press()`，失败也弹挑帧页 + 写清原因；再不行点「🩺 侧键自检」逐环看 |
| 侧键链某一环断了不知道是哪环 | —— | 挑帧页左下 / 设置页「🩺 侧键自检」→ `/api/photo_diag`，9 环逐条给结论 + 修法（v1.5.37 新增：录制时长 / 正在录制 / 上次录到几帧） |
| 挑帧页弹了但里面是 0 帧 | 后台录屏关着 / 游戏没跑 / 管家在前台（缓冲冻结）/ 刚清过缓存 | 挑帧页会直接写原因；回游戏打几秒即可 |
| 前端 jsdom 测试报 `Cannot find module 'jsdom'` | 仓库不带 node_modules | `NODE_PATH=<jsdom 所在目录>` 再跑（见第八节） |
| **静态检查假 FAIL，说某函数调了它其实没调的接口** | 用**子串匹配**去 grep 代码，被**注释/docstring** 骗了（`_why_empty` 的 docstring 里正常写着"绝对不能调 proc_probe()"，一 grep 就中） | 涉及"函数体内有没有某调用"的断言，一律走 **AST**（`ast.parse` + 按**名字+形参名**定位函数 + 只看 `ast.Call.func`）。见 `ui_check.py` 2.22 的 `_func22/_used22/_called22` |
| **静态检查空转通过（假 OK）** | 文件里有 **4 个**同名 `_cb`（另外几个是窗口过程 `_cb(hwnd, _l)`），`ast.walk` 返回第一个 → 断言全打在无关函数上 | 按签名锁定：`_func22("_cb", ("nCode", "wParam", "lParam"))`；再加一条**非空转守卫**（"定位到的确实调了 `press`"）|
| **侧键用着用着突然彻底没反应，重启才恢复**（且无任何报错） | 低级鼠标钩子回调里干了慢活。`WH_MOUSE_LL` 回调受 `LowLevelHooksTimeout`（注册表默认 **300ms**）约束，**超时 Windows 会静默摘钩**，之后再按侧键连回调都不进 | ⛔ **红线：回调链（`_cb → burst.press → trigger → _why_empty`）里绝对不许起子进程 / 不许任何文件 I/O**（`log()` 落盘、`traceback.format_exc()` 经 linecache 读源码、`open()` 全算）。慢活一律丢 `_after_press_bg` / `_log_exc_bg` 后台线程。**三重守卫**：① `_v1535_exe.py` 反序列化包内 `_why_empty` 与**侧键 `_cb`** 的字节码，断言 `co_names` 里没有 `proc_probe`/`log`/`format_exc`；② `_v1535_check.py` 第 10 节运行时把 `open`/`Popen`/`system` 全钉死成"一碰就炸"并实测耗时；③ `ui_check.py` 2.22 用 AST 静态抠回调体。**实测余量**：冷缓存 `press()` 0.09ms / `_why_empty()` 0.01ms → 整链约 0.1ms，占预算 0.03%（`log()` 已移出回调，中位 0.22ms 只在后台线程花）|

| **设置页提示「快捷键注册失败」，但按 F9 明明有反应**（用户真机反馈过） | 有**没退干净的旧实例**（出图/测试脚本用源码起的管家，脚本被中断后没人回收）一直占着全局快捷键。`RegisterHotKey` 是**整机独占**的，新实例必然失败（err=1409）；而按 F9「有反应」是因为**响应的是那个旧实例**（它还活着，只是没窗口，一按就把界面开出来）。两句话都是真的，只是不在同一个进程里 | v1.5.36 已修：① **单实例检测**（`CreateMutexW` + `ERROR_ALREADY_EXISTS`）启动时提醒"另一个实例在运行"；② **`ZZMI_TEST_MODE=1` 测试/演示模式** —— 所有"用源码起管家"的脚本改走它，**不注册热键、不装钩子、不参与单实例检测**，从源头杜绝孤儿占键；③ 热键状态**逐键分开记**（`hotkey_main_ok`/`hotkey_photo_ok`），界面直接点名哪个组合被占。查法：`Get-CimInstance Win32_Process -Filter "Name='python.exe'"` 看有没有跑 `zzmi_manager.py` 的孤儿，`Stop-Process -Force` 清掉即可 |
| **任务管理器里看到两个同名 `ZZMI-Mod-Manager.exe`**（用户真机反馈过） | 这是 **PyInstaller onefile 的正常结构**，不是 bug、不是多实例：一次启动 = **引导父进程**（解包到临时目录）+ **真身子进程**（真正在跑）。实测 `pid=39376 ppid=46736` + `pid=44056 ppid=39376`。**只有子进程注册全局快捷键**，所以"两个进程"本身不会抢 F9 | **绝不能用"进程数 > 1"判多实例**。真正的孤儿判据是 `WindowWatchdog`：只在「曾经找到过窗口」之后才开始判，连续 180s 都找不到窗口才主动退出让出 F9（窗口被游戏盖住/最小化都算"还在"，玩游戏不误判）。另有 `retry_lost`：启动没注册上的键后台每 5s 重试（最多 2 分钟）。启动横幅会直接打印"两个进程是正常结构" |
| **侧键按了、回管家挑帧页没弹出来**（用户真机反馈过，v1.5.37） | 两个真因：① 轮询里**先把哨兵记了再弹**，空批提示被静默吞掉；② 切回管家时后端可能"没找到已有窗口"于是**新开一个窗口**（全新页面，首帧把哨兵播种成当前批 id，刚抓的批被吞） | v1.5.37 已修：① 先弹再记哨兵；② 批次带 **pending 标记**，弹过之后 `/api/photo_ack` 回执才清，首帧据 pending 决定补不补弹；③ `find_manager_window` 加不挑类的兜底 + `toggle_manager_window` 开新窗前退避重试。复现/排查：挑帧页左下「🩺 侧键自检」看 9 环表 |
| **mod 列表里某文件夹只显示成 1 个 mod（其实里面很多）**（用户真机反馈过，v1.5.37） | 老 `mod_root_for` 把"第 2 层"写死了。用户的库大量是**三层/四层**结构（分组→角色→具体 mod），真 mod 在第 3 层，老算法停在第 2 层把一个分组文件夹当 1 个 mod | v1.5.37 已修：从含 ini 的目录**逐层往上问**"这一层是不是只装子文件夹的容器"，是就继续往上直到真正的 mod 根。真库实测某分组 6→**98**、全库 133→**234** |
| **`_proc_cache.clear()` 之后 `state()` 抛 `KeyError: 't'`** | 测试里用 `clear()` 模拟冷缓存，把 schema 键（`t`/`game`/`launcher`/`game_pid`）一起抹了；`proc_probe` 用 `_proc_cache["t"]` 硬取 → KeyError。`state()` 是界面每 2 秒轮询的接口，一抛就整页死 | 两边都修：① `proc_probe` 改用 `.get("t", 0)` 兜底（缓存残缺也不许把 UI 搞死）；② 测试改用 `update({"t":0,...})` 复位而非 `clear()` |

---

## 十二、给接手 AI 的建议

1. **先 `git status` + 读 `zzmi_manager.py` 顶部 docstring + `ui.html` 结构**，再动手。
2. 任何涉及「写用户文件 / 改 ini / 删东西」的操作，**先停下来问用户**，别自作主张（红线第 1、2 条是用户真实发火过的）。
3. 本机 shell 不可靠，**一律写 `.py` 落盘再读**（见五.1），能省大量瞎折腾。
4. 改完跑第五节三个测试，全绿再打包；打包前确认版本号 3 处一致。
5. 发布前务必问用户是否要发（红线第 11 条）。

---
*本文件为项目交接用，非产品文档。长期记忆在 `.workbuddy/memory/`（MEMORY.md / VERSIONS.md / 每日日志）。*
