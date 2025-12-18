from __future__ import annotations

import io
import logging
from typing import Any

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.import_service import ImportService
from app.services.mcp_service import mcp_service

router = APIRouter(prefix="/api/mcp", tags=["mcp"])
logger = logging.getLogger(__name__)


class McpFetchRequest(BaseModel):
    input: str
    type: str = "auto"  # asin、url、keyword、auto


class McpFetchResponse(BaseModel):
    status: str
    message: str
    count: int
    data: list[dict[str, Any]]


@router.post("/fetch", response_model=McpFetchResponse)
async def fetch_mcp_data(
    request: McpFetchRequest,
    db: Session = Depends(get_db),
):
    """
    从 Sorftime MCP 拉取数据并导入到系统中。
    """
    try:
        items = await mcp_service.fetch_category_data(request.input, request.type)

        if not items:
            return McpFetchResponse(
                status="warning",
                message="未获取到数据",
                count=0,
                data=[],
            )

        # 转为 DataFrame 以复用导入逻辑
        df = pd.DataFrame(items)

        # 内存中生成 CSV，复用 ImportService 的 handle_upload
        csv_buffer = io.BytesIO()
        df.to_csv(csv_buffer, index=False, encoding="utf-8")
        csv_buffer.seek(0)

        upload_file = UploadFile(filename=f"mcp_import_{request.input}.csv", file=csv_buffer)

        import_service = ImportService()
        batch = import_service.handle_upload(
            db=db,
            file=upload_file,
            import_strategy="append",
            created_by=None,
        )

        return McpFetchResponse(
            status="success",
            message=f"拉取并导入成功，共 {len(items)} 条；导入批次 ID：{batch.id}",
            count=len(items),
            data=items,
        )

    except Exception as exc:  # noqa: BLE001 - 统一返回 500，避免泄露内部栈信息
        logger.exception("MCP 拉取/导入失败")
        raise HTTPException(status_code=500, detail=f"MCP 拉取/导入失败：{exc}") from exc
