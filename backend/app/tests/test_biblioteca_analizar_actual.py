from __future__ import annotations

import io
from types import SimpleNamespace
import unittest

from docx import Document
from fastapi import HTTPException

from app.api.v1.endpoints import biblioteca
from app.services.biblioteca_motor.analysis import (
    ANALYSIS_TOTAL_BUDGET_SECONDS,
    MAX_AI_CANDIDATES,
    analyze_biblioteca_document,
    extract_candidates,
    extract_docx_blocks,
)


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
        {"code": "VENDEDOR_1", "label": "Vendedor 1", "category": "persona"},
        {"code": "BANCO", "label": "Banco", "category": "valor"},
        {"code": "MATRICULA_INMOBILIARIA", "label": "Matricula inmobiliaria", "category": "inmueble"},
        {"code": "CEDULA_COMPRADOR_1", "label": "Cedula comprador 1", "category": "persona"},
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
        self.calls = 0

    def classify(self, candidates, fields):
        self.calls += 1
        return self.classifications(candidates, fields)


class _FailingClassifier:
    def __init__(self):
        self.calls = 0

    def classify(self, candidates, fields, timeout_seconds=None):
        self.calls += 1
        raise RuntimeError("openai unavailable")


class _TimeoutClassifier:
    def __init__(self):
        self.calls = 0

    def classify(self, candidates, fields, timeout_seconds=None):
        self.calls += 1
        raise TimeoutError("openai timeout")


class _RecordingClassifier:
    def __init__(self):
        self.batch_sizes = []
        self.calls = 0
        self.timeout_seconds = []

    def classify(self, candidates, fields, timeout_seconds=None):
        self.calls += 1
        self.batch_sizes.append(len(candidates))
        self.timeout_seconds.append(timeout_seconds)
        return [
            {"candidate_id": item.candidate_id, "field_code": "VENDEDOR_1", "confidence": 0.9}
            for item in candidates
            if item.candidate_type == "person_name"
        ]


class _InvalidJsonClassifier:
    def __init__(self):
        self.calls = 0

    def classify(self, candidates, fields, timeout_seconds=None):
        self.calls += 1
        return {"classifications": []}


class BibliotecaAnalizarActualTests(unittest.TestCase):
    def test_extraction_in_paragraphs_keeps_exact_offsets(self):
        docx = _docx_bytes(["LOS COMPRADORES: Daniela Campo - cedula de ciudadania numero 1.234.567"])
        blocks = extract_docx_blocks(docx)
        candidates = extract_candidates(docx)
        candidate = next(item for item in candidates if item.original_text == "Daniela Campo")
        block = blocks[candidate.location["block_index"] - 1]

        self.assertEqual(block.text[candidate.location["char_start"]:candidate.location["char_end"]], "Daniela Campo")
        self.assertEqual(candidate.location["block_type"], "paragraph")

    def test_extraction_in_tables_keeps_exact_offsets(self):
        docx = _docx_bytes([], ["Matricula inmobiliaria 050-123456"])
        blocks = extract_docx_blocks(docx)
        candidates = extract_candidates(docx)
        candidate = next(item for item in candidates if item.candidate_type == "matricula_inmobiliaria")
        block = blocks[candidate.location["block_index"] - 1]

        self.assertEqual(candidate.location["block_type"], "table_cell")
        self.assertEqual(block.text[candidate.location["char_start"]:candidate.location["char_end"]], "050-123456")

    def test_repeated_texts_have_different_ids_and_locations(self):
        docx = _docx_bytes(["LOS COMPRADORES: Daniela Campo acepta. Daniela Campo firma."])
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
        docx = _docx_bytes(["LOS VENDEDORES: Carlos Perez comparece al otorgamiento."])

        def classify(candidates, fields):
            return [{"candidate_id": candidates[0].candidate_id, "field_code": "VENDEDOR_1", "confidence": 0.97, "reason": "vendedor"}]

        result = analyze_biblioteca_document(docx, _fields(), ai_classifier=_Classifier(classify))

        self.assertEqual(result["mode"], "hybrid")
        self.assertEqual(result["status"], "completed_hybrid")
        self.assertEqual(result["suggestions"][0]["field_code"], "VENDEDOR_1")
        self.assertEqual(result["suggestions"][0]["source"], "ai")

    def test_unknown_ai_field_code_is_not_renderable_suggestion(self):
        docx = _docx_bytes(["LOS VENDEDORES: Carlos Perez comparece al otorgamiento."])

        def classify(candidates, fields):
            return [{"candidate_id": candidates[0].candidate_id, "field_code": "NO_EXISTE", "confidence": 0.8}]

        result = analyze_biblioteca_document(docx, _fields(), ai_classifier=_Classifier(classify))

        self.assertEqual(result["suggestions"], [])
        self.assertEqual(result["stats"]["suggestions"], 0)
        self.assertGreaterEqual(result["stats"]["unclassified_candidates"], 1)

    def test_ai_is_not_called_for_high_certainty_deterministic_candidates(self):
        classifier = _FailingClassifier()
        docx = _docx_bytes(["LOS COMPRADORES: Daniela Campo"])
        result = analyze_biblioteca_document(docx, _fields(), ai_classifier=classifier)

        self.assertEqual(classifier.calls, 0)
        self.assertEqual(result["status"], "completed_deterministic")
        self.assertGreaterEqual(result["stats"]["deterministic_candidates"], 1)
        self.assertGreaterEqual(len(result["suggestions"]), 1)

    def test_suggestion_contract_keeps_location_fields_for_plugin(self):
        docx = _docx_bytes(["LOS COMPRADORES: Daniela Campo - cedula de ciudadania numero 1.234.567"])
        result = analyze_biblioteca_document(docx, _fields(), ai_classifier=None)
        suggestion = next(item for item in result["suggestions"] if item["original_text"] == "Daniela Campo")
        location = suggestion["location"]

        self.assertEqual(suggestion["original_text"], "Daniela Campo")
        self.assertIn("LOS COMPRADORES", suggestion["context_before"])
        self.assertIn("cedula", suggestion["context_after"])
        self.assertEqual(location["occurrence_index"], 1)
        self.assertTrue(location["location_key"])
        self.assertTrue(location["block_hash"])
        self.assertEqual(location["char_end"] - location["char_start"], len("Daniela Campo"))

    def test_many_candidates_do_not_become_many_suggestions_without_fields(self):
        paragraphs = ["LOS COMPRADORES: Daniela Campo"]
        paragraphs.extend([f"Banco Demo aprobo credito {index}" for index in range(80)])
        docx = _docx_bytes(paragraphs)
        limited_fields = [{"code": "COMPRADOR_1", "label": "Comprador 1", "category": "persona"}]
        result = analyze_biblioteca_document(docx, limited_fields, ai_classifier=None)

        self.assertGreater(result["stats"]["deterministic_candidates"], result["stats"]["suggestions"])
        self.assertLess(result["stats"]["suggestions"], result["stats"]["deterministic_candidates"])
        self.assertTrue(all(item["field_code"] for item in result["suggestions"]))

    def test_legal_headings_are_not_person_names(self):
        docx = _docx_bytes(["LOS COMPRADORES VALOR DEL ACTO INSTRUMENTO PUBLICO"])
        candidates = extract_candidates(docx)

        self.assertFalse([item for item in candidates if item.candidate_type == "person_name"])

    def test_buyer_name_in_role_context_can_be_person_name(self):
        docx = _docx_bytes(["LOS COMPRADORES: DANIELA CAMPO identificada con cedula numero 1234567"])
        candidates = extract_candidates(docx)

        self.assertTrue([item for item in candidates if item.candidate_type == "person_name" and item.original_text == "DANIELA CAMPO"])

    def test_overlapping_spans_are_deduplicated_by_priority(self):
        docx = _docx_bytes(["LOS COMPRADORES: Banco Demo con NIT 900123456-7"])
        candidates = extract_candidates(docx)
        spans = [(item.location["char_start"], item.location["char_end"]) for item in candidates]

        self.assertEqual(len(spans), len(set(spans)))

    def test_stats_keep_total_and_unclassified_candidates(self):
        docx = _docx_bytes(["LOS COMPRADORES: Daniela Campo. Banco Demo aprobo el credito."])
        result = analyze_biblioteca_document(docx, _fields(), ai_classifier=None)

        self.assertGreaterEqual(result["stats"]["deterministic_candidates"], 1)
        self.assertEqual(
            result["stats"]["deterministic_candidates"],
            result["stats"]["classified_candidates"] + result["stats"]["unclassified_candidates"],
        )

    def test_940_candidates_do_not_generate_multiple_ai_calls(self):
        paragraphs = ["LOS COMPRADORES: Daniela Campo"]
        paragraphs.extend([f"LOS VENDEDORES: Carlos Perez comparece {index}" for index in range(940)])
        classifier = _RecordingClassifier()
        result = analyze_biblioteca_document(_docx_bytes(paragraphs), _fields(), ai_classifier=classifier)

        self.assertEqual(classifier.calls, 1)
        self.assertEqual(classifier.batch_sizes, [MAX_AI_CANDIDATES])
        self.assertEqual(result["stats"]["ai_candidates_sent"], MAX_AI_CANDIDATES)
        self.assertGreater(result["stats"]["ai_candidates_omitted"], 0)
        self.assertLess(result["stats"]["suggestions"], result["stats"]["deterministic_candidates"])

    def test_ai_processes_candidates_in_single_bounded_call(self):
        paragraphs = [f"LOS VENDEDORES: Carlos Perez comparece {index}" for index in range(130)]
        classifier = _RecordingClassifier()
        result = analyze_biblioteca_document(_docx_bytes(paragraphs), _fields(), ai_classifier=classifier)

        self.assertEqual(classifier.calls, 1)
        self.assertEqual(classifier.batch_sizes, [MAX_AI_CANDIDATES])
        self.assertTrue(all(timeout <= 10 for timeout in classifier.timeout_seconds if timeout is not None))
        self.assertEqual(result["stats"]["ai_candidates_sent"], MAX_AI_CANDIDATES)
        self.assertGreater(result["stats"]["ai_candidates_omitted"], 0)

    def test_ai_timeout_produces_safe_diagnostic(self):
        docx = _docx_bytes(["LOS COMPRADORES: Daniela Campo", "LOS VENDEDORES: Carlos Perez"])
        result = analyze_biblioteca_document(docx, _fields(), ai_classifier=_TimeoutClassifier())

        self.assertEqual(result["diagnostics"]["ai"]["status"], "timeout")
        self.assertEqual(result["status"], "completed_with_ai_timeout")
        self.assertTrue(any(item["field_code"] == "COMPRADOR_1" for item in result["suggestions"]))
        self.assertNotIn("prompt", result["diagnostics"]["ai"])
        self.assertNotIn("token", result["diagnostics"]["ai"])

    def test_provider_error_keeps_deterministic_suggestions(self):
        docx = _docx_bytes(["LOS COMPRADORES: Daniela Campo", "LOS VENDEDORES: Carlos Perez"])
        result = analyze_biblioteca_document(docx, _fields(), ai_classifier=_FailingClassifier())

        self.assertEqual(result["status"], "completed_with_ai_provider_fallback")
        self.assertGreater(result["stats"]["suggestions"], 0)
        self.assertEqual(result["diagnostics"]["ai"]["status"], "provider_error")

    def test_invalid_ai_response_keeps_deterministic_suggestions(self):
        docx = _docx_bytes(["LOS COMPRADORES: Daniela Campo", "LOS VENDEDORES: Carlos Perez"])
        result = analyze_biblioteca_document(docx, _fields(), ai_classifier=_InvalidJsonClassifier())

        self.assertEqual(result["status"], "completed_with_ai_invalid_response")
        self.assertGreater(result["stats"]["suggestions"], 0)
        self.assertEqual(result["diagnostics"]["ai"]["status"], "invalid_json")

    def test_total_timing_stays_under_budget_with_controlled_mocks(self):
        paragraphs = ["LOS COMPRADORES: Daniela Campo"]
        paragraphs.extend([f"LOS VENDEDORES: Carlos Perez comparece {index}" for index in range(250)])
        result = analyze_biblioteca_document(_docx_bytes(paragraphs), _fields(), ai_classifier=_RecordingClassifier())

        self.assertLess(result["timing"]["total_ms"], ANALYSIS_TOTAL_BUDGET_SECONDS * 1000)
        self.assertIn("extraction_ms", result["timing"])
        self.assertIn("deterministic_ms", result["timing"])
        self.assertIn("ai_ms", result["timing"])

    def test_diagnostics_do_not_include_personal_text_or_secrets(self):
        docx = _docx_bytes(["LOS COMPRADORES: Daniela Campo", "LOS VENDEDORES: Carlos Perez"])
        result = analyze_biblioteca_document(docx, _fields(), ai_classifier=_TimeoutClassifier())
        diagnostics = str(result["diagnostics"])

        self.assertNotIn("Daniela", diagnostics)
        self.assertNotIn("Carlos", diagnostics)
        self.assertNotIn("storage_path", diagnostics)
        self.assertNotIn("api_key", diagnostics)
        self.assertNotIn("token", diagnostics.lower())

    def test_valid_suggestions_are_limited_with_declared_omission(self):
        paragraphs = [f"LOS COMPRADORES: Daniela Campo {index}" for index in range(12)]
        result = analyze_biblioteca_document(
            _docx_bytes(paragraphs),
            _fields(),
            ai_classifier=_RecordingClassifier(),
            max_suggestions=5,
        )

        self.assertEqual(result["stats"]["suggestions"], 5)
        self.assertGreater(result["stats"]["omitted_suggestions"], 0)
        self.assertEqual(len(result["suggestions"]), 5)

    def test_large_synthetic_document_returns_operational_deterministic_result(self):
        paragraphs = [
            "INSTRUMENTO PUBLICO",
            "LOS COMPRADORES: Daniela Campo con cedula numero 1.234.567",
            "MATRICULA INMOBILIARIA 050-123456",
            "VALOR DEL ACTO $ 120.000.000 PESOS",
        ]
        paragraphs.extend([f"ENCABEZADO JURIDICO VALOR DEL ACTO {index}" for index in range(200)])
        paragraphs.extend([f"LOS VENDEDORES: Carlos Perez comparece {index}" for index in range(120)])
        classifier = _RecordingClassifier()
        result = analyze_biblioteca_document(_docx_bytes(paragraphs), _fields(), ai_classifier=classifier)

        self.assertEqual(classifier.calls, 1)
        self.assertLessEqual(classifier.batch_sizes[0], MAX_AI_CANDIDATES)
        self.assertGreater(result["stats"]["suggestions"], 0)
        self.assertLessEqual(result["stats"]["suggestions"], 120)
        self.assertTrue(any(item["source"] == "deterministic" for item in result["suggestions"]))

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
