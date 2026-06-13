from __future__ import annotations

import re

from app.services.minuta.engine.models import RenderIssue, RenderSeverity

from .common_rules import falsy_notarial_value, normalize_key

CONDITIONAL_MARKERS = ("[SI APLICA]", "[NO APLICA]")
SI_APLICA_PATTERN = re.compile(r"\[SI APLICA[^\]]*\]", re.IGNORECASE)


def should_remove_si_aplica_block(values: dict[str, str], paragraph_text: str) -> bool:
    if not SI_APLICA_PATTERN.search(paragraph_text):
        return False
    normalized = normalize_key(paragraph_text)
    if "afectacion" in normalized or "vivienda" in normalized or "familia" in normalized:
        for key in ("queda_afectado", "afectacion_cumple_ley_258", "inmueble_sera_su_casa", "tiene_inmueble_afectado"):
            if key in values and falsy_notarial_value(values.get(key)):
                return True
    if any(token in normalized for token in ("avf", "conyuge", "companero", "consentimiento_hipoteca")):
        spouse_name = values.get("nombre_pareja_o_conyuge", "")
        spouse_document = values.get("numero_documento_pareja_o_conyuge", "")
        if not spouse_name and not spouse_document:
            return True
    return False


def residual_conditional_issue(token: str, location: str) -> RenderIssue:
    return RenderIssue(
        code="residual_conditional_token",
        message=f"Quedó token condicional sin resolver: {token}",
        severity=RenderSeverity.BLOCKER,
        location=location,
        details={"token": token},
    )
