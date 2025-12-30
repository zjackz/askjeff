from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.delete("/data")
def delete_all_data(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    删除除用户表以外的所有业务数据，并重置自增序列（仅管理员）。

    注意：此操作会删除所有业务数据，但保留用户表（users），
    确保管理员账号不会被删除，避免无法登录系统。
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足")

    def safe_delete(table_name: str) -> None:
        """安全删除表数据：表不存在时直接跳过，避免事务被中断。"""
        exists = db.execute(
            text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = :table)"
            ),
            {"table": table_name},
        ).scalar()

        if not exists:
            return

        try:
            with db.begin_nested():
                db.execute(text(f"DELETE FROM {table_name}"))
        except Exception as exc:  # noqa: BLE001 - 管理接口保持容错
            print(f"[警告] 删除表数据失败：{table_name}，错误：{exc}")

    # 按依赖顺序删除数据（子表 -> 父表）
    tables = [
        "system_logs",
        "audit_logs",
        "query_sessions",
        "extraction_runs",
        "product_records",
        "import_batches",
        "export_jobs",
    ]

    for table in tables:
        safe_delete(table)

    # 重置自增序列（仅对存在的序列执行）
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
        except Exception as exc:  # noqa: BLE001 - 管理接口保持容错
            if "does not exist" not in str(exc):
                print(f"[错误] 重置序列失败：{seq_name}，错误：{exc}")

    db.commit()

    return {"message": "已删除所有业务数据并重置自增序列"}
