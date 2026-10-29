# JSON 页面维护实施计划

目标：将现有双语静态个人页面转换为模板 + 可维护 JSON，使用 Python 标准库双向导出和生成，保持当前页面无损。

- [x] 实现 HTML 内容提取，保存双语 JSON 和静态模板，经历、教育及折叠列表可增删条目。
- [x] 实现双语 ID/结构验证、自动计数、生成预览及写入命令。
- [x] 验证初始导出/生成无损、内容修改生效、增删列表计数、错误输入不改页面。
- [x] 编写中文操作说明并同步 MEMORY.md。

文件：scripts/maintain.py（CLI），content/en.json / zh.json（内容），templates/*.html（样式和结构），tests/test_maintain.py（回归检查），MAINTENANCE.md（用法）。
