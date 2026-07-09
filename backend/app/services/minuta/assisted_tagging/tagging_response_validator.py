from __future__ import annotations

import re
import unicodedata
from collections import Counter

from app.services.minuta.assisted_tagging.models import DocxStructure, TaggingFieldProposal, TaggingValidationResult


def normalize_code(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_value = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    code = re.sub(r"[^a-zA-Z0-9]+", "_", ascii_value.lower()).strip("_")
    return code[:80] or "campo"


SECTION_PREFIXES = {
    "personas": "campo_persona",
    "inmueble": "campo_inmueble",
    "valores": "campo_valor",
    "fechas": "campo_fecha",
    "notaria": "campo_notaria",
    "acto": "campo_acto",
    "general": "campo_humano",
}


def _code_exposes_value(code: str, text: str) -> bool:
    if re.search(r"\d{5,}", code):
        return True
    code_tokens = {token for token in code.split("_") if len(token) >= 3}
    value_tokens = {token for token in normalize_code(text).split("_") if len(token) >= 3}
    if not code_tokens or not value_tokens:
        return False
    overlap = code_tokens & value_tokens
    return len(overlap) >= 2 or (len(overlap) == 1 and len(next(iter(overlap))) >= 8)


def controlled_code_for_section(section: str, counters: Counter[str]) -> str:
    prefix = SECTION_PREFIXES.get(normalize_code(section or "general"), "campo_humano")
    counters[prefix] += 1
    return f"{prefix}_{counters[prefix]}"


class TaggingResponseValidator:
    def validate(self, payload: dict, structure: DocxStructure) -> TaggingValidationResult:
        warnings: list[str] = []
        fields: list[TaggingFieldProposal] = []
        full_text = "\n".join(block.text for block in structure.blocks)
        raw_fields = payload.get("fields") if isinstance(payload, dict) else None
        if not isinstance(raw_fields, list):
            return TaggingValidationResult(fields=[], warnings=["El LLM no devolvio una lista de campos valida."])

        used_codes: set[str] = set()
        used_texts: set[str] = set()
        controlled_counters: Counter[str] = Counter()
        for item in raw_fields:
            if not isinstance(item, dict):
                continue
            text = " ".join(str(item.get("text") or "").split())
            if len(text) < 2:
                continue
            if text not in full_text:
                warnings.append(f"Se descarto una propuesta porque el texto no existe en el DOCX: {text[:60]}")
                continue
            if text.upper() in used_texts:
                continue
            used_texts.add(text.upper())

            section = str(item.get("section") or "general").strip() or "general"
            base_code = normalize_code(str(item.get("field_code") or item.get("label") or ""))
            if not base_code or _code_exposes_value(base_code, text):
                base_code = controlled_code_for_section(section, controlled_counters)
            code = base_code
            suffix = 2
            while code in used_codes:
                code = f"{base_code}_{suffix}"
                suffix += 1
            used_codes.add(code)

            confidence_raw = item.get("confidence", 0.5)
            try:
                confidence = max(0.0, min(1.0, float(confidence_raw)))
            except (TypeError, ValueError):
                confidence = 0.5

            fields.append(
                TaggingFieldProposal(
                    field_code=code,
                    label=str(item.get("label") or code.replace("_", " ").title()).strip(),
                    text=text,
                    section=section,
                    confidence=confidence,
                    block_id=str(item.get("block_id") or "") or None,
                    reason=str(item.get("reason") or "") or None,
                    source=str(item.get("source") or "llm"),
                    occurrences=full_text.count(text),
                )
            )

        if not fields:
            warnings.append("No se encontraron variables confiables para marcar en rojo.")
        return TaggingValidationResult(fields=fields, warnings=warnings)
