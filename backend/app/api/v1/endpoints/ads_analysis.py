from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.api.deps import get_current_user
from app.services.ads_analysis_service import AdsAnalysisService
from app.services.ads_import_service import ads_import_service
from app.schemas.amazon_ads import AdsMatrixPoint, AdsDiagnosis, AmazonStoreSchema

router = APIRouter()

@router.post("/import/costs")
async def import_costs(
    store_id: UUID = Query(...),
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user)
):
    """导入产品成本 CSV"""
    return await ads_import_service.import_product_costs(db, store_id, file)

@router.post("/import/ads-report")
async def import_ads_report(
    store_id: UUID = Query(...),
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user)
):
    """导入广告报表 CSV"""
    return await ads_import_service.import_ads_report(db, store_id, file)

@router.get("/stores", response_model=List[AmazonStoreSchema])
def get_user_stores(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的所有店铺列表
    """
    stores = AdsAnalysisService.get_user_stores(db, current_user.id)
    return stores

@router.get("/overview")
def get_ads_overview(
    store_id: UUID = Query(..., description="店铺 ID"),
    days: int = Query(30, ge=7, le=90),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取广告分析概览数据
    """
    return AdsAnalysisService.get_overview_data(
        db=db,
        store_id=store_id,
        user_id=current_user.id,
        days=days
    )

@router.get("/matrix", response_model=List[AdsMatrixPoint])
def get_ads_matrix(
    store_id: UUID = Query(..., description="店铺 ID"),
    days: int = Query(30, ge=7, le=90, description="统计天数 (7-90)"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取广告诊断矩阵数据
    
    返回所有 SKU 的库存周转和 TACOS 数据，用于四象限可视化
    """
    return AdsAnalysisService.get_matrix_data(
        db=db,
        store_id=store_id,
        user_id=current_user.id,
        days=days
    )

@router.get("/{sku}/diagnosis", response_model=AdsDiagnosis)
async def get_sku_diagnosis(
    sku: str,
    store_id: UUID = Query(..., description="店铺 ID"),
    days: int = Query(30, ge=7, le=90),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取单个 SKU 的诊断建议
    """
    # 获取矩阵数据
    matrix_data = AdsAnalysisService.get_matrix_data(
        db=db,
        store_id=store_id,
        user_id=current_user.id,
        days=days
    )
    
    # 查找目标 SKU
    sku_data = next((item for item in matrix_data if item.sku == sku), None)
    
    if not sku_data:
        raise HTTPException(status_code=404, detail=f"SKU {sku} not found")
    
    # 生成诊断 (异步调用 AI)
    from app.services.ads_ai_service import ads_ai_service
    
    metrics_dict = {
        "stock_weeks": sku_data.stock_weeks,
        "tacos": sku_data.tacos,
        "sales": sku_data.sales,
        "ad_spend": sku_data.ad_spend,
        "ctr": sku_data.ctr,
        "cvr": sku_data.cvr,
        "acos": sku_data.acos,
        "roas": sku_data.roas,
        "margin": sku_data.margin
    }
    
    diagnosis_text = await ads_ai_service.generate_sku_diagnosis(sku, metrics_dict)
    
    return AdsDiagnosis(
        sku=sku,
        asin=sku_data.asin,
        status=sku_data.status,
        diagnosis=diagnosis_text,
        metrics={
            "stock_weeks": sku_data.stock_weeks,
            "tacos": sku_data.tacos,
            "sales": sku_data.sales,
            "ad_spend": sku_data.ad_spend,
            "ctr": sku_data.ctr,
            "cvr": sku_data.cvr,
            "acos": sku_data.acos,
            "roas": sku_data.roas,
            "margin": sku_data.margin
        }
    )
