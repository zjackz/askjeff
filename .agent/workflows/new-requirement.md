---
description: 创建新需求的简化流程
---

# 创建新需求工作流

## 前提条件

确保你在 main 分支且代码是最新的：

```bash
git checkout main
git pull origin main
```

## 步骤

### 1. 确定需求编号

查看 `specs/README.md` 中的需求列表，确定下一个可用编号（如 003）。

### 2. 使用 spec-kit 创建规格说明

在 AI 助手中运行：

```
/speckit.specify [详细描述你的需求]
```

这将在 `specs/00X-requirement-name/` 目录下生成 `spec.md`。

### 3. 创建技术实施计划

```
/speckit.plan [技术栈和架构选择]
```

生成 `plan.md` 文件。

### 4. 分解任务

```
/speckit.tasks
```

生成 `tasks.md` 文件。

### 5. 开始实施

```
/speckit.implement
```

或手动按照 tasks.md 逐步实现。

### 6. 提交代码

// turbo-all

```bash
git add .
git commit -m "feat(00X): 实现某功能模块"
git push origin main
```

### 7. 更新需求状态

完成后，编辑 `specs/README.md`，将需求状态更新为 ✅ 已完成，并填写完成日期。

## 注意事项

- **不需要创建功能分支** - 除非是大型重构或实验性功能
- **小步提交** - 每完成一个小功能就提交一次
- **保持 main 稳定** - 确保每次推送的代码都能运行
- **及时更新文档** - 需求变更时同步更新 spec.md

## 示例

假设要添加"用户认证"功能：

1. 编号：003
2. 运行：`/speckit.specify 实现用户登录、注册、密码重置功能，使用 JWT 认证`
3. 运行：`/speckit.plan 使用 FastAPI + JWT + PostgreSQL`
4. 运行：`/speckit.tasks`
5. 运行：`/speckit.implement`
6. 提交：`git commit -m "feat(003): 添加用户认证模块"`
7. 更新 `specs/README.md` 状态
