from __future__ import annotations

import re
import unicodedata
from collections import OrderedDict

from tools.notarial_template_lab.models import (
    DocumentMap,
    FieldProposal,
    Occurrence,
    ProposalOccurrence,
)


ROLE_LABELS = {
    "comprador": ("comprador", "compradora", "compradores"),
    "vendedor": ("vendedor", "vendedora", "vendedores"),
    "otorgante": ("otorgante", "otorgantes"),
    "hipotecante": ("hipotecante", "hipotecantes"),
    "acreedor": ("acreedor", "acreedora", "acreedores"),
    "deudor": ("deudor", "deudora", "deudores"),
    "apoderado": ("apoderado", "apoderada", "apoderados"),
    "poderdante": ("poderdante", "poderdantes"),
}

CONTEXT_LABELS = {
    "inmueble": ("inmueble", "predio", "bien"),
    "apartamento": ("apartamento", "apto", "unidad"),
    "casa": ("casa", "vivienda"),
    "matricula": ("matricula", "matricula inmobiliaria"),
    "valor_acto": ("valor del acto", "cuantia", "valor acto"),
    "precio": ("precio", "valor de venta", "compraventa"),
    "cuota_inicial": ("cuota inicial",),
    "saldo": ("saldo",),
    "credito_hipotecario": ("credito hipotecario", "hipoteca"),
    "avaluo": ("avaluo", "avaluo catastral"),
    "coeficiente": ("coeficiente", "copropiedad"),
    "direccion": ("direccion", "nomenclatura", "domicilio"),
    "correo": ("correo", "email", "mail"),
    "celular": ("celular", "telefono", "movil"),
    "notaria": ("notaria", "notarial"),
    "notario": ("notario", "notaria titular"),
    "protocolo": ("protocolo", "escritura", "otorgamiento"),
    "documento": ("cedula", "c.c", "identificacion", "documento"),
    "nit": ("nit",),
    "codigo_predial": ("codigo predial", "cedula catastral", "catastro", "catastral"),
}

TITLE_WORDS = {
    "capitulo",
    "clausula",
    "paragrafo",
    "comparecencia",
    "declaraciones",
    "otorgamiento",
    "autorizacion",
    "linderos",
}


class FieldProposer:
    def propose(self, document_map: DocumentMap) -> list[FieldProposal]:
        proposals: OrderedDict[tuple[str, str], FieldProposal] = OrderedDict()
        blocks_by_id = {block.block_id: block for block in document_map.blocks}

        for occurrence_type, occurrences in document_map.occurrences_index.items():
            for occurrence in occurrences:
                block = blocks_by_id.get(occurrence.block_id)
                context = " ".join([occurrence.before, occurrence.text, occurrence.after])
                proposal = self._proposal_for_occurrence(occurrence_type, occurrence, context)
                key = (proposal.field_key, proposal.value)
                existing = proposals.get(key)
                if existing is None:
                    proposals[key] = proposal
                else:
                    existing.occurrences.extend(proposal.occurrences)
                    existing.confidence = min(0.99, max(existing.confidence, proposal.confidence) + 0.02)
                    if existing.apply_strategy != "review_required" and len(existing.occurrences) > 1:
                        existing.apply_strategy = "all_occurrences"

        return sorted(proposals.values(), key=lambda item: (-item.confidence, item.field_key, item.value))

    def _proposal_for_occurrence(self, occurrence_type: str, occurrence: Occurrence, context: str) -> FieldProposal:
        normalized_context = normalize_for_match(context)
        normalized_before = normalize_for_match(occurrence.before)
        role = find_role(normalized_context)
        label_key = find_context_label(normalized_context)

        field_key, label, confidence, proposal_type, apply_strategy, reason = self._classify(
            occurrence_type,
            occurrence.text,
            normalized_context,
            normalized_before,
            role,
            label_key,
        )

        return FieldProposal(
            field_key=field_key,
            label=label,
            marker=f"{{{{{field_key}}}}}",
            value=occurrence.text,
            confidence=round(confidence, 2),
            proposal_type=proposal_type,
            occurrences=[
                ProposalOccurrence(
                    occurrence_id=occurrence.occurrence_id,
                    block_id=occurrence.block_id,
                    location=occurrence.location,
                    text=occurrence.text,
                    start=occurrence.start,
                    end=occurrence.end,
                    before=occurrence.before,
                    after=occurrence.after,
                )
            ],
            apply_strategy=apply_strategy,
            reason=reason,
        )

    def _classify(self, occurrence_type: str, value: str, context: str, before_context: str, role: str | None, label_key: str | None):
        if occurrence_type == "real_estate_registration":
            if label_key in {"matricula", "inmueble"}:
                return "matricula_inmobiliaria", "Matricula inmobiliaria", 0.88, "project_field", "all_occurrences", "Patron de matricula con contexto de inmueble o matricula."
            return "matricula_inmobiliaria_revision", "Matricula inmobiliaria por revisar", 0.55, "review_required", "review_required", "Patron de matricula sin rotulo cercano suficiente."

        if occurrence_type == "money":
            money_key = money_field_key(before_context) or money_field_key(context)
            if money_key:
                return money_key, human_label(money_key), 0.86, "document_field", "all_occurrences", "Valor monetario con rotulo notarial cercano."
            return "valor_monetario_revision", "Valor monetario por revisar", 0.52, "review_required", "review_required", "Valor monetario sin rotulo claro de precio, acto, cuota, saldo, credito o avaluo."

        if occurrence_type == "email":
            key = with_role("correo", role)
            return key, human_label(key), 0.9, "document_field", "all_occurrences", "Correo electronico detectable por patron tecnico."

        if occurrence_type == "phone":
            key = with_role("celular", role)
            confidence = 0.86 if label_key == "celular" or role else 0.72
            strategy = "all_occurrences" if confidence >= 0.8 else "review_required"
            proposal_type = "document_field" if confidence >= 0.8 else "review_required"
            return key if confidence >= 0.8 else "telefono_revision", human_label(key), confidence, proposal_type, strategy, "Telefono o celular detectado por patron tecnico y contexto cercano."

        if occurrence_type == "nit":
            key = with_role("nit", role)
            return key, human_label(key), 0.86, "document_field", "all_occurrences", "NIT con digito de verificacion detectado."

        if occurrence_type == "dotted_document":
            if label_key == "documento" or role:
                key = with_role("numero_documento", role)
                return key, human_label(key), 0.84, "document_field", "all_occurrences", "Documento con puntos y contexto de identificacion."
            return "numero_documento_revision", "Numero documento por revisar", 0.5, "review_required", "review_required", "Numero con puntos sin rol ni rotulo de identificacion cercano."

        if occurrence_type == "long_property_code":
            if label_key == "codigo_predial":
                return "codigo_predial", "Codigo predial", 0.82, "project_field", "all_occurrences", "Codigo largo con contexto catastral o predial."
            return "codigo_largo_revision", "Codigo largo por revisar", 0.45, "review_required", "review_required", "Codigo numerico largo sin rotulo predial/catastral suficiente."

        if occurrence_type == "date":
            if label_key in {"protocolo", "notaria"}:
                return "fecha_otorgamiento", "Fecha otorgamiento", 0.82, "document_field", "all_occurrences", "Fecha con contexto de protocolo, escritura u otorgamiento."
            return "fecha_revision", "Fecha por revisar", 0.48, "review_required", "review_required", "Fecha sin contexto notarial especifico."

        if occurrence_type == "uppercase_relevant_phrase":
            if looks_like_title(value):
                return "frase_mayuscula_revision", "Frase mayuscula por revisar", 0.35, "review_required", "review_required", "La frase parece titulo, clausula o encabezado; no se reemplaza automaticamente."
            if role:
                key = with_role("nombre", role)
                return key, human_label(key), 0.72, "review_required", "review_required", "Frase en mayusculas cerca de rol notarial; requiere revision antes de marcar."
            return "frase_mayuscula_revision", "Frase mayuscula por revisar", 0.3, "review_required", "review_required", "Frase en mayusculas sin rol claro."

        return "campo_revision", "Campo por revisar", 0.2, "review_required", "review_required", "Ocurrencia tecnica no clasificada."


def normalize_for_match(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def find_role(context: str) -> str | None:
    for role, labels in ROLE_LABELS.items():
        if any(label in context for label in labels):
            return role
    return None


def find_context_label(context: str) -> str | None:
    for key, labels in CONTEXT_LABELS.items():
        if any(label in context for label in labels):
            return key
    return None


def money_field_key(context: str) -> str | None:
    candidates = [
        ("cuota_inicial", "valor_cuota_inicial"),
        ("saldo", "valor_saldo"),
        ("credito hipotecario", "valor_credito_hipotecario"),
        ("hipoteca", "valor_credito_hipotecario"),
        ("avaluo", "valor_avaluo"),
        ("precio", "valor_precio"),
        ("valor de venta", "valor_precio"),
        ("valor del acto", "valor_acto"),
        ("cuantia", "valor_acto"),
    ]
    matches = [(context.rfind(token), key) for token, key in candidates if token in context]
    if not matches:
        return None
    return max(matches, key=lambda item: item[0])[1]


def with_role(prefix: str, role: str | None) -> str:
    return f"{prefix}_{role}" if role else prefix


def human_label(key: str) -> str:
    words = key.split("_")
    return " ".join([words[0].capitalize()] + [word.lower() for word in words[1:]])


def looks_like_title(value: str) -> bool:
    normalized = normalize_for_match(value)
    if any(word in normalized for word in TITLE_WORDS):
        return True
    words = normalized.split()
    letters = [char for char in value if char.isalpha()]
    uppercase_ratio = (
        sum(1 for char in letters if char.upper() == char and char.lower() != char) / len(letters)
        if letters
        else 0
    )
    return len(words) > 8 and uppercase_ratio > 0.75
