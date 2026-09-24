# -*- coding: utf-8 -*-
"""v1.5.13 后端纯函数回归: 角色子分类 / 选择性下载 / 下载历史。
默认离线(只测本地逻辑); 联网用例用 GB_LIVE_TEST=1 打开。
运行: python tests/test_gb2.py
"""
import os
import sys
import json
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

# 隔离数据目录, 绝不碰真实 config / 下载
_TMP = tempfile.mkdtemp(prefix="zzmi_gb2_")
os.environ["ZZMI_MANAGER_DATA"] = _TMP

import zzmi_manager as Z  # noqa: E402

FAIL = []
PASS = []


def ck(name, cond, extra=""):
    (PASS if cond else FAIL).append(name)
    print(("  ok   " if cond else "  FAIL ") + name + ((" | " + str(extra)) if extra else ""))


def main():
    print("== v1.5.13 GameBanana 后端回归 ==")
    print("data dir:", Z.DATA_DIR)

    # ---- 1. 常量
    ck("GB_CHAR_CAT = 30305", Z.GB_CHAR_CAT == 30305, Z.GB_CHAR_CAT)

    # ---- 2. gb_list 支持 cat 覆盖 (用 fake http 拦掉真请求)
    calls = []

    class FakeResp(object):
        def __init__(self, payload):
            self._b = json.dumps(payload).encode("utf-8")
            self.headers = {}

        def read(self):
            return self._b

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    real_urlopen = Z.urllib.request.urlopen

    def fake_urlopen(req, timeout=None):
        u = req.full_url if hasattr(req, "full_url") else str(req)
        calls.append(u)
        return FakeResp({"_aMetadata": {"_nRecordCount": 130},
                         "_aRecords": [{"_idRow": 1, "_sName": "T", "_bHasFiles": True,
                                        "_aPreviewMedia": {"_aImages": []}}]})

    Z.urllib.request.urlopen = fake_urlopen
    try:
        d = Z.gb_list("game", 19567, 1, 30, cat=30336)
        ck("gb_list(cat=) 走 Generic_Category", "Generic_Category]=30336" in calls[-1],
           calls[-1].split("?")[-1])
        ck("gb_list(cat=) 结果 ok", d["total"] == 130 and len(d["items"]) == 1, d["total"])
        d2 = Z.gb_list("category", 30305, 2, 30)
        ck("gb_list 无 cat 仍按原 kind", "Generic_Category]=30305" in calls[-1])
        ck("gb_list page 生效", "_nPage=2" in calls[-1])
        # perpage 夹取
        Z.gb_list("category", 30305, 1, 999)
        ck("perpage 上限夹到 50", "_nPerpage=50" in calls[-1])
    finally:
        Z.urllib.request.urlopen = real_urlopen

    # ---- 3. 下载历史
    Z.gb_hist_clear()
    Z.gb_hist_mark(718690, "a.zip", os.path.join(_TMP, "downloads", "a.zip"))
    h = Z.gb_hist_get()
    ck("gb_hist_mark 写入", ("718690:a.zip" in h), list(h.keys()))
    ck("历史带 file/path", h.get("718690:a.zip", {}).get("file") == "a.zip")
    Z.gb_hist_clear()
    ck("gb_hist_clear 清空", Z.gb_hist_get() == {})

    # ---- 4. gb_files_batch: 用假 gb_mod_files
    real_mf = Z.gb_mod_files
    seen = []

    def fake_mf(mid):
        seen.append(mid)
        if mid == 3:
            raise RuntimeError("boom")
        return {"id": mid, "name": "m%d" % mid,
                "files": [{"name": "f%d.zip" % mid, "size": 10, "url": "u", "md5": "", "av": "clean"}]}

    Z.gb_mod_files = fake_mf
    try:
        r = Z.gb_files_batch([1, 2, 3, 4], limit=10, workers=2)
        ck("gb_files_batch 返回成功的", set(r.keys()) == {"1", "2", "4"}, sorted(r.keys()))
        ck("gb_files_batch 失败的被跳过", "3" not in r)
        ck("gb_files_batch 保留文件列表", r["1"]["files"][0]["name"] == "f1.zip")
        r2 = Z.gb_files_batch(["x", None, 5], limit=10)
        ck("gb_files_batch 非法 id 被滤掉", list(r2.keys()) == ["5"], list(r2.keys()))
    finally:
        Z.gb_mod_files = real_mf

    # ---- 5. 选择性下载 worker: 只下 picks 里的文件
    dl_calls = []

    def fake_dl_one(url, dest, jid, idx, nf):
        dl_calls.append(os.path.basename(dest))
        with open(dest, "wb") as f:
            f.write(b"x" * 8)
        return 8

    real_dl1 = Z._gb_dl_one
    real_mf2 = Z.gb_mod_files
    Z._gb_dl_one = fake_dl_one
    Z.gb_mod_files = lambda mid: {"id": mid, "name": "multi", "files": [
        {"name": "a.zip", "size": 8, "url": "u1", "md5": "", "av": "clean"},
        {"name": "b.zip", "size": 8, "url": "u2", "md5": "", "av": "clean"},
        {"name": "c.zip", "size": 8, "url": "u3", "md5": "", "av": "clean"},
    ]}
    try:
        cfg = {"downloads_dir": os.path.join(_TMP, "downloads")}
        os.makedirs(cfg["downloads_dir"], exist_ok=True)
        # 全下
        jid = Z.gb_new_job(99, "multi")
        Z.gb_download_worker(jid, cfg, 99)
        j = Z.gb_get_job(jid)
        ck("全下: state=done", j["state"] == "done", j["state"])
        ck("全下: 3 个文件", j["ok_n"] == 3, j.get("ok_n"))
        ck("全下: results 有 3 条", len(j["results"]) == 3, len(j.get("results") or []))
        # 只下 b (先清掉上一轮留下的文件, 免得重名变 b (2))
        del dl_calls[:]
        for n in os.listdir(cfg["downloads_dir"]):
            try:
                os.remove(os.path.join(cfg["downloads_dir"], n))
            except OSError:
                pass
        jid2 = Z.gb_new_job(99, "multi")
        Z.gb_download_worker(jid2, cfg, 99, picks=["b.zip"])
        j2 = Z.gb_get_job(jid2)
        ck("选下: 只下了 b.zip", dl_calls == ["b.zip"], dl_calls)
        ck("选下: ok_n=1", j2["ok_n"] == 1, j2.get("ok_n"))
        # picks 名字对不上 -> 退回全下(不卡死)
        del dl_calls[:]
        jid3 = Z.gb_new_job(99, "multi")
        Z.gb_download_worker(jid3, cfg, 99, picks=["不存在.zip"])
        ck("选下: 名字对不上退回全下", len(dl_calls) == 3, dl_calls)
        # 历史被记录
        hh = Z.gb_hist_get()
        ck("下载后写了历史", any(k.startswith("99:") for k in hh), sorted(hh)[:4])
    finally:
        Z._gb_dl_one = real_dl1
        Z.gb_mod_files = real_mf2

    # ---- 6. 单个文件失败 -> 部分完成 + 半截文件被清掉
    def flaky(url, dest, jid, idx, nf):
        if "b" in os.path.basename(dest):
            with open(dest, "wb") as f:
                f.write(b"partial")
            raise RuntimeError("net down")
        with open(dest, "wb") as f:
            f.write(b"y" * 4)
        return 4

    Z._gb_dl_one = flaky
    Z.gb_mod_files = lambda mid: {"id": mid, "name": "multi", "files": [
        {"name": "a.zip", "size": 4, "url": "u1", "md5": "", "av": "clean"},
        {"name": "b.zip", "size": 4, "url": "u2", "md5": "", "av": "clean"},
    ]}
    try:
        folder = os.path.join(_TMP, "d2")
        os.makedirs(folder, exist_ok=True)
        jid4 = Z.gb_new_job(77, "multi")
        Z.gb_download_worker(jid4, {"downloads_dir": folder}, 77)
        j4 = Z.gb_get_job(jid4)
        ck("部分失败: state=done", j4["state"] == "done", j4["state"])
        ck("部分失败: ok=1 err=1", (j4["ok_n"], j4["err_n"]) == (1, 1), (j4.get("ok_n"), j4.get("err_n")))
        ck("部分失败: 半截文件已删", not os.path.isfile(os.path.join(folder, "b.zip")))
        ck("部分失败: results 标了对错", [x["ok"] for x in j4["results"]] == [True, False],
           [x["ok"] for x in j4["results"]])
    finally:
        Z._gb_dl_one = real_dl1
        Z.gb_mod_files = real_mf2

    # ---- 7. gb_unique_path 不覆盖
    fdir = os.path.join(_TMP, "uniq")
    os.makedirs(fdir, exist_ok=True)
    p1 = Z.gb_unique_path(fdir, "x.zip")
    open(p1, "wb").close()
    p2 = Z.gb_unique_path(fdir, "x.zip")
    ck("重名加 (2)", os.path.basename(p2) == "x (2).zip", os.path.basename(p2))
    # 注: a:b*c?.zip -> 冒号在 basename 里已被系统吞掉, 留下 a 前缀
    san = os.path.basename(Z.gb_unique_path(fdir, "a:b*c?.zip"))
    ck("文件名消毒: 去掉 * ? 等非法字符", ("*" not in san and "?" not in san and san.endswith(".zip")),
       san)
    san2 = os.path.basename(Z.gb_unique_path(fdir, "bad|name<>.zip"))
    ck("文件名消毒: 去掉 | < >", ("|" not in san2 and "<" not in san2),
       san2)

    # ---- 8. 子分类解析(离线: 假 json)
    class FakeResp2(object):
        def __init__(self, payload):
            self._b = json.dumps(payload).encode("utf-8")
            self.headers = {}

        def read(self):
            return self._b

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    Z.gb_http_json = lambda url, timeout=20: [
        {"_sName": "Anby Demara", "_sUrl": "https://gamebanana.com/mods/cats/30336",
         "_nItemCount": 130, "_sIconUrl": "ico"},
        {"_sName": "Bad Row", "_sUrl": "https://gamebanana.com/whatever", "_nItemCount": 0},
    ]
    # cn 走 gb_char_cn 时, 表里没有的会去机翻 —— 这里桩掉, 别打真网络
    Z.gb_translate_one = lambda t: t
    Z.gb_translate_many = lambda ts: {t: t for t in (ts or [])}
    Z._gb_subs_cache = None
    subs = Z.gb_subcategories(30305)
    ck("gb_subcategories 解析出 id", subs and subs[0]["id"] == 30336, subs[:1])
    ck("gb_subcategories 丢掉没 cats/ 的", len(subs) == 1, len(subs))
    ck("gb_subcategories 带 count", subs[0]["count"] == 130)
    ck("gb_subcategories 带中文名 cn", subs[0].get("cn") == "安比·德玛拉", subs[0].get("cn"))

    # ---- 8b. v1.5.14: 角色中文名对照表
    ck("GB_CHAR_CN 非空且够大", len(Z.GB_CHAR_CN) >= 60, len(Z.GB_CHAR_CN))
    ck("gb_char_cn 精确命中", Z.gb_char_cn("Anby Demara") == "安比·德玛拉", Z.gb_char_cn("Anby Demara"))
    ck("gb_char_cn 大小写不敏感", Z.gb_char_cn("hoshimi MIYABI") == "星见雅")
    ck("gb_char_cn 多余空格归一", Z.gb_char_cn("Anby  Demara") == "安比·德玛拉")
    ck("gb_char_cn 去括号后缀", Z.gb_char_cn("Anby Demara (skin)") == "安比·德玛拉",
       Z.gb_char_cn("Anby Demara (skin)"))
    ck("gb_char_cn 空串安全", Z.gb_char_cn("") == "")
    # 表里每个 key 都要能反查到(防止手写表笔误)
    bad_key = [k for k, v in Z.GB_CHAR_CN.items()
               if not v or not all(ord(c) > 127 for c in v.replace("·", "").replace(" ", ""))]
    ck("对照表值都是中文", not bad_key, bad_key[:3])
    ck("对照表 key 都是小写", all(k == k.lower() for k in Z.GB_CHAR_CN))

    # ---- 8c. v1.5.14: pick_folder 不再依赖 tkinter
    import inspect as _insp
    pf = _insp.getsource(Z.pick_folder)
    ck("pick_folder 首选 Windows 原生框", "SHBrowseForFolder" in pf or "_pick_folder_win" in pf)
    ck("pick_folder 支持 owner 窗口", "owner" in _insp.signature(Z.pick_folder).parameters)
    ck("pick_folder 在无 tkinter 时也能 import", callable(Z.pick_folder))
    ck("存在 _shell_execute 回落", callable(getattr(Z, "_shell_execute", None)))
    of = _insp.getsource(Z.open_in_explorer)
    ck("open_in_explorer 三级回落", "ShellExecuteW" in of and "explorer" in of)
    ck("存在看门狗 _pick_keep_front", callable(getattr(Z, "_pick_keep_front", None)))

    # ---- 8e. v1.5.16: 指针截断回归(用户实测「选择…」永远失败, 日志 access violation)
    # 根因: SHBrowseForFolderW 返回 PIDL 指针(64位), ctypes 默认按 c_int 截断
    #      -> SHGetPathFromIDListW 拿野指针 -> 进程崩溃。必须显式声明 restype。
    pfw = _insp.getsource(Z._pick_folder_win)
    ck("SHBrowseForFolderW 声明了 restype", "SHBrowseForFolderW.restype" in pfw)
    ck("restype 是 c_void_p(不是默认 int)",
       "SHBrowseForFolderW.restype = ctypes.c_void_p" in pfw.replace("  ", " "))
    ck("SHBrowseForFolderW 声明了 argtypes", "SHBrowseForFolderW.argtypes" in pfw)
    ck("SHGetPathFromIDListW 声明了签名",
       "SHGetPathFromIDListW.argtypes" in pfw and "SHGetPathFromIDListW.restype" in pfw)
    ck("入参按 c_void_p 传", "ctypes.c_void_p(pidl)" in pfw)
    ck("CoTaskMemFree 声明了 argtypes", "CoTaskMemFree.argtypes" in pfw)
    kf = _insp.getsource(Z._pick_keep_front)
    ck("FindWindowW 声明了 restype(HWND)", "FindWindowW.restype" in kf)
    ck("SetWindowPos 声明了 argtypes", "SetWindowPos.argtypes" in kf)

    # ---- 8d. v1.5.15: 路径引号 / 盘符处理(用户报「目录改不了」的真根因)
    ck("strip_path_quotes 剥双引号", Z.strip_path_quotes('"D:\\xx"') == "D:\\xx",
       Z.strip_path_quotes('"D:\\xx"'))
    ck("strip_path_quotes 剥引号+空格", Z.strip_path_quotes("  'D:\\xx'  ") == "D:\\xx",
       Z.strip_path_quotes("  'D:\\xx'  "))
    ck("strip_path_quotes 剥全角引号", Z.strip_path_quotes("\u201cD:\\xx\u201d") == "D:\\xx",
       Z.strip_path_quotes("\u201cD:\\xx\u201d"))
    ck("strip_path_quotes 不动正常路径", Z.strip_path_quotes("D:\\xx") == "D:\\xx")
    ck("带引号路径判为绝对路径", Z.is_abs_path('"D:\\xx"'), "带引号应识别")
    ck("带引号盘符判为绝对路径", Z.is_abs_path('"D:\\"'))
    ck("光给盘符判为绝对路径", Z.is_abs_path("D:"))
    ck("相对路径仍判非绝对", not Z.is_abs_path("mydl"))
    ck("空串仍判非绝对", not Z.is_abs_path(""))
    ck("strip_abs_prefix 也剥引号", Z.strip_abs_prefix('"abs:D:\\xx"') == "D:\\xx",
       Z.strip_abs_prefix('"abs:D:\\xx"'))

    # ---- 9. 联网(可选)
    if os.environ.get("GB_LIVE_TEST") == "1":
        print("== 联网用例 ==")
        try:
            real = Z.gb_subcategories(30305, refresh=True)
            ck("live: 子分类 >= 50 个", len(real) >= 50, len(real))
            anby = [x for x in real if x["id"] == 30336]
            ck("live: 含安比分类", bool(anby), anby[:1])
            lp = Z.gb_list("category", 30336, 1, 5)
            ck("live: 安比分类有 mod", lp["total"] > 0, lp["total"])
        except Exception as e:
            ck("live 调用", False, repr(e))

    print("")
    print("PASS %d / FAIL %d" % (len(PASS), len(FAIL)))
    if FAIL:
        print("FAILED: %s" % FAIL)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
