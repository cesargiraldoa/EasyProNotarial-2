from types import SimpleNamespace
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.v1.endpoints.biblioteca import list_field_catalog
from app.main import FlexibleCORSMiddleware, app as main_app
from app.models.base import Base
from app.models.notary import Notary  # noqa: F401 - needed for notarial_field_catalog FK metadata
from app.models.notarial_field_catalog import NotarialFieldCatalog


ONLYOFFICE_ORIGIN = "https://onlyoffice.easypronotarial.com"


def _cors_client() -> TestClient:
    app = FastAPI()
    app.add_middleware(FlexibleCORSMiddleware)

    @app.get("/ok")
    def ok():
        return {"ok": True}

    return TestClient(app)


class BibliotecaCorsAuthTests(unittest.TestCase):
    def test_onlyoffice_origin_can_send_authorization_header(self):
        response = _cors_client().options(
            "/ok",
            headers={
                "Origin": ONLYOFFICE_ORIGIN,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Authorization",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["access-control-allow-origin"], ONLYOFFICE_ORIGIN)
        self.assertIn("Authorization", response.headers["access-control-allow-headers"])

    def test_unknown_origin_is_not_opened_by_cors(self):
        response = _cors_client().options(
            "/ok",
            headers={
                "Origin": "https://attacker.example",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Authorization",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertNotIn("access-control-allow-origin", response.headers)

    def test_biblioteca_campos_requires_authentication(self):
        response = TestClient(main_app).get(
            "/api/v1/biblioteca/campos",
            headers={"Origin": ONLYOFFICE_ORIGIN},
        )

        self.assertEqual(response.status_code, 401)

    def test_field_catalog_keeps_global_and_notary_scope(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        try:
            db.add_all(
                [
                    NotarialFieldCatalog(
                        code="GLOBAL_FIELD",
                        label="Global",
                        field_type="text",
                        category="persona",
                        scope="global",
                        notary_id=None,
                        is_active=True,
                    ),
                    NotarialFieldCatalog(
                        code="NOTARY_FIELD",
                        label="Notaría",
                        field_type="text",
                        category="persona",
                        scope="notary",
                        notary_id=10,
                        is_active=True,
                    ),
                    NotarialFieldCatalog(
                        code="OTHER_NOTARY_FIELD",
                        label="Otra notaría",
                        field_type="text",
                        category="persona",
                        scope="notary",
                        notary_id=20,
                        is_active=True,
                    ),
                    NotarialFieldCatalog(
                        code="INACTIVE_NOTARY_FIELD",
                        label="Campo inactivo",
                        field_type="text",
                        category="persona",
                        scope="notary",
                        notary_id=10,
                        is_active=False,
                    ),
                ]
            )
            db.commit()

            result = list_field_catalog(
                category=None,
                scope=None,
                search=None,
                db=db,
                current_user=SimpleNamespace(default_notary_id=10),
            )

            self.assertEqual([item.code for item in result], ["GLOBAL_FIELD", "NOTARY_FIELD"])

            filtered_result = list_field_catalog(
                category="fecha",
                scope=None,
                search=None,
                db=db,
                current_user=SimpleNamespace(default_notary_id=10),
            )

            self.assertEqual(filtered_result, [])
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
