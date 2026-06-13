from __future__ import annotations

from app.services.minuta.engine.models import NotarialDateValue, NotarialMoneyValue, NotarialPerson, NotarialRenderContext
from app.services.minuta.rules.common_rules import extract_digits, normalize_key, normalize_value
from app.services.minuta.rules.date_rules import is_date_field, normalize_month_text, notarial_date_text, notarial_day_text
from app.services.minuta.rules.gender_rules import normalize_gender
from app.services.minuta.rules.money_rules import format_money_value, is_money_field, number_to_words

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
            else:
                text = notarial_date_text(normalized_values[key])
            if text:
                normalized_values[key] = text
                result.append(NotarialDateValue(key=key, iso_value=normalize_value(normalized_values[key]), notarial_text=text))
        return result

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
