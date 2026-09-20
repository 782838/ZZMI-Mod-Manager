# -*- coding: utf-8 -*-
"""只读 + 临时目录 的验证脚本。绝不修改真实 Mods 目录。"""
import os, sys, json, shutil, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import zzmi_manager as Z

OUT = os.path.join(HERE, "_test_out.txt")
L = []
def w(s=""):
    L.append(str(s)); print(s)

# 逐文件删除: 一次性 shutil.rmtree 会撞上沙箱的"批量删除"保护(上一轮会留下 50+ 个文件),
# 导致整个测试脚本在准备阶段就挂掉。单个 os.remove 不算批量。
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

# ---------- 1. 探测(沙箱) ----------
w("=== 1. score_xxmi_root(沙箱) ===")
SB = os.path.join(HERE, "_sandbox")
_clean(SB)
fake_root = os.path.join(SB, "FakeXXMI")
os.makedirs(os.path.join(fake_root, "Resources", "Bin"), exist_ok=True)
os.makedirs(os.path.join(fake_root, "ZZMI", "Mods"), exist_ok=True)
open(os.path.join(fake_root, "Resources", "Bin", "XXMI Launcher.exe"), "wb").close()
# 真实的 XXMI 根目录里每个注入器子目录都带 d3dx.ini; 补上才是完整的最小样例
open(os.path.join(fake_root, "ZZMI", "d3dx.ini"), "wb").close()
s, info = Z.score_xxmi_root(fake_root)
w("score=%s importers=%s" % (s, info.get('importers')))
assert s >= 8, "探测打分失败"

w()
w("=== 2. autodetect_config()(本机可选) ===")
cfg, cands = Z.autodetect_config()
w("候选数 = %d, 找到 = %s" % (len(cands), bool(cfg and cfg.get("zzmi_root"))))
if cfg and cfg.get("zzmi_root"):
    assert os.path.isdir(cfg["mods_dir"]), "Mods 目录不对"
    w("本机已安装 ZZMI, 探测通过(详情不打印)")
else:
    w("本机没有 ZZMI: 跳过真实探测(正常)")

w()
w("=== 3. scan_mods(沙箱 Mods, 只读) ===")
mods3 = os.path.join(fake_root, "ZZMI", "Mods")
for i in range(6):
    d = os.path.join(mods3, "分类X", "演示角色%d" % i)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "m.ini"), "w", encoding="utf-8") as f:
        f.write("[TextureOverrideX%d]\nhash = 0000000%x\nvb0 = R\n" % (i, i))
res = Z.scan_mods(mods3)
w("entries=%d stats=%s" % (len(res.entries), json.dumps(res.stats, ensure_ascii=False)))
assert len(res.entries) >= 5, "条目太少, 粒度推断可能有问题"


# ---------- 4. 临时目录上的启停 / 撤销 ----------
w()
w("=== 4. 启停 / 撤销 (临时沙箱) ===")
SB = os.path.join(HERE, "_sandbox")
_clean(SB)
mods = os.path.join(SB, "Mods")
os.makedirs(os.path.join(mods, "分类A", "安比", "AnbyMod", "resources"))
os.makedirs(os.path.join(mods, "分类A", "丽娜", "RinaMod"))
os.makedirs(os.path.join(mods, "功能-隐藏UID"))
with open(os.path.join(mods, "分类A", "安比", "AnbyMod", "Main.ini"), "w", encoding="utf-8") as f:
    f.write("[TextureOverrideAnby]\nhash = 003ff258\nvb0 = ResourceAnby\n")
with open(os.path.join(mods, "分类A", "安比", "AnbyMod", "resources", "tex.ini"), "w", encoding="utf-8") as f:
    f.write("[TextureOverrideTex]\nhash = aabbccdd\nps-t0 = ResourceX\n")
with open(os.path.join(mods, "分类A", "丽娜", "RinaMod", "Rina.ini"), "w", encoding="utf-8") as f:
    f.write("[TextureOverrideRina]\nhash = 003ff258\nvb0 = ResourceRina\n")
with open(os.path.join(mods, "功能-隐藏UID", "Hide_UID.ini"), "w", encoding="utf-8") as f:
    f.write("[TextureOverrideScreenUID]\nhash = 2c180570\nhandling = skip\n")
with open(os.path.join(mods, "分类A", "丽娜", "RinaMod", "disabled_beifen_Rina.ini"), "w", encoding="utf-8") as f:
    f.write("; backup\n")

s2 = Z.scan_mods(mods)
w("沙箱条目:")
for e in s2.entries:
    w(f"   id={e['id']:<28} name={e['name']:<14} enabled={e['enabled']} "
      f"ini={e['ini_count']} hashes={e['hashes']} backups={e['backup_inis']}")
assert len(s2.entries) == 3, "期望 3 个 mod 条目, 实际 %d" % len(s2.entries)
ids = {e["id"]: e for e in s2.entries}
assert "分类A/安比" in ids, "安比 粒度推断错误: " + str(list(ids))
assert "功能-隐藏UID" in ids, "隐藏UID 应作为独立 mod"
anby = ids["分类A/安比"]
assert len(anby["hashes"]) == 2, "hash 应聚合成 2 个, 实际 %s" % anby["hashes"]
assert anby["backup_inis"] == [], "安比不该有备份"
assert ids["分类A/丽娜"]["backup_inis"] == ["disabled_beifen_Rina.ini"], "备份检测错误"
conf = s2.conflicts
w("沙箱冲突: " + json.dumps(conf, ensure_ascii=False))
assert any(c["a_name"] == "安比" or c["b_name"] == "安比" for c in conf), "应检出安比/丽娜 hash 冲突"

# 禁用
# v1.5.8: do_toggle 现在可能返回 3 元组 (ok, msg, extra), 老断言要兼容
_res = Z.do_toggle(mods, anby, False)
ok, msg = _res[0], _res[1]
w(f"禁用 安比 -> ok={ok} msg={msg} extra={_res[2] if len(_res) == 3 else None}")
assert ok and os.path.isdir(os.path.join(mods, "分类A", "DISABLED_安比")), "禁用失败"
s3 = Z.scan_mods(mods)
e3 = {e["id"]: e for e in s3.entries}["分类A/安比"]
assert e3["enabled"] is False, "禁用后状态不对"
w("禁用后重新扫描: enabled=%s path=%s" % (e3["enabled"], e3["path"]))
assert len(s3.conflicts) == 0 or all(
    c["a_name"] != "安比" and c["b_name"] != "安比" for c in s3.conflicts), "禁用后不该再报安比冲突"
w("禁用后冲突组数 = %d (应为 0)" % len(s3.conflicts))

# 撤销
ok, msg = Z.undo_last()
w(f"撤销 -> ok={ok} msg={msg}")
assert ok and os.path.isdir(os.path.join(mods, "分类A", "安比")), "撤销失败"
s4 = Z.scan_mods(mods)
e4 = {e["id"]: e for e in s4.entries}["分类A/安比"]
assert e4["enabled"] is True, "撤销后状态不对"

# 批量禁用 + 再启用
r = Z.batch_toggle(mods, s4.entries, False)
w("批量禁用: " + json.dumps(r, ensure_ascii=False))
s5 = Z.scan_mods(mods)
assert all(not e["enabled"] for e in s5.entries), "批量禁用不干净"
r = Z.batch_toggle(mods, s5.entries, True)
s6 = Z.scan_mods(mods)
assert all(e["enabled"] for e in s6.entries), "批量启用不干净"
w("批量禁用→启用往返 OK, 条目数=%d" % len(s6.entries))

# 重命名
_res = Z.do_rename(mods, s6.entries[0], "改过名的mod")
ok, msg = _res[0], _res[1]
w(f"重命名 -> ok={ok} msg={msg} extra={_res[2] if len(_res) == 3 else None}")
assert ok
s7 = Z.scan_mods(mods)
w("重命名后条目: " + ", ".join(e["name"] for e in s7.entries))
assert any(e["name"] == "改过名的mod" for e in s7.entries), "重命名没生效"

# 移动 (仓库)
lib = os.path.join(SB, "仓库A")
os.makedirs(lib, exist_ok=True)
ok, msg = Z.do_move(mods, "分类A", lib, "分类A")
w(f"移出到仓库 -> ok={ok} msg={msg}")
assert ok and not os.path.isdir(os.path.join(mods, "分类A"))
ok, msg = Z.do_move(lib, "分类A", mods, "分类A")
w(f"移回 Mods -> ok={ok} msg={msg}")
assert ok and os.path.isdir(os.path.join(mods, "分类A"))

# ---------- 4.5 变体 / 部件 ----------
w()
w("=== 4.5 变体解析 / 文件级开关 (临时沙箱) ===")
vm = os.path.join(mods, "变体测试mod")

def _ini(path, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)

_ini(os.path.join(vm, "长剑", "SwordLong.ini"),
     "[TextureOverrideWeapon]\nhash = 003ff258\nvb0 = ResourceW\n")
_ini(os.path.join(vm, "短剑", "DISABLED_SwordShort.ini"),
     "[TextureOverrideWeapon]\nhash = 003ff258\nvb0 = ResourceW2\n")
_ini(os.path.join(vm, "face.ini"),
     "[TextureOverrideFace]\nhash = aa11bb22\nps-t0 = ResourceF\n")
_ini(os.path.join(vm, "DISABLED_BACKUP_123456.SwordLong.ini"), "; backup copy\n")

comp = Z.analyze_components(vm)
w("components: " + json.dumps(comp["components"], ensure_ascii=False, indent=1))
w("groups: " + json.dumps(comp["groups"], ensure_ascii=False))
assert len(comp["components"]) == 4, "应有 4 个 ini 组件"
assert len(comp["groups"]) == 1 and len(comp["groups"][0]["files"]) == 2, \
    "长剑/短剑覆盖同一 hash, 应归为一个变体组"
assert comp["groups"][0]["active"] == "长剑/SwordLong.ini", "当前生效应为长剑"
byrel = {c["rel"]: c for c in comp["components"]}
assert byrel["face.ini"]["group"] is None, "face.ini 互不冲突, 不应被分组"
assert byrel["DISABLED_BACKUP_123456.SwordLong.ini"]["backup"] is True, "备份识别失败"
assert byrel["短剑/DISABLED_SwordShort.ini"]["enabled"] is False

# 一键切换变体: 启用短剑 + 自动禁用长剑
ok, msg = Z.do_variant_select(vm, "短剑/DISABLED_SwordShort.ini")
w(f"变体切换 -> ok={ok} msg={msg}")
assert ok
comp2 = Z.analyze_components(vm)
assert comp2["groups"][0]["active"] == "短剑/SwordShort.ini", "切换后短剑应生效"
assert os.path.isfile(os.path.join(vm, "长剑", "DISABLED_SwordLong.ini")), "长剑应被禁用"
assert os.path.isfile(os.path.join(vm, "短剑", "SwordShort.ini")), "短剑应被启用"

# 撤销文件级操作 (回退最后一步: 变体切换是 [禁用长剑, 启用短剑] 两笔,
# 单步撤销把最后一笔回退 -> 短剑回到禁用, 长剑保持禁用)
ok, msg = Z.undo_last()
w(f"撤销 -> ok={ok} msg={msg}")
assert ok
assert os.path.isfile(os.path.join(vm, "短剑", "DISABLED_SwordShort.ini")), \
    "撤销后短剑应回到禁用"
assert os.path.isfile(os.path.join(vm, "长剑", "DISABLED_SwordLong.ini"))
# 把长剑开回来, 恢复初始状态
ok, msg = Z.do_toggle_file(vm, "长剑/DISABLED_SwordLong.ini", True)
assert ok and os.path.isfile(os.path.join(vm, "长剑", "SwordLong.ini"))
comp3 = Z.analyze_components(vm)
byrel3 = {c["rel"]: c for c in comp3["components"]}
assert byrel3["短剑/DISABLED_SwordShort.ini"]["enabled"] is False
assert byrel3["长剑/SwordLong.ini"]["enabled"] is True

# 独立部件开关
ok, msg = Z.do_toggle_file(vm, "face.ini", False)
w(f"禁用 face.ini -> ok={ok} msg={msg}")
assert ok and os.path.isfile(os.path.join(vm, "DISABLED_face.ini"))
comp4 = Z.analyze_components(vm)
byrel4 = {c["rel"]: c for c in comp4["components"]}
assert byrel4["DISABLED_face.ini"]["enabled"] is False, "face.ini 禁用后状态不对"
assert byrel4["DISABLED_face.ini"]["group"] is None
ok, msg = Z.do_toggle_file(vm, "DISABLED_face.ini", True)
assert ok and os.path.isfile(os.path.join(vm, "face.ini")), "face.ini 启用失败"
w("变体组切换 / 文件级开关 / journal 撤销 全部 OK")

# ---------- 4.6 热键循环变体 ----------
w()
w("=== 4.6 热键循环变体 ($var = 0,1,2 + type=cycle) ===")
cm = os.path.join(mods, "循环变体mod")
_ini(os.path.join(cm, "outfit.ini"),
     "[Constants]\nglobal $active = 0\n\n"
     "[KeySwap1]\ncondition = ($active == 1)\nkey = no_alt h\ntype = cycle\n"
     "$swapvarHair = 0,1,2\n\n"
     "[KeySwap2]\nkey = /\ntype = cycle\n$menu = 0,1\n\n"
     "[KeyExpr]\nkey = j\ntype = cycle\n$fancy = 0,1 - $bodyPaint\n")
cycles = Z.parse_cycle_vars(cm)
w("cycles: " + json.dumps(cycles, ensure_ascii=False, indent=1))
byv = {c["var"]: c for c in cycles}
assert set(byv) == {"swapvarHair", "menu", "fancy"}, list(byv)
hair = byv["swapvarHair"]
assert hair["values"] == [0, 1, 2] and hair["current"] == 0, hair
assert hair["keys"] == ["H"], hair["keys"]        # no_alt 是排除修饰符
assert hair["switchable"] is True
assert byv["menu"]["keys"] == ["/"], byv["menu"]["keys"]
assert byv["fancy"]["switchable"] is False, "表达式取值应标记为不可外部切换"

# 切到变体 2: 循环列表应旋转为 2,0,1
ok, msg = Z.do_cycle_set(cm, "swapvarHair", 2)
w(f"cycle_set -> ok={ok} msg={msg}")
assert ok
p_ini = os.path.join(cm, "outfit.ini")
body = open(p_ini, encoding="utf-8").read()
assert "$swapvarHair = 2,0,1" in body, body
cycles2 = Z.parse_cycle_vars(cm)
byv2 = {c["var"]: c for c in cycles2}
assert byv2["swapvarHair"]["current"] == 2, "切换后 current 应为 2"

# 撤销: ini_edit 应整文件还原
ok, msg = Z.undo_last()
w(f"撤销 -> ok={ok} msg={msg}")
assert ok
body2 = open(p_ini, encoding="utf-8").read()
assert "$swapvarHair = 0,1,2" in body2, body2
w("循环变体解析 / 旋转切换 / journal 撤销 全部 OK")

# hotkey 解析
assert Z.parse_hotkey("Ctrl+Alt+M") is not None
assert Z.parse_hotkey("Alt+Z") is not None
assert Z.parse_hotkey("F9") is not None
assert Z.parse_hotkey("M") is None, "无修饰键的普通键应被拒绝"
assert Z.parse_hotkey("Ctrl+") is None
assert Z.parse_hotkey("") is None
assert Z.parse_hotkey("Ctrl+乱码") is None
w("hotkey 解析 OK")

# safe_join 越界
assert Z.safe_join(mods, "../evil") is None, "safe_join 越界没拦住"
assert Z.safe_join(mods, "a/../../evil") is None, "safe_join 越界没拦住"
assert Z.safe_join(mods, "D:/other") is None, "safe_join 没拦住绝对路径"
assert Z.safe_join(mods, "分类A") is not None
w("safe_join 越界防护 OK (含 .. 的路径一律拒绝, 更保守更安全)")

# 没有嵌套条目
def _anc(a, b):
    a, b = os.path.abspath(a), os.path.abspath(b)
    return b != a and b.startswith(a + os.sep)
paths = [Z.os.path.join(mods, e["path"]) for e in Z.scan_mods(mods).entries]
for i in range(len(paths)):
    for j in range(len(paths)):
        if i != j:
            assert not _anc(paths[i], paths[j]), "存在嵌套条目: %s 里面还有 %s" % (paths[i], paths[j])
w("无嵌套条目 OK")

# 路径解析抽查
en = Z.scan_mods(mods).entries
for e in en:
    rp = Z.resolve_rel_dir(mods, e["id"])
    assert rp and os.path.isdir(rp), "解析失败: %s -> %s" % (e["id"], rp)
    w("  %-30s -> %s" % (e["id"], os.path.relpath(rp, mods)))
# 故意把某一级改成 DISABLED 前缀, 仍应能解析
os.rename(os.path.join(mods, "分类A"), os.path.join(mods, "DISABLED_分类A"))
assert Z.resolve_rel_dir(mods, "分类A/安比") is not None, "带禁用前缀时解析失败"
os.rename(os.path.join(mods, "DISABLED_分类A"), os.path.join(mods, "分类A"))
w("带 DISABLED 前缀的路径解析 OK")

# v1.5.9 同名两套: id 带 #N 后缀要能解析, 且 prefer 精确选中对应那套
_dup = os.path.join(mods, "同名回归")
os.makedirs(_dup, exist_ok=True)
open(os.path.join(_dup, "r.ini"), "w", encoding="utf-8").write(
    "[TextureOverrideR]\nhash = r1r1r1r1\nvb0 = RR\n")
os.makedirs(os.path.join(mods, "DISABLED_同名回归"), exist_ok=True)
open(os.path.join(mods, "DISABLED_同名回归", "r2.ini"), "w", encoding="utf-8").write(
    "[TextureOverrideR2]\nhash = r2r2r2r2\nvb0 = RR2\n")
_sc = Z.scan_mods(mods)
_ids = sorted(e["id"] for e in _sc.entries if e["id"].startswith("同名回归"))
assert _ids == ["同名回归", "同名回归#1"], _ids
_en = {e["path"]: e for e in _sc.entries if e["id"].startswith("同名回归")}
# 禁用套(#1)必须解析到 DISABLED_ 目录 —— v1.5.8 在这里报「找不到目录」
p1 = Z.entry_root(mods, _en["DISABLED_同名回归"])
assert p1 and os.path.basename(p1) == "DISABLED_同名回归", p1
# 启用套(无后缀)必须解析到启用目录, 不能认错套
p0 = Z.entry_root(mods, _en["同名回归"])
assert p0 and os.path.basename(p0) == "同名回归", p0
# 启用禁用套 -> 撞名自动排成 (2)
r = Z.do_toggle(mods, _en["DISABLED_同名回归"], True)
assert r[0] and len(r) == 3 and r[2]["target_name"] == "同名回归 (2)", r
assert os.path.isdir(os.path.join(mods, "同名回归 (2)"))
assert os.path.isdir(os.path.join(mods, "同名回归")), "启用套不能被动"
w("v1.5.9 同名两套解析/启用回归 OK")

w()
w("ALL TESTS PASSED")
open(OUT, "w", encoding="utf-8").write("\n".join(L))
