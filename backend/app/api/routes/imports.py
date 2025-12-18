from __future__ import annotations


from fastapi import APIRouter, BackgroundTasks, Body, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.errors import AppError
from app.db import SessionLocal
from app.schemas.imports import ImportBatchOut, ImportDetailResponse, ImportListResponse
from app.services.api_import_service import api_import_service
from app.services.deepseek_client import DeepseekClient
from app.services.extraction_service import ExtractionService
from app.services.import_repository import ImportRepository
from app.services.import_service import import_service

router = APIRouter(prefix="/api/imports", tags=["imports"])


@router.post("", response_model=ImportBatchOut, status_code=201)
async def create_import(
    file: UploadFile = File(...),
    importStrategy: str = Form(...),
    sheetName: str | None = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
):
    """
    上传并导入 CSV/XLSX 文件
    """
    from app.config import settings
    from app.core.errors import ValidationException, ErrorCode
    
    # 1. 文件格式验证
    if not file.filename:
        raise ValidationException(
            code=ErrorCode.INVALID_FILE_FORMAT,
            message="文件名不能为空"
        )
    
    valid_extensions = ('.csv', '.xlsx', '.xls')
    if not file.filename.lower().endswith(valid_extensions):
        raise ValidationException(
            code=ErrorCode.INVALID_FILE_FORMAT,
            details={"filename": file.filename, "valid_extensions": list(valid_extensions)}
        )
    
    # 2. 文件大小验证
    file.file.seek(0, 2)  # 移动到文件末尾
    file_size = file.file.tell()
    file.file.seek(0)  # 重置到开头
    
    max_size = settings.max_file_size_mb * 1024 * 1024
    if file_size > max_size:
        raise ValidationException(
            code=ErrorCode.FILE_TOO_LARGE,
            message=f"文件大小超过 {settings.max_file_size_mb}MB 限制",
            details={"file_size_mb": round(file_size / 1024 / 1024, 2), "max_size_mb": settings.max_file_size_mb}
        )
    
    # 3. 执行导入
    try:
        normalized_strategy = import_service.normalize_strategy(importStrategy)
    except ValueError as exc:
        raise AppError(str(exc))
    
    # 使用默认值
    onMissingRequired = "skip"
    columnAliases = None
    
    try:
        batch = import_service.handle_upload(
            db,
            file=file,
            import_strategy=normalized_strategy,
            sheet_name=sheetName,
            on_missing_required=onMissingRequired,
            column_aliases=columnAliases,
        )
        # Trigger automatic translation
        background_tasks.add_task(run_batch_translation_background, batch.id)
    except ValueError as exc:
        raise AppError(str(exc))
    return batch


@router.get("", response_model=ImportListResponse)
async def list_imports(
    status: str | None = Query(default=None),
    asin: str | None = Query(default=None),
    page: int = Query(default=1, alias="page", ge=1),
    page_size: int = Query(default=20, alias="pageSize", ge=1, le=200),
    db: Session = Depends(get_db),
):
    items, total = ImportRepository.list_batches_with_filters(
        db,
        status=status,
        asin=asin,
        page=page,
        page_size=page_size,
    )
    return {"items": items, "total": total}


@router.get("/{batch_id}", response_model=ImportDetailResponse)
def get_import_detail(
    batch_id: int,
    db: Session = Depends(get_db),
):
    batch = ImportRepository.get_batch(db, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")
    failure_items = (batch.failure_summary.get("items") or []) if batch.failure_summary else []
    return {"batch": batch, "failed_rows": failure_items}


@router.get("/{batch_id}/records")
async def get_batch_records(
    batch_id: int,
    limit: int = Query(default=100, le=10000),
    offset: int = Query(default=0),
    db: Session = Depends(get_db)
):
    """Get records for a batch (preview or full data)."""
    from app.models.import_batch import ProductRecord
    records = (
        db.query(ProductRecord)
        .filter(ProductRecord.batch_id == batch_id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    return records


async def run_batch_extraction_background(
    batch_id: int, 
    target_fields: list[str],
    custom_instructions: str | None = None,
    test_mode: bool = False
):
    with SessionLocal() as db:
        service = ExtractionService(db, DeepseekClient())
        await service.extract_batch_features(
            batch_id, 
            target_fields, 
            custom_instructions=custom_instructions,
            test_mode=test_mode
        )


async def run_batch_translation_background(batch_id: int):
    with SessionLocal() as db:
        service = ExtractionService(db, DeepseekClient())
        await service.auto_translate_batch(batch_id)


@router.post("/{batch_id}/extract")
async def extract_batch_features(
    batch_id: int,
    background_tasks: BackgroundTasks,
    target_fields: list[str] = Body(..., embed=True),
    custom_instructions: str | None = Body(None, embed=True),
    test_mode: bool = Body(False, embed=True),
    db: Session = Depends(get_db),
):
    """Start AI feature extraction for a batch."""
    batch = ImportRepository.get_batch(db, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    background_tasks.add_task(
        run_batch_extraction_background, 
        batch_id, 
        target_fields,
        custom_instructions,
        test_mode
    )
    return {"message": "Extraction started", "batch_id": batch_id}
@router.get("/{id}/runs")
def list_extraction_runs(
    id: int,
    db: Session = Depends(get_db)
):
    from app.models.extraction_run import ExtractionRun
    
    runs = (
        db.query(ExtractionRun)
        .filter(ExtractionRun.batch_id == id)
        .order_by(ExtractionRun.created_at.desc())
        .all()
    )
    return {"items": runs}


async def run_api_import_task(
    input_value: str,
    input_type: str | None,
    domain: int,
    test_mode: bool,
    limit: int,
    batch_id: int | None = None,
    created_by: str | None = None,
):
    """后台运行 API 导入任务"""
    from app.db import SessionLocal
    with SessionLocal() as db:
        try:
            await api_import_service.import_from_input(
                db=db,
                input_value=input_value,
                input_type=input_type,
                domain=domain,
                created_by=created_by,
                test_mode=test_mode,
                limit=limit,
                batch_id=batch_id,
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Background API import failed: {e}")


@router.post("/from-api", status_code=201)
async def import_from_api(
    background_tasks: BackgroundTasks,
    input: str = Body(..., embed=True),
    input_type: str | None = Body(None, embed=True),
    domain: int = Body(1, embed=True),
    test_mode: bool = Body(False, embed=True),
    limit: int = Body(100, embed=True),
    db: Session = Depends(get_db),
):
    """
    从 Sorftime API 批量导入产品数据 (后台执行)
    """
    if not input:
        raise HTTPException(status_code=400, detail="输入不能为空")
    
    try:
        # 1. 先解析输入并创建批次 (同步执行，为了立即返回 ID)
        # 我们需要一个轻量级的方法来创建批次
        from app.services.api_import_service import APIImportService
        
        # 临时解析以获取类目信息
        parsed = api_import_service._parse_input(input, input_type)
        
        # 如果是 ASIN 且不是测试模式，尝试同步获取类目 ID (为了文件名准确)
        # 但为了速度，如果获取失败也可以用默认名
        if parsed["type"] == "asin" and not parsed.get("category_id"):
             parsed["category_id"] = "pending"

        batch = api_import_service._create_batch(
            db=db,
            parsed=parsed,
            domain=domain,
            created_by=None, # TODO: 获取当前用户
            test_mode=test_mode
        )
        
        # 2. 启动后台任务执行完整的导入流程
        background_tasks.add_task(
            run_api_import_task,
            input_value=input,
            input_type=input_type,
            domain=domain,
            test_mode=test_mode,
            limit=limit,
            batch_id=batch.id
        )
        
        return {
            "batch_id": batch.id,
            "status": "pending",
            "message": "导入任务已提交到后台"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交任务失败: {str(e)}")


@router.post("/preview-api")
async def preview_api_import(
    input: str = Body(..., embed=True),
    domain: int = Body(1, embed=True),
    test_mode: bool = Body(False, embed=True),
    db: Session = Depends(get_db),
):
    """预览 API 导入内容"""
    try:
        result = await api_import_service.preview_input(input, domain, test_mode, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/from-api/{batch_id}/status")
async def get_api_import_status(
    batch_id: int,
    db: Session = Depends(get_db),
):
    """
    获取 API 导入状态
    
    Returns:
        {
            "batch_id": 123,
            "status": "processing",
            "progress": 45,
            "message": "正在获取产品详情 (45/100)"
        }
    """
    batch = ImportRepository.get_batch(db, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")
    
    return {
        "batch_id": batch.id,
        "status": batch.status,
        "total_rows": batch.total_rows,
        "success_rows": batch.success_rows,
        "failed_rows": batch.failed_rows,
        "import_metadata": batch.import_metadata,
    }
