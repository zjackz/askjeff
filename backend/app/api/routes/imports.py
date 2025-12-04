from __future__ import annotations


from fastapi import APIRouter, BackgroundTasks, Body, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.errors import AppError
from app.db import SessionLocal
from app.schemas.imports import ImportBatchOut, ImportDetailResponse, ImportListResponse
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
            created_by=None,
        )
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
    limit: int = Query(default=5, le=100),
    offset: int = Query(default=0),
    db: Session = Depends(get_db)
):
    """Get records for a batch (preview)."""
    from app.models.import_batch import ProductRecord
    records = (
        db.query(ProductRecord)
        .filter(ProductRecord.batch_id == batch_id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    return records


async def run_batch_extraction_background(batch_id: int, target_fields: list[str]):
    with SessionLocal() as db:
        service = ExtractionService(db, DeepseekClient())
        await service.extract_batch_features(batch_id, target_fields)


@router.post("/{batch_id}/extract")
async def extract_batch_features(
    batch_id: int,
    background_tasks: BackgroundTasks,
    target_fields: list[str] = Body(..., embed=True),
    db: Session = Depends(get_db),
):
    """Start AI feature extraction for a batch."""
    batch = ImportRepository.get_batch(db, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    background_tasks.add_task(run_batch_extraction_background, batch_id, target_fields)
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
