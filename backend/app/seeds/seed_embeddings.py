from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.session import SessionLocal
from app.services.legal_rag import seed_legal_embeddings


def main() -> None:
    with SessionLocal() as session:
        result = seed_legal_embeddings(session)
    print(
        "[OK] Embeddings corpus juridico "
        f"cargados (+{result['created']}/~{result['updated']}) "
        f"provider={result['provider']} model={result['model']}."
    )


if __name__ == "__main__":
    main()
