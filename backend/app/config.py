from __future__ import annotations

import os
from pathlib import Path


class Settings:
    database_url: str
    storage_dir: Path
    deepseek_api_key: str

    def __init__(self) -> None:
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://sorftime:sorftime@localhost:5432/sorftime",
        )
        self.storage_dir = Path(os.getenv("STORAGE_DIR", "backend/storage"))
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.backup_dir = Path(os.getenv("BACKUP_DIR", "backend/backups"))
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # DeepSeek API
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        
        # 文件上传限制
        self.max_file_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", "50"))  # 最大文件大小 (MB)

        # JWT Settings
        self.secret_key = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60 * 24 * 8  # 8 days


settings = Settings()
