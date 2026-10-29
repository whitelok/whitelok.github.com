# 使用 JSON 维护双语个人页面

需要 Python 3.9 或以上，不需要安装第三方依赖。在项目根目录运行下面的命令（脚本也支持从其他目录运行）。

## 日常修改

1. 编辑 `content/profile/en.json`（英文）与 `content/profile/zh.json`（中文）。
2. 运行检查：

   ```bash
   python3 scripts/maintain.py check
   ```

3. 生成两个页面：

   ```bash
   python3 scripts/maintain.py build
   ```

`build` 同时更新 `index.html`、`index_zh.html`，并向 `MEMORY.md` 追加生成记录。脚本不会自动提交或推送 Git。

生成前会先检查、渲染两种语言。JSON 格式错误、条目 ID 不对应、缺字段、HTML 标签未闭合等错误都会阻止写入页面。`check` 不修改文件。

## JSON 内容结构

| 字段 | 内容 |
| --- | --- |
| `language` / `schema_version` | 固定为 `en` 或 `zh` / `1` |
| `title` | 页面标题；生成时同步到 Open Graph、Twitter 和 ProfilePage JSON-LD |
| `meta.description` | 页面描述；生成时同步到社交分享描述和 ProfilePage JSON-LD |
| `meta` 其他字段 | 视口、社交图片、locale 等现有元数据，保持已有字段名 |
| `structured_data` | 原有 JSON-LD 对象，可维护 Person 等信息 |
| `nav` | 左上标识、语言切换标签 |
| `hero.heading_html` / `hero.role_html` | 姓名与头衔，可保留现有加粗/样式标签 |
| `hero.links` | 三个社交按钮的 `label`、`url`；SVG 图标留在模板中 |
| `experience_label` / `education_label` | 工作、教育区块标题 |
| `experience` | 工作经历数组，按显示顺序排列 |
| `education` | 教育经历数组，按显示顺序排列 |
| `footer` | 页脚版权和联系链接 |

工作经历包含 `heading_html`、`time_html`、`subtitle_html`、`bullets`、`groups`、`tags_html`。教育包含 `school_html`、`degree_html`、`year_html`、`groups`。

`groups` 是论文、奖项、媒体报道等折叠组，每个组包含 `id`、`summary_html`、`items`。`bullets` 和 `items` 中每条记录包含 `id` 与 `html`。

- 后缀为 `_html` 的字段以及条目的 `html` 支持现有的 `<b>`、`<i>`、`<a>`、`<span class="badge">` 等富文本，请保留成对标签。
- `title`、链接的 `label` / `url` 和 meta 字段填写普通文本，脚本会执行 HTML 转义。
- JSON 字符串里的双引号需要写作 `\"`，不能使用注释或尾随逗号。
- 不要在 JSON 中维护 CSS、Google Analytics、SVG 图标或动画代码；这些位于 `templates/profile/en.html`、`templates/profile/zh.html`。
- JSON 是本地可信维护文件，富文本不会被清洗，不能作为公开接口接收陌生人输入。

## 新增论文示例

小红书位于 `experience[0]`，其论文组目前是 `groups[0]`。在两份 JSON 的该组 `items` 中，在相同位置添加同一个 ID：

```json
{
  "id": "paper-arxiv-2610-14709",
  "html": "<a href=\"https://arxiv.org/abs/2610.14709\" target=\"_blank\" rel=\"noopener\">Vela: User Behavior as Supervision Sparks LLM Intelligence</a><span class=\"src\">arXiv 2610.14709</span>"
}
```

这是格式示例，Vela 已经在当前数据中，请勿重复添加。

论文标题通常在两版保持英文；需要翻译的奖项、工作内容由用户分别填写。组标题内的 `{{count}}` 会根据 `items` 数量自动替换，不用手动修改论文篇数。`SCI ×1 / EI ×4` 等额外说明不是自动推断值，需自行维护。

新增专利时在对应经历的 `bullets` 中添加记录即可，无需新建折叠组。

## 中英文一致性

两份 JSON 的工作经历、教育、折叠组、条目、bullet 和固定链接必须使用相同 ID、相同顺序。ID 在同级列表中不得重复。已有 ID 是初次导出的稳定标识，修改文字时不需要改 ID；新增时可以使用 `paper-xxx`、`patent-xxx` 等有意义的 ID。

脚本可检查结构和对应关系，**不会自动翻译或判断两段自然语言含义是否一致**。例如英文头衔与中文头衔、英文校名不带中文后缀等已确认差异可以继续保留。只改某版文字不会被拦截；增删条目则需要两版同步。

新增/删除工作经历或教育卡片时，复制一个同类对象并修改 ID、内容及内部条目；两版必须一起更新。新增或删除社交图标按钮、页脚链接，或新增 meta 字段，需要同时调整模板里的对应占位符；脚本会拒绝不匹配的固定链接或 meta 字段。

## 预览与其他 JSON 输入

```bash
python3 scripts/maintain.py build --output-dir /tmp/resume-preview
python3 scripts/maintain.py build --content-dir /path/to/my-json --output-dir /tmp/resume-preview
```

输入目录须包含 `en.json` 与 `zh.json`。预览仅输出两个 HTML；当前 favicon 和分享图片使用站点根路径，完整图片效果需将 HTML 与根目录资源一起放到本地 HTTP 服务或站点上查看。预览不会改写根目录页面或 MEMORY.md。

## 从 HTML 重新导出

初始导出已经完成。日常请编辑 JSON；直接编辑 HTML 后再运行 `build` 会被 JSON 覆盖。

如果确实修改了 HTML 并希望将它重新作为内容来源，请先备份 JSON 与模板，然后运行：

```bash
python3 scripts/maintain.py export --force
python3 scripts/maintain.py check
```

`export` 从两版 HTML 同时提取内容与模板，`--force` 明确允许覆盖旧 JSON 和模板。未给 `--force` 时遇到现有文件会拒绝覆盖。导出不会自动更新浏览器页面或运行 Git。

模板中的 canonical、hreflang、语言属性和结构要按语言分别维护；布局修改同时更新两份模板。模板使用 `{{字段名}}` 占位符，不依赖 Jinja2。

## 回归检查

```bash
python3 -m unittest discover -s tests -v
```

测试覆盖页面内容/结构/样式/脚本往返一致、双语新增论文计数、字段更新、结构错位/重复 ID 拦截、无效 HTML 不写入页面、预览无副作用及导出覆盖保护。
