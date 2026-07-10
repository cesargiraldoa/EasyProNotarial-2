from __future__ import annotations

import argparse
from pathlib import Path

from app.db.session import SessionLocal
from app.services.minuta.inverse_conversion_catalog.corpus_importer import CorpusImporter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import notarial DOCX corpus into the inverse conversion catalog.")
    parser.add_argument("--input-path", required=True, help="ZIP file, DOCX file or folder with notarial documents.")
    parser.add_argument("--output-dir", required=True, help="Directory where JSON/CSV reports will be written.")
    parser.add_argument("--dry-run", action="store_true", help="Generate reports without database writes.")
    parser.add_argument("--commit", action="store_true", help="Persist imported corpus rows to the database.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    dry_run = args.dry_run or not args.commit
    db = SessionLocal() if args.commit else None
    try:
        importer = CorpusImporter(db=db)
        result = importer.import_path(
            input_path=Path(args.input_path),
            output_dir=Path(args.output_dir),
            dry_run=dry_run,
            commit=args.commit,
        )
        print(
            "Import completed: "
            f"documents={len(result.documents)} "
            f"errors={result.error_count} "
            f"unique_fields={len(result.field_frequency)} "
            f"patterns={len(result.patterns)}"
        )
        return 0
    finally:
        if db is not None:
            db.close()


if __name__ == "__main__":
    raise SystemExit(main())
