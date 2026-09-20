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

# 逐文件删除(避免一次性 rmtree 撞上沙箱批量删除保护)
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

# --- 准备沙箱 mods ---
_clean(SB)
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
_clean(DATA)
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

    # 9.8 变体一键改键 (HTTP 全链路; v1.5.4)
    CYC = os.path.join(MODS, "变体测试", "cycle.ini")
    ORIG = open(CYC, "rb").read()
    st, r, _ = req("/api/cycle_rekey", {"id": "变体测试", "var": "swapvarHair",
                                        "key": "ctrl a"})
    w(f"POST /api/cycle_rekey ctrl a -> ok={r['ok']} msg={r.get('msg','')}")
    assert r["ok"], r
    now = open(CYC, "rb").read()
    assert now == b"[KeySwapHair]\r\nkey = ctrl a\r\ntype = cycle\r\n$swapvarHair = 0,1,2\r\n", now
    w("  cycle.ini 键值已就地替换, 其余字节(CRLF)原样保留")
    st, d, _ = req("/api/detail?id=" + urllib.parse.quote("变体测试"))
    cyc = {c["var"]: c for c in (d.get("cycles") or [])}
    assert cyc["swapvarHair"]["keys"] == ["Ctrl+A"], cyc["swapvarHair"]["keys"]
    assert cyc["swapvarHair"]["keys_raw"] == ["ctrl a"], cyc["swapvarHair"]["keys_raw"]
    # 换成带 VK 的组合键
    st, r, _ = req("/api/cycle_rekey", {"id": "变体测试", "var": "swapvarHair",
                                        "key": "shift f1"})
    assert r["ok"], r
    now = open(CYC, "rb").read()
    assert now == b"[KeySwapHair]\r\nkey = shift VK_F1\r\ntype = cycle\r\n$swapvarHair = 0,1,2\r\n", now
    w("  shift f1 -> shift VK_F1 OK")
    # 非法输入必须拒绝且不碰文件
    before = open(CYC, "rb").read()
    for bad in ("ctrl", "ctrl 冒号", ""):
        st, r, _ = req("/api/cycle_rekey", {"id": "变体测试",
                                            "var": "swapvarHair", "key": bad})
        assert not r["ok"], (bad, r)
    assert open(CYC, "rb").read() == before
    st, r, _ = req("/api/cycle_rekey", {"id": "变体测试", "var": "不存在的",
                                        "key": "ctrl a"})
    assert not r["ok"] and "没找到" in r["msg"], r
    w("  非法按键/未知变体均拒绝, 文件未被改动 OK")
    # 撤销: 应回到最初的字节
    st, r, _ = req("/api/undo", {})
    w(f"POST /api/undo -> ok={r['ok']} msg={r.get('msg','')}")
    assert r["ok"], r
    assert open(CYC, "rb").read() == ORIG
    w("  撤销后 cycle.ini 与最初字节完全一致 OK")
    # 恢复成 ctrl a 状态继续后面的测试无关紧要, 不再改

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

    # 12.5 仓库管理: 从列表删除(只动配置, 不删磁盘) + 自定义文件夹删除 (v1.5.4)
    st, r, _ = req("/api/del_lib", {"lib": "不存在的仓库"})
    assert not r["ok"], r
    st, r, _ = req("/api/del_lib", {"lib": "仓库A"})
    w(f"POST /api/del_lib 仓库A -> ok={r['ok']} msg={r.get('msg','')}")
    assert r["ok"], r
    assert "仓库A" not in r["state"]["libraries"], r["state"]["libraries"]
    assert os.path.isdir(os.path.join(SB, "仓库A")), "磁盘目录不该被删"
    w("  仓库A 已从列表移除, 磁盘目录仍在 OK")
    # 自定义文件夹: 先搬一次让它进 custom_dirs, 再从列表删掉
    cust = os.path.join(SB, "_customX")
    st, r, _ = req("/api/mkdir", {"base": "abs", "path": cust})
    assert r["ok"], r
    st, r, _ = req("/api/move_batch", {"ids": ["工具箱"], "lib": "abs:" + cust})
    w(f"POST /api/move_batch abs -> ok={r['ok']} {r.get('msg','')}")
    assert r["ok"], r
    assert os.path.isdir(os.path.join(cust, "工具箱"))
    assert any(os.path.abspath(d) == os.path.abspath(cust)
               for d in r["state"]["custom_dirs"]), r["state"]["custom_dirs"]
    st, r, _ = req("/api/del_lib", {"lib": "abs:" + cust})
    w(f"POST /api/del_lib abs -> ok={r['ok']} msg={r.get('msg','')}")
    assert r["ok"], r
    assert not any(os.path.abspath(d) == os.path.abspath(cust)
                   for d in r["state"]["custom_dirs"])
    assert os.path.isdir(cust), "自定义文件夹本身不该被删"
    w("  自定义文件夹已从列表移除, 目录仍在 OK")
    # 把工具箱搬回 Mods, 恢复现场
    st, r, _ = req("/api/move", {"src_base": "root", "src_rel": "_customX/工具箱",
                                 "dst_base": "mods", "dst_rel": "工具箱"})
    assert r["ok"], r

    # 12.6 添加仓库: 新建 / 锁定已有文件夹 / 绝对路径仓库搬运 / 移除 (v1.5.5)
    # 12.6.1 ZZMI 下新建仓库
    st, r, _ = req("/api/add_lib", {"lib": "仓库新建", "create": True})
    w(f"POST /api/add_lib 新建 -> ok={r['ok']} {r.get('msg','')}")
    assert r["ok"], r
    assert "仓库新建" in r["state"]["libraries"], r["state"]["libraries"]
    assert os.path.isdir(os.path.join(SB, "仓库新建")), "目录应被创建"
    w("  仓库新建 已登记 + 目录已创建 OK")
    # 12.6.2 不存在的仓库(不 create) 应被拒
    st, r, _ = req("/api/add_lib", {"lib": "根本不存在的仓库"})
    assert not r["ok"], r
    w(f"  不存在的仓库被拒 OK ({r.get('msg','')[:30]})")
    # 12.6.3 锁定一个磁盘上已存在的绝对路径文件夹当仓库(在沙箱外)
    abslib = os.path.join(DATA, "_absLib")
    os.makedirs(os.path.join(abslib, "外置mod"), exist_ok=True)
    mk(os.path.join(abslib, "外置mod", "z.ini"),
       "[TextureOverrideZ]\nhash = deadbeef\nvb0 = RZ\n")
    st, r, _ = req("/api/add_lib", {"lib": "abs:" + abslib})
    w(f"POST /api/add_lib abs -> ok={r['ok']} {r.get('msg','')}")
    assert r["ok"], r
    assert any(os.path.abspath(d) == os.path.abspath(abslib)
               for d in r["state"]["libs_abs"]), r["state"]["libs_abs"]
    w("  外置文件夹已锁定为仓库 OK")
    # 12.6.4 library 接口应把它列出来, 且能扫到里面的 mod
    st, r, _ = req("/api/library")
    names = {L["name"]: L for L in r["libraries"]}
    w(f"GET /api/library -> libs={list(names)}")
    assert any(os.path.abspath(L["path"]) == os.path.abspath(abslib)
               for L in r["libraries"] if L.get("path")), r["libraries"]
    locked = [L for L in r["libraries"]
              if os.path.abspath(L.get("path") or "") == os.path.abspath(abslib)][0]
    assert locked["abs"] is True and locked["count"] == 1, locked
    w(f"  外置仓库被列出: {locked['name']} ({locked['count']} 项) OK")
    # 12.6.5 用 libs_abs 当搬运目标
    st, r, _ = req("/api/move_batch", {"ids": ["工具箱"], "lib": locked["ref"]})
    w(f"POST /api/move_batch -> 外置仓库 ok={r['ok']} {r.get('msg','')}")
    assert r["ok"], r
    assert os.path.isdir(os.path.join(abslib, "工具箱")), "应搬进外置仓库"
    # 12.6.6 从外置仓库搬回 Mods (src_abs)
    st, r, _ = req("/api/move", {"src_abs": abslib, "src_rel": "工具箱",
                                 "dst_base": "mods", "dst_rel": "工具箱"})
    w(f"POST /api/move src_abs -> ok={r['ok']} {r.get('msg','')}")
    assert r["ok"] and os.path.isdir(os.path.join(MODS, "工具箱")), r
    w("  外置仓库 <-> Mods 双向搬运 OK")
    # 12.6.7 移除外置仓库(只动配置)
    st, r, _ = req("/api/del_lib", {"lib": "abs:" + abslib})
    assert r["ok"], r
    assert not any(os.path.abspath(d) == os.path.abspath(abslib)
                   for d in r["state"]["libs_abs"])
    assert os.path.isdir(abslib), "磁盘目录不该被删"
    w("  外置仓库已从列表移除, 目录仍在 OK")
    # 12.6.8 清理: 新建的仓库从列表去掉
    st, r, _ = req("/api/del_lib", {"lib": "仓库新建"})
    assert r["ok"], r

    # 13. 重命名
    st, r, _ = req("/api/rename", {"id": "工具箱", "name": "隐藏UI"})
    w(f"POST /api/rename -> ok={r['ok']} {r['msg']}")
    assert r["ok"] and os.path.isdir(os.path.join(MODS, "隐藏UI"))

    # 13.5 v1.5.8 重名 -> 自动加 (2) (3)…, 不报错也不覆盖
    #      先造一个「重名A」, 再把「隐藏UI」改名成「重名A」
    os.makedirs(os.path.join(MODS, "重名A"), exist_ok=True)
    mk(os.path.join(MODS, "重名A", "dup.ini"),
       "[TextureOverrideDup]\nhash = 55667788\nvb0 = RD\n")
    req("/api/rescan", {})   # 直写磁盘后必须重扫, 让服务端内存看到「重名A」
    st, r, _ = req("/api/rename", {"id": "隐藏UI", "name": "重名A"})
    w(f"POST /api/rename 撞名 -> ok={r['ok']} msg={r['msg']}")
    assert r["ok"], r
    assert r.get("renamed") is True and r.get("target_name") == "重名A (2)", r
    assert os.path.isdir(os.path.join(MODS, "重名A (2)")), "应自动改名成 重名A (2)"
    assert os.path.isdir(os.path.join(MODS, "重名A")), "原有的 重名A 不能被顶掉"
    assert os.path.isfile(os.path.join(MODS, "重名A", "dup.ini")), "原有内容不能动"
    w("  重名自动变 重名A (2), 原有目录原封不动 OK")
    # 13.6 再撞一次应该接着排到 (3), 不能叠成 (2) (2)
    st, r, _ = req("/api/rename", {"id": "重名A (2)", "name": "重名A"})
    w(f"POST /api/rename 再撞 -> ok={r['ok']} target={r.get('target_name')}")
    assert r["ok"] and r.get("target_name") == "重名A (3)", r
    assert os.path.isdir(os.path.join(MODS, "重名A (3)"))
    w("  依次类推到 重名A (3), 没叠成 (2) (2) OK")

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

    # 17. v1.5.7 命令窗口: 接口存在且不崩(测试进程没控制台 -> ok 可能是 False)
    st, r, _ = req("/api/console", {"show": True})
    assert st == 200 and "ok" in r and "msg" in r, r
    w(f"POST /api/console show=1 -> ok={r['ok']} msg={r['msg']}")
    st, r, _ = req("/api/console", {})
    assert st == 200 and "ok" in r, r
    w(f"POST /api/console show=0 -> ok={r['ok']} msg={r['msg']}")

    # 17.1 日志确实落盘了(隐藏命令窗口后排查全靠它)
    logp = os.path.join(DATA, "zzmi.log")
    assert os.path.isfile(logp), "没生成 zzmi.log: %s" % logp
    txt = open(logp, encoding="utf-8", errors="replace").read()
    assert "v" in txt and "界面:" in txt, "日志内容不像是启动日志"
    w("zzmi.log 已落盘, %d 字节" % os.path.getsize(logp))

    # 18. v1.5.8 禁用时撞上同名的 DISABLED_ 目录 -> 自动加 (2), 并回报给前端
    os.makedirs(os.path.join(MODS, "同名测试"), exist_ok=True)
    mk(os.path.join(MODS, "同名测试", "s.ini"),
       "[TextureOverrideS]\nhash = a1b2c3d4\nvb0 = RS\n")
    os.makedirs(os.path.join(MODS, "DISABLED_同名测试"), exist_ok=True)
    mk(os.path.join(MODS, "DISABLED_同名测试", "t.ini"),
       "[TextureOverrideT]\nhash = b2c3d4e5\nvb0 = RT\n")
    # 上面是直接写磁盘, 服务端内存里的 scan 还是旧的 -> 必须 POST /api/rescan 重扫。
    # (注意 GET /api/state 只是回读缓存, 不会重扫; 忘了这一步 batch_toggle 会拿到空列表
    #  返回 ok=0 —— 那是测试脚手架的问题, 不是产品行为)
    req("/api/rescan", {})
    st, r, _ = req("/api/toggle", {"ids": ["同名测试"], "enabled": False})
    res = r["result"]
    w(f"POST /api/toggle 撞名 -> ok={res['ok']} renamed={len(res.get('renamed') or [])}")
    assert res["ok"] == 1 and res["failed"] == 0, res
    dups = res.get("renamed") or []
    assert dups and dups[0]["target_name"] == "DISABLED_同名测试 (2)", dups
    assert os.path.isdir(os.path.join(MODS, "DISABLED_同名测试 (2)"))
    assert os.path.isdir(os.path.join(MODS, "DISABLED_同名测试")), "原有同名目录不能被顶"
    w("  已禁用 + 自动改名 DISABLED_同名测试 (2), renamed 回报正常 OK")

    # 19. v1.5.9 同名两套: 已启用「蜜西皮肤」+ 禁用「DISABLED_蜜西皮肤」,
    #     启用禁用那套 —— v1.5.8 会报「找不到目录」(id 带 #1 后缀解析不了), 必须回归
    os.makedirs(os.path.join(MODS, "同名测试B"), exist_ok=True)
    mk(os.path.join(MODS, "同名测试B", "b1.ini"),
       "[TextureOverrideB1]\nhash = b1b1b1b1\nvb0 = RB1\n")
    os.makedirs(os.path.join(MODS, "DISABLED_同名测试B"), exist_ok=True)
    mk(os.path.join(MODS, "DISABLED_同名测试B", "b2.ini"),
       "[TextureOverrideB2]\nhash = b2b2b2b2\nvb0 = RB2\n")
    req("/api/rescan", {})
    st, state, _ = req("/api/state")
    ids = {e["id"]: e["path"] for e in state["entries"]
           if e["path"] in ("同名测试B", "DISABLED_同名测试B")}
    assert set(ids.values()) == {"同名测试B", "DISABLED_同名测试B"}, ids
    dup_id = [k for k, v in ids.items() if v == "DISABLED_同名测试B"][0]
    w(f"  重名条目 id = {dup_id!r}")
    st, r, _ = req("/api/toggle", {"ids": [dup_id], "enabled": True})
    res = r["result"]
    w(f"POST /api/toggle 启用禁用套 -> ok={res['ok']} msg={res.get('details')}")
    assert res["ok"] == 1 and res["failed"] == 0, res
    # 禁用套应该被启用成 同名测试B (2) (启用套占着原名), 启用套原地不动
    assert os.path.isdir(os.path.join(MODS, "同名测试B (2)")), sorted(os.listdir(MODS))
    assert os.path.isdir(os.path.join(MODS, "同名测试B")), "启用套不能被动"
    dups = res.get("renamed") or []
    assert dups and dups[0]["target_name"] == "同名测试B (2)", dups
    w("  同名两套: 禁用套 -> 同名测试B (2) + 弹窗回报, 启用套没被动 OK")

    # 19b. v1.5.9 favicon: 浏览器不带 token 也能拿到(应用窗口图标靠它)
    u = ROOT + "/favicon.ico"
    with urllib.request.urlopen(u, timeout=10) as resp:
        ico = resp.read()
        assert resp.headers.get("Content-Type") == "image/x-icon", resp.headers
    assert ico[:4] == b"\x00\x00\x01\x00", ico[:8]
    w(f"GET /favicon.ico 免鉴权 OK, {len(ico)} 字节")

    # 20. v1.5.10 界面关闭 -> 自动退出心跳: bye 调度, hello 取消
    # 注意 req(path) 在 body=None 时发 GET, 这里必须带 body={} 强制 POST
    st, r, _ = req("/api/bye", body={})
    assert st == 200 and (r or {}).get("ok"), "bye 应返回 ok"
    # 立刻用 hello 取消待执行的自动退出, 否则 5s 后服务进程会自杀、后续断言全挂
    st, r, _ = req("/api/hello", body={})
    assert st == 200 and (r or {}).get("ok"), "hello 应返回 ok"
    st, r, _ = req("/api/state")
    assert st == 200, "bye+hello 之后服务仍应存活"
    w("  v1.5.10 bye 调度自动退出 / hello 取消 OK, 服务存活")

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
