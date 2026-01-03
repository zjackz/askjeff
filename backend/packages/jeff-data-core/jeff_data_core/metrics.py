import logging
from typing import Optional
from prometheus_client import CollectorRegistry, Counter, Histogram, REGISTRY

logger = logging.getLogger("jeff_data_core.metrics")

# 定义指标命名空间
NAMESPACE = "jdc"

# 全局指标容器
class JDCMetrics:
    def __init__(self, registry: CollectorRegistry = REGISTRY):
        self.registry = registry
        
        # 定义指标
        self.etl_rows_processed = Counter(
            f"{NAMESPACE}_etl_rows_processed_total",
            "Total number of rows processed by ETL pipelines",
            ["pipeline", "status"],
            registry=registry
        )
        
        self.etl_job_duration = Histogram(
            f"{NAMESPACE}_etl_job_duration_seconds",
            "Time spent processing ETL jobs",
            ["job_name"],
            registry=registry
        )
        
        self.api_latency = Histogram(
            f"{NAMESPACE}_api_latency_seconds",
            "Latency of JDC internal API calls",
            ["endpoint"],
            registry=registry
        )

# 单例
_metrics: Optional[JDCMetrics] = None

def get_metrics() -> JDCMetrics:
    global _metrics
    if _metrics is None:
        # 默认注册到全局 REGISTRY，方便宿主应用如果是基于 prometheus_client 的可以直接采集到
        _metrics = JDCMetrics()
    return _metrics

def register_jdc_metrics(target_registry: CollectorRegistry):
    """
    允许宿主应用传入自己的 Registry，重建指标以通过宿主暴露
    注意：这不仅是挂载，而是使用新的 registry 重新实例化指标
    """
    global _metrics
    logger.info("Re-initializing JDC metrics with host registry")
    _metrics = JDCMetrics(registry=target_registry)
