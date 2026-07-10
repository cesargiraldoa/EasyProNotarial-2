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
    ORDINAL_ROLES = {"COMPRADOR", "VENDEDOR", "OTORGANTE", "ACEPTANTE", "APODERADO", "PODERDANTE"}

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

        if self.semantic_category(normalized) == "VALOR_VENTA":
            return "VALOR_VENTA", "suggested", 0.9
        if "PRECIO" in tokens and "VENTA" in tokens:
            return "VALOR_VENTA", "suggested", 0.82
        if "VALOR" in tokens and "ACTO" in tokens:
            return "VALOR_VENTA", "conflict" if "VALOR_VENTA" in all_codes else "suggested", 0.68
        if "VENTA" in tokens and ("NUMEROS" in tokens or "NUMERO" in tokens) and "ESCRITURA" not in tokens:
            return "VALOR_VENTA", "suggested", 0.76

        role_token = next((token for token in tokens if token in self.ROLE_TOKENS), None)
        category = self.semantic_category(normalized)
        if role_token and category in {"NUMERO_DOCUMENTO", "TIPO_DOCUMENTO"}:
            role = self._canonical_role(role_token)
            ordinal = self.ordinal_suffix(normalized)
            suffix = f"_{ordinal}" if ordinal else ""
            canonical = f"{category}_{role}{suffix}"
            status = "suggested" if normalized == canonical else "conflict"
            return canonical, status, 0.86 if status == "suggested" else 0.66

        return normalized, "suggested", 0.6

    def semantic_category(self, value: str | None) -> str:
        normalized = self.normalize(value)
        tokens = self.tokens(normalized)
        token_list = normalized.split("_") if normalized else []
        token_text = "_".join(token_list)

        if self._contains_sequence(token_list, ("TIPO", "DOCUMENTO")) or self._contains_sequence(token_list, ("TIPO", "DE", "DOCUMENTO")):
            return "TIPO_DOCUMENTO"
        if (
            "MUNICIPIO" in tokens
            and "EXPEDICION" in tokens
            and "DOCUMENTO" in tokens
        ):
            return "MUNICIPIO_EXPEDICION_DOCUMENTO"
        if "NUMERO" in tokens and "DOCUMENTO" in tokens:
            return "NUMERO_DOCUMENTO"
        if "CEDULA" in tokens and "CATASTRAL" in tokens:
            return "CEDULA_CATASTRAL"
        if "CODIGO" in tokens and "CATASTRAL" in tokens:
            return "CODIGO_CATASTRAL"
        if "FECHA" in tokens and "NACIMIENTO" in tokens:
            return "FECHA_NACIMIENTO"
        if "MUNICIPIO" in tokens and "NACIMIENTO" in tokens:
            return "MUNICIPIO_NACIMIENTO"
        if "NUMERO" in tokens and "ESCRITURA" in tokens and "LETRAS" in tokens:
            return "NUMERO_ESCRITURA_LETRAS"
        if "NUMERO" in tokens and "ESCRITURA" in tokens and ("NUMEROS" in tokens or "NUMERO" in tokens):
            return "NUMERO_ESCRITURA_NUMEROS"
        if token_list and token_list[0] in {"DIA", "DIAS"}:
            return "DIA"
        if token_list and token_list[0] == "MES":
            return "MES"
        if token_list and token_list[0] in {"ANO", "ANIO"}:
            return "ANO"
        if "FECHA" in tokens:
            return "FECHA"
        if ("VALOR" in tokens and "VENTA" in tokens) or ("PRECIO" in tokens and "VENTA" in tokens):
            return "VALOR_VENTA"
        if "VALOR" in tokens:
            return "VALOR"
        if "NOMBRE" in tokens:
            return "NOMBRE"
        if "ESTADO" in tokens and "CIVIL" in tokens:
            return "ESTADO_CIVIL"
        if "CELULAR" in tokens:
            return "CELULAR"
        if "EMAIL" in tokens or "CORREO" in tokens:
            return "EMAIL"
        if "DIRECCION" in tokens:
            return "DIRECCION"
        if "MATRICULA" in tokens:
            return "MATRICULA"
        return token_text or "UNKNOWN"

    def ordinal_suffix(self, value: str | None) -> str | None:
        tokens = self.normalize(value).split("_")
        for index, token in enumerate(tokens[:-1]):
            if token in self.ORDINAL_ROLES and tokens[index + 1].isdigit():
                return tokens[index + 1]
        return None

    def semantic_signature(self, value: str | None) -> tuple[str, str | None]:
        return self.semantic_category(value), self.ordinal_suffix(value)

    def can_alias(self, left: str, right: str) -> bool:
        left_normalized = self.normalize(left)
        right_normalized = self.normalize(right)
        if left_normalized == right_normalized:
            return True

        left_category, left_ordinal = self.semantic_signature(left_normalized)
        right_category, right_ordinal = self.semantic_signature(right_normalized)
        if left_category != right_category:
            return False
        if left_ordinal != right_ordinal:
            return False
        return True

    @staticmethod
    def _contains_sequence(tokens: list[str], sequence: tuple[str, ...]) -> bool:
        if not sequence or len(tokens) < len(sequence):
            return False
        for index in range(0, len(tokens) - len(sequence) + 1):
            if tuple(tokens[index : index + len(sequence)]) == sequence:
                return True
        return False

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
