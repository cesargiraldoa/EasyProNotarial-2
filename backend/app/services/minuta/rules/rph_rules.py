from __future__ import annotations

from dataclasses import asdict, dataclass
import re

from app.services.minuta.rules.common_rules import falsy_notarial_value, normalize_value, truthy_notarial_value


@dataclass(frozen=True)
class RphDecision:
    text: str
    alerts: list[dict]

    def to_dict(self) -> dict:
        return asdict(self)


def normalize_ph_name(value: object) -> str:
    text = normalize_value(value)
    return re.sub(r"\bP\.?\s*H\.?\s+P\.?\s*H\.?\b", "P.H.", text, flags=re.IGNORECASE)


def resolve_rph(values: dict[str, object]) -> RphDecision:
    has_rph = truthy_notarial_value(values.get("es_propiedad_horizontal")) or bool(normalize_value(values.get("coeficiente_copropiedad")))
    if not has_rph:
        return RphDecision("", [])
    paz_y_salvo = values.get("paz_salvo_administracion") or values.get("paz_y_salvo_administracion")
    if truthy_notarial_value(paz_y_salvo):
        return RphDecision("Se deja constancia de que fue presentado paz y salvo de administración de la propiedad horizontal.", [])
    if falsy_notarial_value(paz_y_salvo):
        return RphDecision(
            "No se aportó paz y salvo de administración; las partes quedan advertidas de la responsabilidad solidaria prevista en el artículo 29 de la Ley 675 de 2001.",
            [],
        )
    return RphDecision(
        "Debe revisarse la constancia de paz y salvo de administración de la propiedad horizontal.",
        [{"code": "rph_admin_clearance_missing", "message": "Falta indicar si se presentó paz y salvo de administración.", "field_key": "paz_salvo_administracion"}],
    )
