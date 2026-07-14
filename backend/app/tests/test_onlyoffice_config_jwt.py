from datetime import datetime
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from jose import jwt

from app.modules.document_flow import router as document_flow_router
from app.modules.minuta import router as minuta_router


class OnlyOfficeConfigJwtTests(unittest.TestCase):
    def test_minuta_config_removes_easypro_session_but_keeps_onlyoffice_config_token(self):
        settings = minuta_router.get_settings()
        previous_secret = settings.onlyoffice_jwt_secret
        previous_api_public_url = settings.api_public_url
        settings.onlyoffice_jwt_secret = "onlyoffice-secret"
        settings.api_public_url = "https://easypronotarial-2-production.up.railway.app"
        try:
            file_token = minuta_router._make_file_token(
                "cases/demo/minuta.docx",
                "minuta.docx",
                "Minuta demo",
                1,
            )

            config = minuta_router.minuta_onlyoffice_config(
                request=SimpleNamespace(base_url="http://testserver/"),
                token=file_token,
                current_user=SimpleNamespace(id=7, full_name="User Demo", email="user@example.com"),
            )

            self.assertNotIn("_easypro2_session", config)
            self.assertIn("token", config)
            decoded_config = jwt.decode(config["token"], "onlyoffice-secret", algorithms=["HS256"])
            self.assertEqual(decoded_config["document"]["title"], "Minuta demo")
            self.assertIn("/api/v1/minuta/onlyoffice/file?token=", config["document"]["url"])
            self.assertIn("/api/v1/minuta/onlyoffice/callback?token=", config["editorConfig"]["callbackUrl"])
            jwt.decode(file_token, "onlyoffice-secret", algorithms=["HS256"])
        finally:
            settings.onlyoffice_jwt_secret = previous_secret
            settings.api_public_url = previous_api_public_url

    def test_case_config_keeps_onlyoffice_config_token_and_file_token(self):
        previous_secret = document_flow_router.settings.onlyoffice_jwt_secret
        previous_api_public_url = document_flow_router.settings.api_public_url
        document_flow_router.settings.onlyoffice_jwt_secret = "onlyoffice-secret"
        document_flow_router.settings.api_public_url = "https://easypronotarial-2-production.up.railway.app"
        version = SimpleNamespace(
            id=30,
            file_format="docx",
            updated_at=datetime(2026, 7, 14, 12, 0, 0),
            original_filename="case.docx",
        )
        document = SimpleNamespace(id=20, versions=[version])
        case = SimpleNamespace(id=10, documents=[document])
        try:
            with patch.object(document_flow_router, "load_case_or_404", return_value=case):
                config = document_flow_router.onlyoffice_config(
                    case_id=10,
                    document_id=20,
                    version_id=30,
                    request=SimpleNamespace(base_url="http://testserver/"),
                    db=object(),
                    current_user=SimpleNamespace(id=7, full_name="User Demo", email="user@example.com"),
                )

            self.assertIn("token", config)
            decoded_config = jwt.decode(config["token"], "onlyoffice-secret", algorithms=["HS256"])
            self.assertEqual(decoded_config["document"]["title"], "case.docx")
            self.assertIn("/api/v1/document-flow/cases/10/documents/20/versions/30/onlyoffice/files/30?token=", config["document"]["url"])
            file_token = config["document"]["url"].split("token=", 1)[1]
            decoded_file_token = jwt.decode(file_token, "onlyoffice-secret", algorithms=["HS256"])
            self.assertEqual(decoded_file_token["case_id"], 10)
            self.assertEqual(decoded_file_token["document_id"], 20)
            self.assertEqual(decoded_file_token["version_id"], 30)
            self.assertIn("/api/v1/document-flow/cases/10/documents/20/versions/30/onlyoffice/callback/10/20/30", config["editorConfig"]["callbackUrl"])
        finally:
            document_flow_router.settings.onlyoffice_jwt_secret = previous_secret
            document_flow_router.settings.api_public_url = previous_api_public_url


if __name__ == "__main__":
    unittest.main()
