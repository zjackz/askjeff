from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from app.api import deps
from app.models.user import User
from app.services.backup_service import backup_service

router = APIRouter()

@router.post("", status_code=status.HTTP_201_CREATED)
def create_backup(
    current_user: Annotated[User, Depends(deps.get_current_user)],
):
    """Trigger a new backup (Admin only)."""
    # In a real app, check for admin role. For now, any logged in user.
    try:
        filename = backup_service.create_backup()
        return {"filename": filename, "message": "Backup created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
def list_backups(
    current_user: Annotated[User, Depends(deps.get_current_user)],
):
    """List available backups."""
    return backup_service.list_backups()

@router.get("/{filename}")
def download_backup(
    filename: str,
    current_user: Annotated[User, Depends(deps.get_current_user)],
):
    """Download a backup file."""
    path = backup_service.get_backup_path(filename)
    if not path:
        raise HTTPException(status_code=404, detail="Backup not found")
    return FileResponse(path, filename=filename)

@router.delete("/{filename}")
def delete_backup(
    filename: str,
    current_user: Annotated[User, Depends(deps.get_current_user)],
):
    """Delete a backup file."""
    if backup_service.delete_backup(filename):
        return {"message": "Backup deleted"}
    raise HTTPException(status_code=404, detail="Backup not found")
