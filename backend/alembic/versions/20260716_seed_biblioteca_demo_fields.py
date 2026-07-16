"""seed biblioteca demo field library

Revision ID: 20260716_seed_biblioteca_demo_fields
Revises: 20260715_add_biblioteca_learning
Create Date: 2026-07-16
"""

from __future__ import annotations

import json

from alembic import op
import sqlalchemy as sa


revision = "20260716_seed_biblioteca_demo_fields"
down_revision = "20260715_add_biblioteca_learning"
branch_labels = None
depends_on = None


FIELDS = [
    ("DOCUMENTO", "Documento", "documento"),
    ("NUMERO_ESCRITURA", "Numero de escritura", "documento"),
    ("FECHA_ESCRITURA", "Fecha de escritura", "documento"),
    ("ACTO", "Acto notarial", "documento"),
    ("NOMBRE_PERSONA", "Nombre de persona", "persona"),
    ("TIPO_DOCUMENTO", "Tipo de documento", "persona"),
    ("NUMERO_DOCUMENTO", "Numero de documento", "persona"),
    ("NACIONALIDAD", "Nacionalidad", "persona"),
    ("ESTADO_CIVIL", "Estado civil", "persona"),
    ("DIRECCION", "Direccion", "persona"),
    ("TELEFONO", "Telefono", "persona"),
    ("CORREO", "Correo electronico", "persona"),
    ("PROFESION", "Profesion", "persona"),
    ("ACTIVIDAD_ECONOMICA", "Actividad economica", "persona"),
    ("NOMBRE_COMPRADOR_1", "Nombre comprador 1", "persona"),
    ("TIPO_DOCUMENTO_COMPRADOR_1", "Tipo de documento comprador 1", "persona"),
    ("NUMERO_DOCUMENTO_COMPRADOR_1", "Numero de documento comprador 1", "persona"),
    ("NOMBRE_COMPRADOR_2", "Nombre comprador 2", "persona"),
    ("TIPO_DOCUMENTO_COMPRADOR_2", "Tipo de documento comprador 2", "persona"),
    ("NUMERO_DOCUMENTO_COMPRADOR_2", "Numero de documento comprador 2", "persona"),
    ("RAZON_SOCIAL", "Razon social", "empresa"),
    ("NIT", "NIT", "empresa"),
    ("REPRESENTANTE_LEGAL", "Representante legal", "empresa"),
    ("NUMERO_APARTAMENTO", "Numero de apartamento", "inmueble"),
    ("NUMERO_PARQUEADERO", "Numero de parqueadero", "inmueble"),
    ("TORRE", "Torre", "inmueble"),
    ("PISO", "Piso", "inmueble"),
    ("MATRICULA_INMOBILIARIA", "Matricula inmobiliaria", "inmueble"),
    ("NUMERO_MATRICULA", "Numero de matricula inmobiliaria", "inmueble"),
    ("NUMERO_PREDIAL", "Numero predial", "inmueble"),
    ("CEDULA_CATASTRAL", "Cedula catastral", "inmueble"),
    ("CODIGO_CATASTRAL", "Codigo catastral", "inmueble"),
    ("DIRECCION_INMUEBLE", "Direccion del inmueble", "inmueble"),
    ("AREA_PRIVADA", "Area privada", "inmueble"),
    ("AREA_CONSTRUIDA", "Area construida", "inmueble"),
    ("COEFICIENTE_COPROPIEDAD", "Coeficiente de copropiedad", "inmueble"),
    ("LINDEROS", "Linderos", "inmueble"),
    ("VALOR_COMPRAVENTA", "Valor de compraventa", "valor"),
    ("VALOR_HIPOTECA", "Valor de hipoteca", "valor"),
    ("VALOR_CREDITO", "Valor del credito", "valor"),
    ("VALOR_CUOTA_INICIAL", "Valor de cuota inicial", "valor"),
    ("DERECHOS_NOTARIALES", "Derechos notariales", "valor"),
    ("IVA", "IVA", "valor"),
    ("COMPRADOR", "Comprador", "rol"),
    ("VENDEDOR", "Vendedor", "rol"),
    ("DEUDOR", "Deudor", "rol"),
    ("HIPOTECANTE", "Hipotecante", "rol"),
    ("ACREEDOR", "Acreedor", "rol"),
    ("APODERADO", "Apoderado", "rol"),
    ("PODERDANTE", "Poderdante", "rol"),
    ("FIDEICOMITENTE", "Fideicomitente", "rol"),
    ("FIDEICOMISARIO", "Fideicomisario", "rol"),
]

ALIASES = [
    ("CEDULA_CATRASTAL", "CEDULA_CATASTRAL"),
    ("CODIGO_CATRASTAL", "CODIGO_CATASTRAL"),
    ("TIPO_DE_DOCUMENTO", "TIPO_DOCUMENTO"),
    ("NUMERO_ESCRITURA_EN_NUMEROS", "NUMERO_ESCRITURA"),
    ("NUMERO_ESCRITURA_NUMEROS", "NUMERO_ESCRITURA"),
]

SOURCE = "demo_seed_20260716"


def upgrade() -> None:
    bind = op.get_bind()
    table_names = set(sa.inspect(bind).get_table_names())
    metadata = json.dumps({"source": SOURCE}, ensure_ascii=False)

    if "notarial_field_catalog" in table_names:
        for code, label, category in FIELDS:
            exists = bind.execute(
                sa.text(
                    "SELECT 1 FROM notarial_field_catalog "
                    "WHERE code = :code AND scope = 'global' AND notary_id IS NULL LIMIT 1"
                ),
                {"code": code},
            ).first()
            if exists:
                continue
            bind.execute(
                sa.text(
                    "INSERT INTO notarial_field_catalog "
                    "(code, label, field_type, category, description, options_json, scope, notary_id, "
                    "is_active, created_by_user_id, metadata_json) "
                    "VALUES (:code, :label, 'text', :category, NULL, NULL, 'global', NULL, true, NULL, :metadata)"
                ),
                {"code": code, "label": label, "category": category, "metadata": metadata},
            )

    if "field_definitions" in table_names:
        for code, label, category in FIELDS:
            exists = bind.execute(
                sa.text("SELECT 1 FROM field_definitions WHERE field_code = :code LIMIT 1"),
                {"code": code},
            ).first()
            if exists:
                continue
            bind.execute(
                sa.text(
                    "INSERT INTO field_definitions "
                    "(field_code, display_name, data_type, field_group, legal_role, act_type, "
                    "description, status, confidence, source, metadata_json) "
                    "VALUES (:code, :label, 'text', :category, NULL, NULL, NULL, "
                    "'approved', 1, :source, :metadata)"
                ),
                {"code": code, "label": label, "category": category, "source": SOURCE, "metadata": metadata},
            )

    if "field_aliases" in table_names and "field_definitions" in table_names:
        for raw_code, canonical_code in ALIASES:
            exists = bind.execute(
                sa.text(
                    "SELECT 1 FROM field_aliases "
                    "WHERE raw_field_code = :raw_code AND canonical_field_code = :canonical_code LIMIT 1"
                ),
                {"raw_code": raw_code, "canonical_code": canonical_code},
            ).first()
            if exists:
                continue
            definition = bind.execute(
                sa.text("SELECT id FROM field_definitions WHERE field_code = :canonical_code LIMIT 1"),
                {"canonical_code": canonical_code},
            ).first()
            bind.execute(
                sa.text(
                    "INSERT INTO field_aliases "
                    "(raw_field_code, canonical_field_code, field_definition_id, frequency, status, source, metadata_json) "
                    "VALUES (:raw_code, :canonical_code, :field_definition_id, 1, 'approved', :source, :metadata)"
                ),
                {
                    "raw_code": raw_code,
                    "canonical_code": canonical_code,
                    "field_definition_id": definition[0] if definition else None,
                    "source": SOURCE,
                    "metadata": metadata,
                },
            )


def downgrade() -> None:
    bind = op.get_bind()
    table_names = set(sa.inspect(bind).get_table_names())
    metadata = json.dumps({"source": SOURCE}, ensure_ascii=False)
    if "field_aliases" in table_names:
        bind.execute(sa.text("DELETE FROM field_aliases WHERE metadata_json = :metadata"), {"metadata": metadata})
    if "field_definitions" in table_names:
        bind.execute(sa.text("DELETE FROM field_definitions WHERE metadata_json = :metadata"), {"metadata": metadata})
    if "notarial_field_catalog" in table_names:
        bind.execute(sa.text("DELETE FROM notarial_field_catalog WHERE metadata_json = :metadata"), {"metadata": metadata})
