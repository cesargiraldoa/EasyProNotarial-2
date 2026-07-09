from __future__ import annotations

import re
from collections.abc import Iterable

from app.services.minuta.reverse_template_builder.models import (
    CandidateContext,
    CandidateOccurrence,
    TextBlock,
)
from app.services.minuta.reverse_template_builder.notarial_context_classifier import (
    normalize_context,
    role_from_context,
    section_from_type,
    suggested_key_for,
)


MATRICULA_RE = re.compile(r"\b\d{3}-\d{5,10}\b")
MONEY_RE = re.compile(r"\$\s*\d{1,3}(?:\.\d{3})+(?:,\d{2})?\b")
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b", re.IGNORECASE)
MOBILE_RE = re.compile(r"(?<!\d)(?:\+?57[\s.\-]?)?3\d{2}[\s.\-]?\d{3}[\s.\-]?\d{4}(?!\d)")
DOCUMENT_RE = re.compile(r"\b\d{1,3}(?:\.\d{3}){2,3}(?:-\d)?\b")
UNIT_RE = re.compile(r"\b(?:APARTAMENTO|APTO\.?|UNIDAD)\s+(?:NO\.?\s*)?([A-Z0-9\-]{1,10})\b", re.IGNORECASE)
UPPERCASE_NAME_RE = re.compile(
    r"\b[A-ZÁÉÍÓÚÜÑ]{3,}(?:\s+(?:DE|DEL|LA|LAS|LOS|Y|[A-ZÁÉÍÓÚÜÑ]{3,})){1,5}\b"
)

NON_NAME_TOKENS = {
    "COMPRADOR",
    "COMPRADORA",
    "COMPRADORES",
    "VENDEDOR",
    "VENDEDORA",
    "VENDEDORES",
    "OTORGANTE",
    "OTORGANTES",
    "HIPOTECANTE",
    "HIPOTECANTES",
    "APODERADO",
    "APODERADA",
    "APODERADOS",
    "IDENTIFICADO",
    "IDENTIFICADA",
    "IDENTIFICADOS",
    "CON",
    "CEDULA",
    "NIT",
    "NUMERO",
    "MAYOR",
    "EDAD",
    "DOMICILIADO",
    "DOMICILIADA",
}


def _collapse_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _context_for(block: TextBlock, start: int, end: int, radius: int = 90) -> CandidateContext:
    before = _collapse_spaces(block.text[max(0, start - radius):start])
    after = _collapse_spaces(block.text[end:end + radius])
    return CandidateContext(location=block.location, before=before, after=after)


def _window(block: TextBlock, start: int, end: int, radius: int = 90) -> str:
    return block.text[max(0, start - radius):min(len(block.text), end + radius)]


def _base_confidence(candidate_type: str) -> float:
    return {
        "matricula_inmobiliaria": 0.95,
        "money": 0.9,
        "email": 0.95,
        "mobile": 0.85,
        "document_number": 0.85,
        "property_unit": 0.75,
        "uppercase_name": 0.7,
    }.get(candidate_type, 0.5)


def _make_occurrence(candidate_type: str, text: str, block: TextBlock, start: int, end: int) -> CandidateOccurrence:
    context_text = _window(block, start, end)
    suggested_key, label = suggested_key_for(candidate_type, text, context_text)
    return CandidateOccurrence(
        text=text.strip(),
        suggested_key=suggested_key,
        label=label,
        section=section_from_type(candidate_type, context_text),
        type=candidate_type,
        confidence=_base_confidence(candidate_type),
        context=_context_for(block, start, end),
    )


def _overlaps_money(text: str, start: int, end: int) -> bool:
    for match in MONEY_RE.finditer(text):
        if start >= match.start() and end <= match.end():
            return True
    return False


def _clean_uppercase_name(raw: str) -> str:
    tokens = raw.split()
    while tokens and normalize_context(tokens[0]) in NON_NAME_TOKENS:
        tokens.pop(0)
    while tokens and normalize_context(tokens[-1]) in NON_NAME_TOKENS:
        tokens.pop()
    return " ".join(tokens).strip(" ,.;:")


def _looks_like_name(text: str) -> bool:
    tokens = text.split()
    if len(tokens) < 2 or len(tokens) > 6:
        return False
    useful = [token for token in tokens if normalize_context(token) not in {"DE", "DEL", "LA", "LAS", "LOS", "Y"}]
    if len(useful) < 2:
        return False
    return not all(normalize_context(token) in NON_NAME_TOKENS for token in useful)


def detect_candidates(blocks: Iterable[TextBlock]) -> list[CandidateOccurrence]:
    candidates: list[CandidateOccurrence] = []

    for block in blocks:
        text = block.text or ""

        for match in MATRICULA_RE.finditer(text):
            candidates.append(_make_occurrence("matricula_inmobiliaria", match.group(0), block, match.start(), match.end()))

        for match in MONEY_RE.finditer(text):
            candidates.append(_make_occurrence("money", match.group(0), block, match.start(), match.end()))

        for match in EMAIL_RE.finditer(text):
            candidates.append(_make_occurrence("email", match.group(0), block, match.start(), match.end()))

        for match in MOBILE_RE.finditer(text):
            candidates.append(_make_occurrence("mobile", match.group(0), block, match.start(), match.end()))

        for match in DOCUMENT_RE.finditer(text):
            if _overlaps_money(text, match.start(), match.end()):
                continue
            candidates.append(_make_occurrence("document_number", match.group(0), block, match.start(), match.end()))

        for match in UNIT_RE.finditer(text):
            unit = match.group(1).strip(" .,:;")
            if not any(char.isdigit() for char in unit):
                continue
            candidates.append(_make_occurrence("property_unit", unit, block, match.start(1), match.end(1)))

        for match in UPPERCASE_NAME_RE.finditer(text):
            context = _window(block, match.start(), match.end())
            if role_from_context(context) is None:
                continue
            cleaned = _clean_uppercase_name(match.group(0))
            if not _looks_like_name(cleaned):
                continue
            candidates.append(_make_occurrence("uppercase_name", cleaned, block, match.start(), match.end()))

    return candidates
