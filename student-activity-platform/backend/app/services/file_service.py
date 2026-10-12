"""File handling service for uploads."""
import os
import hashlib
import uuid
from fastapi import UploadFile, HTTPException
from app.core.config import settings


def sanitize_filename(filename: str) -> str:
    """Generate a safe filename with UUID prefix."""
    ext = os.path.splitext(filename)[1].lower()
    safe_name = f"{uuid.uuid4().hex}{ext}"
    return safe_name


def validate_file(file: UploadFile) -> None:
    """Validate file size and extension."""
    ext = os.path.splitext(file.filename or "")[1].lower().lstrip(".")
    if ext not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=400,
            detail=f"File type '.{ext}' not allowed. Allowed: {', '.join(settings.allowed_extensions_list)}"
        )


async def save_upload(file: UploadFile, upload_dir: str = None) -> dict:
    """Save uploaded file and compute SHA-256 hash."""
    upload_dir = upload_dir or settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)

    safe_name = sanitize_filename(file.filename or "upload")
    file_path = os.path.join(upload_dir, safe_name)

    sha256 = hashlib.sha256()
    content = await file.read()

    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE // (1024*1024)}MB"
        )

    sha256.update(content)

    with open(file_path, "wb") as f:
        f.write(content)

    ext = os.path.splitext(file.filename or "")[1].lower().lstrip(".")
    mime_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "pdf": "application/pdf"}

    return {
        "file_path": safe_name,
        "file_hash": sha256.hexdigest(),
        "mime_type": mime_map.get(ext, "application/octet-stream"),
    }


def get_full_path(filename: str) -> str:
    """Get full file path for a stored file."""
    return os.path.join(settings.UPLOAD_DIR, filename)
