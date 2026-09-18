# -*- coding: utf-8 -*-
"""HTTP 层联调: 用隔离数据目录 + 沙箱 mods, 不触碰真实 Mods。"""
import json, os, shutil, subprocess, sys, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
APP = os.path.join(HERE, "..", "zzmi_manager.py")

DATA = os.path.join(HERE, "_http_data")
SB = os.path.join(HERE, "_sandbox")
MODS = os.path.join(SB, "Mods")
OUT = os.path.join(HERE, "_http_out.txt")
L = []
def w(s=""):
    L.append(str(s)); print(s)

# --- 准备沙箱 mods ---
if os.path.isdir(SB):
    shutil.rmtree(SB)
os.makedirs(os.path.join(MODS, "分类A", "安比", "AnbyMod", "resources"))
os.makedirs(os.path.join(MODS, "分类A", "丽娜", "RinaMod"))
os.makedirs(os.path.join(MODS, "工具箱"))
def mk(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(t)
mk(os.path.join(MODS, "分类A", "安比", "AnbyMod", "Main.ini"),
   "[TextureOverrideAnby]\nhash = 003ff258\nvb0 = ResourceAnby\n")
mk(os.path.join(MODS, "分类A", "安比", "AnbyMod", "resources", "tex.ini"),
   "[TextureOverrideTex]\nhash = aabbccdd\nps-t0 = ResourceX\n")
mk(os.path.join(MODS, "分类A", "丽娜", "RinaMod", "Rina.ini"),
   "[TextureOverrideRina]\nhash = 003ff258\nvb0 = ResourceRina\n")
mk(os.path.join(MODS, "工具箱", "Hide.ini"),
   "[TextureOverrideUID]\nhash = 2c180570\nhandling = skip\n")
# 变体测试 mod: A/B 共享 hash(变体组), face 独立部件
os.makedirs(os.path.join(MODS, "变体测试"), exist_ok=True)
mk(os.path.join(MODS, "变体测试", "A.ini"),
   "[TextureOverrideVarA]\nhash = abcdef01\nvb0 = ResourceA\n")
mk(os.path.join(MODS, "变体测试", "DISABLED_B.ini"),
   "[TextureOverrideVarB]\nhash = abcdef01\nvb0 = ResourceB\n")
mk(os.path.join(MODS, "变体测试", "face.ini"),
   "[TextureOverrideFace]\nhash = beef1234\nps-t0 = ResourceF\n")
# 热键循环变体 (游戏内按 H 循环)
mk(os.path.join(MODS, "变体测试", "cycle.ini"),
   "[KeySwapHair]\nkey = no_alt h\ntype = cycle\n$swapvarHair = 0,1,2\n")
# 一张假预览图
png = bytes.fromhex("89504e470d0a1a0a0000000d494844520000000100000001080600000"
                    "01f15c4890000000a49444154789c6300010000050001"
                    "0d0a2db40000000049454e44ae426082")
open(os.path.join(MODS, "分类A", "安比", "AnbyMod", "preview.png"), "wb").write(png)
# 仓库
mk(os.path.join(SB, "仓库A", "备用mod", "x.ini"), "[TextureOverrideX]\nhash = 12345678\nvb0 = R\n")
os.makedirs(os.path.join(SB, "仓库A", "空目录"), exist_ok=True)

# --- 隔离数据目录 + 预置配置 ---
if os.path.isdir(DATA):
    shutil.rmtree(DATA)
os.makedirs(DATA)
json.dump({
    "zzmi_root": SB,                   # 直接把沙箱当根, 便于测仓库
    "launcher_exe": "",
    "importer": "ZZMI",
    "game_exe": "",
    "mods_dir": MODS,
    "libraries": ["仓库A"],
    "theme": "dark",
    "hide_preview": False,
}, open(os.path.join(DATA, "config.json"), "w", encoding="utf-8"), ensure_ascii=False)

env = dict(os.environ)
env["ZZMI_MANAGER_DATA"] = DATA
env["ZZMI_NO_BROWSER"] = "1"
env["PYTHONIOENCODING"] = "utf-8"

proc = subprocess.Popen([PY, APP], env=env, cwd=os.path.join(HERE, ".."),
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                        encoding="utf-8", errors="replace")
log_lines = []

def url_of():
    p = os.path.join(DATA, "last_url.txt")
    for _ in range(80):
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
w("server url = " + str(base))
assert base, "服务没起来"
TOKEN = base.split("t=")[1]
ROOT = base.split("?")[0]

def req(path, body=None, raw=False):
    url = ROOT + path + ("&" if "?" in path else "?") + "t=" + TOKEN
    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    r = urllib.request.Request(url, data=data,
                              headers={"Content-Type": "application/json"},
                              method="POST" if body is not None else "GET")
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            b = resp.read()
            return resp.status, (b if raw else json.loads(b.decode("utf-8"))), dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, None, {}

try:
    # 1. UI 页面
    st, html, hd = req("/", raw=True)
    w(f"GET /  -> {st}, {len(html)} bytes, ctype={hd.get('Content-Type')}")
    assert st == 200 and b"ZZMI Mod" in html
    assert b"__BOOT__" not in html, "BOOT 占位符没被替换"
    assert b"model.token" not in html
    w("  UI 页面正常, 令牌已注入")

    # 2. 无令牌必须被拒
    try:
        urllib.request.urlopen(ROOT + "/api/state", timeout=10)
        w("  !! 无令牌竟然成功了"); assert False
    except urllib.error.HTTPError as e:
        w(f"  无令牌访问 /api/state -> {e.code} (应为 403)")
        assert e.code == 403
    # 错令牌
    try:
        urllib.request.urlopen(ROOT + "/api/state?t=bad", timeout=10)
        assert False
    except urllib.error.HTTPError as e:
        w(f"  错误令牌 -> {e.code} (应为 403)"); assert e.code == 403

    # 3. state
    st, s, _ = req("/api/state")
    w(f"GET /api/state -> {st}")
    w("  configured=%s mods_dir=%s" % (s["configured"], s["mods_dir"]))
    w("  stats=%s" % json.dumps(s["stats"], ensure_ascii=False))
    w("  entries=%d categories=%s" % (len(s["entries"]), [c["name"] for c in s["categories"]]))
    assert st == 200 and s["stats"]["total"] == 4
    ids = {e["id"]: e for e in s["entries"]}
    assert "分类A/安比" in ids and "分类A/丽娜" in ids and "工具箱" in ids \
        and "变体测试" in ids, list(ids)
    assert len(s["conflicts"]) == 1, s["conflicts"]
    anby = ids["分类A/安比"]
    assert anby["thumb"] and anby["thumb"].endswith("preview.png"), anby["thumb"]
    assert "sub_dirs" not in anby, "列表载荷应已瘦身(不带 sub_dirs)"
    assert "hashes" not in anby, "列表载荷应已瘦身(不带 hashes)"
    w("  冲突: %s" % json.dumps(s["conflicts"][0], ensure_ascii=False))
    w("  安比 thumb=%s (列表已瘦身)" % anby["thumb"])

    # 4. thumb
    st, data, hd = req("/thumb?p=" + urllib.parse.quote(anby["thumb"]), raw=True)
    w(f"GET /thumb -> {st}, {len(data)} bytes, {hd.get('Content-Type')}")
    assert st == 200 and (data[:4] == b"\x89PNG" or data[:2] == b"\xff\xd8"), "缩略图格式不对"
    # 越界
    st, _, _ = req("/thumb?p=" + urllib.parse.quote("../../windows/win.ini"), raw=True)
    w(f"  越界 /thumb -> {st} (应为 404/403)")
    assert st in (403, 404)

    # 5. detail  (重字段在这里才下发)
    st, d, _ = req("/api/detail?id=" + urllib.parse.quote("分类A/安比"))
    w(f"GET /api/detail -> {st}, inis={len(d['inis'])}, exists={d['exists']}")
    assert st == 200 and d["exists"] and len(d["inis"]) == 2
    de = d["entry"]
    assert len(de["sub_dirs"]) >= 2, de["sub_dirs"]
    assert any(x["local"] == "AnbyMod/resources" for x in de["sub_dirs"]), de["sub_dirs"]
    assert de["hashes"], "详情里应给出 hash"
    w("  详情子目录=%s hashes=%s" % ([x["local"] for x in de["sub_dirs"]], de["hashes"]))

    # 6. library
    st, lib, _ = req("/api/library")
    w(f"GET /api/library -> {st}, libs={[l['name'] for l in lib['libraries']]}, "
      f"tops={[t['name'] for t in lib['mods_top']]}")
    assert st == 200 and lib["libraries"][0]["name"] == "仓库A"
    assert lib["libraries"][0]["count"] == 2

    # 7. 单条禁用 / 启用
    st, r, _ = req("/api/toggle", {"ids": ["分类A/安比"], "enabled": False})
    w(f"POST /api/toggle(禁用 安比) -> ok={r['result']['ok']} failed={r['result']['failed']}")
    assert r["result"]["ok"] == 1 and r["result"]["failed"] == 0
    assert os.path.isdir(os.path.join(MODS, "分类A", "DISABLED_安比"))
    ids = {e["id"]: e for e in r["state"]["entries"]}
    assert ids["分类A/安比"]["enabled"] is False
    assert not r["state"]["conflicts"], "禁用后不该再有冲突"
    w("  磁盘已改名: 分类A/DISABLED_安比 ; 冲突已消失")

    # 8. 撤销
    st, r, _ = req("/api/undo", {})
    w(f"POST /api/undo -> ok={r['ok']} msg={r['msg']}")
    assert r["ok"] and os.path.isdir(os.path.join(MODS, "分类A", "安比"))
    assert {e["id"]: e for e in r["state"]["entries"]}["分类A/安比"]["enabled"] is True

    # 9. 子目录启停
    st, r, _ = req("/api/dir_toggle", {"rel": "分类A/安比/AnbyMod/resources", "enabled": False})
    w(f"POST /api/dir_toggle -> ok={r['ok']} msg={r['msg']}")
    assert r["ok"] and os.path.isdir(os.path.join(MODS, "分类A", "安比", "AnbyMod", "DISABLED_resources"))
    e = {x["id"]: x for x in r["state"]["entries"]}["分类A/安比"]
    assert e["enabled"] is True and e["partial"] is True, e
    w("  父 mod 仍启用, partial=True (部分子目录被禁用)")
    st, r, _ = req("/api/dir_toggle", {"rel": "分类A/安比/AnbyMod/resources", "enabled": True})
    assert r["ok"]
    e = {x["id"]: x for x in r["state"]["entries"]}["分类A/安比"]
    assert e["partial"] is False

    # 9.5 变体 / 部件 (HTTP 全链路)
    st, d, _ = req("/api/detail?id=" + urllib.parse.quote("变体测试"))
    w(f"GET /api/detail(变体测试) -> {st}, groups={len(d['groups'])}, comps={len(d['components'])}")
    assert st == 200 and len(d["groups"]) == 1, d.get("groups")
    g = d["groups"][0]
    assert g["active"] == "A.ini" and set(g["files"]) == {"A.ini", "DISABLED_B.ini"}, g
    cmap = {c["rel"]: c for c in d["components"]}
    assert cmap["face.ini"]["group"] is None and cmap["face.ini"]["enabled"] is True
    assert cmap["DISABLED_B.ini"]["enabled"] is False
    w("  变体组: %s (当前=%s) ; face.ini 为独立部件" % (g["label"], g["active"]))

    # 一键切换变体 B -> A 应被自动禁用
    st, r, _ = req("/api/variant_select", {"id": "变体测试", "rel": "DISABLED_B.ini"})
    w(f"POST /api/variant_select -> ok={r['ok']} msg={r['msg']}")
    assert r["ok"] and os.path.isfile(os.path.join(MODS, "变体测试", "B.ini"))
    assert os.path.isfile(os.path.join(MODS, "变体测试", "DISABLED_A.ini"))
    st, d2, _ = req("/api/detail?id=" + urllib.parse.quote("变体测试"))
    assert d2["groups"][0]["active"] == "B.ini", d2["groups"]
    w("  切换后磁盘: B.ini 启用 / DISABLED_A.ini ; 详情 active=B.ini")

    # 独立部件开关
    st, r, _ = req("/api/component_toggle", {"id": "变体测试", "rel": "face.ini", "enabled": False})
    w(f"POST /api/component_toggle(face.ini 禁用) -> ok={r['ok']} msg={r['msg']}")
    assert r["ok"] and os.path.isfile(os.path.join(MODS, "变体测试", "DISABLED_face.ini"))
    st, r, _ = req("/api/component_toggle", {"id": "变体测试", "rel": "DISABLED_face.ini", "enabled": True})
    assert r["ok"] and os.path.isfile(os.path.join(MODS, "变体测试", "face.ini"))
    # 切回变体 A, 恢复初始状态
    st, r, _ = req("/api/variant_select", {"id": "变体测试", "rel": "DISABLED_A.ini"})
    assert r["ok"] and os.path.isfile(os.path.join(MODS, "变体测试", "A.ini"))
    w("  部件开关往返 + 切回变体 A OK")

    # 9.7 热键循环变体 (HTTP 全链路)
    st, d, _ = req("/api/detail?id=" + urllib.parse.quote("变体测试"))
    cyc = {c["var"]: c for c in (d.get("cycles") or [])}
    w("  cycles: " + json.dumps(
        [{k: c[k] for k in ("var", "values", "keys", "current", "switchable")}
         for c in (d.get("cycles") or [])], ensure_ascii=False))
    assert "swapvarHair" in cyc, list(cyc)
    assert cyc["swapvarHair"]["values"] == [0, 1, 2]
    assert cyc["swapvarHair"]["current"] == 0
    assert cyc["swapvarHair"]["keys"] == ["H"], cyc["swapvarHair"]["keys"]
    st, r, _ = req("/api/cycle_set", {"id": "变体测试", "var": "swapvarHair",
                                      "value": 2})
    w(f"POST /api/cycle_set -> ok={r['ok']} msg={r['msg']}")
    # v1.4.0: 变体写入功能已移除, 接口必须拒绝且不碰文件
    assert not r["ok"], r
    body = open(os.path.join(MODS, "变体测试", "cycle.ini"),
                encoding="utf-8").read()
    assert "$swapvarHair = 0,1,2" in body, body
    w("  变体写入已移除: 接口拒绝 + 文件未被改动 (HTTP) OK")

    # 10. scope 批量 (按分类禁用)
    st, r, _ = req("/api/scope", {"scope": {"type": "category", "value": "分类A"}, "enabled": False})
    w(f"POST /api/scope(category=分类A, 禁用) -> ok={r['result']['ok']}")
    assert r["result"]["ok"] == 2
    assert os.path.isdir(os.path.join(MODS, "分类A", "DISABLED_安比"))
    assert os.path.isdir(os.path.join(MODS, "分类A", "DISABLED_丽娜"))
    assert all(not e["enabled"] for e in r["state"]["entries"] if e["path"].startswith("分类A"))
    w("  分类内每条 mod 目录已各自改名")
    st, r, _ = req("/api/scope", {"scope": {"type": "category", "value": "分类A"}, "enabled": True})
    assert r["result"]["ok"] == 2 and os.path.isdir(os.path.join(MODS, "分类A", "安比"))

    # 11. 方案
    st, r, _ = req("/api/preset", {"action": "save", "name": "测试方案"})
    w(f"POST /api/preset save -> {r['msg']}")
    assert "测试方案" in r["state"]["presets"]
    st, r, _ = req("/api/toggle", {"ids": ["分类A/丽娜"], "enabled": False})
    assert os.path.isdir(os.path.join(MODS, "分类A", "DISABLED_丽娜"))
    st, r, _ = req("/api/preset", {"action": "apply", "name": "测试方案"})
    w(f"POST /api/preset apply -> {r['msg']}")
    assert r["ok"] and os.path.isdir(os.path.join(MODS, "分类A", "丽娜"))
    assert all(e["enabled"] for e in r["state"]["entries"])
    st, r, _ = req("/api/preset", {"action": "delete", "name": "测试方案"})
    assert r["ok"]

    # 12. 仓库搬运: 移出 / 移入
    st, r, _ = req("/api/move", {"src_base": "mods", "src_rel": "工具箱",
                                 "dst_base": "root", "dst_rel": "仓库A/工具箱"})
    w(f"POST /api/move 移出 -> ok={r['ok']} {r['msg']}")
    assert r["ok"] and os.path.isdir(os.path.join(SB, "仓库A", "工具箱"))
    assert not os.path.exists(os.path.join(MODS, "工具箱"))
    st, r, _ = req("/api/move", {"src_base": "root", "src_rel": "仓库A/工具箱",
                                 "dst_base": "mods", "dst_rel": "工具箱"})
    w(f"POST /api/move 移入 -> ok={r['ok']} {r['msg']}")
    assert r["ok"] and os.path.isdir(os.path.join(MODS, "工具箱"))
    # 恶意越界
    st, r, _ = req("/api/move", {"src_base": "mods", "src_rel": "../仓库A",
                                 "dst_base": "root", "dst_rel": "x"})
    w(f"POST /api/move 越界 -> ok={r['ok']} {r['msg']} (应失败)")
    assert not r["ok"]

    # 13. 重命名
    st, r, _ = req("/api/rename", {"id": "工具箱", "name": "隐藏UI"})
    w(f"POST /api/rename -> ok={r['ok']} {r['msg']}")
    assert r["ok"] and os.path.isdir(os.path.join(MODS, "隐藏UI"))

    # 14. 设置主题 / 预览图
    st, r, _ = req("/api/config", {"theme": "light"})
    assert r["ok"] and r["state"]["theme"] == "light"
    st, r, _ = req("/api/config", {"hide_preview": True})
    assert r["state"]["hide_preview"] is True
    w("POST /api/config 主题/预览图 OK")

    # 14.5 全局快捷键
    st, r, _ = req("/api/config", {"hotkey": "Ctrl+Alt+K"})
    w(f"POST /api/config hotkey -> ok={r['ok']} msg={r.get('msg','')}")
    assert r["ok"] and r["state"]["hotkey"] == "Ctrl+Alt+K"
    st, r, _ = req("/api/config", {"hotkey": "K"})
    assert not r["ok"], "无修饰键的普通键应被拒绝"
    st, r, _ = req("/api/config", {"hotkey": "Ctrl+Alt+F24"})
    assert r["ok"], r.get("msg")
    w("POST /api/config hotkey OK (改键/拒绝裸键/再改键)")
    # 注: 默认 Ctrl+Alt+M 在部分机器上会被其他程序占用, 此时启动日志
    # 会打印注册失败, 设置页也会提示换键 —— 这是预期行为, 不做断言。

    # 15. 错误路径设置
    st, r, _ = req("/api/config", {"zzmi_root": "C:\\Windows"})
    w(f"POST /api/config 错误路径 -> ok={r['ok']} msg={r['msg'][:40]}...")
    assert not r["ok"]

    # 16. 404
    st, _, _ = req("/api/nope")
    assert st == 404

    w()
    w("HTTP TESTS PASSED")
finally:
    proc.terminate()
    try:
        out, _ = proc.communicate(timeout=10)
    except Exception:
        proc.kill()
        out = ""
    w()
    w("=== 服务端日志 ===")
    w((out or "").strip())
    open(OUT, "w", encoding="utf-8").write("\n".join(L))
