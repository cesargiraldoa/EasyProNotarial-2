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
    digits = extract_digits(raw)
    if not digits:
        return raw
    normalized_raw = re.sub(r"[\s$]", "", raw)
    if re.fullmatch(r"[\d.,]+", normalized_raw) is None and not raw.isdigit():
        return raw
    return f"{int(digits):,}".replace(",", ".")


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
