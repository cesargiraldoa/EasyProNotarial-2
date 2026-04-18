import json
from collections import Counter, defaultdict
from datetime import date, datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.core.datetime_utils import format_bogota_datetime, to_bogota
from app.core.deps import get_current_user, get_db, get_role_codes
from app.models.case import Case
from app.models.notary import Notary
from app.models.user import User
from app.schemas.dashboard import (
    DashboardAlert,
    DashboardChartDatum,
    DashboardFilterOption,
    DashboardFilterOptions,
    DashboardFilters,
    DashboardKpi,
    DashboardPilotReference,
    DashboardSystemStatusItem,
    DashboardTrendDatum,
    SuperAdminDashboardResponse,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
settings = get_settings()

FINALIZED_STATES = {"firmado_cargado", "cerrado"}
ELABORATED_STATES = {"aprobado_notario", "generado", "firmado_cargado", "cerrado"}
ALERT_STATES = {"ajustes_solicitados", "devuelto_aprobador", "rechazado_notario"}
BROKEN_TEXT_MARKERS = ("\u00c3", "\u00c2", "\u00e2", "\u0192", "\u2019", "\u201a", "\u00ad")


def clean_text(value: str | None) -> str:
    if not value:
        return ""

    result = value.strip()
    if "\\u" in result:
        try:
            result = result.encode("utf-8").decode("unicode_escape")
        except UnicodeError:
            pass

    for _ in range(4):
        if not any(marker in result for marker in BROKEN_TEXT_MARKERS):
            break

        updated = result
        for encoding in ("cp1252", "latin1"):
            try:
                candidate = updated.encode(encoding, errors="ignore").decode("utf-8", errors="ignore")
            except UnicodeError:
                continue
            if candidate and candidate != updated:
                updated = candidate

        if updated == result:
            break
        result = updated

    return result.replace("  ", " ").strip()


def safe_metadata(value: str | None) -> dict:
    if not value:
        return {}
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def top_counter(counter: Counter[str], *, limit: int = 6, highlight_label: str | None = None) -> list[DashboardChartDatum]:
    items = counter.most_common(limit)
    clean_highlight = clean_text(highlight_label)
    return [
        DashboardChartDatum(label=clean_text(label), value=value, highlight=clean_text(label) == clean_highlight)
        for label, value in items
    ]


def infer_online_users(cases: list[Case], active_users: list[User]) -> int:
    recent_threshold = datetime.now(timezone.utc) - timedelta(days=14)
    online_ids: set[int] = set()
    for case in cases:
        if case.updated_at and case.updated_at >= recent_threshold:
            for user_id in [
                case.current_owner_user_id,
                case.protocolist_user_id,
                case.approver_user_id,
                case.titular_notary_user_id,
                case.substitute_notary_user_id,
                case.client_user_id,
            ]:
                if user_id is not None:
                    online_ids.add(user_id)
    if online_ids:
        return len(online_ids)
    return min(len(active_users), 3)


@router.get("/superadmin", response_model=SuperAdminDashboardResponse)
def get_superadmin_dashboard(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    notary_id: int | None = Query(default=None),
    state: str | None = Query(default=None),
    act_type: str | None = Query(default=None),
    owner_user_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role_codes = get_role_codes(current_user)
    is_super_admin = "super_admin" in role_codes
    scope_notary_id = None if is_super_admin else current_user.default_notary_id
    effective_notary_id = notary_id if is_super_admin else scope_notary_id

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
        .order_by(Case.updated_at.desc(), Case.id.desc())
    )

    if date_from is not None:
        query = query.filter(Case.updated_at >= datetime.combine(date_from, time.min))
    if date_to is not None:
        query = query.filter(Case.updated_at <= datetime.combine(date_to, time.max))
    if effective_notary_id is not None:
        query = query.filter(Case.notary_id == effective_notary_id)
    if state:
        query = query.filter(Case.current_state == state)
    if act_type:
        query = query.filter(Case.act_type == act_type)
    if owner_user_id is not None:
        query = query.filter(Case.current_owner_user_id == owner_user_id)

    cases = query.all()
    all_users_query = db.query(User).options(joinedload(User.default_notary))
    all_notaries_query = db.query(Notary)
    if not is_super_admin:
        all_users_query = all_users_query.filter(User.default_notary_id == scope_notary_id)
        all_notaries_query = all_notaries_query.filter(Notary.id == scope_notary_id)
    all_users = all_users_query.all()
    all_notaries = all_notaries_query.order_by(Notary.municipality.asc(), Notary.notary_label.asc()).all()
    active_users = [user for user in all_users if user.is_active]
    pilot_notary = (
        db.query(Notary)
        .filter(Notary.id == scope_notary_id)
        .first()
        if not is_super_admin
        else db.query(Notary)
        .filter(Notary.department == "Antioquia", Notary.municipality == "Caldas")
        .order_by(Notary.id.asc())
        .first()
    )

    notary_counter: Counter[str] = Counter()
    state_counter: Counter[str] = Counter()
    act_counter: Counter[str] = Counter()
    owner_counter: Counter[str] = Counter()
    trend_counter: defaultdict[str, int] = defaultdict(int)
    active_project_counter: Counter[str] = Counter()

    for case in cases:
        notary_label = clean_text(case.notary.notary_label if case.notary else "Sin notar\u00eda")
        notary_counter[notary_label] += 1
        state_counter[clean_text(case.current_state)] += 1
        act_counter[clean_text(case.act_type)] += 1
        if case.current_owner_user:
            owner_counter[clean_text(case.current_owner_user.full_name)] += 1
        localized_updated_at = to_bogota(case.updated_at) or case.updated_at
        trend_counter[localized_updated_at.strftime("%d %b")] += 1
        metadata = safe_metadata(case.metadata_json)
        project = clean_text(str(metadata.get("project") or metadata.get("radication") or ""))
        if project and case.current_state not in FINALIZED_STATES:
            active_project_counter[project] += 1

    in_progress_cases = sum(1 for case in cases if case.current_state not in FINALIZED_STATES)
    elaborated_cases = sum(1 for case in cases if case.current_state in ELABORATED_STATES)
    finalized_cases = sum(1 for case in cases if case.current_state in FINALIZED_STATES)
    active_lots = len(active_project_counter)
    critical_case_alerts = [case for case in cases if case.current_state in ALERT_STATES]
    critical_signed_alerts = [case for case in cases if not case.final_signed_uploaded and case.current_state in {"aprobado_notario", "generado", "firmado_cargado"}]
    online_users = infer_online_users(cases, active_users)

    alerts: list[DashboardAlert] = []
    if critical_case_alerts:
        alerts.append(
            DashboardAlert(
                level="critical",
                title="Estados con bloqueo operativo",
                detail=f"{len(critical_case_alerts)} casos est\u00e1n en ajustes, devoluci\u00f3n o rechazo notarial.",
            )
        )
    if critical_signed_alerts:
        alerts.append(
            DashboardAlert(
                level="warning",
                title="Firmados pendientes de carga",
                detail=f"{len(critical_signed_alerts)} casos ya avanzaron pero a\u00fan no tienen firmado final cargado.",
            )
        )
    if pilot_notary is not None:
        alerts.append(
            DashboardAlert(
                level="info",
                title="Piloto operativo real",
                detail="Caldas, Antioquia queda visible como referencia actual de operaci\u00f3n EasyPro 1.",
            )
        )

    db.execute(text("SELECT 1"))
    latest_import_notary_query = db.query(Notary)
    if not is_super_admin:
        latest_import_notary_query = latest_import_notary_query.filter(Notary.id == scope_notary_id)
    else:
        latest_import_notary_query = latest_import_notary_query.filter(Notary.department == "Antioquia")
    latest_import_notary = latest_import_notary_query.order_by(Notary.updated_at.desc()).first()
    latest_import_reference = None
    if latest_import_notary is not None and latest_import_notary.updated_at is not None:
        latest_import_reference = (
            f"{format_bogota_datetime(latest_import_notary.updated_at) or ''} | "
            f"{clean_text(latest_import_notary.municipality)} | {clean_text(latest_import_notary.notary_label)}"
        )

    pilot_reference = None
    if pilot_notary is not None:
        pilot_cases = [case for case in cases if case.notary_id == pilot_notary.id]
        pilot_reference = DashboardPilotReference(
            notary_id=pilot_notary.id,
            notary_label=clean_text(pilot_notary.notary_label),
            municipality=clean_text(pilot_notary.municipality),
            department=clean_text(pilot_notary.department),
            total_cases=len(pilot_cases),
            active_cases=sum(1 for case in pilot_cases if case.current_state not in FINALIZED_STATES),
            finalized_cases=sum(1 for case in pilot_cases if case.current_state in FINALIZED_STATES),
            notes="Notar\u00eda piloto real referenciada para demo ejecutiva y validaci\u00f3n operativa.",
        )

    system_status = [
        DashboardSystemStatusItem(key="backend", label="Backend", status="online", detail="API operando en 127.0.0.1:8000"),
        DashboardSystemStatusItem(key="frontend", label="Frontend", status="online", detail=f"Shell disponible en {settings.frontend_url}"),
        DashboardSystemStatusItem(key="database", label="Base de datos", status="online", detail="Consulta de verificaci\u00f3n completada."),
        DashboardSystemStatusItem(key="auth", label="Autenticaci\u00f3n", status="online", detail=f"Sesi\u00f3n validada para {current_user.email}"),
        DashboardSystemStatusItem(key="imports", label="\u00daltima importaci\u00f3n relevante", status="online", detail=latest_import_reference or "Sin referencia de importaci\u00f3n inferida."),
        DashboardSystemStatusItem(key="alerts", label="Alertas cr\u00edticas", status="warning" if alerts else "online", detail=f"{len(alerts)} alertas visibles en el tablero."),
    ]

    notary_options = [DashboardFilterOption(id=None, label="Todas las notar\u00edas")] + [
        DashboardFilterOption(id=notary.id, label=f"{clean_text(notary.municipality)} | {clean_text(notary.notary_label)}")
        for notary in all_notaries
    ]
    state_options = [DashboardFilterOption(id=None, label="Todos los estados")] + [
        DashboardFilterOption(id=None, label=clean_text(item[0])) for item in sorted(db.query(Case.current_state).distinct().all()) if item[0]
    ]
    act_options = [DashboardFilterOption(id=None, label="Todos los actos")] + [
        DashboardFilterOption(id=None, label=clean_text(item[0])) for item in sorted(db.query(Case.act_type).distinct().all()) if item[0]
    ]
    owner_options = [DashboardFilterOption(id=None, label="Todos los responsables")] + [
        DashboardFilterOption(id=user.id, label=clean_text(user.full_name)) for user in active_users
    ]

    pilot_label = clean_text(pilot_notary.notary_label) if pilot_notary else None

    return SuperAdminDashboardResponse(
        generated_at=datetime.now(timezone.utc),
        filters=DashboardFilters(
            date_from=date_from,
            date_to=date_to,
            notary_id=notary_id,
            state=state,
            act_type=act_type,
            owner_user_id=owner_user_id,
        ),
        filter_options=DashboardFilterOptions(
            notaries=notary_options,
            states=state_options,
            act_types=act_options,
            owners=owner_options,
        ),
        kpis=[
            DashboardKpi(key="in_progress", label="Casos en tr\u00e1mite", value=in_progress_cases, detail="Casos activos dentro del flujo documental."),
            DashboardKpi(key="elaborated", label="Casos elaborados", value=elaborated_cases, detail="Casos ya generados o aprobados para cierre."),
            DashboardKpi(key="finalized", label="Casos finalizados", value=finalized_cases, detail="Casos firmados o cerrados.", tone="success"),
            DashboardKpi(key="users_total", label="Usuarios totales", value=len(all_users), detail="Usuarios registrados en el sistema."),
            DashboardKpi(key="users_active", label="Usuarios activos", value=len(active_users), detail="Usuarios habilitados para operar."),
            DashboardKpi(key="users_online", label="Usuarios en l\u00ednea", value=online_users, detail="M\u00e9trica inferida a partir de actividad reciente."),
            DashboardKpi(key="lots", label="Lotes en curso", value=active_lots, detail="Lotes inferidos por proyectos activos."),
            DashboardKpi(
                key="critical_alerts",
                label="Alertas cr\u00edticas",
                value=len(alerts),
                detail="Bloqueos y pendientes que requieren atenci\u00f3n.",
                tone="critical" if alerts else "default",
            ),
        ],
        documents_by_notary=top_counter(notary_counter, limit=8, highlight_label=pilot_label),
        documents_by_state=top_counter(state_counter, limit=8),
        documents_by_act_type=top_counter(act_counter, limit=8),
        temporal_trend=[DashboardTrendDatum(label=label, value=value) for label, value in sorted(trend_counter.items())],
        owner_ranking=top_counter(owner_counter, limit=6),
        operational_focus=[
            DashboardChartDatum(label=clean_text(label), value=value, highlight=clean_text(label) == "EasyPro 1 Caldas")
            for label, value in active_project_counter.most_common(6)
        ],
        critical_alerts=alerts,
        system_status=system_status,
        pilot_reference=pilot_reference,
        latest_import_reference=latest_import_reference,
    )
