from __future__ import annotations

import contextlib
import io
import json
import unittest
from unittest import mock

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.services.minuta.inverse_conversion_catalog.models import (
    CorpusDocument,
    CorpusDocumentField,
    FieldAlias,
    FieldDefinition,
    FieldPattern,
)
from app.services.minuta.inverse_conversion_rag.evidence_builder import EvidenceBuilder
from app.services.minuta.inverse_conversion_rag.repository import InverseConversionReadOnlyRepository, ReadOnlyViolation
from app.services.minuta.inverse_conversion_rag.retriever import InverseConversionRetriever
from app.services.minuta.inverse_conversion_rag.ranker import InverseConversionRanker


CATALOG_TABLES = [
    FieldDefinition.__table__,
    FieldAlias.__table__,
    CorpusDocument.__table__,
    CorpusDocumentField.__table__,
    FieldPattern.__table__,
]


class InverseConversionRagTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine, tables=CATALOG_TABLES)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()
        self._seed()
        self.repository = InverseConversionReadOnlyRepository(self.db)
        self.retriever = InverseConversionRetriever(self.repository)

    def tearDown(self):
        self.repository.close()
        self.db.close()
        Base.metadata.drop_all(self.engine, tables=CATALOG_TABLES)
        self.engine.dispose()

    def _seed(self) -> None:
        definitions = [
            FieldDefinition(field_code="NUMERO_MATRICULA", display_name="Numero Matricula", status="suggested", confidence=0.8),
            FieldDefinition(field_code="VALOR_VENTA", display_name="Valor Venta", status="suggested", confidence=0.9),
            FieldDefinition(field_code="NUMERO_DOCUMENTO_COMPRADOR", display_name="Numero Documento Comprador", status="suggested", confidence=0.8),
            FieldDefinition(field_code="TIPO_DOCUMENTO_COMPRADOR", display_name="Tipo Documento Comprador", status="suggested", confidence=0.8),
            FieldDefinition(field_code="CAMPO_CONFLICTO", display_name="Campo Conflicto", status="conflict", confidence=0.3),
        ]
        self.db.add_all(definitions)
        self.db.flush()

        aliases = [
            FieldAlias(raw_field_code="VALOR_DE_LA_VENTA_EN_NUMEROS", canonical_field_code="VALOR_VENTA", frequency=10, status="suggested"),
            FieldAlias(raw_field_code="EN_NUMEROS_VALOR_DE_LA_VENTA", canonical_field_code="VALOR_VENTA", frequency=9, status="suggested"),
            FieldAlias(raw_field_code="ALIAS_CONFLICTO", canonical_field_code="CAMPO_CONFLICTO", frequency=2, status="conflict"),
        ]
        self.db.add_all(aliases)

        doc = CorpusDocument(
            filename="minuta.docx",
            source_path="fixtures/minuta.docx",
            document_type="docx",
            is_tagged=True,
            marker_count=4,
            processing_status="suggested",
        )
        self.db.add(doc)
        self.db.flush()

        self.db.add_all(
            [
                CorpusDocumentField(corpus_document_id=doc.id, raw_field_code="NUMERO_MATRICULA", occurrences=3, status="draft"),
                CorpusDocumentField(corpus_document_id=doc.id, raw_field_code="VALOR_DE_LA_VENTA_EN_NUMEROS", canonical_field_code="VALOR_VENTA", occurrences=2, status="draft"),
                CorpusDocumentField(corpus_document_id=doc.id, raw_field_code="NUMERO_DOCUMENTO_COMPRADOR", occurrences=1, status="draft"),
                CorpusDocumentField(corpus_document_id=doc.id, raw_field_code="TIPO_DOCUMENTO_COMPRADOR", occurrences=1, status="draft"),
            ]
        )
        self.db.add_all(
            [
                FieldPattern(
                    raw_field_code="NUMERO_MATRICULA",
                    canonical_field_code="NUMERO_MATRICULA",
                    text_before="MATRICULA INMOBILIARIA:",
                    text_after="DEL INMUEBLE",
                    frequency=3,
                    confidence=0.8,
                    status="draft",
                ),
                FieldPattern(
                    raw_field_code="VALOR_DE_LA_VENTA_EN_NUMEROS",
                    canonical_field_code="VALOR_VENTA",
                    text_before="VALOR DEL ACTO: $",
                    text_after="MONEDA CORRIENTE",
                    frequency=2,
                    confidence=0.8,
                    status="draft",
                ),
                FieldPattern(
                    raw_field_code="NUMERO_DOCUMENTO_COMPRADOR",
                    canonical_field_code="NUMERO_DOCUMENTO_COMPRADOR",
                    text_before="COMPRADOR: {{NOMBRE_COMPRADOR}} - {{TIPO_DOCUMENTO_COMPRADOR}} -",
                    text_after="[[--]]",
                    frequency=1,
                    confidence=0.7,
                    status="draft",
                ),
                FieldPattern(
                    raw_field_code="TIPO_DOCUMENTO_COMPRADOR",
                    canonical_field_code="TIPO_DOCUMENTO_COMPRADOR",
                    text_before="COMPRADOR: {{NOMBRE_COMPRADOR}} -",
                    text_after="- {{NUMERO_DOCUMENTO_COMPRADOR}}",
                    frequency=1,
                    confidence=0.7,
                    status="draft",
                ),
            ]
        )
        self.db.commit()

    def test_repository_blocks_write_statements(self):
        with self.assertRaises(ReadOnlyViolation):
            self.db.execute(text("insert into field_definitions (field_code, status, confidence, metadata_json) values ('X', 'suggested', 0, '{}')"))

    def test_retrieve_by_field_code_finds_numero_matricula_patterns(self):
        result = self.retriever.retrieve_by_field_code("NUMERO_MATRICULA", limit=5)

        self.assertGreaterEqual(result.total_candidates, 1)
        self.assertEqual(result.candidates[0].canonical_field_code, "NUMERO_MATRICULA")
        self.assertTrue(any("MATRICULA INMOBILIARIA" in (pattern.text_before or "") for pattern in result.candidates[0].matched_patterns))

    def test_retrieve_by_field_code_finds_aliases_to_valor_venta(self):
        result = self.retriever.retrieve_by_field_code("VALOR_VENTA", limit=5)
        first = result.candidates[0]

        self.assertEqual(first.canonical_field_code, "VALOR_VENTA")
        self.assertIn("VALOR_DE_LA_VENTA_EN_NUMEROS", first.matched_aliases)

    def test_retrieve_by_text_context_uses_tokens(self):
        result = self.retriever.retrieve_by_text_context("valor del acto moneda corriente", limit=5)

        self.assertTrue(any(candidate.canonical_field_code == "VALOR_VENTA" for candidate in result.candidates))

    def test_retrieve_by_before_after_uses_context(self):
        result = self.retriever.retrieve_by_before_after("COMPRADOR:", "- {{NUMERO_DOCUMENTO_COMPRADOR", limit=5)

        self.assertTrue(any(candidate.canonical_field_code == "TIPO_DOCUMENTO_COMPRADOR" for candidate in result.candidates))

    def test_ranker_prioritizes_exact_match_over_similarity(self):
        ranker = InverseConversionRanker()

        exact_score, _, _ = ranker.score_candidate("NUMERO_MATRICULA", query_field_code="NUMERO_MATRICULA", frequency=1)
        similar_score, _, _ = ranker.score_candidate("NUMERO_DOCUMENTO_COMPRADOR", query_field_code="NUMERO_MATRICULA", frequency=20)

        self.assertGreater(exact_score, similar_score)

    def test_ranker_penalizes_conflict(self):
        ranker = InverseConversionRanker()

        suggested_score, _, _ = ranker.score_candidate("VALOR_VENTA", query_field_code="VALOR_VENTA", frequency=1, status="suggested")
        conflict_score, _, warnings = ranker.score_candidate("VALOR_VENTA", query_field_code="VALOR_VENTA", frequency=1, status="conflict")

        self.assertGreater(suggested_score, conflict_score)
        self.assertIn("candidate_status_conflict", warnings)

    def test_ranker_does_not_mix_tipo_documento_with_numero_documento(self):
        score, _, warnings = InverseConversionRanker().score_candidate(
            "TIPO_DOCUMENTO_COMPRADOR",
            query_field_code="NUMERO_DOCUMENTO_COMPRADOR",
            frequency=50,
        )

        self.assertIn("different_semantic_category", warnings)
        self.assertLess(score, 50)

    def test_evidence_builder_returns_auditable_structure(self):
        result = self.retriever.retrieve_by_field_code("NUMERO_MATRICULA", limit=1)
        evidence = result.candidates[0]

        self.assertEqual(evidence.canonical_field_code, "NUMERO_MATRICULA")
        self.assertIsInstance(evidence.confidence_score, float)
        self.assertTrue(evidence.source_documents)
        self.assertTrue(evidence.matched_patterns)
        self.assertTrue(evidence.reasons)

    def test_cli_outputs_json_with_mocked_db(self):
        import scripts.query_inverse_conversion_rag as cli

        cli_session = self.Session()
        original = cli.SessionLocal
        cli.SessionLocal = lambda: cli_session
        try:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                cli_args = ["--field-code", "NUMERO_MATRICULA", "--limit", "1"]
                with mock.patch("sys.argv", ["query_inverse_conversion_rag.py", *cli_args]):
                    self.assertEqual(cli.main(), 0)
            payload = json.loads(stdout.getvalue())
        finally:
            cli.SessionLocal = original
            cli_session.close()

        self.assertEqual(payload["metadata"]["mode"], "field_code")
        self.assertEqual(payload["candidates"][0]["canonical_field_code"], "NUMERO_MATRICULA")

    def test_module_does_not_call_llm(self):
        module_root = __import__("pathlib").Path(__file__).resolve().parents[1] / "services" / "minuta" / "inverse_conversion_rag"
        content = "\n".join(path.read_text(encoding="utf-8").lower() for path in module_root.glob("*.py"))

        self.assertNotIn("openai", content)
        self.assertNotIn("llm", content)

    def test_retrieval_does_not_modify_database(self):
        before = self.db.query(FieldDefinition).count(), self.db.query(FieldAlias).count(), self.db.query(FieldPattern).count()

        self.retriever.retrieve_by_field_code("VALOR_VENTA", limit=5)
        self.retriever.retrieve_by_text_context("comprador matricula", limit=5)

        after = self.db.query(FieldDefinition).count(), self.db.query(FieldAlias).count(), self.db.query(FieldPattern).count()
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
