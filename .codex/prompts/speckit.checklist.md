---
description: 根据用户需求为当前功能生成定制化检查清单。
---

## Checklist Purpose: "Unit Tests for English"

**关键概念**：检查清单是**需求写作的单元测试**——它验证需求在特定领域下的质量、清晰度与完备性。

**不是用于验证/测试实现**：

- ❌ 不是 “验证按钮能正常点击”
- ❌ 不是 “测试错误处理是否工作”
- ❌ 不是 “确认 API 返回 200”
- ❌ 不是检查代码/实现是否符合 spec

**用于需求质量验证**：

- ✅ “是否为所有卡片类型定义了视觉层级要求？”（完备性）
- ✅ “‘突出显示’是否用具体尺寸/位置量化？”（清晰度）
- ✅ “所有交互元素的悬停态要求是否一致？”（一致性）
- ✅ “键盘导航的可访问性要求是否定义？”（覆盖性）
- ✅ “spec 是否定义了 logo 图片加载失败时的行为？”（边界情况）

**比喻**：如果你的 spec 是用英文写的代码，检查清单就是它的单测套件。你在测试需求写得是否好、是否完备且明确，而不是实现是否工作。

## User Input

```text
$ARGUMENTS
```

在继续之前（如果非空）你**必须**先考虑用户输入。

## Execution Steps

1. **准备**：在仓库根目录运行 `.specify/scripts/bash/check-prerequisites.sh --json`，解析 FEATURE_DIR 与 AVAILABLE_DOCS 列表。
   - 所有路径必须是绝对路径。
   - 对含单引号的参数（如 "I'm Groot"），使用转义：'I'\''m Groot'（或尽量使用双引号："I'm Groot"）。

2. **动态澄清意图**：生成最多三条初始澄清问题（无预置题库）。必须：
   - 基于用户表述 + spec/plan/tasks 中提取的信号生成
   - 只问会实质影响检查清单内容的信息
   - 若 `$ARGUMENTS` 已明确，则跳过对应问题
   - 精准优先于覆盖面

   生成算法：
   1. 提取信号：领域关键词（如 auth、latency、UX、API），风险词（“critical”“must”“compliance”），干系人提示（“QA”“review”“security team”），显性交付物（“a11y”“rollback”“contracts”）。
   2. 聚类为最多 4 个候选焦点并排序。
   3. 推断受众与时机（作者、审阅者、QA、发布），若未说明则猜测。
   4. 检测缺失维度：范围、深度/严格度、风险侧重、排除边界、可度量验收标准。
   5. 选择问题原型：
      - 范围细化：如 “需覆盖与 X、Y 的集成触点，还是仅限本地模块正确性？”
      - 风险优先：如 “这些潜在风险领域中哪些应设为必过项？”
      - 深度校准：如 “是轻量 pre-commit 自检还是正式发布闸？”
      - 受众框定：如 “给作者自检还是 PR 同行审核用？”
      - 边界排除：如 “本轮是否明确排除性能调优项？”
      - 场景类别缺口：如 “未发现恢复流——是否纳入回滚/部分失败路径？”

   提问格式规则：
   - 若给选项，使用紧凑表：Option | Candidate | Why It Matters
   - 选项最多 A–E；若自由回答更清晰则不使用表
   - 不要求用户重复已给出的信息
   - 避免猜测类别；若不确定，直接问 “X 是否在范围内？”

   无法交互时的默认：
   - 深度：Standard
   - 受众：代码相关默认 Reviewer（PR），否则 Author
   - 焦点：排名前 2 的信号簇

   输出问题（标注 Q1/Q2/Q3）。若回答后仍有 ≥2 类场景（替代/异常/恢复/非功能域）不清晰，可再问最多两条针对性问题（Q4/Q5），各附一行理由（如 “恢复路径风险未解”）。总题数不超过 5。用户拒绝追加则停止。

3. **理解用户请求**：结合 `$ARGUMENTS` + 澄清回答：
   - 确定清单主题（如 security、review、deploy、ux）
   - 汇总用户明确要求的必含项
   - 将焦点选择映射到分类脚手架
   - 从 spec/plan/tasks 推断缺失上下文（不要臆造）

4. **加载功能上下文**：从 FEATURE_DIR 读取：
   - spec.md：功能需求与范围
   - plan.md（如有）：技术细节、依赖
   - tasks.md（如有）：实施任务

   **上下文加载策略**：
   - 仅加载与当前焦点相关的必要部分（避免全量）
   - 优先将长段落概括为简明场景/需求要点
   - 渐进披露：按需追加读取

5. **生成检查清单内容**：

   **优先级与相关性**：
   - 以用户请求的主题 + 风险信号为主线
   - 每条检查项都要针对“需求写得好不好”，不是“实现好不好”

   **聚焦需求质量，而非实现**：
   - 不要包含验证行为/渲染/点击/执行的语句
   - 不要包含测试用例或 QA 步骤
   - 用 “是否有…要求/定义/说明” 的问句形态

   **必备维度**（可根据主题选取）：
   - 完备性、清晰度、一致性、覆盖、可测性/可度量、依赖/假设、场景分类（主/替代/异常/恢复/非功能）

   **示例（保持需求视角，非实现）**：
   - “是否为播单卡片定义视觉层级及可量化标准？[Clarity]”
   - “是否为悬停/聚焦/禁用等交互态提供一致要求？[Consistency]”
   - “是否定义零数据态与加载失败态的表现？[Edge Case/GAP]”
   - “性能目标是否有具体阈值？[Measurability]”

   **关注边界与缺漏**：
   - “是否定义图片加载失败时的降级行为？[Edge Case]”
   - “是否定义异步剧集数据的加载态？[Completeness]”
   - “是否定义竞争 UI 元素的视觉层级？[Clarity]”

   **条目结构要求**：
   每项遵循：
   - 用问题句检查需求质量
   - 聚焦 spec/plan 是否写明（或缺失）
   - 带质量维度标签 [Completeness/Clarity/Consistency/…]
   - 引用 spec 章节 `[Spec §X.Y]`；若缺失用 `[Gap]`

   **按质量维度示例**：

   完备性：
   - “是否为所有 API 失败模式定义错误响应要求？[Gap]”
   - “是否为所有交互元素定义了可访问性要求？[Completeness]”
   - “是否定义了响应式的移动断点？[Gap]”

   清晰度：
   - “‘fast loading’ 是否有明确时间阈值？[Clarity, Spec §NFR-2]”
   - “‘related episodes’ 的选取标准是否写明？[Clarity, Spec §FR-5]”
   - “‘prominent’ 是否用可测的视觉属性定义？[Ambiguity, Spec §FR-4]”

   一致性：
   - “导航要求是否在各页面一致？[Consistency, Spec §FR-10]”
   - “卡片组件要求在落地页与详情页是否一致？[Consistency]”

   覆盖：
   - “是否定义了零态（无剧集）场景需求？[Coverage, Edge Case]”
   - “是否覆盖并发交互场景？[Coverage, Gap]”
   - “是否定义部分加载失败时的需求？[Coverage, Exception Flow]”

   可度量：
   - “视觉层级要求是否可测/可验证？[Acceptance Criteria, Spec §FR-1]”
   - “‘balanced visual weight’ 能否客观验证？[Measurability, Spec §FR-2]”

   **场景分类与覆盖**（需求质量视角）：
   - 检查是否存在：主路径、替代、异常/错误、恢复、非功能场景的需求
   - 对缺失场景问： “该场景需求是有意排除还是缺失？[Gap]”
   - 有状态变更时加入韧性/回滚：如 “迁移失败是否定义回滚要求？[Gap]”

   **可追溯性要求**：
   - 最低要求：≥80% 条目需含追溯引用
   - 每项引用 spec 章节 `[Spec §X.Y]`，或使用标记 `[Gap]`/`[Ambiguity]`/`[Conflict]`/`[Assumption]`
   - 若无 ID 体系：提问 “是否已建立需求与验收标准的编号体系？[Traceability]”

   **揭示并解决问题**（需求质量问题）：
   - 含糊： “fast 是否量化？[Ambiguity, Spec §NFR-1]”
   - 冲突： “§FR-10 与 §FR-10a 的导航要求是否冲突？[Conflict]”
   - 假设： “‘播客 API 总可用’ 的假设是否已验证？[Assumption]”
   - 依赖： “是否记录外部播客 API 的需求？[Dependency, Gap]”
   - 缺少定义： “‘visual hierarchy’ 是否有可测定义？[Gap]”

   **内容收敛**：
   - 软上限：原始候选 >40 时按风险/影响优先
   - 合并近似重复项
   - 低影响边界情况 >5 条时可合并为一项：如 “边界情况 X/Y/Z 是否已覆盖？[Coverage]”

   **🚫 严禁**（会变成实现测试）：
   - ❌ 以 “Verify/Test/Confirm/Check + 行为” 开头
   - ❌ 涉及代码执行、用户动作、系统行为
   - ❌ “显示正确”“工作正常”“符合预期”
   - ❌ “点击/导航/渲染/加载/执行” 等实现行为
   - ❌ 测试用例、测试计划、QA 流程
   - ❌ 具体实现细节（框架、API、算法）

   **✅ 必须遵守的模式**（测试需求质量）：
   - ✅ “是否为[场景]定义/记录了[需求类型]？”
   - ✅ “‘模糊词’是否量化/澄清？”
   - ✅ “A 与 B 章节的[需求]是否一致？”
   - ✅ “[需求]能否客观测量/验证？”
   - ✅ “是否覆盖了[边界情况/场景]的需求？”
   - ✅ “spec 是否定义了[缺失要素]？”

6. **结构引用**：按 `.specify/templates/checklist-template.md` 的模板生成检查清单标题、元信息、分类标题与 ID 规则。若模板缺失，则使用：H1 标题、用途/创建信息行、`##` 分类，分类下用 `- [ ] CHK### <检查项>`，全局递增 ID 从 CHK001 开始。

7. **报告**：输出新建检查清单的完整路径、条目数，并提醒每次运行会生成新文件。摘要包含：
   - 选择的焦点领域
   - 深度级别
   - 使用者/时机
   - 纳入的用户显式必含项

**重要**：每次 `/speckit.checklist` 调用会创建一个使用简短描述名的检查清单（若文件不存在）。

- 允许生成多种类型（如 `ux.md`、`test.md`、`security.md`）
- 使用含义明确、易记的文件名，便于在 `checklists/` 中识别
- 清理无用清单以避免杂乱

## Example Checklist Types & Sample Items

**UX Requirements Quality：** `ux.md`

示例（检验需求而非实现）：

- “是否用可量化标准定义视觉层级？[Clarity, Spec §FR-1]”
- “是否明确 UI 元素数量与位置？[Completeness, Spec §FR-1]”
- “交互态（hover/focus/active）要求是否一致？[Consistency]”
- “是否为所有交互元素定义可访问性要求？[Coverage, Gap]”
- “图片失败时的降级行为是否定义？[Edge Case, Gap]”
- “‘prominent display’ 能否客观测量？[Measurability, Spec §FR-4]”

**API Requirements Quality：** `api.md`

示例：

- “是否为所有失败场景定义错误响应格式？[Completeness]”
- “限流要求是否有具体阈值？[Clarity]”
- “认证要求在各端点间是否一致？[Consistency]”
- “外部依赖的重试/超时要求是否定义？[Coverage, Gap]”
- “版本策略是否记录在需求中？[Gap]”

**Performance Requirements Quality：** `performance.md`

示例：

- “性能要求是否有具体指标？[Clarity]”
- “关键路径的性能目标是否定义？[Coverage]”
- “不同负载条件下的性能要求是否写明？[Completeness]”
- “性能要求能否客观测量？[Measurability]”
- “高负载降级要求是否定义？[Edge Case, Gap]”

**Security Requirements Quality：** `security.md`

示例：

- “是否为所有受保护资源定义认证要求？[Coverage]”
- “敏感信息的数据保护要求是否写明？[Completeness]”
- “威胁模型是否记录且需求与之对齐？[Traceability]”
- “安全需求是否符合合规义务？[Consistency]”
- “安全故障/泄露响应要求是否定义？[Gap, Exception Flow]”

## Anti-Examples: What NOT To Do

**❌ 错误示例——这些在测试实现，而非需求：**

```markdown
- [ ] CHK001 - Verify landing page displays 3 episode cards [Spec §FR-001]
- [ ] CHK002 - Test hover states work correctly on desktop [Spec §FR-003]
- [ ] CHK003 - Confirm logo click navigates to home page [Spec §FR-010]
- [ ] CHK004 - Check that related episodes section shows 3-5 items [Spec §FR-005]
```

**✅ 正确示例——这些在测试需求质量：**

```markdown
- [ ] CHK001 - 是否明确规定精选剧集数量与布局？[Completeness, Spec §FR-001]
- [ ] CHK002 - 所有交互元素的悬停态要求是否一致？[Consistency, Spec §FR-003]
- [ ] CHK003 - 品牌可点击元素的导航要求是否清晰？[Clarity, Spec §FR-010]
- [ ] CHK004 - 相关剧集的选取标准是否已记录？[Gap, Spec §FR-005]
- [ ] CHK005 - 异步剧集数据是否定义加载态需求？[Gap]
- [ ] CHK006 - “视觉层级” 需求能否客观验证？[Measurability, Spec §FR-001]
```

**关键差异：**

- 错误：测试系统是否工作
- 正确：测试需求是否写得好
- 错误：验证行为
- 正确：校验需求质量
- 错误： “是否做 X？”
- 正确： “X 是否被清晰写在需求里？”
