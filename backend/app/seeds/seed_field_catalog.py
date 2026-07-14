from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy.dialects.postgresql import insert

from app.db.session import SessionLocal
from app.models.notarial_field_catalog import NotarialFieldCatalog


SEED_FIELDS = [
    ("COMPRADOR_1", "Comprador 1 — Nombre completo", "text", "persona", None),
    ("COMPRADOR_2", "Comprador 2 — Nombre completo", "text", "persona", None),
    ("COMPRADOR_3", "Comprador 3 — Nombre completo", "text", "persona", None),
    ("COMPRADOR_4", "Comprador 4 — Nombre completo", "text", "persona", None),
    ("VENDEDOR_1", "Vendedor 1 — Nombre completo", "text", "persona", None),
    ("VENDEDOR_2", "Vendedor 2 — Nombre completo", "text", "persona", None),
    ("DEUDOR_HIPOTECANTE_1", "Deudor hipotecante 1", "text", "persona", None),
    ("DEUDOR_HIPOTECANTE_2", "Deudor hipotecante 2", "text", "persona", None),
    ("APODERADO_1", "Apoderado 1", "text", "persona", None),
    ("CONYUGE_COMPRADOR_1", "Cónyuge del comprador 1", "text", "persona", None),
    ("CONYUGE_VENDEDOR_1", "Cónyuge del vendedor 1", "text", "persona", None),
    ("NOTARIO", "Notario titular", "text", "persona", None),
    ("PROTOCOLISTA", "Protocolista", "text", "persona", None),
    ("CEDULA_COMPRADOR_1", "Cédula comprador 1", "text", "persona", None),
    ("CEDULA_COMPRADOR_2", "Cédula comprador 2", "text", "persona", None),
    ("CEDULA_VENDEDOR_1", "Cédula vendedor 1", "text", "persona", None),
    ("CEDULA_DEUDOR_HIPOTECANTE_1", "Cédula deudor hipotecante 1", "text", "persona", None),
    ("VALOR_COMPRAVENTA", "Valor de la compraventa", "monetary", "valor", None),
    ("VALOR_HIPOTECA", "Valor de la hipoteca", "monetary", "valor", None),
    ("VALOR_LIBERACION", "Valor de la liberación", "monetary", "valor", None),
    ("CUOTA_INICIAL", "Cuota inicial", "monetary", "valor", None),
    ("DERECHOS_NOTARIALES", "Derechos notariales", "monetary", "valor", None),
    ("MATRICULA_INMOBILIARIA", "Matrícula inmobiliaria", "text", "inmueble", None),
    ("MUNICIPIO_INMUEBLE", "Municipio del inmueble", "text", "inmueble", None),
    ("DEPARTAMENTO_INMUEBLE", "Departamento del inmueble", "text", "inmueble", None),
    ("DIRECCION_INMUEBLE", "Dirección del inmueble", "text", "inmueble", None),
    ("TIPO_INMUEBLE", "Tipo de inmueble", "list", "inmueble", ["apartamento", "casa", "local", "lote", "parqueadero", "bodega", "oficina", "deposito"]),
    ("NUMERO_INMUEBLE", "Número del inmueble/unidad", "text", "inmueble", None),
    ("CONJUNTO_EDIFICIO", "Nombre del conjunto o edificio", "text", "inmueble", None),
    ("CEDULA_CATASTRAL", "Cédula catastral", "text", "inmueble", None),
    ("AREA_CONSTRUIDA", "Área construida", "text", "inmueble", None),
    ("PISO_INMUEBLE", "Piso o planta", "text", "inmueble", None),
    ("LINDEROS", "Linderos completos", "text", "inmueble", None),
    ("FECHA_ESCRITURA", "Fecha de otorgamiento de la escritura", "date", "fecha", None),
    ("FECHA_ESCRITURA_ANTERIOR", "Fecha de la escritura de adquisición anterior", "date", "fecha", None),
    ("NUMERO_ESCRITURA", "Número de escritura", "text", "notaria", None),
    ("NOMBRE_NOTARIA", "Nombre de la notaría", "text", "notaria", None),
    ("MUNICIPIO_NOTARIA", "Municipio de la notaría", "text", "notaria", None),
    ("NUMERO_ESCRITURA_ANTERIOR", "Número de escritura de adquisición anterior", "text", "notaria", None),
    ("NOTARIA_ANTERIOR", "Notaría de la escritura anterior", "text", "notaria", None),
]


def seed_field_catalog() -> int:
    with SessionLocal() as db:
        existing_codes = {
            code
            for (code,) in db.query(NotarialFieldCatalog.code)
            .filter(NotarialFieldCatalog.scope == "global", NotarialFieldCatalog.notary_id.is_(None))
            .all()
        }

    rows = [
        {
            "code": code,
            "label": label,
            "field_type": field_type,
            "category": category,
            "description": label,
            "options_json": json.dumps(options, ensure_ascii=False) if options else None,
            "scope": "global",
            "notary_id": None,
            "is_active": True,
            "created_by_user_id": None,
            "metadata_json": "{}",
        }
        for code, label, field_type, category, options in SEED_FIELDS
        if code not in existing_codes
    ]

    if not rows:
        return 0

    with SessionLocal() as db:
        statement = insert(NotarialFieldCatalog).values(rows)
        statement = statement.on_conflict_do_nothing()
        result = db.execute(statement)
        db.commit()
        return int(result.rowcount or 0)


def main() -> None:
    inserted = seed_field_catalog()
    print(f"[OK] Campos globales insertados: {inserted}.")


if __name__ == "__main__":
    main()
