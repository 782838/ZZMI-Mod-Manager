// T7f: 专测「拍完切回管家必弹挑帧页」(用户报的丢失功能B) 的真机场景。
//
// 用户描述的原场景: 游戏全屏盖住管家 -> 按侧键拍 -> alt-tab 切回管家 -> 必须弹。
// Chromium 会节流隐藏窗口的定时器(1 分钟), 所以靠 visibilitychange 补弹。
//
// 这里在 jsdom 里精确复刻:
//   ① 页面可见, 已看过批次1 (_pbShown=1, _pbMax=1)
//   ② 游戏盖住 -> document.hidden=true (jsdom 用 visibilityState 模拟)
//   ③ 后端产出批次2 (pending=true)
//   ④ 补一次 ping (隐藏时也会跑) -> burstForceShow 应该 pbShow 但**不** ack
//   ⑤ 切回来 (hidden=false) -> visibilitychange -> 补弹仍在 + 这时才 ack
//
// 顺带测另一个高危路径: 隐藏期间**没跑过任何 ping**(定时器被节流),
// 切回来第一次 ping 才看见批次2 —— 必须弹。
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

const BOOT = { token: 'tok', version: '1.5.52' };
function makeMeta(id, n) {
  const frames = [];
  for (let i = 0; i < n; i++) frames.push({ i: i, t: (i * 0.08).toFixed(2) });
  const pick = k => {
    const a = [], step = Math.max(1, Math.floor(n / k));
    for (let i = 0; i < n; i += step) a.push(i);
    if (a[a.length - 1] !== n - 1) a.push(n - 1);
    return a;
  };
  return { burst_id: id, frames, tiers: [pick(4), pick(8), pick(16), pick(32), frames.map(f => f.i)], pending: true };
}
const EMPTY = { burst_id: 0, frames: [], tiers: [], pending: false };
function baseState(over) {
  return Object.assign({
    ok: true, version: '1.5.52', theme: 'dark',
    stats: { total: 0, enabled: 0, disabled: 0, pinned: 0, chars: 0, categories: [] },
    categories: [], chars: [], entries: [], presets: [], libraries: [],
    mods_dir: 'C:/m', mods_dir_exists: true, configured: true,
    scan_seconds: 0.1, hotkey: 'F9', hotkey_ok: true, thumb_pending: 0,
    game_running: false, launcher_running: false, detect: { done: true, step: '' },
    photo_on: true, photo_hotkey: 'Ctrl+Shift+C', photo_mouse_btn: 1, photo_seconds: 3,
    photo_dir: 'C:/p', photo_dir_custom: false, photo_dir_default: 'C:/p',
    photo_burst: EMPTY, photo_press_seq: 0, photo_press_pending: false,
  }, over || {});
}

let curPing = { ok: true, burst_id: 0, meta: EMPTY, press_seq: 0, press_ok: true, press_msg: "", press_pending: false };
let ackCalls = [];
let pingCalls = 0;

const dom = new JSDOM(UI.replace('__BOOT__', JSON.stringify(BOOT)), {
  runScripts: 'dangerously', pretendToBeVisual: true, url: 'http://127.0.0.1:1/',
  beforeParse(w) {
    w.fetch = (u, opt) => {
      const url = String(u);
      let payload = { ok: true };
      if (url.includes('/api/state')) payload = baseState({ photo_burst: curPing.meta, photo_press_seq: curPing.press_seq, photo_press_pending: curPing.press_pending });
      else if (url.includes('/api/photo_ping')) { pingCalls++; payload = curPing; }
      else if (url.includes('/api/photo_ack')) { let id = 0; try { id = JSON.parse((opt && opt.body) || '{}').burst_id || 0; } catch (e) {} ackCalls.push(id); payload = { ok: true, acked: id }; }
      else if (url.includes('/api/photo_bursts')) payload = { ok: true, active: 0, max: 3, bursts: curPing.meta && curPing.meta.burst_id ? [{ id: curPing.meta.burst_id, count: (curPing.meta.frames || []).length, secs: 3, fps: 10, t: 0, pending: true }] : [] };
      else if (url.includes('/api/photo_list')) payload = { ok: true, photos: [], dir: 'C:/p' };
      else if (url.includes('/api/photo_diag')) payload = { ok: true, steps: [] };
      return Promise.resolve({ ok: true, json: () => Promise.resolve(payload), text: () => Promise.resolve(JSON.stringify(payload)) });
    };
    // 可控的可见性
    let _hidden = false;
    Object.defineProperty(w.document, 'hidden', { get: () => _hidden, configurable: true });
    Object.defineProperty(w.document, 'visibilityState', { get: () => (_hidden ? 'hidden' : 'visible'), configurable: true });
    w.__setHidden = v => { _hidden = v; };
  },
});

const w = dom.window, d = w.document;
const on = sel => { const e = d.querySelector(sel); return !!(e && e.classList.contains('on')); };
const clickX = () => { const b = d.querySelector('#pbX'); if (b) b.click(); };

(async () => {
  await sleep(400);
  const setPing = (id, n) => { curPing = { ok: true, burst_id: id, count: n, meta: makeMeta(id, n), press_seq: id, press_ok: true, press_msg: "", press_pending: true }; };

  console.log('=== 场景A: 已看过批次1, 游戏盖住时拍下批次2, 切回必须弹 ===');
  setPing(1, 40);
  w.pbPingNow(); await sleep(120);
  ck('A1 批次1 已弹出', on('#mBurst'));
  ck('A2 批次1 已 ack', ackCalls.includes(1), 'ackCalls=' + JSON.stringify(ackCalls));
  // 关掉(用户看完关掉)
  clickX(); await sleep(60);
  ck('A3 关掉后挑帧页收起', !on('#mBurst'));

  // 游戏盖住
  w.__setHidden(true);
  ck('A4 现在文档隐藏', d.hidden === true);
  // 后端产出批次2
  setPing(2, 35);
  w.pbPingNow(); await sleep(120);
  ck('A5 隐藏时也渲染了挑帧页(用户没看见)', on('#mBurst'));
  ck('A6 隐藏时**不** ack(保留 pending)', !ackCalls.includes(2), 'ackCalls=' + JSON.stringify(ackCalls));

  // 切回来
  w.__setHidden(false);
  ck('A7 切回后文档可见', d.hidden === false);
  d.dispatchEvent(new w.Event('visibilitychange'));
  await sleep(150);
  ck('A8 切回后挑帧页仍在(补弹可见)', on('#mBurst'));
  ck('A9 切回后才 ack 批次2', ackCalls.includes(2), 'ackCalls=' + JSON.stringify(ackCalls));

  console.log();
  console.log('=== 场景B: 隐藏期间定时器被节流(一次 ping 都没跑), 切回首次 ping 必须弹 ===');
  clickX(); await sleep(60);
  w.__setHidden(true);
  setPing(3, 30);
  await sleep(80);                        // 隐藏期间不主动 ping(模拟节流)
  ck('B1 隐藏+未 ping -> 挑帧页未弹', !on('#mBurst'));
  w.__setHidden(false);
  d.dispatchEvent(new w.Event('visibilitychange'));
  await sleep(150);
  ck('B2 切回首次 ping -> 弹出批次3', on('#mBurst'));

  console.log();
  console.log('=== 场景C: 连拍多批, 每次切回都要弹最新那批(不能只弹一次) ===');
  clickX(); await sleep(60);
  ackCalls = [];
  for (let id = 4; id <= 6; id++) {
    setPing(id, 20 + id);
    w.pbPingNow(); await sleep(120);
    const okPop = on('#mBurst');
    const hint = (d.querySelector('#pbHint') || {}).textContent || '';
    ck('C' + id + ' 批次' + id + ' 弹出', okPop, hint.slice(0, 40));
    clickX(); await sleep(60);
  }
  ck('C7 三批各自 ack 过', [4,5,6].every(i => ackCalls.includes(i)), 'ack=' + JSON.stringify(ackCalls));

  console.log();
  console.log('PASS ' + PASS.length + ' / FAIL ' + FAIL.length);
  if (FAIL.length) { console.log('FAILED:'); FAIL.forEach(f => console.log('  - ' + f)); process.exit(1); }
})();
