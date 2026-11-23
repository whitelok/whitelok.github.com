# EZVideoRepair 页面维护

页面源码按用途和语言存放在 `src/pages/ezvideorepair/`。

- `product/` 存放产品介绍。
- `marketing/` 存放营销介绍。
- `privacy/` 存放隐私政策。
- `support/` 存放支持信息。

产品介绍页提供中文（`zh.html`）、英文（`en.html`）、西班牙文（`es.html`）、法文（`fr.html`）、阿拉伯文（`ar.html`）和日文（`ja.html`）。营销与隐私页提供前三种语言，支持页提供中英文。编辑时同步维护各语言的源码、页面链接和语言切换入口。阿拉伯语产品页使用从右到左的排版，版本号、型号和分辨率使用从左到右的顺序。

发布路径由 `src/routes.json` 定义。根目录 HTML 是发布产物，修改源码后运行 `python3 scripts/build_pages.py`，再运行 `python3 scripts/build_pages.py --check` 核对产物。

原有命令 `python3 scripts/build_ezvideorepair.py` 生成全部 EZVideoRepair 页面，`python3 scripts/build_ezvideorepair_es.py` 生成三个西班牙语页面。它们共享 `scripts/build_pages.py` 的发布逻辑。

图片、视频、CSS、JavaScript 继续放在 `assets/products/ezvideorepair/`。页面中的相对路径以根目录发布位置为基准。

早期产品 JSON、占位符模板和英文替换翻译表已由当前完整页面源码取代，可通过 Git 历史查看。

## 各语言的操作演示

各产品页的首屏演示按钮指向本页的操作录像。发布新增语言或更新演示时，在对应语言的 App 界面中录制实际修复流程，使用 `1999-USGS-Flume-30s.mp4` 选取 5 秒进行修复，展示原片与结果的比较。原片及四种模型的效果对比视频由各语言页共用。

操作录像按语言保存为 `assets/products/ezvideorepair/usgs-flume/ui-demo-{zh,en,es,fr,ar,ja}.mp4`，每种语言一个文件。同步核对播放器、封面、无障碍说明与 MP4 链接指向的语言。发布前逐页打开操作实录，确认首页入口、播放、跳转及文件直链均正常。工作台、处理时长、模型管理和设置四张配图均从对应语言的真实 App 界面采集，并核对图注和替代文字。

## 下载区的发布信息

每次更新 EZVideoRepair 产品页时，下载按钮下方都按以下顺序分四行展示：

1. 版本号：只显示面向用户的版本号，例如 0.0.6。
2. 更新日期：使用该语言自然的日期格式，并同步更新 `<time datetime="YYYY-MM-DD">`。
3. 兼容系统版本：写明芯片要求和最低 macOS 版本。
4. 安装方式：说明如何打开 DMG 并将 EZVideoRepair 拖入「应用程序」。

六种语言同步更新。每项独占一行，窄屏可以在单项内自然换行。
