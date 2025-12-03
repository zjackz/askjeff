import os
import shutil
import subprocess
import tarfile
import sys
from pathlib import Path

# Add backend dir to path to import config
sys.path.append(str(Path(__file__).parent.parent))
from app.config import settings

def restore(backup_file: str):
    backup_path = Path(backup_file)
    if not backup_path.exists():
        print(f"Error: Backup file {backup_file} not found.")
        return

    print(f"Restoring from {backup_file}...")
    
    # Create temp dir
    temp_dir = settings.backup_dir / "restore_temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)

    try:
        # 1. Extract Archive
        print("Extracting archive...")
        with tarfile.open(backup_path, "r:gz") as tar:
            tar.extractall(temp_dir)
        
        # Find extracted folder (it matches backup name)
        extracted_root = next(temp_dir.iterdir())
        
        # 2. Restore Database
        db_file = extracted_root / "database.sql"
        if db_file.exists():
            print("Restoring database...")
            # Use psql to restore
            # We assume database exists, we might need to drop/create or just clean
            # For simplicity, we just run psql which executes SQL commands
            cmd = ["psql", settings.database_url, "-f", str(db_file)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Database restore failed: {result.stderr}")
            else:
                print("Database restored successfully.")
        else:
            print("No database.sql found in backup.")

        # 3. Restore Storage
        storage_source = extracted_root / "storage"
        if storage_source.exists():
            print("Restoring storage files...")
            if settings.storage_dir.exists():
                shutil.rmtree(settings.storage_dir)
            shutil.copytree(storage_source, settings.storage_dir)
            print("Storage restored successfully.")
        else:
            print("No storage directory found in backup.")

    except Exception as e:
        print(f"Restore failed: {e}")
    finally:
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        print("Done.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python restore.py <path_to_backup_file>")
    else:
        restore(sys.argv[1])
