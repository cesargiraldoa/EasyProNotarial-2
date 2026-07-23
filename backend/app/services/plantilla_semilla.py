"""Resolución de plantillas semilla (cuerpos base) por (acto, fuente, entidad).

Una plantilla semilla es un `NotarialTemplateLibraryItem` con
`template_kind == "seed"` y una versión aprobada cuyo `content_json`
contiene el cuerpo HTML parametrizado con `{{tokens}}`. El formulario
rellena esos tokens en vivo; el cumplimiento sigue saliendo del corpus.

Regla de resolución (decisión A del flujo):
  1. Plantilla específica del banco/entidad para ese acto+fuente.
  2. Si no existe, plantilla genérica del acto (fuente "particular",
     sin entidad) como respaldo → `is_fallback = True`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Sequence

from sqlalchemy.orm import Session

from app.models.notarial_document_intelligence import (
    NotarialTemplateLibraryItem,
    NotarialTemplateVersion,
)

SEED_KIND = "seed"


@dataclass
class PlantillaSemillaResuelta:
    id: int
    acto: str
    fuente: str
    name: str
    body_html: str
    tokens: list[dict[str, Any]]
    bank_name: str | None
    legal_entity_id: int | None
    notaria: str | None
    is_fallback: bool


def _loads(raw: str | None, default: Any) -> Any:
    if not raw or not raw.strip():
        return default
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return default


def _version_body(session: Session, item: NotarialTemplateLibraryItem) -> NotarialTemplateVersion | None:
    query = session.query(NotarialTemplateVersion).filter(
        NotarialTemplateVersion.library_item_id == item.id
    )
    if item.approved_version_id is not None:
        version = query.filter(NotarialTemplateVersion.id == item.approved_version_id).first()
        if version is not None:
            return version
    if item.latest_version_id is not None:
        version = query.filter(NotarialTemplateVersion.id == item.latest_version_id).first()
        if version is not None:
            return version
    return query.order_by(NotarialTemplateVersion.version_number.desc()).first()


def _to_resuelta(
    session: Session, item: NotarialTemplateLibraryItem, *, is_fallback: bool
) -> PlantillaSemillaResuelta | None:
    version = _version_body(session, item)
    if version is None:
        return None
    content = _loads(version.content_json, {})
    body_html = content.get("body_html") if isinstance(content, dict) else None
    if not body_html:
        return None
    placeholder = _loads(version.placeholder_map_json, {})
    tokens = placeholder.get("tokens", []) if isinstance(placeholder, dict) else []
    meta = _loads(item.metadata_json, {})
    return PlantillaSemillaResuelta(
        id=item.id,
        acto=item.act_code or "",
        fuente=str(meta.get("fuente", "")),
        name=item.name,
        body_html=body_html,
        tokens=tokens if isinstance(tokens, list) else [],
        bank_name=item.bank_name,
        legal_entity_id=item.legal_entity_id,
        notaria=meta.get("notaria"),
        is_fallback=is_fallback,
    )


def _base_query(session: Session, notary_ids: Sequence[int], act_code: str):
    query = session.query(NotarialTemplateLibraryItem).filter(
        NotarialTemplateLibraryItem.template_kind == SEED_KIND,
        NotarialTemplateLibraryItem.act_code == act_code,
    )
    ids = [nid for nid in notary_ids if nid is not None]
    if ids:
        query = query.filter(NotarialTemplateLibraryItem.notary_id.in_(ids))
    return query.order_by(NotarialTemplateLibraryItem.updated_at.desc())


def resolver_plantilla_semilla(
    session: Session,
    *,
    notary_ids: Sequence[int],
    act_code: str,
    fuente: str,
    legal_entity_id: int | None,
) -> PlantillaSemillaResuelta | None:
    """Devuelve la plantilla específica; si no hay, cae a la genérica del acto."""

    # 1) Específica de la entidad (banco/proyecto) para ese acto.
    if legal_entity_id is not None:
        item = _base_query(session, notary_ids, act_code).filter(
            NotarialTemplateLibraryItem.legal_entity_id == legal_entity_id
        ).first()
        if item is not None:
            resuelta = _to_resuelta(session, item, is_fallback=False)
            if resuelta is not None:
                return resuelta

    # 2) Genérica del acto (sin entidad). Sirve para particular/proyecto
    #    y como respaldo cuando el banco no tiene plantilla propia.
    generic = _base_query(session, notary_ids, act_code).filter(
        NotarialTemplateLibraryItem.legal_entity_id.is_(None)
    ).first()
    if generic is not None:
        return _to_resuelta(session, generic, is_fallback=legal_entity_id is not None)

    return None
