import re
import unicodedata

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import ValidationError
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, aliased, joinedload

from app.core.deps import get_current_user, get_db, has_role, require_roles
from app.models.notary import Notary
from app.models.notary_commercial_activity import NotaryCommercialActivity
from app.models.notary_crm_audit_log import NotaryCrmAuditLog
from app.models.user import User
from app.schemas.notary import (
    CommercialActivityCreate,
    CommercialActivitySummary,
    NotaryCreate,
    NotaryDetail,
    NotaryFileImportRequest,
    NotaryFilterOptions,
    NotaryImportRequest,
    NotaryImportResult,
    NotaryImportRowError,
    NotaryImportSummary,
    NotaryStatusUpdate,
    NotarySummary,
    NotaryUpdate,
)
from app.services.notary_imports import DEFAULT_ANTIOQUIA_SOURCE_PATH, NotaryImportFileError, load_xlsx_rows

router = APIRouter(prefix="/notaries", tags=["notaries"])

COMMERCIAL_STATUSES = [
    "prospecto",
    "contactado",
    "en seguimiento",
    "reunión agendada",
    "propuesta enviada",
    "negociación",
    "cerrado ganado",
    "cerrado perdido",
    "no interesado",
]
PRIORITIES = ["baja", "media", "alta", "crítica"]


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", normalized.lower()).strip("-")
    return cleaned or "notary"


def ensure_unique_slug(db: Session, base_slug: str, current_id: int | None = None) -> str:
    slug = base_slug
    counter = 2
    while True:
        query = db.query(Notary).filter(Notary.slug == slug)
        if current_id is not None:
            query = query.filter(Notary.id != current_id)
        if query.first() is None:
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


def normalize_catalog_field(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def normalize_email(value: str | None) -> str | None:
    normalized = normalize_catalog_field(value)
    return normalized.lower() if normalized else None


def build_catalog_identity_key(municipality: str, notary_label: str, email: str | None) -> str:
    normalized_email = email or "no-email"
    return "::".join([slugify(municipality), slugify(notary_label), slugify(normalized_email)])


def duplicate_key_string(municipality: str, notary_label: str, email: str | None) -> str:
    return " | ".join(part for part in [municipality, notary_label, email] if part)


def commercial_owner_display(notary: Notary) -> str | None:
    if notary.commercial_owner_user is not None:
        return notary.commercial_owner_user.full_name
    return notary.commercial_owner


def serialize_activity(activity: NotaryCommercialActivity) -> CommercialActivitySummary:
    return CommercialActivitySummary(
        id=activity.id,
        notary_id=activity.notary_id,
        occurred_at=activity.occurred_at,
        management_type=activity.management_type,
        comment=activity.comment,
        responsible=activity.responsible,
        responsible_user_id=activity.responsible_user_id,
        responsible_user_name=activity.responsible_user.full_name if activity.responsible_user else None,
        result=activity.result,
        next_action=activity.next_action,
    )


def serialize_audit(log: NotaryCrmAuditLog):
    return {
        "id": log.id,
        "event_type": log.event_type,
        "field_name": log.field_name,
        "old_value": log.old_value,
        "new_value": log.new_value,
        "comment": log.comment,
        "actor_user_id": log.actor_user_id,
        "actor_user_name": log.actor_user.full_name if log.actor_user else None,
        "created_at": log.created_at,
    }


def attach_notary_summary(notary: Notary, activity_count: int) -> NotarySummary:
    return NotarySummary.model_validate(
        {
            **notary.__dict__,
            "activity_count": activity_count,
            "commercial_owner_display": commercial_owner_display(notary),
            "commercial_owner_user_name": notary.commercial_owner_user.full_name if notary.commercial_owner_user else None,
        }
    )


def attach_notary_detail(notary: Notary) -> NotaryDetail:
    return NotaryDetail.model_validate(
        {
            **notary.__dict__,
            "activity_count": len(notary.commercial_activities),
            "commercial_owner_display": commercial_owner_display(notary),
            "commercial_owner_user_name": notary.commercial_owner_user.full_name if notary.commercial_owner_user else None,
            "commercial_activities": [serialize_activity(activity).model_dump() for activity in notary.commercial_activities],
            "crm_audit_logs": [serialize_audit(log) for log in notary.crm_audit_logs],
        }
    )


def find_duplicate_notary(
    db: Session,
    municipality: str,
    notary_label: str,
    email: str | None,
    current_id: int | None = None,
) -> Notary | None:
    identity_key = build_catalog_identity_key(municipality, notary_label, email)
    query = db.query(Notary).filter(Notary.catalog_identity_key == identity_key)
    if current_id is not None:
        query = query.filter(Notary.id != current_id)
    return query.first()


def ensure_catalog_duplicate_is_available(
    db: Session,
    municipality: str,
    notary_label: str,
    email: str | None,
    current_id: int | None = None,
) -> None:
    existing = find_duplicate_notary(db, municipality, notary_label, email, current_id=current_id)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una notaría con la combinación municipality + notary_label + email.",
        )


def resolve_owner(db: Session, owner_user_id: int | None, owner_text: str | None) -> tuple[int | None, str | None, str | None]:
    normalized_text = normalize_catalog_field(owner_text)
    if owner_user_id is None:
        return None, normalized_text, normalized_text
    user = db.query(User).filter(User.id == owner_user_id, User.is_active.is_(True)).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El responsable comercial no existe o está inactivo.")
    return user.id, user.full_name, user.full_name


def hydrate_notary_payload(db: Session, notary: Notary, payload: NotaryCreate | NotaryUpdate) -> None:
    municipality = normalize_catalog_field(payload.municipality) or payload.city
    notary_label = normalize_catalog_field(payload.notary_label) or payload.commercial_name
    email = normalize_email(str(payload.email) if payload.email else None)
    owner_user_id, owner_text, _ = resolve_owner(db, payload.commercial_owner_user_id, payload.commercial_owner)
    notary.catalog_identity_key = build_catalog_identity_key(municipality, notary_label, email)
    notary.department = normalize_catalog_field(payload.department) or "Antioquia"
    notary.municipality = municipality
    notary.notary_label = notary_label
    notary.legal_name = payload.legal_name
    notary.commercial_name = payload.commercial_name
    notary.city = payload.city
    notary.address = normalize_catalog_field(payload.address)
    notary.phone = normalize_catalog_field(payload.phone)
    notary.email = email
    notary.current_notary_name = normalize_catalog_field(payload.current_notary_name)
    notary.business_hours = normalize_catalog_field(payload.business_hours)
    notary.logo_url = normalize_catalog_field(payload.logo_url)
    notary.primary_color = payload.primary_color
    notary.secondary_color = payload.secondary_color
    notary.base_color = payload.base_color
    notary.accent_color = payload.secondary_color
    notary.institutional_data = payload.institutional_data
    notary.commercial_status = payload.commercial_status
    notary.commercial_owner_user_id = owner_user_id
    notary.commercial_owner = owner_text
    notary.main_contact_name = normalize_catalog_field(payload.main_contact_name)
    notary.main_contact_title = normalize_catalog_field(payload.main_contact_title)
    notary.commercial_phone = normalize_catalog_field(payload.commercial_phone)
    notary.commercial_email = normalize_email(str(payload.commercial_email) if payload.commercial_email else None)
    notary.last_management_at = payload.last_management_at
    notary.next_management_at = payload.next_management_at
    notary.commercial_notes = normalize_catalog_field(payload.commercial_notes)
    notary.priority = payload.priority
    notary.lead_source = normalize_catalog_field(payload.lead_source)
    notary.potential = payload.potential
    notary.internal_observations = normalize_catalog_field(payload.internal_observations)
    notary.is_active = payload.is_active


def create_audit_log(
    db: Session,
    notary_id: int,
    actor_user: User | None,
    event_type: str,
    field_name: str | None,
    old_value: str | None,
    new_value: str | None,
    comment: str | None = None,
) -> None:
    db.add(
        NotaryCrmAuditLog(
            notary_id=notary_id,
            actor_user_id=actor_user.id if actor_user else None,
            event_type=event_type,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            comment=comment,
        )
    )


def apply_import_mapping(notary: Notary, row: dict[str, str]) -> tuple[str, str, str | None]:
    municipality = normalize_catalog_field(row.get("MUNICIPIO"))
    notary_label = normalize_catalog_field(row.get("NOTARÍA"))
    if municipality is None or notary_label is None:
        raise ValueError("La fila no tiene MUNICIPIO o NOTARÍA válidos.")

    normalized_email = normalize_email(row.get("CORREO ELECTRÓNICO"))
    notary.catalog_identity_key = build_catalog_identity_key(municipality, notary_label, normalized_email)
    notary.department = "Antioquia"
    notary.municipality = municipality
    notary.notary_label = notary_label
    notary.city = municipality
    notary.legal_name = notary_label
    notary.commercial_name = notary_label
    notary.address = normalize_catalog_field(row.get("DIRECCIÓN"))
    notary.phone = normalize_catalog_field(row.get("TELÉFONO"))
    notary.email = normalized_email
    notary.current_notary_name = normalize_catalog_field(row.get("NOTARIO/A"))
    notary.business_hours = normalize_catalog_field(row.get("HORARIO"))
    notary.is_active = True
    if not notary.primary_color:
        notary.primary_color = "#0D2E5D"
    if not notary.secondary_color:
        notary.secondary_color = "#4D5B7C"
    if not notary.base_color:
        notary.base_color = "#F4F7FB"
    if not notary.accent_color:
        notary.accent_color = notary.secondary_color or "#4D5B7C"
    return municipality, notary_label, normalized_email


def process_import_rows(
    db: Session,
    rows: list[dict[str, str]],
    overwrite_existing: bool,
    source_path: str | None = None,
    start_row_number: int = 2,
) -> NotaryImportSummary:
    results: list[NotaryImportResult] = []
    row_errors: list[NotaryImportRowError] = []
    created = 0
    updated = 0
    omitted = 0

    for row_index, row_data in enumerate(rows, start=start_row_number):
        municipality = normalize_catalog_field(row_data.get("MUNICIPIO"))
        notary_label = normalize_catalog_field(row_data.get("NOTARÍA"))
        email = normalize_email(row_data.get("CORREO ELECTRÓNICO"))

        try:
            if municipality is None or notary_label is None:
                raise ValueError("La fila no tiene MUNICIPIO o NOTARÍA válidos.")

            duplicate = find_duplicate_notary(db, municipality, notary_label, email)

            if duplicate is None:
                slug_base = slugify(f"{municipality}-{notary_label}")
                duplicate = Notary(slug=ensure_unique_slug(db, slug_base), catalog_identity_key=build_catalog_identity_key(municipality, notary_label, email))
                apply_import_mapping(duplicate, row_data)
                db.add(duplicate)
                action = "created"
                created += 1
            elif overwrite_existing:
                apply_import_mapping(duplicate, row_data)
                action = "updated"
                updated += 1
            else:
                action = "omitted"
                omitted += 1

            if action != "omitted":
                try:
                    with db.begin_nested():
                        db.add(duplicate)
                        db.flush()
                except IntegrityError as exc:
                    raise ValueError("Conflicto de unicidad al importar la fila.") from exc

            results.append(
                NotaryImportResult(
                    row_number=row_index,
                    action=action,
                    notary_id=duplicate.id,
                    slug=duplicate.slug,
                    duplicate_key=duplicate_key_string(municipality, notary_label, email),
                )
            )
        except ValueError as exc:
            db.rollback()
            row_errors.append(
                NotaryImportRowError(
                    row_number=row_index,
                    municipality=municipality,
                    notary_label=notary_label,
                    error=str(exc),
                )
            )

    db.commit()
    return NotaryImportSummary(
        source_path=source_path,
        processed=len(rows),
        created=created,
        updated=updated,
        omitted=omitted,
        errors=row_errors,
        results=results,
    )


@router.get("", response_model=list[NotarySummary])
def list_notaries(
    commercial_status: str | None = Query(default=None),
    municipality: str | None = Query(default=None),
    commercial_owner: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    owner_alias = aliased(User)
    activity_counts = (
        db.query(
            NotaryCommercialActivity.notary_id.label("notary_id"),
            func.count(NotaryCommercialActivity.id).label("activity_count"),
        )
        .group_by(NotaryCommercialActivity.notary_id)
        .subquery()
    )
    query = (
        db.query(Notary, func.coalesce(activity_counts.c.activity_count, 0).label("activity_count"))
        .outerjoin(activity_counts, activity_counts.c.notary_id == Notary.id)
        .outerjoin(owner_alias, owner_alias.id == Notary.commercial_owner_user_id)
        .options(joinedload(Notary.commercial_owner_user))
        .order_by(Notary.municipality.asc(), Notary.notary_label.asc())
    )

    if commercial_status:
        query = query.filter(Notary.commercial_status == commercial_status)
    if municipality:
        query = query.filter(Notary.municipality == municipality)
    if commercial_owner:
        query = query.filter(or_(Notary.commercial_owner == commercial_owner, owner_alias.full_name == commercial_owner))
    if priority:
        query = query.filter(Notary.priority == priority)
    if q:
        search = f"%{q.strip()}%"
        query = query.filter(
            Notary.municipality.ilike(search)
            | Notary.notary_label.ilike(search)
            | Notary.email.ilike(search)
            | Notary.current_notary_name.ilike(search)
            | Notary.commercial_owner.ilike(search)
            | owner_alias.full_name.ilike(search)
        )

    return [attach_notary_summary(notary, activity_count) for notary, activity_count in query.all()]


@router.get("/filters", response_model=NotaryFilterOptions)
def get_notary_filter_options(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notaries = db.query(Notary).options(joinedload(Notary.commercial_owner_user)).all()
    municipalities = sorted({notary.municipality for notary in notaries if notary.municipality})
    commercial_owners = sorted({commercial_owner_display(notary) for notary in notaries if commercial_owner_display(notary)})
    priorities = sorted({notary.priority for notary in notaries if notary.priority})
    statuses = sorted({notary.commercial_status for notary in notaries if notary.commercial_status})
    return NotaryFilterOptions(
        municipalities=municipalities,
        commercial_owners=commercial_owners,
        priorities=priorities or PRIORITIES,
        commercial_statuses=statuses or COMMERCIAL_STATUSES,
    )


@router.get("/{notary_id}", response_model=NotaryDetail)
def get_notary(notary_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notary = (
        db.query(Notary)
        .options(
            joinedload(Notary.commercial_owner_user),
            joinedload(Notary.commercial_activities).joinedload(NotaryCommercialActivity.responsible_user),
            joinedload(Notary.crm_audit_logs).joinedload(NotaryCrmAuditLog.actor_user),
        )
        .filter(Notary.id == notary_id)
        .first()
    )
    if notary is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notaría no encontrada.")
    return attach_notary_detail(notary)


@router.post("", response_model=NotarySummary, status_code=status.HTTP_201_CREATED)
def create_notary(payload: NotaryCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    municipality = normalize_catalog_field(payload.municipality) or payload.city
    notary_label = normalize_catalog_field(payload.notary_label) or payload.commercial_name
    email = normalize_email(str(payload.email) if payload.email else None)
    ensure_catalog_duplicate_is_available(db, municipality, notary_label, email)

    notary = Notary(
        slug=ensure_unique_slug(db, slugify(f"{municipality}-{notary_label}")),
        catalog_identity_key=build_catalog_identity_key(municipality, notary_label, email),
    )
    hydrate_notary_payload(db, notary, payload)
    db.add(notary)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Conflicto de unicidad al crear la notaría.") from exc
    db.refresh(notary)
    return attach_notary_summary(notary, 0)


@router.put("/{notary_id}", response_model=NotarySummary)
def update_notary(notary_id: int, payload: NotaryUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    notary = (
        db.query(Notary)
        .options(joinedload(Notary.commercial_owner_user))
        .filter(Notary.id == notary_id)
        .first()
    )
    if notary is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notaría no encontrada.")

    municipality = normalize_catalog_field(payload.municipality) or payload.city
    notary_label = normalize_catalog_field(payload.notary_label) or payload.commercial_name
    email = normalize_email(str(payload.email) if payload.email else None)
    ensure_catalog_duplicate_is_available(db, municipality, notary_label, email, current_id=notary.id)

    previous_status = notary.commercial_status
    previous_owner = commercial_owner_display(notary)
    previous_owner_user_id = notary.commercial_owner_user_id

    notary.slug = ensure_unique_slug(db, slugify(f"{municipality}-{notary_label}"), current_id=notary.id)
    hydrate_notary_payload(db, notary, payload)
    try:
        db.flush()
        if previous_status != notary.commercial_status:
            create_audit_log(db, notary.id, current_user, "status_changed", "commercial_status", previous_status, notary.commercial_status)
        current_owner = commercial_owner_display(notary)
        if previous_owner != current_owner or previous_owner_user_id != notary.commercial_owner_user_id:
            create_audit_log(db, notary.id, current_user, "owner_changed", "commercial_owner", previous_owner, current_owner)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Conflicto de unicidad al actualizar la notaría.") from exc
    db.refresh(notary)
    activity_count = db.query(NotaryCommercialActivity).filter(NotaryCommercialActivity.notary_id == notary.id).count()
    return attach_notary_summary(notary, activity_count)


@router.patch("/{notary_id}/status", response_model=NotarySummary)
def update_notary_status(notary_id: int, payload: NotaryStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    notary = db.query(Notary).options(joinedload(Notary.commercial_owner_user)).filter(Notary.id == notary_id).first()
    if notary is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notaría no encontrada.")

    previous_value = "activa" if notary.is_active else "inactiva"
    notary.is_active = payload.is_active
    create_audit_log(db, notary.id, current_user, "status_changed", "is_active", previous_value, "activa" if payload.is_active else "inactiva")
    db.commit()
    db.refresh(notary)
    activity_count = db.query(NotaryCommercialActivity).filter(NotaryCommercialActivity.notary_id == notary.id).count()
    return attach_notary_summary(notary, activity_count)


@router.get("/{notary_id}/commercial-activities", response_model=list[CommercialActivitySummary])
def list_commercial_activities(notary_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if db.query(Notary.id).filter(Notary.id == notary_id).first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notaría no encontrada.")
    activities = (
        db.query(NotaryCommercialActivity)
        .options(joinedload(NotaryCommercialActivity.responsible_user))
        .filter(NotaryCommercialActivity.notary_id == notary_id)
        .order_by(NotaryCommercialActivity.occurred_at.desc(), NotaryCommercialActivity.id.desc())
        .all()
    )
    return [serialize_activity(activity) for activity in activities]


@router.post("/{notary_id}/commercial-activities", response_model=CommercialActivitySummary, status_code=status.HTTP_201_CREATED)
def create_commercial_activity(notary_id: int, payload: CommercialActivityCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary", "notary", "approver", "protocolist"))):
    notary = db.query(Notary).filter(Notary.id == notary_id).first()
    if notary is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notaría no encontrada.")

    responsible_text = normalize_catalog_field(payload.responsible)
    responsible_user = None
    if payload.responsible_user_id is not None:
        responsible_user = db.query(User).filter(User.id == payload.responsible_user_id, User.is_active.is_(True)).first()
        if responsible_user is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El responsable de la gestión no existe o está inactivo.")
        responsible_text = responsible_user.full_name

    if not responsible_text:
        responsible_text = current_user.full_name
        responsible_user = current_user

    activity = NotaryCommercialActivity(
        notary_id=notary_id,
        occurred_at=payload.occurred_at,
        management_type=payload.management_type,
        comment=payload.comment,
        responsible=responsible_text,
        responsible_user_id=responsible_user.id if responsible_user else None,
        result=payload.result,
        next_action=payload.next_action,
    )
    db.add(activity)
    notary.last_management_at = payload.occurred_at
    create_audit_log(
        db,
        notary_id,
        current_user,
        "activity_added",
        "commercial_activity",
        None,
        payload.management_type,
        comment=payload.comment,
    )
    db.commit()
    db.refresh(activity)
    activity = db.query(NotaryCommercialActivity).options(joinedload(NotaryCommercialActivity.responsible_user)).filter(NotaryCommercialActivity.id == activity.id).first()
    return serialize_activity(activity)


@router.post("/imports/master-catalog", response_model=NotaryImportSummary, status_code=status.HTTP_201_CREATED)
def import_master_catalog(payload: NotaryImportRequest, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    rows = [row.model_dump(by_alias=True) for row in payload.rows]
    return process_import_rows(db, rows, overwrite_existing=payload.overwrite_existing, source_path="payload://master-catalog", start_row_number=1)


@router.post("/imports/antioquia-source", response_model=NotaryImportSummary, status_code=status.HTTP_201_CREATED)
def import_antioquia_source(payload: NotaryFileImportRequest, db: Session = Depends(get_db), current_user: User = Depends(require_roles("super_admin", "admin_notary"))):
    source_path = payload.source_path or str(DEFAULT_ANTIOQUIA_SOURCE_PATH)
    try:
        workbook = load_xlsx_rows(source_path)
    except NotaryImportFileError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return process_import_rows(
        db,
        workbook.rows,
        overwrite_existing=payload.overwrite_existing,
        source_path=source_path,
        start_row_number=2,
    )


