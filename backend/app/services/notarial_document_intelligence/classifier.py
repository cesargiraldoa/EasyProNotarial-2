from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.act_catalog import ActCatalog
from app.models.notarial_document_intelligence import NotarialDocumentBlock
from app.models.template_field import TemplateField
from app.services.minuta.inverse_conversion_catalog.models import CorpusDocument, FieldAlias, FieldDefinition, FieldPattern


CLASSIFIER_VERSION = "deterministic-catalog-v2"


KNOWN_BANKS = (
    "Bancolombia",
    "Banco Davivienda",
    "Banco de Bogota",
    "Banco Popular",
    "Banco Caja Social",
    "Scotiabank Colpatria",
    "BBVA",
)


@dataclass
class DetectedEntity:
    entity_type: str
    text: str
    normalized_text: str
    canonical_field_code: str | None
    role: str | None
    confidence: float
    block_id: int


@dataclass
class DocumentClassification:
    document_type: str
    document_subtype: str | None = None
    acts: list[str] = field(default_factory=list)
    notary_name: str | None = None
    project_name: str | None = None
    bank_name: str | None = None
    roles: list[str] = field(default_factory=list)
    confidence: float = 0.0
    evidence: list[dict] = field(default_factory=list)
    entities: list[DetectedEntity] = field(default_factory=list)


class NotarialDocumentClassifier:
    def __init__(self, db: Session | None = None) -> None:
        self.db = db

    def classify(self, blocks: list[NotarialDocumentBlock]) -> DocumentClassification:
        text = "\n".join(block.text or "" for block in blocks)
        normalized = _normalize(text)
        acts = self._acts(normalized)
        document_type = self._document_type(normalized, acts)
        entities = self._entities(blocks)
        classification = DocumentClassification(
            document_type=document_type,
            document_subtype=self._subtype(normalized, document_type),
            acts=acts,
            notary_name=self._notary_name(text),
            project_name=self._project_name(text),
            bank_name=self._bank_name(text),
            roles=self._roles(normalized),
            confidence=self._confidence(document_type, acts, entities),
            evidence=[
                {"kind": "keyword", "value": act, "source": "deterministic"} for act in acts
            ],
            entities=entities,
        )
        return classification

    def _document_type(self, normalized: str, acts: list[str]) -> str:
        if "promesa" in normalized and "compraventa" in normalized:
            return "promesa_compraventa"
        if "poder" in normalized:
            return "poder"
        if "hipoteca" in normalized and "compraventa" not in normalized:
            return "escritura_hipoteca"
        if "compraventa" in normalized or "venta" in acts:
            return "escritura_compraventa"
        if "escritura" in normalized:
            return "escritura_publica"
        return "documento_notarial"

    def _subtype(self, normalized: str, document_type: str) -> str | None:
        if "inmueble" in normalized or "matricula inmobiliaria" in normalized:
            return f"{document_type}_inmueble"
        if "vehiculo" in normalized:
            return f"{document_type}_vehiculo"
        return None

    def _acts(self, normalized: str) -> list[str]:
        candidates = {
            "compraventa": ("compraventa", "venta real"),
            "hipoteca": ("hipoteca", "garantia hipotecaria"),
            "promesa_compraventa": ("promesa de compraventa", "promesa compraventa"),
            "constitucion": ("constitucion", "constituye"),
            "cancelacion": ("cancelacion", "cancela"),
            "poder": ("poder", "apoderado"),
        }
        acts = [key for key, markers in candidates.items() if any(marker in normalized for marker in markers)]
        acts.extend(self._catalog_acts(normalized))
        acts = list(dict.fromkeys(acts))
        return acts or ["acto_notarial"]

    def _roles(self, normalized: str) -> list[str]:
        roles = []
        for role, markers in {
            "comprador": ("comprador", "compradora"),
            "vendedor": ("vendedor", "vendedora"),
            "otorgante": ("otorgante", "compareciente"),
            "acreedor": ("acreedor", "banco"),
            "deudor": ("deudor", "hipotecante"),
        }.items():
            if any(marker in normalized for marker in markers):
                roles.append(role)
        return roles

    def _notary_name(self, text: str) -> str | None:
        match = re.search(r"\bNOTAR[IÍ]A\s+(?:[A-ZÁÉÍÓÚÑ0-9]+\s*){1,5}", text, re.IGNORECASE)
        return _clean(match.group(0)) if match else None

    def _project_name(self, text: str) -> str | None:
        match = re.search(r"\b(?:PROYECTO|CONJUNTO|URBANIZACI[OÓ]N)\s+([A-ZÁÉÍÓÚÑ0-9][A-ZÁÉÍÓÚÑ0-9\s\-]{2,80})", text, re.IGNORECASE)
        return _clean(match.group(0)) if match else None

    def _bank_name(self, text: str) -> str | None:
        normalized = _normalize(text)
        banks = list(KNOWN_BANKS)
        banks.extend(self._catalog_values("banco"))
        banks.extend(self._catalog_values("banco_hipotecante"))
        for bank in dict.fromkeys(banks):
            if _normalize(bank) in normalized:
                return bank
        return None

    def _entities(self, blocks: list[NotarialDocumentBlock]) -> list[DetectedEntity]:
        entities: list[DetectedEntity] = []
        patterns = [
            ("real_estate_registration", "matricula_inmobiliaria", re.compile(r"\b\d{3}-\d{5,10}\b")),
            ("nit", "nit", re.compile(r"\b\d{3}(?:\.\d{3}){2}-\d\b")),
            ("money", "valor", re.compile(r"\$\s*\d{1,3}(?:\.\d{3})+(?:,\d{2})?\b")),
            ("email", "correo", re.compile(r"\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b", re.IGNORECASE)),
            ("identity_document", "numero_documento", re.compile(r"\b(?:C\.?C\.?|CEDULA)\s*(?:No\.?)?\s*(\d{1,3}(?:\.\d{3}){1,3})\b", re.IGNORECASE)),
            ("date", "fecha", re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b")),
        ]
        for block in blocks:
            text = block.text or ""
            for entity_type, field_code, pattern in patterns:
                for match in pattern.finditer(text):
                    value = match.group(1) if match.lastindex else match.group(0)
                    entities.append(
                        DetectedEntity(
                            entity_type=entity_type,
                            text=value,
                            normalized_text=_normalize(value),
                            canonical_field_code=field_code,
                            role=self._near_role(text, match.start()),
                            confidence=0.86,
                            block_id=block.id,
                        )
                    )
        return entities

    def _near_role(self, text: str, start: int) -> str | None:
        window = _normalize(text[max(0, start - 120): start + 120])
        for role in ("comprador", "vendedor", "otorgante", "acreedor", "deudor"):
            if role in window:
                return role
        return None

    def _confidence(self, document_type: str, acts: list[str], entities: list[DetectedEntity]) -> float:
        score = 0.45
        if document_type != "documento_notarial":
            score += 0.2
        if acts and acts != ["acto_notarial"]:
            score += 0.15
        if entities:
            score += min(0.2, len(entities) * 0.03)
        return min(score, 0.98)

    def _catalog_acts(self, normalized: str) -> list[str]:
        if self.db is None:
            return []
        if not _table_exists(self.db, "act_catalog"):
            return []
        try:
            rows = self.db.query(ActCatalog).filter(ActCatalog.is_active.is_(True)).all()
        except SQLAlchemyError:
            return []
        acts = []
        for row in rows:
            code = _normalize(row.code or "")
            label = _normalize(row.label or "")
            if (code and code in normalized) or (label and label in normalized):
                acts.append(row.code)
        try:
            corpus_rows = self.db.query(CorpusDocument.act_type).filter(CorpusDocument.act_type.isnot(None)).distinct().all() if _table_exists(self.db, "corpus_documents") else []
        except SQLAlchemyError:
            corpus_rows = []
        for (act_type,) in corpus_rows:
            if act_type and _normalize(act_type) in normalized:
                acts.append(act_type)
        return acts

    def _catalog_values(self, field_hint: str) -> list[str]:
        if self.db is None:
            return []
        values: list[str] = []
        try:
            definitions = self.db.query(FieldDefinition).filter(FieldDefinition.field_code.ilike(f"%{field_hint}%")).all() if _table_exists(self.db, "field_definitions") else []
            aliases = self.db.query(FieldAlias).filter(FieldAlias.canonical_field_code.ilike(f"%{field_hint}%")).all() if _table_exists(self.db, "field_aliases") else []
            patterns = self.db.query(FieldPattern).filter(FieldPattern.canonical_field_code.ilike(f"%{field_hint}%")).all() if _table_exists(self.db, "field_patterns") else []
            template_fields = self.db.query(TemplateField).filter(TemplateField.field_code.ilike(f"%{field_hint}%")).all() if _table_exists(self.db, "template_fields") else []
        except SQLAlchemyError:
            return []
        values.extend(row.display_name for row in definitions if row.display_name)
        values.extend(row.raw_field_code for row in aliases if row.raw_field_code)
        values.extend(row.example_value for row in patterns if row.example_value)
        values.extend(row.label for row in template_fields if row.label)
        return values


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_text = "".join(char for char in normalized if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", ascii_text.lower()).strip()


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip(" .,:;")


def _table_exists(db: Session, table_name: str) -> bool:
    try:
        return inspect(db.get_bind()).has_table(table_name)
    except SQLAlchemyError:
        return False
