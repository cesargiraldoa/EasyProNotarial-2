from __future__ import annotations

from dataclasses import asdict, dataclass

from app.services.minuta.document_alerts import canonical_matricula
from app.services.minuta.rules.common_rules import falsy_notarial_value, normalize_key, normalize_value, truthy_notarial_value


@dataclass(frozen=True)
class AvfDecision:
    decision: str
    text: str
    alerts: list[dict]

    def to_dict(self) -> dict:
        return asdict(self)


def resolve_avf(values: dict[str, object]) -> AvfDecision:
    normalized = {normalize_key(key): normalize_value(value) for key, value in (values or {}).items()}
    matricula = canonical_matricula(normalized)
    casa = normalized.get("inmueble_sera_su_casa") or normalized.get("inmueble_sera_casa_habitacion")
    otro_afectado = normalized.get("tiene_inmueble_afectado") or normalized.get("tiene_bien_afectado")
    estado = normalize_key(normalized.get("estado_civil_comprador") or normalized.get("estado_civil_comprador_1"))
    pareja = normalized.get("nombre_pareja_o_conyuge") or normalized.get("nombre_conyuge") or normalized.get("nombre_companero")
    comparece_pareja = normalized.get("comparece_conyuge") or normalized.get("comparece_companero") or pareja
    comprador_juridico = any(
        truthy_notarial_value(normalized.get(key))
        for key in ("comprador_persona_juridica", "comprador_es_persona_juridica")
    )

    alerts: list[dict] = []
    if not matricula:
        alerts.append({"code": "avf_matricula_missing", "message": "AVF sin matrícula canónica del inmueble principal.", "field_key": "matricula_inmobiliaria"})
    if comprador_juridico:
        return AvfDecision("no_queda_afectado", f"No se constituye afectación a vivienda familiar sobre la matrícula {matricula} porque el comprador es persona jurídica.", alerts)
    if falsy_notarial_value(casa):
        return AvfDecision("no_queda_afectado", f"No se constituye afectación a vivienda familiar sobre la matrícula {matricula} porque el inmueble no se destinará a casa de habitación.", alerts)
    if truthy_notarial_value(otro_afectado):
        return AvfDecision("requiere_revision", f"La afectación a vivienda familiar sobre la matrícula {matricula} requiere revisión porque el comprador informa otro inmueble afectado.", alerts)
    if not casa:
        alerts.append({"code": "avf_home_use_missing", "message": "Falta definir si el inmueble será casa de habitación.", "field_key": "inmueble_sera_su_casa"})
        return AvfDecision("requiere_revision", f"La afectación a vivienda familiar sobre la matrícula {matricula} requiere revisión por datos incompletos.", alerts)
    if "casad" in estado or "union_marital" in estado or "union" in estado:
        if not comparece_pareja:
            alerts.append({"code": "avf_spouse_missing", "message": "Comprador casado o en unión marital sin cónyuge/compañero compareciente.", "field_key": "nombre_pareja_o_conyuge"})
            return AvfDecision("requiere_revision", f"La afectación a vivienda familiar sobre la matrícula {matricula} requiere revisión por falta de comparecencia del cónyuge o compañero.", alerts)
        return AvfDecision("queda_afectado", f"El inmueble identificado con matrícula {matricula} queda afectado a vivienda familiar.", alerts)
    if "solter" in estado or "divorciad" in estado or "viud" in estado:
        return AvfDecision("queda_afectado", f"El inmueble identificado con matrícula {matricula} queda afectado a vivienda familiar si será destinado a casa de habitación.", alerts)
    alerts.append({"code": "avf_marital_status_missing", "message": "Falta estado civil del comprador para decidir AVF.", "field_key": "estado_civil_comprador"})
    return AvfDecision("requiere_revision", f"La afectación a vivienda familiar sobre la matrícula {matricula} requiere revisión por estado civil incompleto.", alerts)
