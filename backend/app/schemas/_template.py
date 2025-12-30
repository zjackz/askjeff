"""
新 Schema 模板

使用方法:
1. 复制此文件到 backend/app/schemas/
2. 重命名为 your_schema.py
3. 替换 Template 为你的模型名
4. 定义具体字段
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class TemplateBase(BaseModel):
    """模板基础模型"""
    param1: str = Field(..., description="参数1说明", min_length=1, max_length=100)
    param2: Optional[str] = Field(None, description="参数2说明", max_length=200)


class TemplateRequest(TemplateBase):
    """模板请求模型"""
    pass


class TemplateResponse(TemplateBase):
    """模板响应模型"""
    id: str = Field(..., description="模板 ID")
    status: str = Field(..., description="状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    """模板列表响应"""
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="每页数量")
    items: List[TemplateResponse] = Field(..., description="模板列表")


class TemplateUpdate(BaseModel):
    """模板更新模型"""
    param1: Optional[str] = Field(None, description="参数1")
    param2: Optional[str] = Field(None, description="参数2")
    
    @validator('param1')
    def validate_param1(cls, v):
        """验证 param1"""
        if v is not None and len(v) == 0:
            raise ValueError("param1 不能为空字符串")
        return v
