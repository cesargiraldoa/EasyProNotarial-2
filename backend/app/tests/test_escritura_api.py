from __future__ import annotations

from datetime import date
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
from app.models.case_document import CaseDocument
from app.models.case_document_version import CaseDocumentVersion
from app.models.legal_embedding import LegalEmbedding
from app.models.notary import Notary
from app.models.user import User
from app.modules.escritura.router import router as escritura_router
from app.services.escritura_reglas import evaluar_reglas
from app.services.legal_rag import HashLegalEmbeddingProvider, seed_legal_embeddings
from app.seeds.seed_corpus import seed_corpus


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


def _valid_compraventa_state() -> dict:
    return {
        "fechaOtorg": "2026-08-14",
        "matricula": "001-123456",
        "linderos": "Norte con la calle 1; Sur con el lote 2.",
        "inmdesc": "Apartamento destinado a vivienda urbana con area de 72 metros cuadrados.",
        "declaracion_precio_real": "incluida",
        "afect": "no",
        "gravamen": "libre",
        "total": 420000000,
        "V": [{"tipo": "natural", "nombre": "VENDEDOR TEST"}],
        "C": [{"tipo": "natural", "nombre": "COMPRADOR TEST"}],
    }


class EscrituraApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = sa.create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)
        self._seed_db()

        app = FastAPI()
        app.include_router(escritura_router, prefix="/api/v1")

        def override_get_db():
            session = self.Session()
            try:
                yield session
            finally:
                session.close()

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = lambda: _auth_user()
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
                ]
            )
            seed_corpus(session)
            seed_legal_embeddings(session, provider=HashLegalEmbeddingProvider())
            session.commit()

    def test_corpus_por_fecha_excluye_norma_inexequible(self):
        response = self.client.get("/api/v1/escritura/corpus?acto=compraventa&fecha=2026-08-14")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        slugs = {item["slug"] for item in payload["normas"]}
        self.assertIn("ley-258-1996-art-3", slugs)
        self.assertIn("ley-1579-2012-art-8", slugs)
        self.assertIn("ley-223-1995-art-231", slugs)
        self.assertIn("estatuto-tributario-art-90", slugs)
        self.assertNotIn("decreto-ley-2106-2019-arts-59-63", slugs)

    def test_put_get_estado_round_trip_data_json(self):
        state = {
            "precio": 420000000,
            "vendedores": [{"nombre": "Rodrigo Elias", "cuota": 50}],
            "opciones": {"ph": True, "vis": "no"},
        }

        saved = self.client.put("/api/v1/escritura/cases/100", json={"acto": "compraventa", "state": state})
        loaded = self.client.get("/api/v1/escritura/cases/100")

        self.assertEqual(saved.status_code, 200)
        self.assertEqual(loaded.status_code, 200)
        self.assertEqual(saved.json()["state"], state)
        self.assertEqual(loaded.json()["state"], state)
        self.assertEqual(loaded.json()["case"]["id"], 100)

    def test_post_documento_crea_version_docx(self):
        saved = self.client.put("/api/v1/escritura/cases/100", json={"acto": "compraventa", "state": _valid_compraventa_state()})
        self.assertEqual(saved.status_code, 200)
        html = """
        <div>
          <p><span class="clh">PRIMERO:</span> Texto de la escritura<span class="cite">Ley 1</span><span class="fill">-----</span></p>
          <p>SEGUNDO: Otra clausula.</p>
        </div>
        """

        with patch("app.services.document_persistence.save_case_file", return_value=("escritura_test.docx", "memory://case-100/escritura_test.docx")):
            response = self.client.post(
                "/api/v1/escritura/cases/100/documento",
                json={
                    "acto": "compraventa",
                    "html": html,
                    "filename": "escritura_test.docx",
                    "cumplimiento_bloqueantes": 0,
                },
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["version_number"], 1)
        self.assertEqual(payload["file_format"], "docx")
        self.assertEqual(payload["storage_path"], "memory://case-100/escritura_test.docx")

        with self.Session() as session:
            self.assertEqual(session.query(CaseDocument).filter(CaseDocument.case_id == 100, CaseDocument.category == "escritura").count(), 1)
            self.assertEqual(session.query(CaseDocumentVersion).count(), 1)

    def test_post_documento_con_bloqueantes_responde_409_sin_version(self):
        state = _valid_compraventa_state()
        state["matricula"] = ""
        saved = self.client.put("/api/v1/escritura/cases/100", json={"acto": "compraventa", "state": state})
        self.assertEqual(saved.status_code, 200)
        response = self.client.post(
            "/api/v1/escritura/cases/100/documento",
            json={
                "acto": "compraventa",
                "html": "<p>Texto suficiente</p>",
                "cumplimiento_bloqueantes": 0,
            },
        )

        self.assertEqual(response.status_code, 409)
        detail = response.json()["detail"]
        self.assertEqual(detail["message"], "hay bloqueantes por resolver")
        self.assertIn("compraventa_matricula_obligatoria", {item["codigo"] for item in detail["bloqueantes"]})
        with self.Session() as session:
            self.assertEqual(session.query(CaseDocumentVersion).count(), 0)

    def test_buscar_corpus_filtra_por_vigencia(self):
        response = self.client.get("/api/v1/escritura/corpus/buscar?q=afectacion vivienda familiar&acto=compraventa&fecha=2026-08-14&top_k=20")

        self.assertEqual(response.status_code, 200)
        refs = {item["source_ref"] for item in response.json()["hits"]}
        self.assertIn("ley-258-1996-art-3", refs)

        old_response = self.client.get("/api/v1/escritura/corpus/buscar?q=decreto 0732 sexo variables&acto=compraventa&fecha=2025-12-31&top_k=20")
        self.assertEqual(old_response.status_code, 200)
        old_refs = {item["source_ref"] for item in old_response.json()["hits"]}
        self.assertNotIn("decreto-0732-2026", old_refs)

        with self.Session() as session:
            before = session.query(LegalEmbedding).count()
            seed_legal_embeddings(session, provider=HashLegalEmbeddingProvider())
            after = session.query(LegalEmbedding).count()
            self.assertEqual(before, after)

    def test_biblioteca_endpoint_devuelve_clausulas_vigentes(self):
        response = self.client.get("/api/v1/escritura/biblioteca?acto=compraventa&fecha=2026-08-14")

        self.assertEqual(response.status_code, 200)
        titles = {item["titulo"] for item in response.json()}
        self.assertIn("Nota - REDAM", titles)

    def test_evaluador_reglas_corpus_interpreta_condiciones_del_state(self):
        with self.Session() as session:
            state = _valid_compraventa_state()
            state.update(
                {
                    "gravamen": "embargo",
                    "activo": "casa_o_apartamento_habitacion",
                    "exencion_uvt": "5000",
                    "requiere_cuenta_afc": True,
                    "destino_admitido": "otra_vivienda",
                    "tope_valor_catastral_eliminado": True,
                }
            )
            hallazgos = evaluar_reglas(session, "compraventa", date(2026, 8, 14), state)

        codigos = {item.codigo for item in hallazgos}
        self.assertIn("compraventa_medida_cautelar_embargo", codigos)
        self.assertIn("compraventa_exencion_casa_habitacion_5000_uvt_afc", codigos)

    def test_evaluador_reglas_corpus_ramas_comunes_compraventa(self):
        with self.Session() as session:
            state = _valid_compraventa_state()
            state.update(
                {
                    "inmuebles": [
                        {
                            "descripcion": "Apartamento 101",
                            "matricula": "001-123456",
                            "linderos": "Norte con la calle 1.",
                            "catastral": "050010101",
                            "nupre": "AAA001",
                        },
                        {
                            "descripcion": "Parqueadero 12",
                            "matricula": "",
                            "linderos": "",
                            "catastral": "050010102",
                            "nupre": "AAA002",
                        },
                    ],
                    "folioEstado": "falsa_tradicion",
                    "encadenamientos": {
                        "cancelacionHipotecaPrevia": True,
                        "cancelacionPatrimonioFamilia": True,
                        "afectacionViviendaFamiliar": True,
                    },
                }
            )
            hallazgos = evaluar_reglas(session, "compraventa", date(2026, 8, 14), state)

        codigos = {item.codigo for item in hallazgos}
        self.assertIn("compraventa_varios_inmuebles_identificacion_individual", codigos)
        self.assertIn("compraventa_varios_inmuebles_clausula_enumera_folios", codigos)
        self.assertIn("compraventa_estado_folio_especial_advertencia_1579", codigos)
        self.assertIn("compraventa_falsa_tradicion_advertencia_saneamiento", codigos)
        self.assertIn("compraventa_encadena_cancelacion_hipoteca_previa", codigos)
        self.assertIn("compraventa_encadena_cancelacion_patrimonio_familia", codigos)
        self.assertIn("compraventa_encadena_afectacion_vivienda_familiar", codigos)

        bloqueantes = {item.codigo for item in hallazgos if item.severidad == "BLOCK"}
        self.assertIn("compraventa_varios_inmuebles_identificacion_individual", bloqueantes)

    def test_case_inexistente_responde_404(self):
        response = self.client.get("/api/v1/escritura/cases/999")

        self.assertEqual(response.status_code, 404)

    def test_case_de_otra_notaria_responde_403(self):
        response = self.client.get("/api/v1/escritura/cases/200")

        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
