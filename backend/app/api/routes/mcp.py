from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.services.mcp_service import mcp_service
from app.services.import_service import ImportService
from app.api.deps import get_db
from sqlalchemy.orm import Session
import pandas as pd
import logging

router = APIRouter(prefix="/api/mcp", tags=["mcp"])
logger = logging.getLogger(__name__)

class McpFetchRequest(BaseModel):
    input: str
    type: str = "auto" # asin, url, keyword, auto

class McpFetchResponse(BaseModel):
    status: str
    message: str
    count: int
    data: List[Dict[str, Any]]

@router.post("/fetch", response_model=McpFetchResponse)
async def fetch_mcp_data(
    request: McpFetchRequest,
    db: Session = Depends(get_db)
):
    """
    Fetch data from Sorftime MCP and import it.
    """
    try:
        # 1. Fetch data from MCP
        items = await mcp_service.fetch_category_data(request.input, request.type)
        
        if not items:
            return McpFetchResponse(
                status="warning",
                message="No data found",
                count=0,
                data=[]
            )
            
        # 2. Convert to DataFrame for ImportService
        df = pd.DataFrame(items)
        
        # 3. Import data via ImportService
        # We create a temporary CSV file to reuse the robust handle_upload logic
        import io
        from fastapi import UploadFile
        
        # Convert DataFrame to CSV in memory
        csv_buffer = io.BytesIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_buffer.seek(0)
        
        # Create a mock UploadFile
        # UploadFile(filename, file)
        upload_file = UploadFile(filename=f"mcp_import_{request.input}.csv", file=csv_buffer)
        
        import_service = ImportService()
        batch = import_service.handle_upload(
            db=db,
            file=upload_file,
            import_strategy="append", # Default to append
            created_by=None, # System import
        )
        
        return McpFetchResponse(
            status="success",
            message=f"Successfully fetched {len(items)} items. Import Batch ID: {batch.id}",
            count=len(items),
            data=items
        )
        
    except Exception as e:
        logger.error(f"Error in MCP fetch: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
