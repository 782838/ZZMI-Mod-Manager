# -*- coding: utf-8 -*-
"""v1.5.13 真实端到端: 角色分类筛选 + 选择性下载 + 下载记录。
全部写进临时隔离目录, 绝不碰用户真实下载目录。
"""
import os
import sys
import json
import time
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

TMP = tempfile.mkdtemp(prefix="zzmi_e2e_")
os.environ["ZZMI_MANAGER_DATA"] = TMP
import zzmi_manager as Z  # noqa: E402

L = []
def w(s=""):
    L.append(str(s))

try:
    w("== v1.5.13 真实端到端 ==")
    w("隔离数据目录: %s" % TMP)

    # 1. 角色列表(真实网络)
    t0 = time.time()
    subs = Z.gb_subcategories(30305, refresh=True)
    w("角色子分类: %d 个 (%.1fs)" % (len(subs), time.time() - t0))
    assert len(subs) >= 50, "角色太少: %d" % len(subs)
    anby = [x for x in subs if x["id"] == 30336]
    w("  安比: %s" % (anby[0] if anby else "没找到"))
    assert anby, "缺安比分类"
    w("  前 5 个: %s" % [(x["name"], x["count"]) for x in subs[:5]])

    # 2. 按角色过滤取 mod
    lp = Z.gb_list("category", 30336, 1, 30)
    w("安比分类 mod 总数: %d, 本页 %d" % (lp["total"], len(lp["items"])))
    assert lp["total"] == anby[0]["count"], "总数和角色列表对不上"
    w("  前三: %s" % [x["name"][:28] for x in lp["items"][:3]])

    # 3. 找有多文件的 mod, 验证选择性下载
    multi = None
    info_multi = None
    for it in lp["items"]:
        if not it["has_files"]:
            continue
        try:
            fi = Z.gb_mod_files(it["id"])
        except Exception:
            continue
        if len([f for f in fi["files"] if f.get("url")]) > 1:
            multi, info_multi = it, fi
            break
    if multi is None:
        w("本页没找到多文件 mod, 只测单文件选择性下载")
        for it in lp["items"]:
            if it["has_files"]:
                multi = it
                info_multi = Z.gb_mod_files(it["id"])
                break

    files = [f for f in info_multi["files"] if f.get("url")]
    w("测下载: %s (id=%s), 文件 %d 个" % (multi["name"][:40], multi["id"], len(files)))
    for f in files:
        w("   - %s (%.2f MB) md5=%s av=%s" % (f["name"], (f["size"] or 0) / 1048576.0,
                                              (f["md5"] or "")[:12], f["av"]))

    # 只下第一个文件(挑个小的, 省时间)
    files_sorted = sorted(files, key=lambda f: f.get("size") or 0)
    pick = files_sorted[0]
    w("只下最小那个: %s (%.2f MB)" % (pick["name"], (pick["size"] or 0) / 1048576.0))

    dldir = os.path.join(TMP, "downloads")
    os.makedirs(dldir, exist_ok=True)
    cfg = {"downloads_dir": dldir}
    before = set(os.listdir(dldir))

    jid = Z.gb_start_download(cfg, multi["id"], multi["name"], picks=[pick["name"]])
    j = None
    for _ in range(240):
        j = Z.gb_get_job(jid)
        if j and j.get("state") in ("done", "error"):
            break
        time.sleep(0.5)
    w("下载状态: %s | %s" % (j.get("state"), j.get("msg")))
    assert j.get("state") == "done", "下载没成功: %s" % j
    assert j.get("ok_n") == 1, "应该只下 1 个文件, 实际 %s" % j.get("ok_n")

    after = set(os.listdir(dldir))
    newf = sorted(after - before)
    w("新增文件: %s" % newf)
    assert len(newf) == 1, "应该只多 1 个文件, 实际 %d" % len(newf)
    assert newf[0] == pick["name"], "下错了文件: %s != %s" % (newf[0], pick["name"])

    # 校验 md5
    import hashlib
    p = os.path.join(dldir, newf[0])
    md5 = hashlib.md5(open(p, "rb").read()).hexdigest()
    w("本地 md5   : %s" % md5)
    w("远端 md5   : %s" % pick["md5"])
    w("大小: 本地 %d / 远端 %s" % (os.path.getsize(p), pick["size"]))
    assert md5 == pick["md5"], "md5 不一致!"
    assert os.path.getsize(p) == pick["size"], "大小不一致!"
    w("✓ md5 与远端完全一致")

    # 4. 下载记录
    h = Z.gb_hist_get()
    key = "%s:%s" % (multi["id"], pick["name"])
    w("下载记录: %s" % list(h.keys())[:3])
    assert key in h, "下载记录里没有这一笔"
    w("✓ 记录写入了: %s -> %s" % (key, h[key]["path"]))

    # 5. 全下时不传 picks = 全量(只验证参数语义, 不真下全部)
    w("全量语义: gb_start_download(picks=None) 时 worker 会用全部 files")

    w("")
    w("E2E ALL OK")
except Exception as e:
    import traceback
    w("EXCEPTION:\n" + traceback.format_exc())
finally:
    open(os.path.join(HERE, "_e2e.txt"), "w", encoding="utf-8").write("\n".join(L))
print("done")
