from __future__ import annotations

import io
from types import SimpleNamespace
import unittest

from docx import Document
from fastapi import HTTPException

from app.api.v1.endpoints import biblioteca
from app.services.biblioteca_motor.analysis import analyze_biblioteca_document, extract_candidates, extract_docx_blocks


def _docx_bytes(paragraphs: list[str], table_cells: list[str] | None = None) -> bytes:
    document = Document()
    for text in paragraphs:
        document.add_paragraph(text)
    if table_cells:
        table = document.add_table(rows=1, cols=len(table_cells))
        for index, text in enumerate(table_cells):
            table.cell(0, index).text = text
    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def _fields():
    return [
        {"code": "COMPRADOR_1", "label": "Comprador 1", "category": "persona"},
        {"code": "MATRICULA_INMOBILIARIA", "label": "Matrícula inmobiliaria", "category": "inmueble"},
        {"code": "CEDULA_COMPRADOR_1", "label": "Cédula comprador 1", "category": "persona"},
    ]


def _user(notary_id: int = 10, role_code: str = "protocolist"):
    return SimpleNamespace(
        default_notary_id=notary_id,
        role_assignments=[SimpleNamespace(notary_id=notary_id, role=SimpleNamespace(code=role_code))],
    )


class _FakeQuery:
    def __init__(self, row):
        self.row = row

    def join(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.row


class _FakeDb:
    def __init__(self, row):
        self.row = row

    def query(self, *args, **kwargs):
        return _FakeQuery(self.row)


class _Classifier:
    def __init__(self, classifications):
        self.classifications = classifications

    def classify(self, candidates, fields):
        return self.classifications(candidates, fields)


class _FailingClassifier:
    def classify(self, candidates, fields):
        raise RuntimeError("openai unavailable")


class BibliotecaAnalizarActualTests(unittest.TestCase):
    def test_extraction_in_paragraphs_keeps_exact_offsets(self):
        docx = _docx_bytes(["LOS COMPRADORES: Daniela Campo - cédula de ciudadanía número 1.234.567"])
        blocks = extract_docx_blocks(docx)
        candidates = extract_candidates(docx)
        candidate = next(item for item in candidates if item.original_text == "Daniela Campo")
        block = blocks[candidate.location["block_index"] - 1]

        self.assertEqual(block.text[candidate.location["char_start"]:candidate.location["char_end"]], "Daniela Campo")
        self.assertEqual(candidate.location["block_type"], "paragraph")

    def test_extraction_in_tables_keeps_exact_offsets(self):
        docx = _docx_bytes([], ["Matrícula inmobiliaria 050-123456"])
        blocks = extract_docx_blocks(docx)
        candidates = extract_candidates(docx)
        candidate = next(item for item in candidates if item.candidate_type == "matricula_inmobiliaria")
        block = blocks[candidate.location["block_index"] - 1]

        self.assertEqual(candidate.location["block_type"], "table_cell")
        self.assertEqual(block.text[candidate.location["char_start"]:candidate.location["char_end"]], "050-123456")

    def test_repeated_texts_have_different_ids_and_locations(self):
        docx = _docx_bytes(["Daniela Campo acepta. Daniela Campo firma."])
        matches = [item for item in extract_candidates(docx) if item.original_text == "Daniela Campo"]

        self.assertEqual(len(matches), 2)
        self.assertNotEqual(matches[0].candidate_id, matches[1].candidate_id)
        self.assertNotEqual(matches[0].location["location_key"], matches[1].location["location_key"])
        self.assertEqual([item.location["occurrence_index"] for item in matches], [1, 2])

    def test_location_key_is_stable_and_block_hash_changes_with_text(self):
        base = _docx_bytes(["LOS COMPRADORES: Daniela Campo"])
        edited = _docx_bytes(["LOS COMPRADORES: Daniela Campo editado"])
        first = next(item for item in extract_candidates(base) if item.original_text == "Daniela Campo")
        second = next(item for item in extract_candidates(base) if item.original_text == "Daniela Campo")
        edited_candidate = next(item for item in extract_candidates(edited) if item.original_text == "Daniela Campo")

        self.assertEqual(first.location["location_key"], second.location["location_key"])
        self.assertEqual(first.candidate_id, second.candidate_id)
        self.assertNotEqual(first.location["block_hash"], edited_candidate.location["block_hash"])

    def test_mocked_ai_classification_is_validated_against_catalog(self):
        docx = _docx_bytes(["LOS COMPRADORES: Daniela Campo"])

        def classify(candidates, fields):
            return [{"candidate_id": candidates[0].candidate_id, "field_code": "COMPRADOR_1", "confidence": 0.97, "reason": "comprador"}]

        result = analyze_biblioteca_document(docx, _fields(), ai_classifier=_Classifier(classify))

        self.assertEqual(result["mode"], "hybrid")
        self.assertEqual(result["suggestions"][0]["field_code"], "COMPRADOR_1")
        self.assertIn(result["suggestions"][0]["source"], {"ai", "hybrid"})

    def test_unknown_ai_field_code_becomes_null_when_no_rule_matches(self):
        docx = _docx_bytes(["Banco Demo aprobó el crédito."])

        def classify(candidates, fields):
            return [{"candidate_id": candidates[0].candidate_id, "field_code": "NO_EXISTE", "confidence": 0.8}]

        result = analyze_biblioteca_document(docx, _fields(), ai_classifier=_Classifier(classify))

        self.assertIsNone(result["suggestions"][0]["field_code"])
        self.assertTrue(result["suggestions"][0]["needs_human_review"])

    def test_ai_failure_keeps_deterministic_partial_result(self):
        docx = _docx_bytes(["LOS COMPRADORES: Daniela Campo"])
        result = analyze_biblioteca_document(docx, _fields(), ai_classifier=_FailingClassifier())

        self.assertEqual(result["status"], "completed_with_ai_fallback")
        self.assertGreaterEqual(result["stats"]["deterministic_candidates"], 1)
        self.assertGreaterEqual(len(result["suggestions"]), 1)

    def test_suggestion_contract_keeps_location_fields_for_plugin(self):
        docx = _docx_bytes(["LOS COMPRADORES: Daniela Campo - cédula de ciudadanía número 1.234.567"])
        result = analyze_biblioteca_document(docx, _fields(), ai_classifier=None)
        suggestion = next(item for item in result["suggestions"] if item["original_text"] == "Daniela Campo")
        location = suggestion["location"]

        self.assertEqual(suggestion["original_text"], "Daniela Campo")
        self.assertIn("LOS COMPRADORES", suggestion["context_before"])
        self.assertIn("cédula", suggestion["context_after"])
        self.assertEqual(location["occurrence_index"], 1)
        self.assertTrue(location["location_key"])
        self.assertTrue(location["block_hash"])
        self.assertEqual(location["char_end"] - location["char_start"], len("Daniela Campo"))

    def test_user_from_other_notary_receives_404_for_case_document(self):
        payload = biblioteca.CaseDocumentContext(kind="case_document", case_id=174, document_id=114, version_id=229)
        db = _FakeDb((SimpleNamespace(storage_path="cases/demo.docx"), 20))

        with self.assertRaises(HTTPException) as issue:
            biblioteca._resolve_case_document(payload, db, _user(notary_id=10))

        self.assertEqual(issue.exception.status_code, 404)

    def test_document_id_and_version_id_must_belong_to_case(self):
        payload = biblioteca.CaseDocumentContext(kind="case_document", case_id=174, document_id=999, version_id=229)

        with self.assertRaises(HTTPException) as issue:
            biblioteca._resolve_case_document(payload, _FakeDb(None), _user())

        self.assertEqual(issue.exception.status_code, 404)

    def test_invalid_minuta_token_is_rejected(self):
        payload = biblioteca.MinutaDocumentContext(kind="minuta", editor_token="invalid")

        with self.assertRaises(HTTPException) as issue:
            biblioteca._resolve_minuta_document(payload, _user())

        self.assertEqual(issue.exception.status_code, 401)

    def test_previous_biblioteca_analizar_endpoint_remains_registered(self):
        paths = {route.path for route in biblioteca.router.routes}

        self.assertIn("/biblioteca/analizar", paths)
        self.assertIn("/biblioteca/analizar-actual", paths)


if __name__ == "__main__":
    unittest.main()
