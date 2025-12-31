from __future__ import annotations

import os
from pathlib import Path
try:
    from dotenv import load_dotenv
    # 尝试从当前目录或上级目录加载 .env
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()
except ImportError:
    # Fallback: 手动解析 .env 文件
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


class Settings:
    database_url: str
    storage_dir: Path
    deepseek_api_key: str
    sorftime_api_key: str
    secret_key: str
    is_testing: bool

    def __init__(self) -> None:
        # 检测是否在测试环境
        self.is_testing = os.getenv("TESTING", "").lower() in {"1", "true", "yes"} or \
                         "pytest" in os.getenv("_", "")
        
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://sorftime:sorftime@localhost:5432/sorftime",
        )
        self.storage_dir = Path(os.getenv("STORAGE_DIR", "backend/storage"))
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.backup_dir = Path(os.getenv("BACKUP_DIR", "backend/backups"))
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # DeepSeek API - 生产环境必需,测试环境可选
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "")
        if not self.deepseek_api_key:
            if self.is_testing:
                # 测试环境使用假密钥
                self.deepseek_api_key = "test_deepseek_key_for_testing"
            else:
                raise ValueError(
                    "❌ 配置错误: 缺少 DEEPSEEK_API_KEY 环境变量\n"
                    "请在 .env 文件中设置: DEEPSEEK_API_KEY=your_api_key_here"
                )
        self.deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        
        # Sorftime API - 生产环境必需,测试环境可选
        self.sorftime_api_key = os.getenv("SORFTIME_API_KEY", "")
        if not self.sorftime_api_key:
            if self.is_testing:
                # 测试环境使用假密钥
                self.sorftime_api_key = "test_sorftime_key_for_testing"
            else:
                raise ValueError(
                    "❌ 配置错误: 缺少 SORFTIME_API_KEY 环境变量\n"
                    "请在 .env 文件中设置: SORFTIME_API_KEY=your_api_key_here"
                )
        
        # 文件上传限制
        self.max_file_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", "50"))  # 最大文件大小 (MB)

        # JWT Settings - 生产环境必需,测试环境可选
        self.secret_key = os.getenv("SECRET_KEY", "")
        if not self.secret_key:
            if self.is_testing:
                # 测试环境使用固定密钥
                self.secret_key = "test_secret_key_for_testing_only_do_not_use_in_production"
            else:
                raise ValueError(
                    "❌ 配置错误: 缺少 SECRET_KEY 环境变量\n"
                    "请在 .env 文件中设置: SECRET_KEY=your_secret_key_here\n"
                    "提示: 可使用命令生成随机密钥: openssl rand -hex 32"
                )
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60 * 24 * 8  # 8 days
        
        # Amazon API Settings
        self.amazon_client_id = os.getenv("AMAZON_CLIENT_ID", "")
        self.amazon_client_secret = os.getenv("AMAZON_CLIENT_SECRET", "")
        self.amazon_refresh_token = os.getenv("AMAZON_REFRESH_TOKEN", "")
        
        # Celery Settings
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = os.getenv("REDIS_PORT", "6379")
        redis_db = os.getenv("REDIS_DB", "0")
        self.CELERY_BROKER_URL = f"redis://{redis_host}:{redis_port}/{redis_db}"
        self.CELERY_RESULT_BACKEND = f"redis://{redis_host}:{redis_port}/{redis_db}"


settings = Settings()
