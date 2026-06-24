import unittest

from app.services.minuta.rules.money_rules import format_cop_value, format_money_value, money_to_words, split_money_integer_and_cents


class MoneyRulesTests(unittest.TestCase):
    def test_integer_values_keep_existing_formatting(self):
        self.assertEqual(format_money_value("200000"), "200.000")
        self.assertEqual(format_money_value("1.234.567"), "1.234.567")

    def test_decimal_comma_is_preserved(self):
        self.assertEqual(format_money_value("123456,78"), "123.456,78")
        self.assertEqual(format_money_value("1.234.567,89"), "1.234.567,89")

    def test_decimal_point_is_converted_to_cop_decimal_separator(self):
        self.assertEqual(format_money_value("123456.78"), "123.456,78")

    def test_peso_symbol_is_preserved_or_added_when_requested(self):
        self.assertEqual(format_money_value("$123.456,78"), "$123.456,78")
        self.assertEqual(format_cop_value("200000", include_symbol=True), "$200.000")
        self.assertEqual(format_cop_value("$200000", include_symbol=True), "$200.000")

    def test_empty_value_returns_empty_string(self):
        self.assertEqual(format_money_value(""), "")
        self.assertEqual(format_cop_value(None, include_symbol=True), "")

    def test_non_money_text_is_preserved(self):
        self.assertEqual(format_money_value("precio por definir"), "precio por definir")

    def test_split_money_integer_and_cents_accepts_supported_decimal_formats(self):
        self.assertEqual(split_money_integer_and_cents("63040480,76"), ("63040480", 76))
        self.assertEqual(split_money_integer_and_cents("63040480.76"), ("63040480", 76))
        self.assertEqual(split_money_integer_and_cents("63.040.480,76"), ("63040480", 76))
        self.assertEqual(split_money_integer_and_cents("$63.040.480,76"), ("63040480", 76))
        self.assertEqual(split_money_integer_and_cents("63040480"), ("63040480", None))

    def test_money_to_words_includes_cents_when_present(self):
        expected = "SESENTA Y TRES MILLONES CUARENTA MIL CUATROCIENTOS OCHENTA PESOS CON SETENTA Y SEIS CENTAVOS"
        self.assertEqual(money_to_words("63040480,76", "PESOS"), expected)
        self.assertEqual(money_to_words("63040480.76", "PESOS"), expected)
        self.assertEqual(money_to_words("63.040.480,76", "PESOS"), expected)
        self.assertEqual(money_to_words("$63.040.480,76", "PESOS"), expected)

    def test_money_to_words_keeps_integer_behavior(self):
        self.assertEqual(
            money_to_words("63040480", "PESOS"),
            "SESENTA Y TRES MILLONES CUARENTA MIL CUATROCIENTOS OCHENTA PESOS",
        )

    def test_money_to_words_uses_currency_suffix_with_cents(self):
        self.assertEqual(
            money_to_words("212.600.000,78", "PESOS MONEDA CORRIENTE"),
            "DOSCIENTOS DOCE MILLONES SEISCIENTOS MIL PESOS MONEDA CORRIENTE CON SETENTA Y OCHO CENTAVOS",
        )


if __name__ == "__main__":
    unittest.main()
