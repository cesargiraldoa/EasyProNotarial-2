from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.legal_entity import LegalEntity
from app.models.legal_entity_representative import LegalEntityRepresentative
from app.models.person import Person

# Apoderados de banco extraídos de escrituras reales de compraventa + hipoteca
# de la Notaría 16 de Medellín. Son agentes bancarios que comparecen y firman
# en instrumentos públicos. Contiene datos personales (cédula): mantener solo
# en repositorios privados; la fuente de verdad operativa es la BD, editable
# desde la app (POST /legal-entities/{id}/representatives).
SEED_BANK_REPRESENTATIVES = [
    {
        "bank_nit": "890.903.938-8",  # Bancolombia S.A.
        "apoderados": [
            {"document_number": "32.182.009", "full_name": "SUSANA MARIA ESPINOSA PACHECO", "power_type": "Apoderada Especial"},
            {"document_number": "43.040.886", "full_name": "CLAUDIA HELENA MAZO ARBOLEDA", "power_type": "Apoderada Especial"},
            {"document_number": "21.394.162", "full_name": "MARIA OLGA GUADALUPE MARTINEZ GIRALDO", "power_type": "Apoderada Especial"},
            {"document_number": "32.352.735", "full_name": "DIANA MARCELA BUILES CORREA", "power_type": "Representante Legal Suplente"},
        ],
    },
]


def _get_or_create_person(db: Session, document_number: str, full_name: str) -> Person:
    existing = (
        db.query(Person)
        .filter(Person.document_type == "CC", Person.document_number == document_number)
        .first()
    )
    if existing is not None:
        return existing
    person = Person(
        document_type="CC",
        document_number=document_number,
        full_name=full_name,
        municipality="Medellín",
        is_transient=False,
    )
    db.add(person)
    db.flush()  # asignar person.id antes de crear la representación
    return person


def seed_bank_representatives(db: Session) -> tuple[int, int]:
    """Siembra los apoderados de banco. Requiere que las entidades ya existan
    (seed_legal_entities). Idempotente por (document_type, document_number) y
    por la restricción única (legal_entity_id, person_id)."""
    created = 0
    skipped = 0
    for group in SEED_BANK_REPRESENTATIVES:
        bank = db.query(LegalEntity).filter(LegalEntity.nit == group["bank_nit"]).first()
        if bank is None:
            skipped += len(group["apoderados"])
            continue
        for ap in group["apoderados"]:
            person = _get_or_create_person(db, ap["document_number"].strip(), ap["full_name"].strip())
            existing_rep = (
                db.query(LegalEntityRepresentative)
                .filter(
                    LegalEntityRepresentative.legal_entity_id == bank.id,
                    LegalEntityRepresentative.person_id == person.id,
                )
                .first()
            )
            if existing_rep is not None:
                skipped += 1
                continue
            db.add(
                LegalEntityRepresentative(
                    legal_entity_id=bank.id,
                    person_id=person.id,
                    power_type=ap["power_type"],
                    is_active=True,
                )
            )
            created += 1
    db.commit()
    return created, skipped


def main() -> None:
    with SessionLocal() as db:
        created, skipped = seed_bank_representatives(db)
        print(f"[OK] Representantes de banco insertados: {created}; existentes/omitidos: {skipped}.")


if __name__ == "__main__":
    main()
