from __future__ import annotations

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from docx import Document

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.notarial_template_lab.docx_structural_extractor import DocxStructuralExtractor
from tools.notarial_template_lab.document_profiler_agent import DocumentProfilerAgent
from tools.notarial_template_lab.field_proposal_agent import FieldProposalAgent
from tools.notarial_template_lab.field_proposer import FieldProposer
from tools.notarial_template_lab.models import FieldProposal, ProposalOccurrence
from tools.notarial_template_lab.prompt_contracts import compact_document_map
from tools.notarial_template_lab.roundtrip_validator import RoundtripValidator
from tools.notarial_template_lab.run_lab import run_lab
from tools.notarial_template_lab.template_draft_writer import TemplateDraftWriter


class FakeLLMClient:
    def __init__(self):
        self.calls = []

    def complete_json(self, system_prompt: str, payload: dict) -> dict:
        self.calls.append((system_prompt, payload))
        if "Contrato JSON" in system_prompt and "document_type" in system_prompt:
            return {
                "document_type": "escritura_publica",
                "recommended_mode": "documento_individual",
                "acts_detected": ["COMPRAVENTA"],
                "structural_sections": [{"title": "Comparecencia", "block_id": "block_x", "location": "body/paragraph 1"}],
                "parties_summary": [],
                "property_summary": {"items": []},
                "money_summary": [],
                "risk_notes": ["Revision humana requerida."],
                "confidence": 0.7,
                "evidence": [{"block_id": "block_x", "location": "body/paragraph 1", "reason": "Bloque sintetico."}],
            }
        document_map = payload["document_map"]
        target_block = next(block for block in document_map["blocks"] if "matricula inmobiliaria" in block["text"])
        value = "123-4567890"
        start = target_block["text"].index(value)
        return {
            "proposals": [
                {
                    "field_key": "matricula_inmobiliaria",
                    "label": "Matricula inmobiliaria",
                    "marker": "{{matricula_inmobiliaria}}",
                    "value": value,
                    "proposal_type": "project_field",
                    "role": None,
                    "scope": "inmueble",
                    "confidence": 0.91,
                    "occurrences": [
                        {
                            "block_id": target_block["block_id"],
                            "location": target_block["location"],
                            "start": start,
                            "end": start + len(value),
                        }
                    ],
                    "evidence": ["Patron de matricula con rotulo cercano."],
                    "reason": "Ubicacion exacta en DocumentMap compacto.",
                    "apply_strategy": "selected_occurrences",
                },
                {
                    "field_key": "sin_ubicacion",
                    "label": "Sin ubicacion",
                    "marker": "{{sin_ubicacion}}",
                    "value": "NO EXISTE",
                    "proposal_type": "document_field",
                    "role": None,
                    "scope": None,
                    "confidence": 0.95,
                    "occurrences": [],
                    "evidence": [],
                    "reason": "Debe normalizarse como review_required.",
                    "apply_strategy": "all_occurrences",
                },
            ]
        }


class NotarialTemplateLabTests(unittest.TestCase):
    def _build_docx(self, path: Path) -> None:
        doc = Document()
        doc.sections[0].header.add_paragraph("NOTARIA DE PRUEBA")
        doc.sections[0].footer.add_paragraph("PROTOCOLO 12/04/2026")

        paragraph = doc.add_paragraph()
        paragraph.add_run("EL COMPRADOR ")
        bold_run = paragraph.add_run("NOMBRE GENERICO UNO")
        bold_run.bold = True
        paragraph.add_run(", identificado con C.C. 123.456.789, celular 3012345678 y correo usuario@example.org.")

        doc.add_paragraph(
            "El inmueble corresponde al APARTAMENTO 1201 con matricula inmobiliaria 123-4567890 "
            "y codigo predial 123456789012345678901234567890."
        )
        doc.add_paragraph("El precio de venta es $98.765.432 y el saldo es $12.345.678.")

        table = doc.add_table(rows=2, cols=2)
        table.cell(0, 0).text = "Rotulo"
        table.cell(0, 1).text = "Valor"
        table.cell(1, 0).text = "NIT otorgante"
        table.cell(1, 1).text = "800.111.222-3"
        nested = table.cell(1, 1).add_table(rows=1, cols=1)
        nested.cell(0, 0).text = "Fecha escritura 05/06/2026"
        doc.save(path)

    def test_extracts_paragraphs_tables_headers_footers_and_runs(self):
        with TemporaryDirectory() as tmp:
            source = Path(tmp) / "synthetic.docx"
            self._build_docx(source)

            document_map = DocxStructuralExtractor().extract(source)

            self.assertGreaterEqual(document_map.quality.total_blocks, 8)
            self.assertGreater(document_map.quality.total_runs, 0)
            self.assertTrue(any("header section" in block.location for block in document_map.blocks))
            self.assertTrue(any("footer section" in block.location for block in document_map.blocks))
            self.assertTrue(any("/table 1/row 2/cell 2" in block.location for block in document_map.blocks))
            self.assertTrue(any("/table 1/row 2/cell 2/table 1" in block.location for block in document_map.blocks))

            buyer_block = next(block for block in document_map.blocks if "NOMBRE GENERICO UNO" in block.raw_text)
            self.assertEqual(buyer_block.runs[0].start, 0)
            self.assertEqual(buyer_block.runs[0].end, len("EL COMPRADOR "))
            self.assertEqual(buyer_block.runs[1].start, len("EL COMPRADOR "))
            self.assertTrue(buyer_block.runs[1].style.bold)

    def test_detects_general_occurrences_and_proposes_generic_fields(self):
        with TemporaryDirectory() as tmp:
            source = Path(tmp) / "synthetic.docx"
            self._build_docx(source)

            document_map = DocxStructuralExtractor().extract(source)
            occurrence_types = set(document_map.occurrences_index)

            self.assertIn("real_estate_registration", occurrence_types)
            self.assertIn("dotted_document", occurrence_types)
            self.assertIn("nit", occurrence_types)
            self.assertIn("money", occurrence_types)
            self.assertIn("email", occurrence_types)
            self.assertIn("phone", occurrence_types)
            self.assertIn("long_property_code", occurrence_types)
            self.assertIn("date", occurrence_types)
            self.assertIn("uppercase_relevant_phrase", occurrence_types)

            proposals = FieldProposer().propose(document_map)
            keys = {proposal.field_key for proposal in proposals}

            self.assertIn("matricula_inmobiliaria", keys)
            self.assertIn("valor_precio", keys)
            self.assertIn("correo_comprador", keys)
            self.assertTrue(any(proposal.proposal_type == "review_required" for proposal in proposals))

    def test_writes_experimental_docx_and_roundtrips_with_marked_detector(self):
        with TemporaryDirectory() as tmp:
            source = Path(tmp) / "synthetic.docx"
            draft = Path(tmp) / "draft.docx"
            self._build_docx(source)

            document_map = DocxStructuralExtractor().extract(source)
            proposals = FieldProposer().propose(document_map)
            draft_result = TemplateDraftWriter().write(source, draft, document_map, proposals)
            validation = RoundtripValidator().validate(draft)

            self.assertTrue(draft.exists())
            self.assertGreater(len(draft_result.replacements), 0)
            self.assertTrue(validation.opens)
            self.assertTrue(validation.contains_markers)
            self.assertTrue(validation.passed, validation.errors)
            self.assertGreater(validation.marked_fields_count, 0)
            detected_keys = {field["key"] for field in validation.marked_fields}
            self.assertIn("matricula_inmobiliaria", detected_keys)

    def test_compacts_document_map_for_llm_with_auditable_offsets(self):
        with TemporaryDirectory() as tmp:
            source = Path(tmp) / "synthetic.docx"
            self._build_docx(source)

            document_map = DocxStructuralExtractor().extract(source)
            compact = compact_document_map(document_map)

            self.assertEqual(compact["document_id"], document_map.document_id)
            self.assertLessEqual(len(compact["blocks"]), len(document_map.blocks))
            self.assertIn("occurrences_index", compact)
            money = compact["occurrences_index"]["money"][0]
            self.assertIn("block_id", money)
            self.assertIn("location", money)
            self.assertIsInstance(money["start"], int)
            self.assertIsInstance(money["end"], int)

    def test_llm_agents_parse_and_normalize_json(self):
        with TemporaryDirectory() as tmp:
            source = Path(tmp) / "synthetic.docx"
            self._build_docx(source)
            document_map = DocxStructuralExtractor().extract(source)
            client = FakeLLMClient()

            profile = DocumentProfilerAgent(client).run(document_map)
            proposals = FieldProposalAgent(client).run(document_map, profile)

            self.assertEqual(profile.recommended_mode, "documento_individual")
            self.assertEqual(proposals[0].field_key, "matricula_inmobiliaria")
            self.assertEqual(proposals[0].apply_strategy, "selected_occurrences")
            self.assertEqual(proposals[1].proposal_type, "review_required")
            self.assertEqual(proposals[1].apply_strategy, "review_required")

    def test_proposal_without_block_id_is_not_replaceable(self):
        with TemporaryDirectory() as tmp:
            source = Path(tmp) / "synthetic.docx"
            draft = Path(tmp) / "draft.docx"
            self._build_docx(source)
            document_map = DocxStructuralExtractor().extract(source)

            proposal = FieldProposal(
                field_key="correo_comprador",
                label="Correo comprador",
                marker="{{correo_comprador}}",
                value="usuario@example.org",
                confidence=0.99,
                proposal_type="document_field",
                occurrences=[
                    ProposalOccurrence(
                        occurrence_id="occ_fake",
                        block_id="",
                        location="",
                        text="usuario@example.org",
                        start=0,
                        end=19,
                        before="",
                        after="",
                    )
                ],
                apply_strategy="selected_occurrences",
                reason="Sin ubicacion exacta.",
            )

            result = TemplateDraftWriter().write(source, draft, document_map, [proposal])

            self.assertEqual(len(result.replacements), 0)
            self.assertTrue(any("block_id" in item["reason"] for item in result.skipped))

    def test_run_lab_with_llm_mock_writes_profile_and_llm_proposals(self):
        with TemporaryDirectory() as tmp:
            source = Path(tmp) / "synthetic.docx"
            artifacts_root = Path(tmp) / "artifacts"
            self._build_docx(source)

            result = run_lab(source, artifacts_root, use_llm=True, llm_client=FakeLLMClient())
            artifacts_dir = Path(result["artifacts_dir"])

            self.assertTrue((artifacts_dir / "02_document_profile.json").exists())
            self.assertTrue((artifacts_dir / "03_field_proposals_llm.json").exists())
            self.assertGreaterEqual(result["total_llm_proposals"], 1)


if __name__ == "__main__":
    unittest.main()
