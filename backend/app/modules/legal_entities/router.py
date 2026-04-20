from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_db, require_roles
from app.models.legal_entity import LegalEntity
from app.models.legal_entity_representative import LegalEntityRepresentative
from app.models.person import Person
from app.models.user import User
from app.schemas.legal_entity import (
    LegalEntityCreate,
    LegalEntityOut,
    LegalEntityRepresentativeCreate,
    LegalEntityRepresentativeOut,
)

router = APIRouter(prefix="/legal-entities", tags=["legal-entities"])


def serialize_legal_entity(entity: LegalEntity) -> LegalEntityOut:
    return LegalEntityOut.model_validate(entity)


def serialize_representative(item: LegalEntityRepresentative) -> LegalEntityRepresentativeOut:
    person = item.person
    return LegalEntityRepresentativeOut(
        id=item.id,
        legal_entity_id=item.legal_entity_id,
        person_id=item.person_id,
        person_name=person.full_name if person else "",
        person_document=f"{person.document_type} {person.document_number}".strip() if person else "",
        power_type=item.power_type,
        is_active=item.is_active,
    )


def load_entity_or_404(db: Session, entity_id: int) -> LegalEntity:
    entity = db.query(LegalEntity).filter(LegalEntity.id == entity_id).first()
    if entity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entidad jurídica no encontrada.")
    return entity


def load_person_or_404(db: Session, person_id: int) -> Person:
    person = db.query(Person).filter(Person.id == person_id).first()
    if person is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona no encontrada.")
    return person


@router.get("", response_model=list[LegalEntityOut])
def list_legal_entities(
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(LegalEntity).order_by(LegalEntity.name.asc())
    if q:
        search = f"%{q.strip()}%"
        query = query.filter(or_(LegalEntity.name.ilike(search), LegalEntity.nit.ilike(search)))
    return [serialize_legal_entity(item) for item in query.all()]


@router.post("", response_model=LegalEntityOut)
def create_legal_entity(
    payload: LegalEntityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "admin_notary", "protocolist", "approver", "notary")),
):
    nit = payload.nit.strip()
    existing = db.query(LegalEntity).filter(LegalEntity.nit == nit).first()
    if existing is not None:
        return serialize_legal_entity(existing)

    entity = LegalEntity(
        nit=nit,
        name=payload.name.strip(),
        legal_representative=payload.legal_representative.strip() if payload.legal_representative else None,
        municipality=payload.municipality.strip() if payload.municipality else None,
        address=payload.address.strip() if payload.address else None,
        phone=payload.phone.strip() if payload.phone else None,
        email=payload.email.strip().lower() if payload.email else None,
    )
    db.add(entity)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.query(LegalEntity).filter(LegalEntity.nit == nit).first()
        if existing is None:
            raise
        return serialize_legal_entity(existing)
    db.refresh(entity)
    return serialize_legal_entity(entity)


@router.get("/{entity_id}/representatives", response_model=list[LegalEntityRepresentativeOut])
def list_entity_representatives(
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    load_entity_or_404(db, entity_id)
    representatives = (
        db.query(LegalEntityRepresentative)
        .options(joinedload(LegalEntityRepresentative.person))
        .filter(
            LegalEntityRepresentative.legal_entity_id == entity_id,
            LegalEntityRepresentative.is_active.is_(True),
        )
        .order_by(LegalEntityRepresentative.id.asc())
        .all()
    )
    return [serialize_representative(item) for item in representatives]


@router.post("/{entity_id}/representatives", response_model=LegalEntityRepresentativeOut)
def create_or_reactivate_representative(
    entity_id: int,
    payload: LegalEntityRepresentativeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "admin_notary", "protocolist", "approver", "notary")),
):
    entity = load_entity_or_404(db, entity_id)
    person = load_person_or_404(db, payload.person_id)

    representative = (
        db.query(LegalEntityRepresentative)
        .options(joinedload(LegalEntityRepresentative.person))
        .filter(
            LegalEntityRepresentative.legal_entity_id == entity.id,
            LegalEntityRepresentative.person_id == person.id,
        )
        .first()
    )
    if representative is None:
        representative = LegalEntityRepresentative(
            legal_entity_id=entity.id,
            person_id=person.id,
            power_type=payload.power_type.strip() if payload.power_type else None,
            is_active=True,
        )
        db.add(representative)
    else:
        representative.power_type = payload.power_type.strip() if payload.power_type else representative.power_type
        representative.is_active = True

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No fue posible registrar el apoderado.") from exc

    db.refresh(representative)
    representative = (
        db.query(LegalEntityRepresentative)
        .options(joinedload(LegalEntityRepresentative.person))
        .filter(LegalEntityRepresentative.id == representative.id)
        .first()
    )
    if representative is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Apoderado no encontrado.")
    return serialize_representative(representative)
