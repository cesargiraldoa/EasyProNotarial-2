from __future__ import annotations

import re


_PHRASE_CLEANUPS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bn[uú]mero\s+n[uú]mero\b", re.IGNORECASE), "número"),
    (re.compile(r"\bd[ií]as\s+d[ií]as\b", re.IGNORECASE), "días"),
    (re.compile(r"\bde\s+de\s+pesos\b", re.IGNORECASE), "de pesos"),
    (re.compile(r"\bcantidad\s+de\s+de\s+pesos\b", re.IGNORECASE), "cantidad de pesos"),
    (re.compile(r"\bP\.?\s*H\.?\s+P\.?\s*H\.?\b", re.IGNORECASE), "P.H."),
    (re.compile(r"\b(var[oó]n|mujer)\s*\((fideicomitente|fideicomisario|comprador|vendedor)\)", re.IGNORECASE), r"\1"),
    (re.compile(r"\s+([,;:])"), r"\1"),
    (re.compile(r"[ ]{2,}"), " "),
)


def normalize_notarial_phrase(text: str) -> str:
    normalized = text
    for pattern, replacement in _PHRASE_CLEANUPS:
        normalized = pattern.sub(replacement, normalized)
    return normalized


def has_duplicate_notarial_phrase(text: str) -> bool:
    return any(pattern.search(text or "") for pattern, _replacement in _PHRASE_CLEANUPS[:6])
