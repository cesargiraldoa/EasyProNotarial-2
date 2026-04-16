from __future__ import annotations

import os
from pathlib import Path

from docx import Document as DocxDocument
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm
from openai import OpenAI

from app.core.config import get_settings


def get_openai_client() -> OpenAI:
    settings = get_settings()
    api_key = getattr(settings, "openai_api_key", "") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY no configurada")
    return OpenAI(api_key=api_key)


def build_gari_prompt(
    act_type: str,
    notary_label: str,
    notary_name: str,
    participants: list[dict],
    act_data: dict,
    template_reference_text: str | None = None,
    variante_id: str | None = None,
) -> str:
    """Construye el prompt para Gari con todos los datos del acto notarial."""
    ROLES_LABEL = {
        "comprador_1": "COMPRADOR(A) 1",
        "comprador_2": "COMPRADOR(A) 2",
        "comprador_3": "COMPRADOR(A) 3",
        "apoderado_fideicomiso": "APODERADO(A) DEL FIDEICOMISO (VENDEDOR)",
        "apoderado_fideicomitente": "APODERADO(A) DEL FIDEICOMITENTE (CONSTRUCTOR/VENDEDOR)",
        "apoderado_banco_libera": "APODERADO(A) DEL BANCO QUE LIBERA HIPOTECA",
        "apoderado_banco_hipoteca": "APODERADO(A) DEL BANCO HIPOTECANTE (NUEVO CRÉDITO)",
        "poderdante": "PODERDANTE",
        "apoderado": "APODERADO(A)",
    }

    ORDEN_ACTOS_POR_VARIANTE = {
        "aragua_apto_1c": [
            "LIBERACIÓN PARCIAL DE HIPOTECA",
            "PROTOCOLIZACIÓN CERTIFICADO TÉCNICO DE OCUPACIÓN",
            "COMPRAVENTA VIS",
            "RENUNCIA A CONDICIÓN RESOLUTORIA",
            "CANCELACIÓN DE COMODATO",
            "CONSTITUCIÓN DE PATRIMONIO DE FAMILIA INEMBARGABLE",
            "PODER ESPECIAL",
        ],
        "aragua_apto_2c": [
            "LIBERACIÓN PARCIAL DE HIPOTECA",
            "PROTOCOLIZACIÓN CERTIFICADO TÉCNICO DE OCUPACIÓN",
            "COMPRAVENTA VIS",
            "RENUNCIA A CONDICIÓN RESOLUTORIA",
            "CANCELACIÓN DE COMODATO",
            "CONSTITUCIÓN DE PATRIMONIO DE FAMILIA INEMBARGABLE",
            "PODER ESPECIAL",
        ],
        "aragua_parq_2c": [
            "LIBERACIÓN PARCIAL DE HIPOTECA",
            "PROTOCOLIZACIÓN CERTIFICADO TÉCNICO DE OCUPACIÓN",
            "COMPRAVENTA VIS",
            "RENUNCIA A CONDICIÓN RESOLUTORIA",
            "CANCELACIÓN DE COMODATO",
            "PODER ESPECIAL",
        ],
        "aragua_parq_3c": [
            "LIBERACIÓN PARCIAL DE HIPOTECA",
            "PROTOCOLIZACIÓN CERTIFICADO TÉCNICO DE OCUPACIÓN",
            "COMPRAVENTA VIS",
            "RENUNCIA A CONDICIÓN RESOLUTORIA",
            "CANCELACIÓN DE COMODATO",
            "PODER ESPECIAL",
        ],
        "jaggua_fna_1c": [
            "LIBERACIÓN PARCIAL DE HIPOTECA",
            "PROTOCOLIZACIÓN CERTIFICADO TÉCNICO DE OCUPACIÓN",
            "COMPRAVENTA VIS",
            "RENUNCIA A CONDICIÓN RESOLUTORIA",
            "CANCELACIÓN DE COMODATO",
            "CONSTITUCIÓN DE HIPOTECA ABIERTA DE PRIMER GRADO",
            "CONSTITUCIÓN DE PATRIMONIO DE FAMILIA INEMBARGABLE",
            "PODER ESPECIAL",
        ],
        "jaggua_fna_2c": [
            "LIBERACIÓN PARCIAL DE HIPOTECA",
            "PROTOCOLIZACIÓN CERTIFICADO TÉCNICO DE OCUPACIÓN",
            "COMPRAVENTA VIS",
            "RENUNCIA A CONDICIÓN RESOLUTORIA",
            "CANCELACIÓN DE COMODATO",
            "CONSTITUCIÓN DE HIPOTECA ABIERTA DE PRIMER GRADO",
            "CONSTITUCIÓN DE PATRIMONIO DE FAMILIA INEMBARGABLE",
            "PODER ESPECIAL",
        ],
        "jaggua_bogota_1c": [
            "LIBERACIÓN PARCIAL DE HIPOTECA",
            "PROTOCOLIZACIÓN CERTIFICADO TÉCNICO DE OCUPACIÓN",
            "COMPRAVENTA VIS",
            "RENUNCIA A CONDICIÓN RESOLUTORIA",
            "CONSTITUCIÓN DE HIPOTECA ABIERTA DE PRIMER GRADO",
            "CONSTITUCIÓN DE PATRIMONIO DE FAMILIA INEMBARGABLE",
            "PODER ESPECIAL",
        ],
        "jaggua_bogota_2c": [
            "LIBERACIÓN PARCIAL DE HIPOTECA",
            "PROTOCOLIZACIÓN CERTIFICADO TÉCNICO DE OCUPACIÓN",
            "COMPRAVENTA VIS",
            "RENUNCIA A CONDICIÓN RESOLUTORIA",
            "CONSTITUCIÓN DE HIPOTECA ABIERTA DE PRIMER GRADO",
            "CONSTITUCIÓN DE PATRIMONIO DE FAMILIA INEMBARGABLE",
            "PODER ESPECIAL",
        ],
    }

    grouped_participants: dict[str, list[dict]] = {}
    for participant in participants:
        role_code = participant.get("role_code", "") or ""
        grouped_participants.setdefault(role_code, []).append(participant)

    participants_text = ""
    ordered_role_codes = list(ROLES_LABEL.keys()) + [
        code for code in grouped_participants if code not in ROLES_LABEL
    ]
    for role_code in ordered_role_codes:
        for p in grouped_participants.get(role_code, []):
            role_label = p.get("role_label", "") or p.get("role_code", "")
            participants_text += (
                f"\n- ROL: {ROLES_LABEL.get(role_code, str(role_label).upper())}"
            )
            participants_text += f"\n  Nombre completo: {p.get('full_name', '')}"
            participants_text += f"\n  Tipo documento: {p.get('document_type', '')}"
            participants_text += f"\n  Número documento: {p.get('document_number', '')}"
            participants_text += f"\n  Sexo: {p.get('sex', '')}"
            participants_text += f"\n  Nacionalidad: {p.get('nationality', '')}"
            participants_text += f"\n  Estado civil: {p.get('marital_status', '')}"
            participants_text += f"\n  Profesión u oficio: {p.get('profession', '')}"
            participants_text += f"\n  Municipio de domicilio: {p.get('municipality', '')}"
            participants_text += (
                f"\n  ¿Está de tránsito?: {'Sí' if p.get('is_transient') else 'No'}"
            )
            participants_text += f"\n  Teléfono: {p.get('phone', '')}"
            participants_text += f"\n  Dirección: {p.get('address', '')}"
            participants_text += f"\n  Email: {p.get('email', '')}"

    act_data_text = ""
    for key, value in act_data.items():
        act_data_text += f"\n- {key}: {value}"

    reference_section = ""
    if template_reference_text:
        reference_section = f"""
PLANTILLA DE REFERENCIA DEL ACTO (usar como guía de estructura y redacción):
---
{template_reference_text[:6000]}
---
"""

    variante_section = ""
    if variante_id and variante_id in ORDEN_ACTOS_POR_VARIANTE:
        actos_ordenados = ORDEN_ACTOS_POR_VARIANTE[variante_id]
        actos_texto = "\n".join(
            f"{idx}. {acto}" for idx, acto in enumerate(actos_ordenados, start=1)
        )
        variante_section = f"""
VARIANTE DOCUMENTAL: {variante_id}
ACTOS QUE DEBE CONTENER EN ESTE ORDEN EXACTO:
{actos_texto}
"""

    return f"""Eres un experto en derecho notarial colombiano. Tu tarea es redactar un instrumento público notarial completo y correcto jurídicamente.

NOTARÍA: {notary_label}
NOTARIO TITULAR: {notary_name}
TIPO DE ACTO: {act_type}

INTERVINIENTES:{participants_text}

DATOS DEL ACTO:{act_data_text}

{variante_section}

{reference_section}

INSTRUCCIONES DE REDACCIÓN:
1. Redacta el documento completo en español formal notarial colombiano
2. Usa el formato de escritura pública con guiones separadores: "- - - - - - - - -"
3. Incluye todas las secciones requeridas para este tipo de acto según la ley colombiana
4. Inserta los datos de los intervinientes exactamente como se proporcionan
5. Usa el género gramatical correcto según el sexo de cada interviniente
6. Incluye las constancias notariales obligatorias:
   - Autorización de tratamiento de datos (Ley 1581 de 2012)
   - Advertencia sobre verificación de datos (Art. 102 Decreto Ley 960 de 1970)
   - Deber de consejo del notario
7. Incluye la sección de liquidación de derechos notariales con los valores proporcionados
8. Incluye la sección de firmas con los datos de los comparecientes
9. El documento debe estar listo para ser firmado sin marcadores de posición ni etiquetas
10. Cada interviniente debe aparecer con EXACTAMENTE los datos proporcionados — nunca inventar ni completar datos faltantes.
11. Cada acto comienza con su título en mayúsculas entre líneas de guiones: - - - - PRIMER ACTO: LIBERACIÓN PARCIAL DE HIPOTECA - - - -
12. Separar párrafos con: - - - - - - - - - - - - - - - - - - - -
13. El documento debe terminar con: OTORGAMIENTO Y AUTORIZACIÓN, luego INSTRUCCIÓN ADMINISTRATIVA #17 DE AGOSTO DE 2010, luego ADVERTENCIAS, luego AUTORIZACIÓN LEY 1581 DE 2012, luego ARTÍCULO 29 LEY 675 DE 2001.
14. El rol del APODERADO(A) DEL FIDEICOMISO actúa como vocera del fideicomiso, no como propietario ni constructor.
15. El rol del APODERADO(A) DEL FIDEICOMITENTE actúa como constructor/promotor/comercializador.

FORMATO DE SALIDA:
- Solo el texto del documento, sin explicaciones adicionales
- Sin etiquetas ni placeholders
- Con los datos reales insertados
- En formato que pueda exportarse directamente a Word
"""


def generate_notarial_document(
    act_type: str,
    notary_label: str,
    notary_name: str,
    participants: list[dict],
    act_data: dict,
    template_reference_text: str | None = None,
    max_tokens: int = 4000,
) -> str:
    """Genera el documento notarial completo usando GPT-4o."""
    client = get_openai_client()
    prompt = build_gari_prompt(
        act_type=act_type,
        notary_label=notary_label,
        notary_name=notary_name,
        participants=participants,
        act_data=act_data,
        template_reference_text=template_reference_text,
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "Eres Gari, el asistente notarial de EasyPro. Redactas instrumentos públicos notariales en Colombia con precisión jurídica y formato correcto. Solo produces el texto del documento, sin explicaciones adicionales.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
        max_tokens=max_tokens,
    )

    return response.choices[0].message.content or ""


def save_gari_document_as_docx(text: str, output_path: str | Path) -> Path:
    """Guarda el texto generado por Gari como archivo .docx simple."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    doc = DocxDocument()
    section = doc.sections[0]
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(3)
    section.right_margin = Cm(3)

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            doc.add_paragraph()
            continue
        p = doc.add_paragraph(line)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if line.startswith("- - -") or line.startswith("---"):
            run = p.runs[0] if p.runs else p.add_run(line)
            run.bold = True

    doc.save(output)
    return output


def resolver_escritura(
    proyecto: str,
    tipo_inmueble: str,
    num_compradores: int,
    banco_hipotecante: str | None,
    campos_caso: dict,
) -> dict:
    """Resuelve la variante de escritura y valida campos requeridos para el caso."""

    def _esta_vacio(valor: object) -> bool:
        if valor is None:
            return True
        if isinstance(valor, str):
            return valor.strip() == ""
        if isinstance(valor, (list, dict, tuple, set)):
            return len(valor) == 0
        return False

    actos_aragua_apto = [
        "liberacion_hipoteca",
        "cto",
        "compraventa_vis",
        "renuncia_resolutoria",
        "cancelacion_comodato",
        "patrimonio_familia",
        "poder_especial",
    ]
    campos_aragua_apto = [
        "numero_apartamento",
        "matricula_inmobiliaria",
        "cedula_catastral",
        "linderos",
        "numero_piso",
        "area_privada",
        "area_total",
        "altura",
        "coeficiente_copropiedad",
        "avaluo_catastral",
        "valor_venta",
        "fecha_promesa_compraventa",
        "paz_salvo_predial_numero",
        "paz_salvo_predial_fecha",
        "paz_salvo_predial_vigencia",
    ]

    actos_aragua_parq = [
        "liberacion_hipoteca",
        "cto",
        "compraventa_vis",
        "renuncia_resolutoria",
        "cancelacion_comodato",
        "poder_especial",
    ]
    campos_aragua_parq = [
        "numero_parqueadero",
        "matricula_inmobiliaria",
        "cedula_catastral",
        "linderos",
        "area_privada",
        "altura",
        "coeficiente_copropiedad",
        "avaluo_catastral",
        "valor_venta",
        "fecha_promesa_compraventa",
        "paz_salvo_predial_numero",
        "paz_salvo_predial_fecha",
        "paz_salvo_predial_vigencia",
    ]

    actos_jaggua_fna = [
        "liberacion_hipoteca",
        "cto",
        "compraventa_vis",
        "renuncia_resolutoria",
        "cancelacion_comodato",
        "hipoteca_primer_grado",
        "patrimonio_familia",
        "poder_especial",
    ]
    campos_jaggua_fna = [
        "numero_apartamento",
        "matricula_inmobiliaria",
        "linderos",
        "numero_piso",
        "area_privada",
        "area_total",
        "altura",
        "coeficiente_copropiedad",
        "valor_venta",
        "cuota_inicial",
        "valor_hipoteca",
        "origen_cuota_inicial",
        "fecha_promesa_compraventa",
        "inmueble_sera_casa_habitacion",
        "tiene_bien_afectado",
    ]

    actos_jaggua_bogota = [
        "liberacion_hipoteca",
        "cto",
        "compraventa_vis",
        "renuncia_resolutoria",
        "hipoteca_primer_grado",
        "patrimonio_familia",
        "poder_especial",
    ]
    campos_jaggua_bogota = [
        "numero_apartamento",
        "matricula_inmobiliaria",
        "linderos",
        "numero_piso",
        "area_privada",
        "area_total",
        "altura",
        "valor_venta",
        "cuota_inicial",
        "valor_hipoteca",
        "origen_cuota_inicial",
        "fecha_promesa_compraventa",
        "inmueble_sera_casa_habitacion",
        "tiene_bien_afectado",
    ]

    variantes = {
        ("aragua", "apartamento", 1, None): {
            "variante_id": "aragua_apto_1c",
            "plantilla_id": "aragua_apto_1c",
            "actos_requeridos": actos_aragua_apto,
            "campos_requeridos": campos_aragua_apto,
            "banco_nit": "890.903.938-8",
            "max_tokens_estimado": 5500,
        },
        ("aragua", "apartamento", 2, None): {
            "variante_id": "aragua_apto_2c",
            "plantilla_id": "aragua_apto_2c",
            "actos_requeridos": actos_aragua_apto,
            "campos_requeridos": campos_aragua_apto,
            "banco_nit": "890.903.938-8",
            "max_tokens_estimado": 5800,
        },
        ("aragua", "parqueadero", 2, None): {
            "variante_id": "aragua_parq_2c",
            "plantilla_id": "aragua_parq_2c",
            "actos_requeridos": actos_aragua_parq,
            "campos_requeridos": campos_aragua_parq,
            "banco_nit": "890.903.938-8",
            "max_tokens_estimado": 5200,
        },
        ("aragua", "parqueadero", 3, None): {
            "variante_id": "aragua_parq_3c",
            "plantilla_id": "aragua_parq_3c",
            "actos_requeridos": actos_aragua_parq,
            "campos_requeridos": campos_aragua_parq,
            "banco_nit": "890.903.938-8",
            "max_tokens_estimado": 5400,
        },
        ("jaggua", "apartamento", 1, "fna"): {
            "variante_id": "jaggua_fna_1c",
            "plantilla_id": "jaggua_fna_1c",
            "actos_requeridos": actos_jaggua_fna,
            "campos_requeridos": campos_jaggua_fna,
            "banco_nit": "899.999.284-4",
            "max_tokens_estimado": 6500,
        },
        ("jaggua", "apartamento", 2, "fna"): {
            "variante_id": "jaggua_fna_2c",
            "plantilla_id": "jaggua_fna_2c",
            "actos_requeridos": actos_jaggua_fna,
            "campos_requeridos": campos_jaggua_fna,
            "banco_nit": "899.999.284-4",
            "max_tokens_estimado": 6800,
        },
        ("jaggua", "apartamento", 1, "bogota"): {
            "variante_id": "jaggua_bogota_1c",
            "plantilla_id": "jaggua_bogota_1c",
            "actos_requeridos": actos_jaggua_bogota,
            "campos_requeridos": campos_jaggua_bogota,
            "banco_nit": "860.002.964-4",
            "max_tokens_estimado": 6800,
        },
        ("jaggua", "apartamento", 2, "bogota"): {
            "variante_id": "jaggua_bogota_2c",
            "plantilla_id": "jaggua_bogota_2c",
            "actos_requeridos": actos_jaggua_bogota,
            "campos_requeridos": campos_jaggua_bogota,
            "banco_nit": "860.002.964-4",
            "max_tokens_estimado": 7200,
        },
    }

    proyecto_norm = (proyecto or "").strip().lower()
    tipo_inmueble_norm = (tipo_inmueble or "").strip().lower()
    banco_norm = (banco_hipotecante or "").strip().lower() or None

    key = (proyecto_norm, tipo_inmueble_norm, num_compradores, banco_norm)
    if key not in variantes:
        raise ValueError(
            "No existe una variante de escritura para la combinación "
            f"proyecto={proyecto_norm}, tipo_inmueble={tipo_inmueble_norm}, "
            f"num_compradores={num_compradores}, banco_hipotecante={banco_norm}."
        )

    variante = variantes[key]
    campos_requeridos = variante["campos_requeridos"]
    campos_faltantes = [
        campo for campo in campos_requeridos if _esta_vacio(campos_caso.get(campo))
    ]

    return {
        "variante_id": variante["variante_id"],
        "plantilla_id": variante["plantilla_id"],
        "actos_requeridos": list(variante["actos_requeridos"]),
        "campos_requeridos": list(campos_requeridos),
        "campos_faltantes": campos_faltantes,
        "banco_nit": variante["banco_nit"],
        "max_tokens_estimado": variante["max_tokens_estimado"],
    }


if __name__ == "__main__":
    ejemplo_aragua = resolver_escritura(
        proyecto="aragua",
        tipo_inmueble="apartamento",
        num_compradores=1,
        banco_hipotecante=None,
        campos_caso={
            "numero_apartamento": "1201",
            "matricula_inmobiliaria": "50N-123456",
            "cedula_catastral": "AA-001",
            "linderos": "Norte con...",
            "numero_piso": "12",
            "area_privada": "80",
            "area_total": "90",
            "altura": "2.40",
            "coeficiente_copropiedad": "1.25%",
            "avaluo_catastral": "180000000",
            "valor_venta": "250000000",
            "fecha_promesa_compraventa": "2026-04-01",
            "paz_salvo_predial_numero": "PSP-55",
            "paz_salvo_predial_fecha": "2026-03-20",
            "paz_salvo_predial_vigencia": "2026",
        },
    )
    print("Ejemplo aragua apartamento 1c:")
    print(ejemplo_aragua)

    ejemplo_jaggua = resolver_escritura(
        proyecto="jaggua",
        tipo_inmueble="apartamento",
        num_compradores=2,
        banco_hipotecante="bogota",
        campos_caso={
            "numero_apartamento": "905",
            "matricula_inmobiliaria": "50C-765432",
            "linderos": "Sur con...",
            "numero_piso": "9",
            "area_privada": "70",
            "area_total": "78",
            "altura": "2.35",
            "valor_venta": "320000000",
            "cuota_inicial": "80000000",
            "valor_hipoteca": "240000000",
            "origen_cuota_inicial": "Ahorros",
            "fecha_promesa_compraventa": "2026-04-10",
            "inmueble_sera_casa_habitacion": True,
            "tiene_bien_afectado": False,
        },
    )
    print("Ejemplo jaggua bogota 2c:")
    print(ejemplo_jaggua)
