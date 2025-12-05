from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer
from pydantic import AliasChoices


class ExportRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    export_type: str = Field(..., alias="exportType")
    filters: dict[str, Any] | None = None
    selected_fields: list[str] = Field(default=[], alias="selectedFields")
    file_format: str = Field("csv", alias="fileFormat")


class ExportJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    export_type: str = Field(
        ..., alias="exportType", validation_alias=AliasChoices("export_type", "exportType")
    )
    status: str
    file_format: str = Field(
        ..., alias="fileFormat", validation_alias=AliasChoices("file_format", "fileFormat")
    )
    filters: dict | None
    selected_fields: list[str] = Field(
        ..., alias="selectedFields", validation_alias=AliasChoices("selected_fields", "selectedFields")
    )
    file_url: str | None = Field(
        default=None, alias="fileUrl", validation_alias=AliasChoices("file_path", "fileUrl")
    )
    triggered_by: str | None = None
    started_at: datetime | None = Field(default=None, alias="startedAt")
    finished_at: datetime | None = Field(default=None, alias="finishedAt")
    error_message: str | None = Field(
        default=None, alias="errorMessage", validation_alias=AliasChoices("error_message", "errorMessage")
    )

    @field_serializer("export_type")
    def _serialize_export_type(self, value: str) -> str:
        return value.replace("_", "-")

    @field_serializer("file_url")
    def _serialize_file_url(self, value: str | None) -> str | None:
        if not value:
            return None
        return f"/exports/{self.id}/download"
