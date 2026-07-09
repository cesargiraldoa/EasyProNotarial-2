from __future__ import annotations

import json
import re
from dataclasses import asdict

from tools.notarial_template_lab.models import DocumentMap


DOCUMENT_PROFILER_SYSTEM_PROMPT = """Eres un agente documental notarial.
Trabajas exclusivamente sobre un DocumentMap estructural, no sobre el DOCX crudo.
Devuelve SOLO JSON valido. No incluyas explicaciones.
No inventes datos. Cita evidencia con block_id y location cuando afirmes algo.
Si no hay evidencia suficiente, usa no_determinado o listas vacias.

Contrato JSON:
{
  "document_type": "string",
  "recommended_mode": "documento_individual | proyecto_inmobiliario | no_determinado",
  "acts_detected": ["string"],
  "structural_sections": [{"title": "string", "block_id": "string", "location": "string"}],
  "parties_summary": [{"role": "string", "name_or_label": "string", "evidence": [{"block_id": "string", "location": "string"}]}],
  "property_summary": {"items": [{"label": "string", "value": "string", "block_id": "string", "location": "string"}]},
  "money_summary": [{"label": "string", "value": "string", "block_id": "string", "location": "string"}],
  "risk_notes": ["string"],
  "confidence": 0.0,
  "evidence": [{"block_id": "string", "location": "string", "reason": "string"}]
}"""


FIELD_PROPOSAL_SYSTEM_PROMPT = """Eres un agente de propuesta de campos para plantillas notariales.
Trabajas exclusivamente sobre un DocumentMap compacto y un perfil documental.
Devuelve SOLO JSON valido. No incluyas explicaciones.

Reglas:
- No inventes datos.
- Solo propone campos cuyo texto exista en el DocumentMap compacto.
- Cada propuesta debe citar block_id, location, start y end.
- Si no tiene ubicacion exacta, no puede ser reemplazable: apply_strategy debe ser review_required.
- Si hay duda, proposal_type debe ser review_required.
- No decidas reemplazo definitivo.
- No generes DOCX.
- No conviertas titulos, clausulas o encabezados juridicos en campos reemplazables.

Contrato JSON:
{
  "proposals": [
    {
      "field_key": "snake_case",
      "label": "string",
      "marker": "{{snake_case}}",
      "value": "string",
      "proposal_type": "project_field | document_field | derived_field | review_required | fixed_text",
      "role": "string|null",
      "scope": "string|null",
      "confidence": 0.0,
      "occurrences": [{"block_id": "string", "location": "string", "start": 0, "end": 0}],
      "evidence": ["string"],
      "reason": "string",
      "apply_strategy": "all_occurrences | selected_occurrences | review_required"
    }
  ]
}"""


def compact_document_map(document_map: DocumentMap, max_blocks: int = 180, max_occurrences_per_type: int = 80) -> dict:
    occurrence_block_ids = {
        occurrence.block_id
        for occurrences in document_map.occurrences_index.values()
        for occurrence in occurrences[:max_occurrences_per_type]
    }
    selected_blocks = []
    for block in document_map.blocks:
        if len(selected_blocks) >= max_blocks and block.block_id not in occurrence_block_ids:
            continue
        text = block.raw_text or ""
        if not text.strip() and block.block_id not in occurrence_block_ids:
            continue
        selected_blocks.append(
            {
                "block_id": block.block_id,
                "kind": block.kind,
                "location": block.location,
                "text": trim_text(text),
                "normalized_text": trim_text(block.normalized_text),
                "char_count": block.char_count,
                "structural_hints": block.structural_hints,
                "runs": [
                    {
                        "run_id": run.run_id,
                        "start": run.start,
                        "end": run.end,
                        "text": trim_text(run.text, 120),
                        "style": asdict(run.style),
                    }
                    for run in block.runs[:20]
                    if run.text
                ],
            }
        )
        if len(selected_blocks) >= max_blocks and occurrence_block_ids.issubset({item["block_id"] for item in selected_blocks}):
            break

    occurrences_index = {}
    for occurrence_type, occurrences in document_map.occurrences_index.items():
        occurrences_index[occurrence_type] = [
            {
                "occurrence_id": occurrence.occurrence_id,
                "text": occurrence.text,
                "block_id": occurrence.block_id,
                "location": occurrence.location,
                "start": occurrence.start,
                "end": occurrence.end,
                "before": trim_text(occurrence.before, 180),
                "after": trim_text(occurrence.after, 180),
            }
            for occurrence in occurrences[:max_occurrences_per_type]
        ]

    return {
        "document_id": document_map.document_id,
        "source_filename": document_map.source_filename,
        "quality": asdict(document_map.quality),
        "blocks": selected_blocks,
        "occurrences_index": occurrences_index,
    }


def trim_text(value: str, max_chars: int = 500) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 1].rstrip() + "…"


def compact_document_map_json(document_map: DocumentMap) -> str:
    return json.dumps(compact_document_map(document_map), ensure_ascii=False, indent=2)
