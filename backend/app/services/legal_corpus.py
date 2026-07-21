from __future__ import annotations

from datetime import date

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models.legal_clausula import LegalClausula
from app.models.legal_norma import LegalNorma
from app.models.legal_regla import LegalRegla
from app.models.legal_tarifa import LegalTarifa

_NON_OPERATIVE_STATES = {"derogada_total", "inexequible", "suspendida", "compilada"}

_ACTO_MATERIA_KEYWORDS = {
    "compraventa": (
        "compraventa",
        "registro",
        "notarial",
        "vivienda",
        "tributario",
        "propiedad horizontal",
        "LA/FT",
    ),
    "hipoteca": (
        "hipoteca",
        "registro",
        "notarial",
        "vivienda",
        "tributario",
        "LA/FT",
    ),
    "cancelacion_hipoteca": (
        "cancelacion_hipoteca",
        "hipoteca",
        "registro",
        "notarial",
        "tributario",
        "LA/FT",
    ),
    "transversal": ("transversal", "notarial"),
}


def _vigencia_predicate(model, fecha: date):
    return and_(
        or_(model.vigencia_desde.is_(None), model.vigencia_desde <= fecha),
        or_(model.vigencia_hasta.is_(None), model.vigencia_hasta >= fecha),
    )


def _norma_vigente_predicate(fecha: date):
    return and_(
        _vigencia_predicate(LegalNorma, fecha),
        LegalNorma.aplicabilidad_operativa == "vigente",
        LegalNorma.estado.not_in(_NON_OPERATIVE_STATES),
    )


def _linked_norma_vigente_or_null(model, fecha: date):
    return or_(model.norma_id.is_(None), _norma_vigente_predicate(fecha))


def _norma_ids_referenciadas(session: Session, acto_code: str, fecha: date) -> set[int]:
    acto_codes = [acto_code]
    if acto_code != "transversal":
        acto_codes.append("transversal")

    clausulas = session.execute(
        select(LegalClausula.norma_id)
        .outerjoin(LegalNorma, LegalClausula.norma_id == LegalNorma.id)
        .where(LegalClausula.acto_code.in_(acto_codes))
        .where(_vigencia_predicate(LegalClausula, fecha))
        .where(_linked_norma_vigente_or_null(LegalClausula, fecha))
        .where(LegalClausula.norma_id.is_not(None))
    ).scalars()

    reglas = session.execute(
        select(LegalRegla.norma_id)
        .outerjoin(LegalNorma, LegalRegla.norma_id == LegalNorma.id)
        .where(LegalRegla.acto_code.in_(acto_codes))
        .where(_vigencia_predicate(LegalRegla, fecha))
        .where(_linked_norma_vigente_or_null(LegalRegla, fecha))
        .where(LegalRegla.norma_id.is_not(None))
    ).scalars()

    tarifas = session.execute(
        select(LegalTarifa.norma_id)
        .outerjoin(LegalNorma, LegalTarifa.norma_id == LegalNorma.id)
        .where(LegalTarifa.anio == fecha.year)
        .where(_vigencia_predicate(LegalTarifa, fecha))
        .where(_linked_norma_vigente_or_null(LegalTarifa, fecha))
        .where(LegalTarifa.norma_id.is_not(None))
    ).scalars()

    return {norma_id for norma_id in [*clausulas, *reglas, *tarifas] if norma_id is not None}


def normas_vigentes(session: Session, acto_code: str, fecha: date) -> list[LegalNorma]:
    keywords = _ACTO_MATERIA_KEYWORDS.get(acto_code, (acto_code,))
    materia_predicate = or_(*(LegalNorma.materia.ilike(f"%{keyword}%") for keyword in keywords))
    norma_ids = _norma_ids_referenciadas(session, acto_code, fecha)

    filtros_acto = [materia_predicate]
    if norma_ids:
        filtros_acto.append(LegalNorma.id.in_(norma_ids))

    stmt = (
        select(LegalNorma)
        .where(_norma_vigente_predicate(fecha))
        .where(or_(*filtros_acto))
        .order_by(LegalNorma.tipo, LegalNorma.anio, LegalNorma.numero, LegalNorma.articulo)
    )
    return list(session.execute(stmt).scalars())


def clausulas_vigentes(session: Session, acto_code: str, fecha: date) -> list[LegalClausula]:
    stmt = (
        select(LegalClausula)
        .outerjoin(LegalNorma, LegalClausula.norma_id == LegalNorma.id)
        .where(LegalClausula.acto_code == acto_code)
        .where(_vigencia_predicate(LegalClausula, fecha))
        .where(_linked_norma_vigente_or_null(LegalClausula, fecha))
        .order_by(LegalClausula.orden)
    )
    return list(session.execute(stmt).scalars())


def reglas_vigentes(session: Session, acto_code: str, fecha: date) -> list[LegalRegla]:
    acto_codes = [acto_code]
    if acto_code != "transversal":
        acto_codes.append("transversal")
    stmt = (
        select(LegalRegla)
        .outerjoin(LegalNorma, LegalRegla.norma_id == LegalNorma.id)
        .where(LegalRegla.acto_code.in_(acto_codes))
        .where(_vigencia_predicate(LegalRegla, fecha))
        .where(_linked_norma_vigente_or_null(LegalRegla, fecha))
        .order_by(LegalRegla.acto_code, LegalRegla.codigo)
    )
    return list(session.execute(stmt).scalars())


def tarifas_vigentes(session: Session, acto_code: str, fecha: date) -> list[LegalTarifa]:
    _ = acto_code
    stmt = (
        select(LegalTarifa)
        .outerjoin(LegalNorma, LegalTarifa.norma_id == LegalNorma.id)
        .where(LegalTarifa.anio == fecha.year)
        .where(_vigencia_predicate(LegalTarifa, fecha))
        .where(_linked_norma_vigente_or_null(LegalTarifa, fecha))
        .order_by(LegalTarifa.concepto)
    )
    return list(session.execute(stmt).scalars())
