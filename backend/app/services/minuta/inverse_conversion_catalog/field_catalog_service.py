from __future__ import annotations

import json
from dataclasses import asdict

from sqlalchemy.orm import Session

from app.services.minuta.inverse_conversion_catalog.field_alias_builder import FieldAliasBuilder
from app.services.minuta.inverse_conversion_catalog.field_code_normalizer import FieldCodeNormalizer
from app.services.minuta.inverse_conversion_catalog.models import (
    AliasSuggestion,
    FieldAlias,
    FieldDefinition,
)


class FieldCatalogService:
    """Build suggested field definitions and aliases from the imported corpus."""

    def __init__(
        self,
        db: Session | None = None,
        normalizer: FieldCodeNormalizer | None = None,
        alias_builder: FieldAliasBuilder | None = None,
    ) -> None:
        self.db = db
        self.normalizer = normalizer or FieldCodeNormalizer()
        self.alias_builder = alias_builder or FieldAliasBuilder(self.normalizer)

    def build_from_frequency(
        self,
        field_frequency: dict[str, int],
        commit: bool = False,
    ) -> dict[str, list[dict]]:
        suggestions = self.alias_builder.build(field_frequency)
        definitions = self._definitions_from_aliases(suggestions)

        if self.db is not None:
            self._persist(definitions, suggestions)
            if commit:
                self.db.commit()
            else:
                self.db.flush()

        return {
            "field_definitions": definitions,
            "field_aliases": [asdict(alias) for alias in suggestions],
            "conflicts": [asdict(alias) for alias in suggestions if alias.status == "conflict"],
        }

    def build_from_database(self, commit: bool = False) -> dict[str, list[dict]]:
        if self.db is None:
            raise ValueError("A database session is required to build from database.")
        from app.services.minuta.inverse_conversion_catalog.models import CorpusDocumentField

        rows = self.db.query(CorpusDocumentField.raw_field_code, CorpusDocumentField.occurrences).all()
        frequency: dict[str, int] = {}
        for raw_code, occurrences in rows:
            frequency[raw_code] = frequency.get(raw_code, 0) + int(occurrences or 0)
        return self.build_from_frequency(frequency, commit=commit)

    def _definitions_from_aliases(self, aliases: list[AliasSuggestion]) -> list[dict]:
        by_canonical: dict[str, dict] = {}
        for alias in aliases:
            status = "conflict" if alias.status == "conflict" else "suggested"
            current = by_canonical.get(alias.canonical_field_code)
            if current is None:
                by_canonical[alias.canonical_field_code] = {
                    "field_code": alias.canonical_field_code,
                    "display_name": self.normalizer.display_name(alias.canonical_field_code),
                    "data_type": None,
                    "field_group": self._field_group(alias.canonical_field_code),
                    "legal_role": self._legal_role(alias.canonical_field_code),
                    "act_type": None,
                    "description": None,
                    "status": status,
                    "confidence": alias.confidence,
                    "source": "inverse_conversion_catalog",
                    "metadata_json": json.dumps({"raw_alias_count": 1}, ensure_ascii=False),
                }
            else:
                current["confidence"] = max(current["confidence"], alias.confidence)
                if status == "conflict":
                    current["status"] = "conflict"
                metadata = json.loads(current["metadata_json"])
                metadata["raw_alias_count"] = metadata.get("raw_alias_count", 0) + 1
                current["metadata_json"] = json.dumps(metadata, ensure_ascii=False)
        return sorted(by_canonical.values(), key=lambda item: item["field_code"])

    def _persist(self, definitions: list[dict], aliases: list[AliasSuggestion]) -> None:
        if self.db is None:
            return
        definition_ids: dict[str, int | None] = {}
        for definition in definitions:
            existing = self.db.query(FieldDefinition).filter_by(field_code=definition["field_code"]).one_or_none()
            if existing is None:
                existing = FieldDefinition(**definition)
                self.db.add(existing)
                self.db.flush()
            definition_ids[definition["field_code"]] = existing.id

        for alias in aliases:
            existing_alias = (
                self.db.query(FieldAlias)
                .filter_by(raw_field_code=alias.raw_field_code, canonical_field_code=alias.canonical_field_code)
                .one_or_none()
            )
            payload = {
                "raw_field_code": alias.raw_field_code,
                "canonical_field_code": alias.canonical_field_code,
                "field_definition_id": definition_ids.get(alias.canonical_field_code),
                "frequency": alias.frequency,
                "status": "conflict" if alias.status == "conflict" else "suggested",
                "source": "inverse_conversion_catalog",
                "metadata_json": json.dumps(
                    {"confidence": alias.confidence, "reason": alias.reason, "context_samples": list(alias.context_samples)},
                    ensure_ascii=False,
                ),
            }
            if existing_alias is None:
                self.db.add(FieldAlias(**payload))
            else:
                for key, value in payload.items():
                    setattr(existing_alias, key, value)

    @staticmethod
    def _field_group(field_code: str) -> str | None:
        tokens = set(field_code.split("_"))
        if {"VALOR", "VENTA"}.issubset(tokens):
            return "values"
        if "DOCUMENTO" in tokens:
            return "participants"
        return None

    @staticmethod
    def _legal_role(field_code: str) -> str | None:
        for role in ("COMPRADOR", "VENDEDOR", "DEUDOR", "ACREEDOR", "OTORGANTE"):
            if role in field_code:
                return role.lower()
        return None
