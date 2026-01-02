"""
Jeff Data Core Configuration

配置管理模块
"""

from dataclasses import dataclass
from typing import Optional
import os
from pathlib import Path


@dataclass
class DatabaseConfig:
    """数据库配置"""
    url: str
    pool_size: int = 20
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600


@dataclass
class RedisConfig:
    """Redis 配置"""
    url: str = "redis://localhost:6379/0"
    max_connections: int = 50
    decode_responses: bool = True


@dataclass
class AmazonConfig:
    """Amazon API 配置"""
    ads_client_id: Optional[str] = None
    ads_client_secret: Optional[str] = None
    ads_refresh_token: Optional[str] = None

    sp_client_id: Optional[str] = None
    sp_client_secret: Optional[str] = None
    sp_refresh_token: Optional[str] = None


@dataclass
class SorftimeConfig:
    """Sorftime API 配置"""
    api_key: Optional[str] = None
    base_url: str = "https://api.sorftime.com"


@dataclass
class AIConfig:
    """AI 提供商配置"""
    deepseek_api_key: Optional[str] = None
    deepseek_base_url: str = "https://api.deepseek.com"

    openai_api_key: Optional[str] = None
    openai_base_url: str = "https://api.openai.com/v1"

    default_provider: str = "deepseek"


@dataclass
class LogConfig:
    """日志配置"""
    level: str = "INFO"
    format: str = "json"
    log_dir: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10 MB
    backup_count: int = 5


@dataclass
class JDCConfig:
    """JDC 统一配置"""

    database: DatabaseConfig
    redis: RedisConfig
    amazon: AmazonConfig
    sorftime: SorftimeConfig
    ai: AIConfig
    log: LogConfig

    @classmethod
    def from_env(cls) -> "JDCConfig":
        """从环境变量加载配置"""
        return cls(
            database=DatabaseConfig(
                url=os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/jdc_db"),
                pool_size=int(os.getenv("DB_POOL_SIZE", "20")),
                max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10"))
            ),
            redis=RedisConfig(
                url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
                max_connections=int(os.getenv("REDIS_MAX_CONN", "50"))
            ),
            amazon=AmazonConfig(
                ads_client_id=os.getenv("AMAZON_ADS_CLIENT_ID"),
                ads_client_secret=os.getenv("AMAZON_ADS_CLIENT_SECRET"),
                ads_refresh_token=os.getenv("AMAZON_ADS_REFRESH_TOKEN"),
                sp_client_id=os.getenv("AMAZON_SP_CLIENT_ID"),
                sp_client_secret=os.getenv("AMAZON_SP_CLIENT_SECRET"),
                sp_refresh_token=os.getenv("AMAZON_SP_REFRESH_TOKEN")
            ),
            sorftime=SorftimeConfig(
                api_key=os.getenv("SORFTIME_API_KEY"),
                base_url=os.getenv("SORFTIME_BASE_URL", "https://api.sorftime.com")
            ),
            ai=AIConfig(
                deepseek_api_key=os.getenv("DEEPSEEK_API_KEY"),
                deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                default_provider=os.getenv("DEFAULT_AI_PROVIDER", "deepseek")
            ),
            log=LogConfig(
                level=os.getenv("LOG_LEVEL", "INFO"),
                format=os.getenv("LOG_FORMAT", "json"),
                log_dir=os.getenv("LOG_DIR"),
                max_file_size=int(os.getenv("LOG_MAX_FILE_SIZE", str(10 * 1024 * 1024))),
                backup_count=int(os.getenv("LOG_BACKUP_COUNT", "5"))
            )
        )

    def validate(self) -> None:
        """验证配置"""
        if not self.database.url:
            raise ValueError("DATABASE_URL is required")

        if self.ai.default_provider not in ["deepseek", "openai"]:
            raise ValueError(f"Invalid AI provider: {self.ai.default_provider}")
