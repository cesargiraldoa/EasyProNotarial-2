from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_db, require_roles
from app.models.case import Case
from app.models.case_participant import CaseParticipant
from app.models.user import User
from app.schemas.billing import EmitMode, GariBillingInvoiceResult
from app.services.gari_billing_client import GariBillingClient, GariBillingError
from app.services.gari_billing_payload import build_gari_billing_invoice_payload

router = APIRouter(prefix="/billing/gari", tags=["billing"])


def load_case_for_billing(db: Session, case_id: int) -> Case:
    case = (
        db.query(Case)
        .options(
            joinedload(Case.notary),
            joinedload(Case.act_data),
            joinedload(Case.participants).joinedload(CaseParticipant.person),
            joinedload(Case.participants).joinedload(CaseParticipant.legal_entity),
            joinedload(Case.created_by_user),
        )
        .filter(Case.id == case_id)
        .first()
    )
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caso no encontrado.")
    return case


def _build_response(result: dict, payload: dict) -> GariBillingInvoiceResult:
    return GariBillingInvoiceResult(
        source_system=result.get("source_system") or payload.get("source_system"),
        external_reference=result.get("external_reference") or payload.get("external_reference"),
        idempotency_key=result.get("idempotency_key") or payload.get("idempotency_key"),
        emit_mode=result.get("emit_mode") or payload.get("emit_mode"),
        invoice_id=result.get("invoice_id"),
        status=result.get("status"),
        full_number=result.get("full_number"),
        total=result.get("total"),
        error_message=result.get("error_message"),
        gari_response=result.get("gari_response", result),
    )


@router.post("/invoices/from-case/{case_id}", response_model=GariBillingInvoiceResult)
def create_invoice_from_case(
    case_id: int,
    emit_mode: EmitMode = Query(default="draft"),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_roles("super_admin", "admin_notary")),
):
    case = load_case_for_billing(db, case_id)
    try:
        payload = build_gari_billing_invoice_payload(case, emit_mode=emit_mode)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    client = GariBillingClient()
    try:
        result = client.create_invoice(payload)
    except GariBillingError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return _build_response(result, payload)
