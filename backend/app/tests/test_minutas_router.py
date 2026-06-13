import unittest

from app.modules.minutas.router import _sanitize_marked_document_name


class MinutasRouterTests(unittest.TestCase):
    def test_sanitize_marked_document_name_uses_custom_name_and_docx_extension(self):
        filename, title = _sanitize_marked_document_name(
            "Compraventa Jaggua - Juan Camilo Vásquez - Apto 804",
            "minuta.docx",
        )

        self.assertEqual(filename, "Compraventa Jaggua - Juan Camilo Vásquez - Apto 804.docx")
        self.assertEqual(title, "Compraventa Jaggua - Juan Camilo Vásquez - Apto 804")

    def test_sanitize_marked_document_name_falls_back_to_current_behavior(self):
        filename, title = _sanitize_marked_document_name("", "MINUTA JAGGUA HIPOTECA BANCO DE BOGOTÁ.docx")

        self.assertEqual(filename, "minuta_generada_MINUTA JAGGUA HIPOTECA BANCO DE BOGOTÁ.docx")
        self.assertEqual(title, "minuta_generada_MINUTA JAGGUA HIPOTECA BANCO DE BOGOTÁ")


if __name__ == "__main__":
    unittest.main()
