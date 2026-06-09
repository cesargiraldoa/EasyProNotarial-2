from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.case import Case
from app.models.notary import Notary


def resolve_existing_max_sequence(db: Session, sequence_type: str, notary_id: int, year: int) -> int:
    if sequence_type == "internal_case":
        return int(
            db.query(func.max(Case.consecutive))
            .filter(Case.notary_id == notary_id, Case.year == year)
            .scalar()
            or 0
        )
    if sequence_type == "official_deed":
        values = (
            db.query(Case.official_deed_number)
            .filter(Case.notary_id == notary_id, Case.official_deed_year == year, Case.official_deed_number.isnot(None))
            .all()
        )
        max_value = 0
        for (official_number,) in values:
            if not official_number:
                continue
            prefix = str(official_number).split("-", 1)[0]
            if prefix.isdigit():
                max_value = max(max_value, int(prefix))
        return max_value
    return 0


def resolve_next_sequence(db: Session, sequence_type: str, notary_id: int, year: int) -> int:
    from app.models.numbering_sequence import NumberingSequence

    sequence = (
        db.query(NumberingSequence)
        .filter(
            NumberingSequence.sequence_type == sequence_type,
            NumberingSequence.notary_id == notary_id,
            NumberingSequence.year == year,
        )
        .first()
    )
    existing_max = resolve_existing_max_sequence(db, sequence_type, notary_id, year)
    if sequence is None:
        sequence = NumberingSequence(sequence_type=sequence_type, notary_id=notary_id, year=year, current_value=existing_max)
        db.add(sequence)
        db.flush()
    elif sequence.current_value < existing_max:
        sequence.current_value = existing_max
        db.flush()
    sequence.current_value += 1
    db.flush()
    return sequence.current_value


def resolve_case_internal_number_prefix(notary: Notary) -> str:
    slug = (notary.slug or "").strip().lower()
    if slug and len(slug) <= 26 and all(char.isalnum() or char == "-" for char in slug):
        return slug
    return str(notary.id)


def build_internal_case_number(notary: Notary, year: int, consecutive: int) -> str:
    return f"CAS-{resolve_case_internal_number_prefix(notary)}-{year}-{consecutive:04d}"


def is_case_number_integrity_error(error: IntegrityError) -> bool:
    message = str(error.orig).lower()
    return any(
        marker in message
        for marker in (
            "uq_cases_internal_case_number",
            "uq_cases_notary_year_consecutive",
            "cases.internal_case_number",
            "cases.notary_id",
            "cases.year",
            "cases.consecutive",
            "unique constraint failed: cases.internal_case_number",
            "unique constraint failed: cases.notary_id, cases.year, cases.consecutive",
            "duplicate key value violates unique constraint",
        )
    )


def build_case_number_conflict_detail(notary: Notary, year: int, consecutive: int) -> str:
    return (
        "No fue posible crear la minuta porque el identificador interno ya existe. "
        f"Se intentó {build_internal_case_number(notary, year, consecutive)}. "
        "Intenta de nuevo; el sistema recalculará el consecutivo."
    )
