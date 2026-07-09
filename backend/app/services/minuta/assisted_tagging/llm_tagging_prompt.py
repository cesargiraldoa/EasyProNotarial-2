from __future__ import annotations

from app.services.minuta.assisted_tagging.models import DocxStructure


MASTER_PROMPT = """Eres el motor embebido de EasyPro para pre-etiquetado de minutas notariales colombianas.

Reglas obligatorias:
- Devuelve solo JSON valido.
- No inventes datos.
- No devuelvas instrucciones para el humano.
- No uses marcadores {{CAMPO}} en la respuesta.
- Identifica textos variables reales que deberian quedar en rojo para revision humana.
- Texto fijo permanece negro. Texto variable, intervenido, insertado o editable queda rojo.
- El backend validara y reconstruira el DOCX; tu salida es solo una propuesta estructurada.

Formato exacto:
{
  "fields": [
    {
      "field_code": "snake_case",
      "label": "Etiqueta humana",
      "text": "texto exacto existente en el DOCX",
      "section": "personas|inmueble|valores|fechas|notaria|acto|general",
      "confidence": 0.0,
      "block_id": "b1",
      "reason": "breve"
    }
  ]
}
"""


def build_prompt(structure: DocxStructure, document_type: str) -> list[dict[str, str]]:
    user_payload = {
        "document_type": document_type,
        "structure": structure.to_llm_payload(),
    }
    return [
        {"role": "system", "content": MASTER_PROMPT},
        {"role": "user", "content": str(user_payload)},
    ]
