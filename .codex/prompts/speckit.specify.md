---
description: 基于自然语言功能描述创建或更新功能规格。
handoffs: 
  - label: Build Technical Plan
    agent: speckit.plan
    prompt: Create a plan for the spec. I am building with...
  - label: Clarify Spec Requirements
    agent: speckit.clarify
    prompt: Clarify specification requirements
    send: true
---

## User Input

```text
$ARGUMENTS
```

在继续之前（如果非空）你**必须**先考虑用户输入。

## Outline

触发消息中 `/speckit.specify` 之后的文字**就是**功能描述。假设即便 `$ARGUMENTS` 字面出现，你也已在对话中获得该描述。仅当用户为空输入时再询问。

据此执行：

1. **生成精简短名**（2–4 词）用于分支：
   - 分析描述提取最有意义的关键词
   - 生成 2–4 词短名，抓住特性要义
   - 优先动词-名词格式（如 “add-user-auth”“fix-payment-bug”）
   - 保留技术术语与缩写（OAuth2、API、JWT 等）
   - 简洁且可一眼看懂
   - 示例：
     - “I want to add user authentication” → “user-auth”
     - “Implement OAuth2 integration for the API” → “oauth2-api-integration”
     - “Create a dashboard for analytics” → “analytics-dashboard”
     - “Fix payment processing timeout bug” → “fix-payment-timeout”

2. **创建新分支前先检查是否已存在**：
   
   a. 先拉取远端分支保持最新：
      ```bash
      git fetch --all --prune
      ```
   
   b. 在全部来源中查找该短名的最高编号：
      - 远端分支：`git ls-remote --heads origin | grep -E 'refs/heads/[0-9]+-<short-name>$'`
      - 本地分支：`git branch | grep -E '^[* ]*[0-9]+-<short-name>$'`
      - Specs 目录：匹配 `specs/[0-9]+-<short-name>`
   
   c. 确定下一个可用编号：
      - 从三处提取全部数字
      - 找出最大值 N
      - 新编号为 N+1
   
   d. 运行脚本 `.specify/scripts/bash/create-new-feature.sh --json "$ARGUMENTS"`，携带计算出的编号与短名：
      - 传 `--number N+1` 与 `--short-name "your-short-name"`，附功能描述
      - Bash 示例：`.specify/scripts/bash/create-new-feature.sh --json "$ARGUMENTS" --json --number 5 --short-name "user-auth" "Add user authentication"`
      - PowerShell 示例：`.specify/scripts/bash/create-new-feature.sh --json "$ARGUMENTS" -Json -Number 5 -ShortName "user-auth" "Add user authentication"`
   
   **重要**：
   - 必须检查三处（远端、本地、specs 目录）以找到最高编号
   - 仅匹配短名完全一致的分支/目录
   - 若未找到，则从 1 开始
   - 每个功能此脚本只能运行一次
   - JSON 会在终端输出——始终以输出为准获取所需内容
   - JSON 会包含 BRANCH_NAME 与 SPEC_FILE 路径
   - 对含单引号的参数（如 "I'm Groot"），使用转义：'I'\''m Groot'（或尽量使用双引号："I'm Groot"）

3. 加载 `.specify/templates/spec-template.md` 理解所需章节。

4. 按以下流程执行：

    1. 从输入解析用户描述
       若为空：ERROR “No feature description provided”
    2. 提取关键概念
       识别：参与者、动作、数据、约束
    3. 对不清晰处：
       - 基于上下文与行业惯例做合理假设
       - 仅在以下情况使用 [NEEDS CLARIFICATION: 具体问题]：
         - 该选择显著影响范围或体验
         - 存在多种合理解释且影响不同
         - 无合理默认值
       - **上限：最多 3 个 [NEEDS CLARIFICATION] 标记**
       - 按影响排序：范围 > 安全/隐私 > 体验 > 技术细节
    4. 填写 User Scenarios & Testing
       若无清晰用户流：ERROR “Cannot determine user scenarios”
    5. 生成 Functional Requirements
       每条需求必须可测试
       未指明细节采用合理默认（在 Assumptions 记录假设）
    6. 定义 Success Criteria
       生成可度量、与技术无关的结果
       同时包含定量（时间/性能/量级）与定性（满意度、完成率）
       每条标准须可在无实现细节下验证
    7. 确认关键实体（如涉及数据）
    8. 返回：SUCCESS（spec 已可用于规划）

5. 使用模板结构将规格写入 SPEC_FILE，替换占位为描述中提取的具体细节，保持章节顺序与标题。

6. **规格质量校验**：初稿完成后按质量标准验证：

   a. **创建规格质量检查清单**：利用模板结构在 `FEATURE_DIR/checklists/requirements.md` 生成清单，内容：

      ```markdown
      # Specification Quality Checklist: [FEATURE NAME]
      
      **Purpose**: Validate specification completeness and quality before proceeding to planning
      **Created**: [DATE]
      **Feature**: [Link to spec.md]
      
      ## Content Quality
      
      - [ ] No implementation details (languages, frameworks, APIs)
      - [ ] Focused on user value and business needs
      - [ ] Written for non-technical stakeholders
      - [ ] All mandatory sections completed
      
      ## Requirement Completeness
      
      - [ ] No [NEEDS CLARIFICATION] markers remain
      - [ ] Requirements are testable and unambiguous
      - [ ] Success criteria are measurable
      - [ ] Success criteria are technology-agnostic (no implementation details)
      - [ ] All acceptance scenarios are defined
      - [ ] Edge cases are identified
      - [ ] Scope is clearly bounded
      - [ ] Dependencies and assumptions identified
      
      ## Feature Readiness
      
      - [ ] All functional requirements have clear acceptance criteria
      - [ ] User scenarios cover primary flows
      - [ ] Feature meets measurable outcomes defined in Success Criteria
      - [ ] No implementation details leak into specification
      
      ## Notes
      
      - Items marked incomplete require spec updates before `/speckit.clarify` or `/speckit.plan`
      ```

   b. **运行验证检查**：逐项审视 spec：
      - 对每条判定通过/未通过
      - 记录发现的问题（引用相关段落）

   c. **处理验证结果**：

      - **若全部通过**：标记清单完成并进入第 6 步

      - **若存在未通过项（不含 [NEEDS CLARIFICATION]）**：
        1. 列出未通过项与具体问题
        2. 更新 spec 以修正
        3. 重跑验证直至全部通过（最多 3 轮）
        4. 若 3 轮后仍未通过，在清单备注中记录剩余问题并警告用户

      - **若仍有 [NEEDS CLARIFICATION] 标记**：
        1. 提取所有标记
        2. **数量限制**：若超过 3，仅保留影响最大的 3 条（按范围/安全/体验影响），其余作合理猜测
        3. 对需澄清项（最多 3）按此格式展示给用户：

           ```markdown
           ## Question [N]: [Topic]
           
           **Context**: [Quote relevant spec section]
           
           **What we need to know**: [Specific question from NEEDS CLARIFICATION marker]
           
           **Suggested Answers**:
           
           | Option | Answer | Implications |
           |--------|--------|--------------|
           | A      | [First suggested answer] | [What this means for the feature] |
           | B      | [Second suggested answer] | [What this means for the feature] |
           | C      | [Third suggested answer] | [What this means for the feature] |
           | Custom | Provide your own answer | [Explain how to provide custom input] |
           
           **Your choice**: _[Wait for user response]_
           ```

        4. **关键 - 表格格式**：确保 markdown 表正确渲染：
           - 使用对齐的竖线与间隔
           - 单元格需留空格：`| Content |` 而非 `|Content|`
           - 表头分隔至少 3 个短横：`|--------|`
           - 自测表格在 markdown 预览下正常
        5. 问题顺序编号（Q1、Q2、Q3，最多 3）
        6. 先呈现所有问题，再等待回答（如 “Q1: A, Q2: Custom - [details], Q3: B”）
        7. 用用户选择/自定义答案替换对应 [NEEDS CLARIFICATION]
        8. 澄清解决后重跑验证

   d. **更新清单**：每轮验证后更新清单的通过/未通过状态

7. 汇报完成：包括分支名、spec 路径、清单结果、以及是否已准备进入下一阶段（`/speckit.clarify` 或 `/speckit.plan`）。

**注意：** 脚本会创建并切换到新分支，初始化 spec 文件后再写入。

## General Guidelines

## Quick Guidelines

- 聚焦用户需要的 **WHAT** 与 **WHY**。
- 避免 **HOW**（不写技术栈、API、代码结构）。
- 面向业务干系人撰写，而非开发者。
- 不要在 spec 内内嵌任何检查清单；检查清单由独立命令生成。

### Section Requirements

- **必填章节**：每个功能都必须完成
- **可选章节**：仅在相关时包含
- 不适用的章节应删除（不要留 “N/A”）

### For AI Generation

当从用户提示生成 spec 时：

1. **做合理假设**：结合上下文、行业标准、常见模式补全空白
2. **记录假设**：在 Assumptions 中记录合理默认
3. **限制澄清**：最多 3 个 [NEEDS CLARIFICATION]，仅用于：
   - 显著影响范围/体验
   - 存在多种合理解释且影响不同
   - 缺乏合理默认
4. **澄清优先级**：scope > security/privacy > UX > 技术细节
5. **像测试人员一样思考**：任何模糊需求都应无法通过“可测试且明确”的检查项
6. **常见需澄清领域**（仅当无合理默认）：
   - 功能范围与边界（包含/排除哪些用例）
   - 用户类型与权限（存在多种冲突解释时）
   - 安全/合规要求（法律/财务相关时）

**合理默认示例**（无需追问）：

- 数据保留：遵循该领域行业惯例
- 性能目标：标准 Web/移动应用期望，除非另有说明
- 错误处理：友好提示与适当降级
- 认证方式：Web 场景采用标准会话或 OAuth2
- 集成模式：未说明则默认 RESTful API

### Success Criteria Guidelines

Success Criteria 必须：

1. **可度量**：包含具体指标（时间、百分比、数量、速率）
2. **技术无关**：不提框架、语言、数据库、工具
3. **面向用户**：描述用户/业务结果，而非系统内部
4. **可验证**：无需了解实现即可验证

**好的示例**：

- “用户能在 3 分钟内完成结账”
- “系统支持 10,000 并发用户”
- “95% 搜索在 1 秒内返回结果”
- “任务完成率提升 40%”

**不佳示例**（过于实现向）：

- “API 响应 <200ms”（太技术，可写为 “用户几乎瞬时看到结果”）
- “数据库可处理 1000 TPS”（技术细节，应转为用户视角指标）
- “React 组件渲染高效”（框架特定）
- “Redis 命中率 >80%”（技术特定）
