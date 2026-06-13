from __future__ import annotations

from dataclasses import dataclass

from .common_rules import normalize_key, normalize_value
from .gender_rules import normalize_gender


@dataclass(frozen=True)
class PersonGrammar:
    gender: str | None
    gender_word: str
    nationality: str
    domiciled: str
    identified: str


def grammar_for_gender(raw_gender: object, raw_nationality: object = "") -> PersonGrammar:
    gender = normalize_gender(raw_gender)
    if gender == "F":
        return PersonGrammar("F", "mujer", "colombiana", "domiciliada", "identificada")
    if gender == "M":
        return PersonGrammar("M", "varón", "colombiano", "domiciliado", "identificado")
    nationality = normalize_value(raw_nationality).lower()
    return PersonGrammar(None, normalize_value(raw_gender).lower(), nationality, "domiciliado(a)", "identificado(a)")


def normalize_document_type(value: object) -> str:
    normalized = normalize_key(value)
    if normalized in {"cc", "c_c", "cedula", "cedula_ciudadania", "cedula_de_ciudadania"}:
        return "cédula de ciudadanía número"
    return normalize_value(value)


def normalize_transit_phrase(value: object) -> str:
    raw = normalize_value(value)
    normalized = normalize_key(raw)
    if not raw or normalized in {"no", "no_esta_de_transito", "no_esta_de_transito_por_este_municipio"}:
        return ""
    if normalized in {"si", "si_esta_de_transito", "de_transito", "transito"}:
        return "de tránsito por este municipio"
    return raw.replace("transito", "tránsito").replace("Transito", "Tránsito")


def collective_label(role: str, genders: list[str | None]) -> str:
    feminine = genders and all(gender == "F" for gender in genders)
    singular = len(genders) == 1
    if role == "comprador":
        if singular:
            return "la compradora" if feminine else "el comprador"
        return "las compradoras" if feminine else "los compradores"
    if role == "adquirente":
        if singular:
            return "la adquirente" if feminine else "el adquirente"
        return "las adquirentes" if feminine else "los adquirentes"
    if role == "hipotecante":
        if singular:
            return "la hipotecante" if feminine else "el hipotecante"
        return "las hipotecantes" if feminine else "los hipotecantes"
    if role == "deudor":
        if singular:
            return "la deudora" if feminine else "el deudor"
        return "las deudoras" if feminine else "los deudores"
    return role


def collective_adjective(kind: str, genders: list[str | None]) -> str:
    feminine = genders and all(gender == "F" for gender in genders)
    plural = len(genders) > 1
    if kind == "identificado":
        if plural:
            return "identificadas" if feminine else "identificados"
        return "identificada" if feminine else "identificado"
    if kind == "domiciliado":
        if plural:
            return "domiciliadas" if feminine else "domiciliados"
        return "domiciliada" if feminine else "domiciliado"
    if kind == "colombiano":
        if plural:
            return "colombianas" if feminine else "colombianos"
        return "colombiana" if feminine else "colombiano"
    return kind
