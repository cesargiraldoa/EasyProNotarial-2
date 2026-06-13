import unittest

from app.services.minuta.marked_template_generator import (
    _derive_missing_marked_values,
    _format_money_value,
    _is_money_field,
    _normalize_money_values_for_fields,
    cleanup_empty_second_buyer_text,
    is_second_buyer_empty,
)


class MarkedTemplateGeneratorCleanupTests(unittest.TestCase):
    def test_is_second_buyer_empty_returns_true_when_all_known_fields_are_blank(self):
        values = {
            "nombre_comprador_2": "",
            "tipo_documento_comprador_2": "",
            "numero_documento_comprador_2": "",
            "direccion_comprador_2": "   ",
            "celular_comprador_2": "",
            "email_comprador_2": "",
        }

        self.assertTrue(is_second_buyer_empty(values))

    def test_is_second_buyer_empty_returns_false_when_any_known_field_has_value(self):
        values = {
            "nombre_comprador_2": "MARIA PEREZ",
            "tipo_documento_comprador_2": "",
        }

        self.assertFalse(is_second_buyer_empty(values))

    def test_cleanup_empty_second_buyer_text_removes_inline_residue_patterns(self):
        self.assertEqual(
            cleanup_empty_second_buyer_text("JUAN CAMILO VASQUEZ MIRA - C.C - 1.037.657.164 y  -  -"),
            "JUAN CAMILO VASQUEZ MIRA - C.C - 1.037.657.164",
        )
        self.assertEqual(
            cleanup_empty_second_buyer_text("JUAN CAMILO VASQUEZ MIRA y ,"),
            "JUAN CAMILO VASQUEZ MIRA",
        )
        self.assertEqual(
            cleanup_empty_second_buyer_text("JUAN CAMILO VASQUEZ MIRA y , de las condiciones del contrato"),
            "JUAN CAMILO VASQUEZ MIRA de las condiciones del contrato",
        )
        self.assertEqual(
            cleanup_empty_second_buyer_text("JUAN CAMILO VASQUEZ MIRA y , identificado con cédula"),
            "JUAN CAMILO VASQUEZ MIRA, identificado con cédula",
        )
        self.assertEqual(
            cleanup_empty_second_buyer_text("JUAN CAMILO VASQUEZ MIRA y , quien comparece"),
            "JUAN CAMILO VASQUEZ MIRA quien comparece",
        )
        self.assertEqual(
            cleanup_empty_second_buyer_text("JUAN CAMILO VASQUEZ MIRA y , respectivamente"),
            "JUAN CAMILO VASQUEZ MIRA",
        )

    def test_cleanup_empty_second_buyer_text_removes_empty_profile_lines(self):
        self.assertEqual(cleanup_empty_second_buyer_text("DIRECCIÓN: ."), "")
        self.assertEqual(cleanup_empty_second_buyer_text("CELULAR: ."), "")
        self.assertEqual(cleanup_empty_second_buyer_text("CORREO: ."), "")
        self.assertEqual(cleanup_empty_second_buyer_text("Profesión u Oficio:"), "")
        self.assertEqual(cleanup_empty_second_buyer_text("Actividad Económica:"), "")
        self.assertEqual(cleanup_empty_second_buyer_text("Estado Civil:"), "")

    def test_derive_missing_marked_values_fills_letters_and_origin(self):
        values = {
            "valor_de_la_venta_en_numeros": "212.600.000",
            "en_numeros_cuota_inicial": "63.040.480",
            "valor_del_acto_de_la_hipoteca": "149.559.520",
            "origen_cuota_inicial": "",
        }
        field_keys = {
            "valor_de_la_venta_en_numeros",
            "valor_apartamento_en_letras",
            "en_numeros_cuota_inicial",
            "en_letras_cuota_inicial",
            "valor_del_acto_de_la_hipoteca",
            "valor_del_acto_de_la_hipoteca_en_letras",
            "origen_cuota_inicial",
        }

        derived = _derive_missing_marked_values(values, field_keys)

        self.assertEqual(
            derived["valor_apartamento_en_letras"],
            "DOSCIENTOS DOCE MILLONES SEISCIENTOS MIL PESOS MONEDA LEGAL",
        )
        self.assertEqual(
            derived["en_letras_cuota_inicial"],
            "SESENTA Y TRES MILLONES CUARENTA MIL CUATROCIENTOS OCHENTA PESOS",
        )
        self.assertEqual(
            derived["valor_del_acto_de_la_hipoteca_en_letras"],
            "CIENTO CUARENTA Y NUEVE MILLONES QUINIENTOS CINCUENTA Y NUEVE MIL QUINIENTOS VEINTE PESOS",
        )
        self.assertEqual(derived["origen_cuota_inicial"], "recursos propios")

    def test_money_normalization_formats_general_monetary_fields_without_touching_non_monetary_numbers(self):
        fields = [
            {"key": "avaluo_total_catastral", "label": "Avalúo total catastral", "section": "values"},
            {"key": "retencion_en_la_fuente", "label": "Retención en la fuente", "section": "liquidation"},
            {"key": "numero_documento_comprador_1", "label": "Número documento comprador 1", "section": "buyers"},
        ]
        values = {
            "avaluo_total_catastral": "120000000",
            "retencion_en_la_fuente": "119000",
            "numero_documento_comprador_1": "1037657164",
        }

        normalized = _normalize_money_values_for_fields(values, fields)

        self.assertTrue(_is_money_field(fields[0]))
        self.assertTrue(_is_money_field(fields[1]))
        self.assertFalse(_is_money_field(fields[2]))
        self.assertEqual(normalized["avaluo_total_catastral"], "120.000.000")
        self.assertEqual(normalized["retencion_en_la_fuente"], "119.000")
        self.assertEqual(normalized["numero_documento_comprador_1"], "1037657164")
        self.assertEqual(_format_money_value("212.600.000"), "212.600.000")


if __name__ == "__main__":
    unittest.main()
