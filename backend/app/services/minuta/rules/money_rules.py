from __future__ import annotations

import re

from .common_rules import extract_digits, normalize_key, normalize_value

MONEY_FIELD_KEYWORDS = (
    "valor",
    "precio",
    "cuota",
    "cuantia",
    "avaluo",
    "retencion",
    "derechos",
    "iva",
    "aporte",
    "fondo",
    "impuesto",
    "hipoteca",
    "notariado",
    "superintendencia",
    "fideicomiso",
)

MONEY_FIELD_EXCLUDED_KEYWORDS = (
    "documento",
    "cedula",
    "telefono",
    "celular",
    "matricula",
    "escritura",
    "consecutivo",
    "anio",
    "ano",
    "year",
    "apartamento",
    "piso",
)


def _format_integer_digits(digits: str) -> str:
    normalized = digits.lstrip("0") or "0"
    return f"{int(normalized):,}".replace(",", ".")


def _parse_money_parts(raw: str) -> tuple[bool, str, str | None] | None:
    text = raw.strip()
    has_symbol = text.startswith("$")
    normalized = re.sub(r"[\s$]", "", text)
    if not normalized or re.fullmatch(r"[\d.,]+", normalized) is None:
        return None

    separator_positions = [
        (idx, char)
        for idx, char in enumerate(normalized)
        if char in ".,"
    ]
    decimal_index: int | None = None
    if separator_positions:
        last_index, _last_separator = separator_positions[-1]
        trailing = normalized[last_index + 1 :]
        separator_count = len(separator_positions)
        same_separator_count = normalized.count(_last_separator)
        if 1 <= len(trailing) <= 2:
            decimal_index = last_index
        elif separator_count == 1 and len(trailing) != 3:
            decimal_index = last_index
        elif separator_count > 1 and same_separator_count == 1 and 1 <= len(trailing) <= 2:
            decimal_index = last_index

    if decimal_index is None:
        integer_digits = extract_digits(normalized)
        decimal_digits = None
    else:
        integer_digits = extract_digits(normalized[:decimal_index])
        decimal_digits = extract_digits(normalized[decimal_index + 1 :])

    if not integer_digits:
        return None
    if decimal_digits == "":
        decimal_digits = None
    return has_symbol, integer_digits, decimal_digits


def extract_money_integer_digits(value: object) -> str:
    raw = normalize_value(value)
    if not raw:
        return ""
    parsed = _parse_money_parts(raw)
    if parsed is None:
        return extract_digits(raw)
    _has_symbol, integer_digits, _decimal_digits = parsed
    return integer_digits


def split_money_integer_and_cents(value: object) -> tuple[str, int | None]:
    raw = normalize_value(value)
    if not raw:
        return "", None
    parsed = _parse_money_parts(raw)
    if parsed is None:
        digits = extract_digits(raw)
        return digits, None

    _has_symbol, integer_digits, decimal_digits = parsed
    cents: int | None = None
    if decimal_digits is not None:
        cents_text = decimal_digits[:2].ljust(2, "0")
        cents = int(cents_text)
    return integer_digits, cents


def is_money_field(field: dict) -> bool:
    haystack = " ".join(
        [
            normalize_key(field.get("key") or ""),
            normalize_key(field.get("label") or ""),
            normalize_key(field.get("section") or ""),
        ]
    )
    if not haystack:
        return False
    if any(keyword in haystack for keyword in MONEY_FIELD_EXCLUDED_KEYWORDS):
        return False
    return any(keyword in haystack for keyword in MONEY_FIELD_KEYWORDS)


def format_money_value(value: object) -> str:
    raw = normalize_value(value)
    if not raw:
        return ""
    parsed = _parse_money_parts(raw)
    if parsed is None:
        return raw
    has_symbol, integer_digits, decimal_digits = parsed
    formatted = _format_integer_digits(integer_digits)
    if decimal_digits is not None:
        formatted = f"{formatted},{decimal_digits}"
    return f"${formatted}" if has_symbol else formatted


def format_cop_value(value: object, include_symbol: bool = False) -> str:
    formatted = format_money_value(value)
    if not formatted:
        return ""
    return f"${formatted}" if include_symbol and not formatted.startswith("$") else formatted


def normalize_cop_replacements(replacements: dict[str, object]) -> dict[str, str]:
    result: dict[str, str] = {}
    for marker, value in (replacements or {}).items():
        key = normalize_key(marker)
        if any(excluded in key for excluded in MONEY_FIELD_EXCLUDED_KEYWORDS):
            result[str(marker)] = normalize_value(value)
            continue
        if any(keyword in key for keyword in MONEY_FIELD_KEYWORDS):
            result[str(marker)] = format_cop_value(value, include_symbol=normalize_value(value).startswith("$"))
        else:
            result[str(marker)] = normalize_value(value)
    return result


UNIDADES = [
    "",
    "UNO",
    "DOS",
    "TRES",
    "CUATRO",
    "CINCO",
    "SEIS",
    "SIETE",
    "OCHO",
    "NUEVE",
    "DIEZ",
    "ONCE",
    "DOCE",
    "TRECE",
    "CATORCE",
    "QUINCE",
    "DIECISÉIS",
    "DIECISIETE",
    "DIECIOCHO",
    "DIECINUEVE",
]
DECENAS = ["", "", "VEINTE", "TREINTA", "CUARENTA", "CINCUENTA", "SESENTA", "SETENTA", "OCHENTA", "NOVENTA"]
CENTENAS = [
    "",
    "CIENTO",
    "DOSCIENTOS",
    "TRESCIENTOS",
    "CUATROCIENTOS",
    "QUINIENTOS",
    "SEISCIENTOS",
    "SETECIENTOS",
    "OCHOCIENTOS",
    "NOVECIENTOS",
]


def hundreds_to_words(number: int) -> str:
    if number == 0:
        return ""
    if number == 100:
        return "CIEN"
    hundreds = number // 100
    remainder = number % 100
    parts: list[str] = []
    if hundreds > 0:
        parts.append(CENTENAS[hundreds])
    if remainder > 0:
        if remainder < 20:
            parts.append(UNIDADES[remainder])
        elif remainder < 30:
            unit = remainder % 10
            if unit == 0:
                parts.append("VEINTE")
            elif unit == 1:
                parts.append("VEINTE Y UN")
            elif unit == 2:
                parts.append("VEINTIDÓS")
            elif unit == 3:
                parts.append("VEINTITRÉS")
            elif unit == 6:
                parts.append("VEINTISÉIS")
            else:
                parts.append(f"VEINTI{UNIDADES[unit].lower()}".upper())
        else:
            tens = remainder // 10
            unit = remainder % 10
            parts.append(DECENAS[tens] if unit == 0 else f"{DECENAS[tens]} Y {UNIDADES[unit]}")
    return " ".join(part for part in parts if part)


def number_to_words(number: int, suffix: str = "") -> str:
    if number <= 0:
        return f"CERO {suffix}".strip() if number == 0 else ""
    parts: list[str] = []
    billions = number // 1_000_000_000
    millions = (number % 1_000_000_000) // 1_000_000
    thousands = (number % 1_000_000) // 1_000
    remainder = number % 1_000
    if billions:
        text = hundreds_to_words(billions)
        parts.append("MIL MILLONES" if billions == 1 else f"{text} MIL MILLONES")
    if millions:
        text = hundreds_to_words(millions)
        parts.append("UN MILLÓN" if millions == 1 else f"{text} MILLONES")
    if thousands:
        text = hundreds_to_words(thousands)
        parts.append("MIL" if thousands == 1 else f"{text} MIL")
    if remainder:
        parts.append(hundreds_to_words(remainder))
    words = " ".join(part for part in parts if part)
    if suffix and number >= 1_000_000 and number % 1_000_000 == 0 and normalize_key(suffix).startswith("pesos"):
        return f"{words} DE {suffix}".strip()
    return f"{words} {suffix}".strip()


def money_to_words(value: object, suffix: str = "PESOS") -> str:
    integer_digits, cents = split_money_integer_and_cents(value)
    if not integer_digits:
        return ""
    words = number_to_words(int(integer_digits), suffix)
    if cents is None or cents <= 0:
        return words
    return f"{words} CON {number_to_words(cents)} CENTAVOS"
