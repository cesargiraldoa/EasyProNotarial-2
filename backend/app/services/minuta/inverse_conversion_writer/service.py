from __future__ import annotations

from pathlib import Path

from app.services.minuta.inverse_conversion_writer.docx_marked_writer import DocxMarkedWriter, marked_docx_filename
from app.services.minuta.inverse_conversion_writer.models import MarkedCandidate, MarkedDocxWriteResult


class InverseConversionMarkedDocxService:
    def __init__(self, writer: DocxMarkedWriter | None = None) -> None:
        self.writer = writer or DocxMarkedWriter()

    def generate(
        self,
        source_path: str | Path,
        destination_path: str | Path,
        original_filename: str,
        candidates: list[MarkedCandidate],
        allowed_field_codes: set[str] | None = None,
        field_aliases: dict[str, str] | None = None,
    ) -> MarkedDocxWriteResult:
        return self.writer.write(
            source_path=source_path,
            destination_path=destination_path,
            candidates=candidates,
            output_filename=marked_docx_filename(original_filename),
            allowed_field_codes=allowed_field_codes,
            field_aliases=field_aliases,
        )
