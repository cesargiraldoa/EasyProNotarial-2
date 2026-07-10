from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from app.db.session import SessionLocal
from app.services.minuta.inverse_conversion_engine.models import EngineOptions
from app.services.minuta.inverse_conversion_engine.service import InverseConversionEngineService


def _options(args: argparse.Namespace) -> EngineOptions:
    return EngineOptions(
        use_llm=bool(args.use_llm),
        use_semantic=bool(args.use_semantic),
        persist_audit=not bool(args.no_audit),
        limit=args.limit,
    )


def _dump(payload: Any) -> None:
    if hasattr(payload, "model_dump"):
        payload = payload.model_dump()
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the inverse conversion production engine in diagnostic mode.")
    parser.add_argument("--text", help="Plain text to analyze.")
    parser.add_argument("--marker", help="Marker code to analyze.")
    parser.add_argument("--before", default="", help="Context before the marker.")
    parser.add_argument("--after", default="", help="Context after the marker.")
    parser.add_argument("--document-path", help="Local DOCX path to analyze without modifying it.")
    parser.add_argument("--use-llm", action="store_true", help="Opt-in LLM mode. Disabled by default.")
    parser.add_argument("--use-semantic", action="store_true", help="Opt-in semantic retrieval. Falls back if no embeddings exist.")
    parser.add_argument("--no-audit", action="store_true", help="Do not write engine audit rows.")
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args()

    selected = [bool(args.text), bool(args.marker), bool(args.document_path)]
    if sum(selected) != 1:
        parser.error("Use exactly one of --text, --marker, or --document-path.")

    db = SessionLocal()
    try:
        service = InverseConversionEngineService(db)
        options = _options(args)
        if args.text:
            result = service.analyze_text(args.text, options=options)
        elif args.marker:
            result = service.analyze_marker(args.marker, args.before, args.after, options=options)
        else:
            result = service.analyze_document_path(str(Path(args.document_path)), options=options)
        _dump(result)
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
