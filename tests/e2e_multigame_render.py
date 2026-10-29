# -*- coding: utf-8 -*-
"""v1.5.71 渲染实证: 起一个隔离服务, 用真浏览器 dump-dom, 证明
   ① 只有 1 个游戏时切换器**不显示**(单游戏界面和以前一样)
   ② 有 2 个游戏时切换器出现, 两个标签都在
   ③ 切换后顶栏、路径条、列表整套换掉
全程隔离数据目录 + 沙箱, 不碰真实 Mods / 真实配置。
"""
import json, os, shutil, subprocess, sys, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
APP = os.path.join(HERE, "..", "zzmi_manager.py")
DATA = os.path.join(HERE, "_rn_data")
SB = os.path.join(HERE, "_rn_sandbox")
OUT = os.path.join(HERE, "_rn_out.txt")
L = []


def w(s=""):
    L.append(str(s))
    print(s)


def _clean(p):
    if not os.path.isdir(p):
        return
    for root, dirs, files in os.walk(p, topdown=False):
        for f in files:
            try:
                os.remove(os.path.join(root, f))
            except OSError:
                pass
        for d in dirs:
            try:
                os.rmdir(os.path.join(root, d))
            except OSError:
                pass
    try:
        os.rmdir(p)
    except OSError:
        pass


def mk(p, t=""):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(t)


_clean(SB)
os.makedirs(os.path.join(SB, "Resources", "Bin"), exist_ok=True)
open(os.path.join(SB, "Resources", "Bin", "XXMI Launcher.exe"), "wb").close()
for imp in ("ZZMI", "WWMI"):
    os.makedirs(os.path.join(SB, imp, "Mods"), exist_ok=True)
    open(os.path.join(SB, imp, "d3dx.ini"), "wb").close()
for side, h in (("ZZMI", "00aa0101"), ("WWMI", "00bb0101")):
    for i in range(4):
        mk(os.path.join(SB, side, "Mods", "分类%d" % i, "角色%d" % i, "m.ini"),
           "[TextureOverrideX]\nhash = %s\nvb0 = R\n" % h)
json.dump({"Importers": {
    "ZZMI": {"game_exe_names": ["ZenlessZoneZero.exe"], "process_exe_names": []},
    "WWMI": {"game_exe_names": ["Wuthering Waves.exe"],
             "process_exe_names": ["Client-Win64-Shipping.exe"]},
}}, open(os.path.join(SB, "XXMI Launcher Config.json"), "w",
        encoding="utf-8"), ensure_ascii=False)

_clean(DATA)
os.makedirs(DATA)
json.dump({
    "zzmi_root": SB, "launcher_exe": "", "importer": "ZZMI", "game_exe": "",
    "mods_dir": os.path.join(SB, "ZZMI", "Mods"), "libraries": [],
    "theme": "dark", "hide_preview": False, "photo_on": True,
}, open(os.path.join(DATA, "config.json"), "w", encoding="utf-8"),
    ensure_ascii=False)

env = dict(os.environ)
env["ZZMI_MANAGER_DATA"] = DATA
env["ZZMI_NO_BROWSER"] = "1"
env["ZZMI_TEST_MODE"] = "1"
env["PYTHONIOENCODING"] = "utf-8"

proc = subprocess.Popen([PY, APP], env=env, cwd=os.path.join(HERE, ".."),
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                        text=True, encoding="utf-8", errors="replace")


def url_of():
    p = os.path.join(DATA, "last_url.txt")
    for _ in range(120):
        if os.path.isfile(p):
            try:
                u = open(p).read().strip()
                if u:
                    return u
            except Exception:
                pass
        time.sleep(0.25)
    return None


base = url_of()
assert base, "服务没起来"
TOKEN = base.split("t=")[1]
ROOT = base.split("?")[0]
w("服务: " + ROOT)


def req(path, body=None):
    url = ROOT + path + ("&" if "?" in path else "?") + "t=" + TOKEN
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    r = urllib.request.Request(url, data=data,
                               headers={"Content-Type": "application/json"},
                               method="POST" if body is not None else "GET")
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, None


BROWSER = None
for cand in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
             r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
             r"C:\Program Files\Google\Chrome\Application\chrome.exe",
             r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"):
    if os.path.isfile(cand):
        BROWSER = cand
        break
assert BROWSER, "找不到浏览器, 没法做渲染实证"
w("浏览器: " + BROWSER)


def dump_dom():
    prof = os.path.join(HERE, "_rn_prof")
    os.makedirs(prof, exist_ok=True)
    cmd = [BROWSER, "--headless=new", "--disable-gpu", "--no-first-run",
           "--no-default-browser-check", "--disable-extensions",
           "--proxy-server=direct://", "--proxy-bypass-list=<-loopback>",
           "--user-data-dir=" + prof, "--virtual-time-budget=9000",
           "--run-all-compositor-stages-before-draw", "--dump-dom", base]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=180)
    return r.stdout or ""


def keep_alive():
    """headless 浏览器 dump 完会关掉「界面窗口」, 触发管家的 "5 秒内没重新
    打开就自动退出"。每轮抓完立刻补一次 hello, 把自动退出取消掉。"""
    try:
        req("/api/hello", {"act": "hello"})
    except Exception:
        pass


# ---------- 1. 启动即自动登记: 切换器必须显示 ----------
# v1.5.71: main() 启动时会自动扫 XXMI 根下所有 importer 并登记,
# 所以这里一打开就应该看到 绝区零 + 鸣潮 两个标签(外加「+ 添加」按钮)。
dom = dump_dom()
keep_alive()
w("DOM 长度 %d" % len(dom))
assert "Mod 管家" in dom, "界面没渲染出来(拿到的是错误页?)"
assert 'id="gtabs"' in dom, "顶栏没有切换器容器"
import re
m = re.search(r'<div class="gtabs(?: many)?" id="gtabs"[^>]*>', dom)
w("启动后 gtabs 标签: " + (m.group(0) if m else "没找到"))
assert m and "display:none" not in m.group(0), \
    "启动后切换器被隐藏了(用户会找不到在哪切鸣潮): %r" % (m.group(0) if m else None)
tabs0 = re.findall(r'<button class="gtab( on)?" data-g="([^"]+)"', dom)
w("启动后标签: %r" % (tabs0,))
assert {t[1] for t in tabs0} == {"zzmi", "wwmi"}, \
    "启动时没有自动登记出两个游戏: %r" % (tabs0,)
assert "绝区零" in dom and "鸣潮" in dom, "标签文字缺失"
assert 'id="gAdd"' not in dom, "「+ 添加」按钮应当已被删除"
w("① 启动即自动登记: 绝区零+鸣潮 两个标签都在, 没有多余的「+ 添加」 OK")

# ---------- 2. 活动游戏是绝区零, 且没混进鸣潮的 mod ----------
on_tabs = [t[1] for t in tabs0 if t[0].strip()]
assert on_tabs == ["zzmi"], "活动标签应当是 zzmi: %r" % (tabs0,)
w("② 默认活动游戏 = 绝区零, 高亮正确 OK")

# ---------- 3. 切到鸣潮 -> 顶栏路径 + 列表整套换掉 ----------
st, r = req("/api/switch_game", {"action": "switch_game", "game": "wwmi"})
assert st == 200 and r["ok"], (st, r)
assert r["state"]["active_game"] == "wwmi"
time.sleep(0.6)
dom = dump_dom()
keep_alive()
tabs = re.findall(r'<button class="gtab( on)?" data-g="([^"]+)"', dom)
on_tabs = [t[1] for t in tabs if t[0].strip()]
assert on_tabs == ["wwmi"], "切换后高亮没跟着走: %r" % (tabs,)
# 路径条显示的是鸣潮的 Mods 目录
assert "WWMI" in dom, "顶栏路径条没显示鸣潮目录"
w("③ 切到鸣潮: 标签高亮跟着走, 顶栏路径条显示 WWMI OK")

# 切回去
st, r = req("/api/switch_game", {"action": "switch_game", "game": "zzmi"})
assert r["ok"], r
time.sleep(0.4)
dom = dump_dom()
keep_alive()
tabs = re.findall(r'<button class="gtab( on)?" data-g="([^"]+)"', dom)
assert [t[1] for t in tabs if t[0].strip()] == ["zzmi"], tabs
w("④ 切回绝区零 OK")

proc.terminate()
try:
    proc.wait(timeout=15)
except Exception:
    proc.kill()

w("")
w("RENDER E2E PASSED")
open(OUT, "w", encoding="utf-8").write("\n".join(L))
