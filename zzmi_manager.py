#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZZMI Mod 管家  (ZZMI Mod Manager)
=========================================
绝区零 ZZMI / XXMI Launcher 的 Mod 管理界面。

v1.3 更新
---------
* 热键循环变体: 解析 ini 里 [Key*] 段的 `$var = 0,1,2` + `type = cycle`
  (游戏里按 H// 等键循环切换的那种), 在界面里做成变体按钮;
  切换 = 旋转循环列表让目标值排第一 (mod 加载时直接处于该变体), 完全可逆
* 全局快捷键: 可自定义(默认 Ctrl+Alt+M), 绝区零运行时按下即可呼出/隐藏管理器窗口

v1.2 更新
---------
* 部件 / 变体开关: 解析每个 mod 内所有 ini 的 TextureOverride hash,
  自动把「覆盖同一游戏资源」的文件归为一个变体组(组内只能开一个, 一键切换);
  不冲突的文件做成独立开关(如 face / body / 附加件)
* 文件级禁用: 文件名加 `DISABLED_` 前缀, 与目录级同一套机制, 永不删文件、可撤销
* 备份副本(DISABLED_BACKUP_* / disabled_beifen_* 等)自动识别并排除, 不会误报变体

v1.1 更新
---------
* 独立窗口: 用 Edge/Chrome 的 --app 模式打开, 看起来就是个软件窗口;
  并强制 `--proxy-server=direct://` 绕过系统代理(很多人 127.0.0.1 被代理拦截导致界面点不动)
* 服务端缩略图: 预览图统一压成 420px JPEG 缓存, 列表秒开不再卡
* 按角色分类: 自动从 mod 名推断角色(可手改), 一个角色多套 mod 一眼看清、一键只留一套
* 连接失败提示: 打不开后端时界面会明确告诉你怎么做

技术要点
--------
* 纯 Python 标准库; 缩略图在有 Pillow 时用 Pillow, 没有就回退原图
* 只绑 127.0.0.1, 带一次性访问令牌
* 禁用 = 目录名加 `DISABLED_` 前缀 (官方 d3dx.ini: exclude_recursive = DISABLED*), 永不删文件
* 所有写操作写 journal, 可撤销

环境变量
--------
ZZMI_MANAGER_DATA  自定义数据目录
ZZMI_NO_BROWSER=1  不自动打开窗口
"""

import hashlib
import json
import mimetypes
import os
import queue
import re
import shutil
import socket
import string
import subprocess
import sys
import threading
import time
import traceback
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

VERSION = "1.4.5"
APP_NAME = "ZZMI Mod 管家"

DISABLED_PREFIX = "DISABLED_"
DISABLED_TEST = re.compile(r"^(?:disabled|禁用)", re.IGNORECASE)

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".avif")
PREVIEW_PRIORITY = ("preview", "cover", "thumb", "screenshot", "default", "1", "0")

DATA_DIR = (os.environ.get("ZZMI_MANAGER_DATA")
            or os.path.join(os.path.expanduser("~"), ".zzmi-manager"))
CONFIG_PATH = os.path.join(DATA_DIR, "config.json")
PRESETS_PATH = os.path.join(DATA_DIR, "presets.json")
JOURNAL_PATH = os.path.join(DATA_DIR, "journal.jsonl")
THUMB_DIR = os.path.join(DATA_DIR, "thumbs")
THUMB_PX = 420


def _res_dir():
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS",
                       os.path.dirname(os.path.abspath(sys.executable)))
    return os.path.dirname(os.path.abspath(__file__))


UI_PATH = os.path.join(_res_dir(), "ui.html")
BG_PATH = os.path.join(_res_dir(), "bg.jpg")

DEFAULT_CONFIG = {
    "zzmi_root": "",
    "launcher_exe": "",
    "importer": "ZZMI",
    "game_exe": "",
    "mods_dir": "",
    "libraries": [],
    "theme": "dark",
    "hide_preview": False,
    "char_overrides": {},
    "win_size": "1320,880",
    "hotkey": "F9",
}

ROOT_SKIP = {"resources", "themes", "locale", "backups", "dds", "bin",
             "strings", "packages", "cache", "security", "debugger"}
IMPORTER_SKIP = {"mods", "core", "shadercache", "shaderfixes", "debugger"}
LIB_NAME_SKIP = ("reshade", "preset", "shader", "cache", "backup", "debug",
                 "log", "temp")


# ===========================================================================
# 基础工具
# ===========================================================================

def log(*a):
    try:
        sys.stdout.write("[%s] %s\n" % (time.strftime("%H:%M:%S"),
                                        " ".join(str(x) for x in a)))
        sys.stdout.flush()
    except Exception:
        pass


def is_disabled_name(name):
    return bool(DISABLED_TEST.match(name or ""))


def strip_disabled(name):
    n = name or ""
    while True:
        m = DISABLED_TEST.match(n)
        if not m:
            break
        n = n[m.end():].lstrip("_- ")
    return n or (name or "")


def human_size(n):
    n = float(n or 0)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return ("%.0f %s" % (n, unit)) if unit == "B" else ("%.1f %s" % (n, unit))
        n /= 1024.0


def human_time(ts):
    try:
        return time.strftime("%m-%d %H:%M", time.localtime(ts))
    except Exception:
        return ""


def read_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def write_json(path, obj):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def norm_rel(p):
    return (p or "").replace("\\", "/").strip("/")


def safe_join(base, rel):
    rel = (rel or "").replace("/", os.sep).replace("\\", os.sep)
    rel = rel.strip(os.sep)
    if not rel:
        return None
    parts = [p for p in rel.split(os.sep) if p not in ("", ".")]
    if any(p == ".." for p in parts):
        return None
    if os.path.isabs(rel) or re.match(r"^[a-zA-Z]:", rel):
        return None
    p = os.path.normpath(os.path.join(base, *parts))
    if not os.path.abspath(p).startswith(os.path.abspath(base) + os.sep):
        return None
    return p


def resolve_rel_dir(base, rel):
    """按相对路径找目录, 允许任意一段带 DISABLED_ / disabled 前缀。"""
    cur = base
    for part in norm_rel(rel).split("/"):
        if not part:
            continue
        try:
            names = os.listdir(cur)
        except OSError:
            return None
        if part in names and os.path.isdir(os.path.join(cur, part)):
            cur = os.path.join(cur, part)
            continue
        hit = None
        for n in names:
            if os.path.isdir(os.path.join(cur, n)) and \
                    strip_disabled(n) == strip_disabled(part):
                hit = n
                break
        if hit is None:
            return None
        cur = os.path.join(cur, hit)
    return cur


# ===========================================================================
# 角色推断
# ===========================================================================

CHAR_VARIANT = {"零号", "异色", "sp", "邦布"}
CHAR_GENERIC_HEAD = {"功能", "工具", "修复", "整合", "其他", "杂项", "未分类",
                     "ui", "uid", "mod", "测试"}
CHAR_WORDS = [
    "微型比基尼", "微比基尼", "吊带比基尼", "条形比基尼", "奶牛比基尼", "比基尼",
    "反兔女郎", "兔女郎", "泳装", "泳衣", "奶牛", "皮肤", "常服丰满", "常服",
    "紧身连衣裤", "身体写作", "身体涂鸦", "身体彩绘", "束缚", "机甲", "切换",
    "替换", "性感的牛", "美丽的豹子", "迷人", "性感", "全裸", "怀孕", "多切换",
    "暗影", "奶盖", "小围裙", "重制", "汉化", "整合", "修复", "逆兔", "正兔",
    "白丝", "黑丝", "破洞", "淫纹", "涂鸦", "写作", "菜单", "模式", "银兎",
]
CHAR_TAIL_DROP = re.compile(r"(v\d+(\.\d+)*|[0-9]+(\.[0-9]+)*|[a-zA-Z]+)$")
STRIP_CHARS = " -_·—－・/."


def auto_char(name):
    """从 mod 名推断角色名; 推断不出来就返回原名。"""
    base = strip_disabled(name or "").strip()
    if not base:
        return base
    segs = [s for s in re.split(r"[-_·—－・/ &+]+", base) if s]
    changed = False
    if len(segs) > 1 and segs[0].lower() in {v.lower() for v in CHAR_VARIANT}:
        segs = segs[1:]
        changed = True
    h = segs[0] if segs else base
    for _ in range(5):
        before = h
        low = h.lower()
        for w in sorted(CHAR_WORDS, key=len, reverse=True):
            wl = w.lower().strip()
            if not wl:
                continue
            if low.endswith(wl) and len(h) > len(wl):
                h = h[:-len(wl)].strip(STRIP_CHARS + "0123456789.")
                break
            if low.startswith(wl) and len(h) - len(wl) >= 2:
                h = h[len(wl):].strip(STRIP_CHARS)
                break
        if h != before:
            continue
        m = CHAR_TAIL_DROP.search(h)
        if m and m.start() >= 2:
            h = h[:m.start()].strip(STRIP_CHARS)
        if h == before:
            break
    h = h.strip(STRIP_CHARS)
    if not h or h.lower() in CHAR_GENERIC_HEAD:
        return base
    if h == base and not changed:
        return base
    return h


# ===========================================================================
# 自动探测 ZZMI
# ===========================================================================

def score_xxmi_root(d):
    if not d or not os.path.isdir(d):
        return 0, {}
    score = 0
    info = {"importers": [], "launcher_exe": "", "config_json": ""}
    for cand in (os.path.join(d, "Resources", "Bin", "XXMI Launcher.exe"),
                 os.path.join(d, "XXMI Launcher.exe")):
        if os.path.isfile(cand):
            info["launcher_exe"] = cand
            score += 6
            break
    cfg = os.path.join(d, "XXMI Launcher Config.json")
    if os.path.isfile(cfg):
        info["config_json"] = cfg
        score += 3
    try:
        for name in os.listdir(d):
            if os.path.isfile(os.path.join(d, name, "d3dx.ini")):
                info["importers"].append(name)
    except Exception:
        pass
    if info["importers"]:
        score += 4
    return score, info


def root_scan_candidates():
    cands, seen = [], set()

    def add(p):
        try:
            p = os.path.normpath(p)
        except Exception:
            return
        if p and p not in seen and os.path.isdir(p):
            seen.add(p)
            cands.append(p)

    for letter in string.ascii_uppercase:
        root = letter + ":\\"
        if not os.path.isdir(root):
            continue
        try:
            for name in os.listdir(root):
                if not name.startswith("$"):
                    add(os.path.join(root, name))
        except Exception:
            pass
    home = os.path.expanduser("~")
    for p in (os.path.join(home, "AppData", "Roaming", "XXMI Launcher"),
              os.path.join(home, "AppData", "Local", "XXMI Launcher"),
              os.path.join(home, "XXMI Launcher"),
              os.path.join(home, "Desktop"),
              os.path.join(home, "Downloads"),
              os.path.join(home, "Documents")):
        add(p)
    for letter in string.ascii_uppercase:
        for lib in ("%s:\\SteamLibrary\\steamapps\\common" % letter,
                    "%s:\\STEAM\\steamapps\\common" % letter,
                    "%s:\\Program Files" % letter,
                    "%s:\\Program Files (x86)" % letter):
            if not os.path.isdir(lib):
                continue
            try:
                for name in os.listdir(lib):
                    if re.search(r"xxmi|zzmi|3d ?migoto|mod", name, re.I):
                        add(os.path.join(lib, name))
            except Exception:
                pass
    return cands


def autodetect_config(progress=None):
    hits = []
    cands = root_scan_candidates()
    total = len(cands)
    for i, d in enumerate(cands):
        if progress and i % 20 == 0:
            progress(i, total)
        s, info = score_xxmi_root(d)
        if s >= 8:
            hits.append((s, d, info))
    if progress:
        progress(total, total)
    if not hits:
        return None, []
    hits.sort(key=lambda x: -x[0])
    _, best_dir, info = hits[0]
    importers = info.get("importers") or []
    importer = "ZZMI"
    if importers:
        importer = ([x for x in importers if x.upper() == "ZZMI"]
                    or [x for x in importers if "ZZ" in x.upper()] or importers)[0]
    cfg = dict(DEFAULT_CONFIG)
    cfg["zzmi_root"] = best_dir
    cfg["launcher_exe"] = info.get("launcher_exe", "")
    cfg["importer"] = importer
    cfg["mods_dir"] = os.path.join(best_dir, importer, "Mods")
    cfg["game_exe"] = game_exe_from_launcher_config(info.get("config_json"), importer)
    cfg["libraries"] = detect_libraries(best_dir, cfg["mods_dir"])
    return cfg, [{"root": d, "importers": hi.get("importers", [])}
                 for _, d, hi in hits[:12]]


def _walk_strings(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            for s in _walk_strings(v):
                yield s
    elif isinstance(obj, list):
        for v in obj:
            for s in _walk_strings(v):
                yield s
    elif isinstance(obj, str):
        yield obj


def game_exe_from_launcher_config(config_json, importer):
    try:
        lj = read_json(config_json or "", {})
        im = (lj.get("Importers") or {}).get(importer) or {}
        gf = im.get("game_folder") or ""
        names = im.get("game_exe_names") or []
        if gf and names:
            exe = os.path.join(gf, names[0])
            if os.path.isfile(exe):
                return exe
        for s in _walk_strings(im):
            s = s.strip().strip('"')
            if not s or not os.path.isdir(s):
                continue
            try:
                files = os.listdir(s)
            except OSError:
                continue
            exes = [f for f in files if f.lower().endswith(".exe")
                    and "crash" not in f.lower() and "uninstall" not in f.lower()]
            if not exes:
                continue
            pref = [f for f in exes if re.search(
                r"zenless|starrail|genshin|wuthering|nap", f, re.I)]
            return os.path.join(s, (pref or exes)[0])
    except Exception:
        pass
    return ""


def _mod_content_stats(p, budget=400):
    n_ini = n_dds = n_ib = 0
    for cur, dirs, files in os.walk(p):
        dirs[:] = [d for d in dirs if d.lower() != "desktop.ini"]
        for f in files:
            low = f.lower()
            if low.endswith(".ini"):
                n_ini += 1
            elif low.endswith(".dds"):
                n_dds += 1
            elif low.endswith(".ib"):
                n_ib += 1
        if n_ini + n_dds + n_ib > budget:
            break
    return n_ini, n_dds, n_ib


def detect_libraries(zzmi_root, mods_dir):
    out = []
    if not os.path.isdir(zzmi_root):
        return out
    mods_abs = os.path.abspath(mods_dir) if mods_dir else ""
    importer_dirs = set()
    try:
        for name in os.listdir(zzmi_root):
            if os.path.isfile(os.path.join(zzmi_root, name, "d3dx.ini")):
                importer_dirs.add(name)
    except Exception:
        pass

    def consider(p, rel, depth):
        if os.path.abspath(p) == mods_abs or depth > 2:
            return
        if any(k in os.path.basename(rel).lower() for k in LIB_NAME_SKIP):
            return
        n_ini, n_dds, n_ib = _mod_content_stats(p)
        if n_ini >= 1 or n_dds >= 20 or n_ib >= 20:
            out.append(rel)

    for imp in sorted(importer_dirs):
        base = os.path.join(zzmi_root, imp)
        try:
            for name in sorted(os.listdir(base)):
                sp = os.path.join(base, name)
                if not os.path.isdir(sp) or name.startswith("."):
                    continue
                if name.lower() in IMPORTER_SKIP:
                    continue
                consider(sp, imp + "/" + name, 2)
        except Exception:
            pass
    try:
        for name in sorted(os.listdir(zzmi_root)):
            sp = os.path.join(zzmi_root, name)
            if not os.path.isdir(sp) or name.startswith("."):
                continue
            if name in importer_dirs or name.lower() in ROOT_SKIP:
                continue
            consider(sp, name, 1)
    except Exception:
        pass
    return out


# ===========================================================================
# 缩略图
# ===========================================================================

_thumb_q = queue.Queue()
_thumb_done = set()
_thumb_lock = threading.Lock()
_PIL = None
_PIL_CHECKED = False


def _get_pil():
    global _PIL, _PIL_CHECKED
    if not _PIL_CHECKED:
        _PIL_CHECKED = True
        try:
            from PIL import Image  # noqa
            _PIL = Image
        except Exception:
            _PIL = None
        log("缩略图引擎:", "Pillow" if _PIL else "无(直接用原图)")
    return _PIL


def thumb_key(src):
    import hashlib
    try:
        st = os.stat(src)
        raw = "%s|%d|%d" % (src.lower(), st.st_size, int(st.st_mtime))
    except OSError:
        raw = src.lower()
    return hashlib.md5(raw.encode("utf-8")).hexdigest()[:20] + ".jpg"


def make_thumb(src, dst, maxpx=THUMB_PX):
    Image = _get_pil()
    if not Image:
        return False
    try:
        with Image.open(src) as im:
            im = im.convert("RGB")
            im.thumbnail((maxpx, maxpx * 2))
            im.save(dst, "JPEG", quality=84)
        return True
    except Exception:
        try:
            if os.path.exists(dst):
                os.remove(dst)
        except OSError:
            pass
        return False


def cached_thumb(src):
    if not src:
        return None
    p = os.path.join(THUMB_DIR, thumb_key(src))
    return p if os.path.isfile(p) else None


def thumb_worker():
    while True:
        src = _thumb_q.get()
        if src is None:
            break
        try:
            if not os.path.isfile(src):
                continue
            dst = os.path.join(THUMB_DIR, thumb_key(src))
            if os.path.isfile(dst):
                continue
            if make_thumb(src, dst):
                with _thumb_lock:
                    _thumb_done.add(src)
        except Exception:
            pass
        finally:
            _thumb_q.task_done()


def enqueue_thumbs(abs_paths):
    os.makedirs(THUMB_DIR, exist_ok=True)
    n = 0
    for p in abs_paths:
        if p in _thumb_done:
            continue
        if os.path.isfile(os.path.join(THUMB_DIR, thumb_key(p))):
            with _thumb_lock:
                _thumb_done.add(p)
            continue
        _thumb_q.put(p)
        n += 1
    return n


# ===========================================================================
# 扫描
# ===========================================================================

class ScanResult(object):
    def __init__(self):
        self.root = ""
        self.entries = []
        self.by_id = {}
        self.categories = []
        self.chars = []
        self.stats = {"total": 0, "enabled": 0, "disabled": 0, "size": 0,
                      "size_h": "0 B", "files": 0, "conflicts": 0, "partial": 0,
                      "chars": 0, "multi_chars": 0}
        self.conflicts = []
        self.thumb_srcs = []
        self.scanned_at = 0
        self.duration = 0


def find_mods_dir(cfg):
    md = cfg.get("mods_dir") or ""
    if md and os.path.isdir(md):
        return md
    root = cfg.get("zzmi_root") or ""
    imp = cfg.get("importer") or "ZZMI"
    cand = os.path.join(root, imp, "Mods")
    if os.path.isdir(cand):
        return cand
    try:
        for name in os.listdir(root):
            sub = os.path.join(root, name, "Mods")
            if os.path.isdir(sub):
                return sub
    except Exception:
        pass
    return md or ""


def scan_mods(mods_dir, char_overrides=None):
    char_overrides = char_overrides or {}
    t0 = time.time()
    res = ScanResult()
    res.root = mods_dir
    if not os.path.isdir(mods_dir):
        res.duration = time.time() - t0
        return res

    dir_info = {}
    ini_dirs = []
    total_files = total_size = 0

    for cur, dirs, files in os.walk(mods_dir):
        dirs[:] = [d for d in dirs if d.lower() != "desktop.ini"]
        rel = os.path.relpath(cur, mods_dir)
        rel = "" if rel == "." else rel
        parts = rel.split(os.sep) if rel else []
        local_ini = [f for f in files if f.lower().endswith(".ini")]
        imgs = [f for f in files if f.lower().endswith(IMAGE_EXTS)]
        sz = 0
        for f in files:
            try:
                sz += os.path.getsize(os.path.join(cur, f))
            except OSError:
                pass
        total_files += len(files)
        total_size += sz
        try:
            mt = os.path.getmtime(cur)
        except OSError:
            mt = 0
        dir_info[cur] = {
            "rel": rel, "name": os.path.basename(cur), "parts": parts,
            "depth": len(parts), "size": sz, "files": len(files), "mtime": mt,
            "ini": local_ini, "imgs": imgs,
            "disabled": any(is_disabled_name(p) for p in parts),
        }
        if local_ini:
            ini_dirs.append(cur)

    if not ini_dirs:
        res.stats = {"total": 0, "enabled": 0, "disabled": 0, "partial": 0,
                     "chars": 0, "multi_chars": 0, "size": total_size,
                     "size_h": human_size(total_size), "files": total_files,
                     "conflicts": 0}
        res.duration = time.time() - t0
        return res

    def mod_root_for(d):
        cur = d
        for _ in range(8):
            parent = os.path.dirname(cur)
            if os.path.abspath(parent) == os.path.abspath(mods_dir):
                break
            pinfo = dir_info.get(parent)
            if pinfo is None or pinfo["depth"] <= 1 or pinfo["ini"]:
                break
            cur = parent
        return cur

    def is_ancestor(a, b):
        a, b = os.path.abspath(a), os.path.abspath(b)
        return b != a and b.startswith(a + os.sep)

    cand = {}
    for d in ini_dirs:
        cand.setdefault(mod_root_for(d), []).append(d)
    kept = []
    for r in sorted(cand, key=lambda p: dir_info[p]["depth"]):
        if not any(is_ancestor(k, r) for k in kept):
            kept.append(r)
    roots = {k: [d for d in ini_dirs
                 if os.path.abspath(d) == os.path.abspath(k) or is_ancestor(k, d)]
             for k in kept}

    hashes_by_dir = collect_hashes(ini_dirs, dir_info)

    entries = []
    for root_abs, sub_inis in roots.items():
        info = dir_info[root_abs]
        parts = info["parts"]

        def in_sub(k, _r=root_abs):
            return k == _r or k.startswith(_r + os.sep)

        sub_size = sum(v["size"] for k, v in dir_info.items() if in_sub(k))
        sub_files = sum(v["files"] for k, v in dir_info.items() if in_sub(k))
        sub_ini = sum(len(v["ini"]) for k, v in dir_info.items() if in_sub(k))
        hs = set()
        sub_dirs = []
        for k, v in dir_info.items():
            if not in_sub(k):
                continue
            hs |= hashes_by_dir.get(k, set())
            if k == root_abs:
                continue
            sub_dirs.append({
                "rel": norm_rel(os.path.relpath(k, mods_dir)),
                "local": norm_rel(os.path.relpath(k, root_abs)),
                "disabled": v["disabled"], "ini": len(v["ini"]),
                "imgs": len(v["imgs"]), "files": v["files"],
            })
        sub_dirs.sort(key=lambda s: s["local"].lower())

        logical = [strip_disabled(p) for p in parts]
        name = parts[-1]
        cid = "/".join(logical)
        char_auto = auto_char(name)
        char = (char_overrides.get(cid) or char_overrides.get(norm_rel(info["rel"]))
                or char_auto)
        thumb_rel = pick_preview(root_abs, dir_info, sub_inis, mods_dir)

        entries.append({
            "id": cid,
            "name": name,
            "char": char,
            "char_auto": char_auto,
            "char_manual": bool(cid in char_overrides
                                or norm_rel(info["rel"]) in char_overrides),
            "path": norm_rel(info["rel"]),
            "category": parts[0] if len(parts) > 1 else "(根目录)",
            "depth": len(parts),
            "enabled": not info["disabled"],
            "dir_disabled": info["disabled"],
            "partial": bool(not info["disabled"]
                            and any(s["disabled"] for s in sub_dirs)),
            "ini_count": sub_ini,
            "ini_roots": [norm_rel(os.path.relpath(p, mods_dir)) for p in sub_inis],
            "sub_dirs": sub_dirs[:200],
            "files": sub_files, "size": sub_size, "size_h": human_size(sub_size),
            "mtime": info["mtime"], "mtime_h": human_time(info["mtime"]),
            "thumb": thumb_rel,
            "backup_inis": find_backup_inis(sub_inis, dir_info),
            "hashes": sorted(hs),
        })
        if thumb_rel:
            ap = os.path.join(mods_dir, thumb_rel.replace("/", os.sep))
            if os.path.isfile(ap):
                res.thumb_srcs.append(ap)

    entries.sort(key=lambda e: (e["char"].lower(), e["category"].lower(),
                                e["name"].lower()))
    used = {}
    for e in entries:
        k = e["id"]
        if k in used:
            used[k] += 1
            e["id"] = "%s#%d" % (k, used[k])
        else:
            used[k] = 0

    res.entries = entries
    res.by_id = {e["id"]: e for e in entries}
    res.conflicts = detect_conflicts(entries)

    cats = {}
    for e in entries:
        cats.setdefault(e["category"], {}).setdefault(e["char"], []).append(e)
    cat_list = []
    for cname in sorted(cats, key=lambda s: s.lower()):
        groups = cats[cname]
        glist = []
        for gname in sorted(groups, key=lambda s: s.lower()):
            items = groups[gname]
            glist.append({"name": gname, "count": len(items),
                          "enabled": sum(1 for i in items if i["enabled"]),
                          "partial": sum(1 for i in items if i["partial"])})
        allitems = [i for g in groups.values() for i in g]
        cat_list.append({"name": cname, "count": len(allitems),
                         "enabled": sum(1 for i in allitems if i["enabled"]),
                         "partial": sum(1 for i in allitems if i["partial"]),
                         "groups": glist})
    res.categories = cat_list

    ch = {}
    for e in entries:
        ch.setdefault(e["char"], []).append(e)
    res.chars = [{"name": c, "count": len(v),
                  "enabled": sum(1 for i in v if i["enabled"]),
                  "multi": len(v) > 1}
                 for c, v in sorted(ch.items(), key=lambda kv: kv[0].lower())]

    res.stats = {
        "total": len(entries),
        "enabled": sum(1 for e in entries if e["enabled"]),
        "disabled": sum(1 for e in entries if not e["enabled"]),
        "partial": sum(1 for e in entries if e["partial"]),
        "chars": len(res.chars),
        "multi_chars": sum(1 for c in res.chars if c["multi"]),
        "size": total_size, "size_h": human_size(total_size), "files": total_files,
        "conflicts": len(res.conflicts),
    }
    res.scanned_at = time.time()
    res.duration = res.scanned_at - t0
    return res


def _img_rank(stem):
    for i, kw in enumerate(PREVIEW_PRIORITY):
        if stem == kw or stem.startswith(kw):
            return i
    if any(h in stem for h in ("help", "readme", "说明", "使用", "教程",
                               "按键", "菜单", "guide", "tutorial")):
        return 80
    if any(h in stem for h in ("screenshot", "截图", "screen")):
        return 20
    return 40


def pick_preview(root_abs, dir_info, sub_inis, rel_base):
    local_dirs = set(sub_inis) | {root_abs}
    best = None
    for k, v in dir_info.items():
        if k != root_abs and not k.startswith(root_abs + os.sep):
            continue
        for f in v["imgs"]:
            try:
                size = os.path.getsize(os.path.join(k, f))
            except OSError:
                continue
            if size > 12 * 1024 * 1024:
                continue
            stem = os.path.splitext(f)[0].lower()
            rank = _img_rank(stem)
            key = (rank, 0 if k in local_dirs else 1, size, f)
            if best is None or key < best[0]:
                best = (key, norm_rel(os.path.relpath(os.path.join(k, f), rel_base)))
    if best and best[0][0] < 80:
        return best[1]
    return None


def find_backup_inis(sub_inis, dir_info):
    out = []
    for d in sub_inis:
        for f in dir_info.get(d, {}).get("ini", []):
            if is_disabled_name(f):
                out.append(f)
    return out[:20]


HASH_RE = re.compile(r"^\s*hash\s*=\s*([0-9a-fA-F]{6,16})\s*$", re.M)
SEC_RE = re.compile(r"^\[([^\]\r\n]+)\]")
REPLACE_HINT = re.compile(
    r"^\s*(vb0|vb1|vb2|ib|draw|drawindexed|match_first_index|"
    r"Resource\\ZZMI\\|ps-t0|run\s*=\s*CommandList)", re.M | re.I)
BACKUP_RE = re.compile(r"(?:backup|beifen|\.bak\b|_bak)", re.IGNORECASE)


def _ini_overrides(txt):
    """解析 ini 文本, 返回真正覆盖游戏资源的 TextureOverride hash 集合。"""
    hs = set()
    for block in re.split(r"(?m)^(?=\[)", txt):
        m = SEC_RE.match(block.strip())
        if not m or not m.group(1).lower().startswith("textureoverride"):
            continue
        hm = HASH_RE.search(block)
        if hm and REPLACE_HINT.search(block[hm.end():]):
            hs.add(hm.group(1).lower())
    return hs


def collect_hashes(ini_dirs, dir_info):
    out = {}
    for d in ini_dirs:
        hs = set()
        for f in dir_info.get(d, {}).get("ini", []):
            if is_disabled_name(f):
                continue
            p = os.path.join(d, f)
            try:
                if os.path.getsize(p) > 4 * 1024 * 1024:
                    continue
                with open(p, "r", encoding="utf-8", errors="replace") as fh:
                    hs |= _ini_overrides(fh.read())
            except Exception:
                continue
        out[d] = hs
    return out


def detect_conflicts(entries):
    idmap = {e["id"]: e for e in entries}
    h2m = {}
    for e in entries:
        if not e["enabled"]:
            continue
        for h in e["hashes"]:
            h2m.setdefault(h, []).append(e["id"])
    pairs = {}
    for h, ids in h2m.items():
        ids = sorted(set(ids))
        if len(ids) < 2:
            continue
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                pairs.setdefault((ids[i], ids[j]), []).append(h)
    out = []
    for (ia, ib), hs in pairs.items():
        a, b = idmap.get(ia), idmap.get(ib)
        if not a or not b:
            continue
        out.append({"a": ia, "b": ib, "a_name": a["name"], "b_name": b["name"],
                    "a_char": a["char"], "b_char": b["char"], "n": len(hs),
                    "hashes": sorted(hs)[:8],
                    "same_char": a["char"] == b["char"]})
    out.sort(key=lambda c: (not c["same_char"], -c["n"]))
    return out[:300]


# ===========================================================================
# 部件 / 变体分析
# ===========================================================================

def _walk_inis(abs_root):
    out = []
    for cur, dirs, files in os.walk(abs_root):
        dirs[:] = [d for d in dirs if d.lower() != "desktop.ini"]
        rel = os.path.relpath(cur, abs_root)
        rel = "" if rel == "." else rel
        for f in files:
            if f.lower().endswith(".ini"):
                out.append((os.path.join(cur, f), norm_rel(os.path.join(rel, f))))
    return sorted(out, key=lambda t: t[1].lower())


def resolve_component_file(abs_root, rel):
    """按相对路径找 mod 内的文件; 允许任意一段(目录或文件)带 DISABLED 前缀。"""
    rel = norm_rel(rel)
    if not rel:
        return None
    p = os.path.join(abs_root, rel.replace("/", os.sep))
    if os.path.isfile(p):
        return p
    cur = abs_root
    parts = [x for x in rel.split("/") if x]
    for part in parts:
        try:
            names = os.listdir(cur)
        except OSError:
            return None
        hit = None
        if part in names:
            hit = part
        else:
            for n in names:
                if strip_disabled(n) == strip_disabled(part):
                    hit = n
                    break
        if hit is None:
            return None
        cur = os.path.join(cur, hit)
    return cur if os.path.isfile(cur) else None


def analyze_components(abs_root):
    """解析 mod 内每个 ini 的覆盖目标, 把「覆盖同一游戏资源」的文件自动归为变体组。

    返回 {"components": [{rel,name,enabled,backup,group,n_hashes,size}],
          "groups":     [{id,label,files,active,n_hashes}]}
    备份副本(DISABLED_BACKUP_* / disabled_beifen_* 之类)不参与分组, 只做展示。
    """
    comps = []
    hmap = {}
    for full, rel in _walk_inis(abs_root):
        name = os.path.basename(full)
        disabled = is_disabled_name(name)
        backup = disabled and bool(BACKUP_RE.search(name))
        hashes = set()
        if not backup:
            try:
                if os.path.getsize(full) <= 4 * 1024 * 1024:
                    with open(full, "r", encoding="utf-8", errors="replace") as fh:
                        hashes = _ini_overrides(fh.read())
            except Exception:
                hashes = set()
        hmap[len(comps)] = hashes
        comps.append({"rel": rel, "name": name, "enabled": not disabled,
                      "backup": backup, "group": None,
                      "n_hashes": len(hashes), "hashes": sorted(hashes),
                      "size": _size(full)})

    # 并查集: 共享任一 hash 的文件归为一组
    parent = list(range(len(comps)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    hash2idx = {}
    for i, hs in hmap.items():
        for h in hs:
            if h in hash2idx:
                ra, rb = find(hash2idx[h]), find(i)
                if ra != rb:
                    parent[rb] = ra
            else:
                hash2idx[h] = i

    clusters = {}
    for i in range(len(comps)):
        clusters.setdefault(find(i), []).append(i)

    groups = []
    gid = 0
    for members in clusters.values():
        if len(members) < 2:
            continue
        gid += 1
        g = {"id": "g%d" % gid, "files": [], "active": None, "n_hashes": 0}
        allh = set()
        names = []
        for i in sorted(members, key=lambda x:
                        (not comps[x]["enabled"], comps[x]["rel"].lower())):
            comps[i]["group"] = g["id"]
            g["files"].append(comps[i]["rel"])
            allh |= hmap[i]
            if comps[i]["enabled"] and g["active"] is None:
                g["active"] = comps[i]["rel"]
            names.append(strip_disabled(os.path.splitext(comps[i]["name"])[0]))
        g["n_hashes"] = len(allh)
        # 组名: 跳过 hash 文件夹(如 0f82a13e), 向上取有意义目录名; 退化用公共前缀
        def _meaningful(rel):
            parts = rel.replace("/", os.sep).split(os.sep)[:-1]  # 去掉文件名
            for f in reversed(parts):
                b = strip_disabled(f)
                if re.fullmatch(r"[0-9a-fA-F]{6,}", b):
                    continue  # hash 文件夹, 跳过
                if b:
                    return b
            return ""
        folders = {}
        for i in members:
            m = _meaningful(comps[i]["rel"])
            if m:
                folders[m] = folders.get(m, 0) + 1
        pre = os.path.commonprefix(names).strip(" -_")
        label = ""
        if folders:
            top = max(folders.values())
            if top >= 2 or len(folders) == 1:
                label = [k for k, v in folders.items() if v == top][0]
        label = label or (pre if len(pre) >= 2 else "")
        if re.fullmatch(r"[0-9a-fA-F]{6,}", label.strip()):
            label = ""  # hash 文件夹名无意义, 退回通用名
        g["label"] = (label or "变体组").strip() or "变体组"
        groups.append(g)
    # 去重: 同组名加序号, 避免单选按钮标题重名(如两个 hash 文件夹同名)
    seen = {}
    for g in groups:
        l = g["label"]
        if l in seen:
            seen[l] += 1
            g["label"] = "%s #%d" % (l, seen[l])
        else:
            seen[l] = 1
    return {"components": comps, "groups": groups}


# ===========================================================================
# 写操作 (全部写 journal, 可撤销)
# ===========================================================================

_jlock = threading.Lock()


def journal_append(rec):
    with _jlock:
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            rec["ts"] = time.time()
            with open(JOURNAL_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except Exception:
            pass


def journal_read(limit=500):
    out = []
    try:
        with open(JOURNAL_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        out.append(json.loads(line))
                    except Exception:
                        pass
    except FileNotFoundError:
        return []
    except Exception:
        return out
    return out[-limit:]


def _rename_dir(src, dst, rec):
    if os.path.exists(dst):
        return False, "目标名已存在: %s" % os.path.basename(dst)
    try:
        os.rename(src, dst)
    except OSError as ex:
        msg = str(ex)
        if "另一个程序正在使用" in msg or "being used by another" in msg:
            msg = "文件被占用(游戏或资源管理器开着这个目录), 先关掉再试。"
        return False, "重命名失败: %s" % msg
    journal_append(rec)
    return True, "ok"


def do_toggle(mods_dir, entry, enable):
    cur = resolve_rel_dir(mods_dir, entry["id"])
    if not cur or not os.path.isdir(cur):
        return False, "找不到目录(可能已被移动)"
    name = os.path.basename(cur)
    disabled = is_disabled_name(name)
    if enable and not disabled:
        return True, "已是启用状态"
    if (not enable) and disabled:
        return True, "已是禁用状态"
    base = strip_disabled(name)
    new = base if enable else (DISABLED_PREFIX + base)
    if new == name:
        return False, "名字已经是目标状态"
    dst = os.path.join(os.path.dirname(cur), new)
    ok, msg = _rename_dir(cur, dst, {"kind": "toggle", "src": cur, "dst": dst,
                                     "enable": bool(enable), "id": entry["id"],
                                     "name": entry["name"]})
    return (True, "已%s" % ("启用" if enable else "禁用")) if ok else (False, msg)


def do_toggle_dir(mods_dir, rel, enable):
    p = resolve_rel_dir(mods_dir, rel)
    if not p or not os.path.isdir(p):
        return False, "目录不存在"
    if os.path.abspath(p) == os.path.abspath(mods_dir):
        return False, "不能操作 Mods 根目录"
    name = os.path.basename(p)
    disabled = is_disabled_name(name)
    if enable == (not disabled):
        return True, "状态没变"
    base = strip_disabled(name)
    new = base if enable else (DISABLED_PREFIX + base)
    if new == name:
        return False, "名字已经是目标状态"
    dst = os.path.join(os.path.dirname(p), new)
    ok, msg = _rename_dir(p, dst, {"kind": "toggle", "src": p, "dst": dst,
                                   "enable": bool(enable), "id": rel, "name": name})
    return (True, "已%s %s" % ("启用" if enable else "禁用", name)) if ok else (False, msg)


def do_toggle_file(abs_root, rel, enable):
    """mod 内单个 ini 文件的启停: 文件名加/去 DISABLED_ 前缀, 永不删除。"""
    p = resolve_component_file(abs_root, rel)
    if not p or not os.path.isfile(p):
        return False, "找不到文件: %s" % rel
    if os.path.abspath(p) == os.path.abspath(abs_root):
        return False, "路径不合法"
    name = os.path.basename(p)
    disabled = is_disabled_name(name)
    if enable and not disabled:
        return True, "已是启用状态"
    if (not enable) and disabled:
        return True, "已是禁用状态"
    base = strip_disabled(name)
    new = base if enable else (DISABLED_PREFIX + base)
    dst = os.path.join(os.path.dirname(p), new)
    if os.path.exists(dst):
        return False, "目标名已存在: %s" % new
    try:
        os.rename(p, dst)
    except OSError as ex:
        msg = str(ex)
        if "另一个程序正在使用" in msg or "being used by another" in msg:
            msg = "文件被占用(游戏正在用它), 先关游戏或稍后再试。"
        return False, "重命名失败: %s" % msg
    journal_append({"kind": "file_toggle", "src": p, "dst": dst,
                    "enable": bool(enable), "id": rel, "name": name})
    return True, "已%s %s" % ("启用" if enable else "禁用", base)


def do_variant_select(abs_root, rel):
    """一键切换变体: 启用指定文件, 并禁用同组里其它已启用的文件。"""
    comp = analyze_components(abs_root)
    tgt = None
    for c in comp["components"]:
        if c["rel"] == rel or strip_disabled(c["rel"]) == strip_disabled(rel):
            tgt = c
            break
    if tgt is None:
        return False, "找不到这个部件"
    # 只处理与目标有直接 hash 冲突的同组成员(避免传递闭包把不相关文件一起关掉)
    ths = set(tgt.get("hashes") or [])
    members = [c for c in comp["components"]
               if c is not tgt and c.get("group") == tgt.get("group")
               and c.get("group") and (ths & set(c.get("hashes") or []))]
    members.append(tgt)
    n = 0
    last_msg = ""
    for m in members:
        want = m["rel"] == tgt["rel"]
        if want == m["enabled"]:
            continue
        good, msg = do_toggle_file(abs_root, m["rel"], want)
        last_msg = msg
        if good:
            n += 1
        else:
            return False, "切换中断: %s" % msg
    if n == 0:
        return True, "这个变体已经在用了"
    return True, "已切换到「%s」(变更 %d 项)%s" % (
        strip_disabled(tgt["name"]), n,
        "" if not last_msg or "已" in last_msg else "; " + last_msg)


# ---------------------------------------------------------------------------
# 热键循环变体: [Key*] 段里 `$var = 0,1,2` + `type = cycle`,
# 游戏内按绑定键循环取值。初始值 = 列表第一个值, 所以把列表旋转即可持久换变体。
# ---------------------------------------------------------------------------

# 取值列表后允许行内注释 (; 或 #), group(2) 只取数字列表
CYCLE_DECL_RE = re.compile(r"^\$(\w+)\s*=\s*([0-9][0-9\s,]*)(?:\s*[;#].*)?$")
CYCLE_EXPR_RE = re.compile(r"^\$(\w+)\s*=\s*([^=\r\n]+)$")
KEYSEC_RE = re.compile(r"^key", re.I)
INI_BACKUP_DIR = os.path.join(DATA_DIR, "ini_backups")

# 变体变量名 -> 中文提示 (小写匹配; 匹配不到就显示原名)
CYCLE_LABEL_CN = {
    "upper": "上装", "lower": "下装", "top": "上衣", "bottom": "下装",
    "bottoms": "下装", "pubic": "私处", "tt": "透视", "skirt": "裙子",
    "bra": "内衣", "panties": "内裤", "thong": "丁字裤", "stockings": "长袜",
    "socks": "袜子", "thighhighs": "过膝袜", "thighstrap": "腿带",
    "gloves": "手套", "glasses": "眼镜", "hair": "头发", "haircolour": "发色",
    "haircolor": "发色", "face": "脸型", "tail": "尾巴", "ears": "耳朵",
    "horns": "角", "wings": "翅膀", "collar": "项圈", "choker": "颈饰",
    "hat": "帽子", "mask": "面具", "shoes": "鞋子", "shoescolour": "鞋色",
    "heels": "高跟鞋", "jacket": "外套", "jacketcolour": "外套色",
    "coat": "大衣", "underwear": "内衣", "leotard": "连体衣",
    "bikinitop": "比基尼上装", "bikinibottom": "比基尼下装",
    "nipplepasties": "乳贴", "nipples": "乳贴", "skin": "肤色",
    "skintone": "肤色", "bodypaint": "身体彩绘", "bodypaintcolor": "彩绘颜色",
    "makeup": "妆容", "lace": "蕾丝", "bows": "蝴蝶结", "bow": "蝴蝶结",
    "straps": "吊带", "garter": "吊袜带", "garters": "吊袜带",
    "garterscolour": "袜带色", "tan": "美黑", "piercings": "穿孔",
    "naked": "全裸", "alt": "备用款式", "furarm": "毛袖", "furchest": "毛胸",
    "furleg": "毛腿", "furhip": "毛臀", "furneck": "毛领", "glow": "发光",
    "health": "战损效果", "acces": "饰品", "earrings": "耳环",
    "necklace": "项链", "bracelet": "手环", "wristbangle": "手镯",
    "bangs": "刘海", "topcolour": "上衣色", "topcolor": "上衣色",
    "bottomscolour": "下装色", "stockingcolour": "长袜色",
    "fan": "扇子", "weapon": "武器", "knife": "短刀", "sword": "剑",
    "gadget": "随身装备", "cutoffpockets": "破洞裤", "jumper": "背带裤",
    "bodybelt": "腰封", "bodymark": "身体纹路", "arm": "手臂",
    "armaccessories": "臂饰", "armaccessoriesleft": "左臂饰",
    "armaccessoriesright": "右臂饰", "legaccessory": "腿饰",
    "neckaccessory": "颈饰", "hairaccessory": "发饰",
    "hairaccessory2": "发饰2", "fingernail": "美甲",
    "fingernaillength": "美甲长度", "fingernailcolour": "美甲色",
    "toerings": "趾环", "shorts": "短裤", "shirts": "衬衫", "shirt": "衬衫",
    "shirtcolour": "衬衫色", "jumpercolour": "背带裤色", "sheath": "剑鞘",
    "helpsize": "帮助大小", "lang": "语言", "img_x": "说明图X", "img_y": "说明图Y",
    "menu": "菜单", "menu_open": "菜单开关", "help": "帮助",
    "creditinfo": "作者信息", "diable.Notification".lower(): "关闭提示",
    "disableNotification".lower(): "关闭提示", "bra": "内衣",
    "t": "全身切换", "w": "武器切换", "h": "隐藏",
    # —— 第二批: 本机 mod 实测未覆盖的变量名 ——
    "anim": "动画", "animplate": "动画板", "body": "身体",
    "hairdec": "发饰", "hairog": "原版发型", "handdec": "手部饰品",
    "leg": "腿部", "legs": "腿部", "nipple": "乳头",
    "t4": "全身预设4", "t5": "全身预设5",
    "armaccessoriescolour": "臂饰色", "ballgag": "口球",
    "blazer": "西装外套", "blindfold": "眼罩", "bodysuit": "紧身衣",
    "bot": "下装", "censor": "审查开关", "cloth": "服装",
    "color": "颜色", "controlhair": "头发控制",
    "gloveleft": "左手套", "gloveright": "右手套",
    "hairclip": "发夹", "hairclipcolour": "发夹色", "heel": "鞋跟",
    "nippleaccessories": "乳饰", "originalshoescolour": "原版鞋色",
    "pants": "裤子", "shinyskin": "油亮皮肤",
    "skimpybottoms": "暴露下装", "skimpytop": "暴露上装",
    "skirtcolour": "裙色", "sock": "袜子", "sockscolour": "袜色",
    "strapscolour": "吊带色", "swapvar": "通用切换", "tailbow": "尾结",
    "thighstrapcolour": "腿带色", "thongstraps": "丁字裤带",
    "thongstrapscolour": "丁字裤带色", "topstraps": "上衣吊带",
    "waist": "腰饰", "yanse": "颜色",
}

_KEY_MOD_MAP = (("no_win", None), ("no_ctrl", None), ("no_alt", None),
                ("no_shift", None), ("no_modifiers", None),
                ("ctrl", "Ctrl"), ("alt", "Alt"), ("shift", "Shift"),
                ("win", "Win"))


def _pretty_keys(keyval):
    """3DMigoto 的 key 行: 空格分隔 = 同时按下的组合键。
    'ctrl alt y 6' -> ['Ctrl+Alt+Y+6'], 'no_ctrl h' -> ['H'], 'h' -> ['H']。
    no_* 是『不能按某修饰键』的排除项, 不参与显示。"""
    parts = []
    for t in (keyval or "").strip().split():
        tl = t.lower()
        hit = False
        for name, disp in _KEY_MOD_MAP:
            if tl == name:
                if disp:
                    parts.append(disp)
                hit = True
                break
        if not hit:
            parts.append(t if len(t) > 1 else t.upper())
    if not parts:
        return []
    return ["+".join(parts)]


def parse_cycle_vars(abs_root):
    """扫描 mod 内已启用 ini 的 [Key*] 段, 汇总每个循环变量的
    取值列表 / 绑定按键 / 当前值 / 可否从外部切换。"""
    found = {}
    for cur, dirs, files in os.walk(abs_root):
        dirs[:] = [d for d in dirs if d.lower() != "desktop.ini"]
        rel_dir = os.path.relpath(cur, abs_root)
        rel_dir = "" if rel_dir == "." else rel_dir
        for f in files:
            if not f.lower().endswith(".ini") or is_disabled_name(f):
                continue
            p = os.path.join(cur, f)
            try:
                if os.path.getsize(p) > 2 * 1024 * 1024:
                    continue
                txt = open(p, "r", encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            rel = norm_rel(os.path.join(rel_dir, f))
            sec_name, sec_cycle, sec_key, sec_decls = None, False, "", []

            def _flush():
                if not sec_cycle or not sec_decls:
                    return
                for ln, var, raw in sec_decls:
                    base_label = re.sub(r"(?i)^(swap_?var_?|swap_?|var_?)",
                                        "", var) or var
                    # 只做「上装/下装」这类具体部位翻译; 翻译不到就显示原名,
                    # 不再用「部位 N」这种笼统叫法
                    label_cn = CYCLE_LABEL_CN.get(base_label.lower())
                    rec = found.setdefault(var, {
                        "var": var,
                        "label": base_label,
                        "label_cn": label_cn,
                        "values": [], "keys": [], "files": [],
                        "switchable": True})
                    for k in _pretty_keys(sec_key):
                        if k not in rec["keys"]:
                            rec["keys"].append(k)
                    if {"rel": rel, "line": ln} not in rec["files"]:
                        rec["files"].append({"rel": rel, "line": ln})
                    if raw == "?":
                        rec["switchable"] = False   # 带表达式, 只能游戏内按键切
                        continue
                    vals = [int(x) for x in
                            raw.replace(" ", "").split(",") if x != ""]
                    if not vals:
                        rec["switchable"] = False
                        continue
                    if not rec["values"]:
                        rec["values"] = vals
                    elif rec["values"] != vals:
                        rec["switchable"] = False   # 各文件取值不一致, 保守不切

            for ln, line in enumerate(txt.splitlines(), 1):
                st = line.strip()
                if st.startswith("[") and st.endswith("]"):
                    _flush()
                    sec_name = st[1:-1].strip()
                    sec_cycle, sec_key, sec_decls = False, "", []
                    continue
                if sec_name is None or not KEYSEC_RE.match(sec_name):
                    continue
                low = st.lower()
                if low.startswith("key=") or low.startswith("key ="):
                    sec_key = st.split("=", 1)[1].strip()
                elif low.startswith("type=") or low.startswith("type ="):
                    if "cycle" in low.split("=", 1)[1].lower():
                        sec_cycle = True
                else:
                    dm = CYCLE_DECL_RE.match(st)
                    if dm:
                        sec_decls.append((ln, dm.group(1), dm.group(2)))
                    elif st.startswith("$") and CYCLE_EXPR_RE.match(st):
                        # 带表达式的循环(如 $menu = 0,1 - $bodyPaint): 展示但不可切
                        m2 = CYCLE_EXPR_RE.match(st)
                        sec_decls.append((ln, m2.group(1), "?"))
            _flush()

    out = list(found.values())
    for rec in out:
        rec["current"] = rec["values"][0] if rec["values"] else None
    out.sort(key=lambda r: r["var"].lower())
    return out


def do_cycle_set(abs_root, var, value):
    """把循环变量 var 的『默认变体』持久设为 value: 仅就地旋转对应那一行
    的值列表, 让 value 排第一(3DMigoto 取首元素作默认)。
    字节级修改, 完整保留原文件编码 / 换行符 / BOM, 绝不重写整文件; 改前
    整文件备份, 写 journal 可撤销。注意: 这只改变『下次进游戏默认加载的变体』,
    游戏内按绑定键仍可即时循环切换。"""
    value = int(value)
    edits = []   # (path, abs_start, abs_end, newbytes)  绝对字节偏移
    for cur, dirs, files in os.walk(abs_root):
        dirs[:] = [d for d in dirs if d.lower() != "desktop.ini"]
        for f in files:
            if not f.lower().endswith(".ini") or is_disabled_name(f):
                continue
            p = os.path.join(cur, f)
            try:
                if os.path.getsize(p) > 2 * 1024 * 1024:
                    continue
                data = open(p, "rb").read()
            except Exception:
                continue
            # latin-1 与字节 1:1, 便于用文本正则定位后回写原字节
            text = data.decode("latin-1")
            sec_name, sec_cycle = None, False
            pos = 0
            for line in text.splitlines(True):
                st = line.strip()
                if st.startswith("[") and st.endswith("]"):
                    sec_name = st[1:-1].strip()
                    sec_cycle = False
                    pos += len(line)
                    continue
                if sec_name is None or not KEYSEC_RE.match(sec_name):
                    pos += len(line)
                    continue
                low = st.lower()
                if low.startswith("type=") or low.startswith("type ="):
                    if "cycle" in low.split("=", 1)[1].lower():
                        sec_cycle = True
                    pos += len(line)
                    continue
                if not sec_cycle:
                    pos += len(line)
                    continue
                m = CYCLE_DECL_RE.search(line)
                if m and m.group(1) == var:
                    vals = [int(x) for x in
                            m.group(2).replace(" ", "").split(",") if x != ""]
                    if value not in vals:
                        pos += len(line)
                        continue
                    if vals[0] == value:   # 已是该默认, 跳过
                        pos += len(line)
                        continue
                    idx = vals.index(value)
                    new = vals[idx:] + vals[:idx]
                    tail = m.group(2).rstrip().endswith(",")
                    newstr = ",".join(str(v) for v in new) + ("," if tail else "")
                    edits.append((p, pos + m.start(2), pos + m.end(2),
                                 newstr.encode("latin-1")))
                pos += len(line)

    if not edits:
        return False, "这个变量没有可切换的取值 %d" % value

    os.makedirs(INI_BACKUP_DIR, exist_ok=True)
    byfile = {}
    for p, s, e, nb in edits:
        byfile.setdefault(p, []).append((s, e, nb))

    changed = 0
    for p, items in byfile.items():
        try:
            data = open(p, "rb").read()
        except Exception as ex:
            return False, "读文件失败: %s" % ex
        bak = os.path.join(INI_BACKUP_DIR, "%s_%s" % (
            hashlib.sha1(os.path.abspath(p).encode("utf-8")).hexdigest()[:12],
            os.path.basename(p)))
        try:
            if not os.path.isfile(bak):
                shutil.copyfile(p, bak)
            items.sort()
            out = bytearray()
            cursor = 0
            for s, e, nb in items:   # 非重叠, 按偏移拼接
                out += data[cursor:s]
                out += nb
                cursor = e
            out += data[cursor:]
            open(p, "wb").write(bytes(out))
        except Exception as ex:
            return False, "写文件失败: %s" % ex
        journal_append({"kind": "ini_edit", "path": p, "backup": bak,
                        "name": os.path.basename(p), "var": var,
                        "value": value})
        changed += 1
    if changed == 0:
        return True, "已经是这个默认变体了"
    return True, "已把默认变体设为 %d (改了 %d 个文件); 游戏内按 F10 或重启生效" % (value, changed)



def batch_toggle(mods_dir, entries, enable):
    entries = sorted(entries, key=lambda e: e["path"].count("/"))
    ok, fails = 0, []
    for e in entries:
        try:
            good, msg = do_toggle(mods_dir, e, enable)
        except Exception as ex:
            good, msg = False, str(ex)
        if good:
            ok += 1
        else:
            fails.append({"id": e["id"], "name": e["name"], "msg": msg})
    return {"ok": ok, "failed": len(fails), "details": fails[:20]}


def undo_last():
    for rec in reversed(journal_read(2000)):
        kind = rec.get("kind")
        if kind == "ini_edit":
            p, bak = rec.get("path"), rec.get("backup")
            if p and bak and os.path.isfile(bak) and os.path.isfile(p):
                try:
                    shutil.copyfile(bak, p)
                except Exception as ex:
                    return False, "撤销失败: %s" % ex
                journal_append({"kind": "undo", "of": rec.get("ts")})
                return True, "已还原: %s" % os.path.basename(p)
            return False, "文件状态已变化, 无法撤销这一步"
        if kind not in ("toggle", "move", "file_toggle"):
            continue
        src, dst = rec.get("src"), rec.get("dst")
        if not src or not dst:
            continue
        if os.path.exists(dst) and not os.path.exists(src):
            try:
                os.rename(dst, src)
            except OSError as ex:
                return False, "撤销失败: %s" % ex
            journal_append({"kind": "undo", "of": rec.get("ts")})
            return True, "已撤销: %s" % os.path.basename(src)
        return False, "文件状态已变化, 无法撤销这一步"
    return False, "没有可撤销的操作"


def do_move(src_base, src_rel, dst_base, dst_rel):
    src = resolve_rel_dir(src_base, src_rel)
    dst = safe_join(dst_base, dst_rel)
    if not src or not os.path.isdir(src):
        return False, "源目录不存在"
    if not dst:
        return False, "目标路径不合法"
    sa, da = os.path.abspath(src), os.path.abspath(dst)
    if sa == da:
        return False, "源和目标相同"
    if da.startswith(sa + os.sep):
        return False, "不能移动到自己的子目录里"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst):
        return False, "目标已存在: %s" % os.path.basename(dst)
    try:
        shutil.move(src, dst)
    except Exception as ex:
        return False, "移动失败: %s" % ex
    journal_append({"kind": "move", "src": src, "dst": dst})
    return True, "已移动"


def do_rename(mods_dir, entry, new_name):
    cur = resolve_rel_dir(mods_dir, entry["id"])
    if not cur or not os.path.isdir(cur):
        return False, "找不到目录"
    new_name = (new_name or "").strip()
    if not new_name or re.search(r'[\\/:*?"<>|]', new_name):
        return False, '名称不合法(不能含 \\ / : * ? " < > |)'
    disabled = is_disabled_name(os.path.basename(cur))
    target = (DISABLED_PREFIX + new_name) if disabled else new_name
    dst = os.path.join(os.path.dirname(cur), target)
    if os.path.abspath(dst) == os.path.abspath(cur):
        return False, "名称没有变化"
    ok, msg = _rename_dir(cur, dst, {"kind": "move", "src": cur, "dst": dst})
    return (True, "已重命名为 %s" % target) if ok else (False, msg)


def open_in_explorer(path):
    if not path or not os.path.exists(path):
        return False
    try:
        if os.path.isfile(path):
            subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
        else:
            os.startfile(path)  # noqa
        return True
    except Exception:
        try:
            subprocess.Popen(["explorer", os.path.normpath(path)])
            return True
        except Exception:
            return False


# ===========================================================================
# 方案 / 进程 / 启动
# ===========================================================================

def presets_load():
    return read_json(PRESETS_PATH, {})


def presets_save(obj):
    write_json(PRESETS_PATH, obj)


_proc_cache = {"t": 0, "game": False, "launcher": False}
_lib_cache = {"t": 0, "data": None}


def invalidate_lib_cache():
    _lib_cache["data"] = None
    _lib_cache["t"] = 0


def proc_probe(cfg, force=False):
    now = time.time()
    if not force and now - _proc_cache["t"] < 5:
        return _proc_cache["game"], _proc_cache["launcher"]
    game = launcher = False
    try:
        out = subprocess.run(["tasklist", "/NH"], capture_output=True, text=True,
                             timeout=8, errors="replace",
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        txt = (out.stdout or "").lower()
        exe = os.path.basename(cfg.get("game_exe") or "ZenlessZoneZero.exe").lower()
        game = exe in txt
        launcher = "xxmi launcher.exe" in txt
    except Exception:
        pass
    _proc_cache.update({"t": now, "game": game, "launcher": launcher})
    return game, launcher


def launch_game(cfg):
    """启动游戏。ZZMI 需要管理员权限注入(d3dx.ini: require_admin=true),
    所以必须用 ShellExecute 的 runas 走 UAC, 否则 CreateProcess 会报 WinError 740。"""
    exe = cfg.get("launcher_exe") or ""
    if not os.path.isfile(exe):
        return False, "找不到 XXMI Launcher: %s" % (exe or "(未配置)")
    game, launcher = proc_probe(cfg, force=True)
    if launcher:
        return False, "XXMI Launcher 已经在运行, 请先关掉它"
    if game:
        return False, "游戏已经在运行了"
    importer = cfg.get("importer") or "ZZMI"
    workdir = os.path.dirname(exe)
    args = "--nogui --xxmi %s" % importer

    if os.name == "nt":
        try:
            import ctypes
            rc = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", exe, args, workdir, 1)      # 1 = SW_SHOWNORMAL
            if rc > 32:
                _proc_cache["t"] = 0
                return True, ("已请求管理员权限 —— 请在 UAC 弹窗点「是」, "
                              "游戏就会启动 (--nogui --xxmi %s)" % importer)
            if rc == 5:
                return False, "你取消了管理员授权, 没有启动\n(ZZMI 注入需要管理员权限, 请再点一次并选「是」)"
            if rc == 2:
                return False, "找不到启动器文件"
            return False, "启动被系统拒绝 (错误码 %d)" % rc
        except Exception as ex:
            log("runas 启动失败, 改用普通方式:", ex)

    try:
        subprocess.Popen([exe, "--nogui", "--xxmi", importer],
                         cwd=workdir, close_fds=True)
    except Exception as ex:
        if "740" in str(ex):
            return False, ("启动需要管理员权限但被拒绝。\n请右键本程序「以管理员身份运行」,"
                           "或手开 XXMI Launcher 点 Launch。")
        return False, "启动失败: %s" % ex
    _proc_cache["t"] = 0
    return True, "已启动游戏 (--nogui --xxmi %s)" % importer


BROWSER_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
]


def find_browser():
    for b in BROWSER_CANDIDATES:
        if os.path.isfile(b):
            return b
    return None


def open_app_window(url, size="1320,880"):
    """用 Edge/Chrome 的 --app 模式开独立窗口, 并强制直连绕过系统代理。"""
    b = find_browser()
    if b:
        args = [b,
                "--app=" + url,
                "--window-size=" + size,
                "--proxy-server=direct://",
                "--proxy-bypass-list=<-loopback>",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-features=Translate"]
        try:
            subprocess.Popen(args, close_fds=True)
            log("已用独立窗口打开:", os.path.basename(b))
            return True
        except Exception as ex:
            log("独立窗口启动失败, 改用默认浏览器:", ex)
    webbrowser.open(url)
    return False


# ===========================================================================
# 应用状态
# ===========================================================================

SLIM_DROP = ("sub_dirs", "hashes", "ini_roots", "char_auto")


class App(object):
    def __init__(self):
        self.cfg = dict(DEFAULT_CONFIG)
        self.scan = ScanResult()
        self.lock = threading.RLock()
        self.token = os.urandom(9).hex()
        self.detect_report = {"done": True, "step": "", "found": None,
                              "candidates": [], "message": ""}
        self.last_error = ""
        self.httpd = None
        self.hotkey = HotkeyManager(self)

    def load_config(self):
        raw = read_json(CONFIG_PATH, None)
        if not isinstance(raw, dict) or "zzmi_root" not in raw:
            if raw is not None:
                try:
                    shutil.copyfile(CONFIG_PATH, os.path.join(
                        DATA_DIR, "config.old-%s.json" % time.strftime("%Y%m%d-%H%M%S")))
                except Exception:
                    pass
            return False
        cfg = dict(DEFAULT_CONFIG)
        cfg.update({k: v for k, v in raw.items() if k in DEFAULT_CONFIG})
        # 一次性迁移: 旧版本写进配置里的默认呼出键 Ctrl+Alt+K -> 新的默认 F9
        if str(cfg.get("hotkey") or "").replace(" ", "").lower() == "ctrl+alt+k":
            cfg["hotkey"] = DEFAULT_CONFIG["hotkey"]
            try:
                write_json(CONFIG_PATH, cfg)
                log("呼出键已迁移为 %s" % cfg["hotkey"])
            except Exception:
                pass
        self.cfg = cfg
        return True

    def save_config(self):
        write_json(CONFIG_PATH, self.cfg)

    def set_root(self, zzmi_root, importer=None, mods_dir=None):
        zzmi_root = (zzmi_root or "").strip().strip('"').rstrip("\\/")
        if not os.path.isdir(zzmi_root):
            return False, "目录不存在: %s" % zzmi_root
        score, info = score_xxmi_root(zzmi_root)
        if score < 8:
            return False, ("这看起来不是 XXMI Launcher 的安装目录。\n"
                           "请选择包含 Resources\\Bin\\XXMI Launcher.exe "
                           "以及 ZZMI 子目录的那一层。")
        importers = info.get("importers") or []
        imp = importer or self.cfg.get("importer") or "ZZMI"
        if importers and imp not in importers:
            imp = ([x for x in importers if x.upper() == "ZZMI"]
                   or [x for x in importers if "ZZ" in x.upper()] or importers)[0]
        self.cfg["zzmi_root"] = zzmi_root
        self.cfg["launcher_exe"] = info.get("launcher_exe", "")
        self.cfg["importer"] = imp
        self.cfg["mods_dir"] = mods_dir or os.path.join(zzmi_root, imp, "Mods")
        exe = game_exe_from_launcher_config(info.get("config_json"), imp)
        if exe:
            self.cfg["game_exe"] = exe
        self.cfg["libraries"] = detect_libraries(zzmi_root, self.cfg["mods_dir"])
        self.save_config()
        invalidate_lib_cache()
        return True, "已保存"

    def rescan(self):
        with self.lock:
            md = find_mods_dir(self.cfg)
            self.scan = scan_mods(md, self.cfg.get("char_overrides") or {}) \
                if md else ScanResult()
            if self.scan.thumb_srcs:
                n = enqueue_thumbs(self.scan.thumb_srcs)
                if n:
                    log("需生成缩略图 %d 张(后台进行)" % n)
            return self.scan

    def mods_dir(self):
        return find_mods_dir(self.cfg)

    def state(self, with_entries=True, probe=True):
        s = self.scan
        md = self.mods_dir()
        game = launcher = False
        if probe:
            game, launcher = proc_probe(self.cfg)
        st = {
            "app": APP_NAME, "version": VERSION,
            "configured": bool(self.cfg.get("zzmi_root")),
            "zzmi_root": self.cfg.get("zzmi_root", ""),
            "mods_dir": md,
            "mods_dir_exists": bool(md and os.path.isdir(md)),
            "launcher_exe": self.cfg.get("launcher_exe", ""),
            "launcher_exists": bool(self.cfg.get("launcher_exe")
                                    and os.path.isfile(self.cfg["launcher_exe"])),
            "importer": self.cfg.get("importer", "ZZMI"),
            "game_exe": self.cfg.get("game_exe", ""),
            "libraries": self.cfg.get("libraries", []),
            "theme": self.cfg.get("theme", "dark"),
            "hide_preview": bool(self.cfg.get("hide_preview")),
            "hotkey": self.cfg.get("hotkey", "F9"),
            "hotkey_ok": self.hotkey.ok is not False,
            "win_size": self.cfg.get("win_size", "1320,880"),
            "stats": s.stats, "categories": s.categories, "chars": s.chars,
            "conflicts": s.conflicts, "presets": presets_load(),
            "journal": [{"ts": r.get("ts"), "kind": r.get("kind"),
                         "name": r.get("name") or os.path.basename(r.get("src") or ""),
                         "enable": r.get("enable"), "t": human_time(r.get("ts"))}
                        for r in journal_read(30)[::-1]],
            "detect": self.detect_report,
            "scan_seconds": round(s.duration, 2),
            "thumb_engine": "Pillow" if _get_pil() else "原图直出",
            "thumb_pending": _thumb_q.qsize(),
            "error": self.last_error,
            "game_running": game, "launcher_running": launcher,
        }
        if with_entries:
            st["entries"] = [{k: v for k, v in e.items() if k not in SLIM_DROP}
                             for e in s.entries]
        return st

    def find_entries(self, ids):
        return [self.scan.by_id[i] for i in (ids or []) if i in self.scan.by_id]

    def scope_entries(self, scope):
        scope = scope or {}
        t, v = scope.get("type"), scope.get("value")
        E = self.scan.entries
        if t == "category":
            return [e for e in E if e["category"] == v]
        if t == "char":
            return [e for e in E if e["char"] == v]
        if t == "status":
            return [e for e in E if e["enabled"] == (v == "enabled")]
        return list(E)


# ===========================================================================
# HTTP 服务
# ===========================================================================

def run_detection(app):
    """后台自动查找 ZZMI 并写入配置 (供首启与界面「自动查找」共用)。"""
    try:
        def prog(i, t):
            app.detect_report["step"] = "已检查 %d / %d 个目录…" % (i, t)
        cfg, cands = autodetect_config(progress=prog)
        if cfg:
            app.cfg.update({k: v for k, v in cfg.items() if v != ""})
            app.save_config()
            app.rescan()
            app.detect_report = {"done": True, "step": "",
                                 "found": cfg["zzmi_root"], "candidates": cands,
                                 "message": "已自动找到: %s" % cfg["zzmi_root"]}
        else:
            app.detect_report = {"done": True, "step": "", "found": None,
                                 "candidates": [],
                                 "message": "没找到, 请手动填写 ZZMI 路径"}
    except Exception as ex:
        app.detect_report = {"done": True, "step": "", "found": None,
                             "candidates": [],
                             "message": "自动查找出错: %s" % ex}


class Handler(BaseHTTPRequestHandler):
    server_version = "ZZMIManager/" + VERSION
    app = None
    quiet = True

    def log_message(self, fmt, *args):
        if not self.quiet:
            log("%s - %s" % (self.address_string(), fmt % args))

    def _send(self, code, body=b"", ctype="application/json; charset=utf-8",
              extra=None):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        try:
            self.wfile.write(body)
        except Exception:
            pass

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj, ensure_ascii=False))

    def _qs(self):
        d = {}
        for k, vals in urllib.parse.parse_qs(
                urllib.parse.urlparse(self.path).query,
                keep_blank_values=True).items():
            d[k] = vals[0]
        return d

    def _ok(self, qs):
        return qs.get("t") == self.app.token

    def _body(self):
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            n = 0
        if n <= 0:
            return {}
        try:
            return json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception:
            return {}

    def do_GET(self):
        try:
            path = urllib.parse.urlparse(self.path).path
            qs = self._qs()
            if path in ("/", "/index.html"):
                return self.serve_ui()
            if path == "/bg.jpg":
                # 界面背景图(随 exe 打包)
                try:
                    with open(BG_PATH, "rb") as f:
                        return self._send(200, f.read(),
                                          "image/jpeg")
                except OSError:
                    return self._json({"error": "not found"}, 404)
            if not self._ok(qs):
                return self._json({"error": "unauthorized"}, 403)
            if path == "/api/state":
                return self._json(self.app.state())
            if path == "/api/detail":
                return self._json(self.detail(qs.get("id") or ""))
            if path == "/api/library":
                return self._json(self.library_list())
            if path == "/api/autodetect":
                self.spawn_detect()
                return self._json({"ok": True})
            if path == "/thumb":
                return self.serve_thumb(qs)
            return self._json({"error": "not found"}, 404)
        except Exception:
            log("GET error:\n" + traceback.format_exc())
            return self._json({"error": "internal"}, 500)

    def do_POST(self):
        try:
            qs = self._qs()
            if not self._ok(qs):
                return self._json({"error": "unauthorized"}, 403)
            act = urllib.parse.urlparse(self.path).path.rsplit("/", 1)[-1]
            body = self._body()
            app = self.app

            if act == "toggle":
                r = batch_toggle(app.mods_dir(), app.find_entries(body.get("ids")),
                                 bool(body.get("enabled")))
                app.rescan()
                return self._json({"result": r, "state": app.state()})

            if act == "scope":
                r = batch_toggle(app.mods_dir(), app.scope_entries(body.get("scope")),
                                 bool(body.get("enabled")))
                app.rescan()
                return self._json({"result": r, "state": app.state()})

            if act == "dir_toggle":
                ok, msg = do_toggle_dir(app.mods_dir(), body.get("rel") or "",
                                        bool(body.get("enabled")))
                app.rescan()
                return self._json({"ok": ok, "msg": msg, "state": app.state()})

            if act == "component_toggle":
                e = app.scan.by_id.get(body.get("id") or "")
                md = app.mods_dir()
                root = resolve_rel_dir(md, e["id"]) if e else None
                if not e or not root or not os.path.isdir(root):
                    return self._json({"ok": False, "msg": "找不到该 mod"})
                ok, msg = do_toggle_file(root, body.get("rel") or "",
                                         bool(body.get("enabled")))
                app.rescan()
                return self._json({"ok": ok, "msg": msg, "state": app.state()})

            if act == "variant_select":
                e = app.scan.by_id.get(body.get("id") or "")
                md = app.mods_dir()
                root = resolve_rel_dir(md, e["id"]) if e else None
                if not e or not root or not os.path.isdir(root):
                    return self._json({"ok": False, "msg": "找不到该 mod"})
                ok, msg = do_variant_select(root, body.get("rel") or "")
                app.rescan()
                return self._json({"ok": ok, "msg": msg, "state": app.state()})

            if act == "cycle_set":
                # v1.4.0 起移除变体写入功能: 工具绝不修改用户 ini。
                # 变体一律在游戏内按绑定键切换, 界面只做只读提示。
                return self._json({"ok": False,
                                   "msg": "变体写入功能已移除; 请在游戏内按绑定键切换变体"})

            if act == "set_char":
                return self._json(self.set_char(body))

            if act == "preset":
                return self._json(self.preset_action(body))

            if act == "undo":
                ok, msg = undo_last()
                app.rescan()
                return self._json({"ok": ok, "msg": msg, "state": app.state()})

            if act == "config":
                return self._json(self.config_action(body))

            if act == "rescan":
                app.rescan()
                return self._json({"ok": True, "state": app.state()})

            if act == "launch":
                ok, msg = launch_game(app.cfg)
                return self._json({"ok": ok, "msg": msg})

            if act == "quit":
                self._json({"ok": True, "msg": "bye"})
                threading.Timer(0.3, lambda: os._exit(0)).start()
                return

            if act == "reveal":
                p = body.get("path") or ""
                if body.get("id"):
                    e = app.scan.by_id.get(body["id"])
                    if e:
                        p = resolve_rel_dir(app.mods_dir(), e["id"]) or ""
                elif p and not os.path.isabs(p):
                    p = os.path.join(app.mods_dir(), p)
                ok = open_in_explorer(p)
                return self._json({"ok": ok, "msg": "" if ok else "路径不存在"})

            if act == "openroot":
                return self._json({"ok": open_in_explorer(body.get("path")
                                                          or app.mods_dir())})

            if act == "move":
                root = app.cfg.get("zzmi_root") or ""
                md = app.mods_dir()
                bases = {"mods": md, "root": root}
                ok, msg = do_move(bases.get(body.get("src_base"), md),
                                  body.get("src_rel") or "",
                                  bases.get(body.get("dst_base"), root),
                                  body.get("dst_rel") or "")
                invalidate_lib_cache()
                app.rescan()
                return self._json({"ok": ok, "msg": msg, "state": app.state()})

            if act == "rename":
                e = app.scan.by_id.get(body.get("id") or "")
                if not e:
                    return self._json({"ok": False, "msg": "找不到该 mod"})
                ok, msg = do_rename(app.mods_dir(), e, body.get("name"))
                app.rescan()
                return self._json({"ok": ok, "msg": msg, "state": app.state()})

            if act == "mkdir":
                base = (app.mods_dir() if body.get("base") == "mods"
                        else app.cfg.get("zzmi_root") or "")
                p = safe_join(base, body.get("rel") or "")
                if not p:
                    return self._json({"ok": False, "msg": "路径不合法"})
                try:
                    os.makedirs(p, exist_ok=True)
                    return self._json({"ok": True, "msg": "已创建", "path": p})
                except Exception as ex:
                    return self._json({"ok": False, "msg": str(ex)})

            return self._json({"error": "not found"}, 404)
        except Exception:
            log("POST error:\n" + traceback.format_exc())
            return self._json({"error": "internal"}, 500)

    def serve_ui(self):
        try:
            with open(UI_PATH, "r", encoding="utf-8") as f:
                html = f.read()
        except Exception as ex:
            return self._send(500, "缺少 ui.html: %s" % ex,
                              "text/plain; charset=utf-8")
        html = html.replace("__BOOT__", json.dumps(
            {"token": self.app.token, "version": VERSION}, ensure_ascii=False))
        return self._send(200, html, "text/html; charset=utf-8")

    def serve_thumb(self, qs):
        rel = qs.get("p") or ""
        root = self.app.scan.root or self.app.mods_dir()
        if not rel or not root:
            return self._send(404, b"", "text/plain")
        p = safe_join(root, rel)
        if not p or not os.path.isfile(p):
            return self._send(404, b"", "text/plain")
        tp = cached_thumb(p)
        if not tp:
            _thumb_q.put(p)
            tp = p
        try:
            if os.path.getsize(tp) > 14 * 1024 * 1024:
                return self._send(413, b"", "text/plain")
            with open(tp, "rb") as f:
                data = f.read()
        except Exception:
            return self._send(500, b"", "text/plain")
        ctype = mimetypes.guess_type(tp)[0] or "application/octet-stream"
        return self._send(200, data, ctype, extra={"Cache-Control": "max-age=86400"})

    def detail(self, mid):
        app = self.app
        e = app.scan.by_id.get(mid)
        if not e:
            return {"error": "not found"}
        md = app.mods_dir()
        abs_root = resolve_rel_dir(md, e["id"]) or os.path.join(md, e["path"])
        comp = analyze_components(abs_root) if os.path.isdir(abs_root) \
            else {"components": [], "groups": []}
        inis = []
        if os.path.isdir(abs_root):
            for cur, dirs, files in os.walk(abs_root):
                dirs[:] = [d for d in dirs if d.lower() != "desktop.ini"]
                rel = os.path.relpath(cur, abs_root)
                rel = "" if rel == "." else rel
                for f in files:
                    if f.lower().endswith(".ini"):
                        inis.append({"rel": norm_rel(os.path.join(rel, f)),
                                     "disabled": is_disabled_name(f),
                                     "size": _size(os.path.join(cur, f))})
        return {"entry": e, "abs_path": abs_root,
                "exists": os.path.isdir(abs_root),
                "inis": sorted(inis, key=lambda i: i["rel"].lower()),
                "components": comp.get("components", []),
                "groups": comp.get("groups", []),
                "cycles": parse_cycle_vars(abs_root)
                if os.path.isdir(abs_root) else []}

    def library_list(self):
        app = self.app
        now = time.time()
        if _lib_cache["data"] is not None and now - _lib_cache["t"] < 90:
            return _lib_cache["data"]
        root = app.cfg.get("zzmi_root") or ""
        out = []
        for lib in app.cfg.get("libraries") or []:
            p = safe_join(root, lib)
            items = []
            if p and os.path.isdir(p):
                for name in sorted(os.listdir(p), key=lambda s: s.lower()):
                    sp = os.path.join(p, name)
                    if not os.path.isdir(sp):
                        continue
                    sz = n = 0
                    for cur, dirs, files in os.walk(sp):
                        n += len(files)
                        for f in files:
                            try:
                                sz += os.path.getsize(os.path.join(cur, f))
                            except OSError:
                                pass
                    items.append({"name": name, "size": sz, "size_h": human_size(sz),
                                  "files": n, "disabled": is_disabled_name(name)})
            out.append({"name": lib, "path": p or "", "items": items,
                        "count": len(items)})
        md = app.mods_dir()
        tops = []
        if md and os.path.isdir(md):
            for name in sorted(os.listdir(md), key=lambda s: s.lower()):
                if os.path.isdir(os.path.join(md, name)):
                    tops.append({"name": name, "disabled": is_disabled_name(name)})
        data = {"libraries": out, "mods_top": tops, "root": root, "mods_dir": md}
        _lib_cache["t"] = now
        _lib_cache["data"] = data
        return data

    def set_char(self, body):
        app = self.app
        e = app.scan.by_id.get(body.get("id") or "")
        if not e:
            return {"ok": False, "msg": "找不到该 mod"}
        char = (body.get("char") or "").strip()
        ov = app.cfg.setdefault("char_overrides", {})
        if not char or char == e["char_auto"]:
            ov.pop(e["id"], None)
            ov.pop(e["path"], None)
            msg = "已恢复自动识别: %s" % e["char_auto"]
        else:
            ov[e["id"]] = char
            msg = "角色已设为「%s」" % char
        app.save_config()
        app.rescan()
        return {"ok": True, "msg": msg, "state": app.state()}

    def config_action(self, body):
        app = self.app
        if body.get("zzmi_root"):
            ok, msg = app.set_root(body["zzmi_root"], body.get("importer"),
                                   body.get("mods_dir"))
            if not ok:
                return {"ok": False, "msg": msg}
            app.rescan()
            return {"ok": True, "msg": "已保存", "state": app.state()}
        changed = False
        if body.get("mods_dir"):
            app.cfg["mods_dir"] = body["mods_dir"].strip().strip('"')
            changed = True
        if "theme" in body:
            app.cfg["theme"] = body["theme"]
            changed = True
        if "hide_preview" in body:
            app.cfg["hide_preview"] = bool(body["hide_preview"])
            changed = True
        if body.get("importer"):
            app.cfg["importer"] = body["importer"]
            changed = True
        if "hotkey" in body:
            combo = parse_hotkey(body["hotkey"])
            if not combo:
                return {"ok": False, "msg":
                        "快捷键格式不对。字母/数字要带修饰键, 如 Ctrl+Alt+K; "
                        "单独按 F1~F12 也可以。"}
            app.cfg["hotkey"] = body["hotkey"].strip()
            app.save_config()
            ok, msg = app.hotkey.register(combo)
            return {"ok": ok, "msg": msg if not ok else
                    "快捷键已设为 " + app.cfg["hotkey"], "state": app.state()}
        if changed:
            app.save_config()
            app.rescan()
            invalidate_lib_cache()
        return {"ok": True, "msg": "已保存", "state": app.state()}

    def preset_action(self, body):
        app = self.app
        act = body.get("action")
        name = (body.get("name") or "").strip()
        presets = presets_load()
        if act == "save":
            if not name:
                return {"ok": False, "msg": "请填方案名"}
            presets[name] = {
                "enabled": sorted(e["id"] for e in app.scan.entries if e["enabled"]),
                "total": len(app.scan.entries), "saved": time.time()}
            presets_save(presets)
            return {"ok": True, "msg": "已保存方案「%s」" % name,
                    "state": app.state()}
        if act == "apply":
            p = presets.get(name)
            if not p:
                return {"ok": False, "msg": "没有这个方案"}
            want = set(p.get("enabled") or [])
            off = [e for e in app.scan.entries if e["enabled"] and e["id"] not in want]
            on = [e for e in app.scan.entries if not e["enabled"] and e["id"] in want]
            r1 = batch_toggle(app.mods_dir(), off, False)
            r2 = batch_toggle(app.mods_dir(), on, True)
            app.rescan()
            return {"ok": True, "msg": "已套用「%s」: 启用 %d / 禁用 %d"
                                       % (name, r2["ok"], r1["ok"]),
                    "state": app.state()}
        if act == "delete":
            if name not in presets:
                return {"ok": False, "msg": "没有这个方案"}
            presets.pop(name, None)
            presets_save(presets)
            return {"ok": True, "msg": "已删除方案「%s」" % name,
                    "state": app.state()}
        return {"ok": False, "msg": "未知操作"}

    def spawn_detect(self):
        app = self.app
        if not app.detect_report.get("done", True):
            return
        app.detect_report = {"done": False, "step": "准备扫描…", "found": None,
                             "candidates": [], "message": ""}
        threading.Thread(target=run_detection, args=(app,), daemon=True).start()


def _size(p):
    try:
        return os.path.getsize(p)
    except OSError:
        return 0


# ===========================================================================
# 全局快捷键 (RegisterHotKey, 游戏运行时也能呼出/隐藏管理器窗口)
# ===========================================================================

MOD_ALT, MOD_CONTROL, MOD_SHIFT, MOD_WIN = 0x0001, 0x0002, 0x0004, 0x0008
MOD_NOREPEAT = 0x4000  # 避免长按重复触发
WM_HOTKEY, WM_QUIT = 0x0312, 0x0012
_HOTKEY_ID = 0x5A4D  # 'ZM'


def parse_hotkey(s):
    """'Ctrl+Alt+M' -> (mods, vk)。字母/数字必须带修饰键; 单独 F1~F12 允许。"""
    if not s:
        return None
    mods, key = 0, None
    for part in s.replace(" ", "").split("+"):
        if not part:
            continue
        p = part.lower()
        if p == "ctrl":
            mods |= MOD_CONTROL
        elif p == "alt":
            mods |= MOD_ALT
        elif p == "shift":
            mods |= MOD_SHIFT
        elif p == "win":
            mods |= MOD_WIN
        else:
            key = part
    if not key:
        return None
    k = key.lower()
    vk = None
    if len(k) == 1 and (k.isalpha() or k.isdigit()):
        vk = ord(k.upper())
    elif re.match(r"^f([1-9]|1[0-9]|2[0-4])$", k):
        vk = 0x70 + int(k[1:]) - 1
    else:
        vk = {"space": 0x20, "tab": 0x09, "home": 0x24, "end": 0x23,
              "insert": 0x2D, "delete": 0x2E, "pageup": 0x21,
              "pagedown": 0x22, "up": 0x26, "down": 0x28, "left": 0x25,
              "right": 0x27, "`": 0xC0, "-": 0xBD, "=": 0xBB, "[": 0xDB,
              "]": 0xDD, "\\": 0xDC, ";": 0xBA, "'": 0xDE, ",": 0xBC,
              ".": 0xBE, "/": 0xBF}.get(k)
    if vk is None:
        return None
    if not (mods & (MOD_CONTROL | MOD_ALT | MOD_SHIFT | MOD_WIN)):
        if not re.match(r"^f([1-9]|1[0-9]|2[0-4])$", k):
            return None  # 普通键必须带修饰键, 否则会劫持游戏按键
    return mods, vk


def find_manager_window():
    """找管理器的 Edge/Chrome app 窗口 (按窗口类 + 标题匹配)。"""
    import ctypes
    user32 = ctypes.windll.user32
    # --app 模式的窗口标题就是页面 <title>: "ZZMI Mod 管家"
    h = user32.FindWindowW("Chrome_WidgetWin_1", APP_NAME)
    if h:
        return h
    # 兜底: 枚举顶层窗口找标题前缀
    proto = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)
    hits = []
    GetWindowTextW = user32.GetWindowTextW
    GetClassNameW = user32.GetClassNameW
    IsWindowVisible = user32.IsWindowVisible

    def _cb(hwnd, _lparam):
        try:
            buf = ctypes.create_unicode_buffer(64)
            GetClassNameW(hwnd, buf, 64)
            if buf.value != "Chrome_WidgetWin_1":
                return 1
            buf = ctypes.create_unicode_buffer(128)
            GetWindowTextW(hwnd, buf, 128)
            if buf.value.startswith(APP_NAME):
                hits.append(hwnd)
        except Exception:
            pass
        return 1

    cb = proto(_cb)
    try:
        user32.EnumWindows(cb, None)
    except Exception:
        pass
    return hits[0] if hits else None


def _bring_to_front(hwnd):
    import ctypes
    user32 = ctypes.windll.user32
    SWP_NOSIZE, SWP_NOMOVE, SWP_SHOWWINDOW = 0x0001, 0x0002, 0x0040
    HWND_TOPMOST, HWND_NOTOPMOST = -1, -2
    user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                        SWP_NOSIZE | SWP_NOMOVE | SWP_SHOWWINDOW)
    user32.SetWindowPos(hwnd, HWND_NOTOPMOST, 0, 0, 0, 0,
                        SWP_NOSIZE | SWP_NOMOVE | SWP_SHOWWINDOW)
    user32.SetForegroundWindow(hwnd)


def toggle_manager_window(app):
    """快捷键动作: 纯显隐切换 —— 没窗口就开; 可见(无论是否前台, 游戏内也
    能藏)就隐藏; 隐藏就显示并置前。Edge 进程不退出, 下次还能呼出。"""
    import ctypes
    user32 = ctypes.windll.user32
    hwnd = find_manager_window()
    if not hwnd:
        url = ""
        try:
            url = open(os.path.join(DATA_DIR, "last_url.txt")).read().strip()
        except OSError:
            pass
        if url:
            open_app_window(url, app.cfg.get("win_size") or "1320,880")
        return
    if user32.IsWindowVisible(hwnd):
        user32.ShowWindow(hwnd, 0)              # SW_HIDE (游戏内也能直接藏)
    else:
        user32.ShowWindow(hwnd, 8)              # SW_SHOWNA
        _bring_to_front(hwnd)


class HotkeyManager(object):
    """后台线程 RegisterHotKey + 消息循环; 换键 = 线程发 WM_QUIT 后重启。"""

    def __init__(self, app):
        self.app = app
        self.tid = None
        self.thread = None
        self.ok = None
        self._evt = threading.Event()

    def start(self):
        s = parse_hotkey(self.app.cfg.get("hotkey") or "F9")
        if s:
            return self.register(s)
        return True, ""

    def register(self, combo):
        """返回 (ok, msg)。"""
        self.stop()
        self.ok, self._evt = None, threading.Event()
        self.thread = threading.Thread(target=self._loop, args=(combo,),
                                       daemon=True)
        self.thread.start()
        self._evt.wait(2.0)
        if self.ok:
            return True, "全局快捷键已生效"
        return False, "快捷键注册失败(可能被其他程序占用)"

    def stop(self):
        if self.tid and self.thread and self.thread.is_alive():
            import ctypes
            ctypes.windll.user32.PostThreadMessageW(
                self.tid, WM_QUIT, 0, 0)
            self.thread.join(timeout=1.5)
        self.thread, self.tid = None, None

    def _loop(self, combo):
        import ctypes
        from ctypes import wintypes
        user32, kernel32 = ctypes.windll.user32, ctypes.windll.kernel32
        self.tid = kernel32.GetCurrentThreadId()
        mods, vk = combo
        if not user32.RegisterHotKey(None, _HOTKEY_ID, mods | MOD_NOREPEAT, vk):
            self.ok = False
            self._evt.set()
            return
        self.ok = True
        self._evt.set()
        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            if msg.message == WM_HOTKEY:
                try:
                    toggle_manager_window(self.app)
                except Exception:
                    log("快捷键处理出错:\n" + traceback.format_exc())
        user32.UnregisterHotKey(None, _HOTKEY_ID)


# ===========================================================================
# 启动
# ===========================================================================

def pick_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(THUMB_DIR, exist_ok=True)
    threading.Thread(target=thumb_worker, daemon=True).start()

    app = App()
    have_cfg = app.load_config()
    md = app.mods_dir()
    pending_detect = False
    if have_cfg and md and os.path.isdir(md):
        log("使用已保存的配置:", app.cfg.get("zzmi_root"))
    else:
        # 不阻塞启动: 服务先起来, 界面秒开, 检测在后台跑并由界面显示进度
        log("没有可用配置, 服务启动后在后台自动查找 ZZMI …")
        pending_detect = True
        app.detect_report = {"done": False, "step": "准备扫描…", "found": None,
                             "candidates": [], "message": ""}

    if app.mods_dir() and os.path.isdir(app.mods_dir()):
        log("扫描 Mods:", app.mods_dir())
        s = app.rescan()
        log("共 %d 个 mod / %d 个角色 (启用 %d / 禁用 %d / 部分 %d / 冲突 %d 组), %.2fs"
            % (s.stats["total"], s.stats["chars"], s.stats["enabled"],
               s.stats["disabled"], s.stats["partial"], s.stats["conflicts"],
               s.duration))

    port = pick_port()
    Handler.app = app
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    httpd.daemon_threads = True
    app.httpd = httpd
    url = "http://127.0.0.1:%d/?t=%s" % (port, app.token)
    try:
        with open(os.path.join(DATA_DIR, "last_url.txt"), "w") as f:
            f.write(url)
    except Exception:
        pass
    log("")
    log("  %s v%s" % (APP_NAME, VERSION))
    log("  界面: %s" % url)
    log("  数据: %s" % DATA_DIR)
    log("  关掉这个窗口(或界面「设置」里的退出)即可结束程序")
    log("")
    if not os.environ.get("ZZMI_NO_BROWSER"):
        threading.Timer(0.6, lambda: open_app_window(
            url, app.cfg.get("win_size") or "1320,880")).start()
    if pending_detect:
        threading.Thread(target=run_detection, args=(app,), daemon=True).start()
    try:
        ok_hk, msg_hk = app.hotkey.start()
    except Exception as ex:
        ok_hk, msg_hk = False, str(ex)
    if app.cfg.get("hotkey"):
        log("全局快捷键: %s%s" % (app.cfg["hotkey"],
                                 "" if ok_hk else "  (注册失败: %s)" % msg_hk))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        log("bye")


if __name__ == "__main__":
    main()
