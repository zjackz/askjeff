---
description: 使用计划模板生成设计产物，执行实施规划流程。
handoffs: 
  - label: Create Tasks
    agent: speckit.tasks
    prompt: Break the plan into tasks
    send: true
  - label: Create Checklist
    agent: speckit.checklist
    prompt: Create a checklist for the following domain...
---

## User Input

```text
$ARGUMENTS
```

在继续之前（如果非空）你**必须**先考虑用户输入。

## Outline

1. **准备**：在仓库根目录运行 `.specify/scripts/bash/setup-plan.sh --json`，解析 FEATURE_SPEC、IMPL_PLAN、SPECS_DIR、BRANCH。对含单引号的参数（如 "I'm Groot"），使用转义：'I'\''m Groot'（或尽量使用双引号："I'm Groot"）。

2. **加载上下文**：读取 FEATURE_SPEC 与 `.specify/memory/constitution.md`。加载已复制的 IMPL_PLAN 模板。

3. **执行规划流程**：遵循 IMPL_PLAN 模板结构：
   - 填写 Technical Context（未知项标记 “NEEDS CLARIFICATION”）
   - 将宪章检查部分填入 constitution 内容
   - 评估闸口（若违反且无正当理由则 ERROR）
   - Phase 0：生成 research.md（解决所有 NEEDS CLARIFICATION）
   - Phase 1：生成 data-model.md、contracts/、quickstart.md
   - Phase 1：运行代理脚本更新 agent 上下文
   - 设计后重新评估宪章检查

4. **停止并报告**：命令在 Phase 2 规划结束后终止。报告分支、IMPL_PLAN 路径与已生成的产物。

## Phases

### Phase 0: Outline & Research

1. **从 Technical Context 提取未知项**：
   - 每个 NEEDS CLARIFICATION → 研究任务
   - 每个依赖 → 最佳实践任务
   - 每个集成 → 模式任务

2. **生成并分发研究代理任务**：

   ```text
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **整合发现** 写入 `research.md`，格式：
   - Decision: [选择]
   - Rationale: [缘由]
   - Alternatives considered: [评估过的替代]

**输出**：完成所有 NEEDS CLARIFICATION 的 research.md

### Phase 1: Design & Contracts

**前置条件：** `research.md` 完成

1. **从 feature spec 提取实体** → `data-model.md`：
   - 实体名、字段、关系
   - 来自需求的校验规则
   - 如适用，状态转换

2. **从功能需求生成 API 契约**：
   - 每个用户动作 → 一个端点
   - 使用标准 REST/GraphQL 模式
   - 输出 OpenAPI/GraphQL schema 至 `/contracts/`

3. **Agent 上下文更新**：
   - 运行 `.specify/scripts/bash/update-agent-context.sh codex`
   - 这些脚本会检测正在使用的 AI 代理
   - 更新对应的代理上下文文件
   - 仅新增当前计划中的新技术
   - 保留标记之间的人工补充

**输出**：data-model.md、/contracts/*、quickstart.md、代理特定文件

## Key rules

- 使用绝对路径
- 遇到闸口失败或澄清未解需直接 ERROR
