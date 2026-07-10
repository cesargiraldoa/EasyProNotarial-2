from __future__ import annotations

import argparse
import json

from app.db.session import SessionLocal
from app.services.minuta.inverse_conversion_rag.repository import InverseConversionReadOnlyRepository
from app.services.minuta.inverse_conversion_rag.retriever import InverseConversionRetriever


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query the read-only inverse conversion RAG layer.")
    parser.add_argument("--field-code", help="Field code to retrieve evidence for.")
    parser.add_argument("--text", help="Free text context to search.")
    parser.add_argument("--before", help="Text before a marker.")
    parser.add_argument("--after", help="Text after a marker.")
    parser.add_argument("--limit", type=int, default=5)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    db = SessionLocal()
    repository = InverseConversionReadOnlyRepository(db)
    try:
        retriever = InverseConversionRetriever(repository)
        if args.field_code and (args.before or args.after):
            result = retriever.retrieve_candidates_for_marker(args.field_code, args.before, args.after, limit=args.limit)
        elif args.field_code:
            result = retriever.retrieve_by_field_code(args.field_code, limit=args.limit)
        elif args.text:
            result = retriever.retrieve_by_text_context(args.text, limit=args.limit)
        elif args.before or args.after:
            result = retriever.retrieve_by_before_after(args.before, args.after, limit=args.limit)
        else:
            raise SystemExit("Provide --field-code, --text, or --before/--after.")

        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0
    finally:
        repository.close()
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
