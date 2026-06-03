from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import requests

from app.core.config import get_settings


class GariBillingError(RuntimeError):
    pass


class GariBillingTimeoutError(GariBillingError):
    pass


@dataclass(slots=True)
class GariBillingResponse:
    status_code: int
    body: dict[str, Any]


class GariBillingClient:
    def __init__(
        self,
        base_url: str | None = None,
        internal_key: str | None = None,
        timeout_seconds: int | None = None,
    ) -> None:
        settings = get_settings()
        self.base_url = self._resolve_config_value(
            explicit_value=base_url,
            env_key="GARI_BILLING_BASE_URL",
            settings_value=settings.gari_billing_base_url,
        ).rstrip("/")
        self.internal_key = self._resolve_config_value(
            explicit_value=internal_key,
            env_key="GARI_BILLING_INTERNAL_KEY",
            settings_value=settings.gari_billing_internal_key,
        )
        timeout_value = timeout_seconds if timeout_seconds is not None else os.getenv("GARI_BILLING_TIMEOUT_SECONDS")
        if timeout_value is None or str(timeout_value).strip() == "":
            timeout_value = settings.gari_billing_timeout_seconds
        self.timeout_seconds = int(timeout_value)

    @staticmethod
    def _resolve_config_value(*, explicit_value: str | int | None, env_key: str, settings_value: str | int) -> str:
        if explicit_value is not None:
            return str(explicit_value).strip()
        env_value = os.getenv(env_key, "")
        if env_value.strip():
            return env_value.strip()
        return str(settings_value).strip()

    def _ensure_configured(self) -> None:
        if not self.base_url:
            raise GariBillingError("GARI_BILLING_BASE_URL no está configurada en backend/.env de EasyPro.")
        if not self.internal_key:
            raise GariBillingError("GARI_BILLING_INTERNAL_KEY no está configurada en backend/.env de EasyPro.")

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        self._ensure_configured()
        url = f"{self.base_url}{path if path.startswith('/') else '/' + path}"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Billing-Internal-Key": self.internal_key,
        }
        try:
            response = requests.request(
                method=method,
                url=url,
                json=payload,
                headers=headers,
                timeout=self.timeout_seconds,
            )
        except requests.Timeout as exc:
            raise GariBillingTimeoutError(f"Timeout al contactar Gari Billing después de {self.timeout_seconds} segundos.") from exc
        except requests.RequestException as exc:
            raise GariBillingError(f"No fue posible conectar con Gari Billing: {exc.__class__.__name__}.") from exc

        response_text = response.text.strip()
        response_json: dict[str, Any]
        try:
            response_json = response.json() if response_text else {}
        except ValueError:
            response_json = {"raw_text": response_text}

        if response.status_code >= 400:
            detail = self._extract_error_message(response_json, response_text)
            raise GariBillingError(f"Gari Billing respondió {response.status_code}: {detail}")

        return response_json

    @staticmethod
    def _extract_error_message(response_json: dict[str, Any], response_text: str) -> str:
        for key in ("detail", "message", "error", "error_message"):
            value = response_json.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        if response_text:
            return response_text[:500]
        return "Respuesta vacía desde Gari Billing."

    @staticmethod
    def _normalize_invoice_response(response_json: dict[str, Any]) -> dict[str, Any]:
        candidates = [response_json]
        for key in ("data", "result", "invoice", "payload"):
            value = response_json.get(key)
            if isinstance(value, dict):
                candidates.append(value)

        normalized: dict[str, Any] = {
            "gari_response": response_json,
            "source_system": None,
            "external_reference": None,
            "idempotency_key": None,
            "emit_mode": None,
            "invoice_id": None,
            "status": None,
            "full_number": None,
            "total": None,
            "error_message": None,
        }
        for candidate in candidates:
            for key in ("source_system", "external_reference", "idempotency_key", "emit_mode", "invoice_id", "status", "full_number", "total", "error_message"):
                value = candidate.get(key)
                if value not in (None, "") and normalized[key] in (None, ""):
                    normalized[key] = value
        if normalized["invoice_id"] is None:
            for key in ("id", "invoiceNumber", "invoice_number"):
                value = response_json.get(key)
                if value not in (None, ""):
                    normalized["invoice_id"] = value
                    break
        if normalized["full_number"] is None:
            for key in ("number", "invoice_number", "document_number"):
                value = response_json.get(key)
                if value not in (None, ""):
                    normalized["full_number"] = value
                    break
        if normalized["status"] is None:
            normalized["status"] = response_json.get("status") or response_json.get("state")
        if normalized["total"] is None:
            total = response_json.get("total")
            if total is None and isinstance(response_json.get("totals"), dict):
                total = response_json["totals"].get("grand_total")
            normalized["total"] = total
        if normalized["error_message"] is None:
            normalized["error_message"] = response_json.get("error_message") or response_json.get("message")
        return normalized

    def create_invoice(self, payload: dict[str, Any]) -> dict[str, Any]:
        response_json = self._request("POST", "/api/integrations/billing/invoices", payload)
        return self._normalize_invoice_response(response_json)

    def get_invoice(self, external_reference: str) -> dict[str, Any]:
        encoded_reference = quote(external_reference, safe="")
        response_json = self._request("GET", f"/api/integrations/billing/invoices/{encoded_reference}")
        return self._normalize_invoice_response(response_json)

    def issue_stub(self, external_reference: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        draft_payload = dict(payload or {})
        draft_payload.setdefault("external_reference", external_reference)
        draft_payload["emit_mode"] = "stub"
        return self.create_invoice(draft_payload)

    def issue_matias_sandbox(self, external_reference: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        draft_payload = dict(payload or {})
        draft_payload.setdefault("external_reference", external_reference)
        draft_payload["emit_mode"] = "matias_sandbox"
        return self.create_invoice(draft_payload)
