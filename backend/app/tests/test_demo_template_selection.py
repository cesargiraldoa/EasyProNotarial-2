from __future__ import annotations

import json
from types import SimpleNamespace
import unittest

from app.api.v1.endpoints.demo_template import _select_explicit_jaggua_version


class DemoTemplateSelectionTests(unittest.TestCase):
    def test_recent_generated_jaggua_document_does_not_replace_seed_template(self):
        generated_case = SimpleNamespace(metadata_json=json.dumps({"source": "marked_template", "filename": "jaggua generado"}))
        generated_document = SimpleNamespace(category="marked_template", title="MINUTA JAGGUA generada")
        generated_version = SimpleNamespace(
            id=20,
            original_filename="MINUTA JAGGUA HIPOTECA BANCO DE BOGOTA - 2 COMPRADORES.docx",
            placeholder_snapshot_json=json.dumps(
                {
                    "source": "marked_template",
                    "fields": [{"key": "numero_apartamento"}],
                    "values": {"numero_apartamento": "804"},
                    "document_name": "MINUTA JAGGUA generada",
                }
            ),
        )

        selected = _select_explicit_jaggua_version([(generated_case, generated_document, generated_version)])

        self.assertIsNone(selected)

    def test_explicit_jaggua_marked_template_can_override_seed(self):
        template_case = SimpleNamespace(metadata_json=json.dumps({"source": "marked_template"}))
        template_document = SimpleNamespace(category="marked_template", title="Plantilla JAGGUA")
        template_version = SimpleNamespace(
            id=10,
            original_filename="jaggua-bogota-2c.docx",
            placeholder_snapshot_json=json.dumps(
                {
                    "source": "marked_template",
                    "demo_template_code": "jaggua-bogota-2c",
                    "template_role": "demo_template",
                }
            ),
        )

        selected = _select_explicit_jaggua_version([(template_case, template_document, template_version)])

        self.assertIs(selected, template_version)


if __name__ == "__main__":
    unittest.main()
