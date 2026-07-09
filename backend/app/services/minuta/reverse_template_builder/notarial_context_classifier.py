from __future__ import annotations

import re
import unicodedata


ROLE_KEYWORDS = {
    "comprador": ("COMPRADOR", "COMPRADORA", "COMPRADORES"),
    "vendedor": ("VENDEDOR", "VENDEDORA", "VENDEDORES"),
    "otorgante": ("OTORGANTE", "OTORGANTES"),
    "hipotecante": ("HIPOTECANTE", "HIPOTECANTES"),
    "apoderado": ("APODERADO", "APODERADA", "APODERADOS"),
}


def strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def normalize_context(text: str) -> str:
    text = strip_accents(text or "").upper()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def snake_case(text: str) -> str:
    normalized = strip_accents(text).lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    return normalized.strip("_") or "campo"


def human_label(text: str) -> str:
    words = [word for word in re.split(r"[_\s]+", text.strip()) if word]
    if not words:
        return "Campo"
    return " ".join([words[0].capitalize()] + [word.lower() for word in words[1:]])


def role_from_context(context: str) -> str | None:
    normalized = normalize_context(context)
    for role, keywords in ROLE_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            return role
    return None


def section_from_type(candidate_type: str, context: str) -> str:
    normalized = normalize_context(context)
    if candidate_type in {"matricula_inmobiliaria", "property_unit"}:
        return "Inmueble"
    if candidate_type == "money":
        return "Valores"
    if candidate_type in {"email", "mobile", "document_number", "uppercase_name"}:
        role = role_from_context(normalized)
        if role == "comprador":
            return "Compradores"
        if role == "vendedor":
            return "Vendedores"
        if role == "apoderado":
            return "Apoderados"
        if role in {"otorgante", "hipotecante"}:
            return "Comparecientes"
        return "Personas"
    return "Otros"


def suggested_key_for(candidate_type: str, text: str, context: str) -> tuple[str, str]:
    normalized = normalize_context(context)
    role = role_from_context(normalized)

    if candidate_type == "matricula_inmobiliaria":
        return "matricula_inmobiliaria", "Matricula inmobiliaria"
    if candidate_type == "money":
        if "CUOTA" in normalized:
            return "valor_cuota", "Valor cuota"
        if "HIPOTECA" in normalized:
            return "valor_hipoteca", "Valor hipoteca"
        if "VENTA" in normalized or "PRECIO" in normalized:
            return "valor_venta", "Valor venta"
        return "valor_monetario", "Valor monetario"
    if candidate_type == "email":
        key = f"email_{role}" if role else "email"
        return key, human_label(key)
    if candidate_type == "mobile":
        key = f"celular_{role}" if role else "celular"
        return key, human_label(key)
    if candidate_type == "document_number":
        if "NIT" in normalized:
            key = f"nit_{role}" if role else "nit"
        else:
            key = f"numero_documento_{role}" if role else "numero_documento"
        return key, human_label(key)
    if candidate_type == "property_unit":
        if "APTO" in normalized or "APARTAMENTO" in normalized:
            return "numero_apartamento", "Numero apartamento"
        return "numero_unidad", "Numero unidad"
    if candidate_type == "uppercase_name":
        key = f"nombre_{role}" if role else "nombre"
        return key, human_label(key)

    key = snake_case(text)
    return key, human_label(key)
