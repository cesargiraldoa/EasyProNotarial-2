from __future__ import annotations

from collections.abc import Iterable

from app.services.minuta.engine.models import RenderIssue, RenderSeverity

from .common_rules import normalize_key, normalize_value

ROLE_BASES = (
    "comprador",
    "comprador_1",
    "comprador_2",
    "vendedor",
    "vendedor_1",
    "vendedor_2",
    "fideicomitente",
    "fideicomisario",
    "poderdante",
    "apoderado",
    "inscrito",
)

GENDER_VALUE_MAP = {
    "hombre": "M",
    "masculino": "M",
    "m": "M",
    "varon": "M",
    "mujer": "F",
    "femenino": "F",
    "f": "F",
    "persona_juridica": "J",
    "juridica": "J",
    "j": "J",
}

EXPECTATIONS = {
    "M": {
        "nationality": {"colombiano"},
        "state_civil": {"casado", "soltero", "divorciado", "viudo"},
        "role_words": {"deudor", "comprador", "vendedor", "apoderado", "inscrito", "fideicomisario"},
    },
    "F": {
        "nationality": {"colombiana"},
        "state_civil": {"casada", "soltera", "divorciada", "viuda"},
        "role_words": {"deudora", "compradora", "vendedora", "apoderada", "inscrita", "fideicomisaria"},
    },
}


def normalize_gender(value: object) -> str | None:
    return GENDER_VALUE_MAP.get(normalize_key(value))


def first_non_empty(values: dict[str, str], keys: Iterable[str]) -> tuple[str | None, str]:
    for key in keys:
        value = normalize_value(values.get(key, ""))
        if value:
            return key, value
    return None, ""


def role_gender(values: dict[str, str], role: str) -> str | None:
    candidates = [
        f"{role}_es_hombre_o_mujer",
        f"{role}_es_hombre_0_mujer",
        f"genero_{role}",
        f"{role}_genero",
        f"{role}_sexo",
    ]
    if role == "comprador_1":
        candidates.extend(["comprador_es_hombre_o_mujer", "genero_comprador", "comprador_genero"])
    key, value = first_non_empty(values, candidates)
    return normalize_gender(value) if key else None


def matches_expected_word(value: str, expected_words: set[str]) -> bool:
    normalized = normalize_key(value)
    return any(normalized == word or normalized.startswith(f"{word}_") for word in expected_words)


def validate_gender_concordance(values: dict[str, str]) -> list[RenderIssue]:
    issues: list[RenderIssue] = []
    for role in ROLE_BASES:
        gender = role_gender(values, role)
        if gender not in {"M", "F"}:
            continue
        expected = EXPECTATIONS[gender]
        nationality_keys = [f"nacionalidad_{role}"]
        state_keys = [f"estado_civil_{role}"]
        if role == "comprador_1":
            nationality_keys.append("nacionalidad_comprador")
            state_keys.append("estado_civil_comprador")

        nationality_key, nationality = first_non_empty(values, nationality_keys)
        if nationality_key and not matches_expected_word(nationality, expected["nationality"]):
            issues.append(
                RenderIssue(
                    code="gender_nationality_mismatch",
                    message=f"Nacionalidad no concuerda con género para {role}.",
                    severity=RenderSeverity.WARNING,
                    field_key=nationality_key,
                    details={"role": role, "value": nationality, "gender": gender},
                )
            )

        state_key, state = first_non_empty(values, state_keys)
        if state_key and not matches_expected_word(state, expected["state_civil"]):
            issues.append(
                RenderIssue(
                    code="gender_state_civil_mismatch",
                    message=f"Estado civil no concuerda con género para {role}.",
                    severity=RenderSeverity.WARNING,
                    field_key=state_key,
                    details={"role": role, "value": state, "gender": gender},
                )
            )
    return issues
