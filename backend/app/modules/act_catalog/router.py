from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.act_catalog import ActCatalog
from app.schemas.act_catalog import ActCatalogOut


act_catalog_router = APIRouter(prefix="/act-catalog", tags=["act-catalog"])


def load_case_or_404(db: Session, case_id: int) -> Case:
    case = db.query(Case).filter(Case.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Minuta no encontrada.")
    return case


LEGACY_CASE_ACTS_BY_VARIANT: dict[str, list[dict[str, str | int]]] = {
    "aragua_apto_1c": [
        {"act_code": "liberacion_hipoteca", "act_label": "Liberación parcial de hipoteca", "act_order": 1, "roles_json": json.dumps(["banco_libera", "fideicomiso"], ensure_ascii=False)},
        {"act_code": "protocolizacion_cto", "act_label": "Protocolización CTO", "act_order": 2, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "compraventa_vis", "act_label": "Compraventa VIS", "act_order": 3, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "renuncia_resolutoria", "act_label": "Renuncia condición resolutoria", "act_order": 4, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "cancelacion_comodato", "act_label": "Cancelación comodato precario", "act_order": 5, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "patrimonio_familia", "act_label": "Constitución patrimonio de familia", "act_order": 6, "roles_json": json.dumps(["compradores"], ensure_ascii=False)},
        {"act_code": "poder_especial", "act_label": "Poder especial", "act_order": 7, "roles_json": json.dumps(["compradores", "constructora"], ensure_ascii=False)},
    ],
    "aragua_apto_2c": [
        {"act_code": "liberacion_hipoteca", "act_label": "Liberación parcial de hipoteca", "act_order": 1, "roles_json": json.dumps(["banco_libera", "fideicomiso"], ensure_ascii=False)},
        {"act_code": "protocolizacion_cto", "act_label": "Protocolización CTO", "act_order": 2, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "compraventa_vis", "act_label": "Compraventa VIS", "act_order": 3, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "renuncia_resolutoria", "act_label": "Renuncia condición resolutoria", "act_order": 4, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "cancelacion_comodato", "act_label": "Cancelación comodato precario", "act_order": 5, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "patrimonio_familia", "act_label": "Constitución patrimonio de familia", "act_order": 6, "roles_json": json.dumps(["compradores"], ensure_ascii=False)},
        {"act_code": "poder_especial", "act_label": "Poder especial", "act_order": 7, "roles_json": json.dumps(["compradores", "constructora"], ensure_ascii=False)},
    ],
    "aragua_parq_2c": [
        {"act_code": "liberacion_hipoteca", "act_label": "Liberación parcial de hipoteca", "act_order": 1, "roles_json": json.dumps(["banco_libera", "fideicomiso"], ensure_ascii=False)},
        {"act_code": "protocolizacion_cto", "act_label": "Protocolización CTO", "act_order": 2, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "compraventa_vis", "act_label": "Compraventa VIS", "act_order": 3, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "renuncia_resolutoria", "act_label": "Renuncia condición resolutoria", "act_order": 4, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "cancelacion_comodato", "act_label": "Cancelación comodato precario", "act_order": 5, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "poder_especial", "act_label": "Poder especial", "act_order": 6, "roles_json": json.dumps(["compradores", "constructora"], ensure_ascii=False)},
    ],
    "aragua_parq_3c": [
        {"act_code": "liberacion_hipoteca", "act_label": "Liberación parcial de hipoteca", "act_order": 1, "roles_json": json.dumps(["banco_libera", "fideicomiso"], ensure_ascii=False)},
        {"act_code": "protocolizacion_cto", "act_label": "Protocolización CTO", "act_order": 2, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "compraventa_vis", "act_label": "Compraventa VIS", "act_order": 3, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "renuncia_resolutoria", "act_label": "Renuncia condición resolutoria", "act_order": 4, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "cancelacion_comodato", "act_label": "Cancelación comodato precario", "act_order": 5, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "poder_especial", "act_label": "Poder especial", "act_order": 6, "roles_json": json.dumps(["compradores", "constructora"], ensure_ascii=False)},
    ],
    "jaggua_fna_1c": [
        {"act_code": "liberacion_hipoteca", "act_label": "Liberación parcial de hipoteca", "act_order": 1, "roles_json": json.dumps(["banco_libera", "fideicomiso"], ensure_ascii=False)},
        {"act_code": "protocolizacion_cto", "act_label": "Protocolización CTO", "act_order": 2, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "compraventa_vis", "act_label": "Compraventa VIS", "act_order": 3, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "renuncia_resolutoria", "act_label": "Renuncia condición resolutoria", "act_order": 4, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "cancelacion_comodato", "act_label": "Cancelación comodato precario", "act_order": 5, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "constitucion_hipoteca", "act_label": "Constitución hipoteca 1er grado", "act_order": 6, "roles_json": json.dumps(["compradores", "banco_hipoteca"], ensure_ascii=False)},
        {"act_code": "patrimonio_familia", "act_label": "Constitución patrimonio de familia", "act_order": 7, "roles_json": json.dumps(["compradores"], ensure_ascii=False)},
        {"act_code": "poder_especial", "act_label": "Poder especial", "act_order": 8, "roles_json": json.dumps(["compradores", "constructora"], ensure_ascii=False)},
    ],
    "jaggua_fna_2c": [
        {"act_code": "liberacion_hipoteca", "act_label": "Liberación parcial de hipoteca", "act_order": 1, "roles_json": json.dumps(["banco_libera", "fideicomiso"], ensure_ascii=False)},
        {"act_code": "protocolizacion_cto", "act_label": "Protocolización CTO", "act_order": 2, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "compraventa_vis", "act_label": "Compraventa VIS", "act_order": 3, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "renuncia_resolutoria", "act_label": "Renuncia condición resolutoria", "act_order": 4, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "cancelacion_comodato", "act_label": "Cancelación comodato precario", "act_order": 5, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "constitucion_hipoteca", "act_label": "Constitución hipoteca 1er grado", "act_order": 6, "roles_json": json.dumps(["compradores", "banco_hipoteca"], ensure_ascii=False)},
        {"act_code": "patrimonio_familia", "act_label": "Constitución patrimonio de familia", "act_order": 7, "roles_json": json.dumps(["compradores"], ensure_ascii=False)},
        {"act_code": "poder_especial", "act_label": "Poder especial", "act_order": 8, "roles_json": json.dumps(["compradores", "constructora"], ensure_ascii=False)},
    ],
    "jaggua_bogota_1c": [
        {"act_code": "liberacion_hipoteca", "act_label": "Liberación parcial de hipoteca", "act_order": 1, "roles_json": json.dumps(["banco_libera", "fideicomiso"], ensure_ascii=False)},
        {"act_code": "protocolizacion_cto", "act_label": "Protocolización CTO", "act_order": 2, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "compraventa_vis", "act_label": "Compraventa VIS", "act_order": 3, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "renuncia_resolutoria", "act_label": "Renuncia condición resolutoria", "act_order": 4, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "constitucion_hipoteca", "act_label": "Constitución hipoteca 1er grado", "act_order": 5, "roles_json": json.dumps(["compradores", "banco_hipoteca"], ensure_ascii=False)},
        {"act_code": "patrimonio_familia", "act_label": "Constitución patrimonio de familia", "act_order": 6, "roles_json": json.dumps(["compradores"], ensure_ascii=False)},
        {"act_code": "poder_especial", "act_label": "Poder especial", "act_order": 7, "roles_json": json.dumps(["compradores", "constructora"], ensure_ascii=False)},
    ],
    "jaggua_bogota_2c": [
        {"act_code": "liberacion_hipoteca", "act_label": "Liberación parcial de hipoteca", "act_order": 1, "roles_json": json.dumps(["banco_libera", "fideicomiso"], ensure_ascii=False)},
        {"act_code": "protocolizacion_cto", "act_label": "Protocolización CTO", "act_order": 2, "roles_json": json.dumps(["fideicomiso", "constructora"], ensure_ascii=False)},
        {"act_code": "compraventa_vis", "act_label": "Compraventa VIS", "act_order": 3, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "renuncia_resolutoria", "act_label": "Renuncia condición resolutoria", "act_order": 4, "roles_json": json.dumps(["fideicomiso", "compradores"], ensure_ascii=False)},
        {"act_code": "constitucion_hipoteca", "act_label": "Constitución hipoteca 1er grado", "act_order": 5, "roles_json": json.dumps(["compradores", "banco_hipoteca"], ensure_ascii=False)},
        {"act_code": "patrimonio_familia", "act_label": "Constitución patrimonio de familia", "act_order": 6, "roles_json": json.dumps(["compradores"], ensure_ascii=False)},
        {"act_code": "poder_especial", "act_label": "Poder especial", "act_order": 7, "roles_json": json.dumps(["compradores", "constructora"], ensure_ascii=False)},
    ],
    "correccion-registro-civil": [
        {"act_code": "correccion_rc", "act_label": "Corrección de Registro Civil", "act_order": 1, "roles_json": json.dumps(["inscrito"], ensure_ascii=False)},
    ],
    "salida-del-pais": [
        {"act_code": "salida_pais", "act_label": "Permiso de salida del país", "act_order": 1, "roles_json": json.dumps(["padre_otorgante", "madre_aceptante", "menor"], ensure_ascii=False)},
    ],
}


@act_catalog_router.get("", response_model=list[ActCatalogOut])
def get_act_catalog(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    acts = db.query(ActCatalog).filter(ActCatalog.is_active.is_(True)).order_by(ActCatalog.id.asc()).all()
    return [ActCatalogOut.model_validate(item) for item in acts]
