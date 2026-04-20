from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.legal_entity import LegalEntity

SEED_LEGAL_ENTITIES = [
    {"nit": "830.054.539-0", "name": "Fiduciaria Bancolombia S.A."},
    {"nit": "900.082.107-5", "name": "Constructora Contex S.A.S. BIC"},
    {"nit": "890.903.938-8", "name": "Bancolombia S.A."},
    {"nit": "860.034.313-7", "name": "Banco Davivienda S.A."},
    {"nit": "899.999.284-4", "name": "Fondo Nacional del Ahorro S.A."},
    {"nit": "860.002.964-4", "name": "Banco de Bogotá S.A."},
]


def seed_legal_entities(db: Session) -> tuple[int, int]:
    created = 0
    skipped = 0
    for payload in SEED_LEGAL_ENTITIES:
        nit = payload["nit"].strip()
        name = payload["name"].strip()
        existing = db.query(LegalEntity).filter(LegalEntity.nit == nit).first()
        if existing is not None:
            skipped += 1
            continue
        db.add(LegalEntity(nit=nit, name=name))
        created += 1
    db.commit()
    return created, skipped


def main() -> None:
    with SessionLocal() as db:
        created, skipped = seed_legal_entities(db)
        print(f"[OK] Entidades jurídicas insertadas: {created}; existentes omitidas: {skipped}.")


if __name__ == "__main__":
    main()
