# 技术实施计划：API 批量导入功能

**需求编号**: 008  
**预估工时**: 12 小时  
**实施周期**: 2-3 天

---

## 技术栈

### 后端
- **框架**: FastAPI
- **数据源**: Sorftime API
- **数据库**: PostgreSQL (复用 ImportBatch, ProductRecord)
- **异步**: asyncio, httpx
- **Excel**: pandas, openpyxl
- **实时通信**: WebSocket

### 前端
- **框架**: Vue 3 + TypeScript
- **UI**: Element Plus
- **实时通信**: WebSocket
- **HTTP**: axios

---

## 目录结构

```
backend/app/
├── services/
│   └── api_import_service.py          # API 导入服务（新建）
├── api/v1/endpoints/
│   └── api_imports.py                  # API 端点（新建）
├── schemas/
│   └── api_imports.py                  # Pydantic Schemas（新建）
└── models/
    └── import_batch.py                 # 扩展现有模型

frontend/src/
├── views/imports/
│   └── APIImport.vue                   # API 导入页面（新建）
├── api/
│   └── apiImports.ts                   # API 客户端（新建）
└── types/
    └── apiImports.ts                   # TypeScript 类型（新建）
```

---

## 详细设计

### 1. 后端服务层

#### APIImportService

**文件**: `backend/app/services/api_import_service.py`

```python
from typing import Dict, Any, List, Optional
from datetime import datetime
import re
import asyncio
import pandas as pd
from sqlalchemy.orm import Session

from app.services.sorftime import SorftimeClient
from app.models.import_batch import ImportBatch, ProductRecord
from app.core.config import settings

class APIImportService:
    """API 批量导入服务"""
    
    def __init__(self, db: Session, sorftime: SorftimeClient):
        self.db = db
        self.sorftime = sorftime
    
    async def import_from_input(
        self,
        input_value: str,
        domain: int = 1,
        batch_size: int = 10
    ) -> str:
        """
        从输入启动导入流程
        
        Args:
            input_value: 用户输入（ASIN/类目ID/URL）
            domain: 站点代码
            batch_size: 每批处理数量
        
        Returns:
            batch_id: 导入批次 ID
        """
        # 1. 解析输入
        parsed = self._parse_input(input_value)
        
        # 2. 创建导入批次
        batch = ImportBatch(
            filename=f"api_import_{parsed['value']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx",
            source_type="api",
            status="processing",
            metadata={
                "input_type": parsed["type"],
                "input_value": input_value,
                "domain": domain,
                "start_time": datetime.utcnow().isoformat()
            }
        )
        self.db.add(batch)
        self.db.commit()
        
        # 3. 异步处理
        asyncio.create_task(self._process_import(batch.id, parsed, domain, batch_size))
        
        return str(batch.id)
    
    async def _process_import(
        self,
        batch_id: str,
        parsed: dict,
        domain: int,
        batch_size: int
    ):
        """异步处理导入流程"""
        try:
            # 1. 获取 Best Sellers
            await self._update_progress(batch_id, "fetching_bestsellers", 0)
            bestsellers = await self._fetch_bestsellers(parsed, domain)
            
            # 2. 提取 ASIN 列表
            asins = [p.get('asin') or p.get('ASIN') for p in bestsellers if p.get('asin') or p.get('ASIN')]
            
            # 3. 批量获取详情
            await self._update_progress(batch_id, "fetching_details", 0)
            products = await self._fetch_details_batch(asins, domain, batch_id, batch_size)
            
            # 4. 保存到数据库
            await self._update_progress(batch_id, "saving_data", 80)
            await self._save_to_database(batch_id, products)
            
            # 5. 生成 Excel
            await self._update_progress(batch_id, "generating_excel", 90)
            filepath = await self._generate_excel(batch_id, products)
            
            # 6. 更新批次状态
            batch = self.db.query(ImportBatch).filter(ImportBatch.id == batch_id).first()
            batch.status = "completed"
            batch.file_path = filepath
            batch.total_rows = len(products)
            batch.processed_rows = len(products)
            self.db.commit()
            
            await self._update_progress(batch_id, "completed", 100)
            
        except Exception as e:
            # 错误处理
            batch = self.db.query(ImportBatch).filter(ImportBatch.id == batch_id).first()
            batch.status = "failed"
            batch.error_message = str(e)
            self.db.commit()
            
            await self._update_progress(batch_id, "failed", 0, str(e))
    
    def _parse_input(self, input_value: str) -> dict:
        """解析输入"""
        input_value = input_value.strip()
        
        # ASIN: B + 9 位字母数字
        if re.match(r'^B[A-Z0-9]{9}$', input_value, re.IGNORECASE):
            return {"type": "asin", "value": input_value.upper()}
        
        # 类目 ID: 纯数字
        if input_value.isdigit():
            return {"type": "category_id", "value": input_value}
        
        # URL: 提取 ASIN 或 Node ID
        if 'amazon.com' in input_value or 'amazon.' in input_value:
            # 提取 ASIN
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', input_value)
            if asin_match:
                return {"type": "asin", "value": asin_match.group(1)}
            
            # 提取 Node ID
            node_match = re.search(r'node=(\d+)', input_value)
            if node_match:
                return {"type": "category_id", "value": node_match.group(1)}
        
        raise ValueError(f"无法识别的输入格式: {input_value}")
    
    async def _fetch_bestsellers(self, parsed: dict, domain: int) -> list:
        """获取 Best Sellers"""
        if parsed["type"] == "category_id":
            response = await self.sorftime.category_request(
                node_id=parsed["value"],
                domain=domain
            )
            if response.code == 0:
                return response.data or []
        
        elif parsed["type"] == "asin":
            # 从 ASIN 获取类目，然后获取 Best Sellers
            product_response = await self.sorftime.product_request(
                asin=parsed["value"],
                domain=domain
            )
            if product_response.code == 0:
                # 提取类目 ID
                category = product_response.data.get('category', [])
                if category:
                    # 使用第一个类目
                    # TODO: 需要从 CategoryTree 获取 Node ID
                    pass
        
        return []
    
    async def _fetch_details_batch(
        self,
        asins: list,
        domain: int,
        batch_id: str,
        batch_size: int
    ) -> list:
        """批量获取产品详情"""
        results = []
        batches = [asins[i:i+batch_size] for i in range(0, len(asins), batch_size)]
        
        for i, batch in enumerate(batches):
            # 调用 API
            asin_str = ','.join(batch)
            response = await self.sorftime.product_request(
                asin=asin_str,
                trend=0,
                domain=domain
            )
            
            if response.code == 0:
                if isinstance(response.data, list):
                    results.extend(response.data)
                else:
                    results.append(response.data)
            
            # 更新进度
            progress = int((i + 1) / len(batches) * 70) + 10  # 10-80%
            await self._update_progress(
                batch_id,
                "fetching_details",
                progress,
                f"正在获取产品详情 ({(i+1)*batch_size}/{len(asins)})"
            )
            
            # 延迟（避免限流）
            if i < len(batches) - 1:
                await asyncio.sleep(1)
        
        return results
    
    async def _save_to_database(self, batch_id: str, products: list):
        """保存到数据库"""
        for product in products:
            record = ProductRecord(
                batch_id=batch_id,
                asin=product.get('asin'),
                title=product.get('title'),
                price=product.get('price'),
                ratings=product.get('ratings'),
                reviews_count=product.get('ratingsCount'),
                raw_data=product,
                status="pending"
            )
            self.db.add(record)
        
        self.db.commit()
    
    async def _generate_excel(self, batch_id: str, products: list) -> str:
        """生成 Excel 文件"""
        df = pd.DataFrame([{
            'ASIN': p.get('asin'),
            'Title': p.get('title'),
            'Price': p.get('price'),
            'Rating': p.get('ratings'),
            'Reviews': p.get('ratingsCount'),
            'Category': p.get('category', [''])[0] if p.get('category') else '',
            'Brand': p.get('brand'),
            'Sales': p.get('listingSalesVolumeOfMonth'),
        } for p in products])
        
        batch = self.db.query(ImportBatch).filter(ImportBatch.id == batch_id).first()
        filepath = f"uploads/api_imports/{batch.filename}"
        
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        df.to_excel(filepath, index=False)
        
        return filepath
    
    async def _update_progress(
        self,
        batch_id: str,
        stage: str,
        progress: int,
        message: str = ""
    ):
        """更新进度（通过 WebSocket）"""
        # TODO: 实现 WebSocket 推送
        pass
```

---

### 2. API 端点

**文件**: `backend/app/api/v1/endpoints/api_imports.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.api_imports import APIImportRequest, APIImportResponse, APIImportStatus
from app.services.api_import_service import APIImportService
from app.services.sorftime import SorftimeClient
from app.db import get_db

router = APIRouter()

@router.post("/from-api", response_model=APIImportResponse)
async def create_api_import(
    request: APIImportRequest,
    db: Session = Depends(get_db),
    sorftime: SorftimeClient = Depends(get_sorftime_client)
):
    """
    从 API 创建导入任务
    """
    service = APIImportService(db, sorftime)
    
    try:
        batch_id = await service.import_from_input(
            input_value=request.input,
            domain=request.domain
        )
        
        return APIImportResponse(
            batch_id=batch_id,
            status="started",
            estimated_time=120
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/from-api/{batch_id}/status", response_model=APIImportStatus)
async def get_import_status(
    batch_id: str,
    db: Session = Depends(get_db)
):
    """
    获取导入状态
    """
    batch = db.query(ImportBatch).filter(ImportBatch.id == batch_id).first()
    
    if not batch:
        raise HTTPException(status_code=404, detail="导入批次不存在")
    
    return APIImportStatus(
        batch_id=str(batch.id),
        status=batch.status,
        progress=int((batch.processed_rows / batch.total_rows * 100) if batch.total_rows else 0),
        message=batch.metadata.get("current_message", "")
    )
```

---

### 3. Pydantic Schemas

**文件**: `backend/app/schemas/api_imports.py`

```python
from pydantic import BaseModel, Field
from typing import Optional

class APIImportRequest(BaseModel):
    """API 导入请求"""
    input: str = Field(..., description="ASIN、类目ID或URL")
    domain: int = Field(default=1, description="站点代码", ge=1, le=14)

class APIImportResponse(BaseModel):
    """API 导入响应"""
    batch_id: str
    status: str
    estimated_time: int  # 秒

class APIImportStatus(BaseModel):
    """API 导入状态"""
    batch_id: str
    status: str
    progress: int  # 0-100
    stage: Optional[str] = None
    message: Optional[str] = None
```

---

### 4. 前端实现

**文件**: `frontend/src/views/imports/APIImport.vue`

```vue
<template>
  <div class="api-import">
    <el-card>
      <template #header>
        <h2>📥 API 批量导入</h2>
      </template>
      
      <el-form :model="form" label-width="120px">
        <el-form-item label="输入">
          <el-input
            v-model="form.input"
            placeholder="输入 ASIN、类目 ID 或链接"
            clearable
          />
          <div class="input-hint">
            支持: ASIN (B08N5WRWNW), 类目ID (172282), 或亚马逊链接
          </div>
        </el-form-item>
        
        <el-form-item label="站点">
          <el-select v-model="form.domain">
            <el-option label="美国" :value="1" />
            <el-option label="英国" :value="2" />
            <el-option label="德国" :value="3" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            :loading="importing"
            @click="startImport"
          >
            🚀 开始导入
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card v-if="batchId" class="progress-card">
      <template #header>
        <h3>📊 导入进度</h3>
      </template>
      
      <el-steps :active="currentStep" finish-status="success">
        <el-step title="解析输入" />
        <el-step title="获取 Best Sellers" />
        <el-step title="获取产品详情" />
        <el-step title="保存数据" />
        <el-step title="生成 Excel" />
        <el-step title="完成" />
      </el-steps>
      
      <el-progress
        :percentage="progress"
        :status="progressStatus"
        class="progress-bar"
      />
      
      <div class="progress-message">{{ progressMessage }}</div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { createAPIImport, getAPIImportStatus } from '@/api/apiImports'
import { ElMessage } from 'element-plus'

const form = ref({
  input: '',
  domain: 1
})

const importing = ref(false)
const batchId = ref('')
const progress = ref(0)
const currentStep = ref(0)
const progressMessage = ref('')
const progressStatus = ref<'success' | 'exception' | ''>('')

const startImport = async () => {
  if (!form.value.input) {
    ElMessage.warning('请输入 ASIN、类目 ID 或链接')
    return
  }
  
  importing.value = true
  
  try {
    const response = await createAPIImport(form.value)
    batchId.value = response.batch_id
    
    // 开始轮询状态
    pollStatus()
  } catch (error: any) {
    ElMessage.error(error.message || '导入失败')
    importing.value = false
  }
}

const pollStatus = async () => {
  const timer = setInterval(async () => {
    try {
      const status = await getAPIImportStatus(batchId.value)
      
      progress.value = status.progress
      progressMessage.value = status.message || ''
      
      // 更新步骤
      if (status.stage === 'fetching_bestsellers') currentStep.value = 1
      else if (status.stage === 'fetching_details') currentStep.value = 2
      else if (status.stage === 'saving_data') currentStep.value = 3
      else if (status.stage === 'generating_excel') currentStep.value = 4
      else if (status.stage === 'completed') currentStep.value = 5
      
      if (status.status === 'completed') {
        clearInterval(timer)
        importing.value = false
        progressStatus.value = 'success'
        ElMessage.success('导入完成！')
      } else if (status.status === 'failed') {
        clearInterval(timer)
        importing.value = false
        progressStatus.value = 'exception'
        ElMessage.error('导入失败')
      }
    } catch (error) {
      clearInterval(timer)
      importing.value = false
    }
  }, 2000)  // 每 2 秒轮询一次
}
</script>
```

---

## 实施步骤

### Day 1: 后端核心 (6h)

1. 创建 APIImportService (3h)
2. 创建 API 端点 (2h)
3. 测试基本流程 (1h)

### Day 2: 前端和优化 (4h)

1. 创建前端页面 (3h)
2. 集成和测试 (1h)

### Day 3: 完善和部署 (2h)

1. 错误处理优化 (1h)
2. 文档和部署 (1h)

---

**文档版本**: 1.0  
**最后更新**: 2025-12-17  
**作者**: AI Assistant
