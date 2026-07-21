from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.legal_clausula import LegalClausula
from app.models.legal_norma import LegalNorma, LegalNormaRelacion
from app.models.legal_regla import LegalRegla
from app.services.legal_rag import LegalEmbeddingProvider, reindex_legal_sources


@dataclass(frozen=True)
class CambioNormativo:
    norma_anterior_id: int
    norma_nueva_id: int | None
    relacion_id: int
    reglas_nuevas_ids: list[int]


def _previous_day(value: date) -> date:
    return value - timedelta(days=1)


def impacto_de_norma(session: Session, norma_id: int) -> dict[str, list[dict[str, Any]]]:
    clausulas = [
        {"id": item.id, "acto_code": item.acto_code, "orden": item.orden, "titulo": item.titulo}
        for item in session.execute(
            select(LegalClausula).where(LegalClausula.norma_id == norma_id).order_by(LegalClausula.acto_code, LegalClausula.orden)
        ).scalars()
    ]
    reglas = [
        {"id": item.id, "acto_code": item.acto_code, "codigo": item.codigo, "severidad": item.severidad, "mensaje": item.mensaje}
        for item in session.execute(
            select(LegalRegla).where(LegalRegla.norma_id == norma_id).order_by(LegalRegla.acto_code, LegalRegla.codigo)
        ).scalars()
    ]
    return {"clausulas": clausulas, "reglas": reglas}


def registrar_cambio(
    session: Session,
    norma_id: int,
    *,
    tipo: str,
    fecha_efecto: date,
    nueva_norma: dict[str, Any] | None = None,
    articulo_afectado: str | None = None,
    notas: str | None = None,
    reglas_nuevas: list[dict[str, Any]] | None = None,
    embedding_provider: LegalEmbeddingProvider | None = None,
    reindexar: bool = True,
) -> CambioNormativo:
    """Registra un cambio normativo preservando historia.

    Flujo operativo: detectar el cambio externo, registrar la version nueva,
    cerrar la vigencia de la version anterior, medir impacto en clausulas/reglas
    referenciadas y reindexar solo las fuentes afectadas. La version anterior no
    se borra ni se marca globalmente como no vigente para no romper consultas
    historicas anteriores a fecha_efecto.
    """

    anterior = session.get(LegalNorma, norma_id)
    if anterior is None:
        raise ValueError(f"Norma no encontrada: {norma_id}")

    anterior.vigencia_hasta = _previous_day(fecha_efecto)
    nueva: LegalNorma | None = None
    if nueva_norma is not None:
        values = {
            "tipo": anterior.tipo,
            "numero": anterior.numero,
            "anio": anterior.anio,
            "articulo": anterior.articulo,
            "materia": anterior.materia,
            "autoridad": anterior.autoridad,
            "estado": anterior.estado,
            "vigencia_formal": anterior.vigencia_formal,
            "aplicabilidad_operativa": anterior.aplicabilidad_operativa,
            "vigencia_desde": fecha_efecto,
            "vigencia_hasta": None,
            "url_oficial": anterior.url_oficial,
            "confianza": anterior.confianza,
            "fecha_verificacion": anterior.fecha_verificacion,
            "texto": anterior.texto,
            "notas": anterior.notas,
            "slug": f"{anterior.slug}-v{fecha_efecto:%Y%m%d}",
        }
        values.update(nueva_norma)
        values["vigencia_desde"] = values.get("vigencia_desde") or fecha_efecto
        nueva = LegalNorma(**values)
        session.add(nueva)
        session.flush()

    relacion = LegalNormaRelacion(
        norma_origen_id=nueva.id if nueva is not None else anterior.id,
        norma_destino_id=anterior.id,
        tipo=tipo,
        articulo_afectado=articulo_afectado,
        fecha_efecto=fecha_efecto,
        notas=notas,
    )
    session.add(relacion)
    session.flush()

    reglas_ids: list[int] = []
    for spec in reglas_nuevas or []:
        codigo_origen = spec.get("codigo_origen")
        regla_anterior: LegalRegla | None = None
        if codigo_origen:
            regla_anterior = session.execute(select(LegalRegla).where(LegalRegla.codigo == codigo_origen)).scalar_one_or_none()
            if regla_anterior is not None:
                regla_anterior.vigencia_hasta = _previous_day(fecha_efecto)
        payload = {key: value for key, value in spec.items() if key != "codigo_origen"}
        payload.setdefault("acto_code", regla_anterior.acto_code if regla_anterior is not None else "transversal")
        payload.setdefault("norma_id", nueva.id if nueva is not None else anterior.id)
        payload.setdefault("vigencia_desde", fecha_efecto)
        payload.setdefault("vigencia_hasta", None)
        regla = LegalRegla(**payload)
        session.add(regla)
        session.flush()
        reglas_ids.append(regla.id)

    if reindexar:
        norma_ids = {anterior.id}
        if nueva is not None:
            norma_ids.add(nueva.id)
        clausula_ids = {
            item.id
            for item in session.execute(select(LegalClausula.id).where(LegalClausula.norma_id.in_(norma_ids))).all()
        }
        reindex_legal_sources(session, {"norma": norma_ids, "clausula": clausula_ids}, provider=embedding_provider)

    session.flush()
    return CambioNormativo(
        norma_anterior_id=anterior.id,
        norma_nueva_id=nueva.id if nueva is not None else None,
        relacion_id=relacion.id,
        reglas_nuevas_ids=reglas_ids,
    )
