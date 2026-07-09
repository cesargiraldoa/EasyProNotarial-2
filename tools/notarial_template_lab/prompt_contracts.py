from __future__ import annotations

import json
import math
import re
from dataclasses import asdict
from pathlib import Path

from tools.notarial_template_lab.models import BlockMap, DocumentMap


DOCUMENT_PROFILER_SYSTEM_PROMPT = """Eres un agente documental notarial.
Trabajas exclusivamente sobre un indice estructural compacto derivado de un DocumentMap, no sobre el DOCX crudo.
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
Trabajas exclusivamente sobre un lote compacto de bloques relevantes y un perfil documental.
Devuelve SOLO JSON valido. No incluyas explicaciones.

Reglas:
- No inventes datos.
- Solo propone campos cuyo texto exista en el lote compacto recibido.
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


DEFAULT_MAX_BLOCKS = 120
DEFAULT_MAX_BLOCK_CHARS = 700
DEFAULT_MAX_OCCURRENCES_PER_TYPE = 60
DEFAULT_MAX_BLOCKS_PER_BATCH = 40
DEFAULT_SAFE_PAYLOAD_TOKENS = 28000

ACT_TERMS = (
    "COMPRAVENTA",
    "HIPOTECA",
    "CANCELACION",
    "PERMUTA",
    "DONACION",
    "FIDUCIA",
    "REGLAMENTO",
    "PROTOCOLIZACION",
)
PARTY_TERMS = (
    "COMPRADOR",
    "VENDEDOR",
    "OTORGANTE",
    "HIPOTECANTE",
    "ACREEDOR",
    "DEUDOR",
    "APODERADO",
    "PODERDANTE",
)
PROPERTY_TERMS = (
    "INMUEBLE",
    "APARTAMENTO",
    "APTO",
    "UNIDAD",
    "CASA",
    "MATRICULA",
    "PREDIAL",
    "DIRECCION",
    "COEFICIENTE",
)
MONEY_TERMS = (
    "VALOR",
    "PRECIO",
    "CUOTA INICIAL",
    "SALDO",
    "CREDITO",
    "HIPOTECARIO",
    "AVALUO",
)
PROTOCOL_TERMS = ("NOTARIA", "NOTARIO", "PROTOCOLO", "ESCRITURA")
SIGNAL_GROUPS = {
    "acts": ACT_TERMS,
    "parties": PARTY_TERMS,
    "property": PROPERTY_TERMS,
    "money": MONEY_TERMS,
    "protocol": PROTOCOL_TERMS,
}
TECHNICAL_OCCURRENCE_TYPES = {
    "real_estate_registration",
    "dotted_document",
    "nit",
    "money",
    "email",
    "phone",
    "long_property_code",
    "date",
    "uppercase_relevant_phrase",
}


class PayloadTooLargeError(ValueError):
    pass


def compact_document_map(
    document_map: DocumentMap,
    max_blocks: int = DEFAULT_MAX_BLOCKS,
    max_occurrences_per_type: int = DEFAULT_MAX_OCCURRENCES_PER_TYPE,
    max_block_chars: int = DEFAULT_MAX_BLOCK_CHARS,
    include_runs: bool = False,
) -> dict:
    occurrence_lookup = occurrences_by_block(document_map, max_occurrences_per_type)
    relevant_blocks = [
        block
        for block in document_map.blocks
        if is_relevant_block(block, occurrence_lookup.get(block.block_id, []))
    ]
    selected_source_blocks = relevant_blocks[: max(0, max_blocks)]
    selected_blocks = [
        compact_block(block, occurrence_lookup.get(block.block_id, []), max_block_chars, include_runs)
        for block in selected_source_blocks
    ]
    occurrences_index = compact_occurrences_index(document_map, max_occurrences_per_type)
    stats = reduction_stats(document_map, selected_source_blocks, selected_blocks, max_block_chars, include_runs)

    return {
        "document_id": document_map.document_id,
        "source_filename": document_map.source_filename,
        "quality": asdict(document_map.quality),
        "blocks": selected_blocks,
        "occurrences_index": occurrences_index,
        "reduction_stats": stats,
    }


def build_profile_payload(
    document_map: DocumentMap,
    max_blocks: int = DEFAULT_MAX_BLOCKS,
    max_block_chars: int = DEFAULT_MAX_BLOCK_CHARS,
    max_occurrences_per_type: int = DEFAULT_MAX_OCCURRENCES_PER_TYPE,
) -> dict:
    compact = compact_document_map(
        document_map,
        max_blocks=max_blocks,
        max_occurrences_per_type=max_occurrences_per_type,
        max_block_chars=max_block_chars,
        include_runs=False,
    )
    blocks = compact["blocks"]
    structural_index = {
        "sections": [section_hint(block) for block in blocks if is_section_candidate(block)][:40],
        "titles": [section_hint(block) for block in blocks if is_title_candidate(block)][:40],
        "relevant_blocks": [
            {
                "block_id": block["block_id"],
                "kind": block["kind"],
                "location": block["location"],
                "text": block["text"],
                "signals": block["signals"],
                "occurrences": block["occurrences"][:8],
            }
            for block in blocks
        ],
        "acts_hints": hints_for_signal(blocks, "acts"),
        "parties_hints": hints_for_signal(blocks, "parties"),
        "property_hints": hints_for_signal(blocks, "property"),
        "money_hints": hints_for_signal(blocks, "money"),
    }
    payload = {
        "document_id": compact["document_id"],
        "source_filename": compact["source_filename"],
        "quality": compact["quality"],
        "reduction_stats": compact["reduction_stats"],
        "structural_index": structural_index,
    }
    payload["reduction_stats"]["estimated_tokens"] = estimate_payload_tokens(payload)
    return payload


def build_field_proposal_batches(
    document_map: DocumentMap,
    max_blocks_per_batch: int = DEFAULT_MAX_BLOCKS_PER_BATCH,
    max_block_chars: int = DEFAULT_MAX_BLOCK_CHARS,
    max_occurrences_per_type: int = DEFAULT_MAX_OCCURRENCES_PER_TYPE,
) -> list[dict]:
    if max_blocks_per_batch < 1:
        raise ValueError("max_blocks_per_batch debe ser mayor que cero")
    compact = compact_document_map(
        document_map,
        max_blocks=len(document_map.blocks),
        max_occurrences_per_type=max_occurrences_per_type,
        max_block_chars=max_block_chars,
        include_runs=False,
    )
    blocks = compact["blocks"]
    total_batches = max(1, math.ceil(len(blocks) / max_blocks_per_batch))
    payloads = []
    for index in range(total_batches):
        start = index * max_blocks_per_batch
        batch_blocks = blocks[start:start + max_blocks_per_batch]
        payload = {
            "document_id": compact["document_id"],
            "source_filename": compact["source_filename"],
            "batch": {
                "index": index + 1,
                "total": total_batches,
                "max_blocks_per_batch": max_blocks_per_batch,
                "max_block_chars": max_block_chars,
            },
            "blocks": batch_blocks,
            "reduction_stats": {
                **compact["reduction_stats"],
                "batch_blocks": len(batch_blocks),
                "batch_index": index + 1,
                "batch_total": total_batches,
            },
        }
        payload["reduction_stats"]["estimated_tokens"] = estimate_payload_tokens(payload)
        payloads.append(payload)
    return payloads


def with_document_profile(batch_payload: dict, document_profile: dict) -> dict:
    payload = dict(batch_payload)
    payload["document_profile"] = document_profile
    payload["reduction_stats"] = dict(batch_payload.get("reduction_stats") or {})
    payload["reduction_stats"]["estimated_tokens"] = estimate_payload_tokens(payload)
    return payload


def assert_payload_within_limit(payload: dict, max_estimated_tokens: int, label: str) -> None:
    estimated_tokens = estimate_payload_tokens(payload)
    if estimated_tokens > max_estimated_tokens:
        raise PayloadTooLargeError(
            f"{label} payload too large, reduce batch size or block chars "
            f"({estimated_tokens} estimated tokens > {max_estimated_tokens})"
        )


def estimate_payload_tokens(payload: dict) -> int:
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return math.ceil(len(encoded) / 4)


def write_debug_payload(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def occurrences_by_block(document_map: DocumentMap, max_occurrences_per_type: int) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for occurrence_type, occurrences in document_map.occurrences_index.items():
        if occurrence_type not in TECHNICAL_OCCURRENCE_TYPES:
            continue
        for occurrence in occurrences[:max_occurrences_per_type]:
            grouped.setdefault(occurrence.block_id, []).append(
                {
                    "occurrence_id": occurrence.occurrence_id,
                    "occurrence_type": occurrence.occurrence_type,
                    "text": occurrence.text,
                    "block_id": occurrence.block_id,
                    "location": occurrence.location,
                    "start": occurrence.start,
                    "end": occurrence.end,
                    "before": trim_text(occurrence.before, 100),
                    "after": trim_text(occurrence.after, 100),
                }
            )
    return grouped


def compact_occurrences_index(document_map: DocumentMap, max_occurrences_per_type: int) -> dict:
    occurrences_index = {}
    for occurrence_type, occurrences in document_map.occurrences_index.items():
        if occurrence_type not in TECHNICAL_OCCURRENCE_TYPES:
            continue
        occurrences_index[occurrence_type] = [
            {
                "occurrence_id": occurrence.occurrence_id,
                "text": occurrence.text,
                "block_id": occurrence.block_id,
                "location": occurrence.location,
                "start": occurrence.start,
                "end": occurrence.end,
                "before": trim_text(occurrence.before, 100),
                "after": trim_text(occurrence.after, 100),
            }
            for occurrence in occurrences[:max_occurrences_per_type]
        ]
    return occurrences_index


def compact_block(block: BlockMap, occurrences: list[dict], max_block_chars: int, include_runs: bool) -> dict:
    signals = detect_signals(block.raw_text)
    item = {
        "block_id": block.block_id,
        "kind": block.kind,
        "location": block.location,
        "text": trim_text(block.raw_text, max_block_chars),
        "char_count": block.char_count,
        "structural_hints": block.structural_hints,
        "signals": signals,
        "occurrences": occurrences[:12],
    }
    if include_runs:
        item["runs"] = [
            {
                "run_id": run.run_id,
                "start": run.start,
                "end": run.end,
                "text": trim_text(run.text, 80),
            }
            for run in block.runs[:8]
            if run.text
        ]
    return item


def is_relevant_block(block: BlockMap, occurrences: list[dict]) -> bool:
    text = block.raw_text or ""
    if not text.strip():
        return False
    if occurrences:
        return True
    if detect_signals(text):
        return True
    return looks_like_heading(text, block.structural_hints)


def detect_signals(text: str) -> dict[str, list[str]]:
    normalized = normalize_upper(text)
    signals = {}
    for group, terms in SIGNAL_GROUPS.items():
        found = [term for term in terms if contains_term(normalized, term)]
        if found:
            signals[group] = found[:8]
    return signals


def contains_term(normalized_text: str, term: str) -> bool:
    pattern = r"(?<![A-Z0-9_])" + re.escape(term).replace(r"\ ", r"\s+") + r"(?![A-Z0-9_])"
    return re.search(pattern, normalized_text) is not None


def is_section_candidate(block: dict) -> bool:
    return bool(block.get("structural_hints", {}).get("is_heading") or looks_like_heading(block.get("text", ""), block.get("structural_hints", {})))


def is_title_candidate(block: dict) -> bool:
    text = block.get("text", "")
    if len(text) > 180:
        return False
    letters = [char for char in text if char.isalpha()]
    if not letters:
        return False
    return sum(1 for char in letters if char.isupper()) / len(letters) > 0.75


def looks_like_heading(text: str, hints: dict | None = None) -> bool:
    value = trim_text(text, 240)
    if not value or len(value) > 180:
        return False
    hints = hints or {}
    if hints.get("is_heading"):
        return True
    if re.match(r"^(CAPITULO|CLAUSULA|PARAGRAFO|SECCION|ARTICULO)\b", normalize_upper(value)):
        return True
    words = value.split()
    if 1 <= len(words) <= 12 and is_title_case_or_upper(value):
        return True
    return False


def is_title_case_or_upper(value: str) -> bool:
    letters = [char for char in value if char.isalpha()]
    if not letters:
        return False
    upper_ratio = sum(1 for char in letters if char.isupper()) / len(letters)
    return upper_ratio > 0.7


def section_hint(block: dict) -> dict:
    return {
        "title": block.get("text", ""),
        "block_id": block.get("block_id", ""),
        "location": block.get("location", ""),
        "signals": block.get("signals", {}),
    }


def hints_for_signal(blocks: list[dict], signal_group: str, limit: int = 30) -> list[dict]:
    hints = []
    for block in blocks:
        if signal_group not in (block.get("signals") or {}):
            continue
        hints.append(
            {
                "block_id": block["block_id"],
                "location": block["location"],
                "text": block["text"],
                "signals": block["signals"][signal_group],
                "occurrences": block.get("occurrences", [])[:6],
            }
        )
        if len(hints) >= limit:
            break
    return hints


def reduction_stats(
    document_map: DocumentMap,
    selected_source_blocks: list[BlockMap],
    selected_blocks: list[dict],
    max_block_chars: int,
    include_runs: bool,
) -> dict:
    original_chars = sum(block.char_count for block in document_map.blocks)
    selected_chars = sum(len(block.get("text", "")) for block in selected_blocks)
    original_occurrences = sum(len(items) for items in document_map.occurrences_index.values())
    selected_occurrences = sum(len(block.get("occurrences", [])) for block in selected_blocks)
    payload = {
        "original_blocks": len(document_map.blocks),
        "selected_blocks": len(selected_blocks),
        "omitted_blocks": max(0, len(document_map.blocks) - len(selected_blocks)),
        "original_chars": original_chars,
        "selected_chars": selected_chars,
        "original_runs": len(document_map.runs),
        "included_runs": sum(len(block.get("runs", [])) for block in selected_blocks) if include_runs else 0,
        "original_occurrences": original_occurrences,
        "selected_occurrences": selected_occurrences,
        "max_block_chars": max_block_chars,
        "include_runs": include_runs,
        "selected_block_ids": [block.block_id for block in selected_source_blocks],
    }
    payload["estimated_tokens"] = estimate_payload_tokens(payload)
    return payload


def trim_text(value: str, max_chars: int = 500) -> str:
    value = re.sub(r"\s+", " ", value or "").strip()
    if len(value) <= max_chars:
        return value
    if max_chars <= 3:
        return value[:max_chars]
    return value[: max_chars - 3].rstrip() + "..."


def normalize_upper(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").upper()


def compact_document_map_json(document_map: DocumentMap) -> str:
    return json.dumps(compact_document_map(document_map), ensure_ascii=False, indent=2)
