// v1.5.61 前端 jsdom 测试: 脚本启动弹窗 + 国服国际服文件互转
// 独立跑: NODE_PATH=... node tests/ui_zs.js
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

const BOOT = { token: 'tok', version: '1.5.61' };

// ---- 假后端状态 ----
let STATUS = {
  ok: true, side: 'intl', side_name: '国际服',
  cur_size: 533617456, cn_size: 533644064, intl_size: 533617456,
  tool_dir: 'F:\\11aa快捷方式\\zzz_0.6.3(3)',
  cn_dir: 'F:\\11aa快捷方式\\外挂前置\\国服原文件',
  intl_dir: 'F:\\11aa快捷方式\\外挂前置\\国际服替换文件3.2(1)',
  game_root: 'F:\\miHoYo Launcher\\games\\ZenlessZoneZero Game',
  has_cn: true, has_intl: true,
};
const calls = [];       // 记录所有请求: {url, body}
let swapResult = { ok: true, msg: '已替换 7 个文件。现在装的是【国服】', side: 'cn' };

const dom = new JSDOM(UI.replace('__BOOT__', JSON.stringify(BOOT)), {
  runScripts: 'dangerously',
  pretendToBeVisual: true,
  url: 'http://127.0.0.1:1/',
  beforeParse(w) {
    w.fetch = (u, opt) => {
      const url = String(u);
      const body = opt && opt.body ? JSON.parse(opt.body) : null;
      calls.push({ url, body });
      let payload = { ok: true };
      if (url.includes('/api/state')) {
        payload = { stats: { total: 0, chars: 0, categories: [] }, entries: [],
                    theme: 'dark', mods_dir: '', hotkey: 'F9', downloads_dir: 'C:/dl',
                    categories: [], chars: [], game_exe: STATUS.game_root + '\\ZenlessZoneZero.exe' };
      } else if (url.includes('/api/zzz_autodetect')) {
        payload = { ok: true, skipped: false, elapsed: 0.42,
                    tool: 'F:\\11aa快捷方式\\zzz_0.6.3(3)',
                    cn: 'F:\\11aa快捷方式\\外挂前置\\国服原文件',
                    intl: 'F:\\11aa快捷方式\\外挂前置\\国际服替换文件3.2(1)',
                    changed: ['注入器', '国服原文件', '国际服替换'] };
      } else if (url.includes('/api/zzz_swap_status')) {
        payload = STATUS;
      } else if (url.includes('/api/zzz_swap_pick')) {
        payload = { ok: true, path: 'X:\\picked', msg: '已记住「国服原文件」: X:\\picked' };
      } else if (url.includes('/api/zzz_tool_pick')) {
        payload = { ok: true, path: 'F:\\tool', msg: '已记住注入器文件夹: F:\\tool' };
      } else if (url.includes('/api/zzz_swap')) {
        payload = swapResult;
      } else if (url.includes('/api/zzz_tool')) {
        payload = { ok: true, msg: '① 脚本 已启动；② 说明 已打开；③ 游戏 已请求启动' };
      }
      return Promise.resolve({
        ok: true, status: 200, json: () => Promise.resolve(payload),
      });
    };
  },
});

const w = dom.window, d = w.document;
const $ = s => d.querySelector(s);
setTimeout(() => {
  // ---- 1. 面板默认隐藏 ----
  ck('面板默认隐藏', !$('#mZS').classList.contains('on'));
  ck('遮罩默认隐藏', !$('#zsMask').classList.contains('on'));

  // ---- 2. 点「脚本启动」→ 打开面板 ----
  $('#btnZZZTool').click();
  ck('点按钮后面板打开', $('#mZS').classList.contains('on'));
  ck('点按钮后遮罩打开', $('#zsMask').classList.contains('on'));
  ck('打开时自动触发了扫描',
     calls.some(c => c.url.includes('/api/zzz_autodetect')));
  ck('自动扫描不是 force',
     (calls.find(c => c.url.includes('/api/zzz_autodetect')) || {}).body
       && calls.find(c => c.url.includes('/api/zzz_autodetect')).body.force === false);

  setTimeout(() => {
    // ---- 2a. 扫描完成后才去读状态(顺序: 先扫描校准, 再刷新显示) ----
    ck('扫描后请求了 swap_status',
       calls.some(c => c.url.includes('/api/zzz_swap_status')));
    // ---- 2b. 扫描条状态 ----
    ck('扫描条显示已找到 3 个', /已自动找到全部 3 个文件夹/.test($('#zsScanMsg').textContent),
       $('#zsScanMsg').textContent);
    ck('扫描条带 done 样式', ($('#zsScanBar').className || '').includes('done'),
       $('#zsScanBar').className);
    // ---- 2c. 重新扫描按钮 ----
    (function(){
      const b = calls.length;
      $('#zsRescan').click();
      setTimeout(() => {
        const f = calls.slice(b).find(c => c.url.includes('/api/zzz_autodetect'));
        ck('点「重新扫描」发 force=true', !!(f && f.body && f.body.force === true),
           JSON.stringify(f && f.body));
      }, 100);
    })();
    // ---- 3. 状态正确渲染 ----
    const side = $('#zsSide');
    ck('侧栏显示「当前装的是：国际服」', /当前装的是：国际服/.test(side.textContent),
       side.textContent.trim().slice(0, 40));
    ck('侧栏带 ok-intl 样式类', side.className.includes('ok-intl'), side.className);
    ck('提示更新前先换回国服', /要更新游戏请点/.test(side.textContent), side.textContent.trim().slice(0, 60));
    ck('国服路径框已回填', ($('#zsCnDir').value || '').includes('国服原文件'),
       $('#zsCnDir').value);
    ck('国际服路径框已回填', ($('#zsIntlDir').value || '').includes('国际服替换文件'),
       $('#zsIntlDir').value);
    ck('注入器路径框已回填', ($('#zsToolDir').value || '').includes('zzz_0.6.3'),
       $('#zsToolDir').value);
    ck('两套都到位 → 底部无警告', ($('#zsFoot').textContent || '').trim() === '',
       $('#zsFoot').textContent);

    // ---- 4. 一键互转 ----
    const before = calls.length;
    // 后端执行前先把状态改好, 这样 zsRefresh 拿到的是"替换后"的状态
    STATUS.side = 'cn'; STATUS.side_name = '国服';
    $('#zsSwap').click();
    setTimeout(() => {
      const swapCalls = calls.slice(before)
        .filter(c => c.url.includes('/api/zzz_swap?'));
      ck('一键互转发出了 POST', swapCalls.length === 1, JSON.stringify(swapCalls));
      ck('一键互转 side=auto', swapCalls[0] && swapCalls[0].body && swapCalls[0].body.side === 'auto',
         JSON.stringify(swapCalls[0] && swapCalls[0].body));
      ck('互转后刷新了 status',
         calls.slice(before).some(c => c.url.includes('/api/zzz_swap_status')));
      setTimeout(() => {
        ck('互转后侧栏更新为国服', /当前装的是：国服/.test($('#zsSide').textContent),
           $('#zsSide').textContent.trim().slice(0, 40));

        // ---- 5. 手动按钮已删除(v1.5.62), 确认页面上不再有 zsToCn/zsToIntl ----
        ck('页面已无「换成国服」按钮', !$('#zsToCn'));
        ck('页面已无「换成国际服」按钮', !$('#zsToIntl'));
        // ---- 5b. 说明区存在 ----
        ck('有「为什么要换」说明区', !!$('.zwhy'));
        ck('说明里提到「更新游戏要用国服」',
           /更新游戏[\s\S]{0,20}必须【国服】/.test($('.zwhy') ? $('.zwhy').textContent : ''),
           ($('.zwhy') ? $('.zwhy').textContent : '').replace(/\s+/g,'').slice(0, 120));
        ck('说明里提到「只挂 mod 不用换」',
           /只挂 mod（XXMI \/ ZZMI）→ 不用换/.test($('.zwhy') ? $('.zwhy').textContent : ''));
        ck('说明里提到「开脚本要用国际服」',
           /用脚本（注入器）→ 必须【国际服】/.test($('.zwhy') ? $('.zwhy').textContent : ''));
        ck('说明里提到「开脚本要用国际服文件」',
           /开脚本/.test($('.zwhy') ? $('.zwhy').textContent : ''));
        // ---- 5c. 侧栏提示随版本变化 ----
        (function(){
          // 当前 STATUS.side 已被改成 cn(上面互转测试改的)
          const t = $('#zsSide').textContent;
          ck('国服时提示「可直接更新游戏」', /可直接更新游戏/.test(t), t.slice(0, 60));
        })();

        // ---- 6. 选文件夹 ----
        const b3 = calls.length;
        $('#zsCnPick').click();
        setTimeout(() => {
          const c3 = calls.slice(b3).filter(c => c.url.includes('/api/zzz_swap_pick'));
          ck('点📁发出 swap_pick', c3.length === 1, JSON.stringify(c3.map(c => c.body)));
          ck('swap_pick which=cn',
             c3.length === 1 && c3[0].body && c3[0].body.which === 'cn',
             JSON.stringify(c3[0] && c3[0].body));

          // ---- 7. 一键启动脚本 ----
          const b4 = calls.length;
          $('#zsToolRun').click();
          // 点下去立刻进入「启动中」禁用态(缓冲期防连点)
          ck('点一键启动后按钮进入禁用态',
             $('#zsToolRun').disabled === true &&
             /启动中/.test($('#zsToolRun').textContent),
             $('#zsToolRun').textContent + ' disabled=' + $('#zsToolRun').disabled);
          setTimeout(() => {
            const c4 = calls.slice(b4).filter(c => c.url.includes('/api/zzz_tool'));
            ck('一键启动脚本发出 zzz_tool', c4.length >= 1, JSON.stringify(c4.length));
            ck('启动完成后按钮恢复可用',
               $('#zsToolRun').disabled === false &&
               /一键启动脚本\+游戏/.test($('#zsToolRun').textContent),
               $('#zsToolRun').textContent + ' disabled=' + $('#zsToolRun').disabled);

            // ---- 8. 关闭 ----
            $('#zsCloseF').click();
            ck('点关闭后面板隐藏', !$('#mZS').classList.contains('on'));
            $('#btnZZZTool').click();
            ck('可重新打开', $('#mZS').classList.contains('on'));
            $('#zsMask').click();
            ck('点遮罩也能关', !$('#mZS').classList.contains('on'));

            // ---- 9. 文件缺失时的警告 ----
            STATUS.has_cn = false;
            $('#btnZZZTool').click();
            setTimeout(() => {
              ck('缺国服文件时底部有警告',
                 /还没配好/.test($('#zsFoot').textContent) &&
                 /国服文件/.test($('#zsFoot').textContent),
                 $('#zsFoot').textContent);

              console.log('\n==== 结果: ' + PASS.length + ' 通过, ' +
                          FAIL.length + ' 失败 ====');
              if (FAIL.length) { console.log('失败项:', FAIL); process.exit(1); }
              process.exit(0);
            }, 150);
          }, 150);
        }, 150);
      }, 200);
    }, 200);
  }, 150);
}, 200);