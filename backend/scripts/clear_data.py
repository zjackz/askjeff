"""
清空所有业务数据（开发环境使用）
"""
from sqlalchemy import text
from app.db import SessionLocal

def safe_delete(db, table_name: str) -> None:
    """安全删除表数据"""
    exists = db.execute(
        text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = :table)"
        ),
        {"table": table_name},
    ).scalar()

    if not exists:
        print(f"  ⊘ 表 {table_name} 不存在，跳过")
        return

    try:
        with db.begin_nested():
            result = db.execute(text(f"DELETE FROM {table_name}"))
            print(f"  ✓ 清空表 {table_name} ({result.rowcount} 行)")
    except Exception as exc:
        print(f"  ✗ 删除表 {table_name} 失败: {exc}")

with SessionLocal() as db:
    print("=" * 60)
    print("清空所有业务数据")
    print("=" * 60)
    
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
    
    print("\n1. 删除表数据:")
    for table in tables:
        safe_delete(db, table)
    
    # 重置自增序列
    sequences_to_reset = [
        "import_batches_id_seq",
        "extraction_runs_id_seq",
        "export_jobs_id_seq",
        "system_logs_id_seq",
    ]
    
    print("\n2. 重置自增序列:")
    for seq_name in sequences_to_reset:
        try:
            with db.begin_nested():
                db.execute(text(f"ALTER SEQUENCE {seq_name} RESTART WITH 1"))
                print(f"  ✓ 重置序列 {seq_name}")
        except Exception as exc:
            if "does not exist" not in str(exc):
                print(f"  ✗ 重置序列 {seq_name} 失败: {exc}")
            else:
                print(f"  ⊘ 序列 {seq_name} 不存在，跳过")
    
    db.commit()
    
    print("\n✓ 所有业务数据已清空并重置序列")
    print("=" * 60)
