"""Siembra plantillas semilla (cuerpos base) para el flujo de captura.

Cada plantilla vive como `NotarialTemplateLibraryItem` (template_kind="seed")
con una `NotarialTemplateVersion` aprobada cuyo `content_json` guarda el cuerpo
HTML parametrizado con `{{tokens}}`. El formulario rellena esos tokens; el
cumplimiento sigue saliendo del corpus.

Las definiciones se leen de `app/seeds/templates/plantillas-semilla/`:
para cada `<slug>.map.json` (metadatos + tokens) hay un `<slug>.html` (cuerpo).
Se siembra una copia por cada notaría existente. Idempotente por
(notary_id, library_key).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.legal_entity import LegalEntity
from app.models.notarial_document_intelligence import (
    NotarialTemplateLibraryItem,
    NotarialTemplateVersion,
)
from app.models.notary import Notary

SEED_DIR = Path(__file__).resolve().parent / "templates" / "plantillas-semilla"


def _load_definitions() -> list[dict[str, Any]]:
    definitions: list[dict[str, Any]] = []
    if not SEED_DIR.exists():
        return definitions
    for map_path in sorted(SEED_DIR.glob("*.map.json")):
        slug = map_path.name[: -len(".map.json")]
        html_path = SEED_DIR / f"{slug}.html"
        if not html_path.exists():
            print(f"[WARN] Plantilla '{slug}': falta {html_path.name}, se omite.")
            continue
        meta = json.loads(map_path.read_text(encoding="utf-8"))
        meta["slug"] = slug
        meta["body_html"] = html_path.read_text(encoding="utf-8")
        definitions.append(meta)
    return definitions


def _library_key(definition: dict[str, Any]) -> str:
    acto = definition.get("acto", "")
    fuente = definition.get("fuente", "")
    entidad = definition.get("bank_nit") or "generico"
    return f"seed|{acto}|{fuente}|{entidad}"


def _resolve_entity_id(db: Session, definition: dict[str, Any]) -> int | None:
    nit = (definition.get("bank_nit") or "").strip()
    if not nit:
        return None
    entity = db.query(LegalEntity).filter(LegalEntity.nit == nit).first()
    if entity is None:
        print(f"[WARN] Plantilla '{definition['slug']}': banco NIT {nit} no está sembrado (legal_entities).")
        return None
    return entity.id


def _upsert_for_notary(db: Session, notary_id: int, definition: dict[str, Any], legal_entity_id: int | None) -> str:
    key = _library_key(definition)
    meta_json = json.dumps(
        {
            "is_seed": True,
            "fuente": definition.get("fuente", ""),
            "notaria": definition.get("notaria"),
            "slug": definition["slug"],
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    content_json = json.dumps(
        {"body_html": definition["body_html"], "format": "html"},
        ensure_ascii=False,
    )
    placeholder_json = json.dumps({"tokens": definition.get("tokens", [])}, ensure_ascii=False)

    item = (
        db.query(NotarialTemplateLibraryItem)
        .filter(
            NotarialTemplateLibraryItem.notary_id == notary_id,
            NotarialTemplateLibraryItem.library_key == key,
        )
        .first()
    )
    action = "sin cambios"
    if item is None:
        item = NotarialTemplateLibraryItem(
            notary_id=notary_id,
            library_key=key,
            name=definition.get("name", definition["slug"]),
            template_kind="seed",
            status="approved",
            act_code=definition.get("acto"),
            document_type=definition.get("document_type"),
            bank_name=definition.get("bank_name"),
            legal_entity_id=legal_entity_id,
            metadata_json=meta_json,
        )
        db.add(item)
        db.flush()
        action = "creada"
    else:
        item.name = definition.get("name", item.name)
        item.act_code = definition.get("acto")
        item.bank_name = definition.get("bank_name")
        item.legal_entity_id = legal_entity_id
        item.status = "approved"
        item.metadata_json = meta_json
        action = "actualizada"

    version = (
        db.query(NotarialTemplateVersion)
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
            provenance_json=json.dumps({"source": "seed_plantillas_semilla"}, ensure_ascii=False),
            storage_path=None,
        )
        db.add(version)
        db.flush()
    else:
        version.content_json = content_json
        version.placeholder_map_json = placeholder_json
        version.status = "approved"

    item.latest_version_id = version.id
    item.approved_version_id = version.id
    db.flush()
    return action


def seed_plantillas_semilla(db: Session) -> dict[str, int]:
    definitions = _load_definitions()
    stats = {"definiciones": len(definitions), "creadas": 0, "actualizadas": 0, "notarias": 0}
    if not definitions:
        print(f"[WARN] No hay definiciones de plantilla en {SEED_DIR}.")
        return stats

    notaries = db.query(Notary).all()
    stats["notarias"] = len(notaries)
    if not notaries:
        print("[WARN] No hay notarías sembradas; no se puede asociar la plantilla.")
        return stats

    for definition in definitions:
        legal_entity_id = _resolve_entity_id(db, definition)
        for notary in notaries:
            action = _upsert_for_notary(db, notary.id, definition, legal_entity_id)
            if action == "creada":
                stats["creadas"] += 1
            elif action == "actualizada":
                stats["actualizadas"] += 1
    db.commit()
    return stats


def main() -> None:
    with SessionLocal() as db:
        stats = seed_plantillas_semilla(db)
    print(
        "[OK] Plantillas semilla: "
        f"{stats['definiciones']} definición(es) × {stats['notarias']} notaría(s) → "
        f"{stats['creadas']} creada(s), {stats['actualizadas']} actualizada(s)."
    )


if __name__ == "__main__":
    main()
