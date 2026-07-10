from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.core.config import get_settings
from app.services.notarial_document_intelligence.hashing import sha256_bytes
from app.services.storage import _has_supabase_credentials, _upload_to_supabase, sanitize_storage_filename


@dataclass(frozen=True)
class StoredDocumentResult:
    filename: str
    content_hash: str
    storage_path: str
    storage_backend: str
    content_type: str
    file_size_bytes: int
    local_path: Path | None = None


class NotarialIntelligenceStorage:
    def __init__(self, local_root: str | Path | None = None, use_supabase: bool | None = None) -> None:
        settings = get_settings()
        self.bucket = settings.notarial_intelligence_storage_bucket
        self.prefix = settings.notarial_intelligence_storage_prefix.strip("/").replace("\\", "/") or "notarial-intelligence"
        self.local_root = Path(local_root or settings.notarial_intelligence_local_storage_dir)
        self.use_supabase = _has_supabase_credentials() if use_supabase is None else use_supabase

    def store_document(self, filename: str, content: bytes, content_type: str) -> StoredDocumentResult:
        content_hash = sha256_bytes(content)
        safe_name = sanitize_storage_filename(filename or "documento.docx")
        extension = Path(safe_name).suffix.lower() or ".docx"
        object_key = f"{self.prefix}/documents/{content_hash[:2]}/{content_hash}{extension}"
        if self.use_supabase:
            _upload_to_supabase(self.bucket, object_key, content, content_type)
            return StoredDocumentResult(
                filename=safe_name,
                content_hash=content_hash,
                storage_path=f"supabase://{self.bucket}/{object_key}",
                storage_backend="supabase",
                content_type=content_type,
                file_size_bytes=len(content),
            )

        target = self.local_root / "documents" / content_hash[:2] / f"{content_hash}{extension}"
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_bytes(content)
        return StoredDocumentResult(
            filename=safe_name,
            content_hash=content_hash,
            storage_path=str(target),
            storage_backend="local",
            content_type=content_type,
            file_size_bytes=len(content),
            local_path=target,
        )
