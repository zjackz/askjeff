---
description: 基于交互或已给的原则输入创建/更新项目宪章，并确保相关模板保持同步。
handoffs: 
  - label: Build Specification
    agent: speckit.specify
    prompt: Implement the feature specification based on the updated constitution. I want to build...
---

## User Input

```text
$ARGUMENTS
```

在继续之前（如果非空）你**必须**先考虑用户输入。

## Outline

你正在更新 `.specify/memory/constitution.md`。该文件是包含方括号占位符（如 `[PROJECT_NAME]`、`[PRINCIPLE_1_NAME]`）的模板。你的工作是：(a) 收集/推导具体值，(b) 精确填充模板，(c) 将改动同步到依赖的文档。

执行流程：

1. 加载 `.specify/memory/constitution.md` 模板。
   - 识别形如 `[ALL_CAPS_IDENTIFIER]` 的全部占位符。
   **重要**：用户可能需要的原则数量与模板不同，如有数字要求需遵循，按通用模板更新。

2. 收集/推导占位符的值：
   - 若用户输入中提供则直接使用。
   - 否则从仓库上下文（README、文档、若内嵌的旧版宪章等）推断。
   - 治理日期：`RATIFICATION_DATE` 为最初通过日（不明则询问或标记 TODO）；若有改动，`LAST_AMENDED_DATE` 设为今日，否则保持原值。
   - `CONSTITUTION_VERSION` 按语义化版本递增：
     - MAJOR：不兼容的治理/原则删除或重定义。
     - MINOR：新增原则/章节或显著扩展指导。
     - PATCH：澄清、措辞、错别字、非语义性优化。
   - 若版本位难以判断，先给出理由再定稿。

3. 起草更新后的宪章内容：
   - 替换全部占位符（不保留方括号 token，除非项目有意留空且需说明）。
   - 保留标题层级，替换后可移除多余注释，除非仍有解释价值。
   - 确保每个 Principle 段：简练名称、段落（或列表）描述不可协商规则，必要时给出理由。
   - 确保 Governance 段包含修订流程、版本策略、合规审查期望。

4. 一致性同步检查（把先前清单转为实际校验）：
   - 阅读 `.specify/templates/plan-template.md`，确保其中 “Constitution Check” 或规则与更新后的原则一致。
   - 阅读 `.specify/templates/spec-template.md`，若宪章新增/删除强制章节或约束，需对齐。
   - 阅读 `.specify/templates/tasks-template.md`，确保任务分类体现新增/删除的原则驱动项（如可观测性、版本化、测试纪律）。
   - 阅读 `.specify/templates/commands/*.md`（包含本文），检查是否有过时引用（如特定代理名 CLAUDE 等），在需要通用化时更新。
   - 阅读运行期指引文档（如 `README.md`、`docs/quickstart.md` 或特定代理指引），更新与变更原则相关的引用。

5. 生成同步影响报告（以 HTML 注释形式置于宪章文件顶部，更新后）：
   - 版本变化：旧 → 新
   - 修改的原则列表（旧标题 → 新标题，若有重命名）
   - 新增章节
   - 删除章节
   - 需要更新的模板（✅ 已更新 / ⚠ 待处理）及路径
   - 如有有意保留的占位符，列出后续 TODO

6. 输出前校验：
   - 无未解释的方括号 token。
   - 版本号与报告一致。
   - 日期使用 YYYY-MM-DD。
   - 原则需具可执行性、可验证性，避免模糊（必要时用 MUST/SHOULD 并给出理由）。

7. 将完成的宪章写回 `.specify/memory/constitution.md`（覆盖）。

8. 最终向用户汇总：
   - 新版本号与递增理由。
   - 需人工跟进的文件。
   - 提议的提交信息（如 `docs: amend constitution to vX.Y.Z (principle additions + governance update)`）。

格式与风格要求：

- 使用模板中的 Markdown 标题，不升降级。
- 长行可适度换行以便阅读（建议 <100 字符），避免生硬折行。
- 各章节间保留单空行。
- 避免行尾空格。

若用户只给部分更新（如仅改一条原则），仍需执行校验与版本决策步骤。

若关键信息缺失（如确实不知道批准日期），插入 `TODO(<FIELD_NAME>): explanation`，并在同步影响报告的 deferred 项中说明。

不要创建新模板；始终操作现有 `.specify/memory/constitution.md` 文件。
