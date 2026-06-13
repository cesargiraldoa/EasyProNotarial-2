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
