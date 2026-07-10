from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.core.config import get_settings
from app.services.notarial_document_intelligence.hashing import sha256_bytes, sha256_file
from app.services.storage import _has_supabase_credentials, _upload_to_supabase, sanitize_storage_filename

MAX_SUPABASE_DOCUMENT_UPLOAD_BYTES = 50 * 1024 * 1024


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

    def store_document(self, notary_id: int, filename: str, content: bytes, content_type: str) -> StoredDocumentResult:
        content_hash = sha256_bytes(content)
        return self._store_content(notary_id, filename, content_hash, content_type, content=content)

    def store_document_path(self, notary_id: int, filename: str, source_path: str | Path, content_type: str) -> StoredDocumentResult:
        source = Path(source_path)
        content_hash = sha256_file(source)
        return self._store_content(notary_id, filename, content_hash, content_type, source_path=source)

    def _store_content(
        self,
        notary_id: int,
        filename: str,
        content_hash: str,
        content_type: str,
        content: bytes | None = None,
        source_path: Path | None = None,
    ) -> StoredDocumentResult:
        safe_name = sanitize_storage_filename(filename or "documento.docx")
        extension = Path(safe_name).suffix.lower() or ".docx"
        object_key = f"{self.prefix}/notary_{notary_id}/documents/{content_hash[:2]}/{content_hash}{extension}"
        if self.use_supabase:
            file_size = len(content) if content is not None else Path(source_path).stat().st_size
            if file_size > MAX_SUPABASE_DOCUMENT_UPLOAD_BYTES:
                raise ValueError("Supabase upload rejected: document exceeds bounded single-file upload size.")
            payload = content if content is not None else Path(source_path).read_bytes()
            _upload_to_supabase(self.bucket, object_key, payload, content_type)
            return StoredDocumentResult(
                filename=safe_name,
                content_hash=content_hash,
                storage_path=f"supabase://{self.bucket}/{object_key}",
                storage_backend="supabase",
                content_type=content_type,
                file_size_bytes=file_size,
            )

        target = self.local_root / f"notary_{notary_id}" / "documents" / content_hash[:2] / f"{content_hash}{extension}"
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            if source_path is not None:
                with Path(source_path).open("rb") as source, target.open("wb") as destination:
                    for chunk in iter(lambda: source.read(1024 * 1024), b""):
                        destination.write(chunk)
            else:
                target.write_bytes(content or b"")
        file_size = len(content) if content is not None else Path(source_path).stat().st_size
        return StoredDocumentResult(
            filename=safe_name,
            content_hash=content_hash,
            storage_path=str(target),
            storage_backend="local",
            content_type=content_type,
            file_size_bytes=file_size,
            local_path=target,
        )
