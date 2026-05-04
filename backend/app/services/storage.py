from __future__ import annotations

import base64
import mimetypes
import os
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

from app.core.config import BASE_DIR

STORAGE_ROOT = BASE_DIR / "storage"
TEMPLATE_STORAGE = STORAGE_ROOT / "templates"
CASE_STORAGE = STORAGE_ROOT / "cases"
SUPABASE_TEMPLATE_BUCKET = os.environ.get("SUPABASE_TEMPLATES_BUCKET", "documentos").strip() or "documentos"


def ensure_storage_dirs() -> None:
    for directory in (STORAGE_ROOT, TEMPLATE_STORAGE, CASE_STORAGE):
        directory.mkdir(parents=True, exist_ok=True)


def template_file_path(filename: str) -> Path:
    ensure_storage_dirs()
    return TEMPLATE_STORAGE / sanitize_filename(filename)


def get_supabase_client():
    from supabase import create_client

    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        raise ValueError("SUPABASE_URL y SUPABASE_SERVICE_KEY requeridos")
    return create_client(url, key)


def _has_supabase_credentials() -> bool:
    return bool((os.environ.get("SUPABASE_URL", "") or "").strip() and (os.environ.get("SUPABASE_SERVICE_KEY", "") or "").strip())


def _upload_to_supabase(bucket: str, path: str, content: bytes, content_type: str) -> None:
    supabase = get_supabase_client()
    supabase.storage.from_(bucket).upload(
        path=path,
        file=content,
        file_options={
            "content-type": content_type,
            "upsert": "true",
        },
    )


def _download_from_supabase(bucket: str, path: str) -> bytes:
    supabase = get_supabase_client()
    result = supabase.storage.from_(bucket).download(path)
    if isinstance(result, bytes):
        return result
    if hasattr(result, "read"):
        return result.read()
    raise TypeError(f"No fue posible descargar el archivo {path} desde Supabase.")


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
    content = base64.b64decode(content_base64)
    if _has_supabase_credentials():
        bucket = SUPABASE_TEMPLATE_BUCKET
        storage_key = f"templates/{final_name}"
        _upload_to_supabase(bucket, storage_key, content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        return final_name, f"supabase://{bucket}/{storage_key}"
    destination = TEMPLATE_STORAGE / final_name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    return final_name, str(destination)


def is_supabase_storage_path(storage_path: str | Path) -> bool:
    return str(storage_path).startswith("supabase://")


def resolve_template_source_path(storage_path: str | Path, temp_dir: str | Path | None = None) -> Path:
    raw = str(storage_path or "").strip()
    if not raw:
        raise FileNotFoundError("La plantilla no tiene un archivo base configurado.")

    if raw.startswith("supabase://"):
        without_scheme = raw[len("supabase://") :]
        bucket, _, key = without_scheme.partition("/")
        if not bucket or not key:
            raise ValueError("La ruta Supabase de la plantilla no es válida.")
        target_dir = Path(temp_dir) if temp_dir else Path(tempfile.mkdtemp(prefix="easypro2-template-"))
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / Path(key).name
        target.write_bytes(_download_from_supabase(bucket, key))
        return target

    if raw.startswith("http://") or raw.startswith("https://"):
        target_dir = Path(temp_dir) if temp_dir else Path(tempfile.mkdtemp(prefix="easypro2-template-"))
        target_dir.mkdir(parents=True, exist_ok=True)
        parsed = urlparse(raw)
        filename = Path(parsed.path).name or "plantilla.docx"
        target = target_dir / filename
        with urlopen(raw) as response:
            target.write_bytes(response.read())
        return target

    path = Path(raw)
    if path.exists():
        return path

    if _has_supabase_credentials() and path.name:
        try:
            bucket = SUPABASE_TEMPLATE_BUCKET
            storage_key = f"templates/{path.name}"
            target_dir = Path(temp_dir) if temp_dir else Path(tempfile.mkdtemp(prefix="easypro2-template-"))
            target_dir.mkdir(parents=True, exist_ok=True)
            target = target_dir / path.name
            target.write_bytes(_download_from_supabase(bucket, storage_key))
            return target
        except Exception:
            pass
    raise FileNotFoundError(f"La plantilla no está disponible en almacenamiento local: {path}")


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
