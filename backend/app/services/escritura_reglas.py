from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy.orm import Session

from app.models.legal_norma import LegalNorma
from app.models.legal_regla import LegalRegla
from app.services.legal_corpus import reglas_vigentes


@dataclass(frozen=True)
class Hallazgo:
    codigo: str
    severidad: str
    mensaje: str
    efecto: str
    norma_id: int | None
    norma: str | None


_MISSING_SENTINELS = {"faltante", "missing", "vacio", "vacío"}


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) == 0
    return False


def _number(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        if isinstance(value, str):
            raw = value.strip().replace("$", "").replace(" ", "")
            if "," in raw:
                raw = raw.replace(".", "").replace(",", ".")
            return Decimal(raw)
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _path_value(state: dict[str, Any], path: str) -> Any:
    current: Any = state
    for part in path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
            continue
        if isinstance(current, list) and part.isdigit():
            index = int(part)
            current = current[index] if 0 <= index < len(current) else None
            continue
        return None
    return current


def _first_party_type(state: dict[str, Any], key: str) -> str | None:
    parties = state.get(key)
    if isinstance(parties, list) and parties and isinstance(parties[0], dict):
        value = parties[0].get("tipo")
        return str(value) if value is not None else None
    return None


def _any_party_type(state: dict[str, Any], key: str, expected: str) -> bool:
    parties = state.get(key)
    if not isinstance(parties, list):
        return False
    return any(isinstance(item, dict) and item.get("tipo") == expected for item in parties)


def _any_party_doc(state: dict[str, Any], expected: set[str]) -> bool:
    for key in ("V", "C"):
        parties = state.get(key)
        if not isinstance(parties, list):
            continue
        if any(isinstance(item, dict) and item.get("tipoDoc") in expected for item in parties):
            return True
    return False


def _nested_bool(state: dict[str, Any], group: str, *keys: str) -> bool:
    data = state.get(group)
    if not isinstance(data, dict):
        return False
    return any(bool(data.get(key)) for key in keys)


def _state_inmuebles(state: dict[str, Any]) -> list[dict[str, Any]]:
    raw = state.get("inmuebles")
    if isinstance(raw, list) and raw:
        return [item for item in raw if isinstance(item, dict)]
    return [
        {
            "descripcion": state.get("inmdesc"),
            "matricula": state.get("matricula"),
            "linderos": state.get("linderos"),
            "catastral": state.get("catastral"),
            "nupre": state.get("nupre"),
        }
    ]


def _encadenamiento_activo(state: dict[str, Any], key: str) -> bool:
    encadenamientos = state.get("encadenamientos")
    return isinstance(encadenamientos, dict) and bool(encadenamientos.get(key))


def _resolve_value(state: dict[str, Any], field: str) -> Any:
    direct = _path_value(state, field)
    if direct is not None:
        return direct

    if field == "varios_inmuebles":
        return len(_state_inmuebles(state)) > 1
    if field == "inmuebles_con_identificacion_incompleta":
        return any(_is_missing(item.get("matricula")) or _is_missing(item.get("linderos")) for item in _state_inmuebles(state))
    if field == "folio_estado_especial":
        return state.get("folioEstado") in {"segregado", "englobe", "desenglobe", "mayor_extension", "falsa_tradicion"}
    if field == "folio_falsa_tradicion":
        return state.get("folioEstado") == "falsa_tradicion"
    if field == "encadenamiento_cancelacion_hipoteca_previa":
        return _encadenamiento_activo(state, "cancelacionHipotecaPrevia")
    if field == "encadenamiento_cancelacion_patrimonio_familia":
        return _encadenamiento_activo(state, "cancelacionPatrimonioFamilia")
    if field == "encadenamiento_afectacion_vivienda_familiar":
        return _encadenamiento_activo(state, "afectacionViviendaFamiliar")
    if field == "parte_extranjera_no_residente":
        return _nested_bool(state, "divisas", "parteExtranjeraNoResidente") or _any_party_doc(state, {"CE", "PA", "PPT"})
    if field == "pago_divisas":
        return _nested_bool(state, "divisas", "pagoDivisas")
    if field == "registro_inversion_extranjera":
        return _nested_bool(state, "divisas", "registroInversionExtranjera")
    if field == "canalizacion_mercado_cambiario":
        return _nested_bool(state, "divisas", "canalizacionMercadoCambiario")
    if field == "poder_exterior_apostillado":
        return _nested_bool(state, "divisas", "poderExteriorApostillado")
    if field == "predio_rural":
        return _nested_bool(state, "rural", "predioRural")
    if field == "baldio_adjudicado":
        return _nested_bool(state, "rural", "baldioAdjudicado")
    if field == "baldio_restriccion_temporal":
        return _nested_bool(state, "rural", "baldioAdjudicado") and _nested_bool(state, "rural", "restriccionTemporal")
    if field == "supera_uaf":
        return _nested_bool(state, "rural", "superaUaf")
    if field == "autorizacion_ant":
        return _nested_bool(state, "rural", "autorizacionAnt")
    if field == "derecho_preferencia_agrario":
        return _nested_bool(state, "rural", "derechoPreferencia")
    if field == "venta_bien_menor":
        return _nested_bool(state, "capacidad", "ventaBienMenor", "menorVendedor")
    if field == "autorizacion_venta_menor":
        return _nested_bool(state, "capacidad", "autorizacionVentaMenor")
    if field == "discapacidad_con_apoyos":
        return _nested_bool(state, "capacidad", "discapacidadConApoyos")
    if field == "apoyo_acreditado":
        return _nested_bool(state, "capacidad", "apoyoAcreditado")

    aliases = {
        "matricula_inmobiliaria": ("matricula", "cMatricula"),
        "hipoteca_numero_escritura": ("cHipEP",),
        "hipoteca_fecha": ("cHipFecha",),
        "hipoteca_notaria": ("cHipNotaria",),
        "hipoteca_fecha_registro": ("cHipRegFecha",),
        "acreedor_comparece": ("cBanco",),
        "apoderado_banco_firma_fuera_sede": ("firma_fuera_sede",),
        "acreedor_firma_fuera_sede": ("firma_fuera_sede",),
        "registro_plazo_especial": ("registro_plazo_especial",),
        "acto_sujeto_impuesto_registro": ("acto_sujeto_impuesto_registro",),
        "registro_presentado_despues_de_meses": ("registro_presentado_despues_de_meses",),
        "declaracion_ley_258": ("afect",),
        "declaracion_precio_real": ("declaracion_precio_real",),
        "area": ("area", "cabida", "inmdesc", "cInmdesc"),
        "linderos": ("linderos",),
    }
    for alias in aliases.get(field, ()):
        value = _path_value(state, alias)
        if value is not None:
            return value

    if field == "vendedor_tipo_persona":
        return _first_party_type(state, "V")
    if field == "vendedor_persona_natural":
        return _any_party_type(state, "V", "natural")
    if field == "inmueble_destinado_vivienda":
        text = f"{state.get('inmdesc', '')} {state.get('cInmdesc', '')}".lower()
        return "vivienda" in text or "apartamento" in text or "casa" in text
    if field == "inmueble_afectado_vivienda_familiar":
        return state.get("afect") == "si"
    if field == "patrimonio_familia_vigente":
        return state.get("gravamen") == "patrimonio"
    if field == "leasing_habitacional_vigente":
        return state.get("gravamen") == "leasing"
    if field == "entidad_financiera_propietaria":
        return state.get("gravamen") == "leasing"
    if field == "cancelacion_acreditada":
        return bool(state.get("cancelacion_acreditada"))
    if field == "conyuge_o_companero_firma":
        return bool(state.get("conyuge_o_companero_firma"))
    if field == "compareciente":
        return state.get("compareciente")
    return None


def _matches_operator(value: Any, operator: str, expected: Any) -> bool:
    if operator == "present":
        return (not _is_missing(value)) is bool(expected)
    if operator == "missing":
        return _is_missing(value) is bool(expected)
    if operator == "eq":
        return value == expected
    if operator == "ne":
        return value != expected
    if operator == "allowed":
        return value in expected if isinstance(expected, list) else False

    left = _number(value)
    right = _number(expected)
    if left is None or right is None:
        return False
    if operator == "lt":
        return left < right
    if operator == "lte":
        return left <= right
    if operator == "gt":
        return left > right
    if operator == "gte":
        return left >= right
    return False


def _matches_expected(value: Any, expected: Any) -> bool:
    if isinstance(expected, dict):
        return all(_matches_operator(value, operator, operand) for operator, operand in expected.items())
    if isinstance(expected, str) and expected.lower() in _MISSING_SENTINELS:
        return _is_missing(value)
    if expected == "embargo_o_medida_cautelar_vigente" and value == "embargo":
        return True
    if isinstance(expected, list):
        if isinstance(value, list):
            return any(item in expected for item in value)
        return value in expected
    left = _number(value)
    right = _number(expected)
    if left is not None and right is not None:
        return left == right
    return value == expected


def condicion_cumple(condicion: dict[str, Any], state: dict[str, Any]) -> bool:
    """Evalua una condicion JSON simple contra el state.

    La condicion usa AND implicito por campo. Cada campo puede tener igualdad
    directa, el valor especial "faltante", o un objeto de operadores:
    present, missing, eq, ne, lt, lte, gt, gte y allowed.
    """

    if not condicion:
        return False
    return all(_matches_expected(_resolve_value(state, field), expected) for field, expected in condicion.items())


def _norma_label(session: Session, norma_id: int | None) -> str | None:
    if norma_id is None:
        return None
    norma = session.get(LegalNorma, norma_id)
    if norma is None:
        return None
    parts = [norma.tipo, norma.numero, str(norma.anio)]
    if norma.articulo:
        parts.append(norma.articulo)
    return " ".join(parts)


def evaluar_reglas(session: Session, acto_code: str, fecha: date, state: dict[str, Any]) -> list[Hallazgo]:
    hallazgos: list[Hallazgo] = []
    for regla in reglas_vigentes(session, acto_code, fecha):
        if condicion_cumple(regla.condicion_json, state):
            hallazgos.append(
                Hallazgo(
                    codigo=regla.codigo,
                    severidad=regla.severidad,
                    mensaje=regla.mensaje,
                    efecto=regla.efecto,
                    norma_id=regla.norma_id,
                    norma=_norma_label(session, regla.norma_id),
                )
            )
    return hallazgos
