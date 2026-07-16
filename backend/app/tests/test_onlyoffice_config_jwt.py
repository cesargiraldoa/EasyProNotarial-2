from datetime import datetime
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from fastapi import HTTPException
from jose import jwt

from app.modules.document_flow import router as document_flow_router
from app.modules.minuta import router as minuta_router


class _OnlyOfficeResponse:
    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload


def _user(notary_id=1, role_notary_id=None, role_code="protocolist"):
    return SimpleNamespace(
        id=7,
        full_name="User Demo",
        email="user@example.com",
        default_notary_id=notary_id,
        role_assignments=[
            SimpleNamespace(
                notary_id=role_notary_id if role_notary_id is not None else notary_id,
                role=SimpleNamespace(code=role_code),
            )
        ],
    )


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

    def test_minuta_file_token_can_include_marked_template_context(self):
        settings = minuta_router.get_settings()
        previous_secret = settings.onlyoffice_jwt_secret
        settings.onlyoffice_jwt_secret = "onlyoffice-secret"
        try:
            file_token = minuta_router._make_file_token(
                "cases/demo/minuta.docx",
                "minuta.docx",
                "Minuta demo",
                1,
                case_id=10,
                document_id=20,
                version_id=30,
                user_id=7,
            )

            decoded = jwt.decode(file_token, "onlyoffice-secret", algorithms=["HS256"])

            self.assertEqual(decoded["case_id"], 10)
            self.assertEqual(decoded["document_id"], 20)
            self.assertEqual(decoded["version_id"], 30)
            self.assertEqual(decoded["user_id"], 7)
        finally:
            settings.onlyoffice_jwt_secret = previous_secret

    def test_minuta_forcesave_uses_same_document_key_as_config_and_posts_command(self):
        settings = minuta_router.get_settings()
        previous_secret = settings.onlyoffice_jwt_secret
        previous_url = settings.onlyoffice_documentserver_url
        settings.onlyoffice_jwt_secret = ""
        settings.onlyoffice_documentserver_url = "https://onlyoffice.example"
        try:
            file_token = minuta_router._make_file_token(
                "cases/demo/minuta.docx",
                "marked-template.docx",
                "Minuta demo",
                1,
            )
            config = minuta_router.minuta_onlyoffice_config(
                request=SimpleNamespace(base_url="http://testserver/"),
                token=file_token,
                current_user=_user(),
            )
            with patch.object(minuta_router._req, "post", return_value=_OnlyOfficeResponse({"error": 0})) as post:
                result = minuta_router.minuta_onlyoffice_forcesave(
                    token=file_token,
                    current_user=_user(),
                    db=object(),
                )

            self.assertEqual(result["status"], "requested")
            call = post.call_args
            self.assertIn("/command?shardkey=minuta-marked-template", call.args[0])
            self.assertEqual(call.kwargs["timeout"], 20)
            self.assertEqual(call.kwargs["json"]["c"], "forcesave")
            self.assertEqual(call.kwargs["json"]["key"], config["document"]["key"])
            self.assertEqual(call.kwargs["json"]["userdata"], "easypro-marked-template-save")
        finally:
            settings.onlyoffice_jwt_secret = previous_secret
            settings.onlyoffice_documentserver_url = previous_url

    def test_minuta_forcesave_includes_command_jwt_when_secret_is_configured(self):
        settings = minuta_router.get_settings()
        previous_secret = settings.onlyoffice_jwt_secret
        previous_url = settings.onlyoffice_documentserver_url
        settings.onlyoffice_jwt_secret = "onlyoffice-secret"
        settings.onlyoffice_documentserver_url = "https://onlyoffice.example/"
        try:
            file_token = minuta_router._make_file_token(
                "cases/demo/minuta.docx",
                "marked-template.docx",
                "Minuta demo",
                1,
            )
            with patch.object(minuta_router._req, "post", return_value=_OnlyOfficeResponse({"error": 0})) as post:
                minuta_router.minuta_onlyoffice_forcesave(token=file_token, current_user=_user(), db=object())

            command_payload = post.call_args.kwargs["json"]
            self.assertIn("token", command_payload)
            decoded = jwt.decode(command_payload["token"], "onlyoffice-secret", algorithms=["HS256"])
            self.assertEqual(decoded["c"], "forcesave")
            self.assertEqual(decoded["key"], "minuta-marked-template")
            self.assertEqual(decoded["userdata"], "easypro-marked-template-save")
            self.assertNotIn("token", decoded)
        finally:
            settings.onlyoffice_jwt_secret = previous_secret
            settings.onlyoffice_documentserver_url = previous_url

    def test_minuta_forcesave_error_4_is_controlled_no_changes(self):
        settings = minuta_router.get_settings()
        previous_secret = settings.onlyoffice_jwt_secret
        settings.onlyoffice_jwt_secret = "onlyoffice-secret"
        try:
            file_token = minuta_router._make_file_token("storage.docx", "storage.docx", "Minuta", 1)
            with patch.object(minuta_router._req, "post", return_value=_OnlyOfficeResponse({"error": 4})):
                result = minuta_router.minuta_onlyoffice_forcesave(token=file_token, current_user=_user(), db=object())

            self.assertEqual(result["status"], "no_changes")
            self.assertEqual(result["onlyoffice_error"], 4)
        finally:
            settings.onlyoffice_jwt_secret = previous_secret

    def test_minuta_forcesave_other_onlyoffice_error_returns_502(self):
        settings = minuta_router.get_settings()
        previous_secret = settings.onlyoffice_jwt_secret
        settings.onlyoffice_jwt_secret = "onlyoffice-secret"
        try:
            file_token = minuta_router._make_file_token("storage.docx", "storage.docx", "Minuta", 1)
            with patch.object(minuta_router._req, "post", return_value=_OnlyOfficeResponse({"error": 9})):
                with self.assertRaises(HTTPException) as raised:
                    minuta_router.minuta_onlyoffice_forcesave(token=file_token, current_user=_user(), db=object())

            self.assertEqual(raised.exception.status_code, 502)
            self.assertEqual(raised.exception.detail["onlyoffice_error"], 9)
        finally:
            settings.onlyoffice_jwt_secret = previous_secret

    def test_minuta_forcesave_blocks_user_without_notary_access(self):
        settings = minuta_router.get_settings()
        previous_secret = settings.onlyoffice_jwt_secret
        settings.onlyoffice_jwt_secret = "onlyoffice-secret"
        try:
            file_token = minuta_router._make_file_token("storage.docx", "storage.docx", "Minuta", 1)
            with patch.object(minuta_router._req, "post") as post:
                with self.assertRaises(HTTPException) as raised:
                    minuta_router.minuta_onlyoffice_forcesave(
                        token=file_token,
                        current_user=_user(notary_id=2, role_notary_id=2),
                        db=object(),
                    )

            self.assertEqual(raised.exception.status_code, 403)
            post.assert_not_called()
        finally:
            settings.onlyoffice_jwt_secret = previous_secret

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
