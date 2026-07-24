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

from app.models.legal_entity import LegalEntity
from app.models.notarial_document_intelligence import (
    NotarialTemplateLibraryItem,
    NotarialTemplateVersion,
)

SEED_KIND = "seed"


def _library_key(acto: str, fuente: str, bank_nit: str | None) -> str:
    entidad = (bank_nit or "").strip() or "generico"
    return f"seed|{acto}|{fuente}|{entidad}"


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


# ---------------------------------------------------------------------------
# Registro maestro (admin): CRUD de moldes editables desde la app, sin seed.
# ---------------------------------------------------------------------------


@dataclass
class PlantillaAdminItem:
    id: int
    acto: str
    fuente: str
    name: str
    bank_name: str | None
    legal_entity_id: int | None
    is_active: bool
    updated_at: str | None


def list_plantillas_admin(session: Session, notary_ids: Sequence[int]) -> list[PlantillaAdminItem]:
    """Lista todos los moldes semilla de las notarías indicadas (sin el cuerpo)."""
    query = session.query(NotarialTemplateLibraryItem).filter(
        NotarialTemplateLibraryItem.template_kind == SEED_KIND,
    )
    ids = [nid for nid in notary_ids if nid is not None]
    if ids:
        query = query.filter(NotarialTemplateLibraryItem.notary_id.in_(ids))
    items = query.order_by(NotarialTemplateLibraryItem.updated_at.desc()).all()
    out: list[PlantillaAdminItem] = []
    for item in items:
        meta = _loads(item.metadata_json, {})
        out.append(
            PlantillaAdminItem(
                id=item.id,
                acto=item.act_code or "",
                fuente=str(meta.get("fuente", "") if isinstance(meta, dict) else ""),
                name=item.name,
                bank_name=item.bank_name,
                legal_entity_id=item.legal_entity_id,
                is_active=item.status == "approved",
                updated_at=item.updated_at.isoformat() if item.updated_at else None,
            )
        )
    return out


def get_plantilla_admin(
    session: Session, item_id: int, notary_ids: Sequence[int]
) -> PlantillaSemillaResuelta | None:
    """Un molde con su cuerpo HTML, si pertenece a una notaría del usuario."""
    query = session.query(NotarialTemplateLibraryItem).filter(
        NotarialTemplateLibraryItem.id == item_id,
        NotarialTemplateLibraryItem.template_kind == SEED_KIND,
    )
    ids = [nid for nid in notary_ids if nid is not None]
    if ids:
        query = query.filter(NotarialTemplateLibraryItem.notary_id.in_(ids))
    item = query.first()
    if item is None:
        return None
    return _to_resuelta(session, item, is_fallback=False)


def upsert_plantilla_admin(
    session: Session,
    *,
    notary_id: int,
    acto: str,
    fuente: str,
    legal_entity_id: int | None,
    name: str,
    body_html: str,
    tokens: list[dict[str, Any]] | None = None,
    notaria: str | None = None,
) -> NotarialTemplateLibraryItem:
    """Crea o actualiza (en su sitio) un molde semilla. Clave: (acto, fuente, banco)."""
    bank_nit: str | None = None
    bank_name: str | None = None
    if legal_entity_id is not None:
        entity = session.get(LegalEntity, legal_entity_id)
        if entity is None:
            raise ValueError("El banco (legal_entity_id) no existe.")
        bank_nit = entity.nit
        bank_name = entity.name

    key = _library_key(acto, fuente, bank_nit)
    meta_json = json.dumps(
        {"is_seed": True, "fuente": fuente, "notaria": notaria, "editable": True},
        ensure_ascii=False,
        sort_keys=True,
    )
    content_json = json.dumps({"body_html": body_html, "format": "html"}, ensure_ascii=False)
    placeholder_json = json.dumps({"tokens": tokens or []}, ensure_ascii=False)

    item = (
        session.query(NotarialTemplateLibraryItem)
        .filter(
            NotarialTemplateLibraryItem.notary_id == notary_id,
            NotarialTemplateLibraryItem.library_key == key,
        )
        .first()
    )
    if item is None:
        item = NotarialTemplateLibraryItem(
            notary_id=notary_id,
            library_key=key,
            name=name,
            template_kind=SEED_KIND,
            status="approved",
            act_code=acto,
            bank_name=bank_name,
            legal_entity_id=legal_entity_id,
            metadata_json=meta_json,
        )
        session.add(item)
        session.flush()
    else:
        item.name = name
        item.act_code = acto
        item.bank_name = bank_name
        item.legal_entity_id = legal_entity_id
        item.status = "approved"
        item.metadata_json = meta_json

    version = (
        session.query(NotarialTemplateVersion)
        .filter(NotarialTemplateVersion.library_item_id == item.id)
        .order_by(NotarialTemplateVersion.version_number.desc())
        .first()
    )
    if version is None:
        version = NotarialTemplateVersion(
            library_item_id=item.id,
            notary_id=notary_id,
            version_number=1,
            status="approved",
            content_json=content_json,
            placeholder_map_json=placeholder_json,
            provenance_json=json.dumps({"source": "admin_registro_maestro"}, ensure_ascii=False),
            storage_path=None,
        )
        session.add(version)
        session.flush()
    else:
        version.content_json = content_json
        version.placeholder_map_json = placeholder_json
        version.status = "approved"

    item.latest_version_id = version.id
    item.approved_version_id = version.id
    session.flush()
    session.commit()
    return item
