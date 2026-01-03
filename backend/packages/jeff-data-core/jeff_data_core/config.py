from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

logger = logging.getLogger("jeff_data_core.config")

class JDCConfig(BaseSettings):
    """
    Jeff Data Core Configuration.
    All environment variables should be prefixed with JDC_ to avoid conflicts
    with the host application.
    """
    model_config = SettingsConfigDict(
        env_prefix="JDC_", 
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Database
    # Allow passing explicit URL or falling back to JDC_DATABASE_URL
    DATABASE_URL: Optional[str] = Field(default=None, description="Database connection string")
    
    # Feature Flags
    ENABLE_METRICS: bool = Field(default=True, description="Whether to collect metrics")
    
    # Processing
    DEFAULT_BATCH_SIZE: int = Field(default=1000, description="Default batch size for ETL operations")

# Global instance for library-level usage, but dependency injection is preferred
_config: Optional[JDCConfig] = None

def get_config() -> JDCConfig:
    global _config
    if _config is None:
        logger.debug("Initializing JDC Config from environment (JDC_ prefix)")
        _config = JDCConfig()
    return _config

def init_config(custom_config: Optional[JDCConfig] = None):
    """Allow host application to inject configuration"""
    global _config
    if custom_config:
        _config = custom_config
    else:
        get_config()
