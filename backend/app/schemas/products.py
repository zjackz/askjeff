from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class ProductOut(BaseModel):
    """产品记录输出契约。"""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    batch_id: int = Field(..., alias="batchId")
    batch_sequence_id: int | None = Field(default=None, alias="batchSequenceId")
    asin: str
    title: str
    category: str | None = None
    price: float | None = None
    currency: str | None = None
    sales_rank: int | None = Field(default=None, alias="salesRank")
    rating: float | None = None
    reviews: int | None = None
    ingested_at: datetime = Field(..., alias="ingestedAt")
    raw_payload: dict[str, Any] | None = Field(default=None, alias="rawPayload")
    normalized_payload: dict[str, Any] | None = Field(default=None, alias="attributes")
    validation_status: str = Field(..., alias="validationStatus")
    validation_messages: dict[str, Any] | None = Field(default=None, alias="validationMessages")
    ai_status: str | None = Field(default=None, alias="aiStatus")
    ai_features: dict[str, Any] | None = Field(default=None, alias="aiFeatures")

    @field_serializer("price", "rating")
    def _serialize_decimal(self, value: float | None) -> float | None:
        return float(value) if value is not None else None


class ProductListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[ProductOut]
    total: int
