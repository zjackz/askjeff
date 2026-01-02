"""
Jeff Data Core 日志模块

提供结构化日志、API 调用日志、同步任务日志
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class StructuredLogger:
    """结构化日志"""

    def __init__(self, name: str, tenant_id: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.tenant_id = tenant_id

    def _log(
        self,
        level: str,
        log_type: str,
        data: Dict[str, Any]
    ):
        """记录日志"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "tenant_id": self.tenant_id,
            "type": log_type,
            "data": data
        }

        self.logger.info(json.dumps(log_entry))

    def log_api_call(
        self,
        api_type: str,
        endpoint: str,
        method: str,
        request_id: Optional[str] = None,
        request_body: Optional[Dict] = None,
        status_code: Optional[int] = None,
        response_time_ms: Optional[int] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """记录 API 调用"""
        self._log(
            level="INFO" if success else "ERROR",
            log_type="api_call",
            data={
                "api_type": api_type,
                "endpoint": endpoint,
                "method": method,
                "request_id": request_id,
                "request_body": request_body,
                "status_code": status_code,
                "response_time_ms": response_time_ms,
                "success": success,
                "error_message": error_message
            }
        )

    def log_sync_task(
        self,
        source_type: str,
        task_type: str,
        status: str,
        records_total: int = 0,
        records_success: int = 0,
        records_failed: int = 0,
        error_message: Optional[str] = None
    ):
        """记录同步任务"""
        self._log(
            level="INFO" if status == "success" else "ERROR",
            log_type="sync_task",
            data={
                "source_type": source_type,
                "task_type": task_type,
                "status": status,
                "records_total": records_total,
                "records_success": records_success,
                "records_failed": records_failed,
                "error_message": error_message
            }
        )

    def log_ai_call(
        self,
        provider: str,
        function_type: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        total_tokens: int = 0,
        cost_usd: float = 0.0,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """记录 AI 调用"""
        self._log(
            level="INFO" if success else "ERROR",
            log_type="ai_call",
            data={
                "provider": provider,
                "function_type": function_type,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "cost_usd": cost_usd,
                "success": success,
                "error_message": error_message
            }
        )

    def log_performance_metric(
        self,
        metric_type: str,
        metric_name: str,
        metric_value: float,
        unit: str,
        tags: Optional[Dict[str, str]] = None
    ):
        """记录性能指标"""
        self._log(
            level="INFO",
            log_type="performance_metric",
            data={
                "metric_type": metric_type,
                "metric_name": metric_name,
                "metric_value": metric_value,
                "unit": unit,
                "tags": tags or {}
            }
        )

    def log_error(
        self,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """记录错误"""
        self._log(
            level="ERROR",
            log_type="error",
            data={
                "error_type": error_type,
                "error_message": error_message,
                "context": context or {}
            }
        )


class PerformanceMetrics:
    """性能指标收集器"""

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_client = None
        if REDIS_AVAILABLE and redis_url:
            try:
                import redis.asyncio as redis_async
                self.redis_client = redis_async.from_url(redis_url)
            except Exception as e:
                logging.warning(f"Failed to connect to Redis: {e}")

    async def record_api_latency(
        self,
        tenant_id: str,
        api_type: str,
        endpoint: str,
        latency_ms: int
    ):
        """记录 API 延迟"""
        if not self.redis_client:
            return

        key = f"perf:api_latency:{tenant_id}:{api_type}:{endpoint}"
        await self.redis_client.lpush(key, latency_ms)
        await self.redis_client.ltrim(key, 0, 999)  # 保留最近 1000 个
        await self.redis_client.expire(key, 86400)  # 24 小时过期

    async def record_sync_performance(
        self,
        tenant_id: str,
        source_type: str,
        duration_ms: int,
        records_count: int
    ):
        """记录同步性能"""
        if not self.redis_client:
            return

        key = f"perf:sync:{tenant_id}:{source_type}"
        await self.redis_client.hset(key, "last_duration", duration_ms)
        await self.redis_client.hset(key, "last_records", records_count)
        await self.redis_client.expire(key, 86400)

    async def get_api_latency_stats(
        self,
        tenant_id: str,
        api_type: str,
        endpoint: str
    ) -> Dict[str, float]:
        """获取 API 延迟统计"""
        if not self.redis_client:
            return {}

        key = f"perf:api_latency:{tenant_id}:{api_type}:{endpoint}"
        values = await self.redis_client.lrange(key, 0, -1)
        
        if not values:
            return {}

        # 转换为数字
        values = [float(v) for v in values if v]

        return {
            "count": len(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "p50": self._percentile(values, 50),
            "p95": self._percentile(values, 95),
            "p99": self._percentile(values, 99)
        }

    def _percentile(self, values: list, percentile: int) -> float:
        """计算百分位数"""
        if not values:
            return 0.0

        values_sorted = sorted(values)
        k = (len(values_sorted) - 1) * percentile / 100
        index = int(k)
        return values_sorted[index]


class LogStorage:
    """日志存储（用于持久化到数据库）"""

    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    def store_api_call(
        self,
        api_type: str,
        endpoint: str,
        method: str,
        request_id: Optional[str] = None,
        request_body: Optional[Dict] = None,
        status_code: Optional[int] = None,
        response_time_ms: Optional[int] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """存储 API 调用日志到数据库"""
        from app.models.jdc_models import JDC_ApiCallLog, JDC_Tenant
        from uuid import uuid4

        # 获取租户 UUID
        tenant = self.db.query(JDC_Tenant).filter(JDC_Tenant.id == self.tenant_id).first()
        if not tenant:
            raise ValueError(f"Tenant not found: {self.tenant_id}")

        log = JDC_ApiCallLog(
            id=uuid4(),
            tenant_id=tenant.id,
            api_type=api_type,
            endpoint=endpoint,
            method=method,
            request_id=request_id,
            request_body=request_body,
            status_code=status_code,
            response_time_ms=response_time_ms,
            success=success,
            error_message=error_message
        )

        self.db.add(log)
        self.db.commit()

    def store_sync_task(
        self,
        source_id: str,
        task_type: str,
        status: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        records_total: int = 0,
        records_success: int = 0,
        records_failed: int = 0,
        error_message: Optional[str] = None
    ):
        """存储同步任务日志到数据库"""
        from app.models.jdc_models import JDC_SyncTask, JDC_Tenant, JDC_DataSource
        from uuid import uuid4

        # 获取租户 UUID
        tenant = self.db.query(JDC_Tenant).filter(JDC_Tenant.id == self.tenant_id).first()
        if not tenant:
            raise ValueError(f"Tenant not found: {self.tenant_id}")

        # 获取数据源
        data_source = self.db.query(JDC_DataSource).filter(JDC_DataSource.id == source_id).first()
        if not data_source:
            raise ValueError(f"Data source not found: {source_id}")

        # 如果 start_time 为 None，使用当前时间
        if start_time is None:
            start_time = datetime.utcnow()

        task = JDC_SyncTask(
            id=uuid4(),
            tenant_id=tenant.id,
            source_id=data_source.id,
            task_type=task_type,
            status=status,
            start_time=start_time,
            end_time=end_time,
            records_total=records_total,
            records_success=records_success,
            records_failed=records_failed,
            error_message=error_message
        )

        self.db.add(task)
        self.db.commit()
