# v1.5.61 真 HTTP 端到端: 起真服务器, 打 /api/zzz_swap_status 与 /api/zzz_swap
import os, sys, json, time, tempfile, shutil, subprocess, urllib.request, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location("zm", os.path.join(ROOT, "zzmi_manager.py"))
zm = importlib.util.module_from_spec(spec); sys.modules["zm"] = zm; spec.loader.exec_module(zm)

PASS, FAIL = [], []
def ck(n, c, e=""):
    (PASS if c else FAIL).append(n)
    print(("  ok   " if c else "  FAIL ") + n + ((" | " + str(e)) if e else ""))

work = tempfile.mkdtemp(prefix="zzzhttp_")
port = 8731
srv = None
try:
    game = os.path.join(work, "G")
    data = os.path.join(game, "ZenlessZoneZero_Data", "il2cpp_data")
    os.makedirs(os.path.join(data, "Metadata"))
    def wf(p, c):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write(c)
    wf(os.path.join(game, "GameAssembly.dll"), "INTL_YYYY")
    wf(os.path.join(data, "Metadata", "global-metadata.dat"), "INTL")
    cn = os.path.join(work, "cn")
    wf(os.path.join(cn, "GameAssembly.dll"), "CN_XXXX")
    wf(os.path.join(cn, "il2cpp_data", "Metadata", "global-metadata.dat"), "CN")
    intl = os.path.join(work, "intl"); sub = os.path.join(intl, "替换文件")
    wf(os.path.join(sub, "GameAssembly.dll"), "INTL_YYYY")
    wf(os.path.join(sub, "il2cpp_data", "Metadata", "global-metadata.dat"), "INTL")

    # 用真 App + 真 Handler, 起真 ThreadingHTTPServer
    zm.DATA_DIR = work
    os.makedirs(os.path.join(work, "downloads"), exist_ok=True)
    app = zm.App()
    app.cfg["game_exe"] = os.path.join(game, "ZenlessZoneZero.exe")
    wf(app.cfg["game_exe"], "x")
    app.cfg["cn_files_dir"] = cn
    app.cfg["intl_files_dir"] = intl
    app.cfg["mods_dir"] = os.path.join(work, "Mods")
    os.makedirs(app.cfg["mods_dir"], exist_ok=True)

    import threading
    from http.server import ThreadingHTTPServer
    zm.Handler.app = app
    srv = ThreadingHTTPServer(("127.0.0.1", port), zm.Handler)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    time.sleep(0.5)
    token = app.token

    def call(act, body=None):
        url = "http://127.0.0.1:%d/api/%s?t=%s" % (port, act, token)
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())

    st = call("zzz_swap_status", {})
    ck("HTTP: status 识别当前为国际服", st.get("side") == "intl", st.get("side"))
    ck("HTTP: status 返回两套路径", bool(st.get("cn_dir")) and bool(st.get("intl_dir")), st.get("cn_dir"))
    ck("HTTP: status has_cn/has_intl 都为真", st.get("has_cn") and st.get("has_intl"))

    r = call("zzz_swap", {"side": "auto"})
    ck("HTTP: auto 互转成功", r.get("ok"), r.get("msg"))
    ck("HTTP: 互转后 side=cn", r.get("side") == "cn", r.get("side"))
    ck("HTTP: 文件真的换了(国服)",
       open(os.path.join(game, "GameAssembly.dll")).read() == "CN_XXXX")

    st2 = call("zzz_swap_status", {})
    ck("HTTP: 再查状态变成国服", st2.get("side") == "cn", st2.get("side"))

    r2 = call("zzz_swap", {"side": "auto"})
    ck("HTTP: 再点一次换回国际服", r2.get("ok") and r2.get("side") == "intl", r2.get("msg"))
    ck("HTTP: 文件真的换回了",
       open(os.path.join(game, "GameAssembly.dll")).read() == "INTL_YYYY")

finally:
    if srv:
        try: srv.shutdown()
        except Exception: pass
    shutil.rmtree(work, ignore_errors=True)

print("\n==== 结果: %d 通过, %d 失败 ====" % (len(PASS), len(FAIL)))
if FAIL:
    print("失败项:", FAIL); sys.exit(1)