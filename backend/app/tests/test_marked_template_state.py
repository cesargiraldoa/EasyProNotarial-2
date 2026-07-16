import unittest

from app.services.minuta.marked_template_state import merge_marked_template_state


class MarkedTemplateStateTests(unittest.TestCase):
    def test_merge_preserves_previous_values_and_adds_new_marker_empty(self):
        previous = {
            "source": "marked_template",
            "document_name": "MINUTA JAGGUA",
            "fields": [
                {
                    "key": "nombre_comprador_1",
                    "label": "Nombre comprador 1",
                    "section": "Compradores",
                    "occurrences": 2,
                    "marker_types": ["curly"],
                    "raw_markers": ["{{NOMBRE_COMPRADOR_1}}"],
                }
            ],
            "values": {"nombre_comprador_1": "ANA MARIA"},
        }
        detected = {
            "fields": [
                {
                    "key": "numero_parqueadero",
                    "label": "Numero parqueadero",
                    "section": "Inmueble",
                    "occurrences": 1,
                    "marker_types": ["curly"],
                    "raw_markers": ["{{NUMERO_PARQUEADERO}}"],
                }
            ]
        }

        merged = merge_marked_template_state(previous, detected, document_name="fallback")

        self.assertEqual(merged["document_name"], "MINUTA JAGGUA")
        self.assertEqual([field["key"] for field in merged["fields"]], ["nombre_comprador_1", "numero_parqueadero"])
        self.assertEqual(merged["values"]["nombre_comprador_1"], "ANA MARIA")
        self.assertEqual(merged["values"]["numero_parqueadero"], "")


if __name__ == "__main__":
    unittest.main()
