# 截图规范（重要）

本目录的图片会随仓库公开，**提交前必须确认里面没有任何真实数据**。

## 硬性要求

1. **不得出现真实的 mod 库路径**。
   统一使用演示路径 `D:\ZZMI_Demo\ZZMI\Mods`（界面顶栏那个路径 chip 最容易漏）。
2. **不得出现真实 mod 名 / 真实角色组合**。
   统一使用「示例角色 · 示例皮肤 A」这类占位名。
3. **不得出现真实 mod 的封面/缩略图 —— 哪怕是从截图里"抠"出来的也不行**。
   卡片缩略图必须是**空白**（跟 `界面预览-浅色/深色.png` 一样）或**自绘的纯色占位块**，
   绝不能用 mod 库里的任何图片素材。
4. **不得出现任何与本项目无关的窗口内容**。
   截图前确认前台只有管家窗口，别把别的应用（聊天记录、磁盘清理表、账号名）一起截进去。
5. 窗口标题栏、任务栏、浏览器地址栏、左下角账号头像都属于**会被截进去的区域**，注意检查。

## 怎么出图

用 `_ui_preview/_snap_repo.js`：它把 `ui.html` 用 jsdom 渲染成静态 HTML，
喂的是**纯演示数据**，再用无头 Edge 截图，天然不含真实数据。

> ⚠️ **注意 `_ui_preview/covers/`**：那批缩略图是从真实 mod 素材里弄来的，
> **出图时绝对不要用**（`_snap_repo.js` 里已经把 `thumb` 置空）。
> 要么让卡片缩略图空着，要么用自绘的纯色占位块。

```
# 渲染静态快照（输出到 _ui_preview/snap_repo_*.html）
node _ui_preview/_snap_repo.js

# 出图（--screenshot 必须是绝对路径；页面用 file:/// 绝对 URL，否则会走代理报 502）
msedge --headless=new --disable-gpu --no-proxy-server --hide-scrollbars \
  --window-size=1680,1000 --screenshot="D:/_zzmi_shots/repo_wide.png" \
  "file:///.../_ui_preview/snap_repo_wide.html"
```

`_ui_preview/_snap.js` 里也有 `mods_dir` 等字段，**同样是演示路径**，不要改回真实路径。

## 提交前自检

```bash
# 1. 出图脚本里不该出现任何真实的盘符绝对路径（只允许 D:\ZZMI_Demo\... 这种演示路径）
grep -rnE "[A-Za-z]:\\\\" _ui_preview/ | grep -v "ZZMI_Demo" || echo "干净"

# 2. 截图里肉眼过一遍顶栏路径 chip（静态 grep 抓不到渲染进像素的字）
```
