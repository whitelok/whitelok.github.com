# 项目目录与维护入口

项目由个人主页和产品站点组成，使用静态 HTML 发布。

```text
.
├── *.html                         # 已有公开页面，文件名就是发布 URL
├── favicon.svg / favicon.ico      # 站点图标
├── og-cover.png                   # 首页分享图
├── robots.txt / sitemap.xml       # 搜索引擎入口
├── MEMORY.md                      # 项目约定与操作记录
├── src/
│   ├── routes.json                # 页面源码到公开 HTML 的对应清单
│   └── pages/
│       ├── catalog/               # 产品目录，zh.html / en.html
│       └── ezvideorepair/
│           ├── product/           # 产品介绍，zh / en / es
│           ├── marketing/         # 营销介绍，zh / en / es
│           ├── privacy/           # 隐私政策，zh / en / es
│           └── support/           # 支持信息，zh / en
├── content/profile/               # 个人主页 en.json / zh.json
├── templates/profile/             # 个人主页 en.html / zh.html 模板
├── assets/products/
│   ├── catalog.css                # 产品目录样式
│   └── ezvideorepair/             # 产品样式、脚本、图标、截图与视频
├── scripts/
│   ├── maintain.py                # 个人主页检查、生成与导出
│   ├── build_pages.py             # 按清单发布产品站点和目录
│   ├── build_ezvideorepair.py      # 原有产品构建命令入口
│   └── build_ezvideorepair_es.py   # 原有西班牙语构建命令入口
├── tests/                         # 个人主页、产品站点回归检查
└── docs/                          # 目录、维护指南及历史计划
```

## 编辑与生成

个人主页编辑 `content/profile/` 和 `templates/profile/`，运行以下命令。

```bash
python3 scripts/maintain.py check
python3 scripts/maintain.py build
```

产品目录及产品各类页面编辑 `src/pages/` 下的对应语言源码，运行以下命令。

```bash
python3 scripts/build_pages.py
python3 scripts/build_pages.py --check
```

完整回归检查与本地预览使用以下命令。

```bash
python3 -m unittest discover -s tests -v
python3 -m http.server 8000
```

## 发布地址

根目录保留现有 15 个 HTML。个人主页由 `maintain.py` 维护，其余 13 页由 `src/routes.json` 映射。新增页面时向清单添加源码和目标文件的对应关系。

根目录 HTML 和 `assets/` 是网站实际发布文件。`src/`、`content/`、`templates/` 是维护源码，页面中的相对链接需按生成后的根目录位置填写。favicon、分享图片和资源地址沿用现有路径。

个人主页细节见 `docs/maintenance.md`，产品站点维护见 `docs/ezvideorepair-product-page.md`。
