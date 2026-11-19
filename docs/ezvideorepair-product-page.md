# EZVideoRepair 页面维护

页面源码按用途和语言存放在 `src/pages/ezvideorepair/`。

- `product/` 存放产品介绍。
- `marketing/` 存放营销介绍。
- `privacy/` 存放隐私政策。
- `support/` 存放支持信息。

每个目录以 `zh.html`、`en.html`、`es.html` 区分语言，支持页目前有中英文。编辑时同步维护相应语言的内容与链接。西班牙语页面直接维护已翻译的源码。

发布路径由 `src/routes.json` 定义。根目录 HTML 是发布产物，修改源码后运行 `python3 scripts/build_pages.py`，再运行 `python3 scripts/build_pages.py --check` 核对产物。

原有命令 `python3 scripts/build_ezvideorepair.py` 生成全部 EZVideoRepair 页面，`python3 scripts/build_ezvideorepair_es.py` 生成三个西班牙语页面。它们共享 `scripts/build_pages.py` 的发布逻辑。

图片、视频、CSS、JavaScript 继续放在 `assets/products/ezvideorepair/`。页面中的相对路径以根目录发布位置为基准。

早期产品 JSON、占位符模板和英文替换翻译表已由当前完整页面源码取代，可通过 Git 历史查看。
