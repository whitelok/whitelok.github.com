# Vibe Coding Memory — Karl Luo 个人介绍页

> 用途：供后续 vibe coding 会话复用。包含任务背景、技术经验、设计规范、用户偏好、内容数据源。
> 产物：`index.html`（英文版）+ `index_zh.html`（中文版，内容一致全翻译）+ `avatar.png`（LinkedIn 头像抠图，当前版本已从页面移除但文件保留）。语言切换为导航栏右上角小胶囊按钮 `.lang-switch`（中文 ⇄ English，12px，勿放回 hero）。
> 最后更新：2026-10-29（整理项目目录结构）

## ⚠️ 第一规则（用户明确要求）

**内容维护来源已改为 `content/profile/en.json` 与 `content/profile/zh.json`；修改内容后运行 `python3 scripts/maintain.py build` 同时生成两版。布局、样式和动画修改应在 `templates/profile/en.html` 与 `templates/profile/zh.html` 中同步进行，再生成页面。不要仅修改生成的 HTML，否则下次 build 会覆盖。完整说明见 `docs/maintenance.md`。**

**后续所有操作都必须同步记录到 `MEMORY.md`（用户于 2026-10-02 明确要求）。每次操作完成后记录实际改动、验证结果及必要的差异或限制，并更新本文件的最后更新日期。**

**任何内容/样式修改，必须同步更新英文版（index.html）和中文版（index_zh.html）两个文件，保持结构、样式、信息完全一致（仅语言不同）。修改后两版都要截图验证。**
例外：用户明确指定只改某一版时（如中文版头衔"模型工程负责人"仅改 zh 版），按指令执行并在本文件记录差异。

### 两版已知差异
- **学校名称**：用户于 2026-10-10 明确要求英文版 `index.html` 仅显示 Shanghai University、Guangzhou University，不显示中文学校名；中文版保留原有学校名称。
- **头衔**：EN 用 "Director of Machine Learning Systems"；ZH 用户指定用「**模型工程负责人**」（2026-10-01，4 处：title/meta/hero role/小红书 h3）。

---

## 1. 任务背景

- 目标：根据 LinkedIn 主页 + 两份 PDF 制作**本地个人介绍 HTML 页面**（单文件、无外部依赖、双击可开）。
- 人物：Karl Luo（骆兆楷），Director of Machine Learning Systems @ RedNote·小红书。
- 数据源：
  - `https://www.linkedin.com/in/karl-luo-a74a4964`（未登录公开页大量字段被星号掩码，只能拿到姓名/公司/学校/粉丝数）
  - `Profile.pdf`（LinkedIn 导出，含完整经历/教育）
  - `screencapture-linkedin-*.pdf` + 同名 `.png`（登录态全页截图，含头像、奖学金细节、准确粉丝数 2.6K）

## 2. 技术经验（重要）

### 模型读不了 PDF 的绕法
- 模型不支持 PDF 附件输入，**不要反复尝试 read PDF**。
- 文本型 PDF：`pdftotext -layout in.pdf out.txt`（macOS 自带 poppler），再 read 文本。
- 截图型 PDF：检查同目录是否有**同名 PNG**（用户导出的 screencapture 常带 PNG），PNG 可直接 read；大图用 PIL 切块（1100px 宽/块）分批读。
- `pdfimages -list` 可查 PDF 内嵌图片（LinkedIn 导出 PDF 无图片）。

### 头像提取（PIL）
- 从全页截图定位圆形头像：先低分辨率估算中心坐标和半径 → 按缩放比换算回原图 → 逐步微调裁剪框。
- 圆形抠图：4 倍超采样画 ellipse mask → LANCZOS 缩小 → `putalpha`，边缘 inset 几 px 去杂边。
- 产物 400×400 透明 PNG。（注：后续版本用户要求删除头像，文件保留在目录中可复用。）

### 页面验证工作流（每次改完必做）
```bash
# 1. 生成静态预览（禁用 reveal 动画，否则截图内容不可见）
sed -e 's/\.reveal{opacity:0;transform:translateY(26px);/\.reveal{opacity:1;transform:none;/' \
    index.html > /tmp/preview.html
# 2. headless Chrome 截图
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --window-size=1440,5600 --hide-scrollbars --screenshot=/tmp/full.png file:///tmp/preview.html
# 3. PIL/numpy 定位内容并裁块再 read（整图太大读不了）
#    注意：页面有全屏 ambient 渐变，简单阈值会误判 → 用深色文字检测 a<120 定位内容行
```
- hero 若用 `min-height:100vh`，截图前 sed 改成固定值，否则整屏被 hero 占满（当前版本已移除 100vh）。
- headless 截图时**计数动画会停在中间值**（如 299M+），不是 bug（当前版本计数器已随 stats 区一起删除）。
- 临时预览文件若引用相对路径资源（如 avatar.png），需拷贝到同一临时目录。
- 用完清理 /tmp 临时文件，`open` 真实文件让用户查看。

## 3. 设计规范（当前定稿 · 浅色主题）

### 色板 / 基础
- 背景 `#f5f6f8`，卡片 `#fff`，文字 `#171a21` / dim `#565d6b` / faint `#959cab`
- 主色 小红书红 `#ff2442`（deep `#e01a36`，soft `rgba(255,36,66,.08)`），奖项金 `#c9930a`
- 圆角 16px；阴影 `0 1px 2px + 0 8px 28px rgba(20,24,40,.07)`；hover 上浮 -4px
- 字体栈 Inter/SF Pro/PingFang；等宽 SF Mono/Menlo（时间、计数、来源标注）
- 环境光：fixed 定位的红/蓝 radial-gradient（opacity ~.1, blur 50px）
- 动效：IntersectionObserver `.reveal` 上滑渐入；支持 `prefers-reduced-motion`

### 页面结构（当前）
```
nav（毛玻璃，KL logo + 语言切换；顶部 Experience/Education/Contact 导航已删除，勿恢复）
└─ hero：Karl Luo.骆兆楷（h1 超大字+红句点+中文名小字灰色）→ 头衔行 → 3 按钮（LinkedIn/Google Scholar/Team GitHub）
└─ — EXPERIENCE（kicker 大标题）→ timeline（6 段经历，近→远）
└─ — EDUCATION（kicker 大标题）→ 纵向教育卡片 ×2
└─ footer（邮箱/LinkedIn/Scholar/GitHub）
```
**已删除元素**（用户明确要求，勿恢复）：About 区、stats 数据框、Expertise 技能墙、hero 简介长句、hero meta 标签（地点/粉丝数）、头像、Get in touch 按钮、"Where I've worked / Where I studied" 二级标题。

### 组件
- **kicker 区块标题**：不用 h2！红色 `— EXPERIENCE`（mono **18px bold** 大写 + 前置 34px×2px 红横线）
- **timeline**：左侧 2px 渐变红线，当前公司红圈带光晕、过往灰圈；条目 **h3 17px**（公司红 `·` 中文 — 岗位）；时间 mono 12px 灰；要点红短横 bullet；tag 胶囊
- **bullet 句式（标杆=小红书条目）**：**动词开头的完整句子**（Lead/Founded/Co-founded/Developed/Contributed/Served/Granted/Optimized/Accelerated/Built/Tuned），**禁止 "LLM:"/"Training:"/"Publication:" 这类分类前缀**；关键术语行内 `<b>` 加粗
- **折叠组 `<details class="fold" open>`**（核心组件，默认展开，CSS 已泛化不限于 timeline）：白底圆角边框，summary 11.5px 带红色 ▸（open 旋转 90°），右侧 `.cnt` 计数（mono 10px）；内容 `ul.fold-list` 11px 红点 bullet；`.src` 来源标注（mono 9.5px）；`.badge` 红色徽章（如 `CCF-B · IF 3.8`、`EMNLP 2026 Main · 15.4% acceptance`）
- **教育卡片**：`.edu` 纵向单栏，白卡 padding 18-20px，校名 14.5px、专业 12px、年份 mono 10.5px，内部嵌 fold 子项（11px/内容 10.5px）

## 4. 用户偏好（多轮迭代沉淀，务必遵守）

1. **极简结构**：见上方"已删除元素"清单——这些都被要求删过，勿主动加回。
2. **归组原则**：论文/专利/奖项/宣传稿/开源贡献**不单独开区块**，必须嵌入对应公司/学校条目内，用 `<details open>` 折叠子项（Academic Publications / Press & Media Coverage / Open Source & Community / Awards / Scholarships & Honors）。专利单独一条普通 bullet。
3. **折叠组默认展开**、小字体、可收起。
4. **bullet 句式统一**：动词开头完整句，无分类前缀（腾讯/阿里/NVIDIA 已按小红书标杆统一）。
5. **排序**：工作经历近→远；所有论文列表也近→远（新→旧）。
6. **论文格式**：本人作者加粗（`**Luo, Z.**`）；期刊/会议名斜体；CCF 等级/影响因子/录取率用 `.badge`；arXiv/HF 论文附链接 + 编号 mono 标注。
7. **中英文混排**：公司名 `英文 · 中文`；技术名词保留中文（混元/无量/一念/昇腾/燧原/紫霄/智影/小蛮驴/点点/AI搜索）。
8. **间距紧凑**：区块 padding ~26-76px，hero 不要 100vh。
9. **奖项**：奖牌 emoji（🏆🥇🥉⭐）逐条列出，归入 Awards 折叠子项。
10. **标题归属清晰**：复合身份（如 PCG C++ Committee Member）放正文 bullet 写清时间段，不堆在 h3 标题里。

## 5. 内容数据源（已核实，可直接复用）

- **小红书 · Xiaohongshu** — Director of ML Systems（2025.08– 至今）：
  - bullets：Lead ML Infra（Search/Ads/Rec，technical lead+核心贡献者）；创立 AI Infra（AIGC/LLM/VLM，**生产级统一框架**——用户 2026-10-01 明确将"业界首个"软化为 production-grade）；LLM serving → AI搜索+点点 300M MAU；AIGC 推理优化 GPU/NPU/PPU/XPU（speed-of-light）；Awards: 🏆 2025 Impact Challenge — Business Breakthrough Award, Annual Champion
  - Academic Publications 折叠组（10 篇，近→远）：RedKnot(2606.06256)、Akashic(2607.05708)、FlowBlock(2607.17652)、Hierarchical Latent Reasoning(2607.27760)、OneModel(2608.18606)、PILOT(2608.26530)、AtomRec(2609.04882)、RedKnot-MLA(2609.07008)、PACT(HF 2609.26355)、EMNLP 2026 Main（15.4% acceptance，无链接带 badge）
  - Press & Media 折叠组（9 篇）：KV Cache 按头分家/China Daily RedKnot/FDFO 木桶效应/发改委谢涛演讲/B站云栖大会 T-Head SAIL（标题为完整版「…完整回放 1080P（精准空降到 25:50）」，t=1550）/OneModel×2/GR-Inference×2（含 NVIDIA Developer）
  - Open Source 折叠组（4）：RedKnot 仓库、Megatron-Bridge PR#3769、sglang PR#27551/#27877
- **腾讯 · Tencent** — Deep Learning Framework Senior Staff（2020.05–2025.08，深圳 5y4m）：
  - bullets（动词开头）：Founded KsanaLLM（一念，超 SGLang/vLLM 45%，基准 2025-06-13，ima.copilot）；Developed 混元 AI-Infra（GPU/昇腾/燧原/紫霄）；Co-founded Venus（智影/王者/和平精英）；Co-founded 无量（10B+ QPD）+ GameLoop 联邦学习主架构；Contributed HugeCTR（MLPerf 2020/2021 世界纪录，NVIDIA Dev Blog）+ S-LoRA PR#13；Served PCG C++ Committee Member（2021.11–2025.08）；Granted patent CN118446316A
  - Academic Publications 折叠组（1）：KubeGPU, J. Supercomputing 79(1):591–625, 2023
  - Awards 折叠组（6）：🥇2024 PCG H1 CVP 技术创新奖；🥉2024 腾讯技术突破奖铜奖；⭐优秀员工 2020–2023；⭐杰出贡献 2020/2022/2023；⭐开源协同优秀贡献 2021–2023；⭐2020 卓越研发奖+开源协同奖
- **阿里 · Alibaba DAMO**（2018.10–2020.05，杭州 1y8m）：达摩院自动驾驶实验室·小蛮驴物流车项目；训练侧（图优化/剪枝/量化压缩/蒸馏/NAS AutoML-Keras）；推理侧（TVM 调优、GPU/NPU 自定义算子、Autopilot 边缘推理引擎）
- **NVIDIA**（2016.05–2018.10，上海 2y6m）：TensorRT 4.0+/5.0RC 特性开发、DrivePX2/Jetson TX2/TX1 调优、INT8/INT4 量化校准；cuDNN 调优；GFE/GFN/COSMOS 自动化
- **饿了么实习**（2015.09–2016.03，上海）：Talaris API（Flask+Vespone+Thrift+Redis+MySQL）
- **Intel 实习**（2014.05–2015.08，1y4m）：面向 **Intel Xeon Phi（至强融核）众核处理器**的自动化 Profiling 与**性能调优**（PVL 团队；调优含义已润色进正文，不写"侧重…"尾巴）；基于 MCG 框架搭建分布式自动化测试系统（Django+UWSGI+Nginx / Celery 调度 / Redis / MySQL）
- **上海大学硕士**（2013–2016，HPC 与并行计算，First Honour）：
  - Scholarships & Honors（6）：国家研究生奖学金(2014,2015)、光华一等奖、PAC 华东一等奖、研究生 MCM 二等奖、校一等奖学金、校优秀学生
  - Academic Publications（4，近→远，标注 SCI×1/EI×4）：psobj NSS 2015（Springer pp.96–109）；JSS 2015 102:182–191 `CCF-B·IF 3.8`；Nguyen CIS 2014 pp.115–125；Bitcoin CSA 2013 IEEE pp.483–486
- **广州大学本科**（2009–2013，**应用数学系信息安全专业密码学方向** → "Information Security (Cryptography), Department of Applied Mathematics"，GPA 3.75）：
  - Scholarships & Honors（5）：全国信息技术应用大赛二等奖(2011)、AFC 挑战杯省金奖(2011)、校金奖(2010)、校奖学金×4、中国专利×2
  - Academic Publications（1）：ISPEC 2014 Obfuscating encrypted web traffic `CCF-C`（用户明确要求从上大挪到广大）
- 联系：whitelok@gmail.com / linkedin.com/in/karl-luo-a74a4964 / Google Scholar（user=tKJPx-oAAAAJ）/ github.com/rednote-machine-learning

## 6. 变更响应模式

用户习惯**连续小步修改**（每轮 1-3 个精确指令），标准响应流程：
1. **同一改动同时 edit 英文版 index.html 和中文版 index_zh.html**（见"第一规则"）
2. sed 静态化 + headless 截图 + PIL 裁块验证（两版都要验证，定位到改动区域）
3. 清理临时文件 + `open` 页面
4. 一句话汇报改动点
5. 同步更新 `MEMORY.md`，记录本次操作及验证结果。

## 7. 操作记录

### 2026-10-02
- 在英文版 `index.html` 和中文版 `index_zh.html` 的 `<head>` 元素之后，原样添加用户提供的 Google tag（gtag.js）代码，测量 ID 为 `G-XBS6JF7VRM`。
- 脚本异步加载 `https://www.googletagmanager.com/gtag/js?id=G-XBS6JF7VRM`，初始化 `window.dataLayer` 和 `gtag`，并调用 `gtag('config', 'G-XBS6JF7VRM')`。
- 验证：已检查两版各仅有一份 Google 代码，`git diff --check` 通过；尚未验证上线后的数据接收。本次未修改可见内容或样式，未执行截图验证。
- 将用户要求「后面的操作都要同步到 MEMORY.md」写入本文件的第一规则和变更响应流程。
- 用户授权将上述双语 Google Analytics 修改及本文件提交并推送到 `origin/master`（`https://github.com/whitelok/whitelok.github.com`）；提交前 `git diff --check` 通过。推送结果以 Git 命令回执为准。

### 2026-10-03
- 为 `index.html` 和 `index_zh.html` 添加 canonical、SVG/ICO favicon、Open Graph、Twitter 大图卡片及 WebSite/ProfilePage/Person JSON-LD，保留原 Google Analytics 代码和全部正文、样式。
- 英文 canonical 为 `https://whitelok.github.io/`；中文为 `https://whitelok.github.io/index_zh.html`。两版均标注 `en`、`zh-CN` 和指向英文首页的 `x-default` hreflang；Open Graph locale 分别为 `en_US`、`zh_CN`，不是示例中的日语。
- 英文标题/描述长度为 57/144 字符，中文为 25/86 字符；描述使用页面真实履历内容。
- 根目录创建 `favicon.svg` 和 `favicon.ico`（红色 KL 标识）、`og-cover.png`（1200×630，沿用页面色板与姓名/头衔）、`robots.txt`（允许抓取并提供 sitemap 入口）、`sitemap.xml`（两版规范 URL 及语言关联）。本次 sitemap 仅覆盖用户指定的两个个人介绍页面。
- 验证：两版 HTML 解析、唯一 canonical/Google tag、JSON-LD 解析、标题/描述长度、引用资源存在性、XML 解析、封面尺寸及 `git diff --check` 通过；逐字比较确认 `<style>` 之后内容未变。两版 headless Chrome 截图及封面已查看，显示正常。
- 用户已授权将本次 SEO 修改、五个新增资源文件及 `MEMORY.md` 提交并推送到 `origin/master`；推送结果以 Git 命令回执为准。线上 SEO 得分和收录效果需发布后重新检测。

### 2026-10-08
- 按用户要求删除两版顶部的三个区块导航项：英文 Experience/Education/Contact，中文工作经历/教育经历/联系方式；保留 KL 标识和语言切换按钮。
- 修改文件：`index.html`、`index_zh.html`、`MEMORY.md`。两版导航结构检查通过；用户已授权提交并推送到 `origin/master`，推送结果以 Git 命令回执为准。
- 验证：`git diff --check` 通过；两版 Chrome 截图已查看，顶部仅保留标识和语言切换，页面显示正常。

### 2026-10-08：新增小红书学术论文
- 读取用户指定的 Google Scholar 主页（https://scholar.google.com/citations?hl=en&user=tKJPx-oAAAAJ），按最新论文列表与现有条目比较，确认新增三篇，并在 arXiv 核实标题、编号及 Zhaokai Luo 作者身份。
- 在 `index.html` 与 `index_zh.html` 的小红书 Academic Publications / 学术论文列表顶部，按 Scholar 顺序添加：CompoWorld: Compositional Environment Scaling for General Agents（https://arxiv.org/abs/2609.33665）；Skill2Env: Capability-Oriented Environment Synthesis from Skills for General Agents（https://arxiv.org/abs/2609.33772）；Learning to Learn from Context: Synthetic Training from Perturbed Public Documents（https://arxiv.org/abs/2609.33642）。
- 沿用现有标题链接、`target="_blank"`、`rel="noopener"` 和 `.src` arXiv 编号格式；计数从 10 更新为 13，保留原有十篇及其顺序。
- 验证：两版各 13 个条目、新增链接无重复、双语链接列表一致、`git diff --check` 通过；已查看两版论文区域 Chrome 截图，显示正常。
- 用户已授权将新增三篇小红书论文、双语计数更新及 `MEMORY.md` 提交并推送到 `origin/master`；推送结果以 Git 命令回执为准。

### 2026-10-10：开源贡献补充 PR 标题
- 在双语工作经历 Open Source & Community / 开源与社区贡献的三个 GitHub PR 条目末尾追加 GitHub 原始英文标题，保留仓库链接、PR 编号和现有样式。
- PR #3769：[model] feat: add Qwen3.5 text model bridges (dense + MoE)。
- PR #27551：[dLLM] Make FDFO a framework capability for all dLLM algorithms。
- PR #27877：[dLLM] Reuse block KV/req slots in place across FDFO rounds。
- 标题来源：GitHub PR 页面（sglang #27551/#27877）及 GitHub REST API（Megatron-Bridge #3769）。两版条目一致，`git diff --check` 通过；用户已授权将双语 PR 标题及 `MEMORY.md` 提交并推送到 `origin/master`，推送结果以 Git 命令回执为准。
- 已查看双语页面截图，三个完整 PR 标题显示正常。

### 2026-10-10：同步页脚修改
- 用户请求推送时发现两版页脚新增本地修改：删除英文 `Crafted locally with HTML & CSS` 及中文「本地 HTML & CSS 手工制作」，保留版权年份和姓名。
- 将双语页脚修改与本记录一起提交并推送至 `origin/master`；`git diff --check` 通过。推送结果以 Git 回执为准。

### 2026-10-10：英文版学校名称
- 按用户指定仅修改 `index.html`：删除 Shanghai University 后的「· 上海大学」及 Guangzhou University 后的「· 广州大学」。中文版保持原样，并在两版已知差异中记录。
- 验证：英文学校名保留、两处中文后缀已删除，`git diff --check` 通过；尚未提交或推送。

### 2026-10-10：KubeGPU 论文等级
- 根据用户提供的等级，在中英文版腾讯工作经历的 KubeGPU 论文末尾添加 `<span class="badge">CCF-C</span>`，沿用现有论文等级徽章样式。
- 验证：两版 KubeGPU 条目各有一个 CCF-C 徽章，`git diff --check` 通过；尚未提交或推送。

### 2026-10-10：推送学校名称与论文等级修改
- 用户授权将英文版学校中文后缀删除、双语 KubeGPU 的 CCF-C 徽章及 MEMORY.md 操作记录一起提交并推送到 origin/master。
- 提交前 git diff --check 通过；推送结果以 Git 命令回执为准。

### 2026-10-14：新增 Vela 论文
- 在中英文版小红书学术论文列表顶部添加 Vela: User Behavior as Supervision Sparks LLM Intelligence（https://arxiv.org/abs/2610.14709），沿用标题链接与 .src arXiv 编号格式，计数从 13 更新为 14。
- 已从 arXiv 核实标题、编号及 Zhaokai Luo 作者身份；两版均为 14 条且新增链接无重复，git diff --check 通过。本次未进行截图验证。
- 用户已授权将 Vela 论文双语更新及 MEMORY.md 提交并推送至 origin/master；提交前 git diff --check 通过，推送结果以 Git 回执为准。

### 2026-10-17：手机工作经历首次打开空白
- 根据用户截图发现标题和时间线可见、工作条目不可见；根因是 `.reveal` 默认 opacity:0，IntersectionObserver threshold:.12 对手机上的超长工作经历条目可能永远无法达到，导致持续透明。
- 同步修复 index.html 与 index_zh.html：内容默认可见，observer 阈值改为 0，进入视口时仅通过一次性 keyframes 播放原有渐入上移动画；无 IntersectionObserver 或 JS 未运行时正文仍可见，减少动态效果偏好下禁用动画。
- 验证：Node VM 检查观察器阈值、进入回调、缺少观察器环境正常执行和默认可见 CSS；git diff --check 通过。使用全新 Chrome 配置在 390×844 窗口截图，已查看双语 Experience 工作内容可见。尚未在用户截图所用的手机 WebView 真机验证。
- 用户已授权将双语手机版显示修复及 MEMORY.md 提交并推送到 origin/master；提交前 git diff --check 通过，推送结果以 Git 回执为准。

### 2026-10-17：相连的社交链接按钮
- 中英文版 LinkedIn、Google Scholar、Team GitHub 改为一组相连按钮：共享外框和圆角，按钮间用分隔线，不再分开或换行。
- 手机宽度下整组占满可用宽度，按钮使用弹性宽度、较小图标和自适应字号；约束 hero 内容最大宽度，防止内容撑宽按钮组。保留原链接及键盘焦点提示。
- 窄屏媒体规则覆盖 600px 以下；git diff --check 通过。初次 Chrome 390px 窗口截图存在浏览器最小布局宽度导致的裁切，后续使用 500px 窗口验证完整显示。尚未提交或推送。
- 已查看两版最终 500px 窄屏截图，三项相连且完整显示在同一行。

### 2026-10-17：推送相连社交按钮
- 用户授权将中英文相连社交按钮及手机自适应样式、MEMORY.md 记录一起提交并推送至 origin/master。
- 提交前 git diff --check 通过；推送结果以 Git 回执为准。

### 2026-10-17：缩小手机姓名上方留白
- 两版在 600px 以下将 hero 顶部 padding 从 170px 调整为 96px，减少姓名上方 74px 留白，保留桌面间距及固定导航栏所需空间。
- git diff --check 通过；尚未提交或推送。
- 已查看两版 500px 窄屏 Chrome 截图，姓名顶部留白缩小且未被导航遮挡。

### 2026-10-17：小红书专利记录
- 根据用户提供的专利号，在中英文版小红书工作经历的普通 bullet 列表末尾添加 CN122845659A，使用专利申请表述及加粗编号格式，未声明已获授权，未另建区块。
- 已检查两版各出现一次并归属小红书条目；git diff --check 通过。尚未提交或推送。

### 2026-10-17：缩小桌面姓名上方留白
- 按用户要求，将中英文版默认 hero 顶部 padding 从 170px 缩小至 110px，减少桌面顶部 60px 留白；保留已调整的手机 96px 规则。
- git diff --check 通过，未改动正文内容。尚未提交或推送。
- 已查看两版 1440px 桌面截图，姓名顶部间距缩小且未被导航遮挡，专利申请条目显示正常。

### 2026-10-17：推送顶部间距与专利记录
- 用户授权将双语手机/桌面 hero 顶部间距调整、小红书专利申请 CN122845659A 及 MEMORY.md 操作记录一起提交并推送至 origin/master。
- 提交前 git diff --check 通过；推送结果以 Git 回执为准。

### 2026-10-17：通过 JSON 生成双语页面
- 运行 scripts/maintain.py build，双语结构及 HTML 检查通过，更新 index.html 与 index_zh.html；工作经历 6 项、教育 2 项。具体修改见 content/en.json 和 content/zh.json 的 Git 差异。

### 2026-10-17：Python + JSON 双语维护工具
- 新增 `scripts/maintain.py`，仅使用 Python 3.9+ 标准库；提供 export / check / build，以及 --content-dir、--output-dir、export --force。
- 将当前页面内容导出到 `content/en.json`、`content/zh.json`；静态 CSS、SVG、Google Analytics、canonical/hreflang、动画保存在双语 templates/*.html。JSON 包含 SEO、姓名头衔、链接、工作经历、专利、论文、折叠组、教育和页脚等内容。
- 两版按条目 ID 和顺序检查工作、教育、bullet、折叠组及其列表的对应关系，允许既有语言文案差异；不会自动翻译或判断自然语言语义一致。折叠组的 {{count}} 自动更新，title/description 自动同步社交元数据与 ProfilePage JSON-LD。
- check 和预览不修改源页面；build 先完成两版验证和渲染再写入，并自动追加 MEMORY.md 生成记录。export 默认拒绝覆盖已有数据，须显式 --force。
- 新增 MAINTENANCE.md 中文说明、10 项 unittest 回归检查、实施计划；.gitignore 排除 Python 缓存。
- 已用初始 JSON 生成当前两版页面，仅格式空白变化；HTML token 比较证明内容、标签、属性、JSON-LD、样式和脚本保持一致。回归覆盖新增论文及计数、错误输入不写入、预览隔离、导出保护等。
- 尚未提交或推送。

### 2026-10-26：通过 JSON 生成双语页面
- 运行 scripts/maintain.py build，双语结构及 HTML 检查通过，更新 index.html 与 index_zh.html；工作经历 6 项、教育 2 项。具体修改见 content/en.json 和 content/zh.json 的 Git 差异。

### 2026-10-26：新增 Iris 与 Navalia 论文
- 在中英文版小红书工作经历的学术论文列表顶部添加 Iris: Climbing to the Search Frontier 和 Navalia: Advancing Cowork Agents through Verifiable Task Synthesis and Long-Horizon Post-Training，使用用户提供的 Google Scholar 链接，计数从 14 更新为 16。
- 双语内容检查、页面生成、条目唯一性和 git diff --check 通过；用户授权提交并推送本次论文更新。

### 2026-10-26：论文链接改为 arXiv
- 核实 Iris 对应 arXiv 2609.04304、Navalia 对应 arXiv 2610.26887，将双语页面链接改为 arXiv abs 页面，并同步来源编号和 JSON 数据。
- 双语内容检查、页面生成及暂存差异检查通过；按用户要求重新提交。

### 2026-10-26：通过 JSON 生成双语页面
- 运行 scripts/maintain.py build，双语结构及 HTML 检查通过，更新 index.html 与 index_zh.html；工作经历 6 项、教育 2 项。具体修改见 content/en.json 和 content/zh.json 的 Git 差异。

### 2026-10-26：小红书论文按 arXiv 时间排序
- 中英文版小红书学术论文按 arXiv 编号对应的首次提交顺序从新到旧排列；EMNLP 2026 论文保留在末尾，PACT 按其 HF Papers 对应的 arXiv 编号 2609.26355 参与排序。
- 保留全部 16 篇论文，未修改标题、链接与计数；双语生成和排序一致性检查通过。

### 2026-10-26：通过 JSON 生成双语页面
- 运行 scripts/maintain.py build，双语结构及 HTML 检查通过，更新 index.html 与 index_zh.html；工作经历 6 项、教育 2 项。具体修改见 content/en.json 和 content/zh.json 的 Git 差异。

### 2026-10-27：更新 EMNLP 论文正式链接
- 读取用户提供的 Scholar 记录，确认其对应现有 Rethinking Diffusion Large Language Models via Time-aware Weighting and Block-oriented Refinements，正式发表链接为 https://aclanthology.org/2026.emnlp-main.1836/。
- 双语 JSON 为标题添加正式页面链接及 .src 论文编号标注，保留 EMNLP 2026 Main 和录取率徽章、末尾位置及总数 16。
- 双语内容检查、页面生成、链接唯一性和 git diff --check 通过。

### 2026-10-27：通过 JSON 生成双语页面
- 运行 scripts/maintain.py build，双语结构及 HTML 检查通过，更新 index.html 与 index_zh.html；工作经历 6 项、教育 2 项。具体修改见 content/en.json 和 content/zh.json 的 Git 差异。

### 2026-10-27：移除 EMNLP 灰色来源标记
- 按用户要求从中英文版 EMNLP 论文移除灰色 ACL Anthology 2026.emnlp-main.1836 标记，保留标题正式链接及会议、录取率徽章。
- 双语生成检查、标记移除和链接保留检查、git diff --check 通过。

### 2026-10-27：通过 JSON 生成双语页面
- 运行 scripts/maintain.py build，双语结构及 HTML 检查通过，更新 index.html 与 index_zh.html；工作经历 6 项、教育 2 项。具体修改见 content/en.json 和 content/zh.json 的 Git 差异。

### 2026-10-28：清理与当前首页无关的旧博客文件
- 检查双语首页、模板、内容及 sitemap 引用后，将旧博客年份文章、archives、page、css、js、lib、images、resources、旧 404.html 和 ._.DS_Store 移出项目，共 159 个文件、74,705,030 字节。旧文章地址在发布清理后将不再提供内容。
- 保留双语首页、favicon、og-cover.png、robots.txt、sitemap.xml，以及 JSON 内容、模板、维护脚本、测试、维护说明与实施记录；未改动首页代码和内容。
- 删除前文件备份位于 /private/tmp/whitelok-legacy-backup-5c65du4m，包含 cleanup-manifest.json；原 Git 已跟踪文件也可从历史恢复。
- 已核对首页哈希保持一致、本地资源均存在、双语内容检查与维护回归测试通过。尚未提交或推送。
- 回归初次运行发现新增论文计数测试仍硬编码 15；改为按输入原有条目数加 1 计算预期值，重跑 10 项测试全部通过。


## 2026-10-28: EZVideoRepair independent bilingual product pages

- Added ezvideorepair.html (Chinese primary) and ezvideorepair_en.html. Existing personal index pages were not edited or regenerated by this task.
- Paired content: content/ezvideorepair/zh.json and en.json. Shared template: templates/ezvideorepair.html. Dedicated styles, script, app icon and real no-media screenshots: product-assets/ezvideorepair/.
- Rebuild both with python3 scripts/build_ezvideorepair.py. Maintenance: docs/ezvideorepair-product-page.md. Every future change must check both languages; Chinese is primary and English should read naturally.
- Original design informed by the user-provided HitPaw structure, with actual supported features only. States Apple Silicon, macOS 14+, 24GB memory, ~7.79GB model and 512-pixel short-edge limit. No 4K/8K, interpolation, public installer or App Store availability claim. CTAs point to the actual GitHub project and Hugging Face model repository. No analytics added.
- Verification: two product-page structure/link/asset tests pass; existing scripts/maintain.py check passes for both personal languages. Isolated headless-browser QA covers Chinese and English at 1440px desktop and 390px mobile, with no horizontal overflow or broken images and keyboard-operable FAQ. Top/features/FAQ screenshots were checked. Secondary light-background text contrast improved in shared CSS.
- Local delivery only: no website deployment or repository push. Preexisting uncommitted changes preserved.

### 2026-10-29：新增研究落地产品入口
- 在双语首页社交按钮组下方新增 Research → Apps / 研究落地入口，分别链接 products_en.html、products.html；同步 JSON 和模板。
- 新增双语产品卡片页和共享 product-assets/catalog.css，展示已有 EZVideoRepair 图标、应用截图、本地推理简介与源码/模型包状态；整张卡片链接用户指定的 ezvideorepair.html。保留现有产品双语页面不变。
- 页面入口沿用原有视觉风格，产品目录提供语言切换、返回作者主页及响应式布局。

### 2026-10-29：通过 JSON 生成双语页面
- 运行 scripts/maintain.py build，双语结构及 HTML 检查通过，更新 index.html 与 index_zh.html；工作经历 6 项、教育 2 项。具体修改见 content/en.json 和 content/zh.json 的 Git 差异。
- 验证：双语生成与 12 项回归测试通过，四页本地链接与资源检查通过；浏览器截图确认双语首页入口及产品卡片显示，实际点击英文首页入口和卡片成功打开 ezvideorepair.html。尚未提交或推送。

### 2026-10-29：整理项目目录结构
- 根目录保留六个公开 HTML、favicon、og-cover.png、robots.txt、sitemap.xml 和 MEMORY.md，公开页面 URL 不变。
- 首页 JSON 和模板分别归入 content/profile/、templates/profile/；产品模板归入 templates/ezvideorepair/page.html；产品静态资源从 product-assets/ 统一迁至 assets/products/。
- MAINTENANCE.md 移至 docs/maintenance.md，新增 docs/structure.md 作为目录与维护入口说明；更新生成脚本、测试、模板、JSON 和页面资源引用。历史实施计划保留原记录。

### 2026-10-29：通过 JSON 生成双语页面
- 运行 scripts/maintain.py build，双语结构及 HTML 检查通过，更新 index.html 与 index_zh.html；工作经历 6 项、教育 2 项。具体修改见 content/profile/en.json 和 content/profile/zh.json 的 Git 差异。
- 验证：双语首页和产品生成成功、12 项回归测试通过；六个公开页面与整理前相比仅资源路径变化，所有本地链接与资源存在。尚未提交或推送。

### 2026-10-29：提交产品入口与目录整理
- 用户授权提交并推送当前产品入口、双语产品目录及 EZVideoRepair 页面、资源与生成维护工具，并包含目录整理和说明。
- 提交前首页内容检查、12 项回归测试及 git diff --check 通过；推送结果以 Git 回执为准。

### 2026-10-29：EZVideoRepair 产品卡片标为未上线
- 按用户要求，将双语产品目录中的 EZVideoRepair 卡片改为灰色静态 article，移除链接及跳转箭头，不参与键盘链接导航，并添加尚未上线 / Coming soon 状态。
- 移除目录中暗示已上线的可获取文案，改为准备中；保留产品介绍页原文件。
- 验证：双语卡片均无产品链接、href 或 tabindex，12 项回归测试与 git diff --check 通过。尚未提交或推送。

### 2026-10-29：移除首页研究落地按钮
- 按用户要求，从中英文首页移除 Research → Apps / 研究落地入口，删除对应 hero JSON 链接、模板标记及专用样式；保留独立产品目录与介绍页。

### 2026-10-29：通过 JSON 生成双语页面
- 运行 scripts/maintain.py build，双语结构及 HTML 检查通过，更新 index.html 与 index_zh.html；工作经历 6 项、教育 2 项。具体修改见 content/profile/en.json 和 content/profile/zh.json 的 Git 差异。
- 验证：双语生成检查及 12 项测试通过；确认两版入口和专用样式已移除，原社交按钮保留。尚未提交或推送。

### 2026-10-29：提交双语隐私政策页面
- 用户要求推送当前改动，包含新增 ezvideorepair-privacy.html、ezvideorepair-privacy_en.html 及产品页页脚隐私链接；保留现有政策正文。
- 同步产品 JSON 和共享模板中的隐私链接，防止下次生成丢失；提交前执行生成、回归测试和差异检查。
