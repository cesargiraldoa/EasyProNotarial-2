from __future__ import annotations

import argparse
import json

from app.db.session import SessionLocal
from app.services.minuta.inverse_conversion_engine.semantic_indexer import SemanticIndexer


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare or persist inverse conversion semantic index records.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Preview records without writing. Default.")
    mode.add_argument("--commit", action="store_true", help="Write records to inverse_conversion_embeddings only.")
    parser.add_argument("--limit", type=int, default=None, help="Optional total source limit.")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        result = SemanticIndexer(db).index_sources(commit=bool(args.commit), limit=args.limit)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2, default=str))
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
