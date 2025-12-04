# ASKJeff 快速开始指南

本指南帮助你在 5 分钟内启动并使用 ASKJeff 系统。

## 前置要求

- Docker 和 Docker Compose
- Git

## 快速启动

### 1. 克隆项目

```bash
git clone <repository-url>
cd askjeff
```

### 2. 启动服务

```bash
# 启动所有服务（数据库、后端、前端）
make up

# 或者使用 docker compose 命令
docker compose -p askjeff-dev -f infra/docker/compose.dev.yml up -d
```

等待所有容器启动完成（约 30 秒）。

### 3. 访问系统

- **前端界面**: <http://localhost:5174>
- **后端 API 文档**: <http://localhost:8001/docs>
- **健康检查**: <http://localhost:8001/health>

### 4. 默认登录

系统提供两个默认账号：

**管理员账号**:
- 用户名: `admin`
- 密码: `admin666`

**运营人员账号**:
- 用户名: `shangu`
- 密码: `shangu666`

登录页面会自动填入管理员账号密码。

## 核心功能使用

### 功能 1: 批量导入产品数据

1. 访问前端 <http://localhost:5174>
2. 登录后进入「导入」页面
3. 上传 CSV 或 XLSX 文件
4. 选择导入策略（追加/覆盖）
5. 等待导入完成

**支持的文件格式**:
- CSV（UTF-8 或 GBK 编码）
- XLSX/XLS

**必需字段**:
- `asin`: 产品 ASIN 码
- `title`: 产品标题
- `price`: 价格

### 功能 2: AI 特征提取

1. 在导入列表中找到已完成的批次
2. 点击「AI 提取」按钮
3. 选择要提取的字段（如：品牌、材质、尺寸等）
4. 等待 AI 处理完成
5. 在「提取」页面查看结果

### 功能 3: 自然语言查询

1. 点击右下角的聊天图标
2. 输入自然语言问题，例如：
   - "有多少个产品？"
   - "价格最高的 5 个产品是什么？"
   - "显示所有评分大于 4.5 的产品"
3. 系统会自动查询数据库并返回结果

### 功能 4: 数据导出

1. 进入「导出」页面
2. 选择导出类型：
   - 清洗后的产品数据
   - AI 提取结果
3. 选择要导出的字段
4. 选择文件格式（CSV/XLSX）
5. 点击「创建导出」
6. 在导出历史中下载文件

## 常用命令

```bash
# 查看服务状态
make ps
docker ps

# 查看日志
make backend-logs
make frontend-logs

# 停止服务
make down

# 重启服务
make restart

# 运行测试
make test-backend

# 进入后端容器
docker compose -p askjeff-dev -f infra/docker/compose.dev.yml exec backend bash

# 进入数据库
docker compose -p askjeff-dev -f infra/docker/compose.dev.yml exec db psql -U sorftime
```

## 环境配置

### 配置 DeepSeek API

编辑 `.env` 文件：

```bash
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### 配置数据库

默认配置：
- 主机: `localhost:5433`
- 数据库: `sorftime`
- 用户名: `sorftime`
- 密码: `sorftime`

修改配置请编辑 `infra/docker/compose.dev.yml`。

## 常见问题

### Q: Docker 容器启动失败？

**A**: 检查端口占用：

```bash
# 检查端口是否被占用
lsof -i :5174  # 前端
lsof -i :8001  # 后端
lsof -i :5433  # 数据库

# 停止占用端口的进程或修改 compose.dev.yml 中的端口映射
```

### Q: 前端无法连接后端？

**A**: 检查后端健康状态：

```bash
curl http://localhost:8001/health
```

如果返回 `{"status":"healthy",...}`，说明后端正常。检查前端环境变量配置。

### Q: 导入文件失败？

**A**: 常见原因：
1. 文件编码问题 - 确保 CSV 使用 UTF-8 或 GBK 编码
2. 缺少必需字段 - 确保包含 `asin`, `title`, `price`
3. 文件过大 - 默认限制 50MB，可在 `backend/app/config.py` 修改

### Q: AI 提取不工作？

**A**: 检查 DeepSeek API 配置：

```bash
# 进入后端容器
docker compose -p askjeff-dev -f infra/docker/compose.dev.yml exec backend bash

# 检查环境变量
echo $DEEPSEEK_API_KEY
```

### Q: 如何重置数据库？

**A**: 

```bash
# 停止服务
make down

# 删除数据库卷
docker volume rm askjeff-dev_postgres-data

# 重新启动
make up
```

## 开发模式

### 后端开发

后端代码修改会自动热重载。查看日志：

```bash
make backend-logs
```

### 前端开发

前端使用 Vite，支持热模块替换（HMR）。修改代码后浏览器会自动刷新。

### 运行测试

```bash
# 后端测试
make test-backend

# 查看测试覆盖率
docker compose -p askjeff-dev -f infra/docker/compose.dev.yml exec backend bash -c "poetry run pytest --cov=app tests/"
```

## 下一步

- 查看 [API 文档](http://localhost:8001/docs) 了解所有接口
- 阅读 [需求文档](../specs/README.md) 了解功能详情
- 查看 [部署指南](./deployment.md) 了解生产环境部署

## 获取帮助

- 查看项目 [README](../../README.md)
- 查看 [需求管理](../specs/README.md)
- 提交 Issue 或 PR
