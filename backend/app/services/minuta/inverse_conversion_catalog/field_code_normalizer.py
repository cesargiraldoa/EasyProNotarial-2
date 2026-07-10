from __future__ import annotations

import re
import unicodedata


class FieldCodeNormalizer:
    """Normalize field labels into uppercase snake case and simple review candidates."""

    VALUE_TOKENS = {"VALOR", "VENTA", "PRECIO", "ACTO", "NUMEROS", "NUMERO", "NUMEROS", "LETRAS"}
    DOCUMENT_TOKENS = {"CEDULA", "DOCUMENTO", "NUMERO", "IDENTIFICACION"}
    ROLE_TOKENS = {
        "COMPRADOR",
        "COMPRADORA",
        "VENDEDOR",
        "VENDEDORA",
        "DEUDOR",
        "ACREEDOR",
        "OTORGANTE",
    }

    def normalize(self, value: str | None) -> str:
        if not value:
            return ""
        cleaned = value.strip()
        cleaned = re.sub(r"^\{\{\s*|\s*\}\}$", "", cleaned)
        cleaned = self._strip_accents(cleaned)
        cleaned = cleaned.upper()
        cleaned = cleaned.replace("&", " Y ")
        cleaned = re.sub(r"[^A-Z0-9]+", "_", cleaned)
        cleaned = re.sub(r"_+", "_", cleaned)
        return cleaned.strip("_")

    def tokens(self, value: str | None) -> set[str]:
        normalized = self.normalize(value)
        return {token for token in normalized.split("_") if token}

    def display_name(self, field_code: str) -> str:
        return self.normalize(field_code).replace("_", " ").title()

    def suggest_canonical(self, field_code: str, all_codes: set[str] | None = None) -> tuple[str, str, float]:
        normalized = self.normalize(field_code)
        tokens = self.tokens(normalized)
        all_codes = all_codes or set()

        if {"VALOR", "VENTA"}.issubset(tokens):
            return "VALOR_VENTA", "suggested", 0.9
        if "PRECIO" in tokens and "VENTA" in tokens:
            return "VALOR_VENTA", "suggested", 0.82
        if "VALOR" in tokens and "ACTO" in tokens:
            return "VALOR_VENTA", "conflict" if "VALOR_VENTA" in all_codes else "suggested", 0.68
        if "VENTA" in tokens and ("NUMEROS" in tokens or "NUMERO" in tokens):
            return "VALOR_VENTA", "suggested", 0.76

        role_token = next((token for token in tokens if token in self.ROLE_TOKENS), None)
        if role_token and tokens.intersection(self.DOCUMENT_TOKENS):
            role = self._canonical_role(role_token)
            canonical = f"NUMERO_DOCUMENTO_{role}"
            status = "suggested" if "NUMERO" in tokens and "DOCUMENTO" in tokens else "conflict"
            return canonical, status, 0.86 if status == "suggested" else 0.66

        return normalized, "suggested", 0.6

    @staticmethod
    def _strip_accents(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        return "".join(char for char in normalized if not unicodedata.combining(char))

    @staticmethod
    def _canonical_role(role: str) -> str:
        if role == "COMPRADORA":
            return "COMPRADOR"
        if role == "VENDEDORA":
            return "VENDEDOR"
        return role
