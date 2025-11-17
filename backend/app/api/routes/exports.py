from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.errors import AppError
from app.api.deps import get_db
from app.schemas.exports import ExportJobOut, ExportRequest
# 为便于测试替换，导入模块而不是对象
from app.services import export_service as service_module

router = APIRouter(prefix="/exports", tags=["exports"])


@router.post("", response_model=ExportJobOut, status_code=202)
async def create_export(payload: ExportRequest, db: Session = Depends(get_db)):
    try:
        job = service_module.export_service.create_job(
            db,
            export_type=payload.export_type,
            filters=payload.filters,
            selected_fields=payload.selected_fields,
            file_format=payload.file_format,
        )
    except ValueError as exc:
        raise AppError(str(exc))
    return job


@router.get("/{job_id}", response_model=ExportJobOut)
async def get_export(job_id: str, db: Session = Depends(get_db)):
    job = service_module.export_service.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="导出任务不存在")
    return job


@router.get("/{job_id}/download")
async def download_export(job_id: str, db: Session = Depends(get_db)):
    job = service_module.export_service.get_job(db, job_id)
    if not job or not job.file_path:
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(job.file_path, filename=f"export-{job_id}.{job.file_format}")
