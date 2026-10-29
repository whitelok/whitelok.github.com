# 项目目录与维护入口

项目使用静态 HTML，可直接由 GitHub Pages 发布。根目录保留公开页面，内容、模板、资源和工具按用途归类。

```text
.
├── index.html / index_zh.html           # 英文 / 中文个人主页（生成）
├── products.html / products_en.html     # 中文 / 英文产品卡片目录（直接编辑）
├── ezvideorepair.html                   # 中文产品介绍页（生成）
├── ezvideorepair_en.html                # 英文产品介绍页（生成）
├── favicon.svg / favicon.ico            # 站点图标，保留通用根路径
├── og-cover.png                         # 主页分享图，保留已有公开地址
├── robots.txt / sitemap.xml             # 搜索引擎入口
├── MEMORY.md                           # 项目约定与操作历史
├── assets/
│   └── products/
│       ├── catalog.css                 # 产品卡片目录样式
│       └── ezvideorepair/
│           ├── icon.png
│           ├── app-zh.png / app-en.png
│           ├── style.css
│           └── page.js
├── content/
│   ├── profile/en.json / zh.json        # 双语个人主页内容
│   └── ezvideorepair/en.json / zh.json  # 双语产品介绍内容
├── templates/
│   ├── profile/en.html / zh.html        # 个人主页结构、样式与交互
│   └── ezvideorepair/page.html          # 产品介绍共享模板
├── scripts/
│   ├── maintain.py                     # 个人主页导出 / 检查 / 生成
│   └── build_ezvideorepair.py           # 产品介绍页生成
├── tests/
│   ├── test_maintain.py
│   └── test_ezvideorepair.py
└── docs/
    ├── structure.md                    # 本文
    ├── maintenance.md                  # 个人主页 JSON 维护指南
    ├── ezvideorepair-product-page.md    # 产品介绍维护指南
    └── superpowers/plans/              # 历史实施计划
```

## 日常修改

- **个人主页**：编辑 `content/profile/` 和 `templates/profile/`，运行 `python3 scripts/maintain.py check`，再运行 `python3 scripts/maintain.py build`。不要只改生成的首页。
- **产品介绍**：编辑 `content/ezvideorepair/`、`templates/ezvideorepair/page.html` 和 `assets/products/ezvideorepair/`，运行 `python3 scripts/build_ezvideorepair.py`。
- **产品目录**：直接同步编辑 `products.html`、`products_en.html`，共享样式位于 `assets/products/catalog.css`。
- **完整验证**：运行 `python3 -m unittest discover -s tests -v`。
- **本地预览**：在根目录运行 `python3 -m http.server 8000`，浏览 `http://localhost:8000/`。

生成脚本入口和公开 HTML 地址保持不变。`maintain.py --content-dir` 仍接收直接包含 `en.json`、`zh.json` 的目录，默认目录现为 `content/profile/`。资源迁移后统一使用 `assets/products/`，没有保留旧 `product-assets/` 的副本。
