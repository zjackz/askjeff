from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.models.import_batch import ImportBatch, ProductRecord
from app.models.extraction import ExtractionTask, ExtractionItem
from app.models.extraction_run import ExtractionRun
from app.models.export_job import ExportJob
from app.models.system_log import SystemLog
from app.models.query_session import QuerySession
from app.models.audit_log import AuditLog

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.delete("/data")
def delete_all_data(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete all data except users and reset ID sequences (Admin only).
    
    注意: 此操作会删除所有业务数据,但保留用户表(users),
    确保管理员账号不会被删除,避免无法登录系统。
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Helper to safely delete table data
    def safe_delete(table_name: str):
        # Check if table exists to avoid "relation does not exist" errors
        # causing transaction aborts
        exists = db.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = :table)"
        ), {"table": table_name}).scalar()
        
        if not exists:
            return

        try:
            with db.begin_nested():
                db.execute(text(f"DELETE FROM {table_name}"))
        except Exception as e:
            print(f"Warning: Failed to delete {table_name}: {e}")

    # 1. Delete data in order of dependencies (Child -> Parent)
    # Tables to delete (using actual table names)
    tables = [
        "system_logs",
        "audit_logs",
        "query_sessions",
        # "extraction_items", # Table missing in current schema
        # "extraction_tasks", # Table missing in current schema
        "extraction_runs",
        "product_records", # Fixed from "products"
        "import_batches",
        "export_jobs",
    ]
    
    for table in tables:
        safe_delete(table)
    
    # 2. Reset ID sequences for tables with Identity/autoincrement
    sequences_to_reset = [
        "import_batches_id_seq",
        "extraction_runs_id_seq",
        "export_jobs_id_seq",
        "system_logs_id_seq",
    ]
    
    for seq_name in sequences_to_reset:
        try:
            with db.begin_nested():
                db.execute(text(f"ALTER SEQUENCE {seq_name} RESTART WITH 1"))
        except Exception as e:
            if "does not exist" not in str(e):
                print(f"Error resetting sequence {seq_name}: {e}")

    db.commit()
    
    return {"message": "All data deleted and ID sequences reset successfully"}
