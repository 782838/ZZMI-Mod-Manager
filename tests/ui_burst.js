// v1.5.35 前端 jsdom 测试: 侧键/热键抓拍后, 挑帧页必须自己弹出来。
// 独立跑: NODE_PATH=<jsdom 所在目录> node tests/ui_burst.js
//
// 为什么要有这个: 用户真机反馈「点了鼠标侧键再回管家, 没跳到挑帧页」。
// 后端链是 hook -> burst.press() -> 前端哨兵轮询 /api/photo_ping -> burstForceShow()。
// 光看代码看不出毛病, 所以这里把整条前端链在 jsdom 里跑一遍, 用假 fetch 造出
// "后端刚多了一批帧"/"按了但没抓到"的时刻, 看 #mBurst 到底有没有拿到 .on。
//
// 覆盖: 侧键弹页 / 同批不重置档位 / 设置页开着 / 照片墙开着 / 空批 /
//       press_ok=false 弹空状态+原因 / 同一次 press 不重复弹 /
//       visibilitychange 立刻补哨兵 / 🧹清除缓存 / 🩺侧键自检
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const ROOT = path.dirname(__dirname);
const UI = fs.readFileSync(path.join(ROOT, 'ui.html'), 'utf8');

const PASS = [], FAIL = [];
function ck(name, cond, extra) {
  (cond ? PASS : FAIL).push(name);
  console.log((cond ? '  ok   ' : '  FAIL ') + name + (extra !== undefined ? ' | ' + extra : ''));
}
const sleep = ms => new Promise(r => setTimeout(r, ms));

const BOOT = { token: 'tok', version: '1.5.34' };

// ---- 造一份后端会吐的 meta: n 帧 + 5 层金字塔 ----
function makeMeta(id, n) {
  const frames = [];
  for (let i = 0; i < n; i++) frames.push({ i: i, t: (i * 0.08).toFixed(2) });
  const pick = k => {
    const a = [], step = Math.max(1, Math.floor(n / k));
    for (let i = 0; i < n; i += step) a.push(i);
    if (a[a.length - 1] !== n - 1) a.push(n - 1);
    return a;
  };
  return { burst_id: id, frames: frames, tiers: [pick(4), pick(8), pick(16), pick(32), frames.map(f => f.i)] };
}
const EMPTY = { burst_id: 0, frames: [], tiers: [] };

function baseState(over) {
  return Object.assign({
    ok: true, version: '1.5.34', theme: 'dark',
    stats: { total: 0, enabled: 0, disabled: 0, pinned: 0, chars: 0, categories: [] },
    categories: [], chars: [], entries: [], presets: [], libraries: [],
    mods_dir: 'C:/m', mods_dir_exists: true, configured: true,
    scan_seconds: 0.1, hotkey: 'F9', hotkey_ok: true, thumb_pending: 0,
    game_running: false, launcher_running: false, detect: { done: true, step: '' },
    photo_on: true, photo_hotkey: 'Ctrl+Shift+C', photo_mouse_btn: 1, photo_seconds: 3,
    photo_dir: 'C:/p', photo_dir_custom: false, photo_dir_default: 'C:/p',
    photo_burst: EMPTY,
  }, over || {});
}

// 可控的假后端
let stateExtra = {};
let ping = { ok: true, burst_id: 0, count: 0, meta: EMPTY, press_seq: 0, press_ok: true, press_msg: "" };
let pingCalls = 0;
let stateCalls = 0;
let diagCalls = 0;
let clearCalls = 0;
let closeCalls = 0;
let ackCalls = 0;
let burstsListCalls = 0;
let switchCalls = 0;
// v1.5.39: 模拟后端的 3 批缓存。burstsMeta 按 call 顺序返回不同长度的列表;
// switch 调用就把 active 切到对应 idx, 然后下一次 /api/photo_ping 的 meta
// 跟着切, 模拟前端切完再翻页能看到那一批。
let fakeBursts = [];        // [{id, count, secs, t, pending}]
let fakeActiveIdx = 0;      // 当前"后端认为"的活动批
function rebuildPing() {
  // 让后端下一次 /api/photo_ping 返回 fakeActiveIdx 那一批(重建 meta)
  const b = fakeBursts[fakeActiveIdx];
  if (b) {
    const meta = makeMeta(b.id, b.count);
    ping = { ok: true, burst_id: b.id, count: b.count, meta: meta };
  } else {
    ping = { ok: true, burst_id: 0, count: 0, meta: EMPTY };
  }
}

const dom = new JSDOM(UI.replace('__BOOT__', JSON.stringify(BOOT)), {
  runScripts: 'dangerously',
  pretendToBeVisual: true,
  url: 'http://127.0.0.1:1/',
  beforeParse(w) {
    w.fetch = (u, opt) => {
      const url = String(u);
      let payload = { ok: true };
      if (url.includes('/api/state')) {
        stateCalls++;
        payload = baseState(stateExtra);
      } else if (url.includes('/api/photo_ping')) {
        pingCalls++;
        payload = ping;
      } else if (url.includes('/api/photo_trigger')) {
        payload = { ok: true, count: 0, burst_id: 0, meta: EMPTY };
      } else if (url.includes('/api/photo_list')) {
        payload = { ok: true, photos: [], dir: 'C:/p' };
      } else if (url.includes('/api/photo_close')) {
        closeCalls++;
        payload = { ok: true };
      } else if (url.includes('/api/photo_clear')) {
        clearCalls++;
        ping = { ok: true, burst_id: 0, count: 0, meta: EMPTY,
                 press_seq: 0, press_ok: true, press_msg: "" };
        payload = { ok: true, cleared: 36, burst_id: 0, msg: '已清除连拍缓存(36 帧)' };
      } else if (url.includes('/api/photo_ack')) {
        ackCalls++;
        payload = { ok: true, acked: 1 };
      } else if (url.includes('/api/photo_diag')) {
        diagCalls++;
        payload = { ok: true, steps: [
          { k: '后台录屏', ok: true, v: '开', fix: 'x' },
          { k: '侧键监听', ok: false, v: '装不上', fix: '以管理员身份运行' },
        ] };
      } else if (url.includes('/api/photo_bursts')) {
        burstsListCalls++;
        payload = { ok: true, active: fakeActiveIdx, max: 3, bursts: fakeBursts };
      } else if (url.includes('/api/photo_switch')) {
        switchCalls++;
        // opt.body 可能是 JSON 字符串 {"idx":1} 或 form-encoded idx=1
        let _idx = 0;
        try {
          const b = (opt && opt.body) || '';
          if (b.startsWith('{')) {
            const o = JSON.parse(b);
            _idx = parseInt(o.idx || 0) || 0;
          } else if (b.includes('=')) {
            _idx = parseInt(b.split('=')[1]) || 0;
          } else {
            _idx = parseInt(b) || 0;
          }
        } catch (e) { _idx = 0; }
        fakeActiveIdx = Math.max(0, Math.min(fakeBursts.length - 1, _idx));
        rebuildPing();
        const b2 = fakeBursts[fakeActiveIdx];
        payload = { ok: true, active: fakeActiveIdx,
                    meta: b2 ? makeMeta(b2.id, b2.count) : EMPTY };
      }
      return Promise.resolve({
        ok: true, status: 200,
        json: () => Promise.resolve(payload),
        text: () => Promise.resolve(JSON.stringify(payload)),
      });
    };
    w.matchMedia = () => ({ matches: false, addListener() {}, removeListener() {},
                            addEventListener() {}, removeEventListener() {} });
    w.confirm = () => true;
    w.alert = () => {};
    w.open = () => null;
    w.requestAnimationFrame = cb => setTimeout(cb, 0);
  },
});

const w = dom.window, d = w.document;
const $ = s => d.querySelector(s);
const $$ = s => Array.prototype.slice.call(d.querySelectorAll(s));
const on = s => { const e = $(s); return !!(e && e.classList.contains('on')); };
const curTier = () => {
  const b = $('#pbTiers').querySelector('.on');
  return b ? +b.dataset.tier : -1;
};

(async () => {
  await sleep(200);   // 等 load() 跑完
  console.log('== v1.5.35 侧键抓拍自动弹挑帧页 (jsdom) ==');

  ck('页面加载完成(state 已拉到)', stateCalls > 0, 'stateCalls=' + stateCalls);
  ck('初始不在挑帧页', !on('#mBurst'));
  ck('函数 burstForceShow 已挂', typeof w.burstForceShow === 'function');
  ck('函数 burstPressShow 已挂', typeof w.burstPressShow === 'function');
  ck('函数 pbPingNow 已挂', typeof w.pbPingNow === 'function');

  // ---------- 场景 1: 侧键按下 -> 后端出现新 burst ----------
  const m1 = makeMeta(7, 36);
  ping = { ok: true, burst_id: 7, count: 36, meta: m1 };
  await sleep(900);   // 等 600ms 哨兵
  ck('侧键后自动弹出挑帧页', on('#mBurst'));
  ck('遮罩也一起打开', on('#mask'));
  ck('档位按钮渲染了 5 档', $('#pbTiers').children.length === 5,
     $('#pbTiers').children.length);
  ck('胶片条渲染了帧', $('#pbStrip').children.length > 0, $('#pbStrip').children.length);
  ck('标题栏显示帧数', ($('#pbHint').textContent || '').includes('36'),
     $('#pbHint').textContent);

  // ---------- 场景 2: 同一个 id 不该重复弹(免得把用户翻到的档位重置) ----------
  $$('#pbTiers button')[3].click();      // 用户切到第 4 档
  await sleep(50);
  ck('切档生效(前置条件)', curTier() === 3, 'tier=' + curTier());
  await sleep(900);
  ck('同一批不重复重置档位', curTier() === 3, 'tier=' + curTier());

  // ---------- 场景 3: 用户关掉后再来一批新的 -> 还得弹 ----------
  $('#pbClose').onclick && $('#pbClose').click();
  await sleep(100);
  ck('「弃掉关闭」后收起挑帧页', !on('#mBurst'));

  const m2 = makeMeta(8, 20);
  ping = { ok: true, burst_id: 8, count: 20, meta: m2 };
  await sleep(900);
  ck('新一批(id 变了)再次弹出', on('#mBurst'));

  // ---------- 场景 4: 管家正开着设置页时侧键 -> 要顶掉设置页 ----------
  $('#pbClose').onclick && $('#pbClose').click();
  await sleep(50);
  if (w.openSetup) w.openSetup();
  await sleep(50);
  ck('设置页已打开(前置条件)', on('#mSet'));
  const m3 = makeMeta(9, 12);
  ping = { ok: true, burst_id: 9, count: 12, meta: m3 };
  await sleep(900);
  ck('设置页开着也能弹出挑帧页', on('#mBurst'));
  ck('设置页被收掉了(不叠两层)', !on('#mSet'));

  // ---------- 场景 5: 照片墙开着时侧键 ----------
  $('#pbClose').onclick && $('#pbClose').click();
  await sleep(50);
  $('#btnWall').click();
  await sleep(150);
  ck('照片墙已打开(前置条件)', on('#mWall'));
  const m4 = makeMeta(10, 8);
  ping = { ok: true, burst_id: 10, count: 8, meta: m4, press_seq: 0, press_ok: true, press_msg: '' };
  await sleep(900);
  ck('照片墙开着也能弹出挑帧页', on('#mBurst'));
  ck('照片墙被收掉了', !on('#mWall'));

  // ---------- 场景 6: 空批(缓冲里没帧) -> 也要弹, 并说明原因 ----------
  $('#pbClose').onclick && $('#pbClose').click();
  await sleep(50);
  ping = { ok: true, burst_id: 11, count: 0, meta: { burst_id: 11, frames: [], tiers: [] },
           press_seq: 0, press_ok: true, press_msg: '' };
  await sleep(900);
  ck('空批也会弹(显示"没抓到帧"而不是静默)', on('#mBurst'));
  ck('空批显示原因', ($('#pbEmpty').textContent || '').length > 0, $('#pbEmpty').textContent);
  ck('空批时藏起「留这张」', $('#pbKeep').style.display === 'none');
  ck('空批时「清除缓存」还在', $('#pbClear').style.display !== 'none');

  // ---------- 场景 7 (v1.5.35): 侧键按了但没抓到帧 -> 弹空状态 + 后端给的原因 ----------
  $('#pbClose').onclick && $('#pbClose').click();
  await sleep(50);
  const WHY = '没检测到游戏在跑 —— 连拍只在游戏运行时录屏。';
  ping = { ok: true, burst_id: 0, count: 0, meta: EMPTY,
           press_seq: 1, press_ok: false, press_msg: WHY };
  await sleep(900);
  ck('press_ok=false 也会弹出挑帧页', on('#mBurst'));
  ck('press 失败时把后端原因原样显示', ($('#pbEmpty').textContent || '') === WHY,
     $('#pbEmpty').textContent);

  // ---------- 场景 8 (v1.5.35): 同一次 press 不重复弹 ----------
  $('#pbClose').onclick && $('#pbClose').click();
  await sleep(50);
  await sleep(900);   // 同一个 press_seq 反复轮询
  ck('同一个 press_seq 不重复弹', !on('#mBurst'));

  // ---------- 场景 9 (v1.5.35): visibilitychange 立刻补一次(不等 600ms 定时器) ----------
  const before = pingCalls;
  d.dispatchEvent(new w.Event('visibilitychange'));
  await sleep(60);
  ck('visibilitychange 立刻补一次哨兵', pingCalls > before, before + ' -> ' + pingCalls);

  // ---------- 场景 10 (v1.5.35): 🧹 清除缓存 ----------
  const m5 = makeMeta(12, 10);
  ping = { ok: true, burst_id: 12, count: 10, meta: m5, press_seq: 0, press_ok: true, press_msg: '' };
  await sleep(900);
  ck('又弹出一批(前置条件)', on('#mBurst'));
  const cBefore = clearCalls;
  $('#pbClear').click();
  await sleep(200);
  ck('清除缓存调到了 /api/photo_clear', clearCalls === cBefore + 1, clearCalls);
  ck('清除缓存后收起挑帧页', !on('#mBurst'));

  // ---------- 场景 11 (v1.5.35): 🩺 侧键自检 ----------
  const m6 = makeMeta(13, 6);
  ping = { ok: true, burst_id: 13, count: 6, meta: m6, press_seq: 0, press_ok: true, press_msg: '' };
  await sleep(900);
  ck('自检前先弹出一批(前置条件)', on('#mBurst'));
  const dBefore = diagCalls;
  $('#pbDiag').click();
  await sleep(200);
  ck('自检调到了 /api/photo_diag', diagCalls === dBefore + 1, diagCalls);
  ck('自检结果渲染出来了', $('#pbDiagBox').children.length > 0);
  ck('自检里带修法', ($('#pbDiagBox').textContent || '').includes('以管理员身份运行'),
     ($('#pbDiagBox').textContent || '').slice(0, 80));

  // ---------- 场景 12 (v1.5.36): 挑帧页**开着**时又来一批新的 -> 档位/提示/胶片条都要刷新 ----------
  // 用户报「第二次点侧键后仅上方刷新, 下方胶片条不变」。先把"前端到底刷不刷新"钉死:
  // 只要后端给的是**不同形状**的批次, 前端必须整块重画(档位文本 + 提示 + 胶片条)。
  // 如果这里过了, 而真机还是"下方不变", 那问题就不在前端 —— 而是后端两批帧**内容相同**
  // (管家在前台时缓冲被冻结, 见 zzmi_manager.py 的 _is_manager_foreground 分支)。
  $('#pbClose').onclick && $('#pbClose').click();
  await sleep(50);
  const mA = makeMeta(20, 36);
  ping = { ok: true, burst_id: 20, count: 36, meta: mA, press_seq: 0, press_ok: true, press_msg: '' };
  await sleep(900);
  ck('场景12 前置: 第一批已弹出', on('#mBurst'));
  const tierTxt = () => $$('#pbTiers button').map(b => b.textContent).join('|');
  const stripSig = () => $$('#pbStrip .pbs').map(e => e.dataset.i).join(',');
  const t1 = tierTxt(), s1 = stripSig(), h1 = $('#pbHint').textContent;
  // 挑帧页还开着, 直接来第二批(形状明显不同: 20 帧)
  const mB = makeMeta(21, 20);
  ping = { ok: true, burst_id: 21, count: 20, meta: mB, press_seq: 0, press_ok: true, press_msg: '' };
  await sleep(1200);
  ck('场景12 挑帧页仍开着(没被收掉)', on('#mBurst'));
  ck('场景12 提示刷新成新批的帧数', h1 !== $('#pbHint').textContent
     && ($('#pbHint').textContent || '').includes('20'), $('#pbHint').textContent);
  ck('场景12 档位文本刷新', t1 !== tierTxt(), tierTxt());
  ck('场景12 胶片条刷新(不是旧批的帧号)', s1 !== stripSig(), stripSig());
  ck('场景12 大图指向新批的帧', ($('#pbBig').getAttribute('src') || '').includes('i=19'),
     $('#pbBig').getAttribute('src'));

  // ---------- 场景 13 (v1.5.37): 页面首帧遇到 pending 批次 -> **必须弹出来** ----------
  // 用户报「在游戏里按侧键 -> 等几秒 -> 回管家 -> 没弹出截图界面」。
  // 真机路径: 切回管家时后端"没找到已有窗口"于是新开了一个窗口 = 全新页面加载,
  // 老写法在首帧无条件把 _pbShown 播种成当前 burst_id, 刚抓的那批被静默吞掉。
  // 现在靠 pending 标记: 没给用户看过的那批, 首帧不播种 + 主动补弹。
  $('#pbClose').onclick && $('#pbClose').click();
  await sleep(50);
  ck('场景13 前置: 挑帧页已收起', !on('#mBurst'));
  // 把哨兵清干净, 免得上一场景在途的响应干扰本场景
  ping = { ok: true, burst_id: 0, count: 0, meta: EMPTY,
           press_seq: 0, press_ok: true, press_msg: '' };
  stateExtra = {};
  await sleep(120);
  const m13 = makeMeta(33, 24);
  // 直接调页面里的播种函数(等价于"页面刚加载完拿到第一份 state")
  w.pbSeedFromState({
    photo_burst: Object.assign({ pending: true }, m13),
    photo_press_seq: 33, photo_press_ok: true, photo_press_pending: true,
  });
  await sleep(60);
  ck('场景13 pending 批次在首帧就弹出挑帧页', on('#mBurst'));
  ck('场景13 弹的是这批(pending=true)', ($('#pbHint').textContent || '').includes('24'),
     $('#pbHint').textContent);
  ck('场景13 弹完给后端 ack', ackCalls > 0, ackCalls);

  // 对照组: 同一批但 pending=false(用户已经看过) -> 首帧**不能**再弹一次
  $('#pbClose').onclick && $('#pbClose').click();
  await sleep(50);
  w.pbSeedFromState({
    photo_burst: Object.assign({ pending: false }, m13),
    photo_press_seq: 33, photo_press_ok: true, photo_press_pending: false,
  });
  await sleep(60);
  ck('场景13b pending=false 的首帧不重复弹(不打扰用户)', !on('#mBurst'));

  // ---------- 场景 14 (v1.5.37): 空批**只由 /api/state 轮询**发现 -> 也必须弹 ----------
  // 老写法在 state 轮询里先 `_pressSeen = np` 再调 burstPressShow, 于是里面
  // `seq === _pressSeen` 直接 return —— 提示被静默吞掉。这正是"按了没反应/没弹页"
  // 的另一条真实路径。这里让 ping 什么都不报, 只让 state 报, 逼出那条分支。
  $('#pbClose').onclick && $('#pbClose').click();
  await sleep(50);
  ping = { ok: true, burst_id: 0, count: 0, meta: EMPTY,
           press_seq: 0, press_ok: true, press_msg: '' };
  stateExtra = { photo_burst: EMPTY, photo_press_seq: 777, photo_press_ok: false,
                 photo_press_msg: '场景14 专用原因: 屏幕捕获被拦住了' };
  await sleep(2600);
  ck('场景14 state 轮询发现的空批也弹出挑帧页', on('#mBurst'));
  ck('场景14 显示后端给的原因',
     ($('#pbEmpty').textContent || '').includes('场景14 专用原因'),
     ($('#pbEmpty').textContent || '').slice(0, 60));
  stateExtra = {};

  // ---------- 场景 15 (v1.5.37): 录制中给一条提示(反馈, 不是额外动作) ----------
  $('#pbClose').onclick && $('#pbClose').click();
  await sleep(50);
  $('#toast').className = 'toast';
  stateExtra = { photo_burst: EMPTY, photo_press_seq: 0, photo_rec:
                 { recording: true, left: 2.4, seconds: 3, seq: 91 } };
  ping = { ok: true, burst_id: 0, count: 0, meta: EMPTY,
           press_seq: 0, press_ok: true, press_msg: '',
           recording: true, rec_left: 2.4, rec_seconds: 3, rec_seq: 91 };
  await sleep(900);
  ck('场景15 录制中给出提示', ($('#toast').className || '').includes('on')
     && ($('#toast').textContent || '').includes('正在录制'),
     $('#toast').textContent);
  ck('场景15 录制中不弹挑帧页(录完才弹)', !on('#mBurst'));
  // 同一个 rec_seq 不重复提示
  $('#toast').className = 'toast';
  await sleep(900);
  ck('场景15 同一段录制不重复提示', !($('#toast').className || '').includes('on'),
     $('#toast').className);
  // 录完 -> 正常弹出
  const m15 = makeMeta(40, 30);
  ping = { ok: true, burst_id: 40, count: 30, meta: m15,
           press_seq: 91, press_ok: true, press_msg: '', recording: false };
  await sleep(900);
  ck('场景15 录完之后正常弹出挑帧页', on('#mBurst'));

  // ---------- 场景 16 (v1.5.38): 页面被全屏游戏盖住(隐藏)时弹出的批次不算"已看",
  //   用户 alt-tab 回管家(可见)后才 ack 并补弹 —— 修复"回管家没弹挑帧页" ----------
  $('#pbClose').onclick && $('#pbClose').click();
  await sleep(100);
  ck('场景16 前置: 挑帧页已收起', !on('#mBurst'));
  // 模拟页面被游戏盖住: document.hidden = true / visibilityState = 'hidden'
  let hiddenFlag = true;
  try {
    Object.defineProperty(d, 'hidden', { configurable: true, get: () => hiddenFlag });
    Object.defineProperty(d, 'visibilityState', { configurable: true, get: () => (hiddenFlag ? 'hidden' : 'visible') });
  } catch (e) { /* 实例阴影兜底, 忽略 */ }
  const ackBefore16 = ackCalls;
  const m16 = makeMeta(60, 30);
  ping = { ok: true, burst_id: 60, count: 30, meta: m16 };
  await sleep(900);   // 隐藏期间哨兵仍会跑
  ck('场景16 隐藏时弹窗照样渲染(用户没看见)', on('#mBurst'));
  ck('场景16 隐藏时**不** ack(保留 pending 待补弹)', ackCalls === ackBefore16,
     'ackCalls ' + ackBefore16 + '->' + ackCalls);
  // 用户 alt-tab 回管家: 页面变可见 + 触发 visibilitychange -> pbPingNow 补弹
  hiddenFlag = false;
  d.dispatchEvent(new w.Event('visibilitychange'));
  await sleep(900);
  ck('场景16 回来后补弹仍在(可见时)', on('#mBurst'));
  ck('场景16 回来后才 ack(清 pending)', ackCalls > ackBefore16,
     'ackCalls ' + ackBefore16 + '->' + ackCalls);
  $('#pbClose').onclick && $('#pbClose').click();
  await sleep(100);

  // ---------- 场景 17 (v1.5.39): 3 批缓存 + 切换按钮 ----------
  // 后端已有 3 批: burst 70/71/72(72 最新 = active 0)。
  fakeBursts = [
    { id: 72, count: 50, secs: 3.0, t: Date.now()/1000,         pending: false },
    { id: 71, count: 40, secs: 3.0, t: Date.now()/1000 - 60,    pending: false },
    { id: 70, count: 60, secs: 3.0, t: Date.now()/1000 - 120,   pending: false },
  ];
  fakeActiveIdx = 0;
  rebuildPing();
  await sleep(900);   // 等 ping 把第 1 批弹出来
  ck('场景17 前置: 第 1 批(72)已弹出', on('#mBurst'));
  ck('场景17 📦1/📦2/📦3 三个按钮都在',
     $$('#pbBursts [data-bi]').length === 3);
  ck('场景17 当前活动批 📦1 高亮(on)',
     $('#pbBursts [data-bi="0"]').classList.contains('on'));
  ck('场景17 📦1 按钮文案含帧数',
     ($('#pbBursts [data-bi="0"]').textContent || '').includes('50'));
  // 点 📦2 -> 切到 burst 71
  $('#pbBursts [data-bi="1"]').click();
  await sleep(800);
  ck('场景17 点了 📦2 后调了 /api/photo_switch', switchCalls > 0, 'switchCalls=' + switchCalls);
  ck('场景17 切到 📦2 后画面帧数刷新成 40',
     ($('#pbHint').textContent || '').includes('40'),
     'hint=' + $('#pbHint').textContent);
  // 再次点 📦1 -> 切回
  $('#pbBursts [data-bi="0"]').click();
  await sleep(800);
  ck('场景17 切回 📦1 后帧数回到 50',
     ($('#pbHint').textContent || '').includes('50'),
     'hint=' + $('#pbHint').textContent);
  $('#pbClose').onclick && $('#pbClose').click();
  await sleep(100);

  console.log('');
  console.log('PASS ' + PASS.length + ' / FAIL ' + FAIL.length);
  if (FAIL.length) { console.log('FAILED: ' + FAIL.join(' | ')); process.exit(1); }
  process.exit(0);
})().catch(e => { console.error('harness 崩了:', e); process.exit(2); });
