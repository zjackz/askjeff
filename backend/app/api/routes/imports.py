from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.errors import AppError
from app.schemas.imports import ImportBatchOut, ImportDetailResponse, ImportListResponse
from app.services.import_repository import ImportRepository
from app.services.import_service import import_service

router = APIRouter(prefix="/imports", tags=["imports"])


@router.post("", response_model=ImportBatchOut, status_code=201)
async def create_import(
    file: UploadFile,
    importStrategy: str = Form(...),
    db: Session = Depends(get_db),
):
    if importStrategy not in {"overwrite", "append", "update_only"}:
        raise AppError("不支持的导入策略")
    if file.filename is None:
        raise AppError("文件名不能为空")
    batch = import_service.handle_upload(
        db,
        file=file,
        import_strategy=importStrategy,
    )
    return batch


@router.get("", response_model=ImportListResponse)
async def list_imports(status: str | None = None, db: Session = Depends(get_db)):
    batches = ImportRepository.list_batches(db, status=status)
    return {"items": batches}


@router.get("/{batch_id}", response_model=ImportDetailResponse)
async def get_import_detail(batch_id: str, db: Session = Depends(get_db)):
    batch = ImportRepository.get_batch(db, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")
    return {"batch": batch, "failure_summary": batch.failure_summary}
