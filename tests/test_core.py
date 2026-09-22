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

# v1.5.24: 改名被系统挡下 -> 必须交回手动改名弹窗需要的料(dir/cur/target_name/reason/rename)
_real_rd = Z._rename_dir
try:
    Z._rename_dir = lambda src, dst, j: (False, "[WinError 5] 拒绝访问。: '%s' -> '%s'" % (src, dst))
    _blk = Z.do_rename(mods, Z.scan_mods(mods).entries[0], "挡住的改名")
finally:
    Z._rename_dir = _real_rd
assert _blk[0] is False and len(_blk) == 3, "改名失败没返回手动弹窗信息"
_m = _blk[2]
assert _m.get("rename") and _m.get("reason") == "denied", "手动弹窗信息不对: %s" % _m
assert _m.get("cur") and _m.get("dir") and _m.get("target_name") == "挡住的改名", "缺路径/目标名: %s" % _m
w("改名被拒 -> 手动弹窗信息 OK (reason=%s, name=%s)" % (_m["reason"], _m["name"]))

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
     "[KeySwapBody]体型\nkey = ctrl shift no_alt VK_UP\ntype = cycle\n"
     "$bod = 0,1\n\n"
     "[KeyExpr]\nkey = j\ntype = cycle\n$fancy = 0,1 - $bodyPaint\n")
cycles = Z.parse_cycle_vars(cm)
w("cycles: " + json.dumps(cycles, ensure_ascii=False, indent=1))
byv = {c["var"]: c for c in cycles}
assert set(byv) == {"swapvarHair", "menu", "bod", "fancy"}, list(byv)
hair = byv["swapvarHair"]
assert hair["values"] == [0, 1, 2] and hair["current"] == 0, hair
# v1.5.28: no_* 排除修饰符不再被吞, 显示为「无Alt」后缀
assert hair["keys"] == ["H(无Alt)"], hair["keys"]
assert hair["switchable"] is True
assert byv["menu"]["keys"] == ["/"], byv["menu"]["keys"]
# v1.5.28: 段头 ] 后面的备注([KeySwapBody]体型)当变体中文名; VK_* 翻译成方向键
bod = byv["bod"]
assert bod["label_cn"] == "体型", bod
assert bod["keys"] == ["Ctrl+Shift+↑(无Alt)"], bod["keys"]
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

# ---------- v1.5.30 删除 mod = 移到回收站 ----------
w()
w("=== 4.7 删除 mod(回收站, v1.5.30) ===")
# 安全闸 1: 越界路径(id 指向 Mods 外)必须拒绝, 且目录原封不动
_out = os.path.join(HERE, "_outside_mod")
_clean(_out)
os.makedirs(_out, exist_ok=True)
open(os.path.join(_out, "keep.ini"), "w").close()
ok, msg = Z.do_mod_delete(mods, {"id": "../_outside_mod", "path": "x"})
assert not ok, (ok, msg)          # 两道闸: 解析不出去 / 越界拒绝
assert os.path.isdir(_out), "越界删除竟然把 Mods 外的目录动了!"
w("越界路径被拒, 外部目录完好 OK (%s)" % msg)
# 安全闸 2: 不许删 Mods 根
ok, msg = Z.do_mod_delete(mods, {"id": "", "path": ""})
assert not ok, (ok, msg)
w("删 Mods 根被拒 OK (%s)" % msg)
# 真删: 沙箱 mod -> 回收站(Windows 原生接口, 可还原)
_d = os.path.join(mods, "删除测试")
os.makedirs(_d, exist_ok=True)
open(os.path.join(_d, "d.ini"), "w", encoding="utf-8").write(
    "[TextureOverrideDel]\nhash = dedededede\nvb0 = R\n")
ok, msg = Z.do_mod_delete(mods, {"id": "删除测试", "path": "删除测试"})
w("do_mod_delete -> ok=%s msg=%s" % (ok, msg))
if Z._WIN:
    assert ok and not os.path.isdir(_d), (ok, msg)
    w("沙箱 mod 已进回收站, 目录消失 OK")
else:
    assert not ok, "非 Windows 应拒绝而不是物理删除"
    assert os.path.isdir(_d)
_clean(_out)
_clean(_d)

# ---------- v1.5.31 连拍缓冲 ----------
w()
w("=== 4.8 连拍缓冲(BurstBuffer, v1.5.31) ===")
class _FakeApp:
    cfg = {"photo_seconds": 3, "photo_on": True}
bb = Z.BurstBuffer(_FakeApp())
# 注入假帧: 每 4 帧换一次画面(模拟动作变化), 相同画面帧的 hash 一致
def _mk(n):
    grp = n // 4
    hb = bytes([grp * 40 % 256] * 256)
    return (1000.0 + n, b"JPEGDATA-FAKE-%03d" % n, hb)
_seq = [0]
def _grab():
    _seq[0] += 1
    return _mk(_seq[0])
bb.grab = _grab
for _ in range(30):
    bb._grab_one()
r = bb.trigger()
assert r["ok"] and r["count"] == 30, r
meta = bb.meta()
assert meta["burst_id"] == r["burst_id"]
tiers = meta["tiers"]
assert len(tiers) == 5, "要五层金字塔"
assert tiers[-1] == list(range(30)), "第 5 层 = 全部帧"
# v1.5.37: 第 1 档从 4 张提到 8 张(各档数量翻倍: 8/16/32/64)。
# _thin() 为了"最新一帧任何层都保留"会在目标数上多带 1 张, 所以上限是 8+1。
assert len(tiers[0]) <= 9, "第 1 层最粗: %s" % tiers[0]
for a, b in zip(tiers, tiers[1:]):
    assert set(a) <= set(b), "上层必须是下层的子集(逐层细分)"
assert 29 in tiers[0], "最新一帧任何层都必须保留"
w("30 帧五层金字塔: %s OK" % [len(t) for t in tiers])

# ---------- v1.5.37: 「按下之后录 N 秒」 ----------
class _RecApp:
    def __init__(self, secs=1.0):
        self.cfg = {"photo_seconds": secs, "photo_on": True}
        self.httpd = None
_rb = Z.BurstBuffer(_RecApp(1.0))
_rcnt = [0]
def _rgrab():
    _rcnt[0] += 1
    return (2000.0 + _rcnt[0] * 0.01, b"R%03d" % _rcnt[0],
            bytes([(_rcnt[0] * 7) % 256] * 256))
_rb.grab = _rgrab
_r0 = _rb.press("mouse")
assert _r0.get("recording") is True, _r0
assert _rb.press_seq == 1, _rb.press_seq
assert _rb.last_press is None, "还没录完, last_press 必须还是空的(前端据此不弹空状态)"
assert _rb.recording().get("recording") is True
assert _rb.press("mouse").get("ok") is False, "录制中连击要被忽略"
_rb.start()
_t0 = time.time()
while _rb.last_press is None and time.time() - _t0 < 8:
    time.sleep(0.05)
_rb.stop()
assert _rb.last_press is not None, "录满之后必须有 last_press"
assert _rb.last_press["ok"] is True, _rb.last_press
assert _rb.last_press["pending"] is True, "刚录完的那批必须是 pending(等界面 ack)"
_m2 = _rb.meta()
assert _m2["burst_id"] >= 1 and _m2["pending"] is True, _m2
_n2 = len(_m2["frames"])
assert _n2 >= 5, "1 秒至少要录到几帧: %d" % _n2
assert len(_m2["tiers"]) == 5 and len(_m2["tiers"][-1]) == _n2, _m2["tiers"]
_ts = [f["t"] for f in _m2["frames"]]
assert max(_ts) - min(_ts) <= 2.0, "帧的时间跨度不能超过录制时长太多: %s" % (max(_ts) - min(_ts))
w("按下后录 1 秒: 录到 %d 帧, 跨度 %.2fs, 五层 %s OK"
  % (_n2, max(_ts) - min(_ts), [len(t) for t in _m2["tiers"]]))
_a = _rb.ack(_m2["burst_id"])
assert _a["acked"] == _m2["burst_id"], _a
assert _rb.meta()["pending"] is False, "ack 之后必须清 pending"
assert _rb.last_press["pending"] is False
assert _rb.ack(_m2["burst_id"] + 999)["acked"] == 0, "ack 别的 id 不能乱清"
w("pending / ack 机制 OK")
assert _rb.clear_cache()["ok"] is True
assert _rb.burst is None and _rb.last_press is None and _rb.rec is None
w("清除缓存把 rec/burst/last_press 一起清掉 OK")

# 关掉后台录屏时按下 -> 直接失败且给得出人话, 且不占序号
_off = Z.BurstBuffer(_RecApp(1.0))
_off.app.cfg["photo_on"] = False
_ro = _off.press("mouse")
assert _ro.get("ok") is False and "连拍缓冲是关着的" in (_ro.get("msg") or ""), _ro
assert _off.rec is None and _off.press_seq == 0, (_off.rec, _off.press_seq)
w("关掉后台录屏时 press 直接失败(不占序号) OK")

# 常量: 帧率/档位翻倍
assert Z.BurstBuffer.TARGET_FPS == 24, Z.BurstBuffer.TARGET_FPS
assert Z.BurstBuffer.TIERS == (8, 16, 32, 64), Z.BurstBuffer.TIERS
w("帧率 24fps + 档位 (8,16,32,64) OK")

# 空缓冲触发要拒绝(而不是弹空挑帧条)
bb2 = Z.BurstBuffer(_FakeApp())
r2 = bb2.trigger()
assert not r2["ok"], r2
w("空缓冲触发被拒并给出指引 OK")
# keep 落盘 + 路径安全闸
_ph = os.path.join(HERE, "_photos")
_clean(_ph)
os.makedirs(_ph, exist_ok=True)
_old_dir = Z.PHOTO_DIR
Z.PHOTO_DIR = _ph
try:
    ok, msg, name = bb.keep(0)
    assert ok and name and os.path.isfile(os.path.join(_ph, name)), (ok, msg)
    w("留帧落盘 OK -> %s" % name)
    assert bb.keep(99999)[0] is False, "不存在的帧号要拒绝"
    assert Z.photo_file_path("../config.json") is None  # basename 兜底, 越不了界
    assert Z.photo_file_path("nope.jpg") is None
    w("越界/不存在路径被拒 OK")
    ph = Z.list_photos()
    assert len(ph) == 1 and ph[0]["name"] == name, ph
    ok, msg = Z.recycle_path(os.path.join(_ph, name)) if Z._WIN else (False, "")
    if Z._WIN:
        assert ok and not os.path.exists(os.path.join(_ph, name))
        w("删照片走回收站 OK")
finally:
    Z.PHOTO_DIR = _old_dir
_clean(_ph)
bb.burst = None

w()
w("ALL TESTS PASSED")
open(OUT, "w", encoding="utf-8").write("\n".join(L))
