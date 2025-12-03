import os
import shutil
import subprocess
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Sequence

from app.config import settings
from app.utils.time import utc_now

class BackupService:
    def __init__(self) -> None:
        self.backup_dir = settings.backup_dir
        self.storage_dir = settings.storage_dir
        self.db_url = settings.database_url

    def create_backup(self) -> str:
        """Create a full backup (DB + Storage)."""
        timestamp = utc_now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        temp_dir = self.backup_dir / "temp" / backup_name
        temp_dir.mkdir(parents=True, exist_ok=True)

        try:
            # 1. Backup Database
            db_file = temp_dir / "database.sql"
            self._dump_database(db_file)

            # 2. Backup Storage
            storage_dest = temp_dir / "storage"
            if self.storage_dir.exists():
                shutil.copytree(self.storage_dir, storage_dest)
            else:
                storage_dest.mkdir()

            # 3. Create Archive
            archive_path = self.backup_dir / f"{backup_name}.tar.gz"
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(temp_dir, arcname=backup_name)

            return archive_path.name
        finally:
            # Cleanup temp
            if temp_dir.exists():
                shutil.rmtree(temp_dir.parent)

    def list_backups(self) -> Sequence[dict]:
        """List all backup files."""
        backups = []
        for file in self.backup_dir.glob("backup_*.tar.gz"):
            stat = file.stat()
            backups.append({
                "filename": file.name,
                "size_bytes": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            })
        return sorted(backups, key=lambda x: x["created_at"], reverse=True)

    def get_backup_path(self, filename: str) -> Path | None:
        path = self.backup_dir / filename
        if path.exists() and path.is_file():
            return path
        return None

    def delete_backup(self, filename: str) -> bool:
        path = self.get_backup_path(filename)
        if path:
            path.unlink()
            return True
        return False

    def _dump_database(self, output_path: Path) -> None:
        """Run pg_dump."""
        # Use explicit flags to avoid parsing issues
        from sqlalchemy.engine import make_url
        url = make_url(str(self.db_url))
        
        env = os.environ.copy()
        env["PGPASSWORD"] = url.password or ""
        
        cmd = [
            "pg_dump",
            "-h", url.host or "localhost",
            "-p", str(url.port or 5432),
            "-U", url.username or "postgres",
            "-d", url.database or "postgres",
            "-f", str(output_path)
        ]
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Database backup failed: {result.stderr}")

backup_service = BackupService()
