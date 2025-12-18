# askjeff 开发规范

AI 代理开发指南 - 快速索引与项目配置

**最后更新**: 2025-12-18

> 📋 **需求管理**: [specs/README.md](specs/README.md) | 🚀 **快速开始**: `/new-requirement`

---

## 🤖 AI 使用指南

### 默认行为
**AI 只需阅读本文件**,其他文档按需加载。

### 按需加载表

| 场景 | 阅读文档 |
|------|---------|
| 开始新任务 | [quick-start.md](AGENTS/quick-start.md) |
| 编写代码 | [coding-guidelines.md](AGENTS/coding-guidelines.md) (自检清单) |
| 遇到问题 | [common-pitfalls.md](AGENTS/common-pitfalls.md) (搜索关键词) |
| API 失败 | [logging-guidelines.md](AGENTS/logging-guidelines.md) (诊断流程) |
| 编写测试 | [testing-guidelines.md](AGENTS/testing-guidelines.md) (示例) |
| UI 开发 | [ui-ux-guidelines.md](AGENTS/ui-ux-guidelines.md) |

---

## 🚀 当前工作模式

**快速迭代模式** - 优先实现功能,核心功能必须有测试

<details>
<summary>其他模式 (点击查看)</summary>

- **严格模式**: TDD,生产环境修复
- **探索模式**: 技术选型,实验性代码

</details>

---

## ⚡ 快速命令

<details>
<summary>常用命令速查 (点击展开)</summary>

```bash
# 开发环境
make up                    # 启动服务
make ps                    # 查看状态
make backend-logs          # 查看日志

# 测试
docker exec askjeff-dev-backend-1 poetry run pytest tests/
pnpm --prefix frontend lint

# 数据库
docker exec askjeff-dev-backend-1 alembic upgrade head
docker exec askjeff-dev-db-1 psql -U sorftime -d askjeff

# 日志排查
docker exec askjeff-dev-db-1 psql -U sorftime -d askjeff -c \
"SELECT * FROM system_logs WHERE level='error' ORDER BY timestamp DESC LIMIT 5;"

# Git
git pull
git add . && git commit -m "feat(编号): 描述" && git push
```

</details>

---

## 📚 完整规范索引

### 核心规范
- [编程规范](AGENTS/coding-guidelines.md) - 编码标准、自检清单
- [开发手册](AGENTS/playbook.md) - 开发流程、验证门禁
- [日志规范](AGENTS/logging-guidelines.md) - 日志分析、问题诊断
- [测试规范](AGENTS/testing-guidelines.md) - 测试策略、编写规范
- [UI/UX 规范](AGENTS/ui-ux-guidelines.md) - UI 统一规范

### 实用指南 ⭐
- [快速启动](AGENTS/quick-start.md) - 任务模板、诊断流程
- [常见陷阱](AGENTS/common-pitfalls.md) - TOP 10 问题、解决方案
- [优化模式](AGENTS/optimization-patterns.md) ⭐ - 代码优化和重构最佳实践
- [代码审查模板](AGENTS/code-review-template.md) - 标准审查流程

### 自动化工具 🛠️
- `scripts/check_code_quality.py` - 后端代码质量自动检查
- `scripts/check_frontend_quality.py` ⭐ - 前端代码质量自动检查

---

## 🛠️ 项目配置

### 技术栈
- **前端**: Vue 3 + TypeScript + Vite + Element Plus + Pinia
- **后端**: FastAPI (Python 3.12+) + Pydantic v2 + SQLAlchemy 2.0
- **数据库**: PostgreSQL 15
- **DevOps**: Docker + Docker Compose (必须在容器中开发)

### 版本约束

| 组件 | 当前版本 | 最低版本 |
|------|---------|---------|
| Python | 3.12 | 3.12 |
| PostgreSQL | 15 | 14 |
| Node.js | 20.x | 18.x |
| Docker | 24.x | 20.x |

⚠️ 升级前必须运行完整测试套件

### 项目结构

```
askjeff/
├── frontend/          # Vue 3 前端
├── backend/           # FastAPI 后端
│   ├── app/          # 应用代码
│   ├── tests/        # 测试
│   └── migrations/   # 数据库迁移
├── specs/            # 需求文档
├── AGENTS/           # AI 开发规范
└── .agent/workflows/ # 工作流程
```

---

## 🛡️ 项目治理规范 (Governance)

为了防止配置漂移和脚本混乱，所有 AI 和开发者必须遵守以下治理规则：

### 1. 脚本存放规范
- **严禁**在 `backend/` 根目录创建 `.py` 脚本。
- 所有一次性脚本、初始化脚本必须存放在 `backend/scripts/` 目录下。
- 脚本必须支持幂等性（重复运行不报错）。

### 2. 操作入口规范
- **严禁**直接运行 `python xxx.py`。
- 所有运维操作必须封装在 `Makefile` 中。
- 如果需要新功能，先在 `Makefile` 中注册命令，再调用脚本。

### 3. 配置唯一性
- 账号、密码、端口等配置必须在 `backend/app/core/config.py` 或 `.env` 中定义。
- **严禁**在脚本中硬编码这些值。

---

## 📝 Prompt 配置化规范

**核心原则**: 所有用于 AI 生成的 System Prompt **必须**配置化，禁止硬编码在业务逻辑中。

### 配置文件位置

所有 Prompt 配置文件统一存放在: `backend/app/prompts/`

### 使用规范

✅ **必须**:
- 所有 Prompt 独立成文件
- 在业务代码中通过 import 引用
- 添加详细的注释说明用途

❌ **禁止**:
- 在业务逻辑中硬编码 Prompt
- 使用字符串拼接构建 Prompt

---

## 📋 开发流程

### 创建新需求

```bash
/new-requirement  # 在 AI 助手中运行
```

### 验证与推送

```bash
# 1. 测试
docker exec askjeff-dev-backend-1 poetry run pytest tests/
pnpm --prefix frontend lint

# 2. 提交
git add .
git commit -m "feat(编号): 描述"
git push
```

**测试要求**:
- ✅ 新增 API 端点必须有集成测试
- ✅ 核心业务逻辑必须有单元测试
- ✅ 所有测试必须通过才能推送

---

## 🎯 项目特定规范

### 通用规范
- ✅ 所有代码、注释、文档必须使用中文
- ✅ 提交信息格式: `feat(编号): 描述` 或 `fix(编号): 描述`
- ✅ 小步提交,每完成一个小功能就提交

### 前端规范
- 使用 `<script setup>` + Composition API
- Element Plus 默认尺寸,禁止随意 `size="small"`
- 表格分页: `[20, 50, 100, 200]`,默认 50
- 所有 API 调用必须有 loading 状态

### 后端规范
- 模块拆分: `api/routers` | `services` | `models` | `schemas`
- 所有外部 API 调用必须有超时(默认 30s)
- 敏感数据必须脱敏记录
- 分页查询最大 200 条

### 权限控制
- `admin`: 管理员,所有权限
- `shangu`: 运营人员,日常操作权限

---

## 🔍 日志与诊断

### 核心原则
**问题诊断优先级: 日志 > 猜测**

### 数据库连接
- 容器: `askjeff-dev-db-1`
- 用户: `sorftime`
- 数据库: `askjeff`

### 快速诊断

```bash
# 查询最近错误
docker exec askjeff-dev-db-1 psql -U sorftime -d askjeff -c \
"SELECT * FROM system_logs WHERE level='error' ORDER BY timestamp DESC LIMIT 5;"
```

详见: [logging-guidelines.md](AGENTS/logging-guidelines.md)

---

## 📖 参考资料

- [项目 README](README.md) - 快速启动指南
- [需求管理](specs/README.md) - 功能需求索引
- [新需求工作流](.agent/workflows/new-requirement.md) - 创建新需求步骤
