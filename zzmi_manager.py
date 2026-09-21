#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZZMI Mod 管家  (ZZMI Mod Manager)
=========================================
绝区零 ZZMI / XXMI Launcher 的 Mod 管理界面。

v1.5.30 更新
-----------
* **卡片上新增「🗑 删除」按钮(开关左边, 标红)**: 点删除要走**两道确认弹窗** ——
  第一道问「真的要删吗」, 第二道明确提醒「删除方式=移到回收站, 不是彻底抹掉,
  后悔了去回收站右键→还原就能回来」, 两道都点确认才动手。
  后端走 Windows 原生回收站接口(SHFileOperation + ALLOWUNDO), **物理删除这条路根本不存在**;
  另有安全闸: 只认 Mods 目录里面的真实 mod 文件夹, 越界路径一律拒绝。
  删除成功后自动清掉收藏/使用时间/自选封面这些指向它的死记录

v1.5.29 更新
-----------
* **彻底屏蔽 Edge「超级拖放」搜索条**: 在界面里拖选文字松手, 浏览器会弹出
  「🔍 松开鼠标以搜索文本」蓝色提示条 —— 这是 Edge 的「超级拖放」功能, 不是网页做的。
  现在程序每次开窗口前都会往**自己的专属浏览器目录**里写一条设置
  (`edge_super_drag_drop.enabled = false`, 键名取自 msedge.dll 内部), 相当于替你把
  edge://settings 里那个开关拨到关 —— **只影响管家窗口, 你日常用的 Edge 一点不动**;
  启动参数里同时关掉对应功能开关做双保险

v1.5.28 更新
-----------
* **修: 变体识别不全的根因** —— 很多 mod 的段头写成 `[KeySwap0]后裙摆` 这种「] 后面带中文
  备注」的形式, 以前的解析只认整行就是 `[...]` 的段头, 这些段整个被跳过。现在按 3DMigoto
  真实规则取第一个 `]` 之前的部分当段名, 后面的备注(如「后裙摆」「丝袜」)还会直接当变体中文名,
  比内置翻译表更准
* **修: 变体按键信息不完整** —— `key = ctrl shift no_alt VK_UP` 里的 `no_alt` 是「不能按 Alt」
  的排除条件, 以前被整个吞掉不显示; 现在显示成 `Ctrl+Shift+↑(无Alt)`, 一眼看清真实绑定。
  落单的 `'`(撇号键)也不再被当成未闭合引号
* **修: 搜索框不再弹 Edge 的「保存的信息」自动填充** —— 主搜索框和「过滤角色」框都加了
  autocomplete=off, 浏览器不会再往这两个框里塞你的历史输入
* **F9 改成最小化/恢复**: 以前 F9 是把窗口直接藏掉(任务栏都没了, 点不回来); 现在 F9 = 最小化
  到任务栏, 点任务栏图标或再按 F9 都能恢复并置顶

v1.5.24 更新
-----------
* **重命名被系统挡下时, 也给「手动来一下」弹窗**: 以前禁用/启用失败会弹教程(打开资源管理器、
  自动选中那个 mod 文件夹、置顶, 直接按 F2 就能改), 但**改名**失败只甩一条红色小横幅
  (`重命名失败: [WinError 5] 拒绝访问。`)。现在改名撞到「拒绝访问 / 被占用」也弹同一个教程,
  里面写清楚「文件夹叫什么 → 要改成什么」, 点「📂 去改名(F2)」就跳到资源管理器里选中好,
  还能「📋 复制新名字」直接粘贴 —— 和工具本来要做的一模一样

v1.5.23 更新
-----------
* **修: 下载区文件行竖排(一个字一行)**。v1.5.22 给文件行加的中文译名用了
  `flex:0 0 100%` 想独占一行, 但那一行本身是不换行的 flex 容器 → 文件名被挤到
  1 字符宽, 显示成竖排。现给文件行加 `flex-wrap:wrap`, 译名自然换到下一行
* **下载区底部新增翻页条**: 列表很长时滑到最底下也能直接「上一页/下一页」,
  不必再滑回顶部; 翻页后自动回到列表顶部

v1.5.22 更新
-----------
* **下载区文件名也会翻中文**: 以前只翻 mod 标题, 文件那一行(如
  `white_high_heels_recolor_3.zip`)保持英文。现在文件名先去后缀/下划线换空格
  清洗成短语再机翻, 翻得出来就显示在文件名下面(受「中文译名」开关控制);
  翻不出(如整串是角色名)就不硬凑, 保持原样
* **蓝飞机(Telegram)接口暂时关闭**: 该功能还没实测通过, 本版把入口整体下线
  (下载区只剩香蕉网), 测通后下个版本恢复

v1.5.21 更新
-----------
* **修: 重命名后卡片图变灰/半天出不来**。根因不是图丢了 —— 是缩略图还没生成时,
  后端直接把**整张原图**(实测有 7MB)塞给页面, 叠加后台正在批量压图, 页面好几秒收不完,
  看起来就像图没了。现在第一次请求就**当场生成缩略图**(毫秒级), 立刻显示
* **修: 重命名后自己选的封面会跟丢**: 封面/角色标记现在会自动跟着新文件夹名迁移,
  不会再留在旧路径上失效
* (你录屏里看到的灰图就是第一条; 等几秒其实会自己出来, 但体验就是"坏了")

v1.5.20 更新
-----------
* **界面窗口不再往你的浏览器里写历史**: 以前用 Edge/Chrome 打开后, 浏览器历史里会留下一串
  `127.0.0.1:端口` 记录。现在给本程序单独一个数据目录(`数据目录\browser-profile`),
  历史/缓存只写进这里, **你自己的 Edge 历史里再也搜不到这些记录**(以前留下的旧记录要在
  Edge 里 Ctrl+H 手动删一次)
* **找不到浏览器时让你自己挑**: 顺序 Edge -> 谷歌 Chrome -> 都没有就弹文件框让你自己选一个
  浏览器, 选过一次就记住。选了非 Chrome 内核(如火狐)也能用, 只是退化成普通标签页
* 另外修掉了程序退出时命令行偶尔甩出的一段 traceback(无害但吓人)

v1.5.19 更新
-----------
* **修: 卡片排版又被挤爆(根因终于挖到)**: 卡片底部按钮行(详情/重命名/只留这套+开关)不换行,
  它的最小宽度(~250px)把网格每列从 216px 撑到 250px+, 整行横向溢出 -> 右侧卡片被窗口裁掉、
  按钮文字被压换行。现在按钮行放不下会自动换行、按钮均分空间, 任何窗口宽度都不再溢出
* (v1.5.11 加「重命名」按钮后埋下的雷, 2 按钮时代不触发, 所以"之前是好的")

v1.5.18 更新
-----------
* **蓝飞机(Telegram)下载区现在开箱即用**: telethon 库已直接打进安装包里, 不用再自己装任何依赖。
  打开「下载区 → 蓝飞机」按教程申请 api_id/api_hash、填代理、验证码登录, 就能导入频道里的 mod
* 连接 Telegram/香蕉网失败时都会提示「请确认代理/魔法已开启」

v1.5.17 更新
-----------
* 下载区顶部新增双 tab: 「香蕉网」(默认, 匿名可用) 与「蓝飞机」(Telegram 导入, 含完整教程与设置表单)
* 首次引入 Telegram userbot 导入: 拉频道消息、下载 zip/ini 附件与预览图, 只写工具自己的下载目录
* **修: 「📁 选择…」终于能用了(真凶找到了)**: 上次换成了 Windows 自带的文件夹选择框,
  但没给这个系统函数声明返回值类型 —— 它返回的是 64 位指针, Python 默认按 32 位读,
  指针被砍掉一半, 紧接着拿它去取路径就**内存越界, 程序直接崩**。
  日志里那句 `access violation reading 0x...` 就是它。现在签名声明齐了,
  实测能正常弹出、正常选中、正常取回路径
* 不会再出现「点了按钮像没反应」: 就算系统框真出不来, 也会明确告诉你可以直接粘贴路径

v1.5.15 更新
-----------
* **修: 下载目录真的改不了了(关键)**: 从资源管理器地址栏复制路径时 Windows 会自动加引号
  (英文双引号包住整个路径), 以前没处理 -> 被当成相对路径拼到程序自己的目录后面 -> 报「建不了这个文件夹」,
  看起来就是「怎么都改不了」。现在引号(含中文引号)一律剥掉, 带引号粘贴也能正确生效
* **修: 相对路径会静默跑偏**: 以前输入相对路径会被悄悄拼到程序运行目录, 文件下到哪都不知道。
  现在明确拒绝并提示「请填完整路径(例如 D: 后面跟文件夹名)」
* **选择文件夹更稳**: 选择框现在挂到界面窗口上(天然在浏览器之上), 另有看门狗反复把它拽到最前,
  不会再出现「点了没反应」。选完**直接生效**, 不用再点「改到这里」
* **每个按钮都有反馈**: 「📂 打开」「改到这里」无论成功失败都弹提示并带上实际路径,
  不会再有「按了没动静」的感觉

v1.5.14 更新
-----------
* **角色名显示中文**: v1.5.13 的角色下拉只有英文转写名(Anby Demara 这种), 认不出是谁。
  现在显示成「安比·德玛拉 · Anby Demara (130)」——中文在前、英文保留方便搜索。
  内置了绝区零 62 个角色的官方中文名对照表(零网络依赖), 以后出新角色会自动机翻兜底
* **修: 「📁 选择…」点了没反应**: 打包后弹文件夹选择框必失败(`No module named 'tkinter'`,
  PyInstaller 默认不收 tkinter)。改成直接调 Windows 自带的文件夹选择框, 任何机器都能用;
  另外弹框前先把界面窗口顶到最前, 免得选择框开在浏览器后面看不见
* **修: 「📂 打开」打不开文件夹**: 本程序是管理员权限跑的, 有些机器上 explorer 被静默拦掉。
  改成三级回落(explorer 定位 → explorer 直开 → ShellExecuteW), 总有一级能开

v1.5.13 更新
-----------
* **下载区加「角色分类」**: 香蕉网 Character Skins 下面其实有 62 个角色(安比、雅、薇薇安…),
  以前只能按整个分类爬。现在下载区顶部有个角色下拉, 选谁就只列谁的 mod(带该角色的 mod 数量),
  也能随时切回「全部角色」。角色列表本地缓存 1 天, 想手动刷就点旁边的「↻ 刷新」
* **下载的文件自己挑**: 每个 mod 卡片现在会展开它的全部文件(文件名 + 大小 + 杀毒结果),
  勾哪个下哪个 —— 一个 mod 有多个版本/分卷时不用整个包都拖下来; 还能「全选 / 全不选」。
  怕请求太多可以关掉「列出文件」开关
* **「已下载」标记**: 下过的文件在卡片上标「已下载」, 一眼看出哪些重复了。
  下载目录弹窗里也能看到目录位置、文件总数和总大小, 还能一键清空记录(只清标记, 不删文件)
* **下载目录能选不用手打**: 弹窗里加了「📁 选择…」直接弹系统文件夹选择框

v1.5.12 更新
-----------
* **新增「⬇ 下载区」: 直接从 GameBanana 抓 mod**: 界面上点「⬇ 下载区」, 粘贴一个 GameBanana
  链接(分类页 / 游戏 mod 列表 / 单个 mod), 就会把上面的 mod 名字、预览图、作者列出来,
  每个都带「下载」按钮, 一键下到本地下载目录; 还能翻页、看大图、打开/清空下载目录
* **mod 名字自动翻译成中文**: 外网 mod 名大多是英文, 下载区会显示中文译名(可开关)。
  翻译结果本地缓存, 同一个名字不会反复翻
* **下载目录可自定义**: 默认放在 数据目录/downloads, 也能在下载区里改成任意盘任意文件夹

v1.5.11 更新
-----------
* **修复: 深色主题下输入弹窗文字看不清**: 弹窗的说明文字和输入框文字误用了按钮黑字色(--ink),
  深色主题下变成黑底黑字。现改为主题文字色(--txt), 深浅两套主题都清晰
* **mod 卡片新增「✎ 重命名」按钮**: 以前重命名要点进"详情"再按按钮, 现在卡片上直接一点就改,
  和详情里的入口共用同一套逻辑(名字被占用仍会自动加序号并弹窗说明)

v1.5.10 更新
-----------
* **关掉界面 = 程序真的退出了**: 以前关浏览器界面后, 真正的程序(那个被隐藏的命令窗口)
  还在后台跑、占着文件锁, 导致新安装包覆盖不了、还杀不掉(它是提权进程, 普通方式拒绝对)。
  现在界面窗口一关, 程序会在几秒后自动退出; 刷新页面(F5)不会误杀
* **输入弹窗换成自制窗(标题「ZZMI MOD 管家」)**: 以前那些"输入名字"的框是浏览器原生 prompt,
  标题栏显示的是网址、没法改。现在统一用自制弹窗, 标题就是「ZZMI MOD 管家」
* **更新提醒加了注意事项**: 发现新版本时, 提醒条里写明"更新前请先关掉本程序", 避免装不上
* **以后只发安装包, 不再单独发便携版 exe**: 安装包自带程序, 少一份文件、少一次 UAC

v1.5.9 更新
-----------
* **修掉「同名 mod 启不了」的最后一个坑**: 同一个 mod 的「启用套」和「禁用套」同时存在时
  (比如「蜜西皮肤」和「DISABLED_蜜西皮肤」都在), 点禁用那套的开关会报
  「找不到目录(可能已被移动)」—— 根因是重名条目的内部编号带了 #1 后缀, 找目录时没剥掉。
  现在: 禁用套能正常启用(重名就自动排成 XXX (2) 并弹窗), 启用套也不会被认错
* **图标换成绝区零官方图标**: exe / 安装包 / 界面窗口 / 任务栏全部统一,
  界面窗口之前显示的「地球」图标就是因为没配网页图标, 现在随程序带上

v1.5.8 更新
-----------
* **重名不再失败, 自动加序号**: 启用/禁用/重命名的时候, 如果目标名字已经被别的文件夹占了
  (最典型的就是「露西皮肤」和「DISABLED_露西皮肤」两套同时在), 以前会直接报错失败,
  现在**自动在后面加 (2) (3)…** —— 和 Windows 复制文件一个逻辑, 依次类推, 绝不覆盖任何一个
* **弹窗告诉你改成了什么**: 自动改名后会弹一个说明窗, 写清「你想叫 X → 实际叫 X (2)」,
  不满意就地重命名即可; 批量操作/套用方案时会一次性列出所有被改名的项
* 已经带 (2) 的名字会**接着往下排**(变成 (3)), 不会叠成「XXX (2) (2)」这种套娃名
* 单个 ini 文件、子目录的启停同样处理

v1.5.7 更新
-----------
* **不再有黑窗口挡着**: 以前每次打开都会弹一个黑色命令窗口(关掉它程序就退出了),
  现在界面一起来**命令窗口会自动藏掉**, 桌面上只留界面本身
* 日志没丢 —— 全部同时写进 `数据目录/zzmi.log`(超过 512KB 自动轮转成 .old),
  出问题时在界面「设置」里可以一键把命令窗口调回来看, 或手动加 `--console` 启动

v1.5.6 更新
-----------
* **改不了名的时候手把手教你**: 启用/禁用某个 mod 时如果文件夹改名失败(游戏还开着、
  被资源管理器占着、或是只读/杀软锁着), 除了原来那行提示, 现在会**弹一个教程弹窗**:
  说清是「被占用」还是「没权限」, 直接告诉你该把文件夹名改成什么, 附 4 步操作说明
* **一键复制 DISABLED_**: 弹窗里有「📋 复制 DISABLED_」, 点一下就把这串字符放进剪贴板,
  到资源管理器里粘贴到文件夹名最前面即可; 旁边「📂 去改名」直接打开那个 mod 所在的文件夹,
  并且**像「打开文件夹」一样把窗口顶到屏幕最前面**, 不用自己一层层翻进去
* **启用失败则反过来**: 启用失败(要删掉名字前面的 DISABLED_)时是同一套弹窗, 只是教程
  反过来 —— 教你**把 DISABLED_ 删掉**, 按钮变成「📂 去回删」
* 这套教程对**批量启用/禁用、全选启用/禁用、套用方案**同样生效(哪个卡住了就教你改哪个)

v1.5.5 更新
-----------
* **仓库可以自己加了**: 「🗑 仓库管理」面板里新增「添加仓库」—— 既能**在 ZZMI 目录下新建**,
  也能**锁定一个磁盘上已存在的文件夹**(任意盘符都行, 不必在 ZZMI 目录里); 加过的会一直留在
  下拉列表里, 想移出就点「移除」(只去列表, 磁盘文件夹一个都不删)
* **仓库列表空了也不迷路**: 仓库页在"还没发现仓库目录"时给出「＋ 添加仓库 / 📁 手动寻找
  仓库路径」入口, 不用再去别的地方绕一圈才能建仓库

v1.5.4 更新
-----------
* **变体一键改键**: 详情页「变体提示」那一行的每个变体后面多了「⌨ 改键」—— 输入
  「修饰键 空格 主键」(例如 ctrl a / shift f1 / 小键盘0) 即可改掉游戏内的循环切换键;
  工具自己去 ini 里找 `key =` 那行**只换键位**, 注释/换行/编码原样保留, 改前整文件备份,
  顶栏「撤销」可还原
* **仓库可以删了**: 搬运下拉新增「🗑 删除仓库…」, 仓库和自定义文件夹都能逐项移除 ——
  只从列表里去掉, 磁盘上的文件夹和 mod 一个都不会删
* **新装默认不带仓库**: 不再自动塞几个探测到的仓库, 列表从空开始, 想用自己加

v1.5.3 更新
-----------
* **mod 直接从 Mods 根开始找**: 以前只认「Mods\\分类\\mod」这种两层结构, 直接把 mod
  文件夹丢进 Mods 里会被当成内部子目录(名字显示成 resources/sub), 现在会自动收拢
  成 mod 本身并归到「(根目录)」; ini 直接散落在 Mods 根目录的也会合成一条, 不再报错
* **自定义文件夹(搬运目标)**: 仓库下拉新增「📁 自定义文件夹…」, 弹出文件夹浏览器 ——
  可层层点进去、可跳盘符/桌面/文档/下载、可在当面位置新建文件夹, 选完即可搬;
  用过的路径会记住, 下次直接选。不再局限于 ZZMI 目录下的仓库

v1.5.2 更新
-----------
* 窗口改成**打开就全屏**(最大化)。之前按"屏幕一半居中"太小了, 现在:
  --start-maximized 起步, 并额外用 Win32 把它最大化一次(有些 Edge/Chrome 版本
  在 --app 模式下不认 start-maximized); 想固定尺寸就把设置里的 win_size 写成
  1000,700 这种, 此时仍按该尺寸居中打开

v1.5.1 更新
-----------
* 「打开文件夹」直接弹到最前面, 不用再点一次任务栏。本程序常以管理员身份运行,
  这时系统的 SetForegroundWindow 会被拒绝 —— 现在改用「topmost 闪一下 + 敲 ALT 解前台锁」
  的方式把目标窗口顶到最前
* 窗口默认按**屏幕的二分之一大小 + 正中间**打开(自动跟随屏幕分辨率, 换显示器也对);
  想固定尺寸就在设置里把 win_size 写成 1000,700 这种(此时仍会居中), 写 auto 就跟着屏幕走
  —— (注: 该默认值已在 v1.5.2 改成打开即全屏, 见上)

v1.5 更新
---------
* 一键搬运: 在卡片上勾选多个 mod(或按当前筛选全选), 选好仓库, 一次搬过去 ——
  搬走的 mod 不再留在 Mods 里被扫描、被游戏加载; 目标仓库同名自动加 (2) 绝不覆盖;
  每次搬运都写日志, 顶栏「撤销」可回退
* 禁用/改名不再怕「拒绝访问(WinError 5)」: 被占用时自动重试并告诉你到底是谁挡着
  (游戏还开着 / 资源管理器开着那个目录 / 杀软拦截), 本工具自己读图片时也改成
  「允许删除共享」, 保证自己永远不会成为占用方

v1.4.9 更新
-----------
* 收藏置顶: mod / 角色 / 分类都能标 ⭐ —— 卡片右上角、侧栏列表行、详情页都有开关;
  侧栏「总览」新增「⭐ 收藏」入口, 收藏过的永远排在最前面
* 默认排序改为「使用时间最近」: 每次启用 mod / 切变体都会记下使用时间(文件很少被改,
  按修改时间排基本看不出先后), 没记录过的回退用修改时间

v1.4.8 更新
-----------
* 列表顺序: 已启用在前、未启用在后, 同组内按修改时间从新到旧
* 预览图: 可点开大图、可一键换封面(把照片存进 mod 文件夹)、可在文件夹已有的
  图片里自己挑一张当封面; 并**彻底禁用把 .dds 当预览图**(贴图/模型资源一律不读)
* 角色归并: 名字里的括号附属说明先剥掉(希格莉德{…}=希格莉德、月城柳（…）=月城柳),
  「功能/工具/修复…」类 mod 统一归成一个名字, 「NPC/NoName/Name…」占位名统一归成 NPC

v1.4 更新
---------
* 变体键全识别: VK_* 虚拟键码(如 VK_CAPITAL→大写锁定、VK_RBUTTON→鼠标右键、
  VK_F1~F24、鼠标侧键、小键盘、OEM 键等)全部翻译成中文键名, 不再显示裸名
* 预览图读全层级: 递归扫描 mod 所有层级(第 1/2/3 层…), 深层里的样本图也能被读到并做封面;
  封面优先级改为「预览/封面/示例等关键词 > 截图 > 其他」, 不再被顶层贴图分页名(1/0)压住
* 检查更新: 界面顶部有「检查更新」按钮, 启动时也会自动查一次;
  发现新版本会弹提醒条(带下载链接), 设置里可改更新仓库(owner/repo)

v1.3 更新
---------
* 热键循环变体: 解析 ini 里 [Key*] 段的 `$var = 0,1,2` + `type = cycle`
  (游戏里按 H// 等键循环切换的那种), 在界面里做成变体按钮;
  切换 = 旋转循环列表让目标值排第一 (mod 加载时直接处于该变体), 完全可逆
* 全局快捷键: 可自定义(默认 Ctrl+Alt+M), 绝区零运行时按下即可呼出/隐藏管理器窗口

v1.2 更新
---------
* 部件 / 变体开关: 解析每个 mod 内所有 ini 的 TextureOverride hash,
  自动把「覆盖同一游戏资源」的文件归为一个变体组(组内只能开一个, 一键切换);
  不冲突的文件做成独立开关(如 face / body / 附加件)
* 文件级禁用: 文件名加 `DISABLED_` 前缀, 与目录级同一套机制, 永不删文件、可撤销
* 备份副本(DISABLED_BACKUP_* / disabled_beifen_* 等)自动识别并排除, 不会误报变体

v1.1 更新
---------
* 独立窗口: 用 Edge/Chrome 的 --app 模式打开, 看起来就是个软件窗口;
  并强制 `--proxy-server=direct://` 绕过系统代理(很多人 127.0.0.1 被代理拦截导致界面点不动)
* 服务端缩略图: 预览图统一压成 420px JPEG 缓存, 列表秒开不再卡
* 按角色分类: 自动从 mod 名推断角色(可手改), 一个角色多套 mod 一眼看清、一键只留一套
* 连接失败提示: 打不开后端时界面会明确告诉你怎么做

技术要点
--------
* 纯 Python 标准库; 缩略图在有 Pillow 时用 Pillow, 没有就回退原图
* 只绑 127.0.0.1, 带一次性访问令牌
* 禁用 = 目录名加 `DISABLED_` 前缀 (官方 d3dx.ini: exclude_recursive = DISABLED*), 永不删文件
* 所有写操作写 journal, 可撤销

环境变量
--------
ZZMI_MANAGER_DATA  自定义数据目录
ZZMI_NO_BROWSER=1  不自动打开窗口
"""

import base64
import ctypes
from ctypes import wintypes
import hashlib
import io
import json
import mimetypes
import os
import queue
import re
import shutil
import socket
import string
import subprocess
import sys
import threading
import time
import traceback
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

VERSION = "1.5.30"
APP_NAME = "ZZMI Mod 管家"

# GitHub 仓库(用于自动更新检查); 也可以在设置里改成自己的 fork
UPDATE_REPO = "782838/ZZMI-Mod-Manager"

DISABLED_PREFIX = "DISABLED_"
DISABLED_TEST = re.compile(r"^(?:disabled|禁用)", re.IGNORECASE)

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".avif")
# 永远不当作预览图的扩展名 —— .dds 是游戏贴图/模型资源, 拿来当封面只会选到模型文件, 直接禁用
NEVER_IMAGE_EXTS = (".dds",)
# 「一键添加预览图」写进 mod 文件夹的文件名前缀: 优先级最高, 保证用户选的封面一定生效
COVER_STEM = "zzmi_cover"
# 单个 mod 最多扫多少张候选图片(给「切换预览图」列表用)
MAX_CANDIDATE_IMAGES = 60
# 预览图优先级关键词(命中即 rank 0, 最优先做封面; 含中英文样本图命名)
PREVIEW_PRIORITY = ("preview", "cover", "thumb", "showcase", "sample",
                    "预览", "示例", "样例", "展示", "封面", "说明图", "pic")

DATA_DIR = (os.environ.get("ZZMI_MANAGER_DATA")
            or os.path.join(os.path.expanduser("~"), ".zzmi-manager"))
CONFIG_PATH = os.path.join(DATA_DIR, "config.json")
PRESETS_PATH = os.path.join(DATA_DIR, "presets.json")
JOURNAL_PATH = os.path.join(DATA_DIR, "journal.jsonl")
THUMB_DIR = os.path.join(DATA_DIR, "thumbs")
THUMB_PX = 420


def _res_dir():
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS",
                       os.path.dirname(os.path.abspath(sys.executable)))
    return os.path.dirname(os.path.abspath(__file__))


UI_PATH = os.path.join(_res_dir(), "ui.html")
BG_PATH = os.path.join(_res_dir(), "bg.jpg")
# v1.5.9 绝区零图标 favicon: 打包后在资源根, 源码运行时在 installer/ 下
ICON_PATH = os.path.join(_res_dir(), "app.ico")
if not os.path.isfile(ICON_PATH):
    ICON_PATH = os.path.join(_res_dir(), "installer", "app.ico")

DEFAULT_CONFIG = {
    "zzmi_root": "",
    "launcher_exe": "",
    "importer": "ZZMI",
    "game_exe": "",
    "mods_dir": "",
    "libraries": [],
    "libs_abs": [],         # 锁定为仓库的绝对路径(可以在任意盘, 不必在 ZZMI 目录下)
    "custom_dirs": [],      # 「自定义文件夹」最近用过的目标(完整路径)
    "theme": "dark",
    "hide_preview": False,
    "char_overrides": {},
    "thumb_overrides": {},
    "pinned_mods": [],
    "pinned_cats": [],
    "pinned_chars": [],
    "usage": {},
    "win_size": "auto",
    "hotkey": "F9",
    "update_repo": UPDATE_REPO,
    "downloads_dir": "",        # v1.5.12 下载区: mod 下载到哪(空=数据目录/downloads)
    "show_translated": True,    # v1.5.12 下载区: 是否显示中文译名
}

ROOT_SKIP = {"resources", "themes", "locale", "backups", "dds", "bin",
             "strings", "packages", "cache", "security", "debugger"}
IMPORTER_SKIP = {"mods", "core", "shadercache", "shaderfixes", "debugger"}
LIB_NAME_SKIP = ("reshade", "preset", "shader", "cache", "backup", "debug",
                 "log", "temp")


# ===========================================================================
# 基础工具
# ===========================================================================

def log(*a):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), " ".join(str(x) for x in a))
    try:
        sys.stdout.write(line + "\n")
        sys.stdout.flush()
    except Exception:
        pass
    # v1.5.7: 命令窗口会藏起来, 所以日志同时落盘一份, 出问题好排查
    try:
        p = os.path.join(DATA_DIR, "zzmi.log")
        if os.path.isfile(p) and os.path.getsize(p) > 512 * 1024:
            os.replace(p, p + ".old")          # 超过 512KB 就轮转一次
        with open(p, "a", encoding="utf-8", errors="replace") as f:
            f.write(line + "\n")
    except Exception:
        pass


def is_disabled_name(name):
    return bool(DISABLED_TEST.match(name or ""))


def strip_disabled(name):
    n = name or ""
    while True:
        m = DISABLED_TEST.match(n)
        if not m:
            break
        n = n[m.end():].lstrip("_- ")
    return n or (name or "")


def human_size(n):
    n = float(n or 0)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return ("%.0f %s" % (n, unit)) if unit == "B" else ("%.1f %s" % (n, unit))
        n /= 1024.0


def human_time(ts):
    try:
        return time.strftime("%m-%d %H:%M", time.localtime(ts))
    except Exception:
        return ""


def read_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def write_json(path, obj):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def norm_rel(p):
    return (p or "").replace("\\", "/").strip("/")


def safe_join(base, rel):
    rel = (rel or "").replace("/", os.sep).replace("\\", os.sep)
    rel = rel.strip(os.sep)
    if not rel:
        return None
    parts = [p for p in rel.split(os.sep) if p not in ("", ".")]
    if any(p == ".." for p in parts):
        return None
    if os.path.isabs(rel) or re.match(r"^[a-zA-Z]:", rel):
        return None
    p = os.path.normpath(os.path.join(base, *parts))
    if not os.path.abspath(p).startswith(os.path.abspath(base) + os.sep):
        return None
    return p


# 重名条目的 id 会被 scan_mods 加上 "#1" "#2" 后缀(见 entries 去重那段),
# 解析路径时必须剥掉, 否则永远「找不到目录」。
_TAIL_NUM_ID_RE = re.compile(r"^(.*)#\d{1,3}$")


def resolve_rel_dir(base, rel, prefer=None):
    """按相对路径找目录, 允许任意一段带 DISABLED_ / disabled 前缀。

    v1.5.9: 同一个 mod 的「启用套 + 禁用套」同时存在时, 两个条目的 id 都来自
    同一个名字(其中一个带 #N)。剥掉后缀后 stripped 名字能同时匹配两个目录,
    这时用 prefer(= 扫描时记录的真实目录名)精确选中, 不认错套。
    prefer 只作用于最后一段 —— 它是条目自己的目录名, 和上级目录无关。
    """
    parts = [p for p in norm_rel(rel).split("/") if p]
    if parts:
        m = _TAIL_NUM_ID_RE.match(parts[-1])
        if m:
            parts[-1] = m.group(1)
    last = len(parts) - 1
    cur = base
    for idx, part in enumerate(parts):
        try:
            names = os.listdir(cur)
        except OSError:
            return None
        # v1.5.9: 同名两套(启用套+禁用套)的 stripped 名字一模一样,
        # 走 exact 匹配会认错套(典型: 想启用 DISABLED_套, 却匹配到已启用的那套,
        # 白返回一个「已是启用状态」)。所以最后一段且带着 prefer 时,
        # 一律以 prefer(扫描时记录的真实目录名)为准, exact 只在 prefer==part 时直接用。
        if part in names and os.path.isdir(os.path.join(cur, part)) \
                and not (idx == last and prefer and part != prefer):
            cur = os.path.join(cur, part)
            continue
        cands = [n for n in names
                 if os.path.isdir(os.path.join(cur, n))
                 and strip_disabled(n) == strip_disabled(part)]
        hit = None
        if cands:
            if prefer and idx == last and prefer in cands:
                hit = prefer
            elif part in cands:
                hit = part
            else:
                hit = cands[0]
        if hit is None:
            return None
        cur = os.path.join(cur, hit)
    return cur


def entry_root(mods_dir, e):
    """按条目找它的真实目录(自动处理 id 的 #N 后缀 + 同名两套的精确选中)。"""
    if not e:
        return None
    prefer = os.path.basename(norm_rel(e.get("path") or ""))
    return resolve_rel_dir(mods_dir, e["id"], prefer=prefer or None)


# ===========================================================================
# Windows 文件占用 / 改名加固
#
# 为什么需要: 重命名一个文件夹, Windows 要求「文件夹本身可删 + 里面任何被打开的
# 文件都允许删除共享(sharing delete)」。游戏(3DMigoto 加载着 ini)、资源管理器开着
# 那个目录、杀软实时扫描、甚至本工具自己在读里面的图, 都会让改名报
# [WinError 5] 拒绝访问 / 另一个程序正在使用 —— 而且往往只持续几十毫秒。
# 所以: ①先探测到底为什么改不了 ②失败自动重试 ③本工具自己读文件时带上
# FILE_SHARE_DELETE, 保证自己永远不会成为"占用方"。
# ===========================================================================

_WIN = (os.name == "nt")

def _k32():
    import ctypes
    from ctypes import wintypes
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    k.CreateFileW.restype = wintypes.HANDLE
    k.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                              ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD,
                              wintypes.HANDLE]
    return k, ctypes, wintypes


_DELETE = 0x00010000
_SHARE_ALL = 0x1 | 0x2 | 0x4          # READ | WRITE | DELETE
_SHARE_RWD = _SHARE_ALL
_OPEN_EXISTING = 3
_BACKUP_SEMANTICS = 0x02000000        # 打开目录必须带这个
_INVALID = -1

_LOCK_TEXT = {
    5: "权限被拒绝(只读属性 / 杀软拦截 / 没有管理员权限)",
    32: "正被别的程序占用(最可能是游戏还开着, 或资源管理器开着这个目录)",
    33: "文件被锁定",
}


def _probe_delete(path):
    """探测能否拿到 DELETE 权限(= 能不能改名/移动)。返回 (ok, 中文原因)"""
    if not _WIN:
        return True, ""
    try:
        k, ctypes, wintypes = _k32()
        h = k.CreateFileW(path, _DELETE, _SHARE_ALL, None, _OPEN_EXISTING,
                          _BACKUP_SEMANTICS, None)
        bad = (h is None or h == wintypes.HANDLE(_INVALID).value or
               h == ctypes.c_void_p(_INVALID).value)
        if not bad:
            k.CloseHandle(h)
            return True, ""
        e = ctypes.get_last_error()
        return False, _LOCK_TEXT.get(e, "错误码 %d" % e)
    except Exception:
        return True, ""      # 探测本身失败就不下结论, 交给真正的改名去试


def lock_reason(path, scan_files=40):
    """给一个目录做体检: 是目录本身被占, 还是里面某个文件被占。"""
    ok, why = _probe_delete(path)
    if not ok:
        return False, "目录本身" + why
    if not os.path.isdir(path):
        return True, ""
    n = 0
    for cur, dirs, files in os.walk(path):
        for d in dirs:
            if n >= scan_files:
                break
            ok2, why2 = _probe_delete(os.path.join(cur, d))
            n += 1
            if not ok2:
                return False, "子目录「%s」%s" % (d, why2)
        for f in files:
            if n >= scan_files:
                break
            ok2, why2 = _probe_delete(os.path.join(cur, f))
            n += 1
            if not ok2:
                return False, "里面的文件「%s」%s" % (f, why2)
        if n >= scan_files:
            break
    return True, ""


def read_bytes_shared(path, cap=None):
    """读文件内容, 但用 FILE_SHARE_DELETE 打开 —— 本工具读图时不会挡住你改名。
    cap 给出时超过就只读前 cap 字节(返回的 bytes 会被截断)。"""
    if _WIN:
        try:
            k, ctypes, wintypes = _k32()
            h = k.CreateFileW(path, 0x80000000, _SHARE_RWD, None, _OPEN_EXISTING,
                              0x80 | 0x10000000, None)   # NORMAL|SEQUENTIAL
            if h in (None, wintypes.HANDLE(_INVALID).value):
                h = None
            if h is not None:
                ReadFile = k.ReadFile
                ReadFile.argtypes = [wintypes.HANDLE, ctypes.c_void_p,
                                     wintypes.DWORD, ctypes.POINTER(wintypes.DWORD),
                                     ctypes.c_void_p]
                buf = ctypes.create_string_buffer(1 << 16)
                chunks, total = [], 0
                while True:
                    got = wintypes.DWORD(0)
                    if not ReadFile(h, buf, len(buf), ctypes.byref(got), None):
                        break
                    if got.value == 0:
                        break
                    chunks.append(buf.raw[:got.value])
                    total += got.value
                    if cap and total >= cap:
                        break
                k.CloseHandle(h)
                data = b"".join(chunks)
                return data[:cap] if cap else data
        except Exception:
            pass
    with open(path, "rb") as f:
        return f.read(cap) if cap else f.read()


def unique_path(dst, limit=60):
    """目标已存在时自动加 (2) (3)…, 绝不覆盖已有文件。"""
    if not os.path.exists(dst):
        return dst
    base, ext = os.path.splitext(dst)
    for i in range(2, limit + 2):
        cand = "%s (%d)%s" % (base, i, ext)
        if not os.path.exists(cand):
            return cand
    return None


# 已经被我们用过后缀的名字, 再重名就接着往后排: "露西皮肤 (2)" -> "露西皮肤 (3)"
# 而不是叠成 "露西皮肤 (2) (2)"。只认半角/全角括号 + 纯数字结尾。
_NUM_SUFFIX_RE = re.compile(r"^(.*?)[\s]*[（(](\d{1,3})[）)]$")


def auto_unique_name(dst, limit=200):
    """目标已存在时自动往后加 (2) (3)…

    跟 unique_path 的区别: 这个**只管起名, 不落盘也不判断能不能写**,
    返回 (最终路径, 用到的序号)。序号从 2 起, 也就是用户说的「依次类推」。
    已带 (n) 后缀的名字会接着往下排, 避免出现 (2) (2) 这种套娃名。

    返回值里 seq=None 表示原名没被占用, 不需要提示用户。
    """
    if not os.path.exists(dst):
        return dst, None
    d, name = os.path.split(dst)
    m = _NUM_SUFFIX_RE.match(name)
    stem, start = (m.group(1), int(m.group(2)) + 1) if m else (name, 2)
    for i in range(start, start + limit):
        cand = os.path.join(d, "%s (%d)" % (stem, i))
        if not os.path.exists(cand):
            return cand, i
    return None, None


def move_dir(src, dst, rec=None, tries=3):
    """搬目录: 优先 os.rename(同盘瞬间完成), 失败自动重试, 跨盘回退 shutil.move。
    成功写 journal(可撤销); 失败给出「到底被谁挡着」的中文原因。"""
    if not src or not os.path.isdir(src):
        return False, "源目录不存在"
    if not dst:
        return False, "目标路径不合法"
    sa, da = os.path.abspath(src), os.path.abspath(dst)
    if sa == da:
        return False, "源和目标相同"
    if da.startswith(sa + os.sep):
        return False, "不能移动到自己的子目录里"
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
    except OSError as ex:
        return False, "建不了目标目录: %s" % ex
    if os.path.exists(dst):
        return False, "目标已存在: %s" % os.path.basename(dst)
    last = None
    for i in range(max(1, tries)):
        try:
            os.rename(src, dst)
            if rec:
                journal_append(rec)
            return True, "ok"
        except OSError as ex:
            last = ex
            # 跨盘(不同卷)时 rename 会失败, 用 shutil.move 复制+删除
            if getattr(ex, "winerror", None) in (17, 18) or "different disk" in str(ex).lower():
                try:
                    shutil.move(src, dst)
                    if rec:
                        journal_append(rec)
                    return True, "ok(跨盘复制)"
                except Exception as ex2:
                    last = ex2
            ok, why = lock_reason(src, scan_files=12)
            if not ok and i >= 1:
                return False, "被占用: %s" % why
            time.sleep(0.12 * (i + 1))
    ok, why = lock_reason(src, scan_files=12)
    if not ok:
        return False, "被占用: %s" % why
    msg = str(last or "")
    if "另一个程序正在使用" in msg or "being used by another" in msg:
        return False, "被占用(游戏或资源管理器开着这个目录), 关掉再试"
    return False, "失败: %s" % msg


# ===========================================================================
# 角色推断
# ===========================================================================

CHAR_VARIANT = {"零号", "异色", "sp", "邦布"}
# 工具/功能类 mod: 推断出这些词就统一归到一个名字下, 否则一个功能 mod 就占侧栏一行
CHAR_TOOL_WORDS = {
    "功能": "功能", "工具": "工具", "修复": "修复", "补丁": "补丁", "整合": "整合",
    "整合包": "整合", "其他": "其他", "其它": "其他", "杂项": "杂项", "未分类": "未分类",
    "测试": "测试", "菜单": "菜单", "界面": "界面", "ui": "UI", "uid": "UID",
    "mod": "Mod", "模组": "Mod",
}
# NPC / 占位名: 统一归到 NPC, 不然 Name / NoName / NPC / NPC2 会各占一行
CHAR_NPC_WORDS = {"npc", "noname", "no name", "no_name", "name", "无名", "无名氏",
                  "占位", "占位符", "placeholder", "undefined", "null"}
CHAR_GENERIC_HEAD = {"功能", "工具", "修复", "整合", "其他", "杂项", "未分类",
                     "ui", "uid", "mod", "测试"}
CHAR_WORDS = [
    "微型比基尼", "微比基尼", "吊带比基尼", "条形比基尼", "奶牛比基尼", "比基尼",
    "反兔女郎", "兔女郎", "泳装", "泳衣", "奶牛", "皮肤", "常服丰满", "常服",
    "紧身连衣裤", "身体写作", "身体涂鸦", "身体彩绘", "束缚", "机甲", "切换",
    "替换", "性感的牛", "美丽的豹子", "迷人", "性感", "全裸", "怀孕", "多切换",
    "暗影", "奶盖", "小围裙", "重制", "汉化", "整合", "修复", "逆兔", "正兔",
    "白丝", "黑丝", "破洞", "淫纹", "涂鸦", "写作", "菜单", "模式", "银兎",
    "时装", "服饰", "套装", "礼服", "旗袍", "和服", "制服",
]
CHAR_TAIL_DROP = re.compile(r"(v\d+(\.\d+)*|[0-9]+(\.[0-9]+)*|[a-zA-Z]+)$")
STRIP_CHARS = " -_·—－・/."
# 名字里的括号内容都是附属说明(如「希格莉德{隐隐约约…}」「月城柳（只能看到一点…）」),
# 留着参与匹配只会把同一个角色拆成好几条, 所以先剥掉
_BRACKET_BODY = r"[^）)\]】〕〉」》]*"
BRACKET_PAIRS = re.compile(r"[（(\[{【〔〈「《]" + _BRACKET_BODY + r"[）)\]】〕〉」》]")
BRACKET_OPEN_TAIL = re.compile(r"[（(\[{【〔〈「《]" + _BRACKET_BODY + r"$")


def strip_brackets(s):
    """剥掉名字里的括号附属说明: 希格莉德{隐隐约约…} -> 希格莉德; 月城柳（…） -> 月城柳。"""
    s = BRACKET_PAIRS.sub("", s or "")
    s = BRACKET_OPEN_TAIL.sub("", s)
    return s.strip()


def auto_char(name):
    """从 mod 名推断角色名; 推断不出来就返回剥掉括号后的原名。

    v1.4.7 起:
      * 先剥掉括号/花括号等附属说明, 让「希格莉德」和「希格莉德{…}」归到一起;
      * 「功能 / 工具 / 修复 …」这类统一归成一个名字(功能 Arc / 功能-隐藏UID -> 功能);
      * 「NPC / NoName / Name …」这类占位名统一归成 NPC。
    """
    base = strip_disabled(name or "").strip()
    if not base:
        return base
    core = strip_brackets(base).strip(STRIP_CHARS)
    if not core:
        return base
    if core.lower() in CHAR_NPC_WORDS or core.lower().startswith("npc"):
        return "NPC"
    segs = [s for s in re.split(r"[-_·—－・/ &+]+", core) if s]
    changed = (core != base)
    if len(segs) > 1 and segs[0].lower() in {v.lower() for v in CHAR_VARIANT}:
        segs = segs[1:]
        changed = True
    # 工具/功能类 -> 统一成一个名字(只看前两段, 避免误伤角色名里的字)
    for seg in segs[:2]:
        key = seg.strip().lower()
        if key in CHAR_TOOL_WORDS:
            return CHAR_TOOL_WORDS[key]
        if key.startswith("npc"):
            return "NPC"
    h = segs[0] if segs else core
    for _ in range(5):
        before = h
        low = h.lower()
        for w in sorted(CHAR_WORDS, key=len, reverse=True):
            wl = w.lower().strip()
            if not wl:
                continue
            if low.endswith(wl) and len(h) > len(wl):
                h = h[:-len(wl)].strip(STRIP_CHARS + "0123456789.")
                break
            if low.startswith(wl) and len(h) - len(wl) >= 2:
                h = h[len(wl):].strip(STRIP_CHARS)
                break
        if h != before:
            continue
        m = CHAR_TAIL_DROP.search(h)
        if m and m.start() >= 2:
            h = h[:m.start()].strip(STRIP_CHARS)
        if h == before:
            break
    h = h.strip(STRIP_CHARS)
    if not h or h.lower() in CHAR_GENERIC_HEAD:
        return core          # 归不到具体角色: 用剥掉括号后的名字(也别退回带括号的原名)
    return h


# ---------------------------------------------------------------------------
# 层级判定: Mods 下第 1 层到底是"分类文件夹"还是"直接放在根下的 mod"
# ---------------------------------------------------------------------------

# ini 直接散落在 Mods 根目录时, 合出来这条 entry 用的标记
ROOT_MOD_ID = "__mods_root__"
ROOT_MOD_NAME = "(Mods 根目录散装)"

# mod 内部常见的资源目录名 —— 见到这些名字, 说明它的上一层才是 mod 本身
INNER_DIR_WORDS = (
    "resources", "resource", "texture", "textures", "tex", "body", "face",
    "hair", "weapon", "fx", "icons", "icon", "fonts", "font", "shader",
    "shaders", "mesh", "models", "model", "main body", "mainbody",
    "贴图", "资源", "身体", "脸", "头发", "武器", "特效", "材质",
)

# 分类文件夹常见的名字特征
CLASSIFY_WORDS = (
    "合集", "分类", "功能", "工具", "整合", "补丁", "全部", "未使用",
    "备份", "仓库", "暂存", "收藏", "其它", "其他", "mods",
)


def looks_like_inner_dir(name):
    """这一层看着像不像「mod 内部的资源目录」(而不是 mod 本身)。"""
    n = (name or "").strip().lower()
    if not n:
        return False
    for w in INNER_DIR_WORDS:
        if n == w or n.startswith(w + " ") or n.endswith(" " + w):
            return True
    return False


def is_classifier_dir(name, strong=False):
    """Mods 下的第 1 层目录是「分类文件夹」还是「直接放在根下的 mod」。

    返回 True = 它是分类(下面还有一层 mod), False = 它自己就是个 mod。
    strong=True 时只用强判据(分类词 / 能提炼出角色名), 不再因为"没有中文"
    就当成分类 —— 用于"这个目录下只有唯一一个分支"的场景, 那种情况它更可能
    是一个 mod 而不是分类。
    """
    n = strip_disabled(name or "").strip()
    if not n:
        return True
    low = n.lower()
    for w in CLASSIFY_WORDS:
        if w in low:
            return True
    body = strip_brackets(n)
    c = auto_char(body)
    if c and c != body and len(c) >= 2:
        return False         # 能提炼出角色名 -> 它本身就是个 mod
    if strong:
        return False         # 没有强判据命中 + 只有单一分支 -> 当成 mod
    if not any('\u4e00' <= c <= '\u9fff' for c in body):
        return True          # 没有中文(纯编号/英文短名) -> 更像分类容器
    return True


# ===========================================================================
# 自动探测 ZZMI
# ===========================================================================

def score_xxmi_root(d):
    if not d or not os.path.isdir(d):
        return 0, {}
    score = 0
    info = {"importers": [], "launcher_exe": "", "config_json": ""}
    for cand in (os.path.join(d, "Resources", "Bin", "XXMI Launcher.exe"),
                 os.path.join(d, "XXMI Launcher.exe")):
        if os.path.isfile(cand):
            info["launcher_exe"] = cand
            score += 6
            break
    cfg = os.path.join(d, "XXMI Launcher Config.json")
    if os.path.isfile(cfg):
        info["config_json"] = cfg
        score += 3
    try:
        for name in os.listdir(d):
            if os.path.isfile(os.path.join(d, name, "d3dx.ini")):
                info["importers"].append(name)
    except Exception:
        pass
    if info["importers"]:
        score += 4
    return score, info


def root_scan_candidates():
    cands, seen = [], set()

    def add(p):
        try:
            p = os.path.normpath(p)
        except Exception:
            return
        if p and p not in seen and os.path.isdir(p):
            seen.add(p)
            cands.append(p)

    for letter in string.ascii_uppercase:
        root = letter + ":\\"
        if not os.path.isdir(root):
            continue
        try:
            for name in os.listdir(root):
                if not name.startswith("$"):
                    add(os.path.join(root, name))
        except Exception:
            pass
    home = os.path.expanduser("~")
    for p in (os.path.join(home, "AppData", "Roaming", "XXMI Launcher"),
              os.path.join(home, "AppData", "Local", "XXMI Launcher"),
              os.path.join(home, "XXMI Launcher"),
              os.path.join(home, "Desktop"),
              os.path.join(home, "Downloads"),
              os.path.join(home, "Documents")):
        add(p)
    for letter in string.ascii_uppercase:
        for lib in ("%s:\\SteamLibrary\\steamapps\\common" % letter,
                    "%s:\\STEAM\\steamapps\\common" % letter,
                    "%s:\\Program Files" % letter,
                    "%s:\\Program Files (x86)" % letter):
            if not os.path.isdir(lib):
                continue
            try:
                for name in os.listdir(lib):
                    if re.search(r"xxmi|zzmi|3d ?migoto|mod", name, re.I):
                        add(os.path.join(lib, name))
            except Exception:
                pass
    return cands


def autodetect_config(progress=None):
    hits = []
    cands = root_scan_candidates()
    total = len(cands)
    for i, d in enumerate(cands):
        if progress and i % 20 == 0:
            progress(i, total)
        s, info = score_xxmi_root(d)
        if s >= 8:
            hits.append((s, d, info))
    if progress:
        progress(total, total)
    if not hits:
        return None, []
    hits.sort(key=lambda x: -x[0])
    _, best_dir, info = hits[0]
    importers = info.get("importers") or []
    importer = "ZZMI"
    if importers:
        importer = ([x for x in importers if x.upper() == "ZZMI"]
                    or [x for x in importers if "ZZ" in x.upper()] or importers)[0]
    cfg = dict(DEFAULT_CONFIG)
    cfg["zzmi_root"] = best_dir
    cfg["launcher_exe"] = info.get("launcher_exe", "")
    cfg["importer"] = importer
    cfg["mods_dir"] = os.path.join(best_dir, importer, "Mods")
    cfg["game_exe"] = game_exe_from_launcher_config(info.get("config_json"), importer)
    # v1.5.4: 不再自动探测仓库 —— 仓库由玩家自己添加(新建/自定义文件夹)
    cfg["libraries"] = []
    return cfg, [{"root": d, "importers": hi.get("importers", [])}
                 for _, d, hi in hits[:12]]


def _walk_strings(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            for s in _walk_strings(v):
                yield s
    elif isinstance(obj, list):
        for v in obj:
            for s in _walk_strings(v):
                yield s
    elif isinstance(obj, str):
        yield obj


def game_exe_from_launcher_config(config_json, importer):
    try:
        lj = read_json(config_json or "", {})
        im = (lj.get("Importers") or {}).get(importer) or {}
        gf = im.get("game_folder") or ""
        names = im.get("game_exe_names") or []
        if gf and names:
            exe = os.path.join(gf, names[0])
            if os.path.isfile(exe):
                return exe
        for s in _walk_strings(im):
            s = s.strip().strip('"')
            if not s or not os.path.isdir(s):
                continue
            try:
                files = os.listdir(s)
            except OSError:
                continue
            exes = [f for f in files if f.lower().endswith(".exe")
                    and "crash" not in f.lower() and "uninstall" not in f.lower()]
            if not exes:
                continue
            pref = [f for f in exes if re.search(
                r"zenless|starrail|genshin|wuthering|nap", f, re.I)]
            return os.path.join(s, (pref or exes)[0])
    except Exception:
        pass
    return ""


def _mod_content_stats(p, budget=400):
    n_ini = n_dds = n_ib = 0
    for cur, dirs, files in os.walk(p):
        dirs[:] = [d for d in dirs if d.lower() != "desktop.ini"]
        for f in files:
            low = f.lower()
            if low.endswith(".ini"):
                n_ini += 1
            elif low.endswith(".dds"):
                n_dds += 1
            elif low.endswith(".ib"):
                n_ib += 1
        if n_ini + n_dds + n_ib > budget:
            break
    return n_ini, n_dds, n_ib


def detect_libraries(zzmi_root, mods_dir):
    out = []
    if not os.path.isdir(zzmi_root):
        return out
    mods_abs = os.path.abspath(mods_dir) if mods_dir else ""
    importer_dirs = set()
    try:
        for name in os.listdir(zzmi_root):
            if os.path.isfile(os.path.join(zzmi_root, name, "d3dx.ini")):
                importer_dirs.add(name)
    except Exception:
        pass

    def consider(p, rel, depth):
        if os.path.abspath(p) == mods_abs or depth > 2:
            return
        if any(k in os.path.basename(rel).lower() for k in LIB_NAME_SKIP):
            return
        n_ini, n_dds, n_ib = _mod_content_stats(p)
        if n_ini >= 1 or n_dds >= 20 or n_ib >= 20:
            out.append(rel)

    for imp in sorted(importer_dirs):
        base = os.path.join(zzmi_root, imp)
        try:
            for name in sorted(os.listdir(base)):
                sp = os.path.join(base, name)
                if not os.path.isdir(sp) or name.startswith("."):
                    continue
                if name.lower() in IMPORTER_SKIP:
                    continue
                consider(sp, imp + "/" + name, 2)
        except Exception:
            pass
    try:
        for name in sorted(os.listdir(zzmi_root)):
            sp = os.path.join(zzmi_root, name)
            if not os.path.isdir(sp) or name.startswith("."):
                continue
            if name in importer_dirs or name.lower() in ROOT_SKIP:
                continue
            consider(sp, name, 1)
    except Exception:
        pass
    return out


# ===========================================================================
# 缩略图
# ===========================================================================

_thumb_q = queue.Queue()
_thumb_done = set()
_thumb_lock = threading.Lock()
_PIL = None
_PIL_CHECKED = False


def _get_pil():
    global _PIL, _PIL_CHECKED
    if not _PIL_CHECKED:
        _PIL_CHECKED = True
        try:
            from PIL import Image  # noqa
            _PIL = Image
        except Exception:
            _PIL = None
        log("缩略图引擎:", "Pillow" if _PIL else "无(直接用原图)")
    return _PIL


def thumb_key(src):
    import hashlib
    try:
        st = os.stat(src)
        raw = "%s|%d|%d" % (src.lower(), st.st_size, int(st.st_mtime))
    except OSError:
        raw = src.lower()
    return hashlib.md5(raw.encode("utf-8")).hexdigest()[:20] + ".jpg"


def make_thumb(src, dst, maxpx=THUMB_PX):
    Image = _get_pil()
    if not Image:
        return False
    try:
        # 用 SHARE_DELETE 读取: 我们读图时不会挡住用户改名/搬运
        data = read_bytes_shared(src)
        if not data:
            return False
        with Image.open(io.BytesIO(data)) as im:
            im = im.convert("RGB")
            im.thumbnail((maxpx, maxpx * 2))
            im.save(dst, "JPEG", quality=84)
        return True
    except Exception:
        try:
            if os.path.exists(dst):
                os.remove(dst)
        except OSError:
            pass
        return False


def cached_thumb(src):
    if not src:
        return None
    p = os.path.join(THUMB_DIR, thumb_key(src))
    return p if os.path.isfile(p) else None


def thumb_worker():
    while True:
        src = _thumb_q.get()
        if src is None:
            break
        try:
            if not os.path.isfile(src):
                continue
            dst = os.path.join(THUMB_DIR, thumb_key(src))
            if os.path.isfile(dst):
                continue
            if make_thumb(src, dst):
                with _thumb_lock:
                    _thumb_done.add(src)
        except Exception:
            pass
        finally:
            _thumb_q.task_done()


def enqueue_thumbs(abs_paths):
    os.makedirs(THUMB_DIR, exist_ok=True)
    n = 0
    for p in abs_paths:
        if p in _thumb_done:
            continue
        if os.path.isfile(os.path.join(THUMB_DIR, thumb_key(p))):
            with _thumb_lock:
                _thumb_done.add(p)
            continue
        _thumb_q.put(p)
        n += 1
    return n


# ===========================================================================
# 扫描
# ===========================================================================

class ScanResult(object):
    def __init__(self):
        self.root = ""
        self.entries = []
        self.by_id = {}
        self.categories = []
        self.chars = []
        self.stats = {"total": 0, "enabled": 0, "disabled": 0, "size": 0,
                      "size_h": "0 B", "files": 0, "conflicts": 0, "partial": 0,
                      "chars": 0, "multi_chars": 0}
        self.conflicts = []
        self.thumb_srcs = []
        self.scanned_at = 0
        self.duration = 0


def find_mods_dir(cfg):
    md = cfg.get("mods_dir") or ""
    if md and os.path.isdir(md):
        return md
    root = cfg.get("zzmi_root") or ""
    imp = cfg.get("importer") or "ZZMI"
    cand = os.path.join(root, imp, "Mods")
    if os.path.isdir(cand):
        return cand
    try:
        for name in os.listdir(root):
            sub = os.path.join(root, name, "Mods")
            if os.path.isdir(sub):
                return sub
    except Exception:
        pass
    return md or ""


def scan_mods(mods_dir, char_overrides=None, thumb_overrides=None, meta=None):
    # meta: {"pinned_mods":[], "pinned_cats":[], "pinned_chars":[], "usage":{路径:秒}}
    char_overrides = char_overrides or {}
    thumb_overrides = thumb_overrides or {}
    meta = meta or {}
    pm = set(meta.get("pinned_mods") or [])
    pc = set(meta.get("pinned_cats") or [])
    pch = set(meta.get("pinned_chars") or [])
    usage = meta.get("usage") or {}
    t0 = time.time()
    res = ScanResult()
    res.root = mods_dir
    if not os.path.isdir(mods_dir):
        res.duration = time.time() - t0
        return res

    dir_info = {}
    ini_dirs = []
    total_files = total_size = 0

    for cur, dirs, files in os.walk(mods_dir):
        dirs[:] = [d for d in dirs if d.lower() != "desktop.ini"]
        rel = os.path.relpath(cur, mods_dir)
        rel = "" if rel == "." else rel
        parts = rel.split(os.sep) if rel else []
        local_ini = [f for f in files if f.lower().endswith(".ini")]
        # 注意: .dds 明确排除(见 NEVER_IMAGE_EXTS), 免得封面选到模型/贴图文件
        imgs = [f for f in files
                if f.lower().endswith(IMAGE_EXTS)
                and not f.lower().endswith(NEVER_IMAGE_EXTS)]
        sz = 0
        for f in files:
            try:
                sz += os.path.getsize(os.path.join(cur, f))
            except OSError:
                pass
        total_files += len(files)
        total_size += sz
        try:
            mt = os.path.getmtime(cur)
        except OSError:
            mt = 0
        dir_info[cur] = {
            "rel": rel, "name": os.path.basename(cur), "parts": parts,
            "depth": len(parts), "size": sz, "files": len(files), "mtime": mt,
            "ini": local_ini, "imgs": imgs,
            "disabled": any(is_disabled_name(p) for p in parts),
        }
        if local_ini:
            ini_dirs.append(cur)

    if not ini_dirs:
        res.stats = {"total": 0, "enabled": 0, "disabled": 0, "partial": 0,
                     "chars": 0, "multi_chars": 0, "size": total_size,
                     "size_h": human_size(total_size), "files": total_files,
                     "conflicts": 0}
        res.duration = time.time() - t0
        return res

    def mod_root_for(d):
        """从「含 ini 的目录」往上归并出这个 mod 的根目录。

        层级判定:
          * ini 直接散落在 Mods 根目录   -> 就是 Mods 根自己(单独一条)
          * 第 1 层是分类文件夹          -> mod 在第 2 层(更深的一律收到第 2 层)
          * 第 1 层自己就是 mod(直接放根) -> mod 就是第 1 层, 不再往里钻
        """
        parts = dir_info[d]["parts"]
        if not parts:
            return d                  # ini 散落在 Mods 根目录
        if len(parts) == 1:
            return d                  # mod 直接放在 Mods 根下
        top = os.path.join(mods_dir, parts[0])
        # 第 2 层看着像 mod 内部的资源目录(resources/贴图/body…) -> 第 1 层才是 mod
        if looks_like_inner_dir(parts[1]):
            return top
        # 第 1 层下面挂着多个含 ini 的分支 -> 它一定是分类文件夹
        if len(branch_count.get(parts[0], ())) >= 2:
            return os.path.join(mods_dir, parts[0], parts[1])
        # 只有一个分支: 名字像分类才是分类, 否则第 1 层自己就是那个 mod
        if is_classifier_dir(parts[0], strong=True):
            return os.path.join(mods_dir, parts[0], parts[1])
        return top                    # 第 1 层不是分类, 那它本身就是个 mod

    def is_ancestor(a, b):
        a, b = os.path.abspath(a), os.path.abspath(b)
        return b != a and b.startswith(a + os.sep)

    # 每个「第 1 层目录」下面挂着几个含 ini 的分支 —— 用来判断它是分类还是单个 mod
    branch_count = {}
    for d in ini_dirs:
        ps = dir_info[d]["parts"]
        if not ps:
            continue
        branch_count.setdefault(ps[0], set()).add(ps[1] if len(ps) > 1 else "")

    cand = {}
    for d in ini_dirs:
        cand.setdefault(mod_root_for(d), []).append(d)

    # 「ini 直接散落在 Mods 根」这条只代表根目录自己的那几个 ini。
    # 它的路径是所有 mod 的父目录, 若混进去做"祖先去重"会把其它 mod 全吞掉,
    # 所以先给普通 mod 去重, 再把散装这条单独放回去。
    def _is_mods_root(p):
        return os.path.abspath(p) == os.path.abspath(mods_dir)

    kept = []
    for r in sorted((p for p in cand if not _is_mods_root(p)),
                    key=lambda p: dir_info[p]["depth"]):
        if not any(is_ancestor(k, r) for k in kept):
            kept.append(r)
    if any(_is_mods_root(p) for p in cand):
        kept.append(mods_dir)

    roots = {k: [d for d in ini_dirs
             if os.path.abspath(d) == os.path.abspath(k)
             or (not _is_mods_root(k) and is_ancestor(k, d))]
             for k in kept}

    hashes_by_dir = collect_hashes(ini_dirs, dir_info)

    entries = []
    for root_abs, sub_inis in roots.items():
        info = dir_info[root_abs]
        parts = info["parts"]

        def in_sub(k, _r=root_abs):
            return k == _r or k.startswith(_r + os.sep)

        sub_size = sum(v["size"] for k, v in dir_info.items() if in_sub(k))
        sub_files = sum(v["files"] for k, v in dir_info.items() if in_sub(k))
        sub_ini = sum(len(v["ini"]) for k, v in dir_info.items() if in_sub(k))
        hs = set()
        sub_dirs = []
        for k, v in dir_info.items():
            if not in_sub(k):
                continue
            hs |= hashes_by_dir.get(k, set())
            if k == root_abs:
                continue
            sub_dirs.append({
                "rel": norm_rel(os.path.relpath(k, mods_dir)),
                "local": norm_rel(os.path.relpath(k, root_abs)),
                "disabled": v["disabled"], "ini": len(v["ini"]),
                "imgs": len(v["imgs"]), "files": v["files"],
            })
        sub_dirs.sort(key=lambda s: s["local"].lower())

        if parts:
            logical = [strip_disabled(p) for p in parts]
            name = parts[-1]
            cid = "/".join(logical)
            cat = parts[0] if len(parts) > 1 else "(根目录)"
        else:
            # ini 直接散落在 Mods 根目录(没有子文件夹) —— 合成一条, 别让下标越界
            logical = []
            name = ROOT_MOD_NAME
            cid = ROOT_MOD_ID
            cat = "(根目录)"
        char_auto = auto_char(name)
        char = (char_overrides.get(cid) or char_overrides.get(norm_rel(info["rel"]))
                or char_auto)
        # 用户手动指定过封面(切换预览图 / 一键添加预览图)就优先用它, 失效则回退自动挑
        thumb_rel = None
        for _key in (cid, norm_rel(info["rel"])):
            _cand = thumb_overrides.get(_key)
            if _cand and os.path.isfile(os.path.join(mods_dir, _cand.replace("/", os.sep))):
                thumb_rel = norm_rel(_cand)
                break
        if not thumb_rel:
            thumb_rel = pick_preview(root_abs, dir_info, sub_inis, mods_dir)

        entries.append({
            "id": cid,
            "name": name,
            "char": char,
            "char_auto": char_auto,
            "char_manual": bool(cid in char_overrides
                                or norm_rel(info["rel"]) in char_overrides),
            "path": norm_rel(info["rel"]),
            "category": cat,
            "depth": len(parts),
            "enabled": not info["disabled"],
            # 收藏: mod 自身 / 所属分类 / 所属角色 任一被置顶, 这张卡就算置顶
            "pinned": (cid in pm or norm_rel(info["rel"]) in pm
                       or cat in pc or char in pch),
            # 使用时间: 每次启用/切变体记录一次, 没有记录回退用目录修改时间
            "usage": usage.get(cid) or usage.get(norm_rel(info["rel"])) or info["mtime"],
            "dir_disabled": info["disabled"],
            "partial": bool(not info["disabled"]
                            and any(s["disabled"] for s in sub_dirs)),
            "ini_count": sub_ini,
            "ini_roots": [norm_rel(os.path.relpath(p, mods_dir)) for p in sub_inis],
            "sub_dirs": sub_dirs[:200],
            "files": sub_files, "size": sub_size, "size_h": human_size(sub_size),
            "mtime": info["mtime"], "mtime_h": human_time(info["mtime"]),
            "thumb": thumb_rel,
            "backup_inis": find_backup_inis(sub_inis, dir_info),
            "hashes": sorted(hs),
        })
        if thumb_rel:
            ap = os.path.join(mods_dir, thumb_rel.replace("/", os.sep))
            if os.path.isfile(ap):
                res.thumb_srcs.append(ap)

    # 默认顺序: 收藏置顶最前, 其次已启用, 同组内按使用时间从新到旧
    # (usage 没记录时回退为目录 mtime, 见上面 usage 字段)
    entries.sort(key=lambda e: (not e["pinned"], not e["enabled"],
                                -e["usage"], e["char"].lower(),
                                e["name"].lower()))
    used = {}
    for e in entries:
        k = e["id"]
        if k in used:
            used[k] += 1
            e["id"] = "%s#%d" % (k, used[k])
        else:
            used[k] = 0

    res.entries = entries
    res.by_id = {e["id"]: e for e in entries}
    res.conflicts = detect_conflicts(entries)

    cats = {}
    for e in entries:
        cats.setdefault(e["category"], {}).setdefault(e["char"], []).append(e)
    cat_list = []
    # 收藏的分类置顶, 其余按名字; 组内同理(收藏的角色排在该分类最前)
    for cname in sorted(cats, key=lambda s: (s not in pc, s.lower())):
        groups = cats[cname]
        glist = []
        for gname in sorted(groups, key=lambda s: (s not in pch, s.lower())):
            items = groups[gname]
            glist.append({"name": gname, "count": len(items),
                          "enabled": sum(1 for i in items if i["enabled"]),
                          "partial": sum(1 for i in items if i["partial"]),
                          "pinned": gname in pch})
        allitems = [i for g in groups.values() for i in g]
        cat_list.append({"name": cname, "count": len(allitems),
                         "enabled": sum(1 for i in allitems if i["enabled"]),
                         "partial": sum(1 for i in allitems if i["partial"]),
                         "pinned": cname in pc,
                         "groups": glist})
    res.categories = cat_list

    ch = {}
    for e in entries:
        ch.setdefault(e["char"], []).append(e)
    res.chars = [{"name": c, "count": len(v),
                  "enabled": sum(1 for i in v if i["enabled"]),
                  "pinned": c in pch,
                  "multi": len(v) > 1}
                 for c, v in sorted(ch.items(),
                                    key=lambda kv: (kv[0] not in pch,
                                                    kv[0].lower()))]

    res.stats = {
        "total": len(entries),
        "enabled": sum(1 for e in entries if e["enabled"]),
        "disabled": sum(1 for e in entries if not e["enabled"]),
        "pinned": sum(1 for e in entries if e["pinned"]),
        "partial": sum(1 for e in entries if e["partial"]),
        "chars": len(res.chars),
        "multi_chars": sum(1 for c in res.chars if c["multi"]),
        "size": total_size, "size_h": human_size(total_size), "files": total_files,
        "conflicts": len(res.conflicts),
    }
    res.scanned_at = time.time()
    res.duration = res.scanned_at - t0
    return res


def _img_rank(stem):
    """给预览图打分: 越小越优先做封面。"""
    # 0) 用户自己放进来的封面(「一键添加预览图」写的 zzmi_cover.*)永远排第一
    if stem.startswith(COVER_STEM):
        return -1
    # 1) 明确的预览/封面类关键词(含中英文) —— 最优先, 且能命中深层样本图
    for w in PREVIEW_PRIORITY:
        if stem == w or stem.startswith(w):
            return 0
    # 2) 说明/帮助类 —— 排除, 不参与封面
    if any(h in stem for h in ("help", "readme", "说明", "使用", "教程",
                               "按键", "菜单", "操作", "guide", "tutorial")):
        return 80
    # 3) 截图
    if any(h in stem for h in ("screenshot", "截图", "screen")):
        return 10
    if stem == "default" or stem.startswith("default"):
        return 20
    # "1"/"0" 常被用作贴图分页名, 不一定是预览, 优先级放低
    if stem in ("1", "0"):
        return 30
    return 40


def iter_mod_images(abs_root, limit=MAX_CANDIDATE_IMAGES):
    """列出这个 mod 文件夹里所有能当封面的图片(递归; 明确排除 .dds 等非图片),
    按「更适合做封面」的顺序排列, 供界面里「切换预览图」挑选。
    返回 [{rel, name, size, size_h, manual}] —— rel 相对 mod 文件夹。"""
    out = []
    if not os.path.isdir(abs_root):
        return out
    for cur, dirs, files in os.walk(abs_root):
        dirs[:] = [d for d in dirs if d.lower() != "desktop.ini"]
        for f in files:
            low = f.lower()
            if low.endswith(NEVER_IMAGE_EXTS) or not low.endswith(IMAGE_EXTS):
                continue
            fp = os.path.join(cur, f)
            try:
                sz = os.path.getsize(fp)
            except OSError:
                continue
            out.append({"rel": norm_rel(os.path.relpath(fp, abs_root)),
                        "name": f, "size": sz, "size_h": human_size(sz),
                        "manual": low.startswith(COVER_STEM)})
    out.sort(key=lambda x: (_img_rank(os.path.splitext(x["name"])[0].lower()),
                            -x["size"], x["rel"].lower()))
    return out[:limit]


def write_mod_cover(abs_root, filename, data):
    """「一键添加预览图」: 把用户选的照片写进 mod 文件夹根部, 命名 zzmi_cover.<ext>。

    只写我们自己的 zzmi_cover.* (写之前先把旧的同名文件删掉), **从不碰用户原有的
    图片和 ini**。返回 (相对文件名, 错误信息)。"""
    ext = os.path.splitext(filename or "")[1].lower()
    if ext not in IMAGE_EXTS:
        return None, "只支持这些格式: " + " / ".join(IMAGE_EXTS)
    if not data:
        return None, "图片是空的"
    if len(data) > 25 * 1024 * 1024:
        return None, "图片太大(超过 25MB), 请先压缩一下"
    if not os.path.isdir(abs_root):
        return None, "mod 文件夹不存在"
    for f in os.listdir(abs_root):
        p = os.path.join(abs_root, f)
        if f.lower().startswith(COVER_STEM) and os.path.isfile(p):
            try:
                os.remove(p)          # 这是本工具上一次生成的封面, 不是用户的文件
            except OSError:
                pass
    dst = os.path.join(abs_root, COVER_STEM + ext)
    try:
        with open(dst, "wb") as fh:
            fh.write(data)
    except OSError as ex:
        return None, "写入失败: %s" % ex
    return COVER_STEM + ext, ""


def pick_preview(root_abs, dir_info, sub_inis, rel_base):
    """在 mod 子树(含所有层级, 不限第几层)里挑一张最适合做封面的图。

    排序优先级:
      1) 关键词优先级最高(preview/cover/预览/示例 等);
      2) 同档时优先体积大的(更可能是作者放的真预览, 而非几 KB 的占位/图标);
      3) 层级深度只作为最后的兜底, 不再惩罚深层文件夹 —— 这样第 2、3 层
         里作者放的样本图也能被正确读到。"""
    best = None
    for k, v in dir_info.items():
        if k != root_abs and not k.startswith(root_abs + os.sep):
            continue
        depth = v.get("depth", 0)
        for f in v["imgs"]:
            try:
                size = os.path.getsize(os.path.join(k, f))
            except OSError:
                continue
            if size > 12 * 1024 * 1024:
                continue
            stem = os.path.splitext(f)[0].lower()
            rank = _img_rank(stem)
            # rank 越小越优先; 同 rank 体积大优先(更可能是真预览); 最后才看层级
            key = (rank, -size, depth, f)
            if best is None or key < best[0]:
                best = (key, norm_rel(os.path.relpath(os.path.join(k, f), rel_base)))
    if best and best[0][0] < 80:
        return best[1]
    return None


def find_backup_inis(sub_inis, dir_info):
    out = []
    for d in sub_inis:
        for f in dir_info.get(d, {}).get("ini", []):
            if is_disabled_name(f):
                out.append(f)
    return out[:20]


HASH_RE = re.compile(r"^\s*hash\s*=\s*([0-9a-fA-F]{6,16})\s*$", re.M)
SEC_RE = re.compile(r"^\[([^\]\r\n]+)\]")
REPLACE_HINT = re.compile(
    r"^\s*(vb0|vb1|vb2|ib|draw|drawindexed|match_first_index|"
    r"Resource\\ZZMI\\|ps-t0|run\s*=\s*CommandList)", re.M | re.I)
BACKUP_RE = re.compile(r"(?:backup|beifen|\.bak\b|_bak)", re.IGNORECASE)


def _ini_overrides(txt):
    """解析 ini 文本, 返回真正覆盖游戏资源的 TextureOverride hash 集合。"""
    hs = set()
    for block in re.split(r"(?m)^(?=\[)", txt):
        m = SEC_RE.match(block.strip())
        if not m or not m.group(1).lower().startswith("textureoverride"):
            continue
        hm = HASH_RE.search(block)
        if hm and REPLACE_HINT.search(block[hm.end():]):
            hs.add(hm.group(1).lower())
    return hs


def collect_hashes(ini_dirs, dir_info):
    out = {}
    for d in ini_dirs:
        hs = set()
        for f in dir_info.get(d, {}).get("ini", []):
            if is_disabled_name(f):
                continue
            p = os.path.join(d, f)
            try:
                if os.path.getsize(p) > 4 * 1024 * 1024:
                    continue
                with open(p, "r", encoding="utf-8", errors="replace") as fh:
                    hs |= _ini_overrides(fh.read())
            except Exception:
                continue
        out[d] = hs
    return out


def detect_conflicts(entries):
    idmap = {e["id"]: e for e in entries}
    h2m = {}
    for e in entries:
        if not e["enabled"]:
            continue
        for h in e["hashes"]:
            h2m.setdefault(h, []).append(e["id"])
    pairs = {}
    for h, ids in h2m.items():
        ids = sorted(set(ids))
        if len(ids) < 2:
            continue
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                pairs.setdefault((ids[i], ids[j]), []).append(h)
    out = []
    for (ia, ib), hs in pairs.items():
        a, b = idmap.get(ia), idmap.get(ib)
        if not a or not b:
            continue
        out.append({"a": ia, "b": ib, "a_name": a["name"], "b_name": b["name"],
                    "a_char": a["char"], "b_char": b["char"], "n": len(hs),
                    "hashes": sorted(hs)[:8],
                    "same_char": a["char"] == b["char"]})
    out.sort(key=lambda c: (not c["same_char"], -c["n"]))
    return out[:300]


# ===========================================================================
# 部件 / 变体分析
# ===========================================================================

def _walk_inis(abs_root):
    out = []
    for cur, dirs, files in os.walk(abs_root):
        dirs[:] = [d for d in dirs if d.lower() != "desktop.ini"]
        rel = os.path.relpath(cur, abs_root)
        rel = "" if rel == "." else rel
        for f in files:
            if f.lower().endswith(".ini"):
                out.append((os.path.join(cur, f), norm_rel(os.path.join(rel, f))))
    return sorted(out, key=lambda t: t[1].lower())


def resolve_component_file(abs_root, rel):
    """按相对路径找 mod 内的文件; 允许任意一段(目录或文件)带 DISABLED 前缀。"""
    rel = norm_rel(rel)
    if not rel:
        return None
    p = os.path.join(abs_root, rel.replace("/", os.sep))
    if os.path.isfile(p):
        return p
    cur = abs_root
    parts = [x for x in rel.split("/") if x]
    for part in parts:
        try:
            names = os.listdir(cur)
        except OSError:
            return None
        hit = None
        if part in names:
            hit = part
        else:
            for n in names:
                if strip_disabled(n) == strip_disabled(part):
                    hit = n
                    break
        if hit is None:
            return None
        cur = os.path.join(cur, hit)
    return cur if os.path.isfile(cur) else None


def analyze_components(abs_root):
    """解析 mod 内每个 ini 的覆盖目标, 把「覆盖同一游戏资源」的文件自动归为变体组。

    返回 {"components": [{rel,name,enabled,backup,group,n_hashes,size}],
          "groups":     [{id,label,files,active,n_hashes}]}
    备份副本(DISABLED_BACKUP_* / disabled_beifen_* 之类)不参与分组, 只做展示。
    """
    comps = []
    hmap = {}
    for full, rel in _walk_inis(abs_root):
        name = os.path.basename(full)
        disabled = is_disabled_name(name)
        backup = disabled and bool(BACKUP_RE.search(name))
        hashes = set()
        if not backup:
            try:
                if os.path.getsize(full) <= 4 * 1024 * 1024:
                    with open(full, "r", encoding="utf-8", errors="replace") as fh:
                        hashes = _ini_overrides(fh.read())
            except Exception:
                hashes = set()
        hmap[len(comps)] = hashes
        comps.append({"rel": rel, "name": name, "enabled": not disabled,
                      "backup": backup, "group": None,
                      "n_hashes": len(hashes), "hashes": sorted(hashes),
                      "size": _size(full)})

    # 并查集: 共享任一 hash 的文件归为一组
    parent = list(range(len(comps)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    hash2idx = {}
    for i, hs in hmap.items():
        for h in hs:
            if h in hash2idx:
                ra, rb = find(hash2idx[h]), find(i)
                if ra != rb:
                    parent[rb] = ra
            else:
                hash2idx[h] = i

    clusters = {}
    for i in range(len(comps)):
        clusters.setdefault(find(i), []).append(i)

    groups = []
    gid = 0
    for members in clusters.values():
        if len(members) < 2:
            continue
        gid += 1
        g = {"id": "g%d" % gid, "files": [], "active": None, "n_hashes": 0}
        allh = set()
        names = []
        for i in sorted(members, key=lambda x:
                        (not comps[x]["enabled"], comps[x]["rel"].lower())):
            comps[i]["group"] = g["id"]
            g["files"].append(comps[i]["rel"])
            allh |= hmap[i]
            if comps[i]["enabled"] and g["active"] is None:
                g["active"] = comps[i]["rel"]
            names.append(strip_disabled(os.path.splitext(comps[i]["name"])[0]))
        g["n_hashes"] = len(allh)
        # 组名: 跳过 hash 文件夹(如 0f82a13e), 向上取有意义目录名; 退化用公共前缀
        def _meaningful(rel):
            parts = rel.replace("/", os.sep).split(os.sep)[:-1]  # 去掉文件名
            for f in reversed(parts):
                b = strip_disabled(f)
                if re.fullmatch(r"[0-9a-fA-F]{6,}", b):
                    continue  # hash 文件夹, 跳过
                if b:
                    return b
            return ""
        folders = {}
        for i in members:
            m = _meaningful(comps[i]["rel"])
            if m:
                folders[m] = folders.get(m, 0) + 1
        pre = os.path.commonprefix(names).strip(" -_")
        label = ""
        if folders:
            top = max(folders.values())
            if top >= 2 or len(folders) == 1:
                label = [k for k, v in folders.items() if v == top][0]
        label = label or (pre if len(pre) >= 2 else "")
        if re.fullmatch(r"[0-9a-fA-F]{6,}", label.strip()):
            label = ""  # hash 文件夹名无意义, 退回通用名
        g["label"] = (label or "变体组").strip() or "变体组"
        groups.append(g)
    # 去重: 同组名加序号, 避免单选按钮标题重名(如两个 hash 文件夹同名)
    seen = {}
    for g in groups:
        l = g["label"]
        if l in seen:
            seen[l] += 1
            g["label"] = "%s #%d" % (l, seen[l])
        else:
            seen[l] = 1
    return {"components": comps, "groups": groups}


# ===========================================================================
# 写操作 (全部写 journal, 可撤销)
# ===========================================================================

_jlock = threading.Lock()


def journal_append(rec):
    with _jlock:
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            rec["ts"] = time.time()
            with open(JOURNAL_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except Exception:
            pass


def journal_read(limit=500):
    out = []
    try:
        with open(JOURNAL_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        out.append(json.loads(line))
                    except Exception:
                        pass
    except FileNotFoundError:
        return []
    except Exception:
        return out
    return out[-limit:]


def _rename_dir(src, dst, rec, tries=3):
    """重命名目录(启用/禁用/改名都走这里)。
    被占用时自动重试几次(占用往往是杀软/缩略图线程几十毫秒的事),
    仍失败就用 lock_reason 告诉你到底是谁挡着。"""
    if os.path.exists(dst):
        return False, "目标名已存在: %s" % os.path.basename(dst)
    last = None
    for i in range(max(1, tries)):
        try:
            os.rename(src, dst)
            journal_append(rec)
            return True, "ok"
        except OSError as ex:
            last = ex
            ok, why = lock_reason(src, scan_files=10)
            if not ok and i >= 1:
                return False, ("重命名失败 —— %s。\n"
                               "把游戏 / 资源管理器窗口关掉(或稍等两秒)再点一次即可。"
                               % why)
            time.sleep(0.12 * (i + 1))
    ok, why = lock_reason(src, scan_files=10)
    if not ok:
        return False, ("重命名失败 —— %s。\n"
                       "把游戏 / 资源管理器窗口关掉(或稍等两秒)再点一次即可。" % why)
    msg = str(last or "")
    if "另一个程序正在使用" in msg or "being used by another" in msg:
        msg = "文件被占用(游戏或资源管理器开着这个目录), 先关掉再试。"
    return False, "重命名失败: %s" % msg


def toggle_root_ini_files(mods_dir, enable):
    """启用/禁用「直接散落在 Mods 根目录里」的 ini —— 没有子文件夹可改名,
    所以改成逐个 ini 加/去 DISABLED_ 前缀。只改文件名, 不删任何文件。"""
    try:
        names = sorted(os.listdir(mods_dir))
    except OSError as ex:
        return False, "读不了 Mods 目录: %s" % ex
    inis = [n for n in names
            if n.lower().endswith(".ini") and n.lower() != "desktop.ini"
            and os.path.isfile(os.path.join(mods_dir, n))]
    if not inis:
        return False, "Mods 根目录里已经没有 ini 了"
    done, errs = 0, []
    for n in inis:
        base = strip_disabled(n)
        new = base if enable else (DISABLED_PREFIX + base)
        if new == n:
            continue
        src, dst = os.path.join(mods_dir, n), os.path.join(mods_dir, new)
        # v1.5.8: 根目录里同名 ini 也自动加后缀(unique_path 会保住 .ini 扩展名)
        if os.path.exists(dst):
            uniq = unique_path(dst)
            if not uniq:
                errs.append("%s: 同名太多, 先清理一下" % n)
                continue
            dst = uniq
        try:
            os.rename(src, dst)
            journal_append({"kind": "toggle_file", "src": src, "dst": dst,
                            "enable": bool(enable), "id": ROOT_MOD_ID,
                            "name": n})
            done += 1
        except OSError as ex:
            errs.append("%s: %s" % (n, ex))
    if done:
        msg = "已%s根目录的 %d 个 ini" % ("启用" if enable else "禁用", done)
        if errs:
            msg += " · %d 个没成: %s" % (len(errs), errs[0])
        return True, msg
    if errs:
        return False, errs[0]
    return True, "已经是目标状态了"


def do_toggle(mods_dir, entry, enable):
    # 散落在 Mods 根目录的 ini 没有目录可改名 -> 走 ini 级启停
    if not (entry.get("path") or "").strip():
        return toggle_root_ini_files(mods_dir, enable)
    cur = entry_root(mods_dir, entry)
    if not cur or not os.path.isdir(cur):
        return False, "找不到目录(可能已被移动)"
    name = os.path.basename(cur)
    disabled = is_disabled_name(name)
    if enable and not disabled:
        return True, "已是启用状态"
    if (not enable) and disabled:
        return True, "已是禁用状态"
    base = strip_disabled(name)
    new = base if enable else (DISABLED_PREFIX + base)
    if new == name:
        return False, "名字已经是目标状态"
    dst = os.path.join(os.path.dirname(cur), new)
    # v1.5.8: 同名的另一套还躺在同目录里(比如「露西皮肤」和「DISABLED_露西皮肤」),
    # 直接改名会撞车。不报错, 自动加 (2) (3)… 并把最终名字交回前端提示玩家。
    dst, seq = auto_unique_name(dst)
    if not dst:
        return False, "同名太多(已排到 200), 先去清理一下重复的 mod"
    target = os.path.basename(dst)
    renamed = seq is not None
    ok, msg = _rename_dir(cur, dst, {"kind": "toggle", "src": cur, "dst": dst,
                                     "enable": bool(enable), "id": entry["id"],
                                     "name": entry["name"]})
    if ok:
        out = "已%s" % ("启用" if enable else "禁用")
        if renamed:
            out += " —— 因为「%s」已被占用, 自动改名为「%s」" % (
                base if enable else DISABLED_PREFIX + base, target)
        return True, out, {"dir": os.path.dirname(cur), "cur": dst,
                           "want": dst, "target_name": target,
                           "enable": bool(enable), "renamed": renamed,
                           "orig_name": base if enable else DISABLED_PREFIX + base,
                           "seq": seq}
    return False, msg, {"dir": os.path.dirname(cur), "cur": cur, "want": dst,
                        "target_name": target, "enable": bool(enable)}


def do_toggle_dir(mods_dir, rel, enable):
    p = resolve_rel_dir(mods_dir, rel)
    if not p or not os.path.isdir(p):
        return False, "目录不存在"
    if os.path.abspath(p) == os.path.abspath(mods_dir):
        return False, "不能操作 Mods 根目录"
    name = os.path.basename(p)
    disabled = is_disabled_name(name)
    if enable == (not disabled):
        return True, "状态没变"
    base = strip_disabled(name)
    new = base if enable else (DISABLED_PREFIX + base)
    if new == name:
        return False, "名字已经是目标状态"
    dst = os.path.join(os.path.dirname(p), new)
    # v1.5.8: 子目录重名同样自动加 (2) (3)…
    dst, seq = auto_unique_name(dst)
    if not dst:
        return False, "同名太多(已排到 200), 先清理一下重复的目录"
    target = os.path.basename(dst)
    ok, msg = _rename_dir(p, dst, {"kind": "toggle", "src": p, "dst": dst,
                                   "enable": bool(enable), "id": rel, "name": name})
    if ok:
        out = "已%s %s" % ("启用" if enable else "禁用", target)
        if seq is not None:
            out += "（因重名自动加 (%d)）" % seq
        return True, out, {"renamed": seq is not None, "orig_name": new,
                           "target_name": target, "seq": seq,
                           "enable": bool(enable)}
    return False, msg


def do_toggle_file(abs_root, rel, enable):
    """mod 内单个 ini 文件的启停: 文件名加/去 DISABLED_ 前缀, 永不删除。"""
    p = resolve_component_file(abs_root, rel)
    if not p or not os.path.isfile(p):
        return False, "找不到文件: %s" % rel
    if os.path.abspath(p) == os.path.abspath(abs_root):
        return False, "路径不合法"
    name = os.path.basename(p)
    disabled = is_disabled_name(name)
    if enable and not disabled:
        return True, "已是启用状态"
    if (not enable) and disabled:
        return True, "已是禁用状态"
    base = strip_disabled(name)
    new = base if enable else (DISABLED_PREFIX + base)
    dst = os.path.join(os.path.dirname(p), new)
    # v1.5.8: 单个 ini 重名也自动加 (2) (3)…(注意 ini 要保住 .ini 后缀, 所以用 unique_path)
    renamed = False
    if os.path.exists(dst):
        uniq = unique_path(dst)
        if not uniq:
            return False, "同名太多, 先清理一下重复的 ini"
        dst, renamed = uniq, True
    try:
        os.rename(p, dst)
    except OSError as ex:
        msg = str(ex)
        if "另一个程序正在使用" in msg or "being used by another" in msg:
            msg = "文件被占用(游戏正在用它), 先关游戏或稍后再试。"
        return False, "重命名失败: %s" % msg
    journal_append({"kind": "file_toggle", "src": p, "dst": dst,
                    "enable": bool(enable), "id": rel, "name": name})
    got = os.path.basename(dst)
    out = "已%s %s" % ("启用" if enable else "禁用", got)
    if renamed:
        out += "（因重名自动加了后缀）"
    return True, out


def do_variant_select(abs_root, rel):
    """一键切换变体: 启用指定文件, 并禁用同组里其它已启用的文件。"""
    comp = analyze_components(abs_root)
    tgt = None
    for c in comp["components"]:
        if c["rel"] == rel or strip_disabled(c["rel"]) == strip_disabled(rel):
            tgt = c
            break
    if tgt is None:
        return False, "找不到这个部件"
    # 只处理与目标有直接 hash 冲突的同组成员(避免传递闭包把不相关文件一起关掉)
    ths = set(tgt.get("hashes") or [])
    members = [c for c in comp["components"]
               if c is not tgt and c.get("group") == tgt.get("group")
               and c.get("group") and (ths & set(c.get("hashes") or []))]
    members.append(tgt)
    n = 0
    last_msg = ""
    for m in members:
        want = m["rel"] == tgt["rel"]
        if want == m["enabled"]:
            continue
        good, msg = do_toggle_file(abs_root, m["rel"], want)
        last_msg = msg
        if good:
            n += 1
        else:
            return False, "切换中断: %s" % msg
    if n == 0:
        return True, "这个变体已经在用了"
    return True, "已切换到「%s」(变更 %d 项)%s" % (
        strip_disabled(tgt["name"]), n,
        "" if not last_msg or "已" in last_msg else "; " + last_msg)


# ---------------------------------------------------------------------------
# 热键循环变体: [Key*] 段里 `$var = 0,1,2` + `type = cycle`,
# 游戏内按绑定键循环取值。初始值 = 列表第一个值, 所以把列表旋转即可持久换变体。
# ---------------------------------------------------------------------------

# 取值列表后允许行内注释 (; 或 #), group(2) 只取数字列表
CYCLE_DECL_RE = re.compile(r"^\$(\w+)\s*=\s*([0-9][0-9\s,]*)(?:\s*[;#].*)?$")
CYCLE_EXPR_RE = re.compile(r"^\$(\w+)\s*=\s*([^=\r\n]+)$")
KEYSEC_RE = re.compile(r"^key", re.I)
INI_BACKUP_DIR = os.path.join(DATA_DIR, "ini_backups")


def _ini_section(st):
    """ini 段头行 -> 段名; 不是段头返回 None。
    3DMigoto 允许 ] 后面跟备注(如 [KeySwap0]后裙摆), 所以只要求
    以 [ 开头且行内含 ], 段名取到第一个 ] 为止。"""
    if not st.startswith("["):
        return None
    close = st.find("]")
    if close < 0:
        return None
    return st[1:close].strip()

# 变体变量名 -> 中文提示 (小写匹配; 匹配不到就显示原名)
CYCLE_LABEL_CN = {
    "upper": "上装", "lower": "下装", "top": "上衣", "bottom": "下装",
    "bottoms": "下装", "pubic": "私处", "tt": "透视", "skirt": "裙子",
    "bra": "内衣", "panties": "内裤", "thong": "丁字裤", "stockings": "长袜",
    "socks": "袜子", "thighhighs": "过膝袜", "thighstrap": "腿带",
    "gloves": "手套", "glasses": "眼镜", "hair": "头发", "haircolour": "发色",
    "haircolor": "发色", "face": "脸型", "tail": "尾巴", "ears": "耳朵",
    "horns": "角", "wings": "翅膀", "collar": "项圈", "choker": "颈饰",
    "hat": "帽子", "mask": "面具", "shoes": "鞋子", "shoescolour": "鞋色",
    "heels": "高跟鞋", "jacket": "外套", "jacketcolour": "外套色",
    "coat": "大衣", "underwear": "内衣", "leotard": "连体衣",
    "bikinitop": "比基尼上装", "bikinibottom": "比基尼下装",
    "nipplepasties": "乳贴", "nipples": "乳贴", "skin": "肤色",
    "skintone": "肤色", "bodypaint": "身体彩绘", "bodypaintcolor": "彩绘颜色",
    "makeup": "妆容", "lace": "蕾丝", "bows": "蝴蝶结", "bow": "蝴蝶结",
    "straps": "吊带", "garter": "吊袜带", "garters": "吊袜带",
    "garterscolour": "袜带色", "tan": "美黑", "piercings": "穿孔",
    "naked": "全裸", "alt": "备用款式", "furarm": "毛袖", "furchest": "毛胸",
    "furleg": "毛腿", "furhip": "毛臀", "furneck": "毛领", "glow": "发光",
    "health": "战损效果", "acces": "饰品", "earrings": "耳环",
    "necklace": "项链", "bracelet": "手环", "wristbangle": "手镯",
    "bangs": "刘海", "topcolour": "上衣色", "topcolor": "上衣色",
    "bottomscolour": "下装色", "stockingcolour": "长袜色",
    "fan": "扇子", "weapon": "武器", "knife": "短刀", "sword": "剑",
    "gadget": "随身装备", "cutoffpockets": "破洞裤", "jumper": "背带裤",
    "bodybelt": "腰封", "bodymark": "身体纹路", "arm": "手臂",
    "armaccessories": "臂饰", "armaccessoriesleft": "左臂饰",
    "armaccessoriesright": "右臂饰", "legaccessory": "腿饰",
    "neckaccessory": "颈饰", "hairaccessory": "发饰",
    "hairaccessory2": "发饰2", "fingernail": "美甲",
    "fingernaillength": "美甲长度", "fingernailcolour": "美甲色",
    "toerings": "趾环", "shorts": "短裤", "shirts": "衬衫", "shirt": "衬衫",
    "shirtcolour": "衬衫色", "jumpercolour": "背带裤色", "sheath": "剑鞘",
    "helpsize": "帮助大小", "lang": "语言", "img_x": "说明图X", "img_y": "说明图Y",
    "menu": "菜单", "menu_open": "菜单开关", "help": "帮助",
    "creditinfo": "作者信息", "diable.Notification".lower(): "关闭提示",
    "disableNotification".lower(): "关闭提示", "bra": "内衣",
    "t": "全身切换", "w": "武器切换", "h": "隐藏",
    # —— 第二批: 本机 mod 实测未覆盖的变量名 ——
    "anim": "动画", "animplate": "动画板", "body": "身体",
    "hairdec": "发饰", "hairog": "原版发型", "handdec": "手部饰品",
    "leg": "腿部", "legs": "腿部", "nipple": "乳头",
    "t4": "全身预设4", "t5": "全身预设5",
    "armaccessoriescolour": "臂饰色", "ballgag": "口球",
    "blazer": "西装外套", "blindfold": "眼罩", "bodysuit": "紧身衣",
    "bot": "下装", "censor": "审查开关", "cloth": "服装",
    "color": "颜色", "controlhair": "头发控制",
    "gloveleft": "左手套", "gloveright": "右手套",
    "hairclip": "发夹", "hairclipcolour": "发夹色", "heel": "鞋跟",
    "nippleaccessories": "乳饰", "originalshoescolour": "原版鞋色",
    "pants": "裤子", "shinyskin": "油亮皮肤",
    "skimpybottoms": "暴露下装", "skimpytop": "暴露上装",
    "skirtcolour": "裙色", "sock": "袜子", "sockscolour": "袜色",
    "strapscolour": "吊带色", "swapvar": "通用切换", "tailbow": "尾结",
    "thighstrapcolour": "腿带色", "thongstraps": "丁字裤带",
    "thongstrapscolour": "丁字裤带色", "topstraps": "上衣吊带",
    "waist": "腰饰", "yanse": "颜色",
}

_KEY_MOD_MAP = (("no_win", "!Win"), ("no_ctrl", "!Ctrl"), ("no_alt", "!Alt"),
                ("no_shift", "!Shift"), ("no_modifiers", "!Mod"),
                ("ctrl", "Ctrl"), ("alt", "Alt"), ("shift", "Shift"),
                ("win", "Win"))


# 3DMigoto 常用的 VK_* 虚拟键码 -> 中文/可读名 (键名大小写不敏感匹配)
_VK_MAP = {
    # 鼠标
    "VK_LBUTTON": "鼠标左键", "VK_RBUTTON": "鼠标右键", "VK_MBUTTON": "鼠标中键",
    "VK_XBUTTON1": "鼠标侧键1", "VK_XBUTTON2": "鼠标侧键2",
    # 控制键
    "VK_BACK": "退格", "VK_TAB": "Tab", "VK_CLEAR": "清除", "VK_RETURN": "回车",
    "VK_ENTER": "回车", "VK_SHIFT": "Shift", "VK_CONTROL": "Ctrl", "VK_MENU": "Alt",
    "VK_PAUSE": "暂停", "VK_CAPITAL": "大写锁定", "VK_KANA": "假名",
    "VK_HANGUL": "韩文", "VK_JUNJA": "转换", "VK_FINAL": "终结",
    "VK_HANJA": "汉字", "VK_KANJI": "汉字",
    "VK_ESCAPE": "Esc", "VK_CONVERT": "转换", "VK_NONCONVERT": "非转换",
    "VK_ACCEPT": "接受", "VK_MODECHANGE": "模式切换",
    "VK_SPACE": "空格", "VK_PRIOR": "PageUp", "VK_NEXT": "PageDown",
    "VK_END": "End", "VK_HOME": "Home",
    "VK_LEFT": "←", "VK_UP": "↑", "VK_RIGHT": "→", "VK_DOWN": "↓",
    "VK_SELECT": "选择", "VK_PRINT": "打印", "VK_EXECUTE": "执行",
    "VK_SNAPSHOT": "截图键", "VK_INSERT": "Insert", "VK_DELETE": "Delete",
    "VK_HELP": "帮助键",
    # 数字
    "VK_0": "0", "VK_1": "1", "VK_2": "2", "VK_3": "3", "VK_4": "4",
    "VK_5": "5", "VK_6": "6", "VK_7": "7", "VK_8": "8", "VK_9": "9",
    # 字母
    "VK_A": "A", "VK_B": "B", "VK_C": "C", "VK_D": "D", "VK_E": "E", "VK_F": "F",
    "VK_G": "G", "VK_H": "H", "VK_I": "I", "VK_J": "J", "VK_K": "K", "VK_L": "L",
    "VK_M": "M", "VK_N": "N", "VK_O": "O", "VK_P": "P", "VK_Q": "Q", "VK_R": "R",
    "VK_S": "S", "VK_T": "T", "VK_U": "U", "VK_V": "V", "VK_W": "W", "VK_X": "X",
    "VK_Y": "Y", "VK_Z": "Z",
    # 小键盘
    "VK_NUMPAD0": "小键盘0", "VK_NUMPAD1": "小键盘1", "VK_NUMPAD2": "小键盘2",
    "VK_NUMPAD3": "小键盘3", "VK_NUMPAD4": "小键盘4", "VK_NUMPAD5": "小键盘5",
    "VK_NUMPAD6": "小键盘6", "VK_NUMPAD7": "小键盘7", "VK_NUMPAD8": "小键盘8",
    "VK_NUMPAD9": "小键盘9",
    "VK_MULTIPLY": "小键盘*", "VK_ADD": "小键盘+", "VK_SEPARATOR": "小键盘分隔",
    "VK_SUBTRACT": "小键盘-", "VK_DECIMAL": "小键盘.", "VK_DIVIDE": "小键盘/",
    # 功能键
    "VK_F1": "F1", "VK_F2": "F2", "VK_F3": "F3", "VK_F4": "F4", "VK_F5": "F5",
    "VK_F6": "F6", "VK_F7": "F7", "VK_F8": "F8", "VK_F9": "F9", "VK_F10": "F10",
    "VK_F11": "F11", "VK_F12": "F12", "VK_F13": "F13", "VK_F14": "F14",
    "VK_F15": "F15", "VK_F16": "F16", "VK_F17": "F17", "VK_F18": "F18",
    "VK_F19": "F19", "VK_F20": "F20", "VK_F21": "F21", "VK_F22": "F22",
    "VK_F23": "F23", "VK_F24": "F24",
    # 锁定 / 左右区分
    "VK_NUMLOCK": "小键盘锁定", "VK_SCROLL": "ScrollLock",
    "VK_LSHIFT": "左Shift", "VK_RSHIFT": "右Shift", "VK_LCONTROL": "左Ctrl",
    "VK_RCONTROL": "右Ctrl", "VK_LMENU": "左Alt", "VK_RMENU": "右Alt",
    "VK_LWIN": "左Win", "VK_RWIN": "右Win",
    # OEM 键
    "VK_OEM_1": ";:", "VK_OEM_PLUS": "+", "VK_OEM_COMMA": ",",
    "VK_OEM_MINUS": "-", "VK_OEM_PERIOD": ".", "VK_OEM_2": "/?", "VK_OEM_3": "`~",
    "VK_OEM_4": "[", "VK_OEM_5": "\\", "VK_OEM_6": "]", "VK_OEM_7": "'\"",
    "VK_OEM_8": "OEM8", "VK_OEM_102": "\\",
    # 多媒体 / 浏览器
    "VK_BROWSER_BACK": "浏览器后退", "VK_BROWSER_FORWARD": "浏览器前进",
    "VK_BROWSER_REFRESH": "浏览器刷新", "VK_BROWSER_STOP": "浏览器停止",
    "VK_BROWSER_SEARCH": "浏览器搜索", "VK_BROWSER_FAVORITES": "浏览器收藏",
    "VK_BROWSER_HOME": "浏览器主页",
    "VK_VOLUME_MUTE": "静音", "VK_VOLUME_DOWN": "音量-", "VK_VOLUME_UP": "音量+",
    "VK_MEDIA_NEXT_TRACK": "下一曲", "VK_MEDIA_PREV_TRACK": "上一曲",
    "VK_MEDIA_STOP": "停止", "VK_MEDIA_PLAY_PAUSE": "播放/暂停",
    "VK_LAUNCH_MAIL": "邮件", "VK_LAUNCH_MEDIA_SELECT": "媒体选择",
    "VK_LAUNCH_APP1": "启动应用1", "VK_LAUNCH_APP2": "启动应用2",
    "VK_APPS": "右键菜单键", "VK_SLEEP": "休眠", "VK_ZOOM": "缩放",
    "VK_ATTN": "Attn", "VK_CRSEL": "CrSel", "VK_EXSEL": "ExSel",
    "VK_EREOF": "EraseEof", "VK_PLAY": "播放", "VK_PA1": "PA1",
    "VK_OEM_CLEAR": "清除", "VK_PROCESSKEY": "IME处理键",
}


def _pretty_keys(keyval):
    """3DMigoto 的 key 行: 空格分隔 = 同时按下的组合键。
    'ctrl alt y 6' -> ['Ctrl+Alt+Y+6'], 'no_ctrl h' -> ['H(无Ctrl)'],
    'h' -> ['H'], 'VK_CAPITAL' -> ['大写锁定'], 'VK_RBUTTON' -> ['鼠标右键']。
    no_* 是『不能按某修饰键』的排除项, 显示为「无X」后缀; VK_* 一律翻译成中文键名。
    支持引号包裹的空格: \"' '\" -> ['空格']。"""
    parts = []
    neg_parts = []
    # 用 shlex 风格的简单解析: 保留引号内的内容作为整体
    tokens = []
    raw = (keyval or "").strip()
    i = 0
    while i < len(raw):
        if raw[i] in ('"', "'"):
            quote = raw[i]
            j = i + 1
            while j < len(raw) and raw[j] != quote:
                j += 1
            if j < len(raw):
                tokens.append(raw[i+1:j])  # 成对引号: 去掉引号取内容
                i = j + 1
                continue
            # 落单引号 = 撇号键本身(Key = '), 当普通字符处理
        if raw[i].isspace():
            i += 1
            continue
        j = i
        while j < len(raw) and not raw[j].isspace():
            j += 1
        tokens.append(raw[i:j])
        i = j
    for t in tokens:
        # 引号包裹的空格 -> 空格键
        if t == ' ':
            parts.append("空格")
            continue
        tl = t.lower()
        hit = False
        for name, disp in _KEY_MOD_MAP:
            if tl == name:
                if disp:
                    if disp.startswith("!"):
                        neg_parts.append(disp[1:])  # !Ctrl -> Ctrl (later shown as 无Ctrl)
                    else:
                        parts.append(disp)
                hit = True
                break
        if hit:
            continue
        # VK_ 虚拟键码 -> 中文键名
        if tl.startswith("vk_"):
            parts.append(_VK_MAP.get(tl.upper(), t))
            continue
        # 0x41 这种十六进制原始键码
        if re.match(r"^0x[0-9a-f]+$", tl):
            parts.append("按键 " + t)
            continue
        parts.append(t if len(t) > 1 else t.upper())
    if not parts:
        return []
    result = "+".join(parts)
    if neg_parts:
        result += "(无" + "+".join(neg_parts) + ")"
    return [result]


def parse_cycle_vars(abs_root):
    """扫描 mod 内已启用 ini 的 [Key*] 段, 汇总每个循环变量的
    取值列表 / 绑定按键 / 当前值 / 可否从外部切换。"""
    found = {}
    for cur, dirs, files in os.walk(abs_root):
        dirs[:] = [d for d in dirs if d.lower() != "desktop.ini"]
        rel_dir = os.path.relpath(cur, abs_root)
        rel_dir = "" if rel_dir == "." else rel_dir
        for f in files:
            if not f.lower().endswith(".ini") or is_disabled_name(f):
                continue
            p = os.path.join(cur, f)
            try:
                if os.path.getsize(p) > 2 * 1024 * 1024:
                    continue
                txt = open(p, "r", encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            rel = norm_rel(os.path.join(rel_dir, f))
            sec_name, sec_cycle, sec_key, sec_decls = None, False, "", []
            sec_note = ""

            def _flush():
                if not sec_cycle or not sec_decls:
                    return
                for ln, var, raw in sec_decls:
                    base_label = re.sub(r"(?i)^(swap_?var_?|swap_?|var_?)",
                                        "", var) or var
                    # 段头 ] 后面的作者备注(如 [KeySwap2]丝袜)就是最准确的中文名,
                    # 优先于内置翻译表
                    label_cn = sec_note or CYCLE_LABEL_CN.get(base_label.lower())
                    rec = found.setdefault(var, {
                        "var": var,
                        "label": base_label,
                        "label_cn": label_cn,
                        "values": [], "keys": [], "keys_raw": [], "files": [],
                        "switchable": True})
                    if sec_note and not rec.get("label_cn"):
                        rec["label_cn"] = sec_note
                    for k in _pretty_keys(sec_key):
                        if k not in rec["keys"]:
                            rec["keys"].append(k)
                    if (sec_key or "").strip() and \
                            sec_key not in rec["keys_raw"]:
                        rec["keys_raw"].append(sec_key)
                    if {"rel": rel, "line": ln} not in rec["files"]:
                        rec["files"].append({"rel": rel, "line": ln})
                    if raw == "?":
                        rec["switchable"] = False   # 带表达式, 只能游戏内按键切
                        continue
                    vals = [int(x) for x in
                            raw.replace(" ", "").split(",") if x != ""]
                    if not vals:
                        rec["switchable"] = False
                        continue
                    if not rec["values"]:
                        rec["values"] = vals
                    elif rec["values"] != vals:
                        rec["switchable"] = False   # 各文件取值不一致, 保守不切

            for ln, line in enumerate(txt.splitlines(), 1):
                st = line.strip()
                sec = _ini_section(st)
                if sec is not None:
                    _flush()
                    sec_name = sec
                    sec_note = st[st.find("]") + 1:].strip()
                    sec_cycle, sec_key, sec_decls = False, "", []
                    continue
                if sec_name is None or not KEYSEC_RE.match(sec_name):
                    continue
                low = st.lower()
                if low.startswith("key=") or low.startswith("key ="):
                    # 行内注释(; # 后面)不是键名, 截掉再显示
                    sec_key = re.split(r"[;#]", st.split("=", 1)[1])[0].strip()
                elif low.startswith("type=") or low.startswith("type ="):
                    if "cycle" in low.split("=", 1)[1].lower():
                        sec_cycle = True
                else:
                    dm = CYCLE_DECL_RE.match(st)
                    if dm:
                        sec_decls.append((ln, dm.group(1), dm.group(2)))
                    elif st.startswith("$") and CYCLE_EXPR_RE.match(st):
                        # 带表达式的循环(如 $menu = 0,1 - $bodyPaint): 展示但不可切
                        m2 = CYCLE_EXPR_RE.match(st)
                        sec_decls.append((ln, m2.group(1), "?"))
            _flush()

    out = list(found.values())
    for rec in out:
        rec["current"] = rec["values"][0] if rec["values"] else None
    out.sort(key=lambda r: r["var"].lower())
    return out


def do_cycle_set(abs_root, var, value):
    """把循环变量 var 的『默认变体』持久设为 value: 仅就地旋转对应那一行
    的值列表, 让 value 排第一(3DMigoto 取首元素作默认)。
    字节级修改, 完整保留原文件编码 / 换行符 / BOM, 绝不重写整文件; 改前
    整文件备份, 写 journal 可撤销。注意: 这只改变『下次进游戏默认加载的变体』,
    游戏内按绑定键仍可即时循环切换。"""
    value = int(value)
    edits = []   # (path, abs_start, abs_end, newbytes)  绝对字节偏移
    for cur, dirs, files in os.walk(abs_root):
        dirs[:] = [d for d in dirs if d.lower() != "desktop.ini"]
        for f in files:
            if not f.lower().endswith(".ini") or is_disabled_name(f):
                continue
            p = os.path.join(cur, f)
            try:
                if os.path.getsize(p) > 2 * 1024 * 1024:
                    continue
                data = read_bytes_shared(p)
            except Exception:
                continue
            # latin-1 与字节 1:1, 便于用文本正则定位后回写原字节
            text = data.decode("latin-1")
            sec_name, sec_cycle = None, False
            pos = 0
            for line in text.splitlines(True):
                st = line.strip()
                sec = _ini_section(st)
                if sec is not None:
                    sec_name = sec
                    sec_cycle = False
                    pos += len(line)
                    continue
                if sec_name is None or not KEYSEC_RE.match(sec_name):
                    pos += len(line)
                    continue
                low = st.lower()
                if low.startswith("type=") or low.startswith("type ="):
                    if "cycle" in low.split("=", 1)[1].lower():
                        sec_cycle = True
                    pos += len(line)
                    continue
                if not sec_cycle:
                    pos += len(line)
                    continue
                m = CYCLE_DECL_RE.search(line)
                if m and m.group(1) == var:
                    vals = [int(x) for x in
                            m.group(2).replace(" ", "").split(",") if x != ""]
                    if value not in vals:
                        pos += len(line)
                        continue
                    if vals[0] == value:   # 已是该默认, 跳过
                        pos += len(line)
                        continue
                    idx = vals.index(value)
                    new = vals[idx:] + vals[:idx]
                    tail = m.group(2).rstrip().endswith(",")
                    newstr = ",".join(str(v) for v in new) + ("," if tail else "")
                    edits.append((p, pos + m.start(2), pos + m.end(2),
                                 newstr.encode("latin-1")))
                pos += len(line)

    if not edits:
        return False, "这个变量没有可切换的取值 %d" % value

    os.makedirs(INI_BACKUP_DIR, exist_ok=True)
    byfile = {}
    for p, s, e, nb in edits:
        byfile.setdefault(p, []).append((s, e, nb))

    changed = 0
    for p, items in byfile.items():
        try:
            data = open(p, "rb").read()
        except Exception as ex:
            return False, "读文件失败: %s" % ex
        bak = os.path.join(INI_BACKUP_DIR, "%s_%s" % (
            hashlib.sha1(os.path.abspath(p).encode("utf-8")).hexdigest()[:12],
            os.path.basename(p)))
        try:
            if not os.path.isfile(bak):
                shutil.copyfile(p, bak)
            items.sort()
            out = bytearray()
            cursor = 0
            for s, e, nb in items:   # 非重叠, 按偏移拼接
                out += data[cursor:s]
                out += nb
                cursor = e
            out += data[cursor:]
            open(p, "wb").write(bytes(out))
        except Exception as ex:
            return False, "写文件失败: %s" % ex
        journal_append({"kind": "ini_edit", "path": p, "backup": bak,
                        "name": os.path.basename(p), "var": var,
                        "value": value})
        changed += 1
    if changed == 0:
        return True, "已经是这个默认变体了"
    return True, "已把默认变体设为 %d (改了 %d 个文件); 游戏内按 F10 或重启生效" % (value, changed)


# ---------------------------------------------------------------------------
# 变体一键改键: 玩家输入「键位 空格 键位」(如 ctrl a), 找到该变体 [Key*]
# cycle 段里绑定的 key = 行, 把键值部分就地替换成新绑定。
# 与 do_cycle_set 同一套安全机制: latin-1 字节级定位、只动键值那一段,
# 编码/换行/BOM/注释原样保留, 改前整文件备份, 写 journal 可撤销。
# ---------------------------------------------------------------------------

# 用户输入的友好键名 -> 3DMigoto key 行里的写法 (全部小写匹配)
_KEY_INPUT_MAP = {
    "ctrl": "ctrl", "ctl": "ctrl", "control": "ctrl",
    "shift": "shift", "alt": "alt", "win": "win", "windows": "win",
    "tab": "VK_TAB", "enter": "VK_RETURN", "return": "VK_RETURN",
    "回车": "VK_RETURN", "esc": "VK_ESCAPE", "escape": "VK_ESCAPE",
    "space": "VK_SPACE", "spacebar": "VK_SPACE", "空格": "VK_SPACE",
    "backspace": "VK_BACK", "退格": "VK_BACK",
    "caps": "VK_CAPITAL", "capslock": "VK_CAPITAL", "大写锁定": "VK_CAPITAL",
    "numlock": "VK_NUMLOCK", "小键盘锁定": "VK_NUMLOCK",
    "scrolllock": "VK_SCROLL", "pause": "VK_PAUSE", "break": "VK_PAUSE",
    "printscreen": "VK_SNAPSHOT", "prtsc": "VK_SNAPSHOT",
    "up": "VK_UP", "down": "VK_DOWN", "left": "VK_LEFT", "right": "VK_RIGHT",
    "上": "VK_UP", "下": "VK_DOWN", "左": "VK_LEFT", "右": "VK_RIGHT",
    "pageup": "VK_PRIOR", "pgup": "VK_PRIOR", "上一页": "VK_PRIOR",
    "pagedown": "VK_NEXT", "pgdn": "VK_NEXT", "下一页": "VK_NEXT",
    "insert": "VK_INSERT", "ins": "VK_INSERT", "插入": "VK_INSERT",
    "delete": "VK_DELETE", "del": "VK_DELETE", "删除": "VK_DELETE",
    "home": "VK_HOME", "end": "VK_END",
    "minus": "VK_OEM_MINUS", "-": "VK_OEM_MINUS",
    "plus": "VK_OEM_PLUS", "=": "VK_OEM_PLUS",
    "comma": "VK_OEM_COMMA", ",": "VK_OEM_COMMA",
    "period": "VK_OEM_PERIOD", ".": "VK_OEM_PERIOD", "dot": "VK_OEM_PERIOD",
    "slash": "VK_OEM_2", "/": "VK_OEM_2",
    "semicolon": "VK_OEM_1", ";": "VK_OEM_1",
    "quote": "VK_OEM_7", "'": "VK_OEM_7",
    "backquote": "VK_OEM_3", "`": "VK_OEM_3",
    "backslash": "VK_OEM_5", "\\": "VK_OEM_5",
    "lbracket": "VK_OEM_4", "[": "VK_OEM_4",
    "rbracket": "VK_OEM_6", "]": "VK_OEM_6",
    "multiply": "VK_MULTIPLY", "add": "VK_ADD", "subtract": "VK_SUBTRACT",
    "decimal": "VK_DECIMAL", "divide": "VK_DIVIDE",
    "mouse1": "VK_LBUTTON", "lbutton": "VK_LBUTTON", "鼠标左键": "VK_LBUTTON",
    "mouse2": "VK_RBUTTON", "rbutton": "VK_RBUTTON", "鼠标右键": "VK_RBUTTON",
    "mouse3": "VK_MBUTTON", "mbutton": "VK_MBUTTON", "鼠标中键": "VK_MBUTTON",
    "mouse4": "VK_XBUTTON1", "xbutton1": "VK_XBUTTON1", "鼠标侧键1": "VK_XBUTTON1",
    "mouse5": "VK_XBUTTON2", "xbutton2": "VK_XBUTTON2", "鼠标侧键2": "VK_XBUTTON2",
}
for _i in range(1, 25):                     # f1..f24
    _KEY_INPUT_MAP["f%d" % _i] = "VK_F%d" % _i
for _i in range(10):                        # numpad0..9
    _KEY_INPUT_MAP["numpad%d" % _i] = "VK_NUMPAD%d" % _i
    _KEY_INPUT_MAP["小键盘%d" % _i] = "VK_NUMPAD%d" % _i

_KEY_PLAIN_MODS = ("ctrl", "shift", "alt", "win")


def parse_key_input(s):
    """把玩家输入的按键串解析成 3DMigoto key = 行的值。
    'ctrl a' -> 'ctrl a', 'shift f1' -> 'shift VK_F1', 'numpad0' -> 'VK_NUMPAD0',
    'vk_up' -> 'VK_UP'。返回 (新值, None) 或 (None, 错误信息)。"""
    toks = [t for t in re.split(r"[\s+]+", (s or "").strip()) if t]
    if not toks:
        return None, "按键不能为空。格式: 键位 空格 键位, 例如 ctrl a"
    out = []
    for t in toks:
        tl = t.strip().lower()
        if not tl:
            continue
        if tl.startswith("vk_"):            # 已是 VK 写法, 原样收下
            out.append(tl.upper())
            continue
        if re.match(r"^0x[0-9a-f]+$", tl):  # 原始十六进制键码
            out.append(tl)
            continue
        if tl in _KEY_INPUT_MAP:
            out.append(_KEY_INPUT_MAP[tl])
            continue
        if len(tl) == 1 and ("a" <= tl <= "z" or "0" <= tl <= "9"):
            out.append(tl)                  # 单个字母/数字直接用裸名(h 这种)
            continue
        return None, ("不认识的按键「%s」。\n可写: ctrl a / shift f1 / alt q / "
                      "numpad0 / up / del / 鼠标侧键1 / VK_CAPITAL 等" % t)
    if not out:
        return None, "按键不能为空。格式: 键位 空格 键位, 例如 ctrl a"
    if all(t in _KEY_PLAIN_MODS for t in out):
        return None, "只按修饰键(Ctrl/Shift/Alt/Win)没有意义, 后面要跟一个主键, 例如 ctrl a"
    return " ".join(out), None


def do_cycle_rekey(abs_root, var, key_input):
    """把循环变量 var 的绑定按键改成玩家输入的新键。
    找 mod 内已启用 ini 中 [Key*] 且 type = cycle 且声明了 $var 的段,
    段内所有 key = 行的键值部分就地替换。字节级 + 备份 + journal 可撤销。"""
    var = (var or "").strip()
    new_raw, err = parse_key_input(key_input)
    if err:
        return False, err
    new_disp = "、".join(_pretty_keys(new_raw)) or new_raw
    edits = []   # (path, abs_start, abs_end, newbytes, oldraw)
    for cur, dirs, files in os.walk(abs_root):
        dirs[:] = [d for d in dirs if d.lower() != "desktop.ini"]
        for f in files:
            if not f.lower().endswith(".ini") or is_disabled_name(f):
                continue
            p = os.path.join(cur, f)
            try:
                if os.path.getsize(p) > 2 * 1024 * 1024:
                    continue
                data = read_bytes_shared(p)
            except Exception:
                continue
            text = data.decode("latin-1")   # latin-1 与字节 1:1, 可定位后回写
            sec_name, sec_cycle, sec_var, sec_spans = None, False, False, []
            pos = 0
            for line in text.splitlines(True):
                st = line.strip()
                sec = _ini_section(st)
                if sec is not None:
                    if sec_name is not None and sec_cycle and sec_var:
                        edits.extend((p, s, e, nb, old)
                                     for (s, e, old) in sec_spans
                                     for nb in [new_raw.encode("latin-1")]
                                     if old != new_raw)
                    sec_name = sec
                    sec_cycle, sec_var, sec_spans = False, False, []
                    pos += len(line)
                    continue
                if sec_name is None or not KEYSEC_RE.match(sec_name):
                    pos += len(line)
                    continue
                low = st.lower()
                if low.startswith("key=") or low.startswith("key ="):
                    eq = line.find("=")
                    after = line[eq + 1:]
                    cm = re.search(r"[;#]", after)
                    val_part = after if cm is None else after[:cm.start()]
                    stripped = val_part.strip()
                    if stripped:
                        start = pos + eq + 1 + (len(val_part) - len(val_part.lstrip()))
                        sec_spans.append((start, start + len(stripped), stripped))
                    pos += len(line)
                    continue
                if low.startswith("type=") or low.startswith("type ="):
                    if "cycle" in low.split("=", 1)[1].lower():
                        sec_cycle = True
                    pos += len(line)
                    continue
                dm = CYCLE_DECL_RE.match(st)
                if dm and dm.group(1) == var:
                    sec_var = True
                elif st.startswith("$"):
                    m2 = CYCLE_EXPR_RE.match(st)
                    if m2 and m2.group(1) == var:
                        sec_var = True
                pos += len(line)
            if sec_name is not None and sec_cycle and sec_var:
                edits.extend((p, s, e, nb, old)
                             for (s, e, old) in sec_spans
                             for nb in [new_raw.encode("latin-1")]
                             if old != new_raw)

    if not edits:
        return False, ("没找到「%s」绑定的 key 行 —— 这个变体可能没有绑定按键,"
                       "或它的段不是 [Key*] + type = cycle 的写法" % var)

    os.makedirs(INI_BACKUP_DIR, exist_ok=True)
    byfile = {}
    for p, s, e, nb, old in edits:
        byfile.setdefault(p, []).append((s, e, nb))
    old_disp = "、".join(_pretty_keys(edits[0][4])) or edits[0][4]

    changed = 0
    for p, items in byfile.items():
        try:
            data = open(p, "rb").read()
        except Exception as ex:
            return False, "读文件失败: %s" % ex
        bak = os.path.join(INI_BACKUP_DIR, "%s_%s" % (
            hashlib.sha1(os.path.abspath(p).encode("utf-8")).hexdigest()[:12],
            os.path.basename(p)))
        try:
            if not os.path.isfile(bak):
                shutil.copyfile(p, bak)
            items.sort()
            out = bytearray()
            cursor = 0
            for s, e, nb in items:   # 非重叠, 按偏移拼接
                out += data[cursor:s]
                out += nb
                cursor = e
            out += data[cursor:]
            open(p, "wb").write(bytes(out))
        except Exception as ex:
            return False, "写文件失败: %s" % ex
        journal_append({"kind": "ini_edit", "path": p, "backup": bak,
                        "name": os.path.basename(p), "var": var,
                        "key": new_raw})
        changed += 1
    if changed == 0:
        return True, "这个变体已经是 %s 了, 没有改动" % new_disp
    return True, "已把「%s」的按键从 %s 改为 %s (改了 %d 个文件); 进游戏按 F10 或重启生效, 顶栏「撤销」可还原" % (
        var, old_disp, new_disp, changed)



def batch_toggle(mods_dir, entries, enable):
    entries = sorted(entries, key=lambda e: e["path"].count("/"))
    ok, fails, renamed = 0, [], []
    for e in entries:
        info = None
        try:
            res = do_toggle(mods_dir, e, enable)
            if len(res) == 3:
                good, msg, info = res
            else:
                good, msg = res
        except Exception as ex:
            good, msg = False, str(ex)
        if good:
            ok += 1
            # v1.5.8: 因为撞名被自动加后缀的, 也算"改了名", 收进 renamed 交给前端提示
            if info and info.get("renamed"):
                renamed.append({"id": e["id"], "name": e["name"],
                                "orig_name": info.get("orig_name"),
                                "target_name": info.get("target_name"),
                                "seq": info.get("seq"),
                                "enable": bool(enable)})
        else:
            d = {"id": e["id"], "name": e["name"], "msg": msg,
                 # v1.5.6: 把"卡在哪一步"告诉前端, 好弹出对应的手动处理教程
                 "enable": bool(enable), "reason": lock_reason_kind(msg)}
            if info:
                d.update(info)
            fails.append(d)
    return {"ok": ok, "failed": len(fails), "details": fails[:20],
            "renamed": renamed[:60]}


def lock_reason_kind(msg):
    """把重命名失败的中文原因归成 'busy'(被占用) / 'denied'(权限) / 'other',
    前端据此决定弹"手动加 DISABLED_"还是"手动删 DISABLED_"。

    注意顺序: _rename_dir 在真的被拒时给的是 lock_reason 文案, 而权限那类措辞
    (拒绝访问 / 只读 / 杀软) 也可能同时出现"占用"字样, 所以先判 denied。
    """
    m = msg or ""
    # v1.5.8: 「因为「XXX」已被占用, 自动改名为…」是**成功**消息(v1.5.8 的重名自动加后缀),
    # 只有失败才会走到这里判原因, 但保险起见先挡一道 —— 免得那句里的"已被占用"
    # 被当成"文件被占用"而错弹手动改名教程。
    if "自动改名" in m:
        return "other"
    if "拒绝访问" in m or "权限" in m or "只读" in m or "杀软" in m:
        return "denied"
    if "占用" in m or "打开" in m or "游戏" in m:
        return "busy"
    return "other"


def undo_last():
    for rec in reversed(journal_read(2000)):
        kind = rec.get("kind")
        if kind == "ini_edit":
            p, bak = rec.get("path"), rec.get("backup")
            if p and bak and os.path.isfile(bak) and os.path.isfile(p):
                try:
                    shutil.copyfile(bak, p)
                except Exception as ex:
                    return False, "撤销失败: %s" % ex
                journal_append({"kind": "undo", "of": rec.get("ts")})
                return True, "已还原: %s" % os.path.basename(p)
            return False, "文件状态已变化, 无法撤销这一步"
        if kind not in ("toggle", "move", "file_toggle"):
            continue
        src, dst = rec.get("src"), rec.get("dst")
        if not src or not dst:
            continue
        if os.path.exists(dst) and not os.path.exists(src):
            try:
                os.rename(dst, src)
            except OSError as ex:
                return False, "撤销失败: %s" % ex
            journal_append({"kind": "undo", "of": rec.get("ts")})
            return True, "已撤销: %s" % os.path.basename(src)
        return False, "文件状态已变化, 无法撤销这一步"
    return False, "没有可撤销的操作"


def do_move(src_base, src_rel, dst_base, dst_rel):
    src = resolve_rel_dir(src_base, src_rel)
    dst = safe_join(dst_base, dst_rel)
    if not src or not os.path.isdir(src):
        return False, "源目录不存在"
    if not dst:
        return False, "目标路径不合法"
    if os.path.abspath(src) == os.path.abspath(dst):
        return False, "源和目标相同"
    if os.path.abspath(dst).startswith(os.path.abspath(src) + os.sep):
        return False, "不能移动到自己的子目录里"
    ok, msg = move_dir(src, dst, {"kind": "move", "src": src, "dst": dst})
    return (True, "已移动") if ok else (False, msg)


def strip_path_quotes(p):
    """去掉用户复制路径时常带的引号 / 首尾空白。

    v1.5.15: 从资源管理器地址栏复制路径时 Windows 会自动加引号("D:\\xx"),
    以前没处理 -> 被当成相对路径拼到默认目录后面 -> 报「建不了这个文件夹」,
    用户看到的就是「目录根本改不了」。引号一律剥掉。

    注意左右引号是不同的字符(全角 " 和 "), 要按配对处理。
    """
    s = (p or "").strip()
    pairs = (('"', '"'), ("'", "'"),
             ("\u201c", "\u201d"),      # 中文左右双引号 “ ”
             ("\u2018", "\u2019"),      # 中文左右单引号 ‘ ’
             ("\u300c", "\u300d"))      # 直角引号 「 」
    changed = True
    while changed and len(s) >= 2:
        changed = False
        for a, b in pairs:
            if s[0] == a and s[-1] == b:
                s = s[1:-1].strip()
                changed = True
                break
    return s


def is_abs_path(p):
    """判断用户给的是不是一个完整路径(F:\\xxx / \\\\nas\\share / abs:前缀)。"""
    s = strip_path_quotes(p)
    if s.startswith("abs:"):
        return True
    if re.match(r"^[A-Za-z]:[\\/]", s):
        return True
    if re.match(r"^[A-Za-z]:$", s):          # 光给个盘符 "D:"
        return True
    if s.startswith("\\\\") or s.startswith("//"):
        return True
    return False


def strip_abs_prefix(p):
    s = strip_path_quotes(p)
    return s[4:].strip() if s.startswith("abs:") else s


def list_drives():
    """Windows 下有哪些盘符; 非 Windows 就给根目录。"""
    if not _WIN:
        return [os.sep]
    import string
    return ["%s:\\" % c for c in string.ascii_uppercase
            if os.path.isdir("%s:\\" % c)]


def move_mods_batch(mods_dir, entries, dst_root):
    """把一批 mod 目录搬到 dst_root(仓库)下。同名自动加 (2), 绝不覆盖。"""
    ok, fails, moved = 0, [], []
    names = []
    for e in entries:
        # 散落在 Mods 根目录的 ini 没有"整个目录"可搬, 别把 Mods 根给搬走了
        if not (e.get("path") or "").strip():
            fails.append({"id": e["id"], "name": e["name"],
                          "msg": "这是散落在 Mods 根目录的 ini, 没有独立文件夹可搬"})
            continue
        src = entry_root(mods_dir, e)
        if not src or not os.path.isdir(src):
            fails.append({"id": e["id"], "name": e["name"], "msg": "找不到目录(可能已被移动)"})
            continue
        name = os.path.basename(src)
        dst = os.path.join(dst_root, name)
        if os.path.abspath(dst) == os.path.abspath(src):
            fails.append({"id": e["id"], "name": e["name"], "msg": "已经在目标位置了"})
            continue
        if os.path.exists(dst):
            uniq = unique_path(dst)
            if not uniq:
                fails.append({"id": e["id"], "name": e["name"],
                              "msg": "目标里同名太多, 请先改名"})
                continue
            dst = uniq
        good, msg = move_dir(src, dst, {"kind": "move", "src": src, "dst": dst,
                                        "id": e["id"], "name": e["name"]})
        if good:
            ok += 1
            moved.append({"name": name, "as": os.path.basename(dst),
                          "to": os.path.dirname(dst)})
        else:
            fails.append({"id": e["id"], "name": e["name"], "msg": msg})
    return {"ok": ok, "failed": len(fails), "details": fails[:20],
            "moved": moved[:60]}


def _migrate_override_keys(cfg, old_rel, new_rel):
    """重命名 mod 文件夹后, 把配置里以旧路径为键/值的覆盖项迁到新路径。

    覆盖 thumb_overrides(键=mod路径, 值=封面图路径) 和 char_overrides
    (键=mod路径, 值=角色名)。不匹配的一律不动; 不清任何旧键(禁用中的 mod
    合法地不在当前列表里, 清了会丢用户设置)。"""
    if not old_rel or not new_rel or old_rel == new_rel:
        return
    oldp, newp = old_rel + "/", new_rel + "/"
    for name in ("thumb_overrides", "char_overrides"):
        ov = cfg.get(name)
        if not isinstance(ov, dict):
            continue
        for k in list(ov.keys()):
            v = ov[k]
            if k == old_rel:
                nk = new_rel
            elif k.startswith(oldp):
                nk = newp + k[len(oldp):]
            else:
                nk = k
            nv = v
            if isinstance(v, str):
                if v == old_rel:
                    nv = new_rel
                elif v.startswith(oldp):
                    nv = newp + v[len(oldp):]
            if nk != k:
                ov.pop(k, None)
            ov[nk] = nv


def do_rename(mods_dir, entry, new_name):
    cur = entry_root(mods_dir, entry)
    if not cur or not os.path.isdir(cur):
        return False, "找不到目录"
    new_name = (new_name or "").strip()
    if not new_name or re.search(r'[\\/:*?"<>|]', new_name):
        return False, '名称不合法(不能含 \\ / : * ? " < > |)'
    disabled = is_disabled_name(os.path.basename(cur))
    target = (DISABLED_PREFIX + new_name) if disabled else new_name
    dst = os.path.join(os.path.dirname(cur), target)
    if os.path.abspath(dst) == os.path.abspath(cur):
        return False, "名称没有变化"
    # v1.5.8: 撞名不再报错 —— 自动加 (2) (3)…, 把最终名字带回前端提示玩家
    dst, seq = auto_unique_name(dst)
    if not dst:
        return False, "同名太多(已排到 200), 先清理一下重复的 mod 吧"
    final = os.path.basename(dst)
    ok, msg = _rename_dir(cur, dst, {"kind": "move", "src": cur, "dst": dst})
    if ok:
        out = "已重命名为 %s" % final
        if seq is not None:
            out += "（「%s」已被占用, 自动加了 (%d)）" % (target, seq)
        return True, out, {"renamed": seq is not None, "orig_name": target,
                           "target_name": final, "seq": seq}
    # v1.5.24: 改名被系统挡下 -> 交回手动改名弹窗需要的料(和启停失败同一套弹窗)
    return False, msg, {"dir": os.path.dirname(cur), "cur": cur, "want": dst,
                        "target_name": final, "name": os.path.basename(cur),
                        "reason": lock_reason_kind(msg), "rename": True}


def recycle_path(abs_path):
    """把一个文件/文件夹**移到回收站**(不是物理删除, 可从回收站还原)。
    返回 (ok, msg)。非 Windows 直接拒绝 —— 宁可不动, 也不 os.remove。"""
    if not _WIN:
        return False, "只有 Windows 支持移到回收站"
    import ctypes
    from ctypes import wintypes
    FO_DELETE = 3
    # FOF_ALLOWUNDO=进回收站; 静默、不弹系统确认/错误框(确认由界面做二次弹窗)
    FLAGS = 0x0004 | 0x0010 | 0x0040 | 0x0400   # SILENT|NOCONFIRMATION|ALLOWUNDO|NOERRORUI

    class SHFILEOPSTRUCTW(ctypes.Structure):
        _fields_ = [("hwnd", wintypes.HWND),
                    ("wFunc", ctypes.c_uint),
                    ("pFrom", wintypes.LPCWSTR),
                    ("pTo", wintypes.LPCWSTR),
                    ("fFlags", ctypes.c_ushort),
                    ("fAnyOperationsAborted", wintypes.BOOL),
                    ("hNameMappings", ctypes.c_void_p),
                    ("lpszProgressTitle", wintypes.LPCWSTR)]
    # pFrom 要求「双 null 结尾」
    op = SHFILEOPSTRUCTW()
    op.hwnd = None
    op.wFunc = FO_DELETE
    op.pFrom = abs_path + "\0\0"
    op.pTo = None
    op.fFlags = FLAGS
    try:
        rc = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op))
    except Exception as ex:
        return False, "移到回收站失败: %s" % ex
    if rc == 0 and not op.fAnyOperationsAborted:
        return True, "已移到回收站"
    if op.fAnyOperationsAborted:
        return False, "已取消"
    return False, {
        0x7C: "没找到这个文件夹(可能已被移走)",
        0x74: "这个文件夹正被占用 —— 先关掉游戏再试",
        0x57: "参数不对(路径异常)",
        0x3A: "路径太长, 先把 mod 挪到浅一点的目录",
    }.get(rc, "移到回收站失败(code=%d)%s" % (rc, ""))


def do_mod_delete(mods_dir, entry):
    """删除整个 mod 文件夹 —— 只走回收站, 永不物理删除。
    安全闸: 目标必须真实存在、且就在 Mods 目录里面(防越界删到盘符/系统目录)。"""
    cur = entry_root(mods_dir, entry)
    if not cur or not os.path.isdir(cur):
        return False, "找不到这个 mod 的文件夹(可能已被移走)"
    md = os.path.abspath(mods_dir)
    target = os.path.abspath(cur)
    if os.path.normcase(target) == os.path.normcase(md):
        return False, "不能删除 Mods 总目录本身"
    if os.path.normcase(target).startswith(os.path.normcase(md) + os.sep):
        pass                                   # 正常: 在 Mods 里面
    else:
        return False, "这个 mod 不在 Mods 目录里, 为安全起见不删"
    ok, msg = recycle_path(target)
    if ok:
        msg = "已把「%s」移到回收站" % os.path.basename(target)
    return ok, msg


def _explorer_windows():
    """列出所有资源管理器窗口: [(hwnd, 标题), ...]"""
    if not _WIN:
        return []
    import ctypes
    user32 = ctypes.windll.user32
    out = []
    proto = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)
    GetClassNameW = user32.GetClassNameW
    GetWindowTextW = user32.GetWindowTextW

    def _cb(hwnd, _l):
        try:
            buf = ctypes.create_unicode_buffer(64)
            GetClassNameW(hwnd, buf, 64)
            if buf.value in ("CabinetWClass", "ExploreWClass"):
                t = ctypes.create_unicode_buffer(520)
                GetWindowTextW(hwnd, t, 520)
                out.append((hwnd, t.value))
        except Exception:
            pass
        return 1

    try:
        user32.EnumWindows(proto(_cb), None)
    except Exception:
        pass
    return out


def force_foreground(hwnd):
    """把某个窗口直接顶到最前(不用用户再点任务栏)。

    本程序常以管理员身份运行, 这时 SetForegroundWindow 会被系统拒绝, 所以:
    先恢复显示 → 用 topmost 闪一下顶开 Z 序 → 敲一下 ALT 解除"前台锁定" → 再 SetForeground。"""
    if not hwnd or not _WIN:
        return False
    import ctypes
    user32 = ctypes.windll.user32
    SW_RESTORE, SW_SHOW = 9, 5
    SWP_NOSIZE, SWP_NOMOVE, SWP_SHOWWINDOW = 0x0001, 0x0002, 0x0040
    HWND_TOPMOST, HWND_NOTOPMOST = -1, -2
    VK_MENU, KEYEVENTF_KEYUP = 0x12, 0x0002
    try:
        if user32.IsIconic(hwnd):
            user32.ShowWindow(hwnd, SW_RESTORE)
        else:
            user32.ShowWindow(hwnd, SW_SHOW)
        user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                            SWP_NOSIZE | SWP_NOMOVE | SWP_SHOWWINDOW)
        user32.SetWindowPos(hwnd, HWND_NOTOPMOST, 0, 0, 0, 0,
                            SWP_NOSIZE | SWP_NOMOVE | SWP_SHOWWINDOW)
        user32.keybd_event(VK_MENU, 0, 0, 0)
        user32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)
        user32.SetForegroundWindow(hwnd)
        user32.BringWindowToTop(hwnd)
        return True
    except Exception:
        return False


def _focus_explorer_async(hint, known, tries=16):
    """后台等资源管理器把窗口开出来, 再拉到最前。
    hint = 目标文件夹名(窗口标题就是它); 找不到标题就用"新出现的窗口"兜底。"""
    hint = (hint or "").lower()
    for _ in range(max(1, tries)):
        time.sleep(0.13)
        wins = _explorer_windows()
        cand = [h for h, t in wins if hint and hint in (t or "").lower()]
        if not cand:
            cand = [h for h, _t in wins if h not in known]
        if cand:
            force_foreground(cand[0])
            return True
    return False


def open_in_explorer(path, select=False):
    """打开文件夹 / 定位文件, 并**直接把它顶到最前**, 不用再点任务栏。

    select=True 时: 传目录也走「/select」方式 —— 打开它所在的父目录并把这一项
    高亮选中(玩家按 F2 就能改名, 不用自己一层层翻进去找)。

    v1.5.14: 打包后本程序是**提权(管理员)**进程, 直接 os.startfile / explorer
    在部分机器上会被静默拦掉(用户实测「📂 打开」没反应)。改成多级回落:
      ① explorer /select(定位)  → ② explorer 直接开目录  → ③ ShellExecuteW
    三级里任意一级成功就算成功。
    """
    if not path or not os.path.exists(path):
        return False
    p = os.path.normpath(path)
    is_file = os.path.isfile(p)
    # /select 需要"要被选中的那个东西", 文件就是文件本身, 目录就是目录本身
    sel_target = p if (is_file or select) else None
    hint = os.path.basename(os.path.dirname(p)) if is_file else os.path.basename(p)
    try:
        known = set(h for h, _t in _explorer_windows())
    except Exception:
        known = set()

    started = False
    # ① /select 定位(会复用已有窗口)
    if sel_target:
        try:
            subprocess.Popen(["explorer", "/select,", sel_target])
            started = True
        except Exception:
            started = False
    # ② explorer 直接开目录 / ③ ShellExecuteW —— 逐级回落
    if not started:
        for attempt in (
            lambda: subprocess.Popen(["explorer", p]),
            lambda: os.startfile(p),  # noqa
            lambda: _shell_execute(p),
        ):
            try:
                attempt()
                started = True
                break
            except Exception:
                continue
    if not started:
        return False
    threading.Thread(target=_focus_explorer_async, args=(hint, known),
                     daemon=True).start()
    return True


def _shell_execute(path):
    """ShellExecuteW 打开(explorer 被拦时的最后一级回落)。"""
    import ctypes
    SW_SHOWNORMAL = 1
    r = ctypes.windll.shell32.ShellExecuteW(None, "open", path, None, None, SW_SHOWNORMAL)
    if int(r) <= 32:
        raise OSError("ShellExecuteW 返回 %s" % r)
    return True


def _pick_folder_win(initial="", owner=None):
    """弹 Windows 原生「浏览文件夹」框(SHBrowseForFolderW), 返回绝对路径; 取消 = ''。

    v1.5.16 致命修正(用户实测「选择…」永远失败):
      · **必须显式声明 restype = c_void_p**。SHBrowseForFolderW 返回的是 PIDL 指针
        (64 位)。ctypes 默认按 c_int(32 位) 解释返回值 -> 指针被截断 ->
        随后 SHGetPathFromIDListW 拿着野指针 -> **access violation, 进程直接崩**
        (日志里能看到 "access violation reading 0x..." 就是这个)。
      · SHGetPathFromIDListW / CoTaskMemFree 的入参也要按指针声明, 否则同样截断。
      · 挂 owner 窗口(界面窗口 hwnd) => 选择框是它的子窗口, 天然压在浏览器之上。
      · 弹框期间另有「反复置顶」看门狗, 双保险。
    """
    import ctypes
    from ctypes import wintypes

    BIF_RETURNONLYFSDIRS = 0x0001
    BIF_NEWDIALOGSTYLE = 0x0040          # 新建文件夹按钮 + 可输入路径
    BIF_EDITBOX = 0x0010
    BIF_USENEWUI = BIF_NEWDIALOGSTYLE | BIF_EDITBOX | BIF_RETURNONLYFSDIRS

    class BROWSEINFOW(ctypes.Structure):
        _fields_ = [("hwndOwner", wintypes.HWND),
                    ("pidlRoot", ctypes.c_void_p),
                    ("pszDisplayName", wintypes.LPWSTR),
                    ("lpszTitle", wintypes.LPCWSTR),
                    ("ulFlags", wintypes.UINT),
                    ("lpfn", ctypes.c_void_p),
                    ("lParam", wintypes.LPARAM),
                    ("iImage", ctypes.c_int)]

    shell32 = ctypes.windll.shell32
    ole32 = ctypes.windll.ole32
    user32 = ctypes.windll.user32

    # ---- 关键: 声明签名, 防止 64 位指针被按 32 位截断(这曾导致进程崩溃) ----
    shell32.SHBrowseForFolderW.argtypes = [ctypes.POINTER(BROWSEINFOW)]
    shell32.SHBrowseForFolderW.restype = ctypes.c_void_p          # PIDL = 指针!
    shell32.SHGetPathFromIDListW.argtypes = [ctypes.c_void_p,
                                             ctypes.c_wchar_p]
    shell32.SHGetPathFromIDListW.restype = wintypes.BOOL
    ole32.CoTaskMemFree.argtypes = [ctypes.c_void_p]
    ole32.CoTaskMemFree.restype = None
    user32.GetForegroundWindow.restype = wintypes.HWND

    buf = ctypes.create_unicode_buffer(260)
    bi = BROWSEINFOW()
    # owner: 优先用传进来的界面窗口; 退一步用当前前台窗口
    bi.hwndOwner = owner or user32.GetForegroundWindow()
    bi.pszDisplayName = ctypes.cast(buf, wintypes.LPWSTR)
    bi.lpszTitle = "选择 mod 下载保存到哪个文件夹"
    bi.ulFlags = BIF_USENEWUI

    ole32.CoInitializeEx(None, 0x2)      # APARTMENTTHREADED
    try:
        pidl = shell32.SHBrowseForFolderW(ctypes.byref(bi))
        if not pidl:
            return ""                    # 用户点了取消
        try:
            path = ctypes.create_unicode_buffer(1024)
            ok = shell32.SHGetPathFromIDListW(ctypes.c_void_p(pidl), path)
            got = path.value if ok else ""
        finally:
            ole32.CoTaskMemFree(ctypes.c_void_p(pidl))
        return os.path.abspath(got) if got else ""
    finally:
        try:
            ole32.CoUninitialize()
        except Exception:
            pass


def _pick_keep_front(hwnd, stop):
    """弹框期间不停把选择框拽到最前 + 闪一下, 保证用户看得见。

    v1.5.16: 所有 hwnd 相关的 Win32 函数都要声明签名 —— HWND 是 64 位指针,
    ctypes 默认按 c_int 解释返回值会截断 (和 SHBrowseForFolderW 那个崩因同类)。
    """
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
    user32.FindWindowW.restype = wintypes.HWND
    user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND,
                                    ctypes.c_int, ctypes.c_int,
                                    ctypes.c_int, ctypes.c_int, ctypes.c_uint]
    user32.SetWindowPos.restype = wintypes.BOOL
    user32.SetForegroundWindow.argtypes = [wintypes.HWND]
    user32.BringWindowToTop.argtypes = [wintypes.HWND]

    found = None
    while not stop.is_set():
        if not found:
            # 浏览文件夹对话框类名固定是 #32770
            h = user32.FindWindowW("#32770", None)
            if h:
                found = h
        if found:
            try:
                user32.SetWindowPos(found, -1, 0, 0, 0, 0, 0x0001 | 0x0002)  # TOPMOST
                user32.SetWindowPos(found, -2, 0, 0, 0, 0, 0x0001 | 0x0002)  # NOTOPMOST
                user32.SetForegroundWindow(found)
                user32.BringWindowToTop(found)
            except Exception:
                pass
        time.sleep(0.35)


def pick_folder(initial="", owner=None):
    """弹系统文件夹选择框(Windows) 与浏览结果的容器, 返回绝对路径; 取消返回 ''。

    v1.5.13: 给「下载目录」用, 免得玩家自己手打路径。
    v1.5.15: 原实现走 tkinter, 打包后必报 `No module named 'tkinter'`
      (PyInstaller 默认不收 tkinter)—— 选文件夹永远失败。改成 Windows 自带
      SHBrowseForFolderW(系统内核自带, 零依赖), 并且:
        · 挂 owner/前台窗口 => 框天然在浏览器之上
        · 起看门狗线程反复置顶 => 就算被盖住也会被拽回来
    v1.5.16: **关键** 修 SHBrowseForFolderW 返回值被 ctypes 按 32 位截断导致的
      access violation(用户实测「选择…」永远失败)。签名已在 _pick_folder_win
      里显式声明。tkinter 只作最后兜底。
    """
    if os.name == "nt":
        stop = threading.Event()
        try:
            hwnd = owner
            if not hwnd:
                try:
                    hwnd = find_manager_window()
                except Exception:
                    hwnd = None
            threading.Thread(target=_pick_keep_front, args=(hwnd, stop),
                             daemon=True).start()
            return _pick_folder_win(initial, hwnd or None)
        except Exception as e:
            log("pick_folder 原生框失败, 试 tkinter: %s" % str(e)[:160])
        finally:
            stop.set()

    # --- 兜底: tkinter ---
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        try:
            root.attributes("-topmost", True)
        except Exception:
            pass
        init = initial if (initial and os.path.isdir(initial)) else None
        p = filedialog.askdirectory(title="选择 mod 下载保存到哪个文件夹",
                                    initialdir=init, mustexist=False)
        try:
            root.destroy()
        except Exception:
            pass
        return os.path.abspath(p) if p else ""
    except Exception as e:
        log("pick_folder 不可用: %s" % str(e)[:160])
        return ""


# ===========================================================================
# 方案 / 进程 / 启动
# ===========================================================================

def presets_load():
    return read_json(PRESETS_PATH, {})


def presets_save(obj):
    write_json(PRESETS_PATH, obj)


_proc_cache = {"t": 0, "game": False, "launcher": False}
_lib_cache = {"t": 0, "data": None}


def invalidate_lib_cache():
    _lib_cache["data"] = None
    _lib_cache["t"] = 0


def proc_probe(cfg, force=False):
    now = time.time()
    if not force and now - _proc_cache["t"] < 5:
        return _proc_cache["game"], _proc_cache["launcher"]
    game = launcher = False
    try:
        out = subprocess.run(["tasklist", "/NH"], capture_output=True, text=True,
                             timeout=8, errors="replace",
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        txt = (out.stdout or "").lower()
        exe = os.path.basename(cfg.get("game_exe") or "ZenlessZoneZero.exe").lower()
        game = exe in txt
        launcher = "xxmi launcher.exe" in txt
    except Exception:
        pass
    _proc_cache.update({"t": now, "game": game, "launcher": launcher})
    return game, launcher


def launch_game(cfg):
    """启动游戏。ZZMI 需要管理员权限注入(d3dx.ini: require_admin=true),
    所以必须用 ShellExecute 的 runas 走 UAC, 否则 CreateProcess 会报 WinError 740。"""
    exe = cfg.get("launcher_exe") or ""
    if not os.path.isfile(exe):
        return False, "找不到 XXMI Launcher: %s" % (exe or "(未配置)")
    game, launcher = proc_probe(cfg, force=True)
    if launcher:
        return False, "XXMI Launcher 已经在运行, 请先关掉它"
    if game:
        return False, "游戏已经在运行了"
    importer = cfg.get("importer") or "ZZMI"
    workdir = os.path.dirname(exe)
    args = "--nogui --xxmi %s" % importer

    if os.name == "nt":
        try:
            import ctypes
            rc = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", exe, args, workdir, 1)      # 1 = SW_SHOWNORMAL
            if rc > 32:
                _proc_cache["t"] = 0
                return True, ("已请求管理员权限 —— 请在 UAC 弹窗点「是」, "
                              "游戏就会启动 (--nogui --xxmi %s)" % importer)
            if rc == 5:
                return False, "你取消了管理员授权, 没有启动\n(ZZMI 注入需要管理员权限, 请再点一次并选「是」)"
            if rc == 2:
                return False, "找不到启动器文件"
            return False, "启动被系统拒绝 (错误码 %d)" % rc
        except Exception as ex:
            log("runas 启动失败, 改用普通方式:", ex)

    try:
        subprocess.Popen([exe, "--nogui", "--xxmi", importer],
                         cwd=workdir, close_fds=True)
    except Exception as ex:
        if "740" in str(ex):
            return False, ("启动需要管理员权限但被拒绝。\n请右键本程序「以管理员身份运行」,"
                           "或手开 XXMI Launcher 点 Launch。")
        return False, "启动失败: %s" % ex
    _proc_cache["t"] = 0
    return True, "已启动游戏 (--nogui --xxmi %s)" % importer


BROWSER_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
]


def find_browser(custom=None):
    """找一个能用的浏览器: 用户自己指定过的优先, 否则 Edge -> Chrome。"""
    if custom and os.path.isfile(custom):
        return custom
    for b in BROWSER_CANDIDATES:
        if os.path.isfile(b):
            return b
    return None


def is_chromium_exe(exe):
    """判断是不是 Chrome 内核(只有它才认 --app / --user-data-dir 那套参数)。"""
    n = os.path.basename(exe or "").lower()
    return ("msedge" in n) or ("chrome" in n) or ("chromium" in n)


def screen_size():
    """主屏逻辑尺寸(像素)。本进程不声明 DPI 感知, 拿到的就是浏览器
    --window-size 认的那套坐标。"""
    if not _WIN:
        return 0, 0
    try:
        import ctypes
        u = ctypes.windll.user32
        return int(u.GetSystemMetrics(0)), int(u.GetSystemMetrics(1))
    except Exception:
        return 0, 0


def centered_position(size_str):
    """把一个 "W,H" 换算成居中的 "X,Y"。"""
    try:
        w, h = [int(x) for x in str(size_str).split(",")[:2]]
    except Exception:
        return ""
    sw, sh = screen_size()
    if sw < 200 or sh < 200:
        return ""
    return "%d,%d" % (max(0, (sw - w) // 2), max(0, (sh - h) // 2))


def window_geometry(size_cfg):
    """算出窗口怎么摆。返回 (是否最大化, --window-size, --window-position)。

    默认 / auto / max / fullscreen -> **打开就全屏(最大化)**;
    用户自己写死尺寸(如 "1000,700") -> 用这个尺寸, 位置居中。"""
    cfg = (size_cfg or "").strip()
    low = cfg.lower()
    if not cfg or low in ("auto", "max", "maximized", "full", "fullscreen") \
            or cfg == "1320,880":          # 1320,880 = 老版本的默认值, 也当自适应
        return True, "", ""
    if "," in cfg:
        return False, cfg, centered_position(cfg)
    return False, cfg, ""


def _maximize_app_window_async(tries=60):
    """等浏览器把窗口开出来, 再用 Win32 把它最大化 —— 双保险:
    --start-maximized 有些 Edge/Chrome 版本在 --app 模式下不认。"""
    before = set()
    try:
        before = set(h for h, _t in _chrome_app_windows())
    except Exception:
        pass
    for _ in range(max(1, tries)):
        time.sleep(0.15)
        try:
            wins = _chrome_app_windows()
        except Exception:
            continue
        cand = [h for h, t in wins if t.startswith(APP_NAME) and h not in before]
        if not cand:
            cand = [h for h, t in wins if t.startswith(APP_NAME)]
        if cand:
            hwnd = cand[0]
            try:
                import ctypes
                ctypes.windll.user32.ShowWindow(hwnd, 3)   # SW_MAXIMIZE
            except Exception:
                pass
            force_foreground(hwnd)
            return True
    return False


def _console_hwnd():
    """拿到本进程的控制台窗口句柄(没有控制台返回 0)。"""
    if not _WIN:
        return 0
    try:
        import ctypes
        return ctypes.windll.kernel32.GetConsoleWindow()
    except Exception:
        return 0


def hide_console(delay=1.6):
    """把那个黑色命令窗口藏起来(不销毁, 日志照写)。

    为什么要 delay: 服务刚起来时还要往控制台打印几行启动信息, 等窗口和浏览器都
    起来之后再藏, 用户就看不到闪烁了。日志同时写进 DATA_DIR\\zzmi.log, 出问题时
    可以手动跑 `--console` 或在界面里点「显示日志」把它调回来。
    """
    if not _WIN:
        return False
    if os.environ.get("ZZMI_KEEP_CONSOLE") == "1":
        return False
    time.sleep(delay)
    hwnd = _console_hwnd()
    if not hwnd:
        return False
    try:
        import ctypes
        user32 = ctypes.windll.user32
        user32.ShowWindow(hwnd, 0)          # SW_HIDE
        return True
    except Exception:
        return False


def show_console():
    """把命令窗口重新显示出来(用于排查问题)。"""
    hwnd = _console_hwnd()
    if not hwnd:
        return False
    try:
        import ctypes
        user32 = ctypes.windll.user32
        user32.ShowWindow(hwnd, 5)          # SW_SHOW
        user32.SetForegroundWindow(hwnd)
        return True
    except Exception:
        return False


def _chrome_app_windows():
    """列出本程序 app 窗口 (class=Chrome_WidgetWin_1): [(hwnd, 标题), ...]"""
    if not _WIN:
        return []
    import ctypes
    user32 = ctypes.windll.user32
    out = []
    proto = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)
    GetClassNameW = user32.GetClassNameW
    GetWindowTextW = user32.GetWindowTextW

    def _cb(hwnd, _l):
        try:
            buf = ctypes.create_unicode_buffer(64)
            GetClassNameW(hwnd, buf, 64)
            if buf.value == "Chrome_WidgetWin_1":
                t = ctypes.create_unicode_buffer(260)
                GetWindowTextW(hwnd, t, 260)
                out.append((hwnd, t.value))
        except Exception:
            pass
        return 1

    try:
        user32.EnumWindows(proto(_cb), None)
    except Exception:
        pass
    return out


class OPENFILENAMEW(ctypes.Structure):
    """comdlg32 的 GetOpenFileNameW 参数结构(64 位下 sizeof 应为 152)。"""
    _fields_ = [
        ("lStructSize", wintypes.DWORD), ("hwndOwner", wintypes.HWND),
        ("hInstance", wintypes.HINSTANCE), ("lpstrFilter", wintypes.LPCWSTR),
        ("lpstrCustomFilter", wintypes.LPWSTR), ("nMaxCustFilter", wintypes.DWORD),
        ("nFilterIndex", wintypes.DWORD), ("lpstrFile", wintypes.LPWSTR),
        ("nMaxFile", wintypes.DWORD), ("lpstrFileTitle", wintypes.LPWSTR),
        ("nMaxFileTitle", wintypes.DWORD), ("lpstrInitialDir", wintypes.LPCWSTR),
        ("lpstrTitle", wintypes.LPCWSTR), ("Flags", wintypes.DWORD),
        ("nFileOffset", wintypes.WORD), ("nFileExtension", wintypes.WORD),
        ("lpstrDefExt", wintypes.LPCWSTR), ("lCustData", wintypes.LPARAM),
        ("lpfnHook", wintypes.LPVOID), ("lpTemplateName", wintypes.LPCWSTR),
        ("pvReserved", wintypes.LPVOID), ("dwReserved", wintypes.DWORD),
        ("FlagsEx", wintypes.DWORD)]


def pick_browser_exe():
    """机器上一个 Chrome 内核浏览器都没有时, 弹文件框让用户自己挑一个 exe。

    只在 Windows 上可用, 且整体包了兜底: 对话框出不来就返回 None,
    调用方再退回系统默认浏览器, 绝不会卡住或崩掉。"""
    if not _WIN:
        return None
    try:
        import ctypes
        from ctypes import wintypes, byref, create_unicode_buffer

        user32 = ctypes.windll.user32
        user32.MessageBoxW.restype = ctypes.c_int
        user32.MessageBoxW.argtypes = [wintypes.HWND, wintypes.LPCWSTR,
                                       wintypes.LPCWSTR, wintypes.UINT]
        comdlg32 = ctypes.windll.comdlg32
        comdlg32.GetOpenFileNameW.restype = wintypes.BOOL
        comdlg32.GetOpenFileNameW.argtypes = [ctypes.POINTER(OPENFILENAMEW)]

        user32.MessageBoxW(None,
                           "没找到 Edge / Chrome。\n\n"
                           "接下来请手动选一个浏览器程序(建议先把 Edge 或 Chrome 装上,\n"
                           "那样的无地址栏独立窗口效果最好)。",
                           APP_NAME, 0x40 | 0x1000)   # MB_ICONINFORMATION|MB_SETFOREGROUND

        buf = create_unicode_buffer(4096)
        ofn = OPENFILENAMEW()
        ofn.lStructSize = ctypes.sizeof(OPENFILENAMEW)
        ofn.lpstrFile = ctypes.cast(buf, wintypes.LPWSTR)
        ofn.nMaxFile = 4096
        ofn.lpstrFilter = "浏览器程序 (*.exe)\0*.exe\0所有文件 (*.*)\0*.*\0\0"
        ofn.lpstrTitle = "选择用来打开界面的浏览器"
        ofn.Flags = 0x00001000 | 0x00000800 | 0x00000004   # FILEMUSTEXIST|EXPLORER|HIDEREADONLY
        if comdlg32.GetOpenFileNameW(byref(ofn)):
            p = buf.value.strip()
            return p if p and os.path.isfile(p) else None
    except Exception as ex:
        log("选择浏览器对话框不可用:", ex)
    return None


def _browser_profile():
    """v1.5.20: 给本程序单独一个浏览器数据目录。

    有了它, 界面浏览记录/缓存只写进这个专属目录, **不会进你自己的 Edge 历史**,
    Edge 里再也搜不到 127.0.0.1 这些记录(用户反馈的历史残留问题)。
    顺带把上一次残留的历史文件擦掉, 目录里始终只有本程序自己。"""
    prof = os.path.join(DATA_DIR, "browser-profile")
    try:
        os.makedirs(prof, exist_ok=True)
    except Exception:
        return None
    try:
        d = os.path.join(prof, "Default")
        for nm in ("History", "History-journal", "History Provider Cache",
                   "Current Session", "Current Tabs", "Last Session",
                   "Last Tabs", "Sessions", "Shortcuts", "Visited Links"):
            for p in (os.path.join(d, nm), os.path.join(d, nm + "-journal")):
                if os.path.isfile(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass
    except Exception:
        pass
    return prof


def _disable_edge_super_drag(prof):
    """v1.5.29: 关掉 Edge 的「超级拖放」—— 拖选文字松手会弹出
    「松开鼠标以搜索文本」蓝色提示条, 像浏览器多像网页插件, 玩家很反感。
    写法: 往**本程序专属浏览器目录**的 Default/Preferences 里写
    edge_super_drag_drop.enabled=false(键名取自 msedge.dll 内部设置路径),
    只影响管家自己的窗口, 用户自己日常用的 Edge 完全不动。"""
    pf = os.path.join(prof, "Default", "Preferences")
    try:
        d = {}
        if os.path.isfile(pf):
            with open(pf, "r", encoding="utf-8", errors="replace") as f:
                d = json.load(f)
        if not isinstance(d, dict):
            d = {}
        sec = d.get("edge_super_drag_drop")
        if isinstance(sec, dict) and sec.get("enabled") is False:
            return                      # 已经关过, 不重复写
        d["edge_super_drag_drop"] = dict(sec, enabled=False) \
            if isinstance(sec, dict) else {"enabled": False}
        tmp = pf + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False)
        os.replace(tmp, pf)
    except Exception as ex:
        log("关闭超级拖放失败(不影响使用):", ex)


def open_app_window(url, size=None, browser=None):
    """用 Edge/Chrome 的 --app 模式开独立窗口(秒开, 无地址栏/标签栏)。
    默认**打开就全屏**(最大化); 设置里把 win_size 写成 1000,700 才用固定尺寸(居中)。
    用户手动选了别的浏览器(非 Chrome 内核)时退化成普通标签页打开, 保证至少能用。"""
    b = browser or find_browser()
    maximize, size, pos = window_geometry(size)
    if b and not is_chromium_exe(b):
        # 火狐这类不认 --app, 直接用普通窗口打开
        subprocess.Popen([b, url], close_fds=True)
        log("已用用户指定的浏览器打开:", os.path.basename(b))
        return
    if b:
        args = [b, "--app=" + url]
        prof = _browser_profile()
        if prof:
            args.append("--user-data-dir=" + prof)
            _disable_edge_super_drag(prof)
        if maximize:
            args.append("--start-maximized")
            sw, sh = screen_size()
            if sw >= 400 and sh >= 300:
                # 万一某些版本不认 start-maximized, 也让它铺满整块屏
                args.append("--window-size=%d,%d" % (sw, sh))
                args.append("--window-position=0,0")
        else:
            if size:
                args.append("--window-size=" + size)
            if pos:
                args.append("--window-position=" + pos)
        args += ["--proxy-server=direct://",
                 "--proxy-bypass-list=<-loopback>",
                 "--no-first-run",
                 "--no-default-browser-check",
                 # msEdgeSuperDragDrop* = Edge「超级拖放」的功能总开关(键名取自
                 # msedge.dll); 不认识的 feature 名会被静默忽略, 无副作用
                 "--disable-features=Translate,msEdgeSuperDragDropSupported,"
                 "msEdgeSuperDragDropSupportedChina"]
    try:
        subprocess.Popen(args, close_fds=True)
        log("已用独立窗口打开: %s  %s" % (os.path.basename(b),
                                        "全屏" if maximize else ("尺寸=" + size)))
        if maximize:
            threading.Thread(target=_maximize_app_window_async,
                             daemon=True).start()
    except Exception as ex:
        log("独立窗口启动失败, 改用默认浏览器:", ex)
        webbrowser.open(url)


# ===========================================================================
# 应用状态
# ===========================================================================

SLIM_DROP = ("sub_dirs", "hashes", "ini_roots", "char_auto")


class App(object):
    # v1.5.10: 界面窗口关闭后等这么多秒再退出(给 F5 刷新留时间, 刷新会先 hello)
    AUTOQUIT_DELAY = 5.0

    def __init__(self):
        self.cfg = dict(DEFAULT_CONFIG)
        self.scan = ScanResult()
        self.lock = threading.RLock()
        self.token = os.urandom(9).hex()
        self._autoquit_timer = None
        self.detect_report = {"done": True, "step": "", "found": None,
                              "candidates": [], "message": ""}
        self.last_error = ""
        self.httpd = None
        self.hotkey = HotkeyManager(self)

    def load_config(self):
        raw = read_json(CONFIG_PATH, None)
        if not isinstance(raw, dict) or "zzmi_root" not in raw:
            if raw is not None:
                try:
                    shutil.copyfile(CONFIG_PATH, os.path.join(
                        DATA_DIR, "config.old-%s.json" % time.strftime("%Y%m%d-%H%M%S")))
                except Exception:
                    pass
            return False
        cfg = dict(DEFAULT_CONFIG)
        cfg.update({k: v for k, v in raw.items() if k in DEFAULT_CONFIG})
        # 一次性迁移: 旧版本写进配置里的默认呼出键 Ctrl+Alt+K -> 新的默认 F9
        if str(cfg.get("hotkey") or "").replace(" ", "").lower() == "ctrl+alt+k":
            cfg["hotkey"] = DEFAULT_CONFIG["hotkey"]
            try:
                write_json(CONFIG_PATH, cfg)
                log("呼出键已迁移为 %s" % cfg["hotkey"])
            except Exception:
                pass
        self.cfg = cfg
        return True

    def save_config(self):
        write_json(CONFIG_PATH, self.cfg)

    # ---- v1.5.10: 界面关闭 -> 自动退出 ---------------------------------
    def cancel_autoquit(self):
        with self.lock:
            t = self._autoquit_timer
            if t:
                t.cancel()
                self._autoquit_timer = None

    def schedule_autoquit(self):
        with self.lock:
            self.cancel_autoquit()
            t = threading.Timer(self.AUTOQUIT_DELAY, self._autoquit_fire)
            t.daemon = True
            self._autoquit_timer = t
            t.start()

    def _autoquit_fire(self):
        self._autoquit_timer = None
        log("界面窗口已关闭, %g 秒内没有重新打开, 程序自动退出"
            % self.AUTOQUIT_DELAY)
        try:
            if self.httpd:
                self.httpd.server_close()
        except Exception:
            pass
        os._exit(0)

    def set_root(self, zzmi_root, importer=None, mods_dir=None):
        zzmi_root = (zzmi_root or "").strip().strip('"').rstrip("\\/")
        if not os.path.isdir(zzmi_root):
            return False, "目录不存在: %s" % zzmi_root
        score, info = score_xxmi_root(zzmi_root)
        if score < 8:
            return False, ("这看起来不是 XXMI Launcher 的安装目录。\n"
                           "请选择包含 Resources\\Bin\\XXMI Launcher.exe "
                           "以及 ZZMI 子目录的那一层。")
        importers = info.get("importers") or []
        imp = importer or self.cfg.get("importer") or "ZZMI"
        if importers and imp not in importers:
            imp = ([x for x in importers if x.upper() == "ZZMI"]
                   or [x for x in importers if "ZZ" in x.upper()] or importers)[0]
        self.cfg["zzmi_root"] = zzmi_root
        self.cfg["launcher_exe"] = info.get("launcher_exe", "")
        self.cfg["importer"] = imp
        self.cfg["mods_dir"] = mods_dir or os.path.join(zzmi_root, imp, "Mods")
        exe = game_exe_from_launcher_config(info.get("config_json"), imp)
        if exe:
            self.cfg["game_exe"] = exe
        # v1.5.5: 换根目录时保留玩家自己登记的仓库 —— 只把新根下已经不存在的剪掉,
        # 再把这次探测到的合并进去(探测只是"顺手发现", 不会顶掉玩家的列表)
        keep = [l for l in (self.cfg.get("libraries") or [])
                if os.path.isdir(safe_join(zzmi_root, l) or "")]
        for d in detect_libraries(zzmi_root, self.cfg["mods_dir"]):
            if d not in keep:
                keep.append(d)
        self.cfg["libraries"] = keep
        # 锁定的绝对路径仓库(在别的盘)跟根目录无关, 原样保留
        self.save_config()
        invalidate_lib_cache()
        return True, "已保存"

    def meta(self):
        return {"pinned_mods": self.cfg.get("pinned_mods") or [],
                "pinned_cats": self.cfg.get("pinned_cats") or [],
                "pinned_chars": self.cfg.get("pinned_chars") or [],
                "usage": self.cfg.get("usage") or {}}

    def touch_usage(self, ids, exclude=None):
        """启用 / 切变体时记录一次「使用时间」, 供默认排序使用。
        exclude 里是批量操作失败的 id, 不算用过。只写配置, 不动 mod 文件。"""
        bad = set(exclude or [])
        now = time.time()
        scan = getattr(self, "scan", None)
        with self.lock:
            u = self.cfg.setdefault("usage", {})
            changed = False
            for i in (ids or []):
                if not i or i in bad:
                    continue
                if scan is not None and getattr(scan, "by_id", None) \
                        and i not in scan.by_id:
                    continue  # 不认识的历史 id 不记, 防表被垃圾撑大
                u[i] = now
                changed = True
            if not changed:
                return
            if len(u) > 2000:  # 防膨胀: 只保留最近 2000 条
                keep = sorted(u.items(), key=lambda kv: -kv[1])[:2000]
                self.cfg["usage"] = dict(keep)
            self.save_config()

    def rescan(self):
        with self.lock:
            md = find_mods_dir(self.cfg)
            self.scan = scan_mods(md, self.cfg.get("char_overrides") or {},
                                  self.cfg.get("thumb_overrides") or {},
                                  self.meta()) if md else ScanResult()
            if self.scan.thumb_srcs:
                n = enqueue_thumbs(self.scan.thumb_srcs)
                if n:
                    log("需生成缩略图 %d 张(后台进行)" % n)
            return self.scan

    def mods_dir(self):
        return find_mods_dir(self.cfg)

    def state(self, with_entries=True, probe=True):
        s = self.scan
        md = self.mods_dir()
        game = launcher = False
        if probe:
            game, launcher = proc_probe(self.cfg)
        st = {
            "app": APP_NAME, "version": VERSION,
            "configured": bool(self.cfg.get("zzmi_root")),
            "zzmi_root": self.cfg.get("zzmi_root", ""),
            "mods_dir": md,
            "mods_dir_exists": bool(md and os.path.isdir(md)),
            "launcher_exe": self.cfg.get("launcher_exe", ""),
            "launcher_exists": bool(self.cfg.get("launcher_exe")
                                    and os.path.isfile(self.cfg["launcher_exe"])),
            "importer": self.cfg.get("importer", "ZZMI"),
            "game_exe": self.cfg.get("game_exe", ""),
            "libraries": self.cfg.get("libraries", []),
            "libs_abs": self.cfg.get("libs_abs", []),
            "custom_dirs": self.cfg.get("custom_dirs", []),
            "theme": self.cfg.get("theme", "dark"),
            "hide_preview": bool(self.cfg.get("hide_preview")),
            "hotkey": self.cfg.get("hotkey", "F9"),
            "hotkey_ok": self.hotkey.ok is not False,
            "downloads_dir": gb_downloads_dir(self.cfg),
            "show_translated": bool(self.cfg.get("show_translated", True)),
            "tg_enabled": bool(TG_ENABLED),   # v1.5.22: 蓝飞机总开关(关=前端隐藏 tab)
            "update_repo": self.cfg.get("update_repo", UPDATE_REPO),
            "win_size": self.cfg.get("win_size") or "auto",
            "stats": s.stats, "categories": s.categories, "chars": s.chars,
            "pinned_mods": self.cfg.get("pinned_mods") or [],
            "pinned_cats": self.cfg.get("pinned_cats") or [],
            "pinned_chars": self.cfg.get("pinned_chars") or [],
            "conflicts": s.conflicts, "presets": presets_load(),
            "journal": [{"ts": r.get("ts"), "kind": r.get("kind"),
                         "name": r.get("name") or os.path.basename(r.get("src") or ""),
                         "enable": r.get("enable"), "t": human_time(r.get("ts"))}
                        for r in journal_read(30)[::-1]],
            "detect": self.detect_report,
            "scan_seconds": round(s.duration, 2),
            "thumb_engine": "Pillow" if _get_pil() else "原图直出",
            "thumb_pending": _thumb_q.qsize(),
            "error": self.last_error,
            "game_running": game, "launcher_running": launcher,
        }
        if with_entries:
            st["entries"] = [{k: v for k, v in e.items() if k not in SLIM_DROP}
                             for e in s.entries]
        return st

    def find_entries(self, ids):
        return [self.scan.by_id[i] for i in (ids or []) if i in self.scan.by_id]

    def scope_entries(self, scope):
        scope = scope or {}
        t, v = scope.get("type"), scope.get("value")
        E = self.scan.entries
        if t == "category":
            return [e for e in E if e["category"] == v]
        if t == "char":
            return [e for e in E if e["char"] == v]
        if t == "status":
            return [e for e in E if e["enabled"] == (v == "enabled")]
        return list(E)


# ===========================================================================
# HTTP 服务
# ===========================================================================

def run_detection(app):
    """后台自动查找 ZZMI 并写入配置 (供首启与界面「自动查找」共用)。"""
    try:
        def prog(i, t):
            app.detect_report["step"] = "已检查 %d / %d 个目录…" % (i, t)
        cfg, cands = autodetect_config(progress=prog)
        if cfg:
            app.cfg.update({k: v for k, v in cfg.items() if v != ""})
            app.save_config()
            app.rescan()
            app.detect_report = {"done": True, "step": "",
                                 "found": cfg["zzmi_root"], "candidates": cands,
                                 "message": "已自动找到: %s" % cfg["zzmi_root"]}
        else:
            app.detect_report = {"done": True, "step": "", "found": None,
                                 "candidates": [],
                                 "message": "没找到, 请手动填写 ZZMI 路径"}
    except Exception as ex:
        app.detect_report = {"done": True, "step": "", "found": None,
                             "candidates": [],
                             "message": "自动查找出错: %s" % ex}


def _parse_ver(s):
    """把 '1.4.6' / 'v1.4' / '1.4.6.2' 解析成 (主, 次, 修订) 三元组, 便于比较。"""
    m = re.search(r"(\d+)(?:\.(\d+))?(?:\.(\d+))?", str(s or ""))
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2) or 0), int(m.group(3) or 0))


def check_update(current_version, repo=None):
    """查 GitHub 最新 release, 判断是否出新版本。
    返回 {ok, update_available, latest, current, url, error}。"""
    repo = (repo or "").strip() or UPDATE_REPO
    if not repo:
        return {"ok": False, "error": "未配置更新仓库"}
    url = "https://api.github.com/repos/%s/releases/latest" % repo
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "ZZMI-Mod-Manager",
                     "Accept": "application/vnd.github+json"})
        # 绕过系统代理直连(GitHub 外部访问不需要本机那个代理, 与仓库里其他 GitHub 脚本一致)
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8", "replace"))
        tag = (data.get("tag_name") or "").lstrip("vV")
        html = data.get("html_url", "")
        if not tag:
            return {"ok": True, "update_available": False, "latest": "",
                    "current": current_version,
                    "url": html or ("https://github.com/%s/releases" % repo)}
        latest = _parse_ver(tag)
        cur = _parse_ver(current_version)
        avail = latest is not None and (cur is None or latest > cur)
        return {"ok": True, "update_available": avail, "latest": tag,
                "current": current_version,
                "url": html or ("https://github.com/%s/releases" % repo)}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


# ===========================================================================
# v1.5.12: GameBanana Mod 下载区
# ---------------------------------------------------------------------------
# 玩家在界面里点「⬇ 下载区」, 粘贴一个 GameBanana 链接(分类 / 游戏 mod 列表 / 单个 mod),
# 后端去抓上面所有 mod 的名字、预览图、作者, 一键下载到本地下载目录。
# 走的都是 GameBanana 公开 API(apiv11), 只读别人网站, 不碰本地任何 mod 文件。
# 名字是英文的, 顺带翻译成中文(默认 MyMemory 免费接口, 结果本地缓存)。
# ===========================================================================
GB_API = "https://gamebanana.com/apiv11"
GB_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
         "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
GB_CAT_RE = re.compile(r"/mods/cats/(\d+)", re.I)
GB_GAMEMODS_RE = re.compile(r"/mods/games/(\d+)", re.I)
GB_GAME_RE = re.compile(r"/games/(\d+)", re.I)
GB_MOD_RE = re.compile(r"/mods/(\d+)(?:[/?#]|$)", re.I)
# v1.5.13: 角色分类。Character Skins(30305) 下有 62 个角色子分类
GB_CHAR_CAT = 30305            # 「Character Skins」分类 id
GB_SUBS_CACHE_PATH = os.path.join(DATA_DIR, "gb_subs_cache.json")
GB_DL_HISTORY_PATH = os.path.join(DATA_DIR, "gb_dl_history.json")
_gb_subs_cache = None
_gb_dl_hist = None
_gb_dl_hist_lock = threading.Lock()
GB_IMG_CACHE = os.path.join(DATA_DIR, "gb_img_cache")
GB_TRANS_CACHE_PATH = os.path.join(DATA_DIR, "gb_trans_cache.json")
GB_JOBS = {}                 # 下载任务表: job_id -> 状态字典
GB_JOBS_LOCK = threading.Lock()
_gb_job_seq = [0]
_gb_trans_cache = None
_gb_trans_lock = threading.Lock()


def gb_http_json(url, timeout=20):
    """GET 一个 GameBanana JSON 接口, 失败重试 3 次(网络抖)。"""
    last = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": GB_UA,
                              "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:
            last = e
            time.sleep(0.6 * (attempt + 1))
    raise last


def gb_parse_url(raw):
    """把玩家粘的链接(或纯编号)解析成 (kind, id, err)。
    kind: 'category' 分类页 | 'game' 游戏的全部 mod | 'mod' 单个 mod。"""
    s = (raw or "").strip()
    if not s:
        return None, None, "请输入 GameBanana 链接"
    if re.fullmatch(r"\d+", s):
        return "category", s, ""            # 纯数字默认当成分类 id
    if not s.lower().startswith(("http://", "https://")):
        s = "https://" + s
    u = urllib.parse.urlparse(s)
    host = (u.netloc or "").lower()
    if "gamebanana.com" not in host:
        return None, None, "只支持 gamebanana.com 的链接"
    path = u.path or ""
    m = GB_CAT_RE.search(path)
    if m:
        return "category", m.group(1), ""
    m = GB_GAMEMODS_RE.search(path)
    if m:
        return "game", m.group(1), ""
    m = GB_GAME_RE.search(path)
    if m:
        return "game", m.group(1), ""
    m = GB_MOD_RE.search(path)
    if m:
        return "mod", m.group(1), ""
    return None, None, "没认出链接类型(支持 分类页 / 游戏 mod 页 / 单个 mod 页)"


def _gb_img_url(im, prefer=530):
    base = (im or {}).get("_sBaseUrl") or ""
    if not base:
        return ""
    f = (im.get("_sFile%d" % prefer) if prefer else "") or im.get("_sFile") or ""
    if not f:
        return ""
    return base.rstrip("/") + "/" + f


def _gb_item(rec):
    """把一条 API 记录压成前端要用的字段。"""
    imgs = ((rec.get("_aPreviewMedia") or {}).get("_aImages") or [])
    prevs = []
    for im in imgs:
        u = _gb_img_url(im, 530)
        if u:
            prevs.append(u)
    sub = rec.get("_aSubmitter") or {}
    return {
        "id": rec.get("_idRow"),
        "name": rec.get("_sName") or "",
        "url": rec.get("_sProfileUrl") or "",
        "author": sub.get("_sName") or "",
        "likes": rec.get("_nLikeCount") or 0,
        "views": rec.get("_nViewCount") or 0,
        "version": rec.get("_sVersion") or "",
        "has_files": bool(rec.get("_bHasFiles")),
        "preview": prevs[0] if prevs else "",
        "previews": prevs[:8],
        "added": rec.get("_tsDateAdded") or 0,
    }


def gb_list(kind, gid, page=1, perpage=30, cat=None):
    """抓一页 mod 列表。perpage 上限 50(GameBanana 规定, 超过报 400)。

    v1.5.13: cat 给出时强制按该分类过滤 —— 用于「角色分类」筛选
    (点某个角色 -> 只列这个角色的 mod)。
    """
    try:
        page = max(1, int(page))
    except (TypeError, ValueError):
        page = 1
    try:
        perpage = max(1, min(50, int(perpage)))
    except (TypeError, ValueError):
        perpage = 30
    if cat:
        key, gid = "Generic_Category", str(cat)
    else:
        key = "Generic_Category" if kind == "category" else "Generic_Game"
    url = ("%s/Mod/Index?_aFilters[%s]=%s&_nPage=%d&_nPerpage=%d"
           % (GB_API, key, gid, page, perpage))
    d = gb_http_json(url)
    recs = d.get("_aRecords") or []
    meta = d.get("_aMetadata") or {}
    return {
        "kind": kind, "gid": gid, "page": page, "perpage": perpage,
        "total": meta.get("_nRecordCount") or len(recs),
        "items": [_gb_item(r) for r in recs],
    }


def gb_mod_files(mid):
    """抓单个 mod 的文件清单(下载链接 + md5 + 杀毒结果)。"""
    d = gb_http_json("%s/Mod/%s/ProfilePage" % (GB_API, mid))
    files = []
    for f in (d.get("_aFiles") or []):
        files.append({
            "name": f.get("_sFile") or "",
            "size": f.get("_nFilesize") or 0,
            "url": f.get("_sDownloadUrl") or "",
            "md5": f.get("_sMd5Checksum") or "",
            "av": f.get("_sAvResult") or "",
        })
    return {"id": mid, "name": d.get("_sName") or "",
            "url": d.get("_sProfileUrl") or "",
            "files": files, "text": d.get("_sText") or ""}


def gb_downloads_dir(cfg):
    """下载目录: 配置里指定, 否则默认 数据目录/downloads。始终保证存在。"""
    p = (cfg.get("downloads_dir") or "").strip()
    if not p:
        p = os.path.join(DATA_DIR, "downloads")
    try:
        os.makedirs(p, exist_ok=True)
    except Exception:
        p = os.path.join(DATA_DIR, "downloads")
        try:
            os.makedirs(p, exist_ok=True)
        except Exception:
            pass
    return p


def gb_list_downloads(cfg):
    d = gb_downloads_dir(cfg)
    out = []
    try:
        names = os.listdir(d)
    except OSError:
        names = []
    for n in sorted(names, key=lambda s: s.lower()):
        p = os.path.join(d, n)
        if not os.path.isfile(p):
            continue
        try:
            st = os.stat(p)
        except OSError:
            continue
        out.append({"name": n, "size": st.st_size,
                    "size_h": human_size(st.st_size), "mtime": st.st_mtime})
    return {"dir": d, "items": out}


def gb_unique_path(folder, name):
    """文件名消毒 + 重名自动加 (2) (3)…, 绝不覆盖已有文件。"""
    name = os.path.basename((name or "").strip()) or "mod.zip"
    name = re.sub(r'[\\/:*?"<>|]+', "_", name).strip() or "mod.zip"
    p = os.path.join(folder, name)
    if not os.path.exists(p):
        return p
    stem, ext = os.path.splitext(name)
    i = 2
    while True:
        p = os.path.join(folder, "%s (%d)%s" % (stem, i, ext))
        if not os.path.exists(p):
            return p
        i += 1


def gb_new_job(mod_id, name):
    with GB_JOBS_LOCK:
        _gb_job_seq[0] += 1
        jid = "gb%d" % _gb_job_seq[0]
        GB_JOBS[jid] = {
            "id": jid, "state": "queued", "mod_id": mod_id, "name": name or "",
            "cur": 0, "total": 0, "received": 0, "size": 0, "pct": 0,
            "done": 0, "ok_n": 0, "err_n": 0, "results": [],
            "msg": "排队中…", "path": "", "ts": time.time(),
        }
        # 清掉 1 小时前就结束的老任务, 防表膨胀
        for k in [k for k, v in GB_JOBS.items()
                  if v.get("state") in ("done", "error")
                  and time.time() - v.get("ts", 0) > 3600]:
            GB_JOBS.pop(k, None)
    return jid


def gb_set_job(jid, **kw):
    with GB_JOBS_LOCK:
        j = GB_JOBS.get(jid)
        if j:
            j.update(kw)


def gb_get_job(jid):
    with GB_JOBS_LOCK:
        j = GB_JOBS.get(jid)
        return dict(j) if j else None


def _gb_dl_one(url, dest, jid, idx, nfiles):
    req = urllib.request.Request(url, headers={"User-Agent": GB_UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        total = 0
        try:
            total = int(r.headers.get("Content-Length") or 0)
        except (TypeError, ValueError):
            total = 0
        got = 0
        with open(dest, "wb") as f:
            while True:
                chunk = r.read(65536)
                if not chunk:
                    break
                f.write(chunk)
                got += len(chunk)
                gb_set_job(jid, received=got, size=total,
                           pct=int(got * 100 / total) if total else 0,
                           cur=idx, total=nfiles)
    return got


def gb_download_worker(jid, cfg, mod_id, picks=None):
    """picks: 只下这些文件名(列表); None/空 = 全下。v1.5.13"""
    try:
        gb_set_job(jid, state="resolving", msg="正在解析下载地址…")
        info = gb_mod_files(mod_id)
        allf = [f for f in info["files"] if f.get("url")]
        if not allf:
            gb_set_job(jid, state="error", msg="这个 mod 没有可下载的文件")
            return
        if picks:
            want = set(str(x) for x in picks)
            files = [f for f in allf if (f.get("name") or "") in want]
            if not files:
                files = allf           # 名字对不上就别卡着, 退回全下
        else:
            files = allf
        folder = gb_downloads_dir(cfg)
        gb_set_job(jid, state="downloading", total=len(files),
                   name=info.get("name") or "", done=0, ok_n=0, err_n=0,
                   results=[])
        last_path = ""
        ok_n, err_n = 0, 0
        results = []
        for i, f in enumerate(files, 1):
            fname = f.get("name") or ("mod_%s_%d.zip" % (mod_id, i))
            dest = gb_unique_path(folder, fname)
            gb_set_job(jid, cur=i, received=0, size=f.get("size") or 0, pct=0,
                       path=dest,
                       msg="下载中 %d/%d: %s" % (i, len(files), os.path.basename(dest)))
            try:
                _gb_dl_one(f["url"], dest, jid, i, len(files))
                ok_n += 1
                last_path = dest
                gb_hist_mark(mod_id, fname, dest)
                results.append({"file": fname, "ok": True, "path": dest,
                                "size": os.path.getsize(dest)})
            except Exception as fe:
                err_n += 1
                # 半截文件别留着骗人
                try:
                    if os.path.isfile(dest):
                        os.remove(dest)
                except OSError:
                    pass
                results.append({"file": fname, "ok": False,
                                "msg": str(fe)[:160]})
                log("GameBanana 下载失败 %s: %s" % (fname, str(fe)[:120]))
            gb_set_job(jid, done=i, ok_n=ok_n, err_n=err_n, results=list(results))
        if ok_n and not err_n:
            gb_set_job(jid, state="done", pct=100, path=last_path,
                       msg="完成: %d 个文件" % ok_n)
        elif ok_n:
            gb_set_job(jid, state="done", pct=100, path=last_path,
                       msg="部分完成: 成功 %d, 失败 %d" % (ok_n, err_n))
        else:
            gb_set_job(jid, state="error",
                       msg="全部失败(%d 个文件)" % err_n)
        log("GameBanana 下载结束: 成功 %d 失败 %d" % (ok_n, err_n))
    except Exception as e:
        gb_set_job(jid, state="error", msg="下载失败: %s" % str(e)[:180])


def gb_start_download(cfg, mod_id, name="", picks=None):
    jid = gb_new_job(mod_id, name)
    threading.Thread(target=gb_download_worker, args=(jid, cfg, mod_id, picks),
                     daemon=True).start()
    return jid


def _gb_trans_load():
    global _gb_trans_cache
    if _gb_trans_cache is None:
        d = read_json(GB_TRANS_CACHE_PATH, None)
        _gb_trans_cache = d if isinstance(d, dict) else {}
    return _gb_trans_cache


def _gb_trans_save():
    try:
        write_json(GB_TRANS_CACHE_PATH, _gb_trans_cache or {})
    except Exception:
        pass


def _gb_trans_fetch(t):
    """只负责发翻译请求, 不碰缓存。翻不出来/失败一律返回原文。"""
    url = ("https://api.mymemory.translated.net/get?q=%s&langpair=en|zh-CN"
           % urllib.parse.quote(t[:480]))
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": GB_UA})
            with urllib.request.urlopen(req, timeout=15) as r:
                d = json.loads(r.read().decode("utf-8", "replace"))
            got = ((d.get("responseData") or {}).get("translatedText") or "").strip()
            return got if (got and got.lower() != t.lower()) else t
        except Exception:
            time.sleep(0.4 * (attempt + 1))
    return t


def _gb_trans_prep(s):
    """v1.5.22: 把"没法直译"的原始名清洗成能翻的短语。

    实测坑: 下载区文件名(如 white_high_heels_recolor_3.zip)原样丢给机翻,
    MyMemory 会整串吐回原文 = 等于没翻。GameBanana 文件对象里没有独立的
    "文件简介"字段(网页文件那一行显示的就是文件名本身), 所以"看简介再翻"
    落到实处就是这步清洗:
      去后缀 -> 下划线/连字符换空格 -> 拆 camelCase -> 压缩空格
      -> 去掉纯数字/版本号/扩展名碎片 -> 截前 6 个词(机翻短句更准)
    """
    s = str(s or "").strip()
    if not s:
        return ""
    s = os.path.splitext(s)[0] if "." in s else s      # 去 .zip/.7z 等后缀
    s = re.sub(r"[\.\_]+", " ", s)                      # 分隔符换空格
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", s)          # camelCase 拆词
    s = re.sub(r"\s+", " ", s).strip()
    keep = []
    for tk in s.split(" "):
        if not tk:
            continue
        if re.fullmatch(r"[0-9]+", tk):                 # 纯数字
            continue
        if re.fullmatch(r"v\d+(?:\.\d+)*", tk, re.I):   # 版本号 v1.0.7
            continue
        if tk.lower() in ("zip", "7z", "rar", "ini", "cfg"):
            continue
        keep.append(tk)
    return " ".join(keep[:6]).strip()


def _gb_trans_clean_fetch(t):
    """v1.5.22: 文件名专用机翻。清洗后短语也翻不动就保留清洗前语义原样,
    绝不让请求失败把整条翻译链打断。"""
    p = _gb_trans_prep(t)
    if not p:
        return t
    got = _gb_trans_fetch(p)
    return got if (got and got != p) else t


def _gb_trans_clean_map(texts):
    """v1.5.22: 批量文件名翻译(走清洗版 fetch)。独立小缓存文件名空间,
    不与标题缓存互踩。翻不出来原样返回, 绝不报错打断。"""
    texts = [str(x) for x in (texts or [])][:40]
    todo = [t for t in texts if t]
    todo = list(dict.fromkeys(todo))
    if not todo:
        return {}
    cache = _gb_trans_load()
    out = {}
    miss = []
    for t in todo:
        k = "\x00fn\x00" + t                 # 文件名独立命名空间, 防与标题串缓存
        if k in cache:
            out[t] = cache[k]
        else:
            miss.append((t, k))
    if miss:
        try:
            import concurrent.futures as _cf
            with _cf.ThreadPoolExecutor(max_workers=4) as ex:
                futs = {ex.submit(_gb_trans_clean_fetch, t): (t, k) for t, k in miss}
                for fu in _cf.as_completed(futs):
                    t, k = futs[fu]
                    try:
                        out[t] = fu.result()
                    except Exception:
                        out[t] = t
            with _gb_trans_lock:
                c = _gb_trans_load()
                if len(c) > 8000:
                    c.clear()
                for t, k in miss:
                    c[k] = out.get(t, t)
            _gb_trans_save()
        except Exception:
            for t, k in miss:
                out.setdefault(t, _gb_trans_clean_fetch(t))
    for t in texts:
        out.setdefault(t, t)
    return out


def gb_translate_one(text):
    """英->中 翻译, 带本地缓存。翻不出来就原样返回, 绝不报错打断。"""
    t = (text or "").strip()
    if not t:
        return ""
    cache = _gb_trans_load()
    if t in cache:
        return cache[t]
    res = _gb_trans_fetch(t)
    with _gb_trans_lock:
        c = _gb_trans_load()
        if len(c) > 8000:            # 防膨胀
            c.clear()
        c[t] = res
    _gb_trans_save()
    return res


def gb_translate_many(texts):
    """批量翻译(单次上限 40 条, 先吃缓存)。返回 {原文: 译文}。
    缓存没命中的会小并发去翻(4 线程), 免得 30 个名字串行等十几秒。"""
    out = {}
    texts = [str(x) for x in (texts or [])][:40]
    cache = _gb_trans_load()
    todo = []
    for t in texts:
        if t in cache:
            out[t] = cache[t]
        elif t and t not in todo:
            todo.append(t)
    if todo:
        try:
            import concurrent.futures as _cf
            with _cf.ThreadPoolExecutor(max_workers=4) as ex:
                futs = {ex.submit(_gb_trans_fetch, t): t for t in todo}
                for fu in _cf.as_completed(futs):
                    t = futs[fu]
                    try:
                        out[t] = fu.result()
                    except Exception:
                        out[t] = t
            with _gb_trans_lock:
                c = _gb_trans_load()
                if len(c) > 8000:
                    c.clear()
                c.update(out)
            _gb_trans_save()
        except Exception:
            for t in todo:
                out.setdefault(t, _gb_trans_fetch(t))
    for t in texts:
        out.setdefault(t, t)
    return out


# ---------------------------------------------------------------------------
# v1.5.13: 角色子分类 / 批量文件清单 / 下载历史
# ---------------------------------------------------------------------------

# v1.5.14: 绝区零角色官方中文名对照(英文转写 -> 中文)。
# 角色下拉里光看英文名认不出是谁(用户实测反馈), 内置一份对照表最准且零网络依赖。
# 表里没有的(新角色/联动)再回落 MyMemory 机翻。
GB_CHAR_CN = {
    "hoshimi miyabi": "星见雅",
    "belle": "铃",
    "nicole demara": "妮可·德玛拉",
    "yixuan": "仪玄",
    "jane doe": "简·杜",
    "ellen joe": "艾莲·乔",
    "astra yao": "耀嘉音",
    "yanagi tsukishiro": "月城柳",
    "anby demara": "安比·德玛拉",
    "remielle dan": "蕾米尔·丹",
    "burnice white": "柏妮思·怀特",
    "evelyn chevalier": "伊芙琳·舒瓦利耶",
    "luciana de montefio": "露西娅娜·德·蒙特菲奥",
    "alice thymefield": "爱丽丝·泰姆菲尔德",
    "qingyi": "青衣",
    "vivian banshee": "薇薇安·班希",
    "zhu yuan": "朱鸢",
    "caesar king": "凯撒·金",
    "yuzuha ukinami": "浮波柚叶",
    "piper wheel": "派派·韦尔",
    "ye shunguang": "叶瞬光",
    "alexandrina sebastiane": "亚历山德丽娜·塞巴斯蒂安",
    "trigger": "扳机",
    "ju fufu": "橘福福",
    "velina airgid": "维琳娜·艾尔吉德",
    "seed": "席德",
    "soldier 11": "十一号",
    "grace howard": "格莉丝·霍华德",
    "dialyn": "黛琳",
    "wise": "哲",
    "yidhari murphy": "伊德海莉·墨菲",
    "lucia elowen": "露西亚·艾洛温",
    "koleda belobog": "珂蕾妲·贝洛伯格",
    "zhao": "照",
    "nekomiya mana": "猫又",
    "soldier 0 anby": "零号·安比",
    "claret flint": "克莱尔·弗林特",
    "pulchra fellini": "波可娜·费里尼",
    "orphie magnusson": "奥菲·马格努松",
    "sigrid de l'azur": "希格莉德·德·拉祖尔",
    "cissia": "希希娅",
    "billy kid": "比利·奇德",
    "corin wickes": "可琳·威克斯",
    "soukaku": "苍角",
    "aria": "爱芮雅",
    "lighter": "莱特",
    "sunna": "桑娜",
    "promeia": "普罗米娅",
    "von lycaon": "冯·莱卡恩",
    "komano manato": "猯野天斗",
    "nangong yu": "南宫羽",
    "norma hollowell": "诺玛·霍洛韦尔",
    "seth lowell": "赛斯·洛威尔",
    "asaba harumasa": "浅羽悠真",
    "anton ivanov": "安东·伊万诺夫",
    "banyue": "半月",
    "pyrois": "皮洛伊斯",
    "hugo vlad": "雨果·弗拉德",
    "ben bigger": "本·比格",
    "starlight billy": "星辉比利",
    "pan yinhu": "潘引壶",
    "roxy ifrita pryce": "萝克茜·伊芙莉塔·普莱斯",
}


def gb_char_cn(name):
    """角色英文名 -> 官方中文名。对照表命中就用表, 否则机翻, 都失败返回原文。"""
    n = (name or "").strip()
    if not n:
        return ""
    k = re.sub(r"\s+", " ", n).lower()
    if k in GB_CHAR_CN:
        return GB_CHAR_CN[k]
    # 去掉常见后缀再试一次(如 "Anby (ZZZ)")
    k2 = re.sub(r"[\(\[].*?[\)\]]", "", k).strip()
    if k2 in GB_CHAR_CN:
        return GB_CHAR_CN[k2]
    try:
        tr = gb_translate_one(n)
        return tr if (tr and tr.lower() != n.lower()) else n
    except Exception:
        return n


def gb_subcategories(cat=GB_CHAR_CAT, refresh=False):
    """拉某个分类下的子分类(角色列表)。本地缓存 1 天, 失败回落缓存。

    返回 [{"id":30336, "name":"Anby Demara", "cn":"安比",
           "count":130, "url":...}, ...]

    v1.5.14: 加 `cn` —— 角色名官方中文译名。英文名(Latin 转写)用户认不出,
    所以内置一份绝区零角色对照表(比机器翻译准, 且零网络依赖);
    表里没有的(新角色/联动)再回落 MyMemory 机翻, 也塞进 cn。
    """
    global _gb_subs_cache
    path = GB_SUBS_CACHE_PATH
    if not refresh:
        if _gb_subs_cache is None:
            d = read_json(path, None)
            if isinstance(d, dict) and d.get("ts") and d.get("items"):
                if time.time() - d["ts"] < 86400:
                    _gb_subs_cache = d
        if _gb_subs_cache:
            return _gb_subs_cache.get("items") or []
    items = []
    try:
        url = "%s/ModCategory/%s/SubCategories" % (GB_API, cat)
        d = gb_http_json(url)
        recs = d if isinstance(d, list) else (d.get("_aRecords") or [])
        for r in recs:
            u = r.get("_sUrl") or ""
            m = re.search(r"/cats/(\d+)", u)
            cid = int(m.group(1)) if m else None
            if not cid:
                continue
            nm = r.get("_sName") or ""
            items.append({
                "id": cid,
                "name": nm,
                "cn": gb_char_cn(nm),
                "count": r.get("_nItemCount") or 0,
                "url": u,
                "icon": r.get("_sIconUrl") or "",
            })
        items.sort(key=lambda x: -(x["count"] or 0))
    except Exception as e:
        log("GameBanana 子分类拉取失败: %s" % str(e)[:120])
        d = read_json(path, None)
        if isinstance(d, dict):
            return d.get("items") or []
        return []
    _gb_subs_cache = {"ts": time.time(), "cat": cat, "items": items}
    try:
        write_json(path, _gb_subs_cache)
    except Exception:
        pass
    return items


# ===================== v1.5.17: 蓝飞机(Telegram) 导入 =====================
# 用 telethon(userbot) 拉「自己已加入的频道」里的 mod 文件(zip/ini)。
# 凭据(api_id/api_hash)只存本机 config, 不进日志、不分发。
# telethon 未安装时所有接口优雅降级(返回清晰错误, 不崩)。
# 分类: Telegram 无原生分类, 按频道 + 文件名/角色名推断; 预览: 下载消息里的 photo。
# v1.5.22: **总开关** —— 功能未实测通过前暂时整体关闭(作者拍板: 等 API 申请
# 下来测通了再开)。所有 /api/tg_* 直接返回「暂未开放」, 前端隐藏整个 tab。
# 恢复只需把 TG_ENABLED 改回 True。
import threading as _tg_threading

TG_ENABLED = False

TG_LOCK = _tg_threading.Lock()
TG_STATE = {"client": None, "phone_code_hash": "", "phone": ""}
TG_SESSION = os.path.join(DATA_DIR, "tg", "tg_session")
TG_EXTS = (".zip", ".ini", ".7z", ".rar", ".cfg")


def _tg_proxy(proxy):
    if not proxy:
        return None
    m = re.match(r"^(socks5|socks4|http)://([^:/]+):(\d+)$", (proxy or "").strip())
    if not m:
        return None
    return (m.group(1), m.group(2), int(m.group(3)))


def _tg_client(app):
    """创建/复用 telethon client(进程内缓存)。无 telethon 或没配凭据 -> None。"""
    with TG_LOCK:
        if TG_STATE["client"] is not None:
            return TG_STATE["client"]
        t = app.cfg.get("tg") or {}
        try:
            api_id = int(t.get("api_id") or 0)
        except Exception:
            api_id = 0
        api_hash = (t.get("api_hash") or "").strip()
        if not api_id or not api_hash:
            return None
        try:
            from telethon import TelegramClient
        except Exception:
            return None
        try:
            os.makedirs(os.path.dirname(TG_SESSION), exist_ok=True)
        except Exception:
            pass
        proxy = _tg_proxy(t.get("proxy") or "")
        c = TelegramClient(TG_SESSION, api_id, api_hash, proxy=proxy)
        TG_STATE["client"] = c
        return c


def _tg_run(client, coro):
    return client.loop.run_until_complete(coro)


def _tg_trunc(e):
    return (str(e) or type(e).__name__).replace("\n", " ").strip()[:200]


def tg_status(app):
    have = False
    try:
        import telethon  # noqa
        have = True
    except Exception:
        pass
    t = app.cfg.get("tg") or {}
    configured = bool(t.get("api_id") and t.get("api_hash"))
    logged_in = False
    c = _tg_client(app)
    if c is not None:
        try:
            with TG_LOCK:
                _tg_run(c, c.connect())
                logged_in = _tg_run(c, c.is_user_authorized())
        except Exception:
            logged_in = False
    return {"ok": True, "telethon": have, "configured": configured,
            "logged_in": bool(logged_in),
            "api_id": t.get("api_id", ""), "api_hash": t.get("api_hash", ""),
            "proxy": t.get("proxy", "")}


def tg_save_cfg(app, api_id, api_hash, proxy):
    t = app.cfg.setdefault("tg", {})
    t["api_id"] = (api_id or "").strip()
    t["api_hash"] = (api_hash or "").strip()
    t["proxy"] = (proxy or "").strip()
    with TG_LOCK:
        TG_STATE["client"] = None
    app.save_config()
    return {"ok": True}


def tg_send_code(app, phone):
    with TG_LOCK:
        c = _tg_client(app)
        if c is None:
            return {"ok": False, "msg": "未配置 api_id/api_hash 或后端未安装 telethon"}
        try:
            _tg_run(c, c.connect())
            sent = _tg_run(c, c.send_code_request(phone))
            TG_STATE["phone_code_hash"] = getattr(sent, "phone_code_hash", "")
            TG_STATE["phone"] = phone
            return {"ok": True, "phone_code_hash": TG_STATE["phone_code_hash"]}
        except Exception as e:
            return {"ok": False, "msg": _tg_trunc(e)}


def tg_sign_in(app, phone, code, password, phone_code_hash):
    with TG_LOCK:
        c = _tg_client(app)
        if c is None:
            return {"ok": False, "msg": "未配置或未安装 telethon"}
        try:
            if password:
                _tg_run(c, c.sign_in(password=password))
            else:
                ph = phone_code_hash or TG_STATE["phone_code_hash"]
                _tg_run(c, c.sign_in(phone, code, phone_code_hash=ph))
            ok = _tg_run(c, c.is_user_authorized())
            return {"ok": bool(ok), "logged_in": bool(ok), "need_password": (not ok)}
        except Exception as e:
            msg = _tg_trunc(e)
            if re.search(r"password|2fa|two.step|two-step", msg, re.I):
                return {"ok": False, "need_password": True, "msg": "需要两步验证密码"}
            return {"ok": False, "msg": msg}


def tg_list(app):
    with TG_LOCK:
        c = _tg_client(app)
        if c is None:
            return {"ok": False, "msg": "未配置或未安装 telethon"}
        try:
            _tg_run(c, c.connect())
            if not _tg_run(c, c.is_user_authorized()):
                return {"ok": False, "msg": "未登录，请先发验证码登录"}
            dialogs = _tg_run(c, c.get_dialogs())
            items = []
            for d in dialogs:
                ent = d.entity
                uname = getattr(ent, "username", None) or ""
                title = getattr(ent, "title", None) or getattr(ent, "first_name", "") or ""
                items.append({"id": getattr(ent, "id", 0), "title": title,
                              "username": uname, "type": type(ent).__name__})
            items.sort(key=lambda x: (x["type"] != "Channel", x["title"].lower()))
            return {"ok": True, "items": items}
        except Exception as e:
            return {"ok": False, "msg": _tg_trunc(e)}


def tg_import(app, channel, prev):
    with TG_LOCK:
        c = _tg_client(app)
        if c is None:
            return {"ok": False, "msg": "未配置或未安装 telethon"}
        try:
            _tg_run(c, c.connect())
            if not _tg_run(c, c.is_user_authorized()):
                return {"ok": False, "msg": "未登录，请先发验证码登录"}
            ent = _tg_run(c, c.get_entity(channel))
            d = gb_downloads_dir(app.cfg)
            prev_dir = os.path.join(d, "tg_previews")
            if prev:
                try:
                    os.makedirs(prev_dir, exist_ok=True)
                except Exception:
                    pass
            items = []
            seen_prev = set()
            msgs = _tg_run(c, c.get_messages(ent, limit=200))
            for m in msgs:
                if m.document:
                    fn = (m.file.name if m.file else None) or ("file_%s" % m.id)
                    if not fn.lower().endswith(TG_EXTS):
                        continue
                    dest = gb_unique_path(d, fn)
                    _tg_run(c, c.download_media(m, file=dest))
                    size = os.path.getsize(dest) if os.path.exists(dest) else 0
                    sub = (m.message or "")[:90]
                    if not sub and size:
                        sub = "%.1f MB" % (size / 1048576.0)
                    items.append({"name": os.path.basename(dest), "path": dest, "sub": sub})
                elif prev and m.photo:
                    pid = getattr(m.photo, "id", m.id)
                    if pid in seen_prev:
                        continue
                    seen_prev.add(pid)
                    ppath = os.path.join(prev_dir, "prev_%s.jpg" % pid)
                    try:
                        _tg_run(c, c.download_media(m, file=ppath))
                    except Exception:
                        pass
            msg = ("导入 %d 个文件" % len(items)) if items else "最近消息里没有 zip/ini 文件"
            return {"ok": True, "items": items, "msg": msg}
        except Exception as e:
            return {"ok": False, "msg": _tg_trunc(e)}


def tg_open(app, path):
    try:
        if path and os.path.exists(path):
            open_in_explorer(os.path.dirname(path))
            return {"ok": True}
    except Exception as e:
        return {"ok": False, "msg": _tg_trunc(e)}
    return {"ok": False, "msg": "文件不存在"}


def gb_files_batch(mod_ids, limit=40, workers=6):
    """并发取多个 mod 的文件清单, 返回 {mod_id: {"files":[...], "name":...}}。
    失败/超时的 mod 会被静默跳过(前端显示「取不到文件」)。"""
    out = {}
    ids = []
    for x in (mod_ids or [])[:limit]:
        try:
            ids.append(int(x))
        except (TypeError, ValueError):
            continue
    if not ids:
        return out

    def one(mid):
        try:
            return mid, gb_mod_files(mid)
        except Exception:
            return mid, None

    try:
        import concurrent.futures as _cf
        with _cf.ThreadPoolExecutor(max_workers=workers) as ex:
            for mid, info in ex.map(one, ids):
                if info:
                    out[str(mid)] = {"name": info.get("name") or "",
                                     "files": info.get("files") or []}
    except Exception:
        for mid in ids:
            try:
                info = gb_mod_files(mid)
                out[str(mid)] = {"name": info.get("name") or "",
                                 "files": info.get("files") or []}
            except Exception:
                pass
    return out


def _gb_hist_load():
    global _gb_dl_hist
    if _gb_dl_hist is None:
        d = read_json(GB_DL_HISTORY_PATH, None)
        _gb_dl_hist = d if isinstance(d, dict) else {}
    return _gb_dl_hist


def _gb_hist_save():
    try:
        write_json(GB_DL_HISTORY_PATH, _gb_dl_hist or {})
    except Exception:
        pass


def gb_hist_mark(mod_id, fname, path=""):
    """记一笔「这个文件下过了」。key = '<mod_id>:<文件名>'。"""
    global _gb_dl_hist
    k = "%s:%s" % (mod_id, fname or "")
    with _gb_dl_hist_lock:
        h = _gb_hist_load()
        if len(h) > 4000:
            h.clear()
        h[k] = {"ts": time.time(), "path": path, "mod_id": str(mod_id), "file": fname or ""}
    _gb_hist_save()


def gb_hist_get():
    with _gb_dl_hist_lock:
        return dict(_gb_hist_load())


def gb_hist_clear():
    global _gb_dl_hist
    with _gb_dl_hist_lock:
        _gb_dl_hist = {}
    _gb_hist_save()


class Handler(BaseHTTPRequestHandler):
    server_version = "ZZMIManager/" + VERSION
    app = None
    quiet = True

    def log_message(self, fmt, *args):
        if not self.quiet:
            log("%s - %s" % (self.address_string(), fmt % args))

    def _send(self, code, body=b"", ctype="application/json; charset=utf-8",
              extra=None):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        try:
            self.wfile.write(body)
        except Exception:
            pass

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj, ensure_ascii=False))

    def _qs(self):
        d = {}
        for k, vals in urllib.parse.parse_qs(
                urllib.parse.urlparse(self.path).query,
                keep_blank_values=True).items():
            d[k] = vals[0]
        return d

    def _ok(self, qs):
        return qs.get("t") == self.app.token

    def _body(self):
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            n = 0
        if n <= 0:
            return {}
        try:
            return json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception:
            return {}

    def do_GET(self):
        try:
            path = urllib.parse.urlparse(self.path).path
            qs = self._qs()
            if path in ("/", "/index.html"):
                return self.serve_ui()
            if path == "/bg.jpg":
                # 界面背景图(随 exe 打包)
                try:
                    with open(BG_PATH, "rb") as f:
                        return self._send(200, f.read(),
                                          "image/jpeg")
                except OSError:
                    return self._json({"error": "not found"}, 404)
            if path == "/favicon.ico":
                # v1.5.9: 绝区零图标。浏览器请求 favicon 不带 token,
                # 所以放在鉴权之前, 应用窗口模式的窗口/任务栏图标也靠它
                try:
                    with open(ICON_PATH, "rb") as f:
                        return self._send(200, f.read(), "image/x-icon")
                except OSError:
                    return self._json({"error": "not found"}, 404)
            if not self._ok(qs):
                return self._json({"error": "unauthorized"}, 403)
            if path == "/api/state":
                return self._json(self.app.state())
            if path == "/api/detail":
                return self._json(self.detail(qs.get("id") or ""))
            if path == "/api/library":
                return self._json(self.library_list())
            if path == "/api/images":
                return self._json(self.list_images(qs.get("id") or ""))
            if path == "/api/autodetect":
                self.spawn_detect()
                return self._json({"ok": True})
            if path == "/api/update_check":
                repo = self.app.cfg.get("update_repo") or UPDATE_REPO
                return self._json(check_update(VERSION, repo))
            if path == "/api/gb_crawl":
                return self._json(self.gb_crawl(qs))
            if path == "/api/gb_subs":
                return self._json({
                    "ok": True,
                    "char_cat": GB_CHAR_CAT,
                    "items": gb_subcategories(
                        qs.get("cat") or GB_CHAR_CAT,
                        refresh=(qs.get("refresh") == "1"))})
            if path == "/api/gb_files":
                ids = [x for x in (qs.get("ids") or "").split(",") if x.strip()]
                return self._json({"ok": True,
                                   "map": gb_files_batch(ids),
                                   "history": gb_hist_get()})
            if path == "/api/gb_history":
                return self._json({"ok": True, "map": gb_hist_get()})
            if path == "/api/gb_dl":
                return self._json({"ok": True,
                                   "job": gb_get_job(qs.get("job") or "")})
            if path == "/api/gb_downloads":
                return self._json(gb_list_downloads(self.app.cfg))
            if path == "/api/tg_status":
                if not TG_ENABLED:
                    return self._json({"ok": False, "disabled": True,
                                       "msg": "蓝飞机接口暂未开放，敬请期待"})
                return self._json(tg_status(self.app))
            if path == "/gbimg":
                return self.gb_serve_img(qs)
            if path == "/thumb":
                return self.serve_thumb(qs)
            return self._json({"error": "not found"}, 404)
        except Exception:
            log("GET error:\n" + traceback.format_exc())
            return self._json({"error": "internal"}, 500)

    def do_POST(self):
        try:
            qs = self._qs()
            if not self._ok(qs):
                return self._json({"error": "unauthorized"}, 403)
            act = urllib.parse.urlparse(self.path).path.rsplit("/", 1)[-1]
            body = self._body()
            app = self.app

            if act == "toggle":
                ids = body.get("ids")
                r = batch_toggle(app.mods_dir(), app.find_entries(ids),
                                 bool(body.get("enabled")))
                if body.get("enabled"):
                    app.touch_usage(ids, exclude=[d["id"] for d in r["details"]])
                app.rescan()
                return self._json({"result": r, "state": app.state()})

            if act == "scope":
                ent = app.scope_entries(body.get("scope"))
                r = batch_toggle(app.mods_dir(), ent, bool(body.get("enabled")))
                if body.get("enabled"):
                    app.touch_usage([e["id"] for e in ent],
                                    exclude=[d["id"] for d in r["details"]])
                app.rescan()
                return self._json({"result": r, "state": app.state()})

            if act == "dir_toggle":
                # v1.5.8: do_toggle_dir 也可能返回 3 元组 (重名自动加序号)
                res = do_toggle_dir(app.mods_dir(), body.get("rel") or "",
                                    bool(body.get("enabled")))
                ok, msg = res[0], res[1]
                extra = res[2] if len(res) == 3 else None
                if ok and body.get("enabled") and body.get("id"):
                    app.touch_usage([body["id"]])
                app.rescan()
                out = {"ok": ok, "msg": msg, "state": app.state()}
                if ok and extra and extra.get("renamed"):
                    out["renamed"] = True
                    out["target_name"] = extra.get("target_name")
                    out["orig_name"] = extra.get("orig_name")
                    out["seq"] = extra.get("seq")
                return self._json(out)

            if act == "component_toggle":
                e = app.scan.by_id.get(body.get("id") or "")
                md = app.mods_dir()
                root = entry_root(md, e)
                if not e or not root or not os.path.isdir(root):
                    return self._json({"ok": False, "msg": "找不到该 mod"})
                ok, msg = do_toggle_file(root, body.get("rel") or "",
                                         bool(body.get("enabled")))
                if ok and body.get("enabled"):
                    app.touch_usage([e["id"]])
                app.rescan()
                return self._json({"ok": ok, "msg": msg, "state": app.state()})

            if act == "variant_select":
                e = app.scan.by_id.get(body.get("id") or "")
                md = app.mods_dir()
                root = entry_root(md, e)
                if not e or not root or not os.path.isdir(root):
                    return self._json({"ok": False, "msg": "找不到该 mod"})
                ok, msg = do_variant_select(root, body.get("rel") or "")
                if ok:
                    app.touch_usage([e["id"]])
                app.rescan()
                return self._json({"ok": ok, "msg": msg, "state": app.state()})

            if act == "cycle_set":
                # v1.4.0 起移除变体取值写入: 默认变体请在游戏内按绑定键切换。
                return self._json({"ok": False,
                                   "msg": "变体写入功能已移除; 请在游戏内按绑定键切换变体"})

            if act == "cycle_rekey":
                # v1.5.4 变体一键改键: 只改 [Key*] cycle 段的 key = 行,
                # 字节级就地替换 + 备份 + journal(玩家明确输入了新按键才动手)
                e = app.scan.by_id.get(body.get("id") or "")
                md = app.mods_dir()
                root = entry_root(md, e)
                if not e or not root or not os.path.isdir(root):
                    return self._json({"ok": False, "msg": "找不到该 mod"})
                if not (e.get("path") or "").strip():
                    # 散落在 Mods 根目录的 ini: 根目录 = 整个 Mods, 不能拿去扫
                    return self._json({"ok": False,
                                       "msg": "散落在 Mods 根目录的 ini 暂不支持改键"})
                ok, msg = do_cycle_rekey(root, body.get("var") or "",
                                         body.get("key") or "")
                return self._json({"ok": ok, "msg": msg})

            if act == "add_lib":
                """把一个文件夹加成仓库。两种:
                · rel 形式(相对 ZZMI 根目录) -> 记进 cfg["libraries"]
                · abs 形式(任意盘)          -> 记进 cfg["libs_abs"]
                create=1 时目录不存在会自动创建。只写配置, 不搬任何文件。"""
                raw = (body.get("lib") or body.get("path") or "").strip()
                if not raw:
                    return self._json({"ok": False, "msg": "没有指定仓库路径"})
                root = app.cfg.get("zzmi_root") or ""
                want_create = bool(body.get("create"))
                if is_abs_path(raw):
                    p = os.path.abspath(strip_abs_prefix(raw))
                    if not p or os.path.dirname(p) == p:
                        return self._json({"ok": False,
                                           "msg": "路径不合法(不能直接用盘符根目录)"})
                    if not os.path.isdir(p):
                        if not want_create:
                            return self._json({"ok": False,
                                               "msg": "找不到这个文件夹: %s" % p})
                        try:
                            os.makedirs(p, exist_ok=True)
                        except Exception as ex:
                            return self._json({"ok": False,
                                               "msg": "建不了这个文件夹: %s" % ex})
                    cur = [d for d in (app.cfg.get("libs_abs") or [])
                           if os.path.abspath(d) != p]
                    cur.insert(0, p)
                    app.cfg["libs_abs"] = cur
                    name = os.path.basename(p.rstrip("\\/")) or p
                    msg = "已把「%s」锁定成仓库" % name
                else:
                    rel = norm_rel(raw)
                    if not rel:
                        return self._json({"ok": False, "msg": "仓库名不合法"})
                    p = safe_join(root, rel)
                    if not p or not root or not os.path.isdir(root):
                        return self._json({"ok": False,
                                           "msg": "还没设置 ZZMI 根目录"})
                    if not os.path.isdir(p):
                        if not want_create:
                            return self._json({"ok": False,
                                               "msg": "找不到这个仓库目录: %s" % rel})
                        try:
                            os.makedirs(p, exist_ok=True)
                        except Exception as ex:
                            return self._json({"ok": False,
                                               "msg": "建不了这个仓库: %s" % ex})
                    libs = list(app.cfg.get("libraries") or [])
                    if rel not in libs:
                        libs.append(rel)
                    app.cfg["libraries"] = libs
                    msg = "已把「%s」加成仓库" % rel
                app.save_config()
                invalidate_lib_cache()
                return self._json({"ok": True, "msg": msg, "state": app.state()})

            if act == "del_lib":
                # 从仓库/自定义文件夹下拉列表里移除一项 —— 只动配置,
                # 磁盘上的文件夹和 mod 一个都不会删
                lib = (body.get("lib") or "").strip()
                if not lib:
                    return self._json({"ok": False, "msg": "没有指定要删除的仓库"})
                if is_abs_path(lib):
                    p = os.path.abspath(strip_abs_prefix(lib))
                    # 锁定的仓库(libs_abs) 和「自定义文件夹」(custom_dirs) 都可能
                    before = list(app.cfg.get("libs_abs") or [])
                    after = [d for d in before if os.path.abspath(d) != p]
                    if len(after) != len(before):
                        app.cfg["libs_abs"] = after
                    cd_before = list(app.cfg.get("custom_dirs") or [])
                    cd_after = [d for d in cd_before if os.path.abspath(d) != p]
                    if len(cd_after) != len(cd_before):
                        app.cfg["custom_dirs"] = cd_after
                    if len(after) == len(before) and \
                            len(cd_after) == len(cd_before):
                        return self._json({"ok": False,
                                           "msg": "列表里没有这个文件夹"})
                    name = p
                else:
                    libn = norm_rel(lib)
                    libs = list(app.cfg.get("libraries") or [])
                    if libn not in libs:
                        return self._json({"ok": False,
                                           "msg": "列表里没有这个仓库"})
                    libs.remove(libn)
                    app.cfg["libraries"] = libs
                    name = libn
                app.save_config()
                invalidate_lib_cache()
                return self._json({"ok": True,
                                   "msg": "已从列表移除「%s」(文件夹本身没有删)"
                                          % name,
                                   "state": app.state()})

            if act == "set_char":
                return self._json(self.set_char(body))

            if act == "set_preview":
                return self._json(self.set_preview(body))

            if act == "pin":
                return self._json(self.pin_action(body))

            if act == "move_batch":
                return self._json(self.move_batch(body))

            if act == "preset":
                return self._json(self.preset_action(body))

            if act == "undo":
                ok, msg = undo_last()
                app.rescan()
                return self._json({"ok": ok, "msg": msg, "state": app.state()})

            if act == "config":
                return self._json(self.config_action(body))

            if act == "rescan":
                app.rescan()
                return self._json({"ok": True, "state": app.state()})

            # ---- v1.5.12: GameBanana 下载区 ---------------------------------
            if act == "gb_download":
                mid = body.get("mod_id")
                if not mid:
                    return self._json({"ok": False, "msg": "缺少 mod_id"})
                picks = body.get("picks") or None
                if isinstance(picks, str):
                    picks = [picks]
                if picks is not None and not isinstance(picks, list):
                    picks = None
                jid = gb_start_download(app.cfg, mid, body.get("name") or "",
                                        picks=picks)
                return self._json({"ok": True, "job": jid})

            if act == "gb_hist_clear":
                gb_hist_clear()
                return self._json({"ok": True, "msg": "已清空下载记录"})

            if act == "pick_dir":
                base = gb_downloads_dir(app.cfg)
                # v1.5.15: 把界面窗口 hwnd 传进去当 owner —— 选择框就是它的子窗口,
                # 天然压在浏览器之上; 再加看门狗反复置顶, 双保险。
                hwnd = None
                try:
                    hwnd = find_manager_window()
                    if hwnd:
                        _bring_to_front(hwnd)
                except Exception:
                    hwnd = None
                p = pick_folder(base, owner=hwnd)
                if not p:
                    return self._json({"ok": False, "msg": "没选文件夹(或系统选择框不可用)"})
                return self._json({"ok": True, "path": p, "msg": "已选中 %s" % p})

            if act == "gb_translate":
                return self._json({"ok": True,
                                   "map": gb_translate_many(body.get("texts") or [])})

            if act == "gb_translate_files":
                # v1.5.22: 下载区文件名翻译(先清洗下划线/后缀/版本号再翻)
                return self._json({"ok": True,
                                   "map": _gb_trans_clean_map(body.get("texts") or [])})

            if act == "gb_dl_delete":
                name = os.path.basename(body.get("name") or "")
                d = gb_downloads_dir(app.cfg)
                p = os.path.join(d, name)
                if not name or not os.path.isfile(p):
                    return self._json({"ok": False, "msg": "文件不存在"})
                try:
                    os.remove(p)
                except Exception as ex:
                    return self._json({"ok": False, "msg": "删除失败: %s" % ex})
                # 顺手把下载记录里指向这个文件的条目标掉
                with _gb_dl_hist_lock:
                    h = _gb_hist_load()
                    pn = os.path.normcase(os.path.abspath(p))
                    for k in [k for k, v in h.items()
                              if os.path.normcase(os.path.abspath(v.get("path") or "")) == pn]:
                        h.pop(k, None)
                _gb_hist_save()
                return self._json({"ok": True, "msg": "已删除 %s" % name,
                                   "downloads": gb_list_downloads(app.cfg)})

            if act == "gb_open_dl":
                d = gb_downloads_dir(app.cfg)
                nm = os.path.basename(body.get("name") or "")
                if nm:
                    fp = os.path.join(d, nm)
                    if os.path.isfile(fp):
                        ok = open_in_explorer(fp, select=True)
                    else:
                        ok = open_in_explorer(d)
                else:
                    ok = open_in_explorer(d)
                return self._json({"ok": ok, "dir": d,
                                   "msg": "已打开下载目录" if ok else "打不开文件夹"})

            if act == "gb_set_dl_dir":
                raw = (body.get("path") or "").strip()
                if not raw:
                    app.cfg["downloads_dir"] = ""
                    app.save_config()
                    return self._json({"ok": True, "dir": gb_downloads_dir(app.cfg),
                                       "msg": "已恢复默认下载目录"})
                # v1.5.15: 先剥掉资源管理器给的引号, 再判绝对路径。
                # 以前带引号会被当成相对路径 -> 拼到 cwd 后面 -> 报「建不了」。
                clean = strip_path_quotes(strip_abs_prefix(raw))
                if re.match(r"^[A-Za-z]:$", clean):
                    clean = clean + "\\"            # "D:" -> "D:\"
                if not is_abs_path(clean):
                    return self._json({
                        "ok": False,
                        "msg": "请填完整路径(例如 D:\\mod下载), 相对路径不知道该放哪"})
                p = os.path.abspath(clean)
                if not p or os.path.dirname(p) == p:
                    return self._json({"ok": False, "msg": "路径不合法(不能直接用盘符根目录)"})
                try:
                    os.makedirs(p, exist_ok=True)
                except Exception as ex:
                    return self._json({"ok": False, "msg": "建不了这个文件夹: %s" % ex})
                if not os.path.isdir(p):
                    return self._json({"ok": False, "msg": "这个路径不是文件夹: %s" % p})
                app.cfg["downloads_dir"] = p
                app.save_config()
                return self._json({"ok": True, "dir": p,
                                   "downloads": gb_list_downloads(app.cfg),
                                   "msg": "下载目录已改为 %s" % p})

            if act == "gb_show_trans":
                app.cfg["show_translated"] = bool(body.get("on"))
                app.save_config()
                return self._json({"ok": True,
                                   "show_translated":
                                       bool(app.cfg.get("show_translated"))})

            if act == "launch":
                ok, msg = launch_game(app.cfg)
                return self._json({"ok": ok, "msg": msg})

            if act == "quit":
                self._json({"ok": True, "msg": "bye"})
                threading.Timer(0.3, lambda: os._exit(0)).start()
                return

            if act == "hello":
                # v1.5.10: 页面加载(含 F5 刷新)先打招呼, 取消还没执行的自动退出
                app.cancel_autoquit()
                return self._json({"ok": True})

            if act == "bye":
                # v1.5.10: 界面窗口关了(pagehide) -> 延迟几秒自动退出,
                # 不再留一个看不见又杀不掉的后台进程(提权进程普通方式杀不掉)
                app.schedule_autoquit()
                return self._json({"ok": True,
                                   "msg": "界面已关闭, 程序即将自动退出"})

            if act == "reveal":
                p = body.get("path") or ""
                if body.get("id"):
                    e = app.scan.by_id.get(body["id"])
                    if e:
                        p = entry_root(app.mods_dir(), e) or ""
                elif p and not os.path.isabs(p):
                    p = os.path.join(app.mods_dir(), p)
                ok = open_in_explorer(p)
                return self._json({"ok": ok, "msg": "" if ok else "路径不存在"})

            if act == "console":
                # v1.5.7: 命令窗口默认藏起来; 需要看日志时可以调回来
                if body.get("show"):
                    ok = show_console()
                    return self._json({"ok": ok,
                                       "msg": "命令窗口已显示" if ok
                                              else "没有找到命令窗口"})
                ok = hide_console(0)
                return self._json({"ok": ok,
                                   "msg": "命令窗口已隐藏" if ok
                                          else "没有找到命令窗口"})

            if act == "openroot":
                return self._json({"ok": open_in_explorer(
                    body.get("path") or app.mods_dir(),
                    select=bool(body.get("select")))})

            if act == "move":
                root = app.cfg.get("zzmi_root") or ""
                md = app.mods_dir()
                bases = {"mods": md, "root": root}
                # 仓库可以锁在任意盘(不在 ZZMI 目录下), 这时用 *_abs 直给绝对路径
                src_base = body.get("src_abs") or bases.get(
                    body.get("src_base"), md)
                dst_base = body.get("dst_abs") or bases.get(
                    body.get("dst_base"), root)
                if body.get("src_abs"):
                    src_base = os.path.abspath(strip_abs_prefix(src_base))
                if body.get("dst_abs"):
                    dst_base = os.path.abspath(strip_abs_prefix(dst_base))
                ok, msg = do_move(src_base, body.get("src_rel") or "",
                                  dst_base, body.get("dst_rel") or "")
                invalidate_lib_cache()
                app.rescan()
                return self._json({"ok": ok, "msg": msg, "state": app.state()})

            if act == "rename":
                e = app.scan.by_id.get(body.get("id") or "")
                if not e:
                    return self._json({"ok": False, "msg": "找不到该 mod"})
                old_rel = e["path"]
                res = do_rename(app.mods_dir(), e, body.get("name"))
                # v1.5.8: 成功时是 3 元组 (True, msg, {renamed, target_name, seq})
                if len(res) == 3:
                    ok, msg, extra = res
                else:
                    ok, msg, extra = res[0], res[1], None
                app.rescan()
                # v1.5.20: 把封面/角色覆盖键迁到新路径, 用户选过的封面不跟丢
                if ok and extra and extra.get("target_name"):
                    d = old_rel.rsplit("/", 1)
                    new_rel = (d[0] + "/" + extra["target_name"]) if len(d) == 2 \
                        else extra["target_name"]
                    _migrate_override_keys(app.cfg, old_rel, new_rel)
                    app.save_config()
                out = {"ok": ok, "msg": msg, "state": app.state()}
                if ok and extra and extra.get("renamed"):
                    out["renamed"] = True
                    out["target_name"] = extra.get("target_name")
                    out["orig_name"] = extra.get("orig_name")
                    out["seq"] = extra.get("seq")
                if not ok and extra:
                    out["manual"] = extra   # v1.5.24: 前端弹「手动改名」教程
                return self._json(out)

            if act == "mod_delete":
                # v1.5.30: 删除 mod = 移到回收站(可还原), 前端已做二次确认
                e = app.scan.by_id.get(body.get("id") or "")
                if not e:
                    return self._json({"ok": False, "msg": "找不到该 mod"})
                name = e.get("name") or ""
                ok, msg = do_mod_delete(app.mods_dir(), e)
                if ok:
                    # 清掉指向它的配置记录(收藏/使用时间/封面/角色标记), 不留死数据
                    mid, mpath = e["id"], e["path"]
                    cfg = app.cfg
                    cfg["pinned_mods"] = [x for x in (cfg.get("pinned_mods") or [])
                                          if x != mid and x != mpath]
                    (cfg.get("usage") or {}).pop(mid, None)
                    for key in ("thumb_overrides", "char_overrides"):
                        d = cfg.get(key) or {}
                        for k in [k for k in d if k == mpath or k == mid]:
                            d.pop(k, None)
                    app.save_config()
                    invalidate_lib_cache()
                app.rescan()
                return self._json({"ok": ok, "msg": msg, "state": app.state()})

            if act == "list_dirs":
                """浏览文件夹(给「自定义文件夹」挑选目标用)。只读。"""
                p = (body.get("path") or "").strip()
                drives = list_drives()
                quick = self._quick_folders()
                if not p:
                    return self._json({"ok": True, "path": "", "parent": "",
                                       "dirs": [], "drives": drives,
                                       "quick": quick})
                p = os.path.abspath(strip_abs_prefix(p))
                if not os.path.isdir(p):
                    return self._json({"ok": False, "msg": "文件夹不存在: %s" % p})
                try:
                    names = sorted(os.listdir(p))
                except OSError as ex:
                    return self._json({"ok": False, "msg": "读不了这个文件夹: %s" % ex})
                dirs = []
                for n in names:
                    if n.lower() in ("desktop.ini", "$recycle.bin",
                                     "system volume information"):
                        continue
                    fp = os.path.join(p, n)
                    try:
                        if not os.path.isdir(fp):
                            continue
                        cnt = len(os.listdir(fp))
                    except OSError:
                        continue
                    dirs.append({"name": n, "path": fp, "count": cnt})
                dirs.sort(key=lambda d: d["name"].lower())
                parent = os.path.dirname(p)
                if parent == p:
                    parent = ""
                return self._json({"ok": True, "path": p, "parent": parent,
                                   "dirs": dirs[:500], "drives": drives,
                                   "quick": quick})

            if act == "mkdir":
                if body.get("base") == "abs" or is_abs_path(
                        body.get("path") or ""):
                    # 在任意位置建新文件夹(「自定义文件夹」里点「新建」时用)
                    p = os.path.abspath(strip_abs_prefix(
                        (body.get("path") or "").strip()))
                    if not p or os.path.dirname(p) == p:
                        return self._json({"ok": False, "msg": "路径不合法"})
                    if not os.path.isdir(os.path.dirname(p)):
                        return self._json({"ok": False,
                                           "msg": "上级文件夹不存在: %s"
                                                  % os.path.dirname(p)})
                else:
                    base = (app.mods_dir() if body.get("base") == "mods"
                            else app.cfg.get("zzmi_root") or "")
                    p = safe_join(base, body.get("rel") or "")
                if not p:
                    return self._json({"ok": False, "msg": "路径不合法"})
                try:
                    os.makedirs(p, exist_ok=True)
                    return self._json({"ok": True, "msg": "已创建", "path": p})
                except Exception as ex:
                    return self._json({"ok": False, "msg": str(ex)})

            # ---- v1.5.17: 蓝飞机(Telegram) 导入 ---------------------------------
            # v1.5.22: TG_ENABLED=False 时整组接口不可用(测通后恢复)
            if act.startswith("tg_") and not TG_ENABLED:
                return self._json({"ok": False, "disabled": True,
                                   "msg": "蓝飞机接口暂未开放，敬请期待"})
            if act == "tg_save_cfg":
                return self._json(tg_save_cfg(app, body.get("api_id", ""),
                                              body.get("api_hash", ""), body.get("proxy", "")))
            if act == "tg_send_code":
                return self._json(tg_send_code(app, body.get("phone", "")))
            if act == "tg_sign_in":
                return self._json(tg_sign_in(app, body.get("phone", ""),
                                            body.get("code", ""), body.get("password", ""),
                                            body.get("phone_code_hash", "")))
            if act == "tg_list":
                return self._json(tg_list(app))
            if act == "tg_import":
                return self._json(tg_import(app, body.get("channel", ""), bool(body.get("prev"))))
            if act == "tg_open":
                return self._json(tg_open(app, body.get("path", "")))

            return self._json({"error": "not found"}, 404)
        except Exception:
            log("POST error:\n" + traceback.format_exc())
            return self._json({"error": "internal"}, 500)

    def _quick_folders(self):
        """「自定义文件夹」里的快捷入口: ZZMI 根目录 / Mods / 桌面 / 文档 / 下载。"""
        out = []
        try:
            root = self.app.cfg.get("zzmi_root") or ""
            if root and os.path.isdir(root):
                out.append({"label": "ZZMI 根目录", "path": root})
            md = self.app.mods_dir()
            if md and os.path.isdir(md) and os.path.abspath(md) != \
                    os.path.abspath(root or " "):
                out.append({"label": "Mods", "path": md})
        except Exception:
            pass
        home = os.path.expanduser("~")
        for label, sub in (("桌面", "Desktop"), ("文档", "Documents"),
                           ("下载", "Downloads")):
            for cand in (os.path.join(home, sub), os.path.join(home, label)):
                if os.path.isdir(cand):
                    out.append({"label": label, "path": cand})
                    break
        return out

    def serve_ui(self):
        try:
            with open(UI_PATH, "r", encoding="utf-8") as f:
                html = f.read()
        except Exception as ex:
            return self._send(500, "缺少 ui.html: %s" % ex,
                              "text/plain; charset=utf-8")
        html = html.replace("__BOOT__", json.dumps(
            {"token": self.app.token, "version": VERSION}, ensure_ascii=False))
        return self._send(200, html, "text/html; charset=utf-8")

    def serve_thumb(self, qs):
        rel = qs.get("p") or ""
        full = (qs.get("full") or "") in ("1", "true", "yes")   # 「放大看大图」送原图
        root = self.app.scan.root or self.app.mods_dir()
        if not rel or not root:
            return self._send(404, b"", "text/plain")
        p = safe_join(root, rel)
        if not p or not os.path.isfile(p):
            return self._send(404, b"", "text/plain")
        # 只送真正的图片: .dds / .ib 这类游戏贴图/模型资源一律拒绝
        low = p.lower()
        if low.endswith(NEVER_IMAGE_EXTS) or not low.endswith(IMAGE_EXTS):
            return self._send(415, b"", "text/plain")
        if full:
            tp, cache, cap = p, "max-age=300", 30 * 1024 * 1024
        else:
            tp = cached_thumb(p)
            if tp is None:
                # v1.5.20: 没有现成缩略图就**当场生成**(毫秒级), 不再把几 MB 的
                # 原图直接怼给页面 —— 以前刚重命名/刚扫描完的第一次请求会收到
                # 整张原图(实测有 7MB), 叠加后台批量压图抢 CPU, 卡片就是一片灰
                # 半天出不来, 看起来像"图丢了"。
                try:
                    os.makedirs(THUMB_DIR, exist_ok=True)
                    dst = os.path.join(THUMB_DIR, thumb_key(p))
                except OSError:
                    dst = ""
                if dst and make_thumb(p, dst):
                    tp = dst
                else:
                    tp = p
                    _thumb_q.put(p)   # 生成失败, 交给后台重试, 这次先送原图顶着
            cache, cap = "max-age=86400", 14 * 1024 * 1024
        try:
            if os.path.getsize(tp) > cap:
                return self._send(413, b"", "text/plain")
            data = read_bytes_shared(tp, cap=cap + 1)   # 不阻塞用户改名/搬运
            if len(data) > cap:
                return self._send(413, b"", "text/plain")
        except Exception:
            return self._send(500, b"", "text/plain")
        ctype = mimetypes.guess_type(tp)[0] or "application/octet-stream"
        return self._send(200, data, ctype, extra={"Cache-Control": cache})

    def gb_crawl(self, qs):
        """爬 GameBanana 一页 mod 列表 / 单个 mod 的文件清单。

        v1.5.13: 可带 cat=<分类id> 直接锁定某个角色分类(角色筛选),
        此时 url 参数可以留空。
        """
        raw = qs.get("url") or ""
        page = qs.get("page") or "1"
        cat = (qs.get("cat") or "").strip()
        if cat and re.fullmatch(r"\d+", cat):
            try:
                data = gb_list("category", cat, page, 30, cat=cat)
                data["ok"] = True
                data["cat"] = cat
                return data
            except Exception as e:
                return {"ok": False, "msg": "爬取失败: %s" % str(e)[:180]}
        kind, gid, err = gb_parse_url(raw)
        if err:
            return {"ok": False, "msg": err}
        try:
            if kind == "mod":
                return {"ok": True, "kind": "mod", "mod": gb_mod_files(gid)}
            data = gb_list(kind, gid, page, 30)
            data["ok"] = True
            return data
        except Exception as e:
            return {"ok": False, "msg": "爬取失败: %s" % str(e)[:180]}

    def gb_serve_img(self, qs):
        """代理 GameBanana 预览图(只放行 images.gamebanana.com), 本地缓存一天。
        走代理是为了同源 + 免得浏览器直连外网图床卡顿/被挡。"""
        u = qs.get("u") or ""
        if not u.startswith("https://images.gamebanana.com/"):
            return self._send(403, b"", "text/plain")
        key = hashlib.sha1(u.encode("utf-8")).hexdigest()
        ext = os.path.splitext(urllib.parse.urlparse(u).path)[1].lower()
        if ext not in IMAGE_EXTS:
            ext = ".jpg"
        cache_p = os.path.join(GB_IMG_CACHE, key + ext)
        cap = 12 * 1024 * 1024
        data = None
        if os.path.isfile(cache_p):
            try:
                data = read_bytes_shared(cache_p, cap=cap + 1)
            except Exception:
                data = None
        if data is None or len(data) > cap:
            try:
                req = urllib.request.Request(u, headers={"User-Agent": GB_UA})
                with urllib.request.urlopen(req, timeout=20) as r:
                    data = r.read(cap + 1)
                try:
                    os.makedirs(GB_IMG_CACHE, exist_ok=True)
                    with open(cache_p, "wb") as f:
                        f.write(data)
                except Exception:
                    pass
            except Exception:
                return self._send(502, b"", "text/plain")
        if len(data) > cap:
            return self._send(413, b"", "text/plain")
        ctype = mimetypes.guess_type(cache_p)[0] or "image/jpeg"
        return self._send(200, data, ctype, extra={"Cache-Control": "max-age=604800"})

    def detail(self, mid):
        app = self.app
        e = app.scan.by_id.get(mid)
        if not e:
            return {"error": "not found"}
        md = app.mods_dir()
        abs_root = entry_root(md, e) or os.path.join(md, e["path"])
        comp = analyze_components(abs_root) if os.path.isdir(abs_root) \
            else {"components": [], "groups": []}
        inis = []
        if os.path.isdir(abs_root):
            for cur, dirs, files in os.walk(abs_root):
                dirs[:] = [d for d in dirs if d.lower() != "desktop.ini"]
                rel = os.path.relpath(cur, abs_root)
                rel = "" if rel == "." else rel
                for f in files:
                    if f.lower().endswith(".ini"):
                        inis.append({"rel": norm_rel(os.path.join(rel, f)),
                                     "disabled": is_disabled_name(f),
                                     "size": _size(os.path.join(cur, f))})
        return {"entry": e, "abs_path": abs_root,
                "exists": os.path.isdir(abs_root),
                "inis": sorted(inis, key=lambda i: i["rel"].lower()),
                "components": comp.get("components", []),
                "groups": comp.get("groups", []),
                "cycles": parse_cycle_vars(abs_root)
                if os.path.isdir(abs_root) else []}

    def library_list(self):
        app = self.app
        now = time.time()
        if _lib_cache["data"] is not None and now - _lib_cache["t"] < 90:
            return _lib_cache["data"]
        root = app.cfg.get("zzmi_root") or ""
        out = []
        # 仓库 = ZZMI 目录下的相对仓库 + 玩家锁定的任意绝对路径仓库
        targets = [(lib, safe_join(root, lib), False)
                   for lib in (app.cfg.get("libraries") or [])]
        targets += [(d, os.path.abspath(d), True)
                    for d in (app.cfg.get("libs_abs") or []) if d]
        for lib, p, is_abs in targets:
            items = []
            if p and os.path.isdir(p):
                for name in sorted(os.listdir(p), key=lambda s: s.lower()):
                    sp = os.path.join(p, name)
                    if not os.path.isdir(sp):
                        continue
                    sz = n = 0
                    for cur, dirs, files in os.walk(sp):
                        n += len(files)
                        for f in files:
                            try:
                                sz += os.path.getsize(os.path.join(cur, f))
                            except OSError:
                                pass
                    items.append({"name": name, "size": sz, "size_h": human_size(sz),
                                  "files": n, "disabled": is_disabled_name(name)})
            name = lib if not is_abs else (os.path.basename(p.rstrip("\\/")) or p)
            out.append({"name": name, "path": p or "", "items": items,
                        "count": len(items), "abs": is_abs,
                        "ref": ("abs:" + p) if is_abs else lib,
                        "exists": bool(p and os.path.isdir(p))})
        md = app.mods_dir()
        tops = []
        if md and os.path.isdir(md):
            for name in sorted(os.listdir(md), key=lambda s: s.lower()):
                if os.path.isdir(os.path.join(md, name)):
                    tops.append({"name": name, "disabled": is_disabled_name(name)})
        data = {"libraries": out, "mods_top": tops, "root": root, "mods_dir": md}
        _lib_cache["t"] = now
        _lib_cache["data"] = data
        return data

    def set_char(self, body):
        app = self.app
        e = app.scan.by_id.get(body.get("id") or "")
        if not e:
            return {"ok": False, "msg": "找不到该 mod"}
        char = (body.get("char") or "").strip()
        ov = app.cfg.setdefault("char_overrides", {})
        if not char or char == e["char_auto"]:
            ov.pop(e["id"], None)
            ov.pop(e["path"], None)
            msg = "已恢复自动识别: %s" % e["char_auto"]
        else:
            ov[e["id"]] = char
            msg = "角色已设为「%s」" % char
        app.save_config()
        app.rescan()
        return {"ok": True, "msg": msg, "state": app.state()}

    def _mod_root(self, mid):
        """按 mod id 找到磁盘上的 mod 文件夹绝对路径。"""
        app = self.app
        e = app.scan.by_id.get(mid or "")
        if not e:
            return None, None
        md = app.mods_dir()
        abs_root = entry_root(md, e) or os.path.join(md, e["path"])
        return e, abs_root

    def list_images(self, mid):
        """列出该 mod 文件夹里所有能当封面的图片(递归, 明确不含 .dds),
        供「切换预览图」让用户自己挑。"""
        e, abs_root = self._mod_root(mid)
        if not e:
            return {"ok": False, "msg": "找不到该 mod"}
        md = self.app.mods_dir()
        cur_rel = ""
        if e.get("thumb"):
            cur_abs = os.path.join(md, e["thumb"].replace("/", os.sep))
            try:
                cur_rel = norm_rel(os.path.relpath(cur_abs, abs_root))
            except ValueError:
                cur_rel = ""
        ov = self.app.cfg.get("thumb_overrides") or {}
        imgs = iter_mod_images(abs_root)
        for im in imgs:
            # 另外给一份「相对 Mods 根」的路径, 界面直接拿去喂 /thumb
            im["thumb"] = norm_rel(os.path.join(e["path"], im["rel"]))
        return {"ok": True, "abs_path": abs_root,
                "images": imgs,
                "current": cur_rel,
                "manual": bool(ov.get(e["id"]) or ov.get(e["path"]))}

    def set_preview(self, body):
        """切换预览图 / 一键添加预览图 / 恢复自动。

        {id, rel}             -> 用 mod 文件夹里已有的某张图当封面
        {id, data, filename}  -> 把用户选的照片写进 mod 文件夹再当封面
        {id, reset: True}     -> 清掉手动指定, 恢复自动挑选
        """
        app = self.app
        e, abs_root = self._mod_root(body.get("id"))
        if not e:
            return {"ok": False, "msg": "找不到该 mod"}
        if not os.path.isdir(abs_root):
            return {"ok": False, "msg": "mod 文件夹不存在"}
        ov = app.cfg.setdefault("thumb_overrides", {})
        if body.get("reset"):
            ov.pop(e["id"], None)
            ov.pop(e["path"], None)
            app.save_config()
            app.rescan()
            return {"ok": True, "msg": "已恢复自动挑选封面", "state": app.state()}

        rel = ""
        if body.get("data"):
            try:
                blob = base64.b64decode((body["data"] or "").split(",")[-1])
            except Exception:
                return {"ok": False, "msg": "图片数据解析失败"}
            rel, err = write_mod_cover(abs_root, body.get("filename") or "", blob)
            if not rel:
                return {"ok": False, "msg": err}
            msg = "已把这张图存进 mod 文件夹并设为封面"
        else:
            want = norm_rel(body.get("rel") or "")
            p = safe_join(abs_root, want)
            if not p or not os.path.isfile(p):
                return {"ok": False, "msg": "找不到这张图片"}
            low = p.lower()
            if low.endswith(NEVER_IMAGE_EXTS) or not low.endswith(IMAGE_EXTS):
                return {"ok": False, "msg": "这种格式不能当预览图"}
            rel = want
            msg = "封面已切换"

        # 同时按 id 和 path 记一份: 重名 mod 的 id 会被加上 #N, 只有 path 一定唯一
        full = norm_rel(os.path.join(e["path"], rel))
        ov[e["id"]] = full
        ov[e["path"]] = full
        app.save_config()
        app.rescan()
        return {"ok": True, "msg": msg, "state": app.state()}

    def config_action(self, body):
        app = self.app
        if body.get("zzmi_root"):
            ok, msg = app.set_root(body["zzmi_root"], body.get("importer"),
                                   body.get("mods_dir"))
            if not ok:
                return {"ok": False, "msg": msg}
            app.rescan()
            return {"ok": True, "msg": "已保存", "state": app.state()}
        changed = False
        if body.get("mods_dir"):
            app.cfg["mods_dir"] = body["mods_dir"].strip().strip('"')
            changed = True
        if "theme" in body:
            app.cfg["theme"] = body["theme"]
            changed = True
        if "hide_preview" in body:
            app.cfg["hide_preview"] = bool(body["hide_preview"])
            changed = True
        if "update_repo" in body:
            repo = (body["update_repo"] or "").strip()
            if repo:
                app.cfg["update_repo"] = repo
                changed = True
        if body.get("importer"):
            app.cfg["importer"] = body["importer"]
            changed = True
        if "hotkey" in body:
            combo = parse_hotkey(body["hotkey"])
            if not combo:
                return {"ok": False, "msg":
                        "快捷键格式不对。字母/数字要带修饰键, 如 Ctrl+Alt+K; "
                        "单独按 F1~F12 也可以。"}
            app.cfg["hotkey"] = body["hotkey"].strip()
            app.save_config()
            ok, msg = app.hotkey.register(combo)
            return {"ok": ok, "msg": msg if not ok else
                    "快捷键已设为 " + app.cfg["hotkey"], "state": app.state()}
        if changed:
            app.save_config()
            app.rescan()
            invalidate_lib_cache()
        return {"ok": True, "msg": "已保存", "state": app.state()}

    def move_batch(self, body):
        """多选一键搬运到仓库: {ids:[...], lib:"仓库名"(空=ZZMI 根目录), sub:"子目录"}。
        只搬目录本身, 不删文件; 同名自动加 (2); 每次搬运都写 journal 可撤销。"""
        app = self.app
        root = app.cfg.get("zzmi_root") or ""
        if not root or not os.path.isdir(root):
            return {"ok": False, "msg": "还没设置 ZZMI 根目录"}
        lib = (body.get("lib") or "").strip()
        sub = norm_rel(body.get("sub") or "")
        if is_abs_path(lib):
            # 用户自己挑的任意文件夹(可以不在 ZZMI 目录下)
            base = os.path.abspath(strip_abs_prefix(lib))
            if not os.path.isdir(base):
                return {"ok": False, "msg": "找不到这个文件夹: %s" % base}
            recent = [d for d in (app.cfg.get("custom_dirs") or [])
                      if os.path.abspath(d) != base]
            recent.insert(0, base)              # 记住, 下次下拉里直接能选
            app.cfg["custom_dirs"] = recent[:8]
            app.save_config()
        elif lib:
            lib = norm_rel(lib)
            base = safe_join(root, lib)
            if not base or not os.path.isdir(base):
                return {"ok": False, "msg": "找不到仓库目录: %s" % lib}
            libs = list(app.cfg.get("libraries") or [])
            if lib not in libs:                 # 用户自己新建的仓库也认下来
                libs.append(lib)
                app.cfg["libraries"] = libs
                app.save_config()
        else:
            base = root
        dst_root = safe_join(base, sub) if sub else base
        if not dst_root:
            return {"ok": False, "msg": "目标路径不合法"}
        ids = [i for i in (body.get("ids") or []) if i]
        if not ids:
            return {"ok": False, "msg": "没有选中任何 mod"}
        ents = app.find_entries(ids)
        if len(ents) < len(ids):
            # 可能刚把新 mod 丢进 Mods 还没重扫, 补扫一次再试
            app.rescan()
            ents = app.find_entries(ids)
        if not ents:
            return {"ok": False, "msg": "没有选中任何 mod"}
        try:
            os.makedirs(dst_root, exist_ok=True)
        except OSError as ex:
            return {"ok": False, "msg": "建不了目标目录: %s" % ex}
        res = move_mods_batch(app.mods_dir(), ents, dst_root)
        invalidate_lib_cache()
        app.rescan()
        where = ((os.path.basename(base) or base) if is_abs_path(lib)
                 else (lib or "ZZMI 根目录"))
        msg = ("已把 %d 个 mod 搬进「%s」" % (res["ok"], where)) if res["ok"] \
            else "搬运失败"
        if res["failed"]:
            msg += " · %d 个没搬成" % res["failed"]
        return {"ok": res["ok"] > 0, "msg": msg, "result": res,
                "state": app.state()}

    def pin_action(self, body):
        """收藏/置顶: {kind: mod|cat|char, key: id或名字, on: true/false}
        on 缺省时为切换。只写配置文件, 不动 mod 文件。"""
        app = self.app
        kind = body.get("kind") or "mod"
        key = (body.get("key") or "").strip()
        if not key:
            return {"ok": False, "msg": "缺少收藏对象"}
        field = {"mod": "pinned_mods", "cat": "pinned_cats",
                 "char": "pinned_chars"}.get(kind)
        if not field:
            return {"ok": False, "msg": "未知收藏类型"}
        lst = list(app.cfg.get(field) or [])
        if body.get("on") is None:
            on = key not in lst
        else:
            on = bool(body.get("on"))
        if on:
            if key not in lst:
                lst.append(key)
            msg = "已收藏 ⭐ %s" % (app.scan.by_id[key]["name"]
                                  if kind == "mod" and key in app.scan.by_id else key)
        else:
            lst = [x for x in lst if x != key]
            msg = "已取消收藏 %s" % key
        with app.lock:
            app.cfg[field] = lst
            app.save_config()
        app.rescan()
        return {"ok": True, "msg": msg, "pinned": on, "state": app.state()}

    def preset_action(self, body):
        app = self.app
        act = body.get("action")
        name = (body.get("name") or "").strip()
        presets = presets_load()
        if act == "save":
            if not name:
                return {"ok": False, "msg": "请填方案名"}
            presets[name] = {
                "enabled": sorted(e["id"] for e in app.scan.entries if e["enabled"]),
                "total": len(app.scan.entries), "saved": time.time()}
            presets_save(presets)
            return {"ok": True, "msg": "已保存方案「%s」" % name,
                    "state": app.state()}
        if act == "apply":
            p = presets.get(name)
            if not p:
                return {"ok": False, "msg": "没有这个方案"}
            want = set(p.get("enabled") or [])
            off = [e for e in app.scan.entries if e["enabled"] and e["id"] not in want]
            on = [e for e in app.scan.entries if not e["enabled"] and e["id"] in want]
            r1 = batch_toggle(app.mods_dir(), off, False)
            r2 = batch_toggle(app.mods_dir(), on, True)
            app.touch_usage([e["id"] for e in on],
                            exclude=[d["id"] for d in r2["details"]])
            app.rescan()
            # v1.5.6: 把没改成功的项也带回去, 前端好弹"手动加/删 DISABLED_"教程
            failed = list(r1["details"]) + list(r2["details"])
            # v1.5.8: 因重名被自动加后缀的也带回去, 前端提示"已自动改名"
            renamed = list(r1.get("renamed") or []) + list(r2.get("renamed") or [])
            return {"ok": True, "msg": "已套用「%s」: 启用 %d / 禁用 %d"
                                       % (name, r2["ok"], r1["ok"]),
                    "failed": failed[:20], "renamed": renamed[:20],
                    "state": app.state()}
        if act == "delete":
            if name not in presets:
                return {"ok": False, "msg": "没有这个方案"}
            presets.pop(name, None)
            presets_save(presets)
            return {"ok": True, "msg": "已删除方案「%s」" % name,
                    "state": app.state()}
        return {"ok": False, "msg": "未知操作"}

    def spawn_detect(self):
        app = self.app
        if not app.detect_report.get("done", True):
            return
        app.detect_report = {"done": False, "step": "准备扫描…", "found": None,
                             "candidates": [], "message": ""}
        threading.Thread(target=run_detection, args=(app,), daemon=True).start()


def _size(p):
    try:
        return os.path.getsize(p)
    except OSError:
        return 0


# ===========================================================================
# 全局快捷键 (RegisterHotKey, 游戏运行时也能呼出/隐藏管理器窗口)
# ===========================================================================

MOD_ALT, MOD_CONTROL, MOD_SHIFT, MOD_WIN = 0x0001, 0x0002, 0x0004, 0x0008
MOD_NOREPEAT = 0x4000  # 避免长按重复触发
WM_HOTKEY, WM_QUIT = 0x0312, 0x0012
_HOTKEY_ID = 0x5A4D  # 'ZM'


def parse_hotkey(s):
    """'Ctrl+Alt+M' -> (mods, vk)。字母/数字必须带修饰键; 单独 F1~F12 允许。"""
    if not s:
        return None
    mods, key = 0, None
    for part in s.replace(" ", "").split("+"):
        if not part:
            continue
        p = part.lower()
        if p == "ctrl":
            mods |= MOD_CONTROL
        elif p == "alt":
            mods |= MOD_ALT
        elif p == "shift":
            mods |= MOD_SHIFT
        elif p == "win":
            mods |= MOD_WIN
        else:
            key = part
    if not key:
        return None
    k = key.lower()
    vk = None
    if len(k) == 1 and (k.isalpha() or k.isdigit()):
        vk = ord(k.upper())
    elif re.match(r"^f([1-9]|1[0-9]|2[0-4])$", k):
        vk = 0x70 + int(k[1:]) - 1
    else:
        vk = {"space": 0x20, "tab": 0x09, "home": 0x24, "end": 0x23,
              "insert": 0x2D, "delete": 0x2E, "pageup": 0x21,
              "pagedown": 0x22, "up": 0x26, "down": 0x28, "left": 0x25,
              "right": 0x27, "`": 0xC0, "-": 0xBD, "=": 0xBB, "[": 0xDB,
              "]": 0xDD, "\\": 0xDC, ";": 0xBA, "'": 0xDE, ",": 0xBC,
              ".": 0xBE, "/": 0xBF}.get(k)
    if vk is None:
        return None
    if not (mods & (MOD_CONTROL | MOD_ALT | MOD_SHIFT | MOD_WIN)):
        if not re.match(r"^f([1-9]|1[0-9]|2[0-4])$", k):
            return None  # 普通键必须带修饰键, 否则会劫持游戏按键
    return mods, vk


def find_manager_window():
    """找管理器的 Edge/Chrome app 窗口 (按窗口类 + 标题匹配)。"""
    import ctypes
    user32 = ctypes.windll.user32
    # --app 模式的窗口标题就是页面 <title>: "ZZMI Mod 管家"
    h = user32.FindWindowW("Chrome_WidgetWin_1", APP_NAME)
    if h:
        return h
    # 兜底: 枚举顶层窗口找标题前缀
    proto = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)
    hits = []
    GetWindowTextW = user32.GetWindowTextW
    GetClassNameW = user32.GetClassNameW
    IsWindowVisible = user32.IsWindowVisible

    def _cb(hwnd, _lparam):
        try:
            buf = ctypes.create_unicode_buffer(64)
            GetClassNameW(hwnd, buf, 64)
            if buf.value != "Chrome_WidgetWin_1":
                return 1
            buf = ctypes.create_unicode_buffer(128)
            GetWindowTextW(hwnd, buf, 128)
            if buf.value.startswith(APP_NAME):
                hits.append(hwnd)
        except Exception:
            pass
        return 1

    cb = proto(_cb)
    try:
        user32.EnumWindows(cb, None)
    except Exception:
        pass
    return hits[0] if hits else None


def _bring_to_front(hwnd):
    return force_foreground(hwnd)


def toggle_manager_window(app):
    """快捷键动作: 最小化/恢复循环 —— 没窗口就开; 可见就最小化到任务栏;
    最小化就恢复并置前。Edge 进程不退出, 下次还能呼出。"""
    import ctypes
    user32 = ctypes.windll.user32
    hwnd = find_manager_window()
    if not hwnd:
        url = ""
        try:
            url = open(os.path.join(DATA_DIR, "last_url.txt")).read().strip()
        except OSError:
            pass
        if url:
            open_app_window(url, app.cfg.get("win_size") or "auto")
        return
    # SW_SHOWMINIMIZED(2) = 最小化; SW_RESTORE(9) = 从最小化恢复
    if user32.IsIconic(hwnd):
        # 当前是最小化状态 → 恢复并置前
        user32.ShowWindow(hwnd, 9)              # SW_RESTORE
        _bring_to_front(hwnd)
    else:
        # 当前是可见状态 → 最小化到任务栏
        user32.ShowWindow(hwnd, 2)              # SW_SHOWMINIMIZED


class HotkeyManager(object):
    """后台线程 RegisterHotKey + 消息循环; 换键 = 线程发 WM_QUIT 后重启。"""

    def __init__(self, app):
        self.app = app
        self.tid = None
        self.thread = None
        self.ok = None
        self._evt = threading.Event()

    def start(self):
        s = parse_hotkey(self.app.cfg.get("hotkey") or "F9")
        if s:
            return self.register(s)
        return True, ""

    def register(self, combo):
        """返回 (ok, msg)。"""
        self.stop()
        self.ok, self._evt = None, threading.Event()
        self.thread = threading.Thread(target=self._loop, args=(combo,),
                                       daemon=True)
        self.thread.start()
        self._evt.wait(2.0)
        if self.ok:
            return True, "全局快捷键已生效"
        return False, "快捷键注册失败(可能被其他程序占用)"

    def stop(self):
        if self.tid and self.thread and self.thread.is_alive():
            import ctypes
            ctypes.windll.user32.PostThreadMessageW(
                self.tid, WM_QUIT, 0, 0)
            self.thread.join(timeout=1.5)
        self.thread, self.tid = None, None

    def _loop(self, combo):
        import ctypes
        from ctypes import wintypes
        user32, kernel32 = ctypes.windll.user32, ctypes.windll.kernel32
        self.tid = kernel32.GetCurrentThreadId()
        mods, vk = combo
        if not user32.RegisterHotKey(None, _HOTKEY_ID, mods | MOD_NOREPEAT, vk):
            self.ok = False
            self._evt.set()
            return
        self.ok = True
        self._evt.set()
        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            if msg.message == WM_HOTKEY:
                try:
                    toggle_manager_window(self.app)
                except Exception:
                    log("快捷键处理出错:\n" + traceback.format_exc())
        user32.UnregisterHotKey(None, _HOTKEY_ID)


# ===========================================================================
# 启动
# ===========================================================================

def pick_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def main():
    # --console / -c: 保留命令窗口(排查问题时用), 等价于 ZZMI_KEEP_CONSOLE=1
    if any(a in ("--console", "-c") for a in sys.argv[1:]):
        os.environ["ZZMI_KEEP_CONSOLE"] = "1"
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(THUMB_DIR, exist_ok=True)
    threading.Thread(target=thumb_worker, daemon=True).start()

    app = App()
    have_cfg = app.load_config()
    md = app.mods_dir()
    pending_detect = False
    if have_cfg and md and os.path.isdir(md):
        log("使用已保存的配置:", app.cfg.get("zzmi_root"))
    else:
        # 不阻塞启动: 服务先起来, 界面秒开, 检测在后台跑并由界面显示进度
        log("没有可用配置, 服务启动后在后台自动查找 ZZMI …")
        pending_detect = True
        app.detect_report = {"done": False, "step": "准备扫描…", "found": None,
                             "candidates": [], "message": ""}

    if app.mods_dir() and os.path.isdir(app.mods_dir()):
        log("扫描 Mods:", app.mods_dir())
        s = app.rescan()
        log("共 %d 个 mod / %d 个角色 (启用 %d / 禁用 %d / 部分 %d / 冲突 %d 组), %.2fs"
            % (s.stats["total"], s.stats["chars"], s.stats["enabled"],
               s.stats["disabled"], s.stats["partial"], s.stats["conflicts"],
               s.duration))

    port = pick_port()
    Handler.app = app
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    httpd.daemon_threads = True
    app.httpd = httpd
    url = "http://127.0.0.1:%d/?t=%s" % (port, app.token)
    try:
        with open(os.path.join(DATA_DIR, "last_url.txt"), "w") as f:
            f.write(url)
    except Exception:
        pass
    log("")
    log("  %s v%s" % (APP_NAME, VERSION))
    log("  界面: %s" % url)
    log("  数据: %s" % DATA_DIR)
    log("  日志: %s" % os.path.join(DATA_DIR, "zzmi.log"))
    log("  关掉界面窗口(或界面「设置」里的退出)即可结束程序")
    log("")
    if not os.environ.get("ZZMI_NO_BROWSER"):
        size = app.cfg.get("win_size") or "auto"
        b = find_browser((app.cfg.get("browser_path") or "").strip() or None)
        if not b:
            # Edge 和 Chrome 都没有: 弹窗让用户自己挑一个浏览器, 选过一次就记住
            picked = pick_browser_exe()
            if picked:
                app.cfg["browser_path"] = picked
                app.save_config()
                b = picked
        if b:
            threading.Timer(0.6, lambda: open_app_window(url, size, b)).start()
        else:
            # 用户取消选择, 或什么都调不出来: 至少用系统默认浏览器把界面开出来
            log("没有可用浏览器, 退回系统默认浏览器打开(普通标签页)")
            threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    # v1.5.7: 界面起来之后就把命令窗口藏掉, 不再挡在桌面上
    if os.environ.get("ZZMI_KEEP_CONSOLE") != "1":
        threading.Thread(target=hide_console, args=(1.8,), daemon=True).start()
    if pending_detect:
        threading.Thread(target=run_detection, args=(app,), daemon=True).start()
    try:
        ok_hk, msg_hk = app.hotkey.start()
    except Exception as ex:
        ok_hk, msg_hk = False, str(ex)
    if app.cfg.get("hotkey"):
        log("全局快捷键: %s%s" % (app.cfg["hotkey"],
                                 "" if ok_hk else "  (注册失败: %s)" % msg_hk))
    # v1.5.20: HTTP 服务转到后台线程(界面窗口由主线程负责拉起)。
    # 这里把异常吃掉: 进程退出瞬间 socket 回收会让 serve_forever 抛一次,
    # 那是正常收尾, 不该在命令行里甩一段吓人的 traceback。
    def _serve():
        try:
            httpd.serve_forever()
        except Exception:
            pass
    threading.Thread(target=_serve, daemon=True).start()
    if _WIN:
        log("  关掉界面窗口即可结束程序")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("bye")


if __name__ == "__main__":
    main()
