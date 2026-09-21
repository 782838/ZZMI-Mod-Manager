# -*- coding: utf-8 -*-
"""用系统自带浏览器(无头)渲染验证界面: JS 语法检查 + DOM 渲染 + 截图。"""
import os, re, subprocess, sys, json, time

HERE = os.path.dirname(os.path.abspath(__file__))
NODE = r"C:\Users\<你的用户名>\.workbuddy\binaries\node\versions\22.22.2-3\node.exe"
UI = os.path.join(HERE, "..", "ui.html")
OUT = os.path.join(HERE, "_ui_check.txt")
L = []
def w(s=""):
    L.append(str(s)); print(s)

URL = open(os.path.join(os.path.expanduser("~"), ".zzmi-manager", "last_url.txt")).read().strip()
w("URL = " + URL)

# ---------- 1. 找浏览器 ----------
BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
]
browser = next((b for b in BROWSERS if os.path.isfile(b)), None)
w("browser = " + str(browser))
if not browser:
    w("没找到浏览器, 跳过渲染验证")
    open(OUT, "w", encoding="utf-8").write("\n".join(L))
    sys.exit(0)

# ---------- 2. 抽出内联 JS 做语法检查 ----------
html = open(UI, "r", encoding="utf-8").read()
m = re.search(r"<script>(.*)</script>", html, re.S)
assert m, "找不到 <script> 块"
js = m.group(1)
jsp = os.path.join(HERE, "_ui_extracted.js")
open(jsp, "w", encoding="utf-8").write(js)
w(f"抽出内联 JS: {len(js)} 字符")
r = subprocess.run([NODE, "--check", jsp], capture_output=True, text=True, encoding="utf-8", errors="replace")
w("node --check -> rc=%d" % r.returncode)
if r.returncode != 0:
    w(r.stdout or ""); w(r.stderr or "")
assert r.returncode == 0, "内联 JS 有语法错误!"
w("  JS 语法检查通过")

# 只出现一次的 DOM id 检查(抓拼写错误)
ids_html = set(re.findall(r'id="([^"]+)"', html))
refs = set(re.findall(r'\$\("#([A-Za-z0-9_\-]+)"\)', js))
missing = sorted(r for r in refs if r not in ids_html)
w("JS 里引用但不存在的元素 id: %s" % (missing or "无"))
assert not missing, "有 JS 引用了不存在的元素: %s" % missing
# 函数引用检查
fn_def = set(re.findall(r"(?:async\s+)?function\s+([A-Za-z0-9_]+)", js))
inline_calls = set(re.findall(r'onclick="([A-Za-z0-9_]+)\(', html)) | \
               set(re.findall(r'oninput="([A-Za-z0-9_]+)\(', html))
missing_fn = sorted(c for c in inline_calls if c not in fn_def)
w("HTML 内联事件里调用但未定义的函数: %s" % (missing_fn or "无"))
assert not missing_fn, "内联事件调用了未定义的函数: %s" % missing_fn

# ---------- 2.5 v1.5.4 新功能静态检查(改键 / 删仓库) ----------
static_checks = [
    ("改键按钮已挂到变体提示行", 'data-rekey="' in html),
    ("改键走 /api/cycle_rekey", "cycle_rekey" in html),
    ("改键输入框预填当前绑定", "keys_raw" in html),
    ("下拉里有仓库管理入口", "__libmgr__" in html and "仓库管理" in html),
    ("仓库管理弹窗存在", 'id="libmgr"' in html),
    ("删除走 /api/del_lib", "del_lib" in html),
    ("删除弹窗声明不动磁盘文件", "一个都不会删" in html),
    ("旧『只读不改文件』文案已下线", "工具不会改你的文件" not in html),
]
w()
w("=== v1.5.4 静态检查 ===")
sbad = []
for name, ok in static_checks:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        sbad.append(name)
assert not sbad, "v1.5.4 静态检查失败: %s" % sbad

# ---------- 2.6 v1.5.5 新功能静态检查(添加/锁定仓库) ----------
static_checks2 = [
    ("仓库管理面板有『添加仓库』输入框", 'id="lmName"' in html),
    ("有『在 ZZMI 下新建』按钮", 'id="lmNewRoot"' in html),
    ("有『手动寻找仓库路径』按钮", 'id="lmFind"' in html and "手动寻找仓库路径" in html),
    ("添加走 /api/add_lib", "add_lib" in html),
    ("仓库页空态给了手动寻找入口", 'id="libFind"' in html),
    ("空态文案仍是『还没发现仓库目录』", "还没发现仓库目录" in html),
    ("搬运下拉含锁定的仓库入口", "锁定的其它位置" in html and "libs_abs" in html),
    ("锁定/自定义文件夹会带上 abs: 前缀", 'stripAbs' in html),
    ("仓库管理入口文案已更新", "仓库管理 / 添加仓库…" in html),
]
w()
w("=== v1.5.5 静态检查 ===")
sbad2 = []
for name, ok in static_checks2:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        sbad2.append(name)
assert not sbad2, "v1.5.5 静态检查失败: %s" % sbad2

# ---------- 2.7 v1.5.6 新功能静态检查(改名失败 → 手动 DISABLED_ 教程弹窗) ----------
static_checks3 = [
    ("有手动处理教程弹窗 #mManual", 'id="mManual"' in html),
    ("弹窗有正文容器 #mmBody", 'id="mmBody"' in html),
    ("有一键复制按钮 #mmCopy", 'id="mmCopy"' in html and "复制 DISABLED_" in html),
    ("有『去改名』跳转按钮 #mmOpen", 'id="mmOpen"' in html),
    ("有 showManualHelp 教程函数", "function showManualHelp(" in html),
    ("有 hasRenameFail 判定函数", "function hasRenameFail(" in html),
    ("有 copyText 剪贴板降级实现", "async function copyText(" in html
                                    and "execCommand" in html),
    ("教程区分占用/无权限两种原因", "denied:" in html and "busy:" in html
                                    and "whyMap" in html),
    ("教程教『加上 DISABLED_』", "在文件夹名前加上" in html),
    ("教程教『删掉 DISABLED_』", "删掉" in html and "DISABLED_" in html),
    ("去改名会跳到文件夹(走 /api/openroot)", '/api/openroot' in html
                                              and "mmPath" in html),
    ("跳转时传 select:true 让资源管理器选中它", "select: true" in html),
    ("批量/全选/套用方案都接了教程", "hasRenameFail([d])" in html
                                     and "r.failed || []" in html.replace("(r.failed || [])", "r.failed || []")),
]
w()
w("=== v1.5.6 静态检查 ===")
sbad3 = []
for name, ok in static_checks3:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        sbad3.append(name)
assert not sbad3, "v1.5.6 静态检查失败: %s" % sbad3

# ---------- 2.8 v1.5.7 新功能静态检查(隐藏命令窗口) ----------
static_checks4 = [
    ("设置里有『显示命令窗口』按钮", 'id="btnConsole"' in html),
    ("按钮走 /api/console", '/api/console' in html),
    ("设置里说明了日志落盘位置", "zzmi.log" in html),
    ("退出提示不再说『关掉黑色控制台窗口』", "关掉那个黑色控制台窗口" not in html),
]
w()
w("=== v1.5.7 静态检查 ===")
sbad4 = []
for name, ok in static_checks4:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        sbad4.append(name)
assert not sbad4, "v1.5.7 静态检查失败: %s" % sbad4

# ---------- 2.9 v1.5.8 新功能静态检查(重名自动加序号) ----------
static_checks5 = [
    ("有重名提示弹窗 #mDup", 'id="mDup"' in html),
    ("弹窗有正文容器 #mdBody", 'id="mdBody"' in html),
    ("有 showDupNotice 函数", "showDupNotice(" in html),
    ("提示里说明『自动加序号』", "自动加了个序号" in html or "自动加了序号" in html),
    ("提示里写了『依次类推』的口径", "依次类推" in html),
    ("doToggle 接了 f.renamed", "f.renamed" in html),
    ("套用方案接了 r.renamed", "r.renamed" in html),
    ("重命名弹窗带了 orig_name/target_name", "orig_name" in html and "target_name" in html),
    ("提示说明原来的文件夹没被动过", "一个都没动过" in html),
]
w()
w("=== v1.5.8 静态检查 ===")
sbad5 = []
for name, ok in static_checks5:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        sbad5.append(name)
assert not sbad5, "v1.5.8 静态检查失败: %s" % sbad5

# ---------- 2.10 v1.5.9 静态检查(绝区零图标 favicon) ----------
static_checks6 = [
    ("页面声明了 favicon", 'rel="icon"' in html),
    ("favicon 指向 /favicon.ico", "/favicon.ico" in html),
]
w()
w("=== v1.5.9 静态检查 ===")
sbad6 = []
for name, ok in static_checks6:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        sbad6.append(name)
assert not sbad6, "v1.5.9 静态检查失败: %s" % sbad6

# ---------- 2.11 v1.5.10 静态检查(自制输入弹窗 + 界面关闭自动退出) ----------
static_checks7 = [
    ("有自制输入弹窗 #mAsk", 'id="mAsk"' in html),
    ("输入弹窗有输入框 #mAskInput", 'id="mAskInput"' in html),
    ("弹窗标题是 ZZMI MOD 管家", "ZZMI MOD 管家" in html),
    ("定义了 ask() 输入函数", "function ask(" in html),
    ("界面关闭监听 pagehide", "pagehide" in html),
    ("关闭时通知后端 /api/bye", "/api/bye" in html),
    ("页面加载时打招呼 /api/hello", "/api/hello" in html),
    ("更新提醒加了先关程序提示", "更新时请先关闭本程序" in html),
]
w()
w("=== v1.5.10 静态检查 ===")
sbad7 = []
for name, ok in static_checks7:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        sbad7.append(name)
assert not sbad7, "v1.5.10 静态检查失败: %s" % sbad7

# ---------- 2.12 v1.5.11 静态检查(弹窗深色主题修复 + 卡片重命名按钮) ----------
ask_css = html[html.find(".ask-msg{"):html.find(".ask-input:focus")]
static_checks8 = [
    ("ask-msg 文字色用主题色 --txt", ".ask-msg{" in html and "color:var(--txt)" in ask_css),
    ("ask-msg 不再用按钮黑字 --ink", "color:var(--ink)" not in ask_css),
    ("ask-input 文字色用主题色 --txt", "color:var(--txt)" in html[html.find(".ask-input{"):html.find(".ask-input:focus")]),
    ("卡片有重命名按钮 data-act=rename", 'data-act="rename"' in html),
    ("重命名走共用函数 renameMod", "async function renameMod(" in html),
    ("事件分发处理 rename", 'act === "rename"' in html),
]
w()
w("=== v1.5.11 静态检查 ===")
sbad8 = []
for name, ok in static_checks8:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        sbad8.append(name)
assert not sbad8, "v1.5.11 静态检查失败: %s" % sbad8

# ---------- 2.13 v1.5.12 静态检查(GameBanana 下载区) ----------
static_checks9 = [
    ("顶栏有『下载区』入口 #btnGB", 'id="btnGB"' in html and "下载区" in html),
    ("下载区面板 #mGB 存在", 'id="mGB"' in html),
    ("下载区结果网格 #gbGrid", 'id="gbGrid"' in html),
    ("URL 输入框 #gbUrl + 爬取按钮 #gbGo", 'id="gbUrl"' in html and 'id="gbGo"' in html),
    ("爬取走 /api/gb_crawl", "/api/gb_crawl" in html),
    ("一键下载走 /api/gb_download", "/api/gb_download" in html),
    ("下载进度轮询 /api/gb_dl", "/api/gb_dl?job=" in html),
    ("有中文译名开关 #gbTr", 'id="gbTr"' in html),
    ("翻译走 /api/gb_translate", "/api/gb_translate" in html),
    ("预览图走 /gbimg 代理", "/gbimg?" in html),
    ("有下载目录弹窗 #mGBdl", 'id="mGBdl"' in html),
    ("下载目录走 /api/gb_downloads", "/api/gb_downloads" in html),
    ("可改下载目录 /api/gb_set_dl_dir", "/api/gb_set_dl_dir" in html),
    ("有 gbCrawl / gbDownload 函数", "function gbCrawl(" in html and "function gbDownload(" in html),
]
w()
w("=== v1.5.12 静态检查 ===")
sbad9 = []
for name, ok in static_checks9:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        sbad9.append(name)
assert not sbad9, "v1.5.12 静态检查失败: %s" % sbad9

# ---------- 2.14 v1.5.13 静态检查(角色分类 + 选择性下载 + 下载记录) ----------
static_checks10 = [
    ("有角色下拉 #gbSub", 'id="gbSub"' in html),
    ("有角色刷新按钮 #gbSubReload", 'id="gbSubReload"' in html),
    ("有角色提示 #gbSubInfo", 'id="gbSubInfo"' in html),
    ("角色列表走 /api/gb_subs", "/api/gb_subs" in html),
    ("爬取带 cat 参数", '&cat=' in html and 'gbS.cat' in html),
    ("选了角色不用填链接", 'if (!url && !gbS.cat)' in html),
    ("函数 gbLoadSubs / gbFillSubs / gbPickSub", all(('function %s(' % n) in html for n in ('gbLoadSubs','gbFillSubs','gbPickSub'))),
    ("有列出文件开关 #gbFilesTog", 'id="gbFilesTog"' in html),
    ("文件区用 data-fbox / data-fpick", ('data-fbox=' in html) and ('data-fpick=' in html) and ('esc(key)' in html)),
    ("文件清单走 /api/gb_files", "/api/gb_files" in html),
    ("函数 gbLoadFiles / gbRefreshFileBoxes", ('function gbLoadFiles(' in html and 'function gbRefreshFileBoxes(' in html)),
    ("勾选状态由 gbPicks 汇总", 'function gbPicks(' in html),
    ("下载请求带 picks", 'picks: picks || null' in html),
    ("一个都没勾会拦住", '一个文件都没勾' in html),
    ("有全选/全不选", 'data-all="' in html and 'data-none="' in html),
    ("已下载标记 .gbreg + gbApplyHist", '.gbreg' in html and 'function gbApplyHist(' in html),
    ("历史走 /api/gb_history", "/api/gb_history" in html),
    ("清记录走 /api/gb_hist_clear", "/api/gb_hist_clear" in html),
    ("有清空记录按钮 #gbDlClearHist", 'id="gbDlClearHist"' in html),
    ("有选择文件夹按钮 #gbDlPick", 'id="gbDlPick"' in html),
    ("选择文件夹走 /api/pick_dir", "/api/pick_dir" in html),
    ("下载目录有统计 #gbDlStat", 'id="gbDlStat"' in html),
]
w()
w("=== v1.5.13 静态检查 ===")
sbad10 = []
for name, ok in static_checks10:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        sbad10.append(name)
assert not sbad10, "v1.5.13 静态检查失败: %s" % sbad10

# ---------- 2.15 v1.5.14 静态检查(角色中文名 + 选框/开目录修复) ----------
static_checks11 = [
    ("角色下拉显示中文名 cn", 'x.cn' in html),
    ("中文名排在英文前", 'cn + " · " + x.name' in html),
    ("无中文时回落英文名", '(x.name + " (" + x.count + ")")' in html),
]
w()
w("=== v1.5.14 静态检查 ===")
sbad11 = []
for name, ok in static_checks11:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        sbad11.append(name)
assert not sbad11, "v1.5.14 静态检查失败: %s" % sbad11

# ---------- 2.16 v1.5.15 静态检查(引号路径 + 选完即生效 + 反馈可见) ----------
static_checks12 = [
    ("选择完自动生效(set_dl_dir)", 'gb_set_dl_dir", { path: r.path }' in html),
    ("选择中按钮置灰", 'btn.disabled = true' in html and '选择中…' in html),
    ("选择框提示 Alt+Tab", 'Alt+Tab' in html),
    ("打开目录成功也提示", '已打开下载目录: ' in html),
    ("改路径先问是否恢复默认", '要恢复成默认下载目录吗' in html),
    ("设置中按钮置灰", '设置中…' in html),
]
w()
w("=== v1.5.15 静态检查 ===")
sbad12 = []
for name, ok in static_checks12:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        sbad12.append(name)
assert not sbad12, "v1.5.15 静态检查失败: %s" % sbad12

# ---------- 2.13 v1.5.22 静态检查(文件名翻译 + 蓝飞机暂时关闭) ----------
static_checks13 = [
    ("有文件名翻译接口调用 /api/gb_translate_files", "/api/gb_translate_files" in html),
    ("有 gbTranslateFiles 函数", "function gbTranslateFiles(" in html),
    ("文件行有译名占位 .zfn + data-fen", 'data-fen=' in html and 'class="zfn off"' in html),
    ("gbApplyTr 里应用文件名译名", "gbS.trFMap" in html and "zfn" in html),
    ("蓝飞机 tab 有 id 供隐藏", 'id="gbTgTab"' in html),
    ("renderAll 按 tg_enabled 隐藏蓝飞机 tab", "S.tg_enabled === false" in html and "gbTgTab" in html),
    ("点蓝飞机 tab 在关闭时短路", 'S.tg_enabled === false) return' in html or 'tg_enabled === false){ return' in html),
]
w()
w("=== v1.5.22 静态检查 ===")
sbad13 = []
for name, ok in static_checks13:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        sbad13.append(name)
assert not sbad13, "v1.5.22 静态检查失败: %s" % sbad13

# 后端侧静态断言(直接读主程序源码文件)
try:
    zsrc = open(os.path.join(os.path.dirname(HERE), "zzmi_manager.py"),
                encoding="utf-8").read()
except Exception:
    zsrc = ""
static_checks13b = [
    ("后端有 TG_ENABLED 开关且为 False", "TG_ENABLED = False" in zsrc),
    ("后端有文件名清洗翻译函数 _gb_trans_clean_map", "def _gb_trans_clean_map(" in zsrc),
    ("后端有文件名清洗 _gb_trans_prep", "def _gb_trans_prep(" in zsrc),
    ("POST 拦截 tg_* 关闭", 'act.startswith("tg_") and not TG_ENABLED' in zsrc),
    ("GET /api/tg_status 关闭拦截", 'path == "/api/tg_status"' in zsrc and "not TG_ENABLED" in zsrc),
    ("state 暴露 tg_enabled", '"tg_enabled": bool(TG_ENABLED)' in zsrc),
]
w()
w("=== v1.5.22 后端静态检查 ===")
sbad13b = []
for name, ok in static_checks13b:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        sbad13b.append(name)
assert not sbad13b, "v1.5.22 后端静态检查失败: %s" % sbad13b

# ---------- 2.14 v1.5.23 静态检查(文件行竖排修复 + 底部翻页条) ----------
static_checks14 = [
    (".gbfile 允许换行(否则 .zfn basis:100% 把文件名挤成竖排)",
     re.search(r"\.gbfile\{[^}]*flex-wrap:wrap", html) is not None),
    (".fn 可收缩不抢宽度", re.search(r"\.gbfile \.fn\{[^}]*flex:1 1 auto", html) is not None),
    ("有底部翻页条 #gbPagerBtm", 'id="gbPagerBtm"' in html),
    ("顶部+底部按钮共用 .gbPrev/.gbNext 类(两套同步)",
     html.count('class="btn gbPrev"') >= 2 and html.count('class="btn gbNext"') >= 2),
    ("页码两处同步由 gbPager 统一处理", "function gbPager(" in html and '$$("#gbBananaPane .gbPage")' in html),
    ("翻页后自动回列表顶部", "function gbScrollTop(" in html and "gbScrollTop();" in html),
]
w()
w("=== v1.5.23 静态检查 ===")
sbad14 = []
for name, ok in static_checks14:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        sbad14.append(name)
assert not sbad14, "v1.5.23 静态检查失败: %s" % sbad14

# ---------- 2.15 v1.5.24 静态检查(重命名失败也弹手动教程) ----------
static_checks15 = [
    ("弹窗认得改名模式(f.rename 分流)", "const isRen = !!f.rename;" in html),
    ("有「重命名失败, 得手动来一下」标题", "重命名失败, 得手动来一下" in html),
    ("改名失败时弹教程而不是只甩 toast", "showManualHelp(r.manual" in html),
    ("有「复制新名字」按钮文案", "复制新名字" in html),
    ("后端改名被拒时交回手动信息", '"reason": lock_reason_kind(msg), "rename": True' in zsrc),
    ("后端 /api/rename 透传 manual 信息", 'out["manual"] = extra' in zsrc),
]
w()
w("=== v1.5.24 静态检查 ===")
sbad15 = []
for name, ok in static_checks15:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        sbad15.append(name)
assert not sbad15, "v1.5.24 静态检查失败: %s" % sbad15

# ---------- 2.16 v1.5.28 静态检查(段头备注变体 + 搜索框禁自动填充) ----------
static_checks16 = [
    ("后端有 _ini_section 段头解析(容忍 ]后面跟备注)", "def _ini_section(" in zsrc),
    ("parse_cycle_vars 用 _ini_section", "sec = _ini_section(st)" in zsrc),
    ("段头备注当变体中文名(sec_note)", 'sec_note = st[st.find("]") + 1:].strip()' in zsrc),
    ("备注优先于内置翻译表", "label_cn = sec_note or CYCLE_LABEL_CN" in zsrc),
    ("no_* 排除修饰符映射为 !X 显示", '("no_alt", "!Alt")' in zsrc),
    ("过滤角色框禁掉 Edge 自动填充", 'id="charFilter"' in html and 'id="charFilter" placeholder="🔍 过滤角色…" autocomplete="off"' in html),
    ("主搜索框禁掉 Edge 自动填充", '<input id="q" placeholder="搜索 mod / 角色 / 路径  (按 / 聚焦)" autocomplete="off"' in html),
]
w()
w("=== v1.5.28 静态检查 ===")
sbad16 = []
for name, ok in static_checks16:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        sbad16.append(name)
assert not sbad16, "v1.5.28 静态检查失败: %s" % sbad16

# ---------- 2.17 v1.5.29 静态检查(屏蔽 Edge 超级拖放搜索条) ----------
static_checks17 = [
    ("有 _disable_edge_super_drag 函数", "def _disable_edge_super_drag(" in zsrc),
    ("开窗口前写专属 profile 的 pref", "_disable_edge_super_drag(prof)" in zsrc),
    ("pref 键名正确(edge_super_drag_drop.enabled)", '"edge_super_drag_drop"' in zsrc and "enabled" in zsrc),
    ("启动参数也关掉该 feature", "msEdgeSuperDragDropSupported" in zsrc),
]
w()
w("=== v1.5.29 静态检查 ===")
sbad17 = []
for name, ok in static_checks17:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        sbad17.append(name)
assert not sbad17, "v1.5.29 静态检查失败: %s" % sbad17


# 先确认服务真的还活着 —— last_url.txt 记的是"上一次启动"的端口, 进程一关就是死链,
# 浏览器会安静地渲染出 Edge 的"拒绝连接"错误页, 让渲染校验全部假 FAIL(踩过)。
# 所以这里先探一下, 连不上就直接跳过渲染校验, 而不是拿错误页去判界面坏了。
def _alive(u, tries=3):
    import urllib.request
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for _ in range(tries):
        try:
            with opener.open(u, timeout=6) as resp:
                return 200 <= getattr(resp, "status", 200) < 400
        except Exception:
            time.sleep(0.6)
    return False

if not _alive(URL):
    w("")
    w("!! 服务不在线(%s), 跳过渲染校验。" % URL)
    w("   (last_url.txt 指向的上一次实例已经退出了)")
    w("   要跑渲染校验, 请用 live_check.py —— 它会自己起服务再调本脚本。")
    w("")
    open(OUT, "w", encoding="utf-8").write("\n".join(L))
    sys.exit(0)

prof = os.path.join(HERE, "_chrome_prof")
os.makedirs(prof, exist_ok=True)
domp = os.path.join(HERE, "_dom.html")
common = [browser, "--headless=new", "--disable-gpu", "--no-first-run",
          "--no-default-browser-check", "--disable-extensions",
          # 本地地址不走系统代理, 否则 127.0.0.1 可能被拦截导致拿不到 DOM
          "--proxy-server=direct://", "--proxy-bypass-list=<-loopback>",
          "--user-data-dir=" + prof, "--virtual-time-budget=8000",
          "--run-all-compositor-stages-before-draw"]
try:
    r = subprocess.run(common + ["--dump-dom", URL], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=120)
    dom = r.stdout or ""
except Exception as ex:
    dom = ""
    w("dump-dom 失败: %r" % ex)
open(domp, "w", encoding="utf-8").write(dom)
w(f"dump-dom 输出 {len(dom)} 字符, stderr={len(r.stderr or '')} 字符")

# 拿到的如果不是我们的界面, 而是浏览器自带的错误页, 直接说清, 别让后面 12 条全红
if ("拒绝连接" in dom or "ERR_CONNECTION" in dom or "无法访问此网站" in dom
        or "ZZMI Mod 管家" not in dom):
    w("")
    w("!! 抓到的不是界面(像是浏览器错误页/空白页), 中止渲染校验。")
    w("   DOM 前 300 字符: " + dom[:300].replace("\n", " "))
    open(OUT, "w", encoding="utf-8").write("\n".join(L))
    sys.exit(1)
if r.stderr and r.stderr.strip():
    errs = [ln for ln in r.stderr.splitlines()
            if re.search(r"error|exception|uncaught|failed", ln, re.I)]
    w("浏览器 stderr 里的可疑行(前 12 条):")
    for ln in errs[:12]:
        w("   " + ln[:200])

# ---------- 4. 校验渲染结果 ----------
def has(s):
    return s in dom

checks = [
    ("标题渲染", "ZZMI Mod 管家" in dom),
    ("顶栏按钮", "启动游戏" in dom and "撤销" in dom and "仓库" in dom),
    ("统计已填充", "个 mod" in dom),
    ("卡片已渲染", dom.count('class="card') > 10),
    ("出现真实 mod 名-佩洛伊斯替换暗影", has("佩洛伊斯替换暗影")),
    ("出现真实 mod 名-安比", has("安比")),
    ("出现真实 mod 名-雅", has(">雅<")),
    # 分类维度 = 顶层文件夹名(用户明确要求过: 不要再改成性别分组)
    ("分类树已渲染-顶层文件夹分类", has("1a全女合集") or has("功能")),
    ("分类未被改成性别分组", not (has("女角色") or has("男角色"))),
    ("冲突提示条已出现", "hash 重叠" in dom),
    ("路径 chip 已显示", "F:\\MOD\\ZZMI\\Mods" in dom or "F:/MOD/ZZMI/Mods" in dom),
    ("预览图 img 标签已生成", dom.count("/thumb?") > 5),
    ("未残留 BOOT 占位符", "__BOOT__" not in dom),
    ("未出现未捕获异常字样", "NaN" not in re.sub(r"<script.*?</script>", "", dom, flags=re.S)),
    ("顶栏出现下载区按钮", has("下载区") and has('id="btnGB"')),
    ("下载区面板已渲染进 DOM", has('id="mGB"') and has('id="gbGrid"')),
]
w()
w("=== 渲染校验 ===")

# 没有扫到任何 mod(例如本机没配 Mods 路径)时, "卡片/真实mod名/分类树/缩略图"
# 这几条必然 FAIL —— 那是环境没数据, 不是界面坏了。这种情况直接说清并跳过,
# 别拿空数据当红报(会让静态检查的结论也被淹没)。
_total = 0
try:
    import urllib.request as _ur
    _op = _ur.build_opener(_ur.ProxyHandler({}))
    with _op.open(URL.replace("/?t=", "/api/state?t="), timeout=10) as _resp:
        _total = int(json.loads(_resp.read().decode("utf-8"))["stats"]["total"])
except Exception:
    pass
w("服务扫到的 mod 数 = %d" % _total)
DATA_DEPENDENT = {
    "卡片已渲染", "出现真实 mod 名-佩洛伊斯替换暗影", "出现真实 mod 名-安比",
    "出现真实 mod 名-雅", "分类树已渲染-顶层文件夹分类", "预览图 img 标签已生成",
}
if _total <= 0:
    w("!! 服务端没有任何 mod(本机未配置 Mods 路径), 与数据相关 %d 条校验跳过。" % len(DATA_DEPENDENT))
    w("   界面骨架类校验仍然有效。")
    checks = [(n, o) for (n, o) in checks if n not in DATA_DEPENDENT]

bad = []
for name, ok in checks:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        bad.append(name)

# 统计卡片数
w()
w("卡片数量(含 list 变体) = %d" % dom.count('class="card '))
w("缩略图 <img> 数量 = %d" % dom.count("/thumb?"))
w("侧栏分类项数量 = %d" % dom.count('class="navi on"') )
m2 = re.search(r'id="cAll"[^>]*>(\d+)<', dom)
w("侧栏 全部Mod 计数 = %s" % (m2.group(1) if m2 else "?"))

# ---------- 5. 截图 ----------
shot = os.path.join(HERE, "..", "screenshots", "界面预览-深色.png")
try:
    r2 = subprocess.run(common + ["--screenshot=" + shot, "--window-size=1680,1000", URL],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace", timeout=120)
    ok = os.path.isfile(shot) and os.path.getsize(shot) > 20000
    w("截图 -> %s (%d bytes) rc=%d" % (shot, os.path.getsize(shot) if os.path.isfile(shot) else 0, r2.returncode))
    assert ok, "截图为空"
except Exception as ex:
    w("截图失败: %r" % ex)

w()
if bad:
    w("RENDER CHECK FAILED: " + ", ".join(bad))
else:
    w("RENDER CHECK PASSED")
open(OUT, "w", encoding="utf-8").write("\n".join(L))
sys.exit(1 if bad else 0)
