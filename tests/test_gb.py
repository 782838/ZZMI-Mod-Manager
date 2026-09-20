# -*- coding: utf-8 -*-
"""v1.5.12 GameBanana 下载区: 后端纯函数回归(离线)。

联网用例(真的去爬/下载)默认跳过, 设环境变量 GB_LIVE_TEST=1 才跑:
    set GB_LIVE_TEST=1 && python tests/test_gb.py
"""
import os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("ZZMI_MANAGER_DATA", os.path.join(HERE, "_testgb_data"))
sys.path.insert(0, os.path.dirname(HERE))
import zzmi_manager as Z

bad = []


def check(name, ok):
    print(("  [OK]   " if ok else "  [FAIL] ") + name)
    if not ok:
        bad.append(name)


print("=== gb_parse_url ===")
cases = [
    ("https://gamebanana.com/mods/cats/30305", ("category", "30305")),
    ("http://gamebanana.com/mods/cats/30305?x=1", ("category", "30305")),
    ("https://gamebanana.com/mods/games/19567", ("game", "19567")),
    ("https://gamebanana.com/games/19567", ("game", "19567")),
    ("https://gamebanana.com/mods/718876", ("mod", "718876")),
    ("gamebanana.com/mods/cats/12", ("category", "12")),
    ("30305", ("category", "30305")),
]
for url, want in cases:
    k, g, e = Z.gb_parse_url(url)
    check("%s -> %s/%s" % (url[:44], k, g), (k, g) == want and not e)

print("=== gb_parse_url 拒绝 ===")
for url in ["", "https://example.com/x", "https://gamebanana.com/", "随便写点啥"]:
    k, g, e = Z.gb_parse_url(url)
    check("拒绝 %r" % url[:40], k is None and bool(e))

print("=== gb_unique_path ===")
d = tempfile.mkdtemp(prefix="gbt_")
p1 = Z.gb_unique_path(d, "a.zip")
open(p1, "wb").write(b"x")
p2 = Z.gb_unique_path(d, "a.zip")
open(p2, "wb").write(b"x")
p3 = Z.gb_unique_path(d, "a.zip")
check("重名自动加 (2) (3)", p2.endswith("a (2).zip") and p3.endswith("a (3).zip"))
p4 = Z.gb_unique_path(d, 'bad:name?.zip')
check("非法字符被消毒", ":" not in os.path.basename(p4) and "?" not in os.path.basename(p4))

print("=== _gb_item 解析 ===")
rec = {
    "_idRow": 718876,
    "_sName": "Genderbend Nangong Yu",
    "_sProfileUrl": "https://gamebanana.com/mods/718876",
    "_aSubmitter": {"_sName": "aurue"},
    "_nLikeCount": 6, "_nViewCount": 100, "_bHasFiles": True,
    "_aPreviewMedia": {"_aImages": [
        {"_sType": "screenshot",
         "_sBaseUrl": "https://images.gamebanana.com/img/ss/mods",
         "_sFile": "x.jpg", "_sFile530": "530-90_x.jpg"},
        {"_sType": "screenshot",
         "_sBaseUrl": "https://images.gamebanana.com/img/ss/mods",
         "_sFile": "y.jpg"},
    ]},
}
it = Z._gb_item(rec)
check("id/name/author", it["id"] == 718876 and it["author"] == "aurue"
      and it["name"] == "Genderbend Nangong Yu")
check("优先取 530 缩略图", it["preview"].endswith("/530-90_x.jpg"))
check("多图都收进 previews", len(it["previews"]) == 2)
check("has_files 透传", it["has_files"] is True)

print("=== gb_downloads_dir 默认落到数据目录 ===")
cfg = {}
dirp = Z.gb_downloads_dir(cfg)
check("默认目录存在且以 downloads 结尾",
      os.path.isdir(dirp) and dirp.replace("\\", "/").endswith("/downloads"))
custom = os.path.join(tempfile.mkdtemp(prefix="gbd_"), "我的下载")
check("自定义目录会被创建",
      Z.gb_downloads_dir({"downloads_dir": custom}) == custom and os.path.isdir(custom))

if os.environ.get("GB_LIVE_TEST"):
    print("=== 联网冒烟(GB_LIVE_TEST=1) ===")
    d = Z.gb_list("category", "30305", 1, 3)
    check("爬到列表且有预览图",
          d["total"] > 0 and len(d["items"]) == 3 and d["items"][0]["preview"].startswith("http"))
    m = Z.gb_translate_many(["Cleavage Sweater Skin"])
    check("翻译返回了结果", bool(m.get("Cleavage Sweater Skin")))
else:
    print("\n(联网用例已跳过; 设 GB_LIVE_TEST=1 可跑)")

print()
if bad:
    print("TEST_GB FAILED: " + ", ".join(bad))
    sys.exit(1)
print("TEST_GB PASSED")
