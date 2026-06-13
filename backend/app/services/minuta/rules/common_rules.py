from __future__ import annotations

import re
import unicodedata


def normalize_key(value: object) -> str:
    normalized = unicodedata.normalize("NFD", str(value or ""))
    normalized = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    return re.sub(r"[^a-zA-Z0-9]+", "_", normalized.lower()).strip("_")


def normalize_value(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def extract_digits(value: object) -> str:
    return re.sub(r"\D+", "", normalize_value(value))


def truthy_notarial_value(value: object) -> bool:
    return normalize_key(value) in {"si", "s", "true", "1", "aplica", "afirmativo"}


def falsy_notarial_value(value: object) -> bool:
    return normalize_key(value) in {"no", "n", "false", "0", "no_aplica", "ninguno", "ninguna"}
