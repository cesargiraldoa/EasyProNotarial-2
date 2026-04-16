from __future__ import annotations

import base64
import mimetypes
import shutil
from pathlib import Path

from app.core.config import BASE_DIR

STORAGE_ROOT = BASE_DIR / "storage"
TEMPLATE_STORAGE = STORAGE_ROOT / "templates"
CASE_STORAGE = STORAGE_ROOT / "cases"


def ensure_storage_dirs() -> None:
    for directory in (STORAGE_ROOT, TEMPLATE_STORAGE, CASE_STORAGE):
        directory.mkdir(parents=True, exist_ok=True)


def template_file_path(filename: str) -> Path:
    ensure_storage_dirs()
    return TEMPLATE_STORAGE / sanitize_filename(filename)


def sanitize_filename(filename: str) -> str:
    keep = [char if char.isalnum() or char in {"-", "_", "."} else "_" for char in filename.strip()]
    sanitized = "".join(keep).strip("._") or "archivo"
    return sanitized


def copy_template_file(source_path: str | Path, slug: str) -> tuple[str, str]:
    ensure_storage_dirs()
    source = Path(source_path)
    extension = source.suffix.lower() or ".docx"
    filename = sanitize_filename(f"{slug}{extension}")
    destination = TEMPLATE_STORAGE / filename
    shutil.copy2(source, destination)
    return filename, str(destination)


def save_base64_file(content_base64: str, destination: str | Path) -> Path:
    ensure_storage_dirs()
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    data = base64.b64decode(content_base64)
    target.write_bytes(data)
    return target


def save_template_upload(filename: str, content_base64: str, slug: str) -> tuple[str, str]:
    ensure_storage_dirs()
    safe_name = sanitize_filename(filename)
    extension = Path(safe_name).suffix.lower() or ".docx"
    final_name = sanitize_filename(f"{slug}{extension}")
    destination = TEMPLATE_STORAGE / final_name
    save_base64_file(content_base64, destination)
    return final_name, str(destination)


def next_case_file_path(case_id: int, category: str, version_number: int, file_format: str, filename: str | None = None) -> Path:
    ensure_storage_dirs()
    extension = f".{file_format.lower().lstrip('.')}"
    safe_name = sanitize_filename(filename or f"{category}_v{version_number}{extension}")
    if not safe_name.lower().endswith(extension):
        safe_name = f"{safe_name}{extension}"
    directory = CASE_STORAGE / f"case-{case_id}" / category
    directory.mkdir(parents=True, exist_ok=True)
    return directory / safe_name


def guess_media_type(path: str | Path) -> str:
    media_type, _ = mimetypes.guess_type(str(path))
    return media_type or "application/octet-stream"
