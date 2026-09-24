# -*- coding: utf-8 -*-
"""验证打包后的 exe 能独立跑起来(含 ui.html 资源加载)。只读/沙箱, 不碰真实 Mods。"""
import json, os, shutil, subprocess, sys, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
EXE = os.path.join(HERE, "..", "ZZMI-Mod-Manager.exe")
DATA = os.path.join(HERE, "_exe_data")
SB = os.path.join(HERE, "_sandbox")
MODS = os.path.join(SB, "Mods")
OUT = os.path.join(HERE, "_exe_result.txt")
L = []
def w(s=""):
    L.append(str(s)); print(s)

assert os.path.isfile(EXE), "exe 不存在: " + EXE
w("exe = %s (%.2f MB)" % (EXE, os.path.getsize(EXE) / 1048576.0))

if os.path.isdir(DATA):
    shutil.rmtree(DATA)
os.makedirs(DATA, exist_ok=True)
json.dump({"zzmi_root": SB, "launcher_exe": "", "importer": "ZZMI", "game_exe": "",
           "mods_dir": MODS, "libraries": [], "theme": "dark", "hide_preview": False},
          open(os.path.join(DATA, "config.json"), "w", encoding="utf-8"), ensure_ascii=False)

env = dict(os.environ)
env["ZZMI_MANAGER_DATA"] = DATA
env["ZZMI_NO_BROWSER"] = "1"
# v1.5.43: 必须加这个 —— 否则测试实例会真的注册全局热键(F9)。而 onefile 是
# "引导父进程 + 真身子进程" 两个进程, 收尾只 p.terminate() 掉父进程的话,
# 子进程会活下来变成**占着 F9 的孤儿**, 之后真管家就注册不上热键了(踩过)。
env["ZZMI_TEST_MODE"] = "1"
env["PYTHONIOENCODING"] = "utf-8"

p = subprocess.Popen([EXE], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                     text=True, encoding="utf-8", errors="replace")
try:
    urlp = os.path.join(DATA, "last_url.txt")
    url = None
    for _ in range(120):
        if os.path.isfile(urlp):
            v = open(urlp).read().strip()
            if v:
                url = v
                break
        if p.poll() is not None:
            break
        time.sleep(0.25)
    w("url = " + str(url))
    assert url, "exe 没起来 (退出码 %s)" % p.poll()
    ROOT, TOKEN = url.split("?")[0], url.split("t=")[1]

    def get(path, raw=False):
        u = ROOT + path + ("&" if "?" in path else "?") + "t=" + TOKEN
        with urllib.request.urlopen(u, timeout=60) as r:
            b = r.read()
            return r.status, (b if raw else json.loads(b.decode("utf-8")))

    st, html = get("/", raw=True)
    w("GET / -> %d, %d bytes" % (st, len(html)))
    assert st == 200 and b"ZZMI Mod" in html, "exe 没找到 ui.html!"
    assert b"__BOOT__" not in html
    w("  ui.html 已正确打包并从 exe 内部加载  ✅")

    st, s = get("/api/state")
    w("GET /api/state -> %d, mods=%d, size=%s" %
      (st, s["stats"]["total"], s["stats"]["size_h"]))
    assert st == 200 and s["stats"]["total"] == 4

    st, s2 = get("/thumb?p=" + urllib.parse.quote("分类A/安比/AnbyMod/preview.png"), raw=True)
    w("GET /thumb -> %d, %d bytes" % (st, len(s2)))
    assert st == 200 and (s2[:4] == b"\x89PNG" or s2[:2] == b"\xff\xd8"), \
        "缩略图既不是 png 也不是 jpeg"
    if s2[:2] == b"\xff\xd8":
        w("  返回的是服务端生成的 JPEG 缩略图 ✅")

    w()
    w("EXE TEST PASSED")
finally:
    p.terminate()
    try:
        o, _ = p.communicate(timeout=10)
    except Exception:
        p.kill(); o = ""
    w()
    w("=== exe 输出 ===")
    w((o or "").strip()[:1500])
    open(OUT, "w", encoding="utf-8").write("\n".join(L))
