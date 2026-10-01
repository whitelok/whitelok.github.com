# Vibe Coding Memory — Karl Luo 个人介绍页

> 用途：供后续 vibe coding 会话复用。包含任务背景、技术经验、设计规范、用户偏好、内容数据源。
> 产物：`index.html`（英文版）+ `index_zh.html`（中文版，内容一致全翻译）+ `avatar.png`（LinkedIn 头像抠图，当前版本已从页面移除但文件保留）。语言切换为导航栏右上角小胶囊按钮 `.lang-switch`（中文 ⇄ English，12px，勿放回 hero）。
> 最后更新：2026-10-01（双语版）

## ⚠️ 第一规则（用户明确要求）

**任何内容/样式修改，必须同步更新英文版（index.html）和中文版（index_zh.html）两个文件，保持结构、样式、信息完全一致（仅语言不同）。修改后两版都要截图验证。**
例外：用户明确指定只改某一版时（如中文版头衔"模型工程负责人"仅改 zh 版），按指令执行并在本文件记录差异。

### 两版已知差异
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
nav（毛玻璃，KL logo + Experience/Education/Contact）
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
  - bullets：Lead ML Infra（Search/Ads/Rec，leader+核心贡献者）；创立 AI Infra（AIGC/LLM/VLM，业界首个训推一体框架）；LLM serving → AI搜索+点点 300M MAU；AIGC 推理优化 GPU/NPU/PPU/XPU；Awards: 🏆 2025 Impact Challenge — Business Breakthrough Award, Annual Champion
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
