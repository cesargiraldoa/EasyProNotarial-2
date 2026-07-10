from __future__ import annotations

import argparse
from pathlib import Path

from app.db.session import SessionLocal
from app.services.minuta.inverse_conversion_catalog.corpus_reporter import CorpusReporter
from app.services.minuta.inverse_conversion_catalog.field_catalog_service import FieldCatalogService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build suggested field catalog from imported corpus fields.")
    parser.add_argument("--output-dir", required=True, help="Directory where normalization reports will be written.")
    parser.add_argument("--dry-run", action="store_true", help="Build report without committing catalog rows.")
    parser.add_argument("--commit", action="store_true", help="Persist suggested/conflict catalog rows.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    db = SessionLocal()
    try:
        payload = FieldCatalogService(db=db).build_from_database(commit=args.commit and not args.dry_run)
        if args.dry_run or not args.commit:
            db.rollback()
        CorpusReporter().write_catalog_report(payload, Path(args.output_dir), stem="field_catalog_normalization")
        print(
            "Catalog build completed: "
            f"definitions={len(payload['field_definitions'])} "
            f"aliases={len(payload['field_aliases'])} "
            f"conflicts={len(payload['conflicts'])}"
        )
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
