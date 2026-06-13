from __future__ import annotations

from app.services.minuta.engine.models import NotarialDateValue, NotarialMoneyValue, NotarialPerson, NotarialRenderContext
from app.services.minuta.rules.common_rules import extract_digits, normalize_key, normalize_value
from app.services.minuta.rules.date_rules import (
    contractual_date_text,
    is_contractual_date_key,
    is_date_field,
    normalize_month_text,
    notarial_date_text,
    notarial_day_text,
)
from app.services.minuta.rules.gender_rules import normalize_gender
from app.services.minuta.rules.money_rules import format_money_value, is_money_field, number_to_words
from app.services.minuta.rules.person_rules import grammar_for_gender, normalize_document_type, normalize_transit_phrase

DERIVED_MONEY_RULES = (
    ("valor_de_la_venta_en_numeros", "valor_apartamento_en_letras", "PESOS MONEDA LEGAL"),
    ("en_numeros_cuota_inicial", "en_letras_cuota_inicial", "PESOS"),
    ("valor_del_acto_de_la_hipoteca", "valor_del_acto_de_la_hipoteca_en_letras", "PESOS"),
)

PERSON_ROLES = (
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


class ContextBuilder:
    def build(self, values: dict, fields: list[dict] | None = None) -> NotarialRenderContext:
        fields_list = fields or []
        normalized_values = {normalize_key(key): normalize_value(value) for key, value in (values or {}).items()}
        field_key_map = {normalize_key(field.get("key") or ""): field for field in fields_list if isinstance(field, dict)}

        money_values = self._normalize_money_values(normalized_values, fields_list)
        self._derive_money_letters(normalized_values, field_key_map)
        dates = self._normalize_dates(normalized_values, fields_list)
        self._normalize_person_values(normalized_values)

        return NotarialRenderContext(
            values={str(key): normalize_value(value) for key, value in (values or {}).items()},
            normalized_values=normalized_values,
            fields=fields_list,
            people=self._people(normalized_values),
            money_values=money_values,
            dates=dates,
        )

    def _normalize_money_values(self, normalized_values: dict[str, str], fields: list[dict]) -> list[NotarialMoneyValue]:
        result: list[NotarialMoneyValue] = []
        for field in fields:
            if not isinstance(field, dict) or not is_money_field(field):
                continue
            key = normalize_key(field.get("key") or "")
            if not key or key not in normalized_values:
                continue
            formatted = format_money_value(normalized_values[key])
            normalized_values[key] = formatted
            digits = extract_digits(formatted)
            words = number_to_words(int(digits), "PESOS") if digits else ""
            result.append(NotarialMoneyValue(key=key, numeric_text=digits, formatted_text=formatted, text_in_words=words))
        return result

    def _derive_money_letters(self, normalized_values: dict[str, str], field_key_map: dict[str, dict]) -> None:
        for money_key, letter_key, suffix in DERIVED_MONEY_RULES:
            if money_key not in normalized_values or letter_key not in field_key_map:
                continue
            if normalized_values.get(letter_key, "").strip():
                continue
            digits = extract_digits(normalized_values.get(money_key, ""))
            if digits:
                normalized_values[letter_key] = number_to_words(int(digits), suffix)

    def _normalize_dates(self, normalized_values: dict[str, str], fields: list[dict]) -> list[NotarialDateValue]:
        result: list[NotarialDateValue] = []
        for field in fields:
            if not isinstance(field, dict) or not is_date_field(field):
                continue
            key = normalize_key(field.get("key") or "")
            if not key or key not in normalized_values:
                continue
            if key.startswith("dia_elaboracion"):
                text = notarial_day_text(normalized_values[key])
            elif key.startswith("mes_elaboracion"):
                text = normalize_month_text(normalized_values[key])
            elif is_contractual_date_key(key):
                text = contractual_date_text(normalized_values[key])
            else:
                text = notarial_date_text(normalized_values[key])
            if text:
                normalized_values[key] = text
                result.append(NotarialDateValue(key=key, iso_value=normalize_value(normalized_values[key]), notarial_text=text))
        return result

    def _normalize_person_values(self, normalized_values: dict[str, str]) -> None:
        buyer_1_grammar = grammar_for_gender(
            normalized_values.get("comprador_es_hombre_o_mujer") or normalized_values.get("comprador_1_es_hombre_o_mujer"),
            normalized_values.get("nacionalidad_comprador") or normalized_values.get("nacionalidad_comprador_1"),
        )
        buyer_2_grammar = grammar_for_gender(
            normalized_values.get("comprador_2_es_hombre_o_mujer"),
            normalized_values.get("nacionalidad_comprador_2"),
        )

        if "comprador_es_hombre_o_mujer" in normalized_values:
            normalized_values["comprador_es_hombre_o_mujer"] = buyer_1_grammar.gender_word
        if "comprador_1_es_hombre_o_mujer" in normalized_values:
            normalized_values["comprador_1_es_hombre_o_mujer"] = buyer_1_grammar.gender_word
        if "comprador_2_es_hombre_o_mujer" in normalized_values:
            normalized_values["comprador_2_es_hombre_o_mujer"] = buyer_2_grammar.gender_word

        if "nacionalidad_comprador" in normalized_values:
            normalized_values["nacionalidad_comprador"] = buyer_1_grammar.nationality
        if "nacionalidad_comprador_1" in normalized_values:
            normalized_values["nacionalidad_comprador_1"] = buyer_1_grammar.nationality
        if "nacionalidad_comprador_2" in normalized_values:
            normalized_values["nacionalidad_comprador_2"] = buyer_2_grammar.nationality

        for key in ("tipo_documento_comprador", "tipo_documento_comprador_1", "tipo_documento_comprador_2"):
            if key in normalized_values:
                normalized_values[key] = normalize_document_type(normalized_values[key])
        for key in ("estado_civil_comprador", "estado_civil_comprador_1", "estado_civil_comprador_2"):
            if key in normalized_values:
                normalized_values[key] = normalized_values[key].lower()
        for key in ("seleccione_si_comprador_esta_de_transito", "seleccione_si_comprador_1_esta_de_transito", "seleccione_si_comprador_2_esta_de_transito"):
            if key in normalized_values:
                normalized_values[key] = normalize_transit_phrase(normalized_values[key])

    def _people(self, normalized_values: dict[str, str]) -> list[NotarialPerson]:
        people: list[NotarialPerson] = []
        for role in PERSON_ROLES:
            name = normalized_values.get(f"nombre_{role}", "")
            if role == "comprador_1" and not name:
                name = normalized_values.get("nombre_comprador", "")
            if not name:
                continue
            people.append(
                NotarialPerson(
                    role=role,
                    full_name=name,
                    document_type=normalized_values.get(f"tipo_documento_{role}", ""),
                    document_number=normalized_values.get(f"numero_documento_{role}", ""),
                    gender=normalize_gender(normalized_values.get(f"{role}_es_hombre_o_mujer", "")),
                    nationality=normalized_values.get(f"nacionalidad_{role}", ""),
                    marital_status=normalized_values.get(f"estado_civil_{role}", ""),
                )
            )
        return people
