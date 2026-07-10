from __future__ import annotations

import argparse
from pathlib import Path

from app.db.session import SessionLocal
from app.services.minuta.inverse_conversion_catalog.corpus_reporter import CorpusReporter
from app.services.minuta.inverse_conversion_catalog.models import (
    CorpusDocument,
    CorpusDocumentField,
    FieldAlias,
    FieldDefinition,
    FieldPattern,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export inverse conversion catalog reports as JSON and CSV.")
    parser.add_argument("--output-dir", required=True, help="Directory where JSON/CSV reports will be written.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    db = SessionLocal()
    try:
        total_documents = db.query(CorpusDocument).count()
        total_errors = db.query(CorpusDocument).filter(CorpusDocument.processing_status.in_(["error", "unsupported"])).count()
        total_tagged = db.query(CorpusDocument).filter(CorpusDocument.is_tagged.is_(True)).count()
        definitions = db.query(FieldDefinition).all()
        aliases = db.query(FieldAlias).all()
        patterns = db.query(FieldPattern).all()
        document_fields = db.query(CorpusDocumentField).all()
        field_frequency: dict[str, int] = {}
        for row in document_fields:
            field_frequency[row.raw_field_code] = field_frequency.get(row.raw_field_code, 0) + int(row.occurrences or 0)

        fields_by_notary_project: dict[tuple[str, str, str], int] = {}
        joined_rows = (
            db.query(
                CorpusDocument.notary_name,
                CorpusDocument.project_name,
                CorpusDocumentField.raw_field_code,
                CorpusDocumentField.occurrences,
            )
            .join(CorpusDocumentField, CorpusDocumentField.corpus_document_id == CorpusDocument.id)
            .all()
        )
        for notary_name, project_name, raw_field_code, occurrences in joined_rows:
            key = (notary_name or "", project_name or "", raw_field_code)
            fields_by_notary_project[key] = fields_by_notary_project.get(key, 0) + int(occurrences or 0)

        payload = {
            "summary": [
                {
                    "total_documents_processed": total_documents,
                    "total_documents_with_error": total_errors,
                    "total_documents_tagged": total_tagged,
                    "total_unique_fields": len({alias.raw_field_code for alias in aliases}),
                    "total_suggested_normalized_fields": len(definitions),
                    "total_patterns": len(patterns),
                }
            ],
            "top_fields_by_frequency": [
                {"raw_field_code": raw_field_code, "frequency": frequency}
                for raw_field_code, frequency in sorted(field_frequency.items(), key=lambda item: (-item[1], item[0]))[:50]
            ],
            "fields_by_notary_project": [
                {
                    "notary_name": notary_name,
                    "project_name": project_name,
                    "raw_field_code": raw_field_code,
                    "frequency": frequency,
                }
                for (notary_name, project_name, raw_field_code), frequency in sorted(
                    fields_by_notary_project.items(),
                    key=lambda item: (item[0][0], item[0][1], -item[1], item[0][2]),
                )
            ],
            "field_definitions": [
                {
                    "field_code": row.field_code,
                    "display_name": row.display_name,
                    "status": row.status,
                    "confidence": row.confidence,
                    "field_group": row.field_group,
                    "legal_role": row.legal_role,
                    "act_type": row.act_type,
                }
                for row in definitions
            ],
            "field_aliases": [
                {
                    "raw_field_code": row.raw_field_code,
                    "canonical_field_code": row.canonical_field_code,
                    "frequency": row.frequency,
                    "status": row.status,
                    "source": row.source,
                }
                for row in aliases
            ],
            "field_patterns": [
                {
                    "raw_field_code": row.raw_field_code,
                    "canonical_field_code": row.canonical_field_code,
                    "notary_name": row.notary_name,
                    "project_name": row.project_name,
                    "document_type": row.document_type,
                    "act_type": row.act_type,
                    "text_before": row.text_before,
                    "text_after": row.text_after,
                    "frequency": row.frequency,
                    "confidence": row.confidence,
                    "status": row.status,
                }
                for row in patterns
            ],
            "normalization_conflicts": [
                {
                    "raw_field_code": row.raw_field_code,
                    "canonical_field_code": row.canonical_field_code,
                    "frequency": row.frequency,
                    "status": row.status,
                }
                for row in aliases
                if row.status == "conflict"
            ],
        }

        CorpusReporter().write_catalog_report(payload, Path(args.output_dir), stem="field_catalog_export")
        print(
            "Catalog export completed: "
            f"documents={total_documents} definitions={len(definitions)} aliases={len(aliases)} patterns={len(patterns)}"
        )
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
