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
    ("NUMERO_ESCRITURA", "Número de escritura", "documento"),
    ("FECHA_ESCRITURA", "Fecha de escritura", "documento"),
    ("ACTO", "Acto notarial", "documento"),
    ("NOMBRE_PERSONA", "Nombre de persona", "persona"),
    ("TIPO_DOCUMENTO", "Tipo de documento", "persona"),
    ("NUMERO_DOCUMENTO", "Número de documento", "persona"),
    ("NACIONALIDAD", "Nacionalidad", "persona"),
    ("ESTADO_CIVIL", "Estado civil", "persona"),
    ("DIRECCION", "Dirección", "persona"),
    ("TELEFONO", "Teléfono", "persona"),
    ("CORREO", "Correo electrónico", "persona"),
    ("NOMBRE_COMPRADOR_1", "Nombre comprador 1", "persona"),
    ("TIPO_DOCUMENTO_COMPRADOR_1", "Tipo de documento comprador 1", "persona"),
    ("NUMERO_DOCUMENTO_COMPRADOR_1", "Número de documento comprador 1", "persona"),
    ("NOMBRE_COMPRADOR_2", "Nombre comprador 2", "persona"),
    ("TIPO_DOCUMENTO_COMPRADOR_2", "Tipo de documento comprador 2", "persona"),
    ("NUMERO_DOCUMENTO_COMPRADOR_2", "Número de documento comprador 2", "persona"),
    ("RAZON_SOCIAL", "Razón social", "empresa"),
    ("NIT", "NIT", "empresa"),
    ("REPRESENTANTE_LEGAL", "Representante legal", "empresa"),
    ("NUMERO_APARTAMENTO", "Número de apartamento", "inmueble"),
    ("NUMERO_PARQUEADERO", "Número de parqueadero", "inmueble"),
    ("TORRE", "Torre", "inmueble"),
    ("PISO", "Piso", "inmueble"),
    ("MATRICULA_INMOBILIARIA", "Matrícula inmobiliaria", "inmueble"),
    ("NUMERO_MATRICULA", "Número de matrícula inmobiliaria", "inmueble"),
    ("NUMERO_PREDIAL", "Número predial", "inmueble"),
    ("CEDULA_CATASTRAL", "Cédula catastral", "inmueble"),
    ("CODIGO_CATASTRAL", "Código catastral", "inmueble"),
    ("DIRECCION_INMUEBLE", "Dirección del inmueble", "inmueble"),
    ("AREA_PRIVADA", "Área privada", "inmueble"),
    ("AREA_CONSTRUIDA", "Área construida", "inmueble"),
    ("COEFICIENTE_COPROPIEDAD", "Coeficiente de copropiedad", "inmueble"),
    ("VALOR_COMPRAVENTA", "Valor de compraventa", "valor"),
    ("VALOR_HIPOTECA", "Valor de hipoteca", "valor"),
    ("VALOR_CREDITO", "Valor del crédito", "valor"),
    ("VALOR_CUOTA_INICIAL", "Valor de cuota inicial", "valor"),
    ("DERECHOS_NOTARIALES", "Derechos notariales", "valor"),
    ("IVA", "IVA", "valor"),
    ("APODERADO", "Apoderado", "rol"),
    ("PODERDANTE", "Poderdante", "rol"),
    ("VENDEDOR", "Vendedor", "rol"),
    ("COMPRADOR", "Comprador", "rol"),
    ("ACREEDOR", "Acreedor", "rol"),
    ("DEUDOR", "Deudor", "rol"),
    ("HIPOTECANTE", "Hipotecante", "rol"),
]


SOURCE = "demo_seed_20260716"


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "notarial_field_catalog" not in inspector.get_table_names():
        return

    metadata = json.dumps({"source": SOURCE}, ensure_ascii=False)
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


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "notarial_field_catalog" not in inspector.get_table_names():
        return
    bind.execute(
        sa.text("DELETE FROM notarial_field_catalog WHERE metadata_json = :metadata"),
        {"metadata": json.dumps({"source": SOURCE}, ensure_ascii=False)},
    )
