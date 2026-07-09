from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from docx import Document

from app.services.minuta.assisted_tagging.approved_template_parser import ApprovedTemplateParser
from app.services.minuta.assisted_tagging.docx_red_writer import DocxRedWriter
from app.services.minuta.assisted_tagging.docx_structure_extractor import DocxStructureExtractor
from app.services.minuta.assisted_tagging.llm_tagging_client import LlmTaggingClient
from app.services.minuta.assisted_tagging.tagging_response_validator import TaggingResponseValidator


class AssistedTaggingTest(unittest.TestCase):
    def _sample_docx(self, path: Path) -> None:
        doc = Document()
        doc.add_paragraph("ESCRITURA PUBLICA NUMERO 1234")
        doc.add_paragraph("Comparece JUAN CAMILO VASQUEZ MIRA identificado con C.C. 1.037.657.164.")
        doc.add_paragraph("El precio de venta es $212.600.000 y la fecha es 9 de marzo de 2024.")
        doc.save(str(path))

    def test_pretagging_writes_red_and_parser_builds_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            source = Path(tmp_dir) / "sample.docx"
            red = Path(tmp_dir) / "red.docx"
            self._sample_docx(source)

            structure = DocxStructureExtractor().extract(source)
            raw = LlmTaggingClient()._deterministic_proposal(structure)
            validated = TaggingResponseValidator().validate(raw, structure)
            self.assertGreaterEqual(len(validated.fields), 2)

            audit = DocxRedWriter().write(source, red, validated.fields)
            self.assertGreater(audit["red_runs_written"], 0)

            parsed = ApprovedTemplateParser().parse(red)
            self.assertGreater(parsed.variable_count, 0)
            technical = Path(tmp_dir) / "technical.docx"
            technical.write_bytes(parsed.technical_docx)
            doc = Document(str(technical))
            text = "\n".join(p.text for p in doc.paragraphs)
            self.assertIn("{{", text)
            self.assertIn("}}", text)

    def test_validator_rejects_text_not_present_in_docx(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            source = Path(tmp_dir) / "sample.docx"
            self._sample_docx(source)
            structure = DocxStructureExtractor().extract(source)
            result = TaggingResponseValidator().validate(
                {"fields": [{"field_code": "inventado", "label": "Inventado", "text": "NO EXISTE"}]},
                structure,
            )
            self.assertEqual(result.fields, [])
            self.assertTrue(result.warnings)


if __name__ == "__main__":
    unittest.main()
