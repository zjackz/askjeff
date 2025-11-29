from typing import List
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Body, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db import SessionLocal
from app.schemas.extraction import ExtractionTaskResponse
from app.services.deepseek_client import DeepseekClient
from app.services.extraction_service import ExtractionService

router = APIRouter(prefix="/api/extraction", tags=["extraction"])


def get_service(db: Session = Depends(get_db)) -> ExtractionService:
    return ExtractionService(db, DeepseekClient())


def run_extraction_background(task_id: UUID):
    with SessionLocal() as db:
        service = ExtractionService(db, DeepseekClient())
        service.run_extraction(task_id)


@router.post("/upload", response_model=ExtractionTaskResponse)
async def upload_file(
    file: UploadFile = File(...), service: ExtractionService = Depends(get_service)
):
    """Upload file and create task (PENDING)."""
    try:
        task = await service.create_task(file)
        response = ExtractionTaskResponse.model_validate(task)
        if task.items:
            response.columns = list(task.items[0].original_data.keys())
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{task_id}/start")
async def start_extraction(
    task_id: UUID,
    background_tasks: BackgroundTasks,
    target_fields: List[str] = Body(..., embed=True),
    service: ExtractionService = Depends(get_service),
):
    """Update target fields and start extraction in background."""
    try:
        service.update_task_fields(task_id, target_fields)
        background_tasks.add_task(run_extraction_background, task_id)
        return {"message": "Extraction started", "task_id": task_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{task_id}", response_model=ExtractionTaskResponse)
def get_task(task_id: UUID, service: ExtractionService = Depends(get_service)):
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    response = ExtractionTaskResponse.model_validate(task)
    if task.items:
        response.columns = list(task.items[0].original_data.keys())
    return response


@router.get("/{task_id}/export")
def export_task(task_id: UUID, service: ExtractionService = Depends(get_service)):
    try:
        output = service.export_task(task_id)
        filename = f"extraction_{task_id}.xlsx"
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
