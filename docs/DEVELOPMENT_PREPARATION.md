# 后续开发准备清单

**制定时间**: 2025-12-30  
**目标**: 为新功能开发做好充分准备

---

## 🎯 立即可做 (1-2 小时)

### 1. **创建开发规范文档** ✅ 推荐

#### 1.1 API 开发规范

```markdown
# API 开发规范

## 路由命名
- 使用 RESTful 风格
- 统一使用 /api/v1/ 前缀
- 资源名使用复数: /products, /imports

## 响应格式
- 成功: { "data": {...}, "message": "..." }
- 失败: { "error": {...}, "message": "..." }

## 状态码
- 200: 成功
- 201: 创建成功
- 400: 请求错误
- 401: 未认证
- 403: 无权限
- 404: 资源不存在
- 500: 服务器错误
```

#### 1.2 数据库迁移规范

```markdown
# 数据库迁移规范

## 命名规则
- 格式: YYYYMMDD_HHMM_描述.py
- 示例: 20251230_1400_add_user_role.py

## 最佳实践
- 每次迁移只做一件事
- 提供 upgrade 和 downgrade
- 添加详细注释
- 测试迁移脚本
```

---

### 2. **建立代码模板** ✅ 推荐

#### 2.1 新服务模板

```python
# backend/app/services/template_service.py
"""
[服务名称] 服务

功能描述:
- 功能 1
- 功能 2
"""
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class TemplateService:
    """[服务名称] 服务类"""
    
    def __init__(self):
        """初始化服务"""
        pass
    
    async def process(
        self,
        db: Session,
        *,
        param1: str,
        param2: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        处理主要业务逻辑
        
        Args:
            db: 数据库会话
            param1: 参数1说明
            param2: 参数2说明
        
        Returns:
            处理结果
        
        Raises:
            ValueError: 参数错误
            Exception: 处理失败
        """
        logger.info(f"开始处理: param1={param1}")
        
        try:
            # 业务逻辑
            result = {"status": "success"}
            
            logger.info("处理完成")
            return result
            
        except Exception as e:
            logger.error(f"处理失败: {e}", exc_info=True)
            raise


# 创建服务实例
template_service = TemplateService()
```

#### 2.2 新路由模板

```python
# backend/app/api/routes/template.py
"""
[功能名称] API 路由
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.template import TemplateRequest, TemplateResponse
from app.services.template_service import template_service

router = APIRouter()


@router.post("/template", response_model=TemplateResponse)
async def create_template(
    request: TemplateRequest,
    db: Annotated[Session, Depends(deps.get_db)],
    current_user: Annotated[dict, Depends(deps.get_current_user)]
) -> TemplateResponse:
    """
    创建模板
    
    - **param1**: 参数1说明
    - **param2**: 参数2说明
    """
    try:
        result = await template_service.process(
            db,
            param1=request.param1,
            param2=request.param2
        )
        return TemplateResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")
```

#### 2.3 新 Schema 模板

```python
# backend/app/schemas/template.py
"""
[功能名称] 数据模型
"""
from typing import Optional
from pydantic import BaseModel, Field


class TemplateRequest(BaseModel):
    """模板请求"""
    param1: str = Field(..., description="参数1说明")
    param2: Optional[str] = Field(None, description="参数2说明")


class TemplateResponse(BaseModel):
    """模板响应"""
    status: str = Field(..., description="状态")
    message: str = Field(..., description="消息")
    data: Optional[dict] = Field(None, description="数据")
    
    class Config:
        from_attributes = True
```

---

### 3. **完善测试框架** ✅ 推荐

#### 3.1 测试模板

```python
# backend/tests/api/test_template.py
"""
[功能名称] API 测试
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app

client = TestClient(app)


def test_create_template_success(db: Session):
    """测试创建模板成功"""
    response = client.post(
        "/api/v1/template",
        json={
            "param1": "test",
            "param2": "value"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


def test_create_template_validation_error(db: Session):
    """测试参数验证失败"""
    response = client.post(
        "/api/v1/template",
        json={}
    )
    assert response.status_code == 422


def test_create_template_unauthorized():
    """测试未授权访问"""
    response = client.post(
        "/api/v1/template",
        json={"param1": "test"}
    )
    # 根据实际权限要求调整
    assert response.status_code in [401, 403]
```

---

### 4. **建立前端组件库** ✅ 推荐

#### 4.1 通用组件模板

```vue
<!-- frontend/src/components/common/TemplateComponent.vue -->
<template>
  <div class="template-component">
    <h3>{{ title }}</h3>
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'

interface Props {
  title: string
  data?: any
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'update', value: any): void
  (e: 'delete', id: string): void
}>()

const handleUpdate = (value: any) => {
  emit('update', value)
}
</script>

<style scoped>
.template-component {
  padding: 16px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}
</style>
```

---

## 🔧 技术债优化 (2-4 小时)

### 5. **拆分大文件** 🔶 可选

#### 5.1 拆分 api_import_service.py (33KB)

```
services/api_import/
├── __init__.py
├── service.py          # 主服务 (10KB)
├── validator.py        # 验证逻辑 (8KB)
├── parser.py           # 解析逻辑 (8KB)
└── normalizer.py       # 标准化逻辑 (7KB)
```

**预估工时**: 2-3 小时

---

### 6. **修复前端 ESLint 错误** 🔶 可选

**问题**: 113 个 ESLint 错误
- `vue/no-mutating-props`: 17 处
- `@typescript-eslint/no-explicit-any`: 20+ 处
- `@typescript-eslint/no-unused-vars`: 3 处

**预估工时**: 2-3 小时

---

## 📚 文档完善 (1-2 小时)

### 7. **API 文档** ✅ 推荐

#### 7.1 使用 FastAPI 自动文档
- 访问: <http://localhost:8001/docs>
- 添加详细的 docstring
- 添加请求/响应示例

#### 7.2 创建 API 使用指南

```markdown
# API 使用指南

## 认证
所有 API 需要 JWT Token:
```

Authorization: Bearer <token>

```

## 常用 API

### 1. 数据导入
POST /api/v1/imports
- 上传文件
- 选择导入策略

### 2. 数据导出
POST /api/v1/exports
- 选择导出类型
- 自定义字段
```

---

### 8. **部署文档** ✅ 推荐

```markdown
# 生产环境部署指南

## 环境要求
- Docker 20.x+
- Docker Compose 2.x+
- PostgreSQL 15+

## 部署步骤
1. 克隆代码
2. 配置环境变量
3. 启动服务
4. 数据库迁移
5. 验证部署

## 监控和日志
- 日志位置: /var/log/askjeff/
- 监控端点: /api/health
```

---

## 🛠️ 开发工具配置 (30 分钟)

### 9. **Pre-commit Hooks** ✅ 推荐

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.12

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

---

### 10. **VS Code 配置** ✅ 推荐

```json
// .vscode/settings.json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[vue]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

---

## 🎨 UI/UX 准备 (1-2 小时)

### 11. **设计系统** ✅ 推荐

#### 11.1 颜色规范

```css
/* frontend/src/styles/variables.css */
:root {
  /* 主色 */
  --color-primary: #409EFF;
  --color-success: #67C23A;
  --color-warning: #E6A23C;
  --color-danger: #F56C6C;
  --color-info: #909399;
  
  /* 中性色 */
  --color-text-primary: #303133;
  --color-text-regular: #606266;
  --color-text-secondary: #909399;
  --color-text-placeholder: #C0C4CC;
  
  /* 边框色 */
  --color-border-base: #DCDFE6;
  --color-border-light: #E4E7ED;
  --color-border-lighter: #EBEEF5;
  --color-border-extra-light: #F2F6FC;
  
  /* 背景色 */
  --color-background: #FFFFFF;
  --color-background-base: #F5F7FA;
}
```

#### 11.2 间距规范

```css
/* 间距系统 (8px 基准) */
--spacing-xs: 4px;
--spacing-sm: 8px;
--spacing-md: 16px;
--spacing-lg: 24px;
--spacing-xl: 32px;
--spacing-xxl: 48px;
```

---

### 12. **组件库文档** 🔶 可选

使用 Storybook:

```bash
# 安装 Storybook
cd frontend
npx storybook@latest init

# 运行 Storybook
npm run storybook
```

---

## 🔐 安全加固 (1 小时)

### 13. **安全检查清单** ✅ 推荐

```markdown
# 安全检查清单

## 认证和授权
- [ ] JWT Token 过期时间合理 (当前 8 天)
- [ ] 密码强度要求
- [ ] 防止暴力破解 (登录限流)
- [ ] CORS 配置正确

## 数据安全
- [ ] 敏感数据加密存储
- [ ] SQL 注入防护 (使用 ORM)
- [ ] XSS 防护
- [ ] CSRF 防护

## API 安全
- [ ] 请求限流
- [ ] 输入验证
- [ ] 输出编码
- [ ] 错误信息不泄露敏感信息

## 依赖安全
- [ ] 定期更新依赖
- [ ] 扫描已知漏洞
```

---

### 14. **环境变量管理** ✅ 推荐

```bash
# .env.example (提交到 Git)
# DeepSeek API
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com

# Sorftime API
SORFTIME_API_KEY=your_sorftime_api_key_here

# 数据库
POSTGRES_USER=sorftime
POSTGRES_PASSWORD=change_me_in_production
POSTGRES_DB=sorftime

# JWT
SECRET_KEY=generate_with_openssl_rand_hex_32

# 其他配置
MAX_FILE_SIZE_MB=50
LOG_LEVEL=INFO
```

---

## 📊 监控和日志 (1 小时)

### 15. **日志规范** ✅ 推荐

```python
# 日志级别使用规范
logger.debug("调试信息")      # 开发环境
logger.info("正常流程")       # 关键流程
logger.warning("警告信息")    # 潜在问题
logger.error("错误信息")      # 需要处理的错误
logger.critical("严重错误")   # 系统级错误
```

---

### 16. **性能监控** 🔶 可选

```python
# 添加性能监控装饰器
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start
        
        if duration > 1.0:  # 超过 1 秒记录警告
            logger.warning(f"{func.__name__} took {duration:.2f}s")
        
        return result
    return wrapper
```

---

## 🎯 优先级建议

### 立即执行 (今天完成)
1. ✅ **创建代码模板** - 30 分钟
2. ✅ **完善测试框架** - 30 分钟
3. ✅ **建立开发规范** - 30 分钟
4. ✅ **配置开发工具** - 30 分钟

**总计**: 2 小时

---

### 本周完成
1. ✅ **API 文档完善** - 1 小时
2. ✅ **部署文档** - 1 小时
3. ✅ **安全检查** - 1 小时
4. 🔶 **前端组件库** - 2 小时

**总计**: 5 小时

---

### 下周完成
1. 🔶 **拆分大文件** - 2-3 小时
2. 🔶 **修复 ESLint** - 2-3 小时
3. 🔶 **性能监控** - 1-2 小时

**总计**: 5-8 小时

---

## 📋 检查清单

### 开发环境
- [x] Docker 环境正常
- [x] 测试通过率 92.4%
- [x] Git 历史干净
- [ ] Pre-commit hooks 配置
- [ ] VS Code 配置优化

### 代码质量
- [x] 后端测试覆盖率 92.4%
- [ ] 前端 ESLint 错误修复
- [ ] 代码模板建立
- [ ] 开发规范文档

### 文档
- [x] README.md 完整
- [x] API 文档 (FastAPI 自动生成)
- [ ] 部署文档完善
- [ ] 开发规范文档

### 安全
- [x] JWT 认证
- [x] CORS 配置
- [ ] 安全检查清单
- [ ] 环境变量示例

---

## 🚀 准备就绪标准

当以下条件满足时,即可开始新功能开发:

✅ **必需条件** (已满足):
- [x] 测试通过率 > 90%
- [x] 项目结构清晰
- [x] 基础文档完整
- [x] 开发环境稳定

🔶 **推荐条件** (部分满足):
- [ ] 代码模板建立
- [ ] 开发规范文档
- [ ] Pre-commit hooks
- [ ] 前端组件库

---

**结论**: 
- 核心条件已满足,可以开始开发
- 建议先完成"立即执行"清单 (2 小时)
- 然后开始新功能开发
- 在迭代中逐步完成其他准备工作
