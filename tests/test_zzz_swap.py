# v1.5.61 后端真实替换 e2e: 造沙箱游戏目录 + 两套源, 真跑互转
# 跑: python tests/test_zzz_swap.py
import os, sys, shutil, tempfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location("zm", os.path.join(ROOT, "zzmi_manager.py"))
zm = importlib.util.module_from_spec(spec)
sys.modules["zm"] = zm
spec.loader.exec_module(zm)

PASS, FAIL = [], []
def ck(name, cond, extra=""):
    (PASS if cond else FAIL).append(name)
    print(("  ok   " if cond else "  FAIL ") + name + ((" | " + str(extra)) if extra else ""))

work = tempfile.mkdtemp(prefix="zzzswap_")
try:
    game = os.path.join(work, "ZZ Game")
    data = os.path.join(game, "ZenlessZoneZero_Data", "il2cpp_data")
    os.makedirs(os.path.join(data, "Metadata"))
    os.makedirs(os.path.join(data, "Resources"))
    os.makedirs(os.path.join(data, "etc", "mono", "4.0"))

    def wf(p, content):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)

    # 游戏当前状态 = 国际服 ("I" 标记)
    wf(os.path.join(game, "GameAssembly.dll"), "GAMEASSEMBLY_INTERNATIONAL_YYYY")
    wf(os.path.join(game, "mhypbase.dll"), "MHY_INTERNATIONAL")
    wf(os.path.join(data, "Metadata", "global-metadata.dat"), "IL2CPP_META_INTL")
    wf(os.path.join(data, "Metadata", "startup-metadata.dat"), "STARTUP_INTL")
    wf(os.path.join(data, "Resources", "mscorlib.dll-resources.dat"), "MSCORLIB_INTL")
    wf(os.path.join(data, "etc", "mono", "4.0", "machine.config"), "MACHINE_INTL")

    # 源A: 国服原文件 (根下直接铺)
    cn = os.path.join(work, "国服原文件")
    wf(os.path.join(cn, "GameAssembly.dll"), "GAMEASSEMBLY_CHINA_XXXX")   # 长度不同 -> 指纹不同
    wf(os.path.join(cn, "mhypbase.dll"), "MHY_CHINA")
    wf(os.path.join(cn, "il2cpp_data", "Metadata", "global-metadata.dat"), "IL2CPP_META_CN")
    wf(os.path.join(cn, "il2cpp_data", "Metadata", "startup-metadata.dat"), "STARTUP_CN")
    wf(os.path.join(cn, "il2cpp_data", "Resources", "mscorlib.dll-resources.dat"), "MSCORLIB_CN")
    wf(os.path.join(cn, "il2cpp_data", "etc", "mono", "4.0", "machine.config"), "MACHINE_CN")

    # 源B: 国际服替换文件 (多套了一层 替换文件/)
    intl = os.path.join(work, "国际服替换文件3.2(1)")
    sub = os.path.join(intl, "替换文件")
    wf(os.path.join(sub, "GameAssembly.dll"), "GAMEASSEMBLY_INTERNATIONAL_YYYY")
    wf(os.path.join(sub, "mhypbase.dll"), "MHY_INTERNATIONAL")
    wf(os.path.join(sub, "il2cpp_data", "Metadata", "global-metadata.dat"), "IL2CPP_META_INTL")
    wf(os.path.join(sub, "il2cpp_data", "Metadata", "startup-metadata.dat"), "STARTUP_INTL")
    wf(os.path.join(sub, "il2cpp_data", "Resources", "mscorlib.dll-resources.dat"), "MSCORLIB_INTL")
    wf(os.path.join(sub, "il2cpp_data", "etc", "mono", "4.0", "machine.config"), "MACHINE_INTL")

    cfg = {
        "game_exe": os.path.join(game, "ZenlessZoneZero.exe"),
        "cn_files_dir": cn,
        "intl_files_dir": intl,
    }
    # game_exe 不存在也能推目录; 造一个空文件更真实
    wf(cfg["game_exe"], "fake")

    def r(p):
        with open(p, encoding="utf-8") as f:
            return f.read()

    G = game
    # ---- 1. 识别当前 = 国际服 (靠 GameAssembly.dll 大小) ----
    side, cur, cn_sz, intl_sz = zm._zzz_current_side(cfg)
    ck("识别当前为国际服", side == "intl", "%s cur=%s cn=%s intl=%s" % (side, cur, cn_sz, intl_sz))

    # ---- 2. auto -> 换成国服 ----
    ok, msg, new = zm.zzz_swap_run(cfg, "auto")
    ck("auto 互转成功", ok, msg)
    ck("auto 后方向为国服", new == "cn", new)
    ck("GameAssembly.dll 已换成国服", r(os.path.join(G, "GameAssembly.dll")) == "GAMEASSEMBLY_CHINA_XXXX",
       r(os.path.join(G, "GameAssembly.dll")))
    ck("mhypbase.dll 已换成国服", r(os.path.join(G, "mhypbase.dll")) == "MHY_CHINA")
    ck("global-metadata.dat 已换成国服",
       r(os.path.join(data, "Metadata", "global-metadata.dat")) == "IL2CPP_META_CN")
    ck("startup-metadata.dat 已换成国服",
       r(os.path.join(data, "Metadata", "startup-metadata.dat")) == "STARTUP_CN")
    ck("Resources/*.dat 已换成国服",
       r(os.path.join(data, "Resources", "mscorlib.dll-resources.dat")) == "MSCORLIB_CN")
    ck("machine.config 已换成国服",
       r(os.path.join(data, "etc", "mono", "4.0", "machine.config")) == "MACHINE_CN")

    # ---- 3. 再识别: 应为国服 ----
    side2, *_ = zm._zzz_current_side(cfg)
    ck("换成国服后识别正确", side2 == "cn", side2)

    # ---- 4. auto -> 换回国际服 (模拟"更新时要换回来") ----
    ok, msg, new = zm.zzz_swap_run(cfg, "auto")
    ck("再次 auto 成功换回", ok, msg)
    ck("换回后方向为国际服", new == "intl", new)
    ck("GameAssembly.dll 已换回国际服",
       r(os.path.join(G, "GameAssembly.dll")) == "GAMEASSEMBLY_INTERNATIONAL_YYYY")
    ck("global-metadata.dat 已换回国际服",
       r(os.path.join(data, "Metadata", "global-metadata.dat")) == "IL2CPP_META_INTL")
    ck("machine.config 已换回国际服",
       r(os.path.join(data, "etc", "mono", "4.0", "machine.config")) == "MACHINE_INTL")

    # ---- 5. 指定方向 ----
    ok, msg, new = zm.zzz_swap_run(cfg, "cn")
    ck("强制换成国服", ok and new == "cn", msg)
    ok, msg, new = zm.zzz_swap_run(cfg, "intl")
    ck("强制换成国际服", ok and new == "intl", msg)

    # ---- 6. 源目录选错 -> 明确报错 ----
    bad = dict(cfg); bad["cn_files_dir"] = os.path.join(work, "不存在")
    ok, msg, new = zm.zzz_swap_run(bad, "cn")
    ck("源目录不存在时失败并提示", (not ok) and "文件夹" in msg, msg)

    # ---- 7. 游戏目录缺失 -> 明确报错 ----
    bad2 = dict(cfg); bad2["game_exe"] = os.path.join(work, "nowhere", "ZZ.exe")
    ok, msg, new = zm.zzz_swap_run(bad2, "intl")
    ck("游戏目录缺失时失败并提示", (not ok) and "游戏目录" in msg, msg)

    # ---- 8. 源里没 dll -> 明确报错 ----
    empty = os.path.join(work, "空文件夹"); os.makedirs(empty)
    bad3 = dict(cfg); bad3["cn_files_dir"] = empty
    ok, msg, new = zm.zzz_swap_run(bad3, "cn")
    ck("源里没 GameAssembly.dll 时报错", (not ok) and "GameAssembly" in msg, msg)

    # ---- 9. 认不出的当前版本 + auto -> 提示手动 ----
    with open(os.path.join(G, "GameAssembly.dll"), "w") as f:
        f.write("SOME_OTHER_TOOL_MODIFIED_IT_LONGER")
    side3, *_ = zm._zzz_current_side(cfg)
    ck("被改过后识别为 unknown", side3 == "unknown", side3)
    ok, msg, new = zm.zzz_swap_run(cfg, "auto")
    ck("unknown + auto 时提示手动选", (not ok) and ("手动" in msg), msg)

finally:
    shutil.rmtree(work, ignore_errors=True)

print("\n==== 结果: %d 通过, %d 失败 ====" % (len(PASS), len(FAIL)))
if FAIL:
    print("失败项:", FAIL)
    sys.exit(1)