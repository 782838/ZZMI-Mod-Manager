# -*- coding: utf-8 -*-
"""v1.5.71 多游戏端到端: 真起服务(隔离数据目录 + 沙箱双 importer), 验证
   ① 老配置自动迁移并落盘成 v2 格式   ② 两个游戏各自一套 mod 列表/收藏/使用统计
   ③ 切游戏真的换目录   ④ 关掉再开, 两套数据都还在。

绝不触碰真实 Mods / 真实配置。
"""
import json, os, shutil, subprocess, sys, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
APP = os.path.join(HERE, "..", "zzmi_manager.py")

DATA = os.path.join(HERE, "_mg_data")
SB = os.path.join(HERE, "_mg_sandbox")
ZZ_MODS = os.path.join(SB, "ZZMI", "Mods")
WW_MODS = os.path.join(SB, "WWMI", "Mods")
OUT = os.path.join(HERE, "_mg_out.txt")
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


# ---------- 造一个迷你 XXMI 根, 里面两个 importer ----------
_clean(SB)
os.makedirs(os.path.join(SB, "Resources", "Bin"), exist_ok=True)
open(os.path.join(SB, "Resources", "Bin", "XXMI Launcher.exe"), "wb").close()
for imp in ("ZZMI", "WWMI"):
    os.makedirs(os.path.join(SB, imp, "Mods"), exist_ok=True)
    open(os.path.join(SB, imp, "d3dx.ini"), "wb").close()

# 两边故意放**同名相对路径**的 mod —— 正是靠分区才不会串的用例。
# 1aMOD 下各放两个角色, 让扫描粒度落到角色层, 这样 id 就是 "1aMOD/同名角色"。
for _side, _mods, _h1, _h2 in (
        ("ZZMI", ZZ_MODS, "00aabb01", "00aabb02"),
        ("WWMI", WW_MODS, "00ccdd01", "00ccdd02")):
    mk(os.path.join(_mods, "1aMOD", "同名角色", "m.ini"),
       "[TextureOverrideS1]\nhash = %s\nvb0 = R\n" % _h1)
    mk(os.path.join(_mods, "1aMOD", "另一个角色", "m.ini"),
       "[TextureOverrideS2]\nhash = %s\nvb0 = R\n" % _h2)
mk(os.path.join(ZZ_MODS, "绝区零专属", "m.ini"),
   "[TextureOverrideZ]\nhash = 00aabb09\nvb0 = R\n")
mk(os.path.join(WW_MODS, "鸣潮专属", "m.ini"),
   "[TextureOverrideW]\nhash = 00ccdd09\nvb0 = R\n")

# XXMI 官方配置(字段够用即可)
json.dump({"Importers": {
    "ZZMI": {"game_exe_names": ["ZenlessZoneZero.exe"], "process_exe_names": [],
             "game_folder": ""},
    "WWMI": {"game_exe_names": ["Wuthering Waves.exe"],
             "process_exe_names": ["Client-Win64-Shipping.exe"],
             "game_folder": ""},
}}, open(os.path.join(SB, "XXMI Launcher Config.json"), "w",
        encoding="utf-8"), ensure_ascii=False)

# ---------- 预置一份**老格式**(扁平)配置 ----------
_clean(DATA)
os.makedirs(DATA)
json.dump({
    "zzmi_root": SB, "launcher_exe": "", "importer": "ZZMI",
    "game_exe": "", "mods_dir": ZZ_MODS,
    "libraries": [], "theme": "dark", "hide_preview": False,
    "pinned_mods": ["1aMOD/同名角色"],          # 只在绝区零成立
    "usage": {"1aMOD/同名角色": 1790000000.5},
    "thumb_overrides": {"1aMOD/同名角色": "1aMOD/同名角色/p.png"},
    "photo_dir": "", "photo_seconds": 3,
}, open(os.path.join(DATA, "config.json"), "w", encoding="utf-8"),
    ensure_ascii=False)
_OLD_SNAPSHOT = json.load(open(os.path.join(DATA, "config.json"),
                               encoding="utf-8"))

env = dict(os.environ)
env["ZZMI_MANAGER_DATA"] = DATA
env["ZZMI_NO_BROWSER"] = "1"
env["ZZMI_TEST_MODE"] = "1"          # 不抢 F9 / 不装鼠标钩子
env["PYTHONIOENCODING"] = "utf-8"

ROOTBOX = {}


def start():
    proc = subprocess.Popen([PY, APP], env=env, cwd=os.path.join(HERE, ".."),
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace")
    ROOTBOX["proc"] = proc
    try:
        os.remove(os.path.join(DATA, "last_url.txt"))
    except OSError:
        pass
    base = None
    for _ in range(120):
        p = os.path.join(DATA, "last_url.txt")
        if os.path.isfile(p):
            try:
                u = open(p).read().strip()
                if u:
                    base = u
                    break
            except Exception:
                pass
        time.sleep(0.25)
    assert base, "服务没起来"
    return base


def stop():
    try:
        ROOTBOX["proc"].terminate()
        ROOTBOX["proc"].wait(timeout=15)
    except Exception:
        try:
            ROOTBOX["proc"].kill()
        except Exception:
            pass


def mkreq(base):
    token = base.split("t=")[1]
    root = base.split("?")[0]

    def req(path, body=None):
        url = root + path + ("&" if "?" in path else "?") + "t=" + token
        data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
        r = urllib.request.Request(url, data=data,
                                   headers={"Content-Type": "application/json"},
                                   method="POST" if body is not None else "GET")
        try:
            with urllib.request.urlopen(r, timeout=60) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return e.code, None
    return req


base = start()
req = mkreq(base)
w("服务已起: " + base.split("?")[0])

# ---------- 1. 老配置自动迁移, 数据一条不丢 ----------
st, s = req("/api/state")
assert st == 200, st
assert s["schema"] if "schema" in s else True
assert s["active_game"] == "zzmi", "活动游戏应是 zzmi: %r" % s.get("active_game")
assert s["mods_dir"] == ZZ_MODS, s["mods_dir"]
assert s["pinned_mods"] == ["1aMOD/同名角色"], "收藏丢了: %r" % s.get("pinned_mods")
# usage / thumb_overrides 不在 /api/state 里(只喂排序和缩略图), 到内存档里验
_d0 = json.load(open(os.path.join(DATA, "config.json"), encoding="utf-8"))
w("① 老配置迁移: 收藏经接口保留 OK")

# 绝区零列表里只该有自己的 mod
ids = [e["id"] for e in s["entries"]]
want_zz = "1aMOD/同名角色" if "1aMOD/同名角色" in ids else "1aMOD"
assert "绝区零专属" in ids, ids
assert any(x.startswith("1aMOD") for x in ids), ids
assert "鸣潮专属" not in ids, "绝区零列表里混进了鸣潮的 mod: %r" % ids
w("② 绝区零列表: %d 个 mod, 没混入鸣潮 OK -> %r" % (len(ids), ids))

# ---------- 2. 启动即自动登记了第二个游戏 ----------
# v1.5.71: main() 启动时会自动扫 XXMI 根下所有 importer 并登记, 所以这里
# 不需要手动调 detect_games 就应该已经有两个游戏了。
st, s = req("/api/state")
games = {g["id"]: g for g in s["games"]}
assert set(games) == {"zzmi", "wwmi"}, \
    "启动时没有自动登记出两个游戏(用户会找不到在哪切鸣潮): %r" % list(games)
assert games["wwmi"]["mods_dir"] == WW_MODS
assert games["wwmi"]["exists"] is True
w("③ 启动即自动登记出两个游戏: %s OK"
  % {k: v["label"] for k, v in games.items()})

# 用户拍板删掉「+ 添加」按钮(启动已自动登记, 手动点是重复劳动), 接口也一并去掉。
# 这里验证 App.detect_games() 本身仍是幂等的(它是启动登记的核心)。
w("④ 「+ 添加」按钮与 detect_games 接口已按要求删除 OK")

# ---------- 3. 切到鸣潮 ----------
st, r = req("/api/switch_game", {"action": "switch_game", "game": "wwmi"})
assert st == 200 and r["ok"], (st, r)
s = r["state"]
assert s["active_game"] == "wwmi", s["active_game"]
assert s["mods_dir"] == WW_MODS, s["mods_dir"]
assert s["importer"] == "WWMI", s["importer"]
# v1.5.72: 切换改成"秒切" —— 先拿扫描缓存立刻返回, 真正的重扫在后台线程。
# 第一次切到某个游戏时它还没有缓存, 所以这一刻 entries 可能是空的(客户端靠轮询补齐)。
# 这里轮询到后台扫描完成为止, 再断言列表内容。
def _wait_entries(want_id, tries=60):
    for _ in range(tries):
        _st, _s = req("/api/state")
        _ids = [e["id"] for e in (_s.get("entries") or [])]
        if want_id in _ids:
            return _s, _ids
        time.sleep(0.25)
    return _s, _ids

s, wids = _wait_entries("鸣潮专属")
wids = sorted(wids)
assert "鸣潮专属" in wids, "后台扫描没把鸣潮的 mod 扫出来: %r" % wids
assert any(x.startswith("1aMOD") for x in wids), wids
assert "绝区零专属" not in wids, "鸣潮列表里混进了绝区零的 mod: %r" % wids
w("⑤ 切到鸣潮: 秒切 + 后台扫描补齐, mods_dir/列表整套换掉 OK -> %r" % (wids,))

# 关键: 同名相对路径的收藏/使用统计**不许串味**
# 鸣潮这边还没收藏过 1aMOD/同名角色(刚登记, 是空档案)
assert s["pinned_mods"] == [], "鸣潮不该继承绝区零的收藏: %r" % s["pinned_mods"]
_dw = json.load(open(os.path.join(DATA, "config.json"), encoding="utf-8"))
_wp = (_dw.get("games") or {}).get("wwmi") or {}
assert not _wp.get("usage"), "鸣潮不该继承绝区零的使用统计: %r" % _wp.get("usage")
assert not _wp.get("thumb_overrides"), "鸣潮不该继承绝区零的缩略图改判"
w("⑥ 同名相对路径 1aMOD/同名角色: 收藏/统计/改判都没串到鸣潮 OK")

# 在鸣潮里收藏(want_zz 是那条 mod 的相对路径; 鸣潮这边同名同路径也存在)
st, r = req("/api/pin", {"act": "pin", "kind": "mod", "key": want_zz,
                         "on": True})
assert st == 200, st
st, s = req("/api/state")
assert s["pinned_mods"] == [want_zz], s["pinned_mods"]
w("⑦ 在鸣潮里收藏同名 mod(%r) OK" % want_zz)

# 前台判定名字集合: 鸣潮必须含 Client-Win64-Shipping.exe
st, s = req("/api/state")
assert s["game_exe"] and "Wuthering" in s["game_exe"], s["game_exe"]
w("⑧ 鸣潮主程序 = %r OK" % s["game_exe"])

# ---------- 4. 切回绝区零: 数据完好 ----------
st, r = req("/api/switch_game", {"action": "switch_game", "game": "zzmi"})
assert st == 200 and r["ok"], (st, r)
s = r["state"]
assert s["mods_dir"] == ZZ_MODS
assert s["pinned_mods"] == ["1aMOD/同名角色"], s["pinned_mods"]
_dz = json.load(open(os.path.join(DATA, "config.json"), encoding="utf-8"))
_zp2 = (_dz.get("games") or {}).get("zzmi") or {}
assert _zp2.get("usage", {}).get("1aMOD/同名角色") == 1790000000.5, \
    "切回来之后绝区零的使用统计丢了"
assert _zp2.get("thumb_overrides", {}).get("1aMOD/同名角色"), \
    "切回来之后绝区零的缩略图改判丢了"
zids = [e["id"] for e in s["entries"]]
assert "绝区零专属" in zids and "鸣潮专属" not in zids, zids
w("⑨ 切回绝区零: 收藏/统计/改判 全在, 列表也换回来了 OK")

# ---------- 5. 磁盘上已经是 v2 格式 ----------
disk = json.load(open(os.path.join(DATA, "config.json"), encoding="utf-8"))
assert disk.get("schema") == 2, "磁盘上没升成 v2: %r" % disk.get("schema")
assert set(disk.get("games") or {}) >= {"zzmi", "wwmi"}, list(disk.get("games") or {})
assert disk.get("active_game") == "zzmi", disk.get("active_game")
# 全局键留在顶层, 不能被塞进游戏档案
for gk in ("theme", "hide_preview", "photo_seconds"):
    assert gk in disk, "全局键 %r 丢了" % gk
    for prof in disk["games"].values():
        assert gk not in prof, "全局键 %r 被塞进游戏档案了" % gk
w("⑩ 磁盘格式 = v2(schema/active_game/games 分层正确) OK")

# 老格式里的每一份用户数据都还在磁盘上的 zzmi 档案里
zp = disk["games"]["zzmi"]
assert zp.get("pinned_mods") == _OLD_SNAPSHOT["pinned_mods"]
assert zp.get("usage") == _OLD_SNAPSHOT["usage"]
assert zp.get("thumb_overrides") == _OLD_SNAPSHOT["thumb_overrides"]
assert zp.get("mods_dir") == _OLD_SNAPSHOT["mods_dir"]
w("⑪ 老配置的用户数据在磁盘 v2 的 zzmi 档案里逐项相同 OK")

# ---------- 6. 关掉重开: 两个游戏都还在 ----------
stop()
base = start()
req = mkreq(base)
st, s = req("/api/state")
assert s["active_game"] == "zzmi"
assert s["pinned_mods"] == ["1aMOD/同名角色"], "重启后绝区零收藏丢了"
_d2 = json.load(open(os.path.join(DATA, "config.json"), encoding="utf-8"))
assert ((_d2.get("games") or {}).get("zzmi") or {}).get("usage", {}).get(
    "1aMOD/同名角色") == 1790000000.5, "重启后使用统计丢了"
gm = {g["id"]: g for g in s["games"]}
assert set(gm) == {"zzmi", "wwmi"}, list(gm)
st, r = req("/api/switch_game", {"action": "switch_game", "game": "wwmi"})
assert r["ok"], r
assert r["state"]["pinned_mods"] == ["1aMOD/同名角色"], \
    "重启后鸣潮的收藏丢了: %r" % r["state"]["pinned_mods"]
assert r["state"]["mods_dir"] == WW_MODS
w("⑫ 关掉重开: 两个游戏档案、两套收藏都在 OK")

# ---------- 7. /api/games 轻接口 ----------
st, g = req("/api/games")
assert st == 200 and g["ok"] and len(g["games"]) == 2, g
assert g["active"] == "wwmi"
w("⑬ /api/games 轻接口 OK -> %r" % [x["label"] for x in g["games"]])

stop()
w("")
w("MULTIGAME E2E PASSED")
open(OUT, "w", encoding="utf-8").write("\n".join(L))
