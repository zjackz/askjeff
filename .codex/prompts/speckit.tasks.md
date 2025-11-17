---
description: 基于可用设计文档，为功能生成可执行、按依赖排序的 tasks.md。
handoffs: 
  - label: Analyze For Consistency
    agent: speckit.analyze
    prompt: Run a project analysis for consistency
    send: true
  - label: Implement Project
    agent: speckit.implement
    prompt: Start the implementation in phases
    send: true
---

## User Input

```text
$ARGUMENTS
```

在继续之前（如果非空）你**必须**先考虑用户输入。

## Outline

1. **准备**：在仓库根目录运行 `.specify/scripts/bash/check-prerequisites.sh --json`，解析 FEATURE_DIR 与 AVAILABLE_DOCS 列表。所有路径必须绝对化。对含单引号的参数（如 "I'm Groot"），使用转义：'I'\''m Groot'（或尽量使用双引号："I'm Groot"）。

2. **加载设计文档**：从 FEATURE_DIR 读取：
   - **必需**：plan.md（技术栈、库、结构）、spec.md（含优先级的用户故事）
   - **可选**：data-model.md（实体）、contracts/（API 端点）、research.md（决策）、quickstart.md（测试场景）
   - 注意：并非所有项目都有全部文档；需基于可用信息生成任务。

3. **执行任务生成流程**：
   - 读取 plan.md，提取技术栈、库、项目结构
   - 读取 spec.md，提取用户故事与优先级（P1、P2、P3…）
   - 若存在 data-model.md：提取实体并映射到用户故事
   - 若存在 contracts/：将端点映射到用户故事
   - 若存在 research.md：提取决策生成设置类任务
   - 生成按用户故事组织的任务（见任务生成规则）
   - 生成用户故事完成顺序的依赖图
   - 为每个故事给出并行执行示例
   - 校验任务完备性（每个故事要自测可行）

4. **生成 tasks.md**：使用 `.specify.specify/templates/tasks-template.md` 结构，填入：
   - 来自 plan.md 的正确功能名
   - Phase 1：Setup 任务（项目初始化）
   - Phase 2：基础任务（所有用户故事的阻塞前置）
   - Phase 3+：每个用户故事一阶段（按 spec.md 优先级）
   - 每阶段包含：故事目标、独立测试标准、测试（如被要求）、实现任务
   - 最终阶段：Polish & 交叉关注点
   - 所有任务必须遵循严格检查清单格式（见规则）
   - 清晰写明每个任务的文件路径
   - Dependencies 段展示故事完成顺序
   - 每个故事给出并行执行示例
   - Implementation strategy 段说明 MVP 优先、增量交付

5. **报告**：输出生成的 tasks.md 路径与摘要：
   - 总任务数
   - 每个用户故事的任务数
   - 识别的并行机会
   - 各故事的独立测试标准
   - 建议的 MVP 范围（通常仅用户故事 1）
   - 格式校验：确认所有任务符合检查清单格式（复选框、ID、标签、文件路径）

任务生成上下文：$ARGUMENTS

tasks.md 应可立即执行——每个任务都应足够具体，使 LLM 无需额外上下文即可完成。

## Task Generation Rules

**关键**：任务必须按用户故事组织，以便独立实施与测试。

**测试可选**：仅当规格显式要求或用户指定 TDD 时生成测试任务。

### 检查清单格式（必需）

每个任务必须严格采用：

```text
- [ ] [TaskID] [P?] [Story?] Description with file path
```

**格式要素**：

1. **复选框**：始终以 `- [ ]` 开头
2. **任务 ID**：按执行顺序递增（T001、T002、T003…）
3. **[P] 标记**：仅在可并行（不同文件、无未完成依赖）时加入
4. **[Story] 标签**：仅用户故事阶段必填
   - 形式：[US1]、[US2]…（映射 spec.md 的故事）
   - Setup 阶段：无故事标签
   - Foundational 阶段：无故事标签
   - 用户故事阶段：必须有故事标签
   - Polish 阶段：无故事标签
5. **描述**：明确动作并给出精确文件路径

**示例**：

- ✅ `- [ ] T001 Create project structure per implementation plan`
- ✅ `- [ ] T005 [P] Implement authentication middleware in src/middleware/auth.py`
- ✅ `- [ ] T012 [P] [US1] Create User model in src/models/user.py`
- ✅ `- [ ] T014 [US1] Implement UserService in src/services/user_service.py`
- ❌ `- [ ] Create User model`（缺 ID 与故事标签）
- ❌ `T001 [US1] Create model`（缺复选框）
- ❌ `- [ ] [US1] Create User model`（缺任务 ID）
- ❌ `- [ ] T001 [US1] Create model`（缺文件路径）

### 任务组织

1. **来自用户故事（spec.md）——主组织方式**：
   - 每个用户故事（P1、P2、P3…）为一阶段
   - 将相关组件映射到该故事：
     - 该故事所需模型
     - 该故事所需服务
     - 该故事的端点/UI
     - 若需测试：该故事的专属测试任务
   - 标注故事间依赖（多数故事应独立）

2. **来自契约**：
   - 每个契约/端点 → 服务的用户故事
   - 若需测试：在故事阶段中为每个契约先生成契约测试任务 [P]

3. **来自数据模型**：
   - 每个实体映射到需要它的故事
   - 若实体支持多个故事：放在最早的故事或 Setup 阶段
   - 关系 → 在适当的故事阶段生成服务层任务

4. **来自设置/基础设施**：
   - 共享基础设施 → Setup 阶段
   - 阻塞前置 → Foundational 阶段
   - 故事特定的设置 → 放在对应故事阶段

### 阶段结构

- **Phase 1**：Setup（项目初始化）
- **Phase 2**：Foundational（阻塞前置——必须完成后再做故事）
- **Phase 3+**：按优先级的用户故事
  - 在故事内：若有测试 → 模型 → 服务 → 端点 → 集成
  - 每阶段应是可独立测试的增量
- **最终阶段**：Polish & Cross-Cutting Concerns
