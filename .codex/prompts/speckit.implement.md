---
description: 按 tasks.md 中的任务定义执行实施计划。
---

## User Input

```text
$ARGUMENTS
```

在继续之前（如果非空）你**必须**先考虑用户输入。

## Outline

1. 在仓库根目录运行 `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks`，解析 FEATURE_DIR 与 AVAILABLE_DOCS 列表。路径必须绝对化。对含单引号的参数（如 "I'm Groot"），使用转义：'I'\''m Groot'（或尽量使用双引号："I'm Groot"）。

2. **检查检查清单状态**（若存在 FEATURE_DIR/checklists/）：
   - 扫描 checklists/ 下所有清单
   - 对每个清单统计：
     - 总项数：匹配 `- [ ]`、`- [X]`、`- [x]`
     - 已完成：匹配 `- [X]` 或 `- [x]`
     - 未完成：匹配 `- [ ]`
   - 生成状态表：

     ```text
     | Checklist | Total | Completed | Incomplete | Status |
     |-----------|-------|-----------|------------|--------|
     | ux.md     | 12    | 12        | 0          | ✓ PASS |
     | test.md   | 8     | 5         | 3          | ✗ FAIL |
     | security.md | 6   | 6         | 0          | ✓ PASS |
     ```

   - 计算总体状态：
     - **PASS**：所有清单未完成项为 0
     - **FAIL**：任一清单存在未完成项

   - **若有未完成清单**：
     - 展示表格与未完成数
     - **停止** 并询问：“部分检查清单未完成。是否仍要继续实施？(yes/no)”
     - 等待用户回复
     - 若用户回答 “no/wait/stop”，终止
     - 若用户回答 “yes/proceed/continue”，继续执行第 3 步

   - **若全部完成**：
     - 展示全部通过表格
     - 自动进入第 3 步

3. 读取并分析实施上下文：
   - **必读**：tasks.md（完整任务清单与执行计划）
   - **必读**：plan.md（技术栈、架构、目录结构）
   - **如有**：data-model.md（实体与关系）
   - **如有**：contracts/（API 规格与测试要求）
   - **如有**：research.md（技术决策与约束）
   - **如有**：quickstart.md（集成场景）

4. **项目环境核查**：
   - **必需**：依据实际项目生成/校验忽略文件：

   **检测与创建逻辑**：
   - 通过运行下述命令判断是否为 git 仓库（若是则创建/校验 .gitignore）：

     ```sh
     git rev-parse --git-dir 2>/dev/null
     ```

   - 存在 Dockerfile* 或 plan.md 提到 Docker → 创建/校验 .dockerignore
   - 存在 .eslintrc* → 创建/校验 .eslintignore
   - 存在 eslint.config.* → 确保其中 `ignores` 覆盖所需模式
   - 存在 .prettierrc* → 创建/校验 .prettierignore
   - 存在 .npmrc 或 package.json → 创建/校验 .npmignore（若需发布）
   - 存在 terraform 文件 (*.tf) → 创建/校验 .terraformignore
   - 存在 Helm chart → 视需要创建/校验 .helmignore

   **若忽略文件已存在**：校验是否包含关键模式，仅补充缺失的关键模式
   **若缺失**：依据技术栈创建包含完整模式的忽略文件

   **按技术的常见模式**（来自 plan.md 技术栈）：
   - **Node.js/JavaScript/TypeScript**：`node_modules/`、`dist/`、`build/`、`*.log`、`.env*`
   - **Python**：`__pycache__/`、`*.pyc`、`.venv/`、`venv/`、`dist/`、`*.egg-info/`
   - **Java**：`target/`、`*.class`、`*.jar`、`.gradle/`、`build/`
   - **C#/.NET**：`bin/`、`obj/`、`*.user`、`*.suo`、`packages/`
   - **Go**：`*.exe`、`*.test`、`vendor/`、`*.out`
   - **Ruby**：`.bundle/`、`log/`、`tmp/`、`*.gem`、`vendor/bundle/`
   - **PHP**：`vendor/`、`*.log`、`*.cache`、`*.env`
   - **Rust**：`target/`、`debug/`、`release/`、`*.rs.bk`、`*.rlib`、`*.prof*`、`.idea/`、`*.log`、`.env*`
   - **Kotlin**：`build/`、`out/`、`.gradle/`、`.idea/`、`*.class`、`*.jar`、`*.iml`、`*.log`、`.env*`
   - **C++**：`build/`、`bin/`、`obj/`、`out/`、`*.o`、`*.so`、`*.a`、`*.exe`、`*.dll`、`.idea/`、`*.log`、`.env*`
   - **C**：`build/`、`bin/`、`obj/`、`out/`、`*.o`、`*.a`、`*.so`、`*.exe`、`Makefile`、`config.log`、`.idea/`、`*.log`、`.env*`
   - **Swift**：`.build/`、`DerivedData/`、`*.swiftpm/`、`Packages/`
   - **R**：`.Rproj.user/`、`.Rhistory`、`.RData`、`.Ruserdata`、`*.Rproj`、`packrat/`、`renv/`
   - **通用**：`.DS_Store`、`Thumbs.db`、`*.tmp`、`*.swp`、`.vscode/`、`.idea/`

   **工具特定模式**：
   - **Docker**：`node_modules/`、`.git/`、`Dockerfile*`、`.dockerignore`、`*.log*`、`.env*`、`coverage/`
   - **ESLint**：`node_modules/`、`dist/`、`build/`、`coverage/`、`*.min.js`
   - **Prettier**：`node_modules/`、`dist/`、`build/`、`coverage/`、`package-lock.json`、`yarn.lock`、`pnpm-lock.yaml`
   - **Terraform**：`.terraform/`、`*.tfstate*`、`*.tfvars`、`.terraform.lock.hcl`
   - **Kubernetes/k8s**：`*.secret.yaml`、`secrets/`、`.kube/`、`kubeconfig*`、`*.key`、`*.crt`

5. 解析 tasks.md 结构并提取：
   - **任务阶段**：Setup、Tests、Core、Integration、Polish
   - **任务依赖**：顺序 vs 并行规则
   - **任务细节**：ID、描述、文件路径、并行标记 [P]
   - **执行流**：顺序与依赖要求

6. 按任务计划执行实施：
   - **按阶段执行**：完成当前阶段再进入下一阶段
   - **遵循依赖**：顺序任务按序执行，并行任务 [P] 可并行
   - **TDD 优先**：测试任务优先于对应实现
   - **基于文件的协同**：影响同一文件的任务需顺序执行
   - **校验检查点**：每阶段完成后验证再前进

7. 实施执行规则：
   - **先 Setup**：初始化项目结构、依赖、配置
   - **先写测试**：针对契约、实体、集成场景需先写测试
   - **核心开发**：实现模型、服务、CLI、端点
   - **集成**：数据库连接、中间件、日志、外部服务
   - **收尾与验证**：单测、性能优化、文档

8. 进度跟踪与错误处理：
   - 每完成任务汇报进度
   - 非并行任务失败即中止
   - 并行任务 [P] 可继续成功项并报告失败项
   - 提供清晰错误信息与调试上下文
   - 若无法继续，给出下一步建议
   - **重要**：完成的任务需在 tasks 文件中标记为 [X]

9. 完成验证：
   - 确认全部必需任务完成
   - 检查实现特性符合原始规范
   - 验证测试通过且覆盖满足要求
   - 确认实现遵循技术计划
   - 汇报最终状态与完成工作摘要

注意：该命令假定 tasks.md 已有完整拆分。若任务缺失或不完整，建议先运行 `/speckit.tasks` 生成任务清单。
