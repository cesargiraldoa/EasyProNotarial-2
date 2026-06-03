from __future__ import annotations

import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.deps import get_current_user, get_db
from app.main import app
from app.services.gari_billing_client import GariBillingClient, GariBillingError
from app.services.gari_billing_payload import build_gari_billing_invoice_payload


def _make_case(**overrides):
    notary = SimpleNamespace(notary_label="Notaría Primera de Prueba")
    template = SimpleNamespace(document_type="minuta")
    base = SimpleNamespace(
        id=18,
        notary_id=7,
        case_type="escritura",
        act_type="compraventa",
        metadata_json="{}",
        template=template,
        notary=notary,
    )
    for key, value in overrides.items():
        setattr(base, key, value)
    return base


def _make_user():
    role = SimpleNamespace(code="super_admin")
    assignment = SimpleNamespace(role=role, notary_id=None)
    return SimpleNamespace(
        id=1,
        is_active=True,
        default_notary_id=None,
        role_assignments=[assignment],
    )


class GariBillingPayloadTests(unittest.TestCase):
    def test_builds_payload_with_explicit_billing_customer(self):
        case = _make_case()
        payload = build_gari_billing_invoice_payload(
            case,
            billing_customer={
                "customer_kind": "natural",
                "document_type": "CC",
                "document_number": "123456789",
                "legal_name": "Ana Maria Perez",
                "email": "ana@example.com",
            },
            billing_lines=[
                {
                    "code": "SERV-NOTARIAL-001",
                    "description": "Servicio notarial",
                    "quantity": 1,
                    "unit_price": 100000,
                    "discount_amount": 0,
                    "tax_rate": 19,
                    "unit_measure": "NIU",
                }
            ],
            document_id=86,
            version_id=198,
            document_type="minuta",
        )

        self.assertEqual(payload["customer"]["legal_name"], "Ana Maria Perez")
        self.assertEqual(payload["customer"]["document_type"], "CC")
        self.assertEqual(payload["lines"][0]["code"], "SERV-NOTARIAL-001")
        self.assertEqual(payload["metadata"]["document_id"], 86)
        self.assertEqual(payload["metadata"]["version_id"], 198)
        self.assertEqual(payload["metadata"]["document_type"], "minuta")

    def test_builds_payload_with_explicit_billing_lines(self):
        case = _make_case()
        payload = build_gari_billing_invoice_payload(
            case,
            billing_customer={
                "customer_kind": "juridica",
                "document_type": "NIT",
                "document_number": "900123456-7",
                "legal_name": "Empresa Ejemplo SAS",
            },
            billing_lines=[
                {
                    "code": "SERV-COPIAS-001",
                    "description": "Copias",
                    "quantity": 2,
                    "unit_price": 5000,
                    "discount_amount": 0,
                    "tax_rate": 19,
                    "unit_measure": "NIU",
                },
                {
                    "code": "SERV-OTRO-001",
                    "description": "Otro servicio",
                    "quantity": 1,
                    "unit_price": 20000,
                    "discount_amount": 1000,
                    "tax_rate": 19,
                    "unit_measure": "NIU",
                },
            ],
        )

        self.assertEqual(len(payload["lines"]), 2)
        self.assertEqual(payload["lines"][0]["code"], "SERV-COPIAS-001")
        self.assertEqual(payload["lines"][1]["discount_amount"], 1000)

    def test_raises_clear_error_without_billing_customer(self):
        case = _make_case()

        with self.assertRaises(ValueError) as exc:
            build_gari_billing_invoice_payload(
                case,
                billing_lines=[
                    {
                        "code": "SERV-NOTARIAL-001",
                        "description": "Servicio notarial",
                        "quantity": 1,
                        "unit_price": 100000,
                        "discount_amount": 0,
                        "tax_rate": 19,
                        "unit_measure": "NIU",
                    }
                ],
            )

        self.assertIn("billing_customer", str(exc.exception))

    def test_raises_clear_error_without_billing_lines(self):
        case = _make_case()

        with self.assertRaises(ValueError) as exc:
            build_gari_billing_invoice_payload(
                case,
                billing_customer={
                    "customer_kind": "natural",
                    "document_type": "CC",
                    "document_number": "123456789",
                    "legal_name": "Ana Maria Perez",
                },
            )

        self.assertIn("billing_lines", str(exc.exception))


class GariBillingClientTests(unittest.TestCase):
    def tearDown(self):
        get_settings.cache_clear()

    @patch.dict(
        os.environ,
        {
            "GARI_BILLING_BASE_URL": "http://127.0.0.1:8000",
            "GARI_BILLING_INTERNAL_KEY": "local-gari-billing-dev-key-2026",
            "GARI_BILLING_TIMEOUT_SECONDS": "30",
        },
        clear=True,
    )
    def test_client_reads_env_configuration(self):
        get_settings.cache_clear()

        client = GariBillingClient()

        self.assertEqual(client.base_url, "http://127.0.0.1:8000")
        self.assertEqual(client.internal_key, "local-gari-billing-dev-key-2026")
        self.assertEqual(client.timeout_seconds, 30)

    @patch("app.services.gari_billing_client.get_settings")
    @patch.dict(os.environ, {}, clear=True)
    def test_client_raises_clear_error_when_base_url_missing(self, settings_mock: Mock):
        settings_mock.return_value = SimpleNamespace(
            gari_billing_base_url="",
            gari_billing_internal_key="secret",
            gari_billing_timeout_seconds=30,
        )

        client = GariBillingClient()

        with self.assertRaises(GariBillingError) as exc:
            client.create_invoice({"external_reference": "case_18"})

        self.assertIn("GARI_BILLING_BASE_URL no está configurada en backend/.env de EasyPro", str(exc.exception))

    @patch("app.services.gari_billing_client.get_settings")
    @patch.dict(os.environ, {}, clear=True)
    def test_client_raises_clear_error_when_internal_key_missing(self, settings_mock: Mock):
        settings_mock.return_value = SimpleNamespace(
            gari_billing_base_url="http://127.0.0.1:8000",
            gari_billing_internal_key="",
            gari_billing_timeout_seconds=30,
        )

        client = GariBillingClient()

        with self.assertRaises(GariBillingError) as exc:
            client.create_invoice({"external_reference": "case_18"})

        self.assertIn("GARI_BILLING_INTERNAL_KEY no está configurada en backend/.env de EasyPro", str(exc.exception))

    @patch("app.services.gari_billing_client.requests.request")
    def test_create_invoice_sends_internal_key_header(self, request_mock: Mock):
        response = Mock()
        response.status_code = 200
        response.text = "{\"invoice_id\":\"INV-1\",\"status\":\"draft\",\"full_number\":\"FV-1\",\"total\":100000}"
        response.json.return_value = {
            "invoice_id": "INV-1",
            "status": "draft",
            "full_number": "FV-1",
            "total": 100000,
        }
        request_mock.return_value = response

        client = GariBillingClient(base_url="https://gari.example", internal_key="secret", timeout_seconds=5)
        result = client.create_invoice({"external_reference": "case_18"})

        self.assertEqual(result["invoice_id"], "INV-1")
        request_mock.assert_called_once()
        _, kwargs = request_mock.call_args
        self.assertEqual(kwargs["headers"]["X-Billing-Internal-Key"], "secret")
        self.assertEqual(kwargs["timeout"], 5)

    @patch("app.services.gari_billing_client.requests.request")
    def test_create_invoice_raises_clear_error_on_http_failure(self, request_mock: Mock):
        response = Mock()
        response.status_code = 502
        response.text = "{\"detail\":\"upstream failure\"}"
        response.json.return_value = {"detail": "upstream failure"}
        request_mock.return_value = response

        client = GariBillingClient(base_url="https://gari.example", internal_key="secret", timeout_seconds=5)

        with self.assertRaises(GariBillingError) as exc:
            client.create_invoice({"external_reference": "case_18"})

        self.assertIn("upstream failure", str(exc.exception))


class GariBillingEndpointTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self._overrides = {
            get_current_user: _make_user,
            get_db: lambda: None,
        }
        app.dependency_overrides.update(self._overrides)

    def tearDown(self):
        for key in self._overrides:
            app.dependency_overrides.pop(key, None)

    @patch("app.modules.billing.router.load_case_for_billing")
    @patch("app.modules.billing.router.GariBillingClient")
    @patch("app.modules.billing.router.build_gari_billing_invoice_payload")
    def test_post_from_case_accepts_empty_body(self, payload_builder: Mock, client_cls: Mock, load_case: Mock):
        case = _make_case()
        load_case.return_value = case
        payload_builder.return_value = {"external_reference": "case_18", "emit_mode": "draft", "source_system": "easypro"}
        client_instance = Mock()
        client_instance.create_invoice.return_value = {
            "invoice_id": "INV-1",
            "status": "draft",
            "full_number": "FV-1",
            "total": 100000,
            "gari_response": {"invoice_id": "INV-1"},
        }
        client_cls.return_value = client_instance

        response = self.client.post("/api/v1/billing/gari/invoices/from-case/18?emit_mode=draft")

        self.assertEqual(response.status_code, 200)
        payload_builder.assert_called_once_with(
            case,
            emit_mode="draft",
            billing_customer=None,
            billing_lines=None,
            document_id=None,
            version_id=None,
            document_type=None,
        )
        client_instance.create_invoice.assert_called_once()

    @patch("app.modules.billing.router.load_case_for_billing")
    @patch("app.modules.billing.router.GariBillingClient")
    @patch("app.modules.billing.router.build_gari_billing_invoice_payload")
    def test_post_from_case_accepts_explicit_body(self, payload_builder: Mock, client_cls: Mock, load_case: Mock):
        case = _make_case()
        load_case.return_value = case
        billing_payload = {"external_reference": "case_18", "emit_mode": "draft", "source_system": "easypro"}
        payload_builder.return_value = billing_payload
        client_instance = Mock()
        client_instance.create_invoice.return_value = {
            "invoice_id": "INV-2",
            "status": "draft",
            "full_number": "FV-2",
            "total": 200000,
            "gari_response": {"invoice_id": "INV-2"},
        }
        client_cls.return_value = client_instance

        response = self.client.post(
            "/api/v1/billing/gari/invoices/from-case/18?emit_mode=draft",
            json={
                "emit_mode": "draft",
                "document_id": 86,
                "version_id": 198,
                "document_type": "minuta",
                "billing_customer": {
                    "customer_kind": "natural",
                    "document_type": "CC",
                    "document_number": "123456789",
                    "legal_name": "Ana Maria Perez",
                },
                "billing_lines": [
                    {
                        "code": "SERV-NOTARIAL-001",
                        "description": "Servicio notarial",
                        "quantity": 1,
                        "unit_price": 100000,
                        "discount_amount": 0,
                        "tax_rate": 19,
                        "unit_measure": "NIU",
                    }
                ],
            },
        )

        self.assertEqual(response.status_code, 200)
        payload_builder.assert_called_once()
        client_instance.create_invoice.assert_called_once_with(billing_payload)


if __name__ == "__main__":
    unittest.main()
