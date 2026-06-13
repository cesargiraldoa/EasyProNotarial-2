from __future__ import annotations

from app.services.minuta.engine.models import RenderIssue, RenderSeverity

from .common_rules import normalize_value

ACTOR_REQUIRED_FIELDS = {
    "comprador_2": ("nombre_comprador_2", "numero_documento_comprador_2"),
    "vendedor_2": ("nombre_vendedor_2", "numero_documento_vendedor_2"),
}


def actor_has_data(values: dict[str, str], role: str) -> bool:
    return any(normalize_value(values.get(key)) for key in ACTOR_REQUIRED_FIELDS.get(role, ()))


def validate_required_actors(required_roles: set[str], values: dict[str, str]) -> list[RenderIssue]:
    issues: list[RenderIssue] = []
    for role in sorted(required_roles):
        if role not in ACTOR_REQUIRED_FIELDS:
            continue
        if actor_has_data(values, role):
            continue
        issues.append(
            RenderIssue(
                code="template_requires_missing_actor",
                message=f"La plantilla exige {role}, pero los datos no lo incluyen.",
                severity=RenderSeverity.BLOCKER,
                field_key=role,
                details={"role": role},
            )
        )
    return issues


REQUIRED_FIELD_MESSAGES = {
    "origen_cuota_inicial": "El campo origen_cuota_inicial es requerido para completar la cláusula de forma de pago.",
    "valor_de_la_venta_en_numeros": "El valor de la venta es requerido para completar la cláusula cuarta.",
    "valor_apartamento_en_letras": "El valor de la venta en letras es requerido para completar la cláusula cuarta.",
    "en_numeros_cuota_inicial": "El valor numérico de la cuota inicial es requerido para completar la cláusula cuarta.",
    "en_letras_cuota_inicial": "El valor de la cuota inicial en letras es requerido para completar la cláusula cuarta.",
    "valor_del_acto_de_la_hipoteca": "El valor del acto de la hipoteca es requerido para completar el saldo con crédito hipotecario.",
    "valor_del_acto_de_la_hipoteca_en_letras": "El valor de la hipoteca en letras es requerido para completar el saldo con crédito hipotecario.",
    "nombre_comprador_1": "El nombre del comprador 1 es requerido.",
    "tipo_documento_comprador_1": "El tipo de documento del comprador 1 es requerido.",
    "numero_documento_comprador_1": "El número de documento del comprador 1 es requerido.",
    "comprador_es_hombre_o_mujer": "El género del comprador 1 es requerido para concordancia notarial.",
    "estado_civil_comprador": "El estado civil del comprador 1 es requerido.",
    "nombre_comprador_2": "El nombre del comprador 2 es requerido porque la plantilla exige dos compradores.",
    "tipo_documento_comprador_2": "El tipo de documento del comprador 2 es requerido porque la plantilla exige dos compradores.",
    "numero_documento_comprador_2": "El número de documento del comprador 2 es requerido porque la plantilla exige dos compradores.",
    "comprador_2_es_hombre_o_mujer": "El género del comprador 2 es requerido para concordancia notarial.",
    "estado_civil_comprador_2": "El estado civil del comprador 2 es requerido porque la plantilla exige dos compradores.",
}


def validate_required_fields(field_keys: set[str], values: dict[str, str], marker_by_key: dict[str, str]) -> list[RenderIssue]:
    issues: list[RenderIssue] = []
    for key, message in REQUIRED_FIELD_MESSAGES.items():
        if key not in field_keys:
            continue
        if normalize_value(values.get(key)):
            continue
        issues.append(
            RenderIssue(
                code="required_field_missing",
                message=message,
                severity=RenderSeverity.BLOCKER,
                field_key=key,
                placeholder=marker_by_key.get(key),
            )
        )
    return issues
