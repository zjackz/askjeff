"""
Celery 任务包
"""

from .sync_tasks import (
    sync_inventory_task,
    sync_business_reports_task,
    sync_advertising_task,
    sync_all_stores_task,
)

__all__ = [
    "sync_inventory_task",
    "sync_business_reports_task",
    "sync_advertising_task",
    "sync_all_stores_task",
]
