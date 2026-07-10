from __future__ import annotations

import json
import tempfile
import zipfile
from collections import Counter
from pathlib import Path
from typing import Iterable

from sqlalchemy.orm import Session

from app.services.minuta.inverse_conversion_catalog.corpus_reporter import CorpusReporter
from app.services.minuta.inverse_conversion_catalog.docx_marker_extractor import DocxMarkerExtractor
from app.services.minuta.inverse_conversion_catalog.docx_red_text_extractor import DocxRedTextExtractor
from app.services.minuta.inverse_conversion_catalog.field_alias_builder import FieldAliasBuilder
from app.services.minuta.inverse_conversion_catalog.field_code_normalizer import FieldCodeNormalizer
from app.services.minuta.inverse_conversion_catalog.models import (
    CorpusDocument,
    CorpusDocumentField,
    ExtractedPattern,
    FieldPattern,
    ImportedDocument,
    ImportedField,
    ImportResult,
)
from app.services.minuta.inverse_conversion_catalog.pattern_extractor import PatternExtractor


class CorpusImporter:
    """Import ZIPs/folders of notarial DOCX files into isolated corpus tables."""

    def __init__(
        self,
        db: Session | None = None,
        marker_extractor: DocxMarkerExtractor | None = None,
        red_text_extractor: DocxRedTextExtractor | None = None,
        pattern_extractor: PatternExtractor | None = None,
        alias_builder: FieldAliasBuilder | None = None,
        normalizer: FieldCodeNormalizer | None = None,
    ) -> None:
        self.db = db
        self.normalizer = normalizer or FieldCodeNormalizer()
        self.marker_extractor = marker_extractor or DocxMarkerExtractor()
        self.red_text_extractor = red_text_extractor or DocxRedTextExtractor()
        self.pattern_extractor = pattern_extractor or PatternExtractor(self.normalizer)
        self.alias_builder = alias_builder or FieldAliasBuilder(self.normalizer)

    def import_path(
        self,
        input_path: str | Path,
        output_dir: str | Path | None = None,
        dry_run: bool = True,
        commit: bool = False,
    ) -> ImportResult:
        source = Path(input_path)
        if not source.exists():
            raise FileNotFoundError(source)

        with tempfile.TemporaryDirectory() as tmp_dir:
            source_zip: str | None = None
            root = source
            if source.is_file() and source.suffix.lower() == ".zip":
                source_zip = str(source)
                root = Path(tmp_dir) / "extracted"
                root.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(source) as archive:
                    archive.extractall(root)

            result = self._import_root(root, source_zip=source_zip, dry_run=dry_run)
            result.aliases = self.alias_builder.build(result.field_frequency, result.patterns)

            if self.db is not None and not dry_run:
                if commit:
                    self.db.commit()
                else:
                    self.db.flush()

            if output_dir is not None:
                CorpusReporter().write_import_reports(result, output_dir)

            return result

    def _import_root(self, root: Path, source_zip: str | None, dry_run: bool) -> ImportResult:
        result = ImportResult()
        for path in self._iter_candidate_documents(root):
            if path.suffix.lower() == ".doc":
                document = ImportedDocument(
                    filename=path.name,
                    source_zip=source_zip,
                    source_path=str(path),
                    processing_status="unsupported",
                    error_message="Legacy .doc files are unsupported.",
                )
                result.documents.append(document)
                result.errors.append({"filename": path.name, "source_path": str(path), "error": document.error_message})
                if self.db is not None and not dry_run:
                    self._persist_document(document)
                continue

            try:
                document = self._process_docx(path, source_zip=source_zip)
                result.documents.append(document)
                result.patterns.extend(document.patterns)
                for field in document.fields:
                    result.field_frequency[field.raw_field_code] = result.field_frequency.get(field.raw_field_code, 0) + field.occurrences
                if self.db is not None and not dry_run:
                    self._persist_document(document)
            except Exception as exc:
                document = ImportedDocument(
                    filename=path.name,
                    source_zip=source_zip,
                    source_path=str(path),
                    processing_status="error",
                    error_message=str(exc),
                )
                result.documents.append(document)
                result.errors.append({"filename": path.name, "source_path": str(path), "error": str(exc)})
                if self.db is not None and not dry_run:
                    self._persist_document(document)
        return result

    def _process_docx(self, path: Path, source_zip: str | None) -> ImportedDocument:
        markers = self.marker_extractor.extract_from_docx(path)
        red_text = self.red_text_extractor.extract_from_docx(path)
        field_counts = Counter(marker.raw_field_code for marker in markers)
        patterns = self.pattern_extractor.extract_many(markers, pattern_source_file=str(path))
        fields = [
            ImportedField(
                raw_field_code=raw_code,
                canonical_field_code=None,
                occurrences=count,
                status="draft",
            )
            for raw_code, count in sorted(field_counts.items())
        ]
        return ImportedDocument(
            filename=path.name,
            source_zip=source_zip,
            source_path=str(path),
            document_type=path.suffix.lower().lstrip("."),
            is_tagged=bool(markers),
            marker_count=len(markers),
            red_text_count=len(red_text),
            processing_status="suggested",
            fields=fields,
            patterns=patterns,
        )

    def _persist_document(self, document: ImportedDocument) -> CorpusDocument:
        if self.db is None:
            raise ValueError("A database session is required for persistence.")

        row = CorpusDocument(
            filename=document.filename,
            source_zip=document.source_zip,
            source_path=document.source_path,
            notary_name=document.notary_name,
            project_name=document.project_name,
            document_type=document.document_type,
            act_type=document.act_type,
            is_tagged=document.is_tagged,
            marker_count=document.marker_count,
            red_text_count=document.red_text_count,
            processing_status=document.processing_status,
            error_message=document.error_message,
            metadata_json=json.dumps(document.metadata, ensure_ascii=False),
        )
        self.db.add(row)
        self.db.flush()

        for field in document.fields:
            self.db.add(
                CorpusDocumentField(
                    corpus_document_id=row.id,
                    raw_field_code=field.raw_field_code,
                    canonical_field_code=field.canonical_field_code,
                    example_value=field.example_value,
                    occurrences=field.occurrences,
                    status=field.status,
                    metadata_json=json.dumps(field.metadata, ensure_ascii=False),
                )
            )

        for pattern in document.patterns:
            self.db.add(
                FieldPattern(
                    raw_field_code=pattern.raw_field_code,
                    canonical_field_code=pattern.canonical_field_code,
                    text_before=pattern.text_before,
                    text_after=pattern.text_after,
                    pattern_source_file=pattern.pattern_source_file,
                    frequency=1,
                    confidence=pattern.confidence,
                    status="draft",
                    metadata_json=json.dumps({"location": pattern.location.label()}, ensure_ascii=False),
                )
            )
        return row

    @staticmethod
    def _iter_candidate_documents(root: Path) -> Iterable[Path]:
        if root.is_file():
            if root.suffix.lower() in {".docx", ".doc"}:
                yield root
            return
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".docx", ".doc"}:
                yield path
