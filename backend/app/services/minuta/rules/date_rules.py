from __future__ import annotations

from datetime import date, datetime

from .common_rules import extract_digits, normalize_key, normalize_value
from .money_rules import number_to_words

MONTHS = {
    1: "enero",
    2: "febrero",
    3: "marzo",
    4: "abril",
    5: "mayo",
    6: "junio",
    7: "julio",
    8: "agosto",
    9: "septiembre",
    10: "octubre",
    11: "noviembre",
    12: "diciembre",
}


def is_date_field(field: dict) -> bool:
    haystack = " ".join([normalize_key(field.get("key") or ""), normalize_key(field.get("label") or "")])
    return any(token in haystack for token in ("fecha", "dia_elaboracion", "mes_elaboracion", "ano_elaboracion", "otorgamiento"))


def parse_date_value(value: object) -> date | None:
    raw = normalize_value(value)
    if not raw:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            pass
    digits = extract_digits(raw)
    if len(digits) == 8:
        for fmt in ("%d%m%Y", "%Y%m%d"):
            try:
                return datetime.strptime(digits, fmt).date()
            except ValueError:
                pass
    return None


def notarial_date_text(value: object) -> str:
    parsed = parse_date_value(value)
    if not parsed:
        return normalize_value(value)
    day_words = number_to_words(parsed.day).lower()
    year_words = number_to_words(parsed.year).lower()
    return f"{day_words} ({parsed.day}) días del mes de {MONTHS[parsed.month]} del año {year_words} ({parsed.year})"


def contractual_date_text(value: object) -> str:
    parsed = parse_date_value(value)
    if not parsed:
        return normalize_value(value)
    day_words = number_to_words(parsed.day).lower()
    year_words = number_to_words(parsed.year).lower()
    return f"{day_words} ({parsed.day}) de {MONTHS[parsed.month]} de {year_words} ({parsed.year})"


def notarial_day_text(value: object) -> str:
    digits = extract_digits(value)
    if not digits:
        return normalize_value(value)
    day = int(digits)
    if day < 1 or day > 31:
        return normalize_value(value)
    return f"{number_to_words(day).lower()} ({day}) días"


def normalize_month_text(value: object) -> str:
    raw = normalize_value(value)
    digits = extract_digits(raw)
    if digits:
        month = int(digits)
        if month in MONTHS:
            return MONTHS[month]
    normalized = normalize_key(raw)
    for month_name in MONTHS.values():
        if normalize_key(month_name) == normalized:
            return month_name
    return raw.lower()


def is_contractual_date_key(key: str) -> bool:
    normalized = normalize_key(key)
    return any(token in normalized for token in ("promesa", "contrato", "documento_privado", "celebracion"))
