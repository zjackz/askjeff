---
description: 在生成任务后，对 spec.md、plan.md、tasks.md 进行非破坏式的跨文档一致性与质量分析。
---

## User Input

```text
$ARGUMENTS
```

在继续之前（如果非空）你**必须**先考虑用户输入。

## Goal

在实施前找出三份核心文档（`spec.md`、`plan.md`、`tasks.md`）中的不一致、重复、含糊与欠明确项。此命令**必须**在 `/speckit.tasks` 已成功生成完整 `tasks.md` 后运行。

## Operating Constraints

**严格只读**：**不要**修改任何文件。仅输出结构化分析报告。可提供可选的修正方案（后续编辑需用户明确批准且手动触发）。

**宪章权威**：项目宪章（`.specify/memory/constitution.md`）在此分析范围内**不可协商**。凡与宪章冲突者自动视为 CRITICAL，要求调整 spec、plan 或 tasks，而非稀释、曲解或忽略原则。如需修改原则本身，必须在 `/speckit.analyze` 之外进行单独且明确的宪章更新。

## Execution Steps

### 1. 初始化分析上下文

在仓库根目录运行一次 `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks`，解析 JSON 中的 FEATURE_DIR 与 AVAILABLE_DOCS，得到绝对路径：

- SPEC = FEATURE_DIR/spec.md
- PLAN = FEATURE_DIR/plan.md
- TASKS = FEATURE_DIR/tasks.md

若缺少必需文件则报错并提示用户运行缺失的前置命令。
对含单引号的参数（如 "I'm Groot"），使用转义：'I'\''m Groot'（或尽量使用双引号："I'm Groot"）。

### 2. 逐步加载文档

仅加载每份文档的必要最小上下文：

**来自 spec.md：**

- 概述/背景
- 功能需求
- 非功能需求
- 用户故事
- 边界情况（如有）

**来自 plan.md：**

- 架构/技术栈选择
- 数据模型引用
- 阶段
- 技术约束

**来自 tasks.md：**

- 任务 ID
- 描述
- 阶段分组
- 并行标记 [P]
- 引用的文件路径

**来自宪章：**

- 加载 `.specify/memory/constitution.md` 以校验原则

### 3. 构建语义模型

创建内部表示（输出中不要包含原文档）：

- **需求清单**：为每个功能/非功能需求生成稳定键（根据祈使短语生成 slug，如 “User can upload file” → `user-can-upload-file`）
- **用户故事/动作清单**：离散的用户动作及其验收条件
- **任务覆盖映射**：将每个任务映射到一个或多个需求或故事（按关键词或显式引用如 ID、关键短语推断）
- **宪章规则集**：提取原则名称与 MUST/SHOULD 规范性语句

### 4. 检测流程（尽量节省 tokens）

聚焦高信号问题，总数上限 50 条，其余汇总至溢出摘要。

#### A. 重复检测

- 识别近似重复的需求
- 标注较差表述以便合并

#### B. 含糊检测

- 标记缺乏可度量标准的模糊形容词（fast、scalable、secure、intuitive、robust 等）
- 标记未解决的占位符（TODO、TKTK、???、`<placeholder>` 等）

#### C. 欠明确

- 有动词但缺少对象或可衡量结果的需求
- 缺少验收标准对齐的用户故事
- 任务引用了 spec/plan 未定义的文件或组件

#### D. 宪章对齐

- 任何与 MUST 原则冲突的需求或计划条目
- 缺失宪章要求的章节或质量门

#### E. 覆盖缺口

- 无关联任务的需求
- 未映射到需求/故事的任务
- 未在任务中体现的非功能需求（如性能、安全）

#### F. 不一致

- 术语漂移（同一概念在文件间不同称呼）
- plan 中提到的数据实体在 spec 缺失（或反之）
- 任务排序矛盾（如集成任务排在基础任务前且无依赖说明）
- 冲突需求（如一处要求 Next.js 而另一处指定 Vue）

### 5. 严重性划分

使用以下启发式确定优先级：

- **CRITICAL**：违反宪章 MUST、缺少核心文档、或基础功能被零覆盖需求阻塞
- **HIGH**：重复/冲突需求，安全/性能表述含糊，不可测试的验收标准
- **MEDIUM**：术语漂移、非功能任务缺失、边界情况不明确
- **LOW**：措辞优化、对执行顺序无影响的轻微冗余

### 6. 输出精简分析报告

输出 Markdown 报告（不写文件），结构如下：

## Specification Analysis Report

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| A1 | Duplication | HIGH | spec.md:L120-134 | Two similar requirements ... | Merge phrasing; keep clearer version |

（每条发现一行；ID 以类别首字母稳定生成。）

**覆盖率汇总表：**

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|

**宪章对齐问题：**（如有）

**未映射任务：**（如有）

**指标：**

- 总需求数
- 总任务数
- 覆盖率（≥1 任务的需求占比）
- 含糊计数
- 重复计数
- CRITICAL 问题计数

### 7. 给出后续动作

在报告末尾输出简明后续行动：

- 若存在 CRITICAL：建议在 `/speckit.implement` 前解决
- 若仅 LOW/MEDIUM：可继续，但给出改进建议
- 提供明确命令建议：如 “运行 /speckit.specify 细化”、 “运行 /speckit.plan 调整架构”、 “手动编辑 tasks.md 补充 'performance-metrics' 覆盖”

### 8. 提供修正提议

询问用户：“是否需要我为前 N 个问题给出具体修正方案？”（**不要**自动应用）。

## Operating Principles

### 上下文效率

- **最少高信号 tokens**：聚焦可行动发现，避免穷举
- **渐进披露**：逐步加载文档，不要一次性倾倒
- **Token 友好输出**：发现表最多 50 行，其余汇总
- **结果可复现**：无变更重跑应给出一致的 ID 与计数

### 分析准则

- **绝不修改文件**（只读分析）
- **绝不臆造缺失章节**（缺哪报哪）
- **优先宪章违规**（永远视为 CRITICAL）
- **多用实例少讲泛论**（引用具体片段而非空泛规则）
- **零问题亦要体面报告**（给出覆盖率等统计）

## Context

$ARGUMENTS
