from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_roles
from app.models.person import Person
from app.models.user import User
from app.schemas.person import PersonCreate, PersonSummary, PersonUpdate

router = APIRouter(prefix="/persons", tags=["persons"])


def serialize_person(person: Person) -> PersonSummary:
    return PersonSummary.model_validate(person)


def safe_person_json(value: str | None) -> str:
    if not value:
        return "{}"
    return json.dumps(json.loads(value), ensure_ascii=False)


def load_person_or_404(db: Session, person_id: int) -> Person:
    person = db.query(Person).filter(Person.id == person_id).first()
    if person is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona no encontrada.")
    return person


def hydrate_person(person: Person, payload: PersonCreate | PersonUpdate) -> None:
    person.document_type = payload.document_type.strip().upper()
    person.document_number = payload.document_number.strip()
    person.full_name = payload.full_name.strip()
    person.sex = payload.sex.strip() if payload.sex else None
    person.nationality = payload.nationality.strip() if payload.nationality else None
    person.marital_status = payload.marital_status.strip() if payload.marital_status else None
    person.profession = payload.profession.strip() if payload.profession else None
    person.municipality = payload.municipality.strip() if payload.municipality else None
    person.is_transient = payload.is_transient
    person.phone = payload.phone.strip() if payload.phone else None
    person.address = payload.address.strip() if payload.address else None
    person.email = str(payload.email).strip().lower() if payload.email else None
    person.metadata_json = safe_person_json(payload.metadata_json)


@router.get("", response_model=list[PersonSummary])
def list_persons(q: str | None = Query(default=None), document_type: str | None = Query(default=None), document_number: str | None = Query(default=None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Person).order_by(Person.full_name.asc())
    if document_type and document_number:
        query = query.filter(Person.document_type == document_type.upper().strip(), Person.document_number == document_number.strip())
    elif q:
        search = f"%{q.strip()}%"
        query = query.filter(or_(Person.full_name.ilike(search), Person.document_number.ilike(search), Person.email.ilike(search)))
    return [serialize_person(item) for item in query.limit(25).all()]


@router.get("/{person_id}", response_model=PersonSummary)
def get_person(person_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return serialize_person(load_person_or_404(db, person_id))


@router.post("", response_model=PersonSummary, status_code=status.HTTP_201_CREATED)
def create_person(payload: PersonCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary", "protocolist", "approver", "notary"))):
    person = Person()
    hydrate_person(person, payload)
    db.add(person)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe una persona con ese tipo y número de documento.") from exc
    db.refresh(person)
    return serialize_person(person)


@router.put("/{person_id}", response_model=PersonSummary)
def update_person(person_id: int, payload: PersonUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary", "protocolist", "approver", "notary"))):
    person = load_person_or_404(db, person_id)
    hydrate_person(person, payload)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe una persona con ese tipo y número de documento.") from exc
    db.refresh(person)
    return serialize_person(person)

