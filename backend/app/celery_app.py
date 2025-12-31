"""
Celery 应用配置

用于异步任务处理和定时任务调度
"""

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

# 创建 Celery 应用
celery_app = Celery(
    "askjeff",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.sync_tasks"]
)

# Celery 配置
celery_app.conf.update(
    # 时区设置
    timezone="Asia/Shanghai",
    enable_utc=True,
    
    # 任务序列化
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # 任务结果过期时间 (24 小时)
    result_expires=86400,
    
    # 任务超时时间 (30 分钟)
    task_time_limit=1800,
    task_soft_time_limit=1700,
    
    # 任务重试配置
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Worker 配置
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # 定时任务配置
    beat_schedule={
        # 每日凌晨 2:00 同步库存数据
        "sync-inventory-daily": {
            "task": "app.tasks.sync_tasks.sync_inventory_task",
            "schedule": crontab(hour=2, minute=0),
            "args": (),
        },
        # 每日凌晨 2:30 同步业务报告
        "sync-business-reports-daily": {
            "task": "app.tasks.sync_tasks.sync_business_reports_task",
            "schedule": crontab(hour=2, minute=30),
            "args": (),
        },
        # 每日凌晨 3:00 同步广告数据
        "sync-advertising-daily": {
            "task": "app.tasks.sync_tasks.sync_advertising_task",
            "schedule": crontab(hour=3, minute=0),
            "args": (),
        },
    },
)


# 任务路由配置 (可选,用于多队列)
celery_app.conf.task_routes = {
    "app.tasks.sync_tasks.*": {"queue": "sync"},
}


if __name__ == "__main__":
    celery_app.start()
