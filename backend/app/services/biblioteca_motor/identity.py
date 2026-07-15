from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any

from app.services.biblioteca_motor.contracts import (
    DetectedCandidate,
    FieldDefinition,
    FieldInstance,
    LegalEntity,
    LegalRoleAssignment,
)


ROLE_ALIASES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("COMPRADOR", ("COMPRADOR", "COMPRADORES", "COMPRA")),
    ("VENDEDOR", ("VENDEDOR", "VENDEDORES", "VENDE")),
    ("OTORGANTE", ("OTORGANTE", "OTORGANTES", "COMPARECIENTE", "COMPARECIENTES")),
    ("ACREEDOR", ("ACREEDOR", "ACREEDORES", "BANCO", "HIPOTECANTE")),
    ("DEUDOR", ("DEUDOR", "DEUDORES")),
    ("APODERADO", ("APODERADO", "APODERADA", "APODERADOS")),
    ("PODERDANTE", ("PODERDANTE", "PODERDANTES")),
)


@dataclass(frozen=True)
class CandidateIdentity:
    field_instance: FieldInstance
    entity: LegalEntity | None
    role_assignment: LegalRoleAssignment | None
    visible_code: str


@dataclass(frozen=True)
class IdentityModel:
    candidate_identities: dict[str, CandidateIdentity]
    entities: list[LegalEntity]
    role_assignments: list[LegalRoleAssignment]
    field_instances: list[FieldInstance]


def build_identity_model(candidates: list[DetectedCandidate], field_by_code: dict[str, FieldDefinition]) -> IdentityModel:
    builder = _IdentityBuilder(field_by_code)
    return builder.build(candidates)


class _IdentityBuilder:
    def __init__(self, field_by_code: dict[str, FieldDefinition]) -> None:
        self.field_by_code = field_by_code
        self.entities_by_key: dict[str, _MutableEntity] = {}
        self.role_ordinals: dict[str, list[str]] = {}
        self.role_assignments_by_key: dict[tuple[str, str], LegalRoleAssignment] = {}
        self.field_instances: dict[str, FieldInstance] = {}
        self.candidate_identities: dict[str, CandidateIdentity] = {}

    def build(self, candidates: list[DetectedCandidate]) -> IdentityModel:
        by_block: dict[Any, list[DetectedCandidate]] = {}
        for candidate in candidates:
            by_block.setdefault(candidate.location.get("block_index"), []).append(candidate)

        for block_candidates in by_block.values():
            ordered = sorted(block_candidates, key=lambda item: (int(item.location.get("char_start") or 0), item.candidate_id))
            self._process_block(ordered)

        entities = [item.to_contract(self._role_ids_for_entity(item.entity_id)) for item in self.entities_by_key.values()]
        return IdentityModel(
            candidate_identities=self.candidate_identities,
            entities=sorted(entities, key=lambda item: item.entity_id),
            role_assignments=sorted(self.role_assignments_by_key.values(), key=lambda item: item.assignment_id),
            field_instances=sorted(self.field_instances.values(), key=lambda item: item.field_instance_id),
        )

    def _process_block(self, candidates: list[DetectedCandidate]) -> None:
        if not candidates:
            return
        names = [item for item in candidates if item.candidate_type in {"person_name", "legal_person_name", "bank"}]
        docs = [item for item in candidates if item.candidate_type in {"document_number", "nit"}]

        for candidate in candidates:
            role = _role_from_candidate(candidate)
            entity_type = _entity_type(candidate)
            if entity_type is None:
                continue

            related_name = candidate
            related_doc = _nearest_document(candidate, docs) if candidate.candidate_type in {"person_name", "legal_person_name", "bank"} else candidate
            if candidate.candidate_type in {"document_number", "nit"}:
                related_name = _nearest_name(candidate, names) or candidate

            if candidate.candidate_type == "nit" and related_name.candidate_type == "person_name":
                entity_type = "legal_person"
            if candidate.candidate_type == "bank" or related_name.candidate_type == "bank":
                entity_type = "financial_entity"
                role = role or "ACREEDOR"

            entity = self._entity_for(candidate, related_name, related_doc, entity_type)
            role_assignment = self._role_assignment(entity.entity_id, role) if role else None
            field_instance = self._field_instance_for(candidate, entity, role_assignment)
            self.candidate_identities[candidate.candidate_id] = CandidateIdentity(
                field_instance=field_instance,
                entity=entity.to_contract(self._role_ids_for_entity(entity.entity_id)),
                role_assignment=role_assignment,
                visible_code=field_instance.visible_code,
            )

    def _entity_for(
        self,
        candidate: DetectedCandidate,
        related_name: DetectedCandidate,
        related_doc: DetectedCandidate | None,
        entity_type: str,
    ) -> "_MutableEntity":
        name = related_name.original_text.strip() if related_name.candidate_type not in {"document_number", "nit"} else ""
        normalized_name = _normalize(name)
        document_number = None
        nit = None
        if related_doc and related_doc.candidate_type == "document_number":
            document_number = _digits(related_doc.original_text)
        if related_doc and related_doc.candidate_type == "nit":
            nit = _digits(related_doc.original_text)
        if candidate.candidate_type == "document_number":
            document_number = _digits(candidate.original_text)
        if candidate.candidate_type == "nit":
            nit = _digits(candidate.original_text)

        if entity_type == "natural_person":
            identity_key = f"person:{document_number or normalized_name or _normalize(candidate.original_text)}"
        elif entity_type == "financial_entity":
            identity_key = f"financial:{nit or normalized_name or _normalize(candidate.original_text)}"
        elif entity_type == "legal_person":
            identity_key = f"legal:{nit or normalized_name or _normalize(candidate.original_text)}"
        else:
            identity_key = f"unknown:{_normalize(candidate.original_text)}"

        if normalized_name:
            for existing in self.entities_by_key.values():
                if existing.entity_type == entity_type and existing.normalized_name == normalized_name:
                    existing.document_number = existing.document_number or document_number
                    existing.nit = existing.nit or nit
                    return existing

        entity = self.entities_by_key.get(identity_key)
        if entity is None:
            entity_id = "ent_" + _hash(identity_key)[:14]
            entity = _MutableEntity(
                entity_id=entity_id,
                entity_type=entity_type,
                display_name=name or candidate.original_text.strip(),
                normalized_name=normalized_name or _normalize(candidate.original_text),
                document_number=document_number,
                nit=nit,
                attributes={"identity_key": identity_key},
            )
            self.entities_by_key[identity_key] = entity
        else:
            entity.display_name = entity.display_name or name or candidate.original_text.strip()
            entity.normalized_name = entity.normalized_name or normalized_name
            entity.document_number = entity.document_number or document_number
            entity.nit = entity.nit or nit
        return entity

    def _role_assignment(self, entity_id: str, role: str | None) -> LegalRoleAssignment | None:
        if not role:
            return None
        key = (entity_id, role)
        existing = self.role_assignments_by_key.get(key)
        if existing is not None:
            return existing
        entity_ids = self.role_ordinals.setdefault(role, [])
        if entity_id not in entity_ids:
            entity_ids.append(entity_id)
        ordinal = entity_ids.index(entity_id) + 1
        visible_role_code = f"{role}_{ordinal}"
        assignment = LegalRoleAssignment(
            assignment_id="role_" + _hash(f"{entity_id}:{role}")[:14],
            entity_id=entity_id,
            role=role,
            ordinal=ordinal,
            visible_role_code=visible_role_code,
        )
        self.role_assignments_by_key[key] = assignment
        return assignment

    def _field_instance_for(
        self,
        candidate: DetectedCandidate,
        entity: "_MutableEntity",
        role_assignment: LegalRoleAssignment | None,
    ) -> FieldInstance:
        base_field_code, visible_code = _visible_code(candidate, entity.entity_type, role_assignment)
        field_code = _catalog_code(base_field_code, visible_code, self.field_by_code)
        field = self.field_by_code.get(field_code)
        catalog_status = "matched" if field is not None else "unmapped"
        field_label = field.label if field is not None else _label_from_visible_code(visible_code)
        category = field.category if field is not None else _category_for(candidate, entity.entity_type)
        instance_seed = f"{entity.entity_id}:{base_field_code}"
        field_instance_id = "fi_" + _hash(instance_seed)[:18]
        existing = self.field_instances.get(field_instance_id)
        if existing is not None:
            return existing
        role_ids = (role_assignment.assignment_id,) if role_assignment else ()
        instance = FieldInstance(
            field_instance_id=field_instance_id,
            base_field_code=base_field_code,
            visible_code=visible_code,
            field_code=field_code or visible_code,
            field_label=field_label,
            category=category,
            catalog_status=catalog_status,  # type: ignore[arg-type]
            entity_id=entity.entity_id,
            role=role_assignment.role if role_assignment else None,
            role_ordinal=role_assignment.ordinal if role_assignment else None,
            role_assignment_ids=role_ids,
        )
        self.field_instances[field_instance_id] = instance
        return instance

    def _role_ids_for_entity(self, entity_id: str) -> tuple[str, ...]:
        role_ids = [
            assignment.assignment_id
            for assignment in self.role_assignments_by_key.values()
            if assignment.entity_id == entity_id
        ]
        return tuple(sorted(role_ids))


@dataclass
class _MutableEntity:
    entity_id: str
    entity_type: str
    display_name: str
    normalized_name: str
    document_number: str | None = None
    nit: str | None = None
    attributes: dict[str, Any] | None = None

    def to_contract(self, role_ids: tuple[str, ...]) -> LegalEntity:
        return LegalEntity(
            entity_id=self.entity_id,
            entity_type=self.entity_type,  # type: ignore[arg-type]
            display_name=self.display_name,
            normalized_name=self.normalized_name,
            document_number=self.document_number,
            nit=self.nit,
            attributes=self.attributes or {},
            role_ids=role_ids,
        )


def fallback_field_instance(
    candidate: DetectedCandidate,
    field_code: str,
    field: FieldDefinition | None,
) -> FieldInstance:
    base = field_code if field is not None else candidate.candidate_type.upper()
    visible = field_code or provisional_visible_code(candidate)
    catalog_status = "matched" if field is not None else "unmapped"
    field_instance_id = ("fi_" if field is not None else "prov_") + _hash(
        f"{base}:{_normalize(candidate.original_text)}",
    )[:18]
    return FieldInstance(
        field_instance_id=field_instance_id,
        base_field_code=base,
        visible_code=visible,
        field_code=field.code if field is not None else visible,
        field_label=field.label if field is not None else "Campo nuevo por definir",
        category=field.category if field is not None else _category_for(candidate, "unknown"),
        catalog_status=catalog_status,  # type: ignore[arg-type]
    )


def provisional_visible_code(candidate: DetectedCandidate) -> str:
    normalized_value = _normalize(candidate.original_text)
    digest = _hash(f"{candidate.candidate_type}:{normalized_value}")[:12].upper()
    candidate_type = re.sub(r"[^A-Z0-9]+", "_", candidate.candidate_type.upper()).strip("_") or "OTRO"
    return f"PENDING_FIELD_{candidate_type}_{digest}"


def occurrence_id_for(candidate_id: str, field_instance_id: str) -> str:
    return "occ_" + _hash(f"{candidate_id}:{field_instance_id}")[:12]


def _nearest_name(candidate: DetectedCandidate, names: list[DetectedCandidate]) -> DetectedCandidate | None:
    previous = [
        item for item in names
        if int(item.location.get("char_start") or 0) <= int(candidate.location.get("char_start") or 0)
    ]
    if previous:
        return sorted(previous, key=lambda item: int(item.location.get("char_start") or 0))[-1]
    if names:
        return sorted(names, key=lambda item: abs(int(item.location.get("char_start") or 0) - int(candidate.location.get("char_start") or 0)))[0]
    return None


def _nearest_document(candidate: DetectedCandidate, docs: list[DetectedCandidate]) -> DetectedCandidate | None:
    if candidate.candidate_type == "bank":
        nit_docs = [item for item in docs if item.candidate_type == "nit"]
        if nit_docs:
            return sorted(nit_docs, key=lambda item: abs(int(item.location.get("char_start") or 0) - int(candidate.location.get("char_end") or 0)))[0]
    following = [
        item for item in docs
        if int(item.location.get("char_start") or 0) >= int(candidate.location.get("char_end") or 0)
    ]
    if following:
        return sorted(following, key=lambda item: int(item.location.get("char_start") or 0))[0]
    return None


def _role_from_candidate(candidate: DetectedCandidate) -> str | None:
    text = _normalize(f"{candidate.context_before} {candidate.original_text} {candidate.context_after}")
    if re.search(r"\bOTORGANTES?\b", text):
        return "OTORGANTE"
    for role, aliases in ROLE_ALIASES:
        if any(alias in text for alias in aliases):
            return role
    return None


def _entity_type(candidate: DetectedCandidate) -> str | None:
    if candidate.candidate_type in {"person_name", "document_number"}:
        return "natural_person"
    if candidate.candidate_type in {"legal_person_name", "nit"}:
        return "legal_person"
    if candidate.candidate_type == "bank":
        return "financial_entity"
    return None


def _visible_code(
    candidate: DetectedCandidate,
    entity_type: str,
    role_assignment: LegalRoleAssignment | None,
) -> tuple[str, str]:
    role_code = role_assignment.visible_role_code if role_assignment else None
    if candidate.candidate_type == "person_name":
        if role_code:
            return "NOMBRE", role_code
        return "NOMBRE_PERSONA", "NOMBRE_PERSONA"
    if candidate.candidate_type == "document_number":
        if role_code:
            return "NUMERO_DOCUMENTO", f"CEDULA_{role_code}"
        return "NUMERO_DOCUMENTO", "NUMERO_DOCUMENTO"
    if candidate.candidate_type == "bank":
        if role_code:
            return "NOMBRE_ENTIDAD_FINANCIERA", f"BANCO_{role_code}"
        return "NOMBRE_ENTIDAD_FINANCIERA", "BANCO"
    if candidate.candidate_type == "legal_person_name" or entity_type == "legal_person":
        if candidate.candidate_type == "nit":
            if role_code:
                return "NIT", f"NIT_{role_code}"
            return "NIT", "NIT_PERSONA_JURIDICA"
        if role_code:
            return "RAZON_SOCIAL", f"RAZON_SOCIAL_{role_code}"
        return "RAZON_SOCIAL", "RAZON_SOCIAL"
    return candidate.candidate_type.upper(), candidate.candidate_type.upper()


def _catalog_code(base_field_code: str, visible_code: str, field_by_code: dict[str, FieldDefinition]) -> str:
    candidates = [visible_code]
    if visible_code.startswith("CEDULA_"):
        suffix = visible_code.removeprefix("CEDULA_")
        candidates.extend([f"DOCUMENTO_{suffix}", f"NUMERO_DOCUMENTO_{suffix}"])
    if base_field_code == "NOMBRE" and visible_code:
        candidates.append(f"NOMBRE_{visible_code}")
    if base_field_code == "NOMBRE_ENTIDAD_FINANCIERA":
        candidates.extend(["BANCO", "ENTIDAD_FINANCIERA"])
    if base_field_code == "RAZON_SOCIAL":
        candidates.extend(["RAZON_SOCIAL", "NOMBRE_PERSONA_JURIDICA"])
    if base_field_code == "NIT":
        candidates.extend(["NIT", "NIT_PERSONA_JURIDICA"])
    candidates.append(base_field_code)
    for code in candidates:
        if code in field_by_code:
            return code
    return visible_code


def _category_for(candidate: DetectedCandidate, entity_type: str) -> str:
    if entity_type == "legal_person":
        return "persona_juridica"
    if entity_type == "financial_entity":
        return "entidad"
    if entity_type == "natural_person":
        return "persona"
    mapping = {
        "matricula_inmobiliaria": "inmueble",
        "codigo_catastral": "inmueble",
        "area": "inmueble",
        "address": "ubicacion",
        "money": "valor",
        "date": "fecha",
        "deed_number": "escritura",
        "email": "contacto",
        "phone": "contacto",
    }
    return mapping.get(candidate.candidate_type, "otro")


def _label_from_visible_code(value: str) -> str:
    return value.replace("_", " ").title()


def _normalize(value: str) -> str:
    replacements = {
        "Á": "A",
        "É": "E",
        "Í": "I",
        "Ó": "O",
        "Ú": "U",
        "Ü": "U",
        "Ñ": "N",
        "á": "A",
        "é": "E",
        "í": "I",
        "ó": "O",
        "ú": "U",
        "ü": "U",
        "ñ": "N",
    }
    normalized = "".join(replacements.get(char, char.upper()) for char in value)
    return re.sub(r"\s+", " ", normalized).strip()


def _digits(value: str) -> str:
    return re.sub(r"\D+", "", value)


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
