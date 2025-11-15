---

description: "Task list template for feature implementation"
---

description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**输入**：`/specs/[###-feature-name]/` 内的 plan/spec/research/data-model/contracts  
**前置**：plan.md、spec.md 必须完成  
**语言合规**：代码、注释、提交记录、任务描述、交付文档均需中文呈现，英文术语需附中文注解。

> 任务按用户故事分组，确保每个故事可独立交付。若存在跨故事依赖，需说明原因。

## 任务格式

`[ID] [P?] [US#] 描述（含文件路径）`

- `[P]` 表示可并行（无共享文件/依赖）
- `[US#]` 对应用户故事编号
- 每个故事至少包含：实现任务、验证任务（测试或验收清单）、可观测性/文档任务

## 阶段 1：基础环境

- [ ] T001 初始化项目/依赖
- [ ] T002 [P] 设定代码规范、CI、Secret 管理等

## 阶段 2：通用基础能力

- [ ] T010 建立数据库/Schema/迁移
- [ ] T011 [P] 构建核心服务骨架、错误处理、日志
- [ ] T012 配置权限/配置中心/Feature Flag（若适用）

## 阶段 3：User Story 1 (P1) 🎯

- **目标**： [简述]
- **独立验证**： [测试方式]

### Tests / Evidence

- [ ] T101 [P][US1] 关键测试或验收步骤

### Implementation

- [ ] T102 [US1] …
- [ ] T103 [US1] …

### Observability / Docs

- [ ] T104 [US1] 指标/日志/quickstart 更新

（按需继续添加 User Story 2、3……结构相同）

## 阶段 N：收尾与跨故事事项

- [ ] T901 文档/Runbook/培训
- [ ] T902 性能、安全、可用性加固
- [ ] T903 回归与发布准备

## 执行顺序提示

- 完成阶段 1+2 后，用户故事可并行推进。
- 每个故事需先写测试/验收，再实现，再补 observability。
- 任何跳过宪章要求的动作需要记录在 Complexity Tracking。
