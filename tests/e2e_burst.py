# -*- coding: utf-8 -*-
"""v1.5.50 真机 e2e: 真实 App + 真实抓屏(ImageGrab 抓本机桌面) + 真实 HTTP。
验证用户报告的三个点:
  T1 按下->录 N 秒->封批 -> photo_ping 给出弹页条件(自动弹挑帧页的数据链路)
  T2 连拍 4 次 -> 只留最近 3 批, 最旧被挤掉(三批缓存/第四档清第一档)
  T3 帧经 /api/photoimg 真能取出 JPEG
  T4 /api/photo_switch 切批
  T5 录制线程被杀 -> press 先复活(看门狗) -> 照样录上
  T6 /api/photo_clear 清空
跑法: PYTHONIOENCODING=utf-8 <venv python> _e2e_burst.py > _e2e_out.txt 2>&1
"""
import os, sys, time, json, threading, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # tests/ 的上一级
os.environ["ZZMI_MANAGER_DATA"] = os.path.join(REPO, "_e2e_data")
os.environ["ZZMI_TEST_MODE"] = "1"
os.environ["ZZMI_NO_BROWSER"] = "1"
sys.path.insert(0, REPO)
import zzmi_manager as Z   # noqa: E402

OUT = []
def ck(name, cond, extra=""):
    OUT.append(("  ok   " if cond else "  FAIL ") + name + ((" | " + str(extra)) if extra else ""))
    print(OUT[-1], flush=True)
    return bool(cond)

app = Z.App()
app.burst.start()
app.cfg.update({"photo_on": True, "photo_seconds": 2.0,
                "photo_only_in_game": False, "photo_mouse_btn": 1})
port = Z.pick_port()
Z.Handler.app = app
httpd = Z.ThreadingHTTPServer(("127.0.0.1", port), Z.Handler)
httpd.daemon_threads = True
threading.Thread(target=httpd.serve_forever, daemon=True).start()
TOK = app.token
BASE = "http://127.0.0.1:%d" % port

def http(path):
    sep = "&" if "?" in path else "?"
    with urllib.request.urlopen(BASE + path + sep + "t=" + TOK, timeout=15) as r:
        return r.read()

def jget(path):
    return json.loads(http(path).decode("utf-8"))

def press_and_finish():
    """真·侧键入口 press() (钩子里调的就是它), 用本机真实桌面抓屏录 2 秒。"""
    r = app.burst.press("e2e")
    if not r.get("ok"):
        return None, r
    t0 = time.time()
    while time.time() - t0 < 25:
        if (not app.burst.recording()["recording"]) and app.burst.last_press:
            break
        time.sleep(0.15)
    time.sleep(0.3)
    return app.burst.last_press, r

# ---- T1 真实抓屏 + 弹页数据 ----
lp, pr = press_and_finish()
ck("T1 press 开始录制", bool(pr and pr.get("ok")), pr)
ck("T1 录满封批成功(真 ImageGrab 抓到帧)", bool(lp and lp.get("ok")), lp)
ping = jget("/api/photo_ping")
ck("T1 photo_ping 满足弹页条件(burst_id>0 & pending)",
   ping.get("burst_id", 0) > 0 and ping.get("press_pending") is True,
   "burst_id=%s count=%s pending=%s" % (ping.get("burst_id"), ping.get("count"), ping.get("press_pending")))
first_id = ping.get("burst_id")

# ---- T2 三批缓存: 共按 4 次, 只留最近 3 批 ----
ids = [first_id]
for k in range(3):
    lp2, _ = press_and_finish()
    if not (lp2 and lp2.get("ok")):
        ck("T2 第%d批封批" % (k + 2), False, lp2)
        break
    ids.append(jget("/api/photo_ping").get("burst_id"))
bl = (jget("/api/photo_bursts").get("bursts") or [])
ck("T2 第4批后仍只剩3批", len(bl) == 3, "缓存批=%s" % [b.get("id") for b in bl])
ck("T2 最旧的第1批被挤掉(第四档清第一档)",
   len(ids) == 4 and bl and bl[0].get("id") == ids[3],
   "按下序列=%s 活动批=%s" % (ids, [b.get("id") for b in bl]))

# ---- T3 真帧可取 ----
if bl:
    img = http("/api/photoimg?i=0&_b=%d" % bl[0]["id"])
    ck("T3 photoimg 返回真 JPEG", img[:2] == b"\xff\xd8" and len(img) > 5000,
       "bytes=%d" % len(img))

# ---- T4 切批 ----
if len(bl) >= 2:
    sw = jget("/api/photo_switch?idx=1")
    ck("T4 photo_switch 切到第2新批",
       sw.get("ok") and (sw.get("meta") or {}).get("burst_id") == ids[2],
       "active=%s meta.id=%s 期望=%s" % (sw.get("active"), (sw.get("meta") or {}).get("burst_id"), ids[2]))
    jget("/api/photo_switch?idx=0")

# ---- T5 看门狗: 杀线程 -> press 先复活 -> 照样录上 ----
b = app.burst
b._stop.set()
b.thread.join(5)
ck("T5 线程已被杀(前提)", (b.thread is None) or (not b.thread.is_alive()))
lp5, pr5 = press_and_finish()
ck("T5 press 自动复活并录满封批", bool(lp5 and lp5.get("ok")), pr5)
ck("T5 复活后线程活着", bool(b.thread and b.thread.is_alive()))
p5 = jget("/api/photo_ping")
ck("T5 新批进缓存(ping 可见)", p5.get("burst_id", 0) > 0 and p5.get("press_pending") is True,
   "burst_id=%s" % p5.get("burst_id"))

# ---- T6 清缓存 ----
data = json.dumps({}).encode("utf-8")
req = urllib.request.Request(BASE + "/api/photo_clear?t=" + TOK, data=data,
                             headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=15) as r:
    clr = json.loads(r.read().decode("utf-8"))
p6 = jget("/api/photo_ping")
ck("T6 photo_clear 清空(前端🧹同款端点)",
   clr.get("ok") and p6.get("burst_id", 0) == 0 and p6.get("press_seq", 0) == 0,
   "clear=%s ping.burst_id=%s" % (clr.get("ok"), p6.get("burst_id")))

# ---- T7 v1.5.51: 闸门拦截记录对前端可见 ----
app.burst.last_reject = {"msg": "测试: 绝区零不在最前面  ·  当前前台: explorer.exe", "t": time.time()}
p7 = jget("/api/photo_ping")
ck("T7 photo_ping 带回拦截原因(reject.msg/t)",
   (p7.get("reject") or {}).get("msg", "").startswith("测试:") and (p7.get("reject") or {}).get("t", 0) > 0,
   p7.get("reject"))
app.burst.press("e2e")   # 开录成功 -> last_reject 应被清掉
time.sleep(0.3)
p7b = jget("/api/photo_ping")
ck("T7 真正开录后过期拦截提示被清空", (p7b.get("reject") or {}).get("t", 0) == 0,
   p7b.get("reject"))

n_fail = sum(1 for l in OUT if l.startswith("  FAIL"))
print("E2E %s: %d 项, 失败 %d" % ("PASS" if n_fail == 0 else "FAIL", len(OUT), n_fail), flush=True)
os._exit(0 if n_fail == 0 else 1)
