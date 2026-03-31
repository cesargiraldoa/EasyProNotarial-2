import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, aliased, joinedload

from app.core.deps import get_current_user, get_db, require_roles
from app.models.case import Case
from app.models.case_state_definition import CaseStateDefinition
from app.models.case_timeline_event import CaseTimelineEvent
from app.models.notary import Notary
from app.models.user import User
from app.schemas.case import (
    CaseCreate,
    CaseDetail,
    CaseFilterOptions,
    CaseOwnerUpdate,
    CaseStateDefinitionSummary,
    CaseStateUpdate,
    CaseSummary,
    CaseTimelineEventCreate,
    CaseTimelineEventSummary,
    CaseUpdate,
)

router = APIRouter(prefix="/cases", tags=["cases"])

DEFAULT_CASE_TYPE = "escritura"


def safe_json(value: str | None) -> str:
    if value is None or not value.strip():
        return "{}"
    try:
        return json.dumps(json.loads(value), ensure_ascii=False)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="metadata_json debe ser JSON válido.") from exc


def load_case_or_404(db: Session, case_id: int) -> Case:
    case = (
        db.query(Case)
        .options(
            joinedload(Case.notary),
            joinedload(Case.current_owner_user),
            joinedload(Case.client_user),
            joinedload(Case.protocolist_user),
            joinedload(Case.approver_user),
            joinedload(Case.titular_notary_user),
            joinedload(Case.substitute_notary_user),
            joinedload(Case.timeline_events).joinedload(CaseTimelineEvent.actor_user),
        )
        .filter(Case.id == case_id)
        .first()
    )
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso no encontrado.")
    return case


def get_state_definitions(db: Session, case_type: str) -> list[CaseStateDefinition]:
    definitions = (
        db.query(CaseStateDefinition)
        .filter(CaseStateDefinition.case_type == case_type, CaseStateDefinition.is_active.is_(True))
        .order_by(CaseStateDefinition.step_order.asc())
        .all()
    )
    if definitions:
        return definitions
    return (
        db.query(CaseStateDefinition)
        .filter(CaseStateDefinition.case_type == DEFAULT_CASE_TYPE, CaseStateDefinition.is_active.is_(True))
        .order_by(CaseStateDefinition.step_order.asc())
        .all()
    )


def serialize_timeline_event(event: CaseTimelineEvent) -> CaseTimelineEventSummary:
    return CaseTimelineEventSummary(
        id=event.id,
        event_type=event.event_type,
        from_state=event.from_state,
        to_state=event.to_state,
        comment=event.comment,
        metadata_json=event.metadata_json,
        actor_user_id=event.actor_user_id,
        actor_user_name=event.actor_user.full_name if event.actor_user else None,
        created_at=event.created_at,
    )


def serialize_case_summary(case: Case) -> CaseSummary:
    return CaseSummary(
        id=case.id,
        notary_id=case.notary_id,
        notary_label=case.notary.notary_label,
        case_type=case.case_type,
        act_type=case.act_type,
        consecutive=case.consecutive,
        year=case.year,
        current_state=case.current_state,
        current_owner_user_id=case.current_owner_user_id,
        current_owner_user_name=case.current_owner_user.full_name if case.current_owner_user else None,
        client_user_id=case.client_user_id,
        client_user_name=case.client_user.full_name if case.client_user else None,
        protocolist_user_id=case.protocolist_user_id,
        protocolist_user_name=case.protocolist_user.full_name if case.protocolist_user else None,
        approver_user_id=case.approver_user_id,
        approver_user_name=case.approver_user.full_name if case.approver_user else None,
        titular_notary_user_id=case.titular_notary_user_id,
        titular_notary_user_name=case.titular_notary_user.full_name if case.titular_notary_user else None,
        substitute_notary_user_id=case.substitute_notary_user_id,
        substitute_notary_user_name=case.substitute_notary_user.full_name if case.substitute_notary_user else None,
        requires_client_review=case.requires_client_review,
        final_signed_uploaded=case.final_signed_uploaded,
        metadata_json=case.metadata_json,
        created_at=case.created_at,
        updated_at=case.updated_at,
    )


def serialize_case_detail(db: Session, case: Case) -> CaseDetail:
    summary = serialize_case_summary(case)
    state_definitions = [CaseStateDefinitionSummary.model_validate(item) for item in get_state_definitions(db, case.case_type)]
    return CaseDetail(
        **summary.model_dump(),
        state_definitions=state_definitions,
        timeline_events=[serialize_timeline_event(item) for item in case.timeline_events],
    )


def validate_user_reference(db: Session, user_id: int | None, field_name: str) -> None:
    if user_id is None:
        return
    if db.query(User.id).filter(User.id == user_id, User.is_active.is_(True)).first() is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"{field_name} no existe o está inactivo.")


def resolve_next_consecutive(db: Session, notary_id: int, year: int) -> int:
    current = db.query(func.max(Case.consecutive)).filter(Case.notary_id == notary_id, Case.year == year).scalar()
    return (current or 0) + 1


def hydrate_case(db: Session, case: Case, payload: CaseCreate | CaseUpdate) -> None:
    if db.query(Notary.id).filter(Notary.id == payload.notary_id).first() is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La notaría no existe.")

    for user_id, label in [
        (payload.current_owner_user_id, "El responsable actual"),
        (payload.client_user_id, "El cliente"),
        (payload.protocolist_user_id, "El protocolista"),
        (payload.approver_user_id, "El aprobador"),
        (payload.titular_notary_user_id, "El notario titular"),
        (payload.substitute_notary_user_id, "El notario suplente"),
    ]:
        validate_user_reference(db, user_id, label)

    state_codes = {item.code for item in get_state_definitions(db, payload.case_type)}
    if payload.current_state not in state_codes:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El estado actual no está configurado para el tipo de caso.")

    case.notary_id = payload.notary_id
    case.case_type = payload.case_type.strip()
    case.act_type = payload.act_type.strip()
    case.current_state = payload.current_state
    case.current_owner_user_id = payload.current_owner_user_id
    case.client_user_id = payload.client_user_id
    case.protocolist_user_id = payload.protocolist_user_id
    case.approver_user_id = payload.approver_user_id
    case.titular_notary_user_id = payload.titular_notary_user_id
    case.substitute_notary_user_id = payload.substitute_notary_user_id
    case.requires_client_review = payload.requires_client_review
    case.final_signed_uploaded = payload.final_signed_uploaded
    case.metadata_json = safe_json(payload.metadata_json)


def append_timeline(db: Session, case_id: int, actor_user_id: int | None, event_type: str, from_state: str | None = None, to_state: str | None = None, comment: str | None = None, metadata: dict | None = None) -> None:
    db.add(
        CaseTimelineEvent(
            case_id=case_id,
            actor_user_id=actor_user_id,
            event_type=event_type,
            from_state=from_state,
            to_state=to_state,
            comment=comment,
            metadata_json=json.dumps(metadata or {}, ensure_ascii=False) if metadata is not None else None,
        )
    )


@router.get("", response_model=list[CaseSummary])
def list_cases(
    current_state: str | None = Query(default=None),
    case_type: str | None = Query(default=None),
    notary_id: int | None = Query(default=None),
    current_owner_user_id: int | None = Query(default=None),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    owner_alias = aliased(User)
    query = (
        db.query(Case)
        .options(
            joinedload(Case.notary),
            joinedload(Case.current_owner_user),
            joinedload(Case.client_user),
            joinedload(Case.protocolist_user),
            joinedload(Case.approver_user),
            joinedload(Case.titular_notary_user),
            joinedload(Case.substitute_notary_user),
        )
        .outerjoin(owner_alias, owner_alias.id == Case.current_owner_user_id)
        .order_by(Case.updated_at.desc(), Case.id.desc())
    )
    if current_state:
        query = query.filter(Case.current_state == current_state)
    if case_type:
        query = query.filter(Case.case_type == case_type)
    if notary_id:
        query = query.filter(Case.notary_id == notary_id)
    if current_owner_user_id:
        query = query.filter(Case.current_owner_user_id == current_owner_user_id)
    if q:
        search = f"%{q.strip()}%"
        query = query.join(Notary, Notary.id == Case.notary_id).filter(
            or_(
                Case.act_type.ilike(search),
                Case.case_type.ilike(search),
                Notary.notary_label.ilike(search),
                owner_alias.full_name.ilike(search),
            )
        )
    return [serialize_case_summary(item) for item in query.all()]


@router.get("/filters", response_model=CaseFilterOptions)
def get_case_filters(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cases = db.query(Case).options(joinedload(Case.notary), joinedload(Case.current_owner_user)).all()
    return CaseFilterOptions(
        case_types=sorted({item.case_type for item in cases if item.case_type}),
        act_types=sorted({item.act_type for item in cases if item.act_type}),
        states=sorted({item.current_state for item in cases if item.current_state}),
        owners=sorted({item.current_owner_user.full_name for item in cases if item.current_owner_user}),
        notaries=sorted({item.notary.notary_label for item in cases if item.notary}),
    )


@router.get("/state-definitions", response_model=list[CaseStateDefinitionSummary])
def list_state_definitions(case_type: str = Query(default=DEFAULT_CASE_TYPE), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return [CaseStateDefinitionSummary.model_validate(item) for item in get_state_definitions(db, case_type)]


@router.get("/{case_id}", response_model=CaseDetail)
def get_case(case_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    case = load_case_or_404(db, case_id)
    return serialize_case_detail(db, case)


@router.post("", response_model=CaseDetail, status_code=status.HTTP_201_CREATED)
def create_case(payload: CaseCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary", "protocolist", "approver", "notary"))):
    now = datetime.utcnow()
    year = payload.year or now.year
    consecutive = payload.consecutive or resolve_next_consecutive(db, payload.notary_id, year)
    case = Case(consecutive=consecutive, year=year, current_state=payload.current_state)
    hydrate_case(db, case, payload)
    db.add(case)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un caso con ese consecutivo para la notaría y año.") from exc
    append_timeline(db, case.id, current_user.id, "case_created", None, case.current_state, comment="Caso creado", metadata={"case_type": case.case_type, "act_type": case.act_type})
    db.commit()
    return serialize_case_detail(db, load_case_or_404(db, case.id))


@router.put("/{case_id}", response_model=CaseDetail)
def update_case(case_id: int, payload: CaseUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary", "protocolist", "approver", "notary"))):
    case = load_case_or_404(db, case_id)
    previous_owner = case.current_owner_user.full_name if case.current_owner_user else None
    previous_state = case.current_state
    case.consecutive = payload.consecutive
    case.year = payload.year
    hydrate_case(db, case, payload)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un caso con ese consecutivo para la notaría y año.") from exc
    if previous_state != case.current_state:
        append_timeline(db, case.id, current_user.id, "state_changed", previous_state, case.current_state, comment="Estado actualizado")
    current_owner = case.current_owner_user.full_name if case.current_owner_user else None
    if previous_owner != current_owner:
        append_timeline(db, case.id, current_user.id, "owner_changed", None, None, comment=f"Responsable actual: {current_owner or 'Sin asignar'}")
    db.commit()
    return serialize_case_detail(db, load_case_or_404(db, case.id))


@router.patch("/{case_id}/state", response_model=CaseDetail)
def update_case_state(case_id: int, payload: CaseStateUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary", "protocolist", "approver", "notary"))):
    case = load_case_or_404(db, case_id)
    allowed_states = {item.code for item in get_state_definitions(db, case.case_type)}
    if payload.current_state not in allowed_states:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El estado no está configurado para este tipo de caso.")
    previous_state = case.current_state
    case.current_state = payload.current_state
    append_timeline(db, case.id, current_user.id, "state_changed", previous_state, case.current_state, payload.comment)
    db.commit()
    return serialize_case_detail(db, load_case_or_404(db, case.id))


@router.patch("/{case_id}/owner", response_model=CaseDetail)
def update_case_owner(case_id: int, payload: CaseOwnerUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary", "protocolist", "approver", "notary"))):
    case = load_case_or_404(db, case_id)
    validate_user_reference(db, payload.current_owner_user_id, "El responsable actual")
    previous_owner = case.current_owner_user.full_name if case.current_owner_user else None
    case.current_owner_user_id = payload.current_owner_user_id
    new_owner = db.query(User).filter(User.id == payload.current_owner_user_id).first().full_name if payload.current_owner_user_id else None
    append_timeline(db, case.id, current_user.id, "owner_changed", None, None, payload.comment or f"Responsable actual: {new_owner or 'Sin asignar'}", metadata={"previous_owner": previous_owner, "new_owner": new_owner})
    db.commit()
    return serialize_case_detail(db, load_case_or_404(db, case.id))


@router.post("/{case_id}/timeline-events", response_model=CaseDetail)
def add_case_timeline_event(case_id: int, payload: CaseTimelineEventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    case = load_case_or_404(db, case_id)
    append_timeline(
        db,
        case.id,
        current_user.id,
        "comment_added",
        case.current_state,
        case.current_state,
        payload.comment,
        metadata=json.loads(payload.metadata_json) if payload.metadata_json else None,
    )
    db.commit()
    return serialize_case_detail(db, load_case_or_404(db, case.id))
