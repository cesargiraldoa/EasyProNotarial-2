from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.services.gari_billing_client import GariBillingClient, GariBillingError
from app.services.gari_billing_payload import build_gari_billing_invoice_payload


def _make_case(**overrides):
    person = SimpleNamespace(
        full_name="Ana Maria Perez",
        document_type="CC",
        document_number="123456789",
        email="ana@example.com",
        phone="3001234567",
        address="Cra 1 # 2-3",
    )
    legal_entity = None
    participant = SimpleNamespace(person=person, legal_entity=legal_entity)
    notary = SimpleNamespace(notary_label="Notaría Primera de Prueba")
    base = SimpleNamespace(
        id=18,
        notary_id=7,
        case_type="escritura",
        act_type="compraventa",
        metadata_json="{}",
        participants=[participant],
        notary=notary,
    )
    for key, value in overrides.items():
        setattr(base, key, value)
    return base


class GariBillingPayloadTests(unittest.TestCase):
    def test_builds_default_invoice_payload_from_case(self):
        case = _make_case()

        payload = build_gari_billing_invoice_payload(case)

        self.assertEqual(payload["source_system"], "easypro")
        self.assertEqual(payload["external_reference"], "case_18")
        self.assertEqual(payload["idempotency_key"], "easypro-case_18")
        self.assertEqual(payload["emit_mode"], "draft")
        self.assertEqual(payload["customer"]["customer_kind"], "natural")
        self.assertEqual(payload["customer"]["document_type"], "CC")
        self.assertEqual(payload["customer"]["document_number"], "123456789")
        self.assertEqual(payload["lines"][0]["code"], "SERV-NOTARIAL-001")
        self.assertEqual(payload["metadata"]["document_type"], "minuta")
        self.assertEqual(payload["metadata"]["case_id"], 18)


class GariBillingClientTests(unittest.TestCase):
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
