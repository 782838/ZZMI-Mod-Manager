# -*- coding: utf-8 -*-
"""用系统自带浏览器(无头)渲染验证界面: JS 语法检查 + DOM 渲染 + 截图。"""
import os, re, subprocess, sys, json, time

HERE = os.path.dirname(os.path.abspath(__file__))
# Node 路径: 测试者本机 NODE_PATH/系统 PATH 里的 node.exe 即可, 不绑绝对路径
NODE = "node"
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

# ---------- 2.18 v1.5.30 静态检查(卡片删除按钮 = 二次确认移入回收站) ----------
static_checks18 = [
    ("卡片有红色删除按钮(data-act=del)", 'data-act="del"' in html and "🗑 删除" in html),
    ("删除按钮排在开关左边", html.find('data-act="del"') < html.find('data-act="toggle"')),
    ("第一道确认: 真的要删除吗", "真的要删除" in html),
    ("第二道确认: 提醒移入回收站可还原", "移入回收站" in html and "还原" in html),
    ("确认框支持标红按钮(danger)", 'ok.classList.toggle("danger"' in html),
    ("后端只走回收站(FOF_ALLOWUNDO)", "0x0040" in zsrc and "SHFileOperationW" in zsrc),
    ("后端有越界安全闸", "不在 Mods 目录里" in zsrc),
    ("API 有 mod_delete 路由", 'act == "mod_delete"' in zsrc),
]
w()
w("=== v1.5.30 静态检查 ===")
sbad18 = []
for name, ok in static_checks18:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        sbad18.append(name)
assert not sbad18, "v1.5.30 静态检查失败: %s" % sbad18

# ---------- 2.19 v1.5.31 静态检查(连拍缓冲 + 照片墙) ----------
static_checks19 = [
    ("后端有 BurstBuffer 环形缓冲", "class BurstBuffer" in zsrc and "TARGET_FPS" in zsrc),
    ("只在游戏运行时录屏", "game, _ = proc_probe(cfg)" in zsrc),
    # v1.5.32 把「去重成最多 16 张代表帧」升级成五层金字塔: 去重逻辑从 _dedup
    # 搬进了 _thin(按 _hdiff 算的新颖度挑代表帧)。这里跟着改, 断言「按差异挑代表帧」
    # 这件事仍然成立 —— 常量 TIERS 与 _tiers 由下面 2.20 覆盖, 不重复。
    ("代表帧按差异去重(_thin)", "def _thin" in zsrc and "def _hdiff" in zsrc),
    ("留这张才落盘", "def keep(self, idx)" in zsrc and "PHOTO_DIR" in zsrc),
    ("照片删除也走回收站", 'act == "photo_del"' in zsrc and "recycle_path(p)" in zsrc),
    ("连拍热键注册(第二键)", "_HOTKEY_ID2" in zsrc and "photo_hotkey" in zsrc),
    ("顶栏有 📸 连拍 + 🖼 照片按钮", 'id="btnPhoto"' in html and 'id="btnWall"' in html),
    ("挑帧条 + 照片墙弹窗存在", 'id="mBurst"' in html and 'id="mWall"' in html),
    # v1.5.34: 弹挑帧条的函数从 pbShow 换成了 burstForceShow(先收掉其它遮罩再弹),
    # 断言跟着改 —— 要验的是"轮询发现新 burst 会自动弹", 不是具体调了哪个函数名。
    ("热键触发后轮询自动弹挑帧条", "burstForceShow(st.photo_burst)" in html),
    ("方向键换帧/回车留帧", 'e.key === "ArrowRight"' in html and "pbKeep(); e.preventDefault()" in html),
]
w()
w("=== v1.5.31 静态检查 ===")
sbad19 = []
for name, ok in static_checks19:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        sbad19.append(name)
assert not sbad19, "v1.5.31 静态检查失败: %s" % sbad19

# ---------- 2.20 v1.5.32 静态检查(侧键抓拍 + 五层金字塔 + 前台冻结) ----------
static_checks20 = [
    ("鼠标侧键低级钩子", "WH_MOUSE_LL" in zsrc and "SetWindowsHookExW" in zsrc),
    ("侧键配置项 photo_mouse_btn", "photo_mouse_btn" in zsrc),
    # v1.5.37: 各档数量翻倍 (4,8,16,32) -> (8,16,32,64)
    ("五层金字塔 TIERS", "TIERS = (8, 16, 32, 64)" in zsrc and "def _tiers" in zsrc),
    # v1.5.35 改判据: 老写法「前台 pid != 游戏 pid 就冻结」一旦 PID 对不上, 缓冲永远空,
    # 侧键按下去只会得到「缓冲里还没内容」。现在改成「前台是管家界面才冻结」。
    ("只在自己界面在前台时冻结缓冲", "_is_manager_foreground()" in zsrc),
    # v1.5.37 把等待句柄从 `self._stop` 换成了 `self._rec_event`(为了让 press() 能
    # 立刻唤醒录制分支), 所以这里不能写死 `self._stop.wait(0.5)` —— 按"冻结 = 只等
    # 不 clear_ring"这个**行为**来断言, 不管句柄叫什么名字。
    ("切前台时冻结不清空(只等不 clear)",
     re.search(r"if _is_manager_foreground\(\):\s*\n\s*self\._\w+\.wait\(", zsrc) is not None),
    ("照片墙进页即建目录保证可打开", "os.makedirs(PHOTO_DIR, exist_ok=True)" in zsrc),
    ("挑帧条有档位按钮", 'data-tier=' in html and 'id="pbTiers"' in html),
    ("设置页有侧键下拉", 'id="inPhotoBtn"' in html),
    ("上下方向键换档", 'e.key === "ArrowUp"' in html and "PH.tier" in html),
]
w()
w("=== v1.5.32 静态检查 ===")
sbad20 = []
for name, ok in static_checks20:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        sbad20.append(name)
assert not sbad20, "v1.5.32 静态检查失败: %s" % sbad20

# ---------- 2.21 v1.5.34 静态检查(红按钮/勾选式选择留下/全屏预览/侧键立刻弹/照片目录可改) ----------
static_checks21 = [
    # 红按钮 bug 根因: .btn.danger 被定义两次, 后一条只覆盖 color 不覆盖 background
    # -> 红字压红底。这里断言"只定义一次", 防止以后再被人补一条回去。
    ("红按钮只定义一次(不再红字压红底)", html.count(".btn.danger{") == 1),
    ("红按钮是实心红底白字", ".btn.danger{background:#e5484d;color:#fff" in html),
    ("删掉了没用的「📷 补抓一张」", "pbShot" not in html),
    ("「全部留下」改成勾选式「☑ 选择留下」", 'id="pbPick"' in html and "选择留下" in html),
    ("勾选记在帧号上(可跨档勾)", "PH.sel[fi]" in html and "function pbToggleSel(" in html),
    ("勾选模式有退出按钮", 'id="pbPickX"' in html),
    ("点大图全屏预览", 'id="pbBig"' in html and "zoomFull(pimg(" in html),
    ("抽出通用 zoomFull", "function zoomFull(" in html),
    ("侧键/热键抓拍后把管家窗口顶到最前", "_raise_manager_window" in zsrc),
    ("轻量连拍哨兵接口", '"/api/photo_ping"' in zsrc and "burst_id" in zsrc),
    # 前端 api(path, {}) 会走 POST(JS 里 {} 是真值) —— 哨兵只挂 GET 的话前端拿到
    # {"ok":false,"msg":"未知操作"}, 静默失效。定义 1 处 + GET 1 处 + POST 1 处 = 3。
    ("哨兵 GET/POST 都挂(前端走 POST)", zsrc.count("photo_ping_payload(") >= 3),
    ("哨兵比整页轮询快", "setInterval(pbPingNow, 600)" in html),
    ("新 burst 先收遮罩再弹挑帧页", "function burstForceShow(" in html and "closeAll();" in html),
    ("两个轮询去重(同一批只弹一次)", "_pbShown" in html),
    ("照片目录可自定义(config.photo_dir)", '"photo_dir"' in zsrc and "def apply_photo_dir(" in zsrc),
    ("照片目录跟随配置生效", "apply_photo_dir(cfg)" in zsrc and "apply_photo_dir(self.cfg)" in zsrc),
    ("设置页有照片保存位置", 'id="inPhotoDir"' in html and 'id="btnPhotoDirPick"' in html),
    ("照片墙能直接改保存位置", 'id="pwDir"' in html),
    ("选文件夹支持指定起始目录", 'body.get("base")' in zsrc),
    ("左上角 logo 用绝区零图标", 'src="/favicon.ico"' in html),
]
w()
w("=== v1.5.34 静态检查 ===")
sbad21 = []
for name, ok in static_checks21:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        sbad21.append(name)
assert not sbad21, "v1.5.34 静态检查失败: %s" % sbad21

# ---------- 2.22 v1.5.35 静态检查(侧键没反应修复 / 清除缓存 / 侧键自检) ----------
# 抠出**侧键回调体**用来断言回调链上没有 I/O —— 超 LowLevelHooksTimeout(300ms)
# 会被 Windows 静默摘钩, 侧键从此彻底失效且无任何报错。
# 运行时那半边在 _v1535_check.py 第 10 节(把 open/spawn 全钉死)。
#
# ⚠️ 必须用 AST 而不是子串匹配: 注释和 docstring 里会**正常提到**这些名字
#    (例如 _why_empty 的 docstring 写着"绝对不能调 proc_probe()"), 子串匹配
#    会把注释当成代码 -> 假 FAIL(本脚本踩过)。
import ast as _ast22
try:
    _tree22 = _ast22.parse(zsrc)
except SyntaxError:
    _tree22 = None

def _func22(name, args=None):
    """按**名字 + 形参名**精确定位函数。

    ⚠️ 不能只按名字找: 本文件里有 **4 个** 叫 `_cb` 的函数(另外几个是窗口过程
    `_cb(hwnd, _l)`), `ast.walk` 会返回**第一个** —— 那样后面几条"没调 log()"
    会变成对错误函数的空转通过(本脚本踩过)。侧键那个的签名是
    `(nCode, wParam, lParam)`, 用它钉死。"""
    if _tree22 is None:
        return None
    for n in _ast22.walk(_tree22):
        if isinstance(n, (_ast22.FunctionDef, _ast22.AsyncFunctionDef)) \
                and n.name == name:
            if args is None:
                return n
            if [a.arg for a in n.args.args] == list(args):
                return n
    return None

def _used22(node):
    """函数体里真正用到的名字(含属性名)。注释/docstring 不算。"""
    out = set()
    if node is None:
        return out
    for n in _ast22.walk(node):
        if isinstance(n, _ast22.Name):
            out.add(n.id)
        elif isinstance(n, _ast22.Attribute):
            out.add(n.attr)
    return out

def _called22(node):
    """函数体里真正被调用的名字/属性。"""
    out = set()
    if node is None:
        return out
    for n in _ast22.walk(node):
        if isinstance(n, _ast22.Call):
            f = n.func
            if isinstance(f, _ast22.Name):
                out.add(f.id)
            elif isinstance(f, _ast22.Attribute):
                out.add(f.attr)
    return out

_cb_node = _func22("_cb", ("nCode", "wParam", "lParam"))
_we_node = _func22("_why_empty", ("self",))
_cb_calls = _called22(_cb_node)
_cb_used = _used22(_cb_node)
_we_calls = _called22(_we_node)
_we_used = _used22(_we_node)

static_checks22 = [
    # 根因 1: 失败路径完全静默 —— 老代码只在 trigger() 成功时才顶窗。
    ("抓拍键走统一入口 press()", "def press(self, kind=" in zsrc),
    ("侧键失败也顶窗(不再静默)", zsrc.count("burst.press(") >= 2),
    ("顶窗改成退避重试", "def _raise_manager_window(tries=" in zsrc),
    ("顶窗结果写日志", "def _raise_manager_window_bg(" in zsrc),
    # 根因 2: 冻结判据太严 -> 缓冲永远空
    ("新增 _is_manager_foreground", "def _is_manager_foreground(" in zsrc),
    ("缓冲不再因 PID 对不上而永远空", "foreground_pid() != gpid" not in zsrc),
    # 失败也要能弹出来
    ("空缓冲给得出人话原因", "def _why_empty(" in zsrc),
    ("press 成功失败都记一笔", "self.last_press = {" in zsrc and '"press_seq"' in zsrc),
    ("哨兵回传 press 三件套", '"press_seq": p.get("seq") or 0' in zsrc and
     '"press_ok": bool(p.get("ok"))' in zsrc and '"press_msg": p.get("msg") or ""' in zsrc),
    ("state 与哨兵 press 口径一致", '"photo_press_seq": (getattr(getattr(self, "burst", None),' in zsrc),
    # 清除缓存
    ("新增 clear_cache(只清内存)", "def clear_cache(self):" in zsrc),
    ("photo_clear 接口", 'act == "photo_clear"' in zsrc),
    ("挑帧页有「🧹 清除缓存」", 'id="pbClear"' in html and "清除缓存" in html),
    ("设置页也有清除缓存", 'id="btnPhotoClear"' in html),
    ("清除缓存不动磁盘照片", "只清内存" in zsrc or "一张不动" in zsrc),
    # 侧键自检
    ("新增 photo_diag", "def photo_diag(app):" in zsrc),
    ("photo_diag GET/POST 都挂", zsrc.count("photo_diag(") >= 3),
    ("自检逐环给修法", '"fix": fix' in zsrc or '"fix"' in zsrc),
    ("挑帧页有「🩺 侧键自检」", 'id="pbDiag"' in html),
    ("设置页有「🩺 侧键自检」", 'id="btnPhotoDiag"' in html),
    ("自检面板渲染函数共用", "function diagHTML(" in html),
    # 空状态 + 后台窗口不漏事件
    ("空状态有独立渲染 pbShowEmpty", "function pbShowEmpty(" in html),
    ("空批藏起「留这张」", "空批(没抓到帧)时把「留这张/选择留下」藏起来" in html),
    ("前端处理 press_seq", "function burstPressShow(" in html and "_pressSeen" in html),
    ("回到前台立刻补一次哨兵", 'addEventListener("visibilitychange"' in html and
     'addEventListener("focus", pbPingNow)' in html),
    ("哨兵抽成 pbPingNow 复用", "async function pbPingNow(" in html),
    ("state 暴露钩子状态", '"photo_mouse_ok"' in zsrc),
    ("设置页提示钩子没装上", "S.photo_mouse_ok === false" in html),
    ("版本号与 changelog 头一致(防下次再忘记同步)",
     (lambda m1, m2: m1 and m2 and m1.group(1) == m2.group(1))(
         re.search(r'^VERSION = "([\d.]+)"', zsrc, re.M),
         re.search(r'^v([\d.]+) 更新', zsrc, re.M))),
    # ---- 钩子回调安全(300ms 红线) —— 只看真实代码(AST) ----
    ("AST 解析到侧键回调 _cb", _cb_node is not None),
    ("AST 解析到 _why_empty", _we_node is not None),
    # 非空转守卫: 定位到的必须真的是侧键回调 —— 它一定调 press()。
    # 否则上面那几条"没调 log()"只是在对一个无关函数空转通过。
    ("AST 定位到的确实是侧键回调(调 press)", "press" in _cb_calls),
    ("新增 _after_press_bg(慢活全在后台)", "def _after_press_bg(" in zsrc),
    ("新增 _log_exc_bg(异常也后台写)", "def _log_exc_bg(" in zsrc),
    # _after_press_bg 是作为 target= 传进去的(不是直接调用), 所以查"用到"而不是"调用"
    ("侧键回调把慢活交给 _after_press_bg", "_after_press_bg" in _cb_used),
    ("侧键回调没调 log()", "log" not in _cb_calls),
    ("侧键回调没调 format_exc()", "format_exc" not in _cb_calls),
    ("侧键回调没调 proc_probe()", "proc_probe" not in _cb_calls),
    ("侧键回调没调 open()", "open" not in _cb_calls),
    ("侧键回调没调 Popen/run/system", not (_cb_calls & {"Popen", "run", "system", "popen"})),
    ("_why_empty 没调 proc_probe()", "proc_probe" not in _we_calls),
    # v1.5.37: _why_empty 改口径了 —— 新模型是"按下之后录 N 秒", 只在
    # 「photo_on 关着」那条分支上还会被钩子回调调到, 正文不再需要 _proc_cache。
    # 真正要守的不变量是「不起子进程」(上一行), 这里改成守「不读文件 / 不碰 _proc_cache」。
    ("_why_empty 不碰 _proc_cache(新口径)", "_proc_cache" not in _we_used),
]
w()
w("=== v1.5.35 静态检查 ===")
sbad22 = []
for name, ok in static_checks22:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        sbad22.append(name)
assert not sbad22, "v1.5.35 静态检查失败: %s" % sbad22


# ---------- 2.23 v1.5.36 静态检查(注册失败却能用 / 单实例检测 / 测试模式) ----------
# 真因: 没退干净的旧实例占着全局热键 -> 新实例报"注册失败", 但按 F9 有反应(旧实例响应)。
# 修法: 单实例检测 + 测试模式(不抢热键) + 逐键状态。三条都得静态钉住。
_PROJ23 = os.path.dirname(HERE)
def _read23(rel):
    try:
        return open(os.path.join(_PROJ23, rel), encoding="utf-8").read()
    except Exception:
        return ""

# 热键消息泵也要"0 I/O" —— 用 AST 抠 _loop(self, combo, combo2) 的真实调用
_loop23 = _func22("_loop", ("self", "combo", "combo2"))
_loop23_calls = _called22(_loop23)

_scripts23 = {
    "gen_censored_shots.py": _read23("gen_censored_shots.py"),
    "gen_preview.py": _read23("gen_preview.py"),
    "tests/live_check.py": _read23(os.path.join("tests", "live_check.py")),
    "tests/test_http.py": _read23(os.path.join("tests", "test_http.py")),
}

static_checks23 = [
    # 测试模式: 从源头杜绝"测试实例抢热键又没被回收变孤儿"
    ("后端有 TEST_MODE 开关", 'TEST_MODE = os.environ.get("ZZMI_TEST_MODE") == "1"' in zsrc),
    ("TEST_MODE 不注册全局热键(dry-run)", "self.ok, self.ok_main, self.ok_photo = True, True, True" in zsrc),
    ("TEST_MODE 不装鼠标钩子", "不装鼠标钩子" in zsrc),
    ("main 里 TEST_MODE 跳过 hotkey.start", "测试模式跳过全局快捷键" in zsrc),
    # 单实例检测
    ("有 INSTANCE_MUTEX 常量", "INSTANCE_MUTEX = " in zsrc),
    ("新增 detect_other_instance", "def detect_other_instance(" in zsrc),
    ("用 ERROR_ALREADY_EXISTS(183) 判定", "== 183" in zsrc and "ERROR_ALREADY_EXISTS" in zsrc),
    ("main 里调用 detect_other_instance", "app._mutex, app.other_instance = detect_other_instance()" in zsrc),
    ("TEST_MODE 实例不参与单实例检测", "app._mutex, app.other_instance = None, False" in zsrc),
    # 逐键热键状态
    ("HotkeyManager 有 ok_main/ok_photo", "self.ok_main = None" in zsrc and "self.ok_photo = None" in zsrc),
    ("_loop 逐键记录成败", "self.ok_main = None if not combo else False" in zsrc and
     "self.ok_photo = None if not combo2 else False" in zsrc),
    ("register 失败时逐键点名", "which = \"、\".join(bad)" in zsrc),
    ("register 提到另一个实例占键", "另一个管家实例" in zsrc),
    # state 暴露新字段
    ("state 暴露 hotkey_main_ok", '"hotkey_main_ok"' in zsrc),
    ("state 暴露 hotkey_photo_ok", '"hotkey_photo_ok"' in zsrc),
    ("state 暴露 other_instance", '"other_instance"' in zsrc),
    ("state 暴露 test_mode", '"test_mode"' in zsrc),
    # 前端逐键提示
    ("设置页逐键提示呼出键", "S.hotkey_main_ok===false" in html),
    ("设置页逐键提示连拍键", "S.hotkey_photo_ok === false" in html),
    ("设置页提到另一个实例占键", "S.other_instance" in html),
    # 热键消息泵 0 I/O(AST)
    ("AST 解析到热键 _loop", _loop23 is not None),
    ("热键 _loop 非空转(调 GetMessageW)", "GetMessageW" in _loop23_calls),
    ("热键 _loop 没调 format_exc()", "format_exc" not in _loop23_calls),
    ("热键 _loop 没调 log()", "log" not in _loop23_calls),
    ("热键 _loop 用 _log_exc_bg 报错", "_log_exc_bg" in _loop23_calls),
    # 4 个起源码实例的脚本都改走 TEST_MODE
    ("gen_censored_shots 用 TEST_MODE", "ZZMI_TEST_MODE" in _scripts23["gen_censored_shots.py"]),
    ("gen_preview 用 TEST_MODE", "ZZMI_TEST_MODE" in _scripts23["gen_preview.py"]),
    ("live_check 用 TEST_MODE", "ZZMI_TEST_MODE" in _scripts23["tests/live_check.py"]),
    ("test_http 用 TEST_MODE", "ZZMI_TEST_MODE" in _scripts23["tests/test_http.py"]),
]
w()
w("=== v1.5.36 静态检查 ===")
sbad23 = []
for name, ok in static_checks23:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        sbad23.append(name)
assert not sbad23, "v1.5.36 静态检查失败: %s" % sbad23


# ---------- 2.24 v1.5.37 静态检查(按下后录N秒 / 帧率翻倍 / pending-ack / 三层mod / 孤儿看门狗) ----------
static_checks24 = [
    # 1) 「按下之后录 N 秒」—— 不再是回溯
    ("BurstBuffer 有 rec 状态", "self.rec = None" in zsrc and 'self.rec = {"until"' in zsrc),
    ("press 只开录不立刻出结果", '"recording": True, "seconds": secs' in zsrc),
    ("录制中连击被忽略", "上一段还在录" in zsrc),
    ("_loop 优先处理录制分支", 'if rec is not None:' in zsrc),
    ("有 _finish_rec 收尾", "def _finish_rec(self):" in zsrc),
    ("_finish_rec 里才写 last_press", "self.last_press = {\"seq\": rec.get(\"seq\")" in zsrc),
    ("_finish_rec 才顶窗(录制期间不顶)", "_after_press_bg" in zsrc),
    ("有 recording() 供前端显示", "def recording(self):" in zsrc),
    ("_after_press_bg 录制中直接返回", 'if r.get("recording"):' in zsrc),
    # 2) 帧率 / 档位翻倍 + 抓屏减负
    ("TARGET_FPS 提到 24", "TARGET_FPS = 24" in zsrc),
    ("TIERS 翻倍到 (8,16,32,64)", "TIERS = (8, 16, 32, 64)" in zsrc),
    ("差异指纹改走 C 层(不再逐像素)", 'convert("L").resize((16, 16)).tobytes()' in zsrc),
    ("不再用 getdata() 逐像素", "list(small.getdata())" not in zsrc),
    # 3) pending / ack(修"回到管家没弹挑帧页")
    ("burst 带 pending 标记", '"pending": True' in zsrc),
    ("meta 暴露 pending", '"pending": bool(b.get("pending"))' in zsrc),
    ("有 ack() 方法", "def ack(self, burst_id=0):" in zsrc),
    ("ping 暴露 press_pending", '"press_pending": bool(p.get("pending"))' in zsrc),
    ("ping 暴露 recording/rec_seq", '"recording": bool(rec.get("recording"))' in zsrc
     and '"rec_seq": rec.get("seq") or 0' in zsrc),
    ("state 暴露 photo_press_pending", '"photo_press_pending"' in zsrc),
    ("state 暴露 photo_rec", '"photo_rec"' in zsrc),
    ("GET 路由挂了 photo_ack", 'if path == "/api/photo_ack":' in zsrc),
    ("POST 路由挂了 photo_ack", 'if act == "photo_ack":' in zsrc),
    # 4) 前端: 首帧播种要认 pending; _pressSeen 先弹再记
    ("前端有 pbAck", "function pbAck(id){" in html),
    ("pbShow 里 ack", "pbAck(PH.id);" in html),
    ("pbShowEmpty 里 ack", "pbAck(0);" in html),
    ("首帧播种认 pending", "_pbShown = pb0.pending ? 0 : (pb0.burst_id || 0);" in html),
    ("首帧 pending 时补弹", "if (pb0.pending && pb0.burst_id) burstForceShow(pb0);" in html),
    ("首帧 press_pending 时补弹", "st.photo_press_pending && st.photo_press_seq" in html),
    ("首帧播种抽成 pbSeedFromState", "function pbSeedFromState(st){" in html),
    ("pbSeedFromState 暴露给测试", "window.pbSeedFromState = pbSeedFromState;" in html),
    ("迟到的旧批次不许顶掉新批次", "_pbMax" in html and "if (id <= _pbMax) return;" in html),
    # _pressSeen 必须在 burstPressShow **之后**才更新, 否则空批提示被静默吞掉
    ("_pressSeen 先弹再记", html.index("if (ob === 0 && nb === 0) burstPressShow({press_seq: np")
     < html.index("_pressSeen = Math.max(_pressSeen, np);", 
                  html.index("const np = st.photo_press_seq || 0;"))),
    ("前端有录制提示", "function burstRecIndicator(r){" in html),
    ("ping 里调录制提示", "burstRecIndicator(r);" in html),
    # 5) 任意深度 mod 扫描
    ("有 looks_like_mod_name", "def looks_like_mod_name(name):" in zsrc),
    ("有 is_container_dir", "def is_container_dir(p):" in zsrc),
    ("mod_root_for 逐层下钻(不再硬编码第 2 层)", "last = len(parts) - 1" in zsrc
     and "if not is_container_dir(cand):" in zsrc),
    ("dir_info 存了直接子目录", '"kids": list(dirs)' in zsrc),
    ("不再用老的 branch_count", "branch_count" not in zsrc),
    # 6) 孤儿看门狗 + 热键自动重试
    ("有 WindowWatchdog", "class WindowWatchdog(object):" in zsrc),
    ("看门狗只在见过窗口后才判", "if not self.seen:" in zsrc),
    ("看门狗宽限期 >=120s", "grace=180.0" in zsrc),
    ("看门狗可被环境变量关掉", "ZZMI_NO_WATCHDOG" in zsrc),
    ("App 挂了 watchdog", "self.watchdog = WindowWatchdog(self)" in zsrc),
    ("main 里启动看门狗", "app.watchdog.start()" in zsrc),
    ("有 retry_lost", "def retry_lost(self, tries=24, interval=5.0):" in zsrc),
    ("main 里调用 retry_lost", "app.hotkey.retry_lost()" in zsrc),
    ("HotkeyManager 有注册锁", "self._reg_lock = threading.RLock()" in zsrc),
    # 7) 窗口查找放宽(减少"找不到就新开窗口"的误判)
    ("find_manager_window 有不挑类的兜底", "_scan(False)" in zsrc),
    ("toggle_manager_window 开新窗前先退避重试", "for _ in range(3):" in zsrc
     and "别急着新开窗口" in zsrc),
    # 8) 版本号
    ("版本号与 changelog 头一致(防下次再忘记同步)",
     (lambda m1, m2: m1 and m2 and m1.group(1) == m2.group(1))(
         re.search(r'^VERSION = "([\d.]+)"', zsrc, re.M),
         re.search(r'^v([\d.]+) 更新', zsrc, re.M))),
]
w()
w("=== v1.5.37 静态检查 ===")
sbad24 = []
for name, ok in static_checks24:
    w(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        sbad24.append(name)
assert not sbad24, "v1.5.37 静态检查失败: %s" % sbad24


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

# ---------- 3.5 等后端把缩略图备齐, 再抓 DOM ----------
# 缩略图是**后台异步**生成的: 冷启动时 /api/state 里大多数条目还没有 thumb 字段,
# 页面于是只渲染占位符 ◈, 让「预览图 img 标签已生成」假 FAIL。
# 踩过的坑: 同一份 ui.html, 冷启动抓到 3 张 <img>, 预热后 138 张 —— 与界面无关。
# 所以先等后端备齐再交给浏览器, 而不是拿"还没生成完"的中间态去判界面坏了。
def _thumb_ready(tries=60, need=6):
    import urllib.request as _u
    op = _u.build_opener(_u.ProxyHandler({}))
    u = URL.replace("/?t=", "/api/state?t=")
    n = 0
    for _ in range(tries):
        try:
            with op.open(u, timeout=10) as resp:
                st = json.loads(resp.read().decode("utf-8"))
            n = sum(1 for e in (st.get("entries") or []) if e.get("thumb"))
            if n >= need:
                return n
        except Exception:
            pass
        time.sleep(0.5)
    return n

_thumb_n = _thumb_ready()
w("后端已备好缩略图 %d 条" % _thumb_n)
if _thumb_n < 6:
    w("!! 缩略图仍不足(本机可能没有缩略图引擎), 预览图那条按数据缺失跳过")

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
    ("路径 chip 已显示", re.search(r"[A-Z]:[/\\].*Mods", dom) is not None),
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
elif _thumb_n < 6:
    # 有 mod 但缩略图备不齐(本机没缩略图引擎) —— 只跳过预览图这一条, 其余照判
    w("!! 缩略图备不齐(%d 条), 跳过「预览图 img 标签已生成」。" % _thumb_n)
    checks = [(n, o) for (n, o) in checks if n != "预览图 img 标签已生成"]

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
# ⚠️ 千万别写 screenshots/界面预览-深色.png —— 那个路径是**要提交/发布**的成品图,
# 而这里的截图抓的是**真实 mod 库**(真实 mod 名 + 缩略图 + 本机路径 F:\...\Mods),
# 一跑测试就会把打码成品覆盖成未打码的泄露图(踩过)。
# 要出可发布的图, 请跑仓库根的 gen_censored_shots.py(演示库 + 注入打码 CSS + 硬闸)。
shot = os.path.join(HERE, "_render_debug.png")   # tests/_* 已被 .gitignore 忽略
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
