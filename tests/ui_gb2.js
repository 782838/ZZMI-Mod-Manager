// v1.5.13 前端 jsdom 测试: 角色下拉 / 文件勾选 / 选择性下载 / 已下载标记
// 独立跑: node tests/ui_gb2.js
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const ROOT = path.dirname(__dirname);
const UI = fs.readFileSync(path.join(ROOT, 'ui.html'), 'utf8');

const FAIL = [], PASS = [];
function ck(name, cond, extra) {
  (cond ? PASS : FAIL).push(name);
  console.log((cond ? '  ok   ' : '  FAIL ') + name + (extra !== undefined ? ' | ' + extra : ''));
}
const arr = nl => Array.prototype.slice.call(nl);

const BOOT = { token: 'tok', version: '1.5.13' };

const CRAWL = {
  ok: true, kind: 'category', gid: '30336', page: 1, perpage: 30, total: 130,
  items: [
    { id: 111, name: 'Mod One', url: 'https://gamebanana.com/mods/111',
      author: 'a', likes: 3, views: 9, has_files: true,
      preview: 'https://images.gamebanana.com/x1.jpg', previews: [] },
    { id: 222, name: 'Mod Two', url: 'https://gamebanana.com/mods/222',
      author: 'b', likes: 1, views: 5, has_files: true,
      preview: '', previews: [] },
  ],
};
const SUBS = { ok: true, char_cat: 30305, items: [
  { id: 30336, name: 'Anby Demara', cn: '安比·德玛拉', count: 130, url: 'u', icon: '' },
  { id: 30579, name: 'Hoshimi Miyabi', cn: '星见雅', count: 243, url: 'u', icon: '' },
  { id: 99999, name: 'Nobody Known', cn: '', count: 7, url: 'u', icon: '' },
]};
// 历史: two_a.zip 下过
const HISTORY = { ok: true, map: { '222:two_a.zip': { ts: 1, path: 'p' } } };
const FILES = { ok: true, history: HISTORY.map, map: {
  '111': { name: 'Mod One', files: [
    { name: 'one.zip', size: 1024, url: 'u', md5: '', av: 'clean' }] },
  '222': { name: 'Mod Two', files: [
    { name: 'two_a.zip', size: 2048, url: 'u', md5: '', av: 'clean' },
    { name: 'two_b.rar', size: 4096, url: 'u', md5: '', av: 'caution' }] },
}};

let dlPosted = null;
let histCleared = false;

const dom = new JSDOM(UI.replace('__BOOT__', JSON.stringify(BOOT)), {
  runScripts: 'dangerously',
  pretendToBeVisual: true,
  url: 'http://127.0.0.1:1/',
  beforeParse(w) {
    w.fetch = (u, opt) => {
      const url = String(u);
      const body = opt && opt.body ? JSON.parse(opt.body) : null;
      let payload = { ok: true };
      if (url.includes('/api/state')) {
        payload = { stats: { total: 0, chars: 0, categories: [] }, entries: [],
                    theme: 'dark', mods_dir: '', hotkey: 'F9', downloads_dir: 'C:/dl',
                    categories: [], chars: [] };
      } else if (url.includes('/api/gb_subs')) { payload = SUBS; }
      else if (url.includes('/api/gb_crawl')) { payload = CRAWL; }
      else if (url.includes('/api/gb_files')) { payload = FILES; }
      else if (url.includes('/api/gb_history')) { payload = HISTORY; }
      else if (url.includes('/api/gb_downloads')) {
        payload = { dir: 'C:/dl', items: [
          { name: 'a.zip', size: 1024, size_h: '1.0 KB', mtime: 1 }] };
      }
      else if (url.includes('/api/gb_hist_clear')) { histCleared = true; payload = { ok: true }; }
      else if (url.includes('/api/gb_dl')) { payload = { ok: true, job: null }; }
      else if (url.includes('/api/gb_download')) { dlPosted = body; payload = { ok: true, job: 'gb1' }; }
      else if (url.includes('/api/gb_translate')) { payload = { ok: true, map: {} }; }
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
const $$ = s => arr(d.querySelectorAll(s));
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  await sleep(120);
  console.log('== v1.5.13 前端 jsdom ==');

  ck('有角色下拉 #gbSub', !!$('#gbSub'));
  ck('有刷新按钮 #gbSubReload', !!$('#gbSubReload'));
  ck('有列出文件开关 #gbFilesTog', !!$('#gbFilesTog'));
  ck('有选择文件夹按钮 #gbDlPick', !!$('#gbDlPick'));
  ck('有清空记录按钮 #gbDlClearHist', !!$('#gbDlClearHist'));
  ck('有下载目录统计 #gbDlStat', !!$('#gbDlStat'));
  ck('函数 gbLoadSubs 已挂', typeof w.gbLoadSubs === 'function');
  ck('函数 gbPickSub 已挂', typeof w.gbPickSub === 'function');
  ck('函数 gbPicks 已挂', typeof w.gbPicks === 'function');
  ck('函数 gbLoadFiles 已挂', typeof w.gbLoadFiles === 'function');
  ck('函数 gbApplyHist 已挂', typeof w.gbApplyHist === 'function');

  await w.gbLoadSubs();
  await sleep(30);
  const opts = $$('#gbSub option');
  ck('角色下拉有 全部+3 项', opts.length === 4, opts.length);
  ck('角色名带数量', opts[1].textContent.includes('Anby Demara') && opts[1].textContent.includes('130'),
     opts[1].textContent);
  // v1.5.14: 中文名显示在最前
  ck('角色名带中文译名', opts[1].textContent.includes('安比·德玛拉'), opts[1].textContent);
  ck('中文名排在英文前', opts[1].textContent.indexOf('安比') < opts[1].textContent.indexOf('Anby'),
     opts[1].textContent);
  ck('中文名带分隔符', opts[1].textContent.includes('·'), opts[1].textContent);
  ck('无中文时回落英文', !opts[3].textContent.includes('·') && opts[3].textContent.includes('Nobody Known'),
     opts[3].textContent);
  ck('角色 value = 分类 id', opts[1].value === '30336', opts[1].value);
  ck('角色提示文案', ($('#gbSubInfo').textContent || '').includes('3 个角色'), $('#gbSubInfo').textContent);

  // 选角色 -> 重爬
  $('#gbUrl').value = '';
  $('#gbSub').value = '30336';
  $('#gbSub').dispatchEvent(new w.Event('change'));
  await sleep(80);
  ck('选角色后卡片渲染出来', $$('#gbGrid .gbcard').length === 2, $$('#gbGrid .gbcard').length);
  ck('提示了角色分类', ($('#gbFoot').textContent || '').includes('30336'), $('#gbFoot').textContent);

  await sleep(90);
  ck('两个 mod 都有文件区', $$('#gbGrid .gbfiles[data-fbox]').length === 2,
     $$('#gbGrid .gbfiles[data-fbox]').length);
  const mod1 = $('[data-fbox="111"]');
  const mod2 = $('[data-fbox="222"]');
  ck('mod111 列了 1 个文件', arr(mod1.querySelectorAll('input[data-fpick]')).length === 1);
  ck('mod222 列了 2 个文件', arr(mod2.querySelectorAll('input[data-fpick]')).length === 2);
  ck('文件名显示出来', arr(mod2.querySelectorAll('input'))[0].value === 'two_a.zip',
     arr(mod2.querySelectorAll('input'))[0].value);
  ck('文件默认勾选', arr(d.querySelectorAll('#gbGrid input[data-fpick]')).every(c => c.checked));
  ck('有 全选/全不选', !!mod2.querySelector('[data-none]'));
  ck('杀毒结果有徽章', mod2.querySelector('.av') !== null,
     mod2.querySelector('.av') && mod2.querySelector('.av').textContent);
  ck('caution 显示成 bad', mod2.querySelector('.av.bad') !== null);

  // 已下载标记: two_a.zip 在历史里
  const labels = arr(mod2.querySelectorAll('label.gbfile'));
  const la = labels.find(l => l.querySelector('input').value === 'two_a.zip');
  const lb = labels.find(l => l.querySelector('input').value === 'two_b.rar');
  ck('下过的文件标「已下载」', !!la.querySelector('.gbreg'),
     la.querySelector('.gbreg') && la.querySelector('.gbreg').textContent);
  ck('没下过的文件不标', !lb.querySelector('.gbreg'));

  // 全选/全不选
  mod2.querySelector('[data-none]').dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
  await sleep(20);
  ck('全不选生效', arr(mod2.querySelectorAll('input[data-fpick]')).every(c => !c.checked));
  mod2.querySelector('[data-all]').dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
  await sleep(20);
  ck('全选生效', arr(mod2.querySelectorAll('input[data-fpick]')).every(c => c.checked));

  // gbPicks
  ck('全勾时 gbPicks 返回 null', w.gbPicks('222') === null, w.gbPicks('222'));
  arr(mod2.querySelectorAll('input[data-fpick]'))[0].checked = false;
  const picks = w.gbPicks('222');
  ck('部分勾选返回选中列表', Array.isArray(picks) && picks.length === 1 && picks[0] === 'two_b.rar',
     JSON.stringify(picks));

  // 下载带 picks
  dlPosted = null;
  const btn = d.querySelector('[data-dl="222"]');
  btn.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
  await sleep(90);
  ck('下载请求带 picks', dlPosted && Array.isArray(dlPosted.picks)
     && dlPosted.picks[0] === 'two_b.rar', JSON.stringify(dlPosted));
  ck('下载请求带 mod_id', dlPosted && String(dlPosted.mod_id) === '222', dlPosted && dlPosted.mod_id);

  // 一个都没勾 -> 拒绝
  mod2.querySelector('[data-none]').dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
  const btn2 = d.querySelector('[data-dl="222"]');
  btn2.disabled = false; dlPosted = null;
  if ($('#toast')) $('#toast').textContent = '';
  btn2.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
  await sleep(60);
  ck('一个都没勾时不下单', dlPosted === null, dlPosted);
  ck('一个都没勾时提示了', (($('#toast') || {}).textContent || '').includes('至少勾一个'),
     ($('#toast') || {}).textContent);

  // 全下时不传 picks
  dlPosted = null;
  const btn3 = d.querySelector('[data-dl="111"]');
  btn3.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
  await sleep(80);
  ck('全勾时 picks 为 null(走全量)',
     dlPosted && (dlPosted.picks === null || dlPosted.picks === undefined),
     dlPosted && JSON.stringify(dlPosted.picks));

  // 下载目录弹窗 —— 先走正常的按钮打开路径
  $('#gbDlDir').dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
  await sleep(120);
  ck('下载目录弹窗打开了', $('#mGBdl').classList.contains('on'),
     $('#mGBdl').className);
  ck('下载目录显示位置', ($('#gbDlStat').textContent || '').includes('C:/dl'), $('#gbDlStat').textContent);
  ck('下载目录显示文件数', ($('#gbDlStat').textContent || '').includes('1 个文件'),
     $('#gbDlStat').textContent);
  ck('下载目录列出了文件', ($('#gbDlList').textContent || '').includes('a.zip'),
     $('#gbDlList').textContent);
  ck('下载路径回填到输入框', $('#gbDlPath').value === 'C:/dl', $('#gbDlPath').value);

  // 清空记录 (gbConfirm 走应用内 ask 弹窗, 这里直接桩掉它)
  w.ask = () => Promise.resolve('ok');
  histCleared = false;
  $('#gbDlClearHist').dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
  await sleep(120);
  ck('清空记录会调后端', histCleared);
  ck('清空后已下载标记消失',
     !d.querySelector('#gbGrid label.gbfile .gbreg'),
     d.querySelector('#gbGrid label.gbfile .gbreg'));

  console.log('');
  console.log('PASS ' + PASS.length + ' / FAIL ' + FAIL.length);
  if (FAIL.length) { console.log('FAILED: ' + JSON.stringify(FAIL)); process.exit(1); }
  process.exit(0);
})().catch(e => {
  console.log('EXCEPTION: ' + (e && e.stack || e));
  process.exit(2);
});
