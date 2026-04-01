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
) -> str:
    """Construye el prompt para Gari con todos los datos del acto notarial."""
    participants_text = ""
    for p in participants:
        participants_text += f"\n- Rol: {p.get('role_label', p.get('role_code', ''))}"
        participants_text += f"\n  Nombre: {p.get('full_name', '')}"
        participants_text += f"\n  Tipo documento: {p.get('document_type', '')}"
        participants_text += f"\n  Número documento: {p.get('document_number', '')}"
        participants_text += f"\n  Sexo: {p.get('sex', '')}"
        participants_text += f"\n  Nacionalidad: {p.get('nationality', '')}"
        participants_text += f"\n  Estado civil: {p.get('marital_status', '')}"
        participants_text += f"\n  Profesión: {p.get('profession', '')}"
        participants_text += f"\n  Municipio de domicilio: {p.get('municipality', '')}"
        participants_text += f"\n  De tránsito: {'Sí' if p.get('is_transient') else 'No'}"
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

    return f"""Eres un experto en derecho notarial colombiano. Tu tarea es redactar un instrumento público notarial completo y correcto jurídicamente.

NOTARÍA: {notary_label}
NOTARIO TITULAR: {notary_name}
TIPO DE ACTO: {act_type}

INTERVINIENTES:{participants_text}

DATOS DEL ACTO:{act_data_text}

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
        max_tokens=4000,
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
