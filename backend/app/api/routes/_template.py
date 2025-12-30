"""
新路由模板

使用方法:
1. 复制此文件到 backend/app/api/routes/
2. 重命名为 your_route.py
3. 替换 template 为你的路由名
4. 在 main.py 中注册路由
"""
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.template import TemplateRequest, TemplateResponse, TemplateListResponse
from app.services.template_service import template_service

router = APIRouter()


@router.post("/template", response_model=TemplateResponse, status_code=201)
async def create_template(
    request: TemplateRequest,
    db: Annotated[Session, Depends(deps.get_db)],
    current_user: Annotated[dict, Depends(deps.get_current_user)]
) -> TemplateResponse:
    """
    创建模板
    
    - **param1**: 参数1说明 (必需)
    - **param2**: 参数2说明 (可选)
    
    Returns:
        创建的模板信息
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


@router.get("/template/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    db: Annotated[Session, Depends(deps.get_db)],
    current_user: Annotated[dict, Depends(deps.get_current_user)]
) -> TemplateResponse:
    """
    获取模板详情
    
    - **template_id**: 模板 ID
    """
    # 实现获取逻辑
    pass


@router.get("/template", response_model=TemplateListResponse)
async def list_templates(
    db: Annotated[Session, Depends(deps.get_db)],
    current_user: Annotated[dict, Depends(deps.get_current_user)],
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量")
) -> TemplateListResponse:
    """
    获取模板列表
    
    - **page**: 页码 (默认 1)
    - **page_size**: 每页数量 (默认 50, 最大 200)
    """
    # 实现列表查询逻辑
    pass


@router.put("/template/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    request: TemplateRequest,
    db: Annotated[Session, Depends(deps.get_db)],
    current_user: Annotated[dict, Depends(deps.get_current_user)]
) -> TemplateResponse:
    """
    更新模板
    
    - **template_id**: 模板 ID
    - **request**: 更新内容
    """
    # 实现更新逻辑
    pass


@router.delete("/template/{template_id}")
async def delete_template(
    template_id: str,
    db: Annotated[Session, Depends(deps.get_db)],
    current_user: Annotated[dict, Depends(deps.get_current_user)]
) -> dict:
    """
    删除模板
    
    - **template_id**: 模板 ID
    """
    # 实现删除逻辑
    return {"message": "删除成功"}
