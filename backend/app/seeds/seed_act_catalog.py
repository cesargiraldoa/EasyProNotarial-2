from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.act_catalog import ActCatalog

SEED_ACTS = [
    {"code": "liberacion_hipoteca", "label": "Liberación parcial de hipoteca", "roles": ["banco_libera", "fideicomiso"]},
    {"code": "protocolizacion_cto", "label": "Protocolización CTO", "roles": ["fideicomiso", "constructora"]},
    {"code": "compraventa_vis", "label": "Compraventa VIS", "roles": ["fideicomiso", "compradores"]},
    {"code": "renuncia_resolutoria", "label": "Renuncia condición resolutoria", "roles": ["fideicomiso", "compradores"]},
    {"code": "cancelacion_comodato", "label": "Cancelación comodato precario", "roles": ["fideicomiso", "constructora"]},
    {"code": "constitucion_hipoteca", "label": "Constitución hipoteca 1er grado", "roles": ["compradores", "banco_hipoteca"]},
    {"code": "patrimonio_familia", "label": "Constitución patrimonio de familia", "roles": ["compradores"]},
    {"code": "poder_especial", "label": "Poder especial", "roles": ["compradores", "constructora"]},
    {"code": "correccion_rc", "label": "Corrección de Registro Civil", "roles": ["inscrito"]},
    {"code": "salida_pais", "label": "Permiso de salida del país", "roles": ["padre_otorgante", "madre_aceptante", "menor"]},
    {"code": "poder_general", "label": "Poder general", "roles": ["poderdante", "apoderado"]},
]


def seed_act_catalog(db: Session) -> tuple[int, int]:
    created = 0
    updated = 0
    for payload in SEED_ACTS:
        code = payload["code"].strip()
        label = payload["label"].strip()
        roles_json = json.dumps(payload["roles"], ensure_ascii=False)
        existing = db.query(ActCatalog).filter(ActCatalog.code == code).first()
        if existing is None:
            db.add(
                ActCatalog(
                    code=code,
                    label=label,
                    roles_json=roles_json,
                    is_active=True,
                )
            )
            created += 1
            continue
        existing.label = label
        existing.roles_json = roles_json
        existing.is_active = True
        updated += 1
    db.commit()
    return created, updated


def main() -> None:
    with SessionLocal() as db:
        created, updated = seed_act_catalog(db)
        print(f"[OK] Actos insertados: {created}; actualizados: {updated}.")


if __name__ == "__main__":
    main()
