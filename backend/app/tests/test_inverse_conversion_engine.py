from __future__ import annotations

import contextlib
import io
import json
import os
import unittest
from unittest import mock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes.inverse_conversion_engine import router as engine_router
from app.core.deps import get_db
from app.models.base import Base
from app.services.minuta.inverse_conversion_catalog.models import (
    CorpusDocument,
    CorpusDocumentField,
    FieldAlias,
    FieldDefinition,
    FieldPattern,
)
from app.services.minuta.inverse_conversion_engine.graph import build_inverse_conversion_graph
from app.services.minuta.inverse_conversion_engine.models import (
    EngineCandidate,
    EngineOptions,
    InverseConversionCandidateRow,
    InverseConversionEmbedding,
    InverseConversionRun,
    InverseConversionRunStep,
)
from app.services.minuta.inverse_conversion_engine.nodes import EngineNodes
from app.services.minuta.inverse_conversion_engine.service import InverseConversionEngineService
from app.services.minuta.inverse_conversion_engine.state import InverseConversionState


TABLES = [
    FieldDefinition.__table__,
    FieldAlias.__table__,
    CorpusDocument.__table__,
    CorpusDocumentField.__table__,
    FieldPattern.__table__,
    InverseConversionEmbedding.__table__,
    InverseConversionRun.__table__,
    InverseConversionRunStep.__table__,
    InverseConversionCandidateRow.__table__,
]


class InverseConversionEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine, tables=TABLES)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()
        self._seed()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine, tables=TABLES)
        self.engine.dispose()

    def _seed(self):
        self.db.add_all(
            [
                FieldDefinition(field_code="NUMERO_MATRICULA", display_name="Numero Matricula", status="suggested", confidence=0.9),
                FieldDefinition(field_code="VALOR_VENTA", display_name="Valor Venta", status="suggested", confidence=0.9),
                FieldDefinition(field_code="NUMERO_DOCUMENTO_COMPRADOR", display_name="Numero Documento Comprador", status="suggested", confidence=0.8),
                FieldDefinition(field_code="TIPO_DOCUMENTO_COMPRADOR", display_name="Tipo Documento Comprador", status="suggested", confidence=0.8),
            ]
        )
        self.db.add(FieldAlias(raw_field_code="VALOR_DE_LA_VENTA_EN_NUMEROS", canonical_field_code="VALOR_VENTA", frequency=7, status="suggested"))
        doc = CorpusDocument(filename="fixture.docx", source_path="fixture.docx", marker_count=4, processing_status="suggested", is_tagged=True)
        self.db.add(doc)
        self.db.flush()
        self.db.add_all(
            [
                CorpusDocumentField(corpus_document_id=doc.id, raw_field_code="NUMERO_MATRICULA", occurrences=2, status="draft"),
                CorpusDocumentField(
                    corpus_document_id=doc.id,
                    raw_field_code="VALOR_DE_LA_VENTA_EN_NUMEROS",
                    canonical_field_code="VALOR_VENTA",
                    occurrences=2,
                    status="draft",
                ),
            ]
        )
        self.db.add_all(
            [
                FieldPattern(
                    raw_field_code="NUMERO_MATRICULA",
                    canonical_field_code="NUMERO_MATRICULA",
                    text_before="MATRICULA:",
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
                    raw_field_code="TIPO_DOCUMENTO_COMPRADOR",
                    canonical_field_code="TIPO_DOCUMENTO_COMPRADOR",
                    text_before="COMPRADOR:",
                    text_after="- {{NUMERO_DOCUMENTO_COMPRADOR}}",
                    frequency=1,
                    confidence=0.7,
                    status="draft",
                ),
            ]
        )
        self.db.commit()

    def test_langgraph_builds_valid_graph(self):
        graph = build_inverse_conversion_graph(EngineNodes(self.db, EngineOptions(persist_audit=False)))
        self.assertTrue(hasattr(graph, "invoke"))

    def test_analyze_marker_works_without_llm(self):
        result = InverseConversionEngineService(self.db).analyze_marker(
            "NUMERO_MATRICULA",
            "MATRICULA:",
            "DEL INMUEBLE",
            options=EngineOptions(use_llm=False, persist_audit=False),
        )
        self.assertEqual(result.status, "completed")
        self.assertTrue(any(candidate.canonical_field_code == "NUMERO_MATRICULA" for candidate in result.candidates))

    def test_analyze_marker_accepts_langgraph_dict_state(self):
        candidate = EngineCandidate(
            raw_marker="NUMERO_MATRICULA",
            candidate_field_code="NUMERO_MATRICULA",
            canonical_field_code="NUMERO_MATRICULA",
            confidence_score=0.91,
            status="needs_human_review",
            evidence={"source": "test"},
            warnings=("review_required:Manual review required",),
            requires_human_review=True,
        )

        def run_as_dict(state):
            return {
                **state.__dict__,
                "validated_candidates": [candidate.to_dict()],
                "warnings": ["llm_disabled"],
                "errors": [],
                "requires_human_review": True,
                "final_result": {"metadata": {"source": "mock_langgraph"}},
            }

        with mock.patch(
            "app.services.minuta.inverse_conversion_engine.service.InverseConversionOrchestrator.run",
            side_effect=run_as_dict,
        ):
            result = InverseConversionEngineService(self.db).analyze_marker(
                "NUMERO_MATRICULA",
                "MATRICULA:",
                "DEL INMUEBLE",
                options=EngineOptions(use_llm=False, persist_audit=False),
            )

        self.assertEqual(result.status, "completed")
        self.assertEqual(len(result.candidates), 1)
        self.assertEqual(result.candidates[0].canonical_field_code, "NUMERO_MATRICULA")
        self.assertIn("llm_disabled", result.warnings)
        self.assertEqual(result.metadata["source"], "mock_langgraph")

    def test_analyze_text_works_without_llm(self):
        result = InverseConversionEngineService(self.db).analyze_text(
            "El inmueble tiene {{NUMERO_MATRICULA}} DEL INMUEBLE",
            options=EngineOptions(use_llm=False, persist_audit=False),
        )
        self.assertTrue(result.candidates)
        self.assertIn("llm_disabled", result.warnings)

    def test_missing_api_key_does_not_break(self):
        old_value = os.environ.pop("OPENAI_API_KEY", None)
        try:
            result = InverseConversionEngineService(self.db).analyze_marker(
                "VALOR_VENTA",
                "VALOR DEL ACTO: $",
                "MONEDA CORRIENTE",
                options=EngineOptions(use_llm=True, persist_audit=False),
            )
        finally:
            if old_value is not None:
                os.environ["OPENAI_API_KEY"] = old_value
        self.assertEqual(result.status, "completed")
        self.assertIn("llm_disabled", result.warnings)

    def test_lexical_rag_is_always_used(self):
        state = InverseConversionState(raw_marker="NUMERO_MATRICULA", context_before="MATRICULA:", context_after="DEL INMUEBLE")
        nodes = EngineNodes(self.db, EngineOptions(use_semantic=False, persist_audit=False))
        state = nodes.extract_contexts(state)
        state = nodes.retrieve_lexical_evidence(state)
        self.assertGreater(len(state.lexical_evidence), 0)

    def test_semantic_rag_degrades_without_embeddings(self):
        result = InverseConversionEngineService(self.db).analyze_marker(
            "NUMERO_MATRICULA",
            "MATRICULA:",
            "DEL INMUEBLE",
            options=EngineOptions(use_semantic=True, persist_audit=False),
        )
        self.assertIn("semantic_embeddings_unavailable_using_lexical_fallback", result.warnings)

    def test_audit_registers_run_and_steps_in_engine_tables(self):
        result = InverseConversionEngineService(self.db).analyze_marker("NUMERO_MATRICULA", "MATRICULA:", "DEL INMUEBLE")
        self.assertIsNotNone(result.run_id)
        self.assertGreater(self.db.query(InverseConversionRunStep).filter_by(run_id=result.run_id).count(), 0)
        self.assertGreaterEqual(self.db.query(InverseConversionCandidateRow).filter_by(run_id=result.run_id).count(), 1)

    def test_cli_prints_json(self):
        import scripts.run_inverse_conversion_engine as cli

        cli_session = self.Session()
        original = cli.SessionLocal
        cli.SessionLocal = lambda: cli_session
        try:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                with mock.patch(
                    "sys.argv",
                    ["run_inverse_conversion_engine.py", "--marker", "NUMERO_MATRICULA", "--before", "MATRICULA:", "--after", "DEL INMUEBLE", "--no-audit"],
                ):
                    self.assertEqual(cli.main(), 0)
            payload = json.loads(stdout.getvalue())
        finally:
            cli.SessionLocal = original
            cli_session.close()
        self.assertEqual(payload["status"], "completed")

    def test_endpoint_responds_when_registered(self):
        app = FastAPI()
        app.include_router(engine_router)

        def override_db():
            try:
                yield self.db
            finally:
                pass

        app.dependency_overrides[get_db] = override_db
        response = TestClient(app).post(
            "/inverse-conversion/analyze",
            json={"marker": "NUMERO_MATRICULA", "context_before": "MATRICULA:", "context_after": "DEL INMUEBLE", "options": {"persist_audit": False}},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "completed")

    def test_no_traditional_tables_are_modified_by_no_audit_analysis(self):
        before = self.db.execute(text("select count(*) from field_definitions")).scalar()
        InverseConversionEngineService(self.db).analyze_marker(
            "NUMERO_MATRICULA",
            "MATRICULA:",
            "DEL INMUEBLE",
            options=EngineOptions(persist_audit=False),
        )
        after = self.db.execute(text("select count(*) from field_definitions")).scalar()
        self.assertEqual(before, after)

    def test_no_llm_call_when_use_llm_false(self):
        with mock.patch("app.services.minuta.inverse_conversion_engine.pydantic_ai_client.PydanticAIProposalClient.propose") as propose:
            propose.return_value.proposals = []
            propose.return_value.warnings = ["mocked"]
            InverseConversionEngineService(self.db).analyze_marker(
                "NUMERO_MATRICULA",
                "MATRICULA:",
                "DEL INMUEBLE",
                options=EngineOptions(use_llm=False, persist_audit=False),
            )
            propose.assert_called()


if __name__ == "__main__":
    unittest.main()
