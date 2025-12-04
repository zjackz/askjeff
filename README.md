# ASKJeff - 亚马逊产品信息智能管理系统

ASKJeff 是一个基于 AI 的产品数据管理平台，提供批量导入、智能提取、自然语言查询和灵活导出功能。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/vue-3.x-green.svg)](https://vuejs.org/)

## ✨ 核心功能

### 📥 批量数据导入
- 支持 CSV/XLSX 文件格式
- 自动编码检测（UTF-8/GBK/GB18030）
- 数据验证和清洗
- 导入策略：追加或替换

### 🤖 AI 智能提取
- 基于 DeepSeek 的特征提取
- 自定义提取字段（品牌、材质、尺寸等）
- Token 使用统计和成本计算
- 批量处理支持

### 💬 自然语言查询
- 支持中文自然语言问答
- 自动生成数据库查询
- 智能工具调用（Function Calling）
- 查询历史记录

### 📤 灵活数据导出
- 多种导出类型（清洗数据/AI 结果）
- CSV/XLSX 格式支持
- AI 字段高亮显示
- 自定义字段选择

### 🔍 产品数据查询
- 多维度筛选（价格、评分、分类）
- 全文搜索
- 分页和排序
- 详情查看

## 🚀 快速开始

### 前置要求

- Docker 和 Docker Compose
- Git

### 一键启动

```bash
# 克隆项目
git clone <repository-url>
cd askjeff

# 启动所有服务
make up

# 访问系统
# 前端: http://localhost:5174
# 后端 API: http://localhost:8001/docs
```

**默认登录**:
- 管理员: `admin` / `admin666`
- 运营人员: `shangu` / `shangu666`

详细说明请查看 [快速开始指南](docs/quickstart.md)。

## 📚 文档

- 📖 [快速开始指南](docs/quickstart.md) - 5 分钟上手
- 🔌 [API 使用示例](docs/api-examples.md) - 完整的 API 调用示例
- 🚢 [部署指南](docs/deployment.md) - 生产环境部署
- 💻 [开发指南](docs/development.md) - 本地开发和贡献指南
- 📋 [需求管理](specs/README.md) - 功能需求和开发计划

## 🏗️ 技术栈

### 后端
- **框架**: FastAPI 0.111+
- **数据库**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **AI**: DeepSeek API
- **认证**: JWT
- **测试**: Pytest

### 前端
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **UI 组件**: Element Plus
- **状态管理**: Pinia
- **HTTP 客户端**: Axios

### 基础设施
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx
- **CI/CD**: GitHub Actions

## 📊 项目状态

| 需求 | 状态 | 完成度 |
|------|------|--------|
| 001 - 数据智能控制台 | ✅ 已完成 | 100% |
| 002 - Insight 产品列表 | ✅ 已完成 | 100% |
| 003 - LLM 特征提取 | ✅ 已完成 | 100% |
| 004 - Chatbot 数据库交互 | ✅ 已完成 | 100% |

**测试覆盖**: 69/70 通过 (98.6%)

查看 [需求看板](specs/KANBAN.md) 了解详细进展。

## 🛠️ 常用命令

```bash
# 查看服务状态
make ps

# 查看日志
make backend-logs
make frontend-logs

# 运行测试
make test-backend

# 停止服务
make down

# 重启服务
make restart
```

完整命令列表请查看 [Makefile](Makefile)。

## 📁 项目结构

```text
askjeff/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── api/         # API 路由
│   │   ├── models/      # 数据模型
│   │   ├── services/    # 业务逻辑
│   │   └── schemas/     # Pydantic 模式
│   └── tests/           # 测试文件
├── frontend/            # Vue 3 前端
│   ├── src/
│   │   ├── api/        # API 客户端
│   │   ├── components/ # Vue 组件
│   │   ├── views/      # 页面视图
│   │   └── stores/     # Pinia 状态
│   └── public/         # 静态资源
├── infra/              # 基础设施配置
│   └── docker/         # Docker 配置
├── docs/               # 项目文档
├── specs/              # 需求规格
└── scripts/            # 工具脚本
```

## 🔧 环境配置

创建 `.env` 文件：

```bash
# DeepSeek API
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 数据库
POSTGRES_USER=sorftime
POSTGRES_PASSWORD=sorftime
POSTGRES_DB=sorftime

# JWT
SECRET_KEY=your_secret_key_here

# 其他配置
MAX_FILE_SIZE_MB=50
LOG_LEVEL=INFO
```

## 🤝 贡献指南

欢迎贡献！请查看 [开发指南](docs/development.md) 了解如何参与项目。

### 开发流程

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/)：

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [Element Plus](https://element-plus.org/) - Vue 3 UI 组件库
- [DeepSeek](https://www.deepseek.com/) - AI 大语言模型

## 📞 联系方式

- 项目主页: <https://github.com/your-org/askjeff>
- Issue 追踪: <https://github.com/your-org/askjeff/issues>
- 文档: [docs/](docs/)

---

**注意**: 本项目仅用于演示和学习目的。生产环境使用前请进行充分测试。
