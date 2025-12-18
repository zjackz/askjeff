# AI 快速启动指南

> 本文档为 AI 提供标准化的任务执行模板,加快开发速度并确保一致性。

**最后更新**: 2025-12-18

---

## 🚦 项目启动检查清单

在开始任何开发任务前,AI 应执行以下检查:

### 1. 环境检查

```bash
# 检查服务状态
make ps

# 预期输出:所有服务都是 Up 状态
# askjeff-dev-backend-1   Up
# askjeff-dev-frontend-1  Up
# askjeff-dev-db-1        Up
```

如果服务未启动:

```bash
make up
```

### 2. 代码同步检查

```bash
# 检查是否有未拉取的更新
git fetch
git status

# 如果有更新,先拉取
git pull
```

### 3. 数据库迁移检查

```bash
# 检查是否有未应用的迁移
docker exec askjeff-dev-backend-1 alembic current
docker exec askjeff-dev-backend-1 alembic heads

# 如果不一致,应用迁移
docker exec askjeff-dev-backend-1 alembic upgrade head
```

### 4. 依赖检查

```bash
# 前端依赖
cd frontend && pnpm install

# 后端依赖(通常在 Docker 中自动处理)
docker exec askjeff-dev-backend-1 poetry install
```

---

## 📋 典型任务模板

### 任务 1: 添加新的 API 端点

**场景**: 需要添加一个新的 API 接口

**步骤**:

1. **定义数据模型** (如需要)

   ```bash
   # 位置: backend/app/models/
   # 文件: your_model.py
   ```

2. **定义 Pydantic Schema**

   ```bash
   # 位置: backend/app/schemas/
   # 文件: your_schema.py
   ```

3. **实现 Service 层**

   ```bash
   # 位置: backend/app/services/
   # 文件: your_service.py
   ```

4. **实现 API 路由**

   ```bash
   # 位置: backend/app/api/routes/
   # 文件: your_routes.py
   ```

5. **注册路由**

   ```python
   # 文件: backend/app/main.py
   from app.api.routes import your_routes
   app.include_router(your_routes.router, prefix="/api/v1", tags=["your_tag"])
   ```

6. **编写测试**

   ```bash
   # 位置: backend/tests/api/
   # 文件: test_your_routes.py
   ```

7. **运行测试**

   ```bash
   docker exec askjeff-dev-backend-1 poetry run pytest tests/api/test_your_routes.py -v
   ```

8. **验证 API 文档**
   - 访问: <http://localhost:8000/docs>
   - 检查新端点是否出现

**检查清单**:
- [ ] Schema 有完整的字段验证
- [ ] Service 有异常处理
- [ ] API 有文档字符串
- [ ] 有集成测试(成功+失败场景)
- [ ] 敏感数据已脱敏
- [ ] 日志记录完整

---

### 任务 2: 添加新的前端页面

**场景**: 需要添加一个新的页面视图

**步骤**:

1. **创建页面组件**

   ```bash
   # 位置: frontend/src/views/
   # 文件: YourView.vue
   ```

2. **定义路由**

   ```typescript
   // 文件: frontend/src/router/index.ts
   {
     path: '/your-path',
     name: 'YourView',
     component: () => import('@/views/YourView.vue'),
     meta: { title: '页面标题', roles: ['admin', 'shangu'] }
   }
   ```

3. **添加菜单项** (如需要)

   ```typescript
   // 文件: frontend/src/layout/components/Sidebar/index.vue
   // 或配置文件
   ```

4. **创建 API 调用**

   ```bash
   # 位置: frontend/src/api/
   # 文件: your-api.ts
   ```

5. **创建 Pinia Store** (如需要)

   ```bash
   # 位置: frontend/src/stores/
   # 文件: your-store.ts
   ```

6. **测试页面**
   - 访问页面 URL
   - 检查 Loading 状态
   - 检查错误处理
   - 检查空状态

**检查清单**:
- [ ] 所有 API 调用有 loading 状态
- [ ] 错误提示是中文
- [ ] 表格有分页([20, 50, 100, 200])
- [ ] 表单有校验和首错聚焦
- [ ] 危险操作有二次确认
- [ ] 响应式布局正常

---

### 任务 3: 修复 Bug

**场景**: 用户报告了一个 Bug

**标准流程**:

1. **复现问题**
   - 获取详细的复现步骤
   - 在本地环境复现

2. **查询日志** (最重要!)

   ```bash
   # 查询最近的错误日志
   docker exec askjeff-dev-db-1 psql -U sorftime -d askjeff -c \
   "SELECT to_char(timestamp, 'HH24:MI:SS') as time, level, message, context 
    FROM system_logs 
    WHERE level='error' 
    AND timestamp >= NOW() - INTERVAL '30 minutes' 
    ORDER BY timestamp DESC LIMIT 5;"
   ```

3. **定位根因**
   - 根据日志定位到具体代码行
   - 使用 `rg` 搜索相关代码

   ```bash
   rg "关键字" backend/
   ```

4. **编写测试用例**
   - 先写一个能复现 Bug 的测试
   - 确保测试失败

5. **修复代码**
   - 修改代码
   - 运行测试,确保通过

6. **回归测试**

   ```bash
   # 运行所有相关测试
   docker exec askjeff-dev-backend-1 poetry run pytest tests/ -v
   ```

7. **验证修复**
   - 在本地环境验证
   - 再次查询日志,确认无错误

**检查清单**:
- [ ] 已查询日志定位问题
- [ ] 有测试用例覆盖 Bug
- [ ] 修复后测试通过
- [ ] 无副作用(其他功能正常)
- [ ] 日志中无新错误

---

### 任务 4: 数据库变更

**场景**: 需要修改数据库表结构

**步骤**:

1. **修改 Model**

   ```python
   # 文件: backend/app/models/your_model.py
   # 添加/修改字段
   ```

2. **生成迁移**

   ```bash
   docker exec askjeff-dev-backend-1 alembic revision --autogenerate -m "add field xxx to table yyy"
   ```

3. **检查迁移文件**

   ```bash
   # 位置: backend/migrations/versions/
   # 检查生成的迁移是否正确
   ```

4. **手动调整迁移** (如需要)
   - 添加默认值
   - 处理现有数据
   - 添加索引

5. **应用迁移**

   ```bash
   docker exec askjeff-dev-backend-1 alembic upgrade head
   ```

6. **验证数据库**

   ```bash
   docker exec askjeff-dev-db-1 psql -U sorftime -d askjeff -c "\d your_table"
   ```

7. **更新 Schema**

   ```python
   # 文件: backend/app/schemas/your_schema.py
   # 同步更新 Pydantic Schema
   ```

8. **测试**
   - 测试新字段的读写
   - 测试迁移的可回滚性

**检查清单**:
- [ ] 新字段有默认值或迁移脚本
- [ ] 迁移文件有中文注释
- [ ] 已测试迁移和回滚
- [ ] Schema 已同步更新
- [ ] 相关 API 已更新

---

## 🔍 快速诊断

### API 调用失败
1. 检查后端服务: `docker ps | grep backend`
2. 查看日志: `docker logs askjeff-dev-backend-1 --tail 50`
3. 查询错误: 见 AGENTS.md 快速命令速查表

### 前端白屏
1. 浏览器控制台 → 检查 Console 错误
2. Network 标签 → 检查失败请求
3. 重启服务: `docker restart askjeff-dev-frontend-1`

### 数据库连接失败

```bash
# 测试连接
docker exec askjeff-dev-db-1 psql -U sorftime -d askjeff -c "SELECT 1;"

# 检查环境变量
docker exec askjeff-dev-backend-1 env | grep DATABASE
```

---

## 📊 性能检查

### 数据库查询优化

```bash
# 分析查询计划
docker exec askjeff-dev-db-1 psql -U sorftime -d askjeff -c \
"EXPLAIN ANALYZE SELECT * FROM products WHERE category_id = 1;"
```

### N+1 查询检测

```python
# 在测试中启用 SQL 日志
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

---

## 🎯 AI 工作提示

**开始前**: 确认目标 → 检查 spec → 搜索参考 → 评估复杂度  
**过程中**: 小步提交 → 先查日志 → 参考 common-pitfalls.md  
**完成后**: 运行测试 → 检查日志 → 更新文档 → 提交推送

---

## 📚 参考
- [编码规范](coding-guidelines.md) - 自检清单
- [常见陷阱](common-pitfalls.md) - 已知问题
- [日志规范](logging-guidelines.md) - 诊断流程
- [测试规范](testing-guidelines.md) - 测试模板
