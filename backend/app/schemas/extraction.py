from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ExtractionItemBase(BaseModel):
    original_data: Dict[str, Any]
    extracted_data: Optional[Dict[str, Any]] = None
    status: str
    error_message: Optional[str] = None


class ExtractionItemResponse(ExtractionItemBase):
    id: UUID
    task_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExtractionTaskBase(BaseModel):
    filename: str
    target_fields: List[str]


class ExtractionTaskCreate(ExtractionTaskBase):
    pass


class ExtractionTaskResponse(ExtractionTaskBase):
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    columns: List[str] = []

    model_config = ConfigDict(from_attributes=True)
