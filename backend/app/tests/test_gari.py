from __future__ import annotations

import importlib
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - load all model metadata for create_all
from app.core.deps import get_current_user, get_db
from app.models.base import Base
from app.models.case import Case
from app.models.case_act_data import CaseActData
from app.models.notary import Notary
from app.models.user import User

escritura_router_module = importlib.import_module("app.modules.escritura.router")


def _auth_user(user_id: int = 1, notary_id: int = 1, role_code: str = "protocolist"):
    return SimpleNamespace(
        id=user_id,
        default_notary_id=notary_id,
        role_assignments=[
            SimpleNamespace(
                notary_id=notary_id if role_code != "super_admin" else None,
                role=SimpleNamespace(code=role_code),
            )
        ],
    )


class FakeGariClient:
    model_version = "fake-gari-2026-07-21"

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def complete_json(self, *, purpose: str, prompt: str):
        self.calls.append((purpose, prompt))
        if purpose == "extraccion":
            return {
                "sugerencias": {
                    "matricula": {
                        "valor": "001-123456",
                        "confianza": 0.94,
                        "fuente": "FOLIO DE MATRICULA INMOBILIARIA 001-123456",
                    }
                }
            }
        if purpose == "clasificacion":
            return {"acto_sugerido": "hipoteca", "ramas": ["hipoteca", "propiedad_horizontal", "rama_inventada"]}
        if purpose == "revision":
            return {
                "hallazgos": [
                    {
                        "tipo": "faltante",
                        "detalle": "Falta dejar constancia de indagacion sobre afectacion a vivienda familiar.",
                        "cita_slug": "modelo-no-puede-fijar-cita",
                    }
                ]
            }
        return {}

    def complete_text(self, *, purpose: str, prompt: str):
        self.calls.append((purpose, prompt))
        return '<p class="cl"><span class="clh">PARAGRAFO.</span> El saldo se pagara al desembolso autorizado.</p><span class="cite">cita inventada</span>'


class GariEscrituraTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = sa.create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.fake_llm = FakeGariClient()
        self._seed_db()

        app = FastAPI()
        app.include_router(escritura_router_module.router, prefix="/api/v1")

        def override_get_db():
            session = self.Session()
            try:
                yield session
            finally:
                session.close()

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = lambda: _auth_user()
        app.dependency_overrides[escritura_router_module.get_gari_llm_client] = lambda: self.fake_llm
        self.app = app
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.client.close()
        self.app.dependency_overrides.clear()
        self.engine.dispose()

    def _seed_db(self) -> None:
        with self.Session() as session:
            session.add_all(
                [
                    Notary(
                        id=1,
                        slug="notaria-16",
                        catalog_identity_key="notaria-16-medellin",
                        commercial_name="Notaria 16",
                        legal_name="Notaria 16 de Medellin",
                        municipality="Medellin",
                        notary_label="Notaria 16 de Medellin",
                        city="Medellin",
                        email="n16@example.test",
                    ),
                    Notary(
                        id=2,
                        slug="notaria-17",
                        catalog_identity_key="notaria-17-medellin",
                        commercial_name="Notaria 17",
                        legal_name="Notaria 17 de Medellin",
                        municipality="Medellin",
                        notary_label="Notaria 17 de Medellin",
                        city="Medellin",
                        email="n17@example.test",
                    ),
                    User(
                        id=1,
                        email="protocolista@example.test",
                        full_name="Protocolista Test",
                        password_hash="not-used",
                        default_notary_id=1,
                    ),
                ]
            )
            session.add_all(
                [
                    Case(
                        id=100,
                        notary_id=1,
                        case_type="escritura",
                        act_type="compraventa",
                        consecutive=1,
                        year=2026,
                        internal_case_number="N16-2026-0001",
                        current_state="borrador",
                        current_owner_user_id=1,
                        metadata_json="{}",
                    ),
                    Case(
                        id=200,
                        notary_id=2,
                        case_type="escritura",
                        act_type="compraventa",
                        consecutive=2,
                        year=2026,
                        internal_case_number="N17-2026-0002",
                        current_state="borrador",
                        metadata_json="{}",
                    ),
                    CaseActData(
                        case_id=100,
                        data_json='{"fechaOtorg":"2026-08-14"}',
                        gari_draft_text="Texto de escritura con compraventa y vivienda familiar.",
                    ),
                ]
            )
            session.commit()

    def test_extraer_devuelve_sugerencias_por_validar_sin_sobrescribir(self):
        response = self.client.post(
            "/api/v1/escritura/cases/100/extraer",
            files={"archivo": ("certificado.txt", b"FOLIO DE MATRICULA INMOBILIARIA 001-123456", "text/plain")},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["por_validar"])
        self.assertEqual(payload["estado"], "por validar")
        self.assertEqual(payload["sugerencias"]["matricula"]["valor"], "001-123456")
        with self.Session() as session:
            state = session.scalar(sa.select(CaseActData.data_json).where(CaseActData.case_id == 100))
            self.assertEqual(state, '{"fechaOtorg":"2026-08-14"}')

    def test_extraer_respeta_scoping_por_caso(self):
        response = self.client.post(
            "/api/v1/escritura/cases/200/extraer",
            files={"archivo": ("certificado.txt", b"texto", "text/plain")},
        )

        self.assertEqual(response.status_code, 403)

    def test_redaccion_prosa_devuelve_html_sugerido_editable(self):
        response = self.client.post(
            "/api/v1/escritura/redaccion/prosa",
            json={"acto": "compraventa", "contexto": {"saldo": 1000000}, "instruccion": "Redacta forma de pago atipica."},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["sugerencia"])
        self.assertEqual(payload["estado"], "por validar")
        self.assertIn('class="cl"', payload["html_sugerido"])
        self.assertNotIn("cite", payload["html_sugerido"])

    def test_clasificar_devuelve_acto_y_ramas_permitidas(self):
        response = self.client.post(
            "/api/v1/escritura/clasificar",
            json={"descripcion": "Compra con credito hipotecario sobre apartamento en propiedad horizontal."},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["sugerencia"])
        self.assertEqual(payload["acto_sugerido"], "hipoteca")
        self.assertEqual(payload["ramas"], ["hipoteca", "propiedad_horizontal"])

    def test_revisor_cita_desde_rag_no_desde_modelo(self):
        rag_hit = SimpleNamespace(
            source_ref="ley-258-1996-art-6",
            titulo="Ley 258/1996 art. 6",
            chunk_text="El notario debe indagar sobre afectacion a vivienda familiar.",
        )

        with patch.object(escritura_router_module, "buscar_corpus", return_value=[rag_hit]) as rag_mock:
            response = self.client.post(
                "/api/v1/escritura/cases/100/revisar",
                json={"acto": "compraventa", "html": "<p>Texto sin constancia Ley 258</p>"},
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["sugerencia"])
        self.assertEqual(payload["hallazgos"][0]["cita_slug"], "ley-258-1996-art-6")
        self.assertNotEqual(payload["hallazgos"][0]["cita_slug"], "modelo-no-puede-fijar-cita")
        self.assertGreaterEqual(rag_mock.call_count, 1)


if __name__ == "__main__":
    unittest.main()
