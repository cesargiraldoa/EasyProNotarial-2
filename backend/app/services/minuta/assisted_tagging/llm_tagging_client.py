from __future__ import annotations

import json
import os
import re
import unicodedata

from app.services.minuta.assisted_tagging.llm_tagging_prompt import build_prompt
from app.services.minuta.assisted_tagging.models import DocxStructure, TaggingFieldProposal


MONEY_RE = re.compile(r"(?:\$?\s*)\d{1,3}(?:[.,]\d{3})+(?:,\d{2})?")
DOCUMENT_RE = re.compile(r"\b(?:C\.?C\.?|T\.?I\.?|NIT|PASAPORTE)\s*(?:No\.?|Nro\.?|numero)?\s*[\d.]{5,20}\b", re.IGNORECASE)
MATRICULA_RE = re.compile(r"\b\d{3}[-\s]\d{3,8}\b")
DATE_RE = re.compile(r"\b\d{1,2}\s+de\s+[A-Za-z]+(?:\s+de)?\s+\d{4}\b", re.IGNORECASE)
UPPER_NAME_RE = re.compile(r"\b[A-ZÁÉÍÓÚÜÑ]{3,}(?:\s+[A-ZÁÉÍÓÚÜÑ]{2,}){1,4}\b")

STOP_UPPER = {
    "NOTARIA",
    "NOTARIO",
    "ESCRITURA",
    "PUBLICA",
    "REPUBLICA",
    "COLOMBIA",
    "MUNICIPIO",
    "DEPARTAMENTO",
    "COMPRAVENTA",
    "HIPOTECA",
    "APARTAMENTO",
    "INMUEBLE",
    "MATRICULA",
    "CERTIFICADO",
}


def _strip_accents(value: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFKD", value) if not unicodedata.combining(ch))


def _field_code(label: str) -> str:
    raw = _strip_accents(label).lower()
    raw = re.sub(r"[^a-z0-9]+", "_", raw).strip("_")
    return raw[:80] or "campo"


def _label_from_text(text: str, kind: str, index: int) -> str:
    if kind == "nombre":
        return f"Nombre comprador {index}"
    if kind == "documento":
        return f"Documento comprador {index}"
    if kind == "valor":
        return "Valor venta" if index == 1 else f"Valor {index}"
    if kind == "fecha":
        return f"Fecha {index}"
    if kind == "matricula":
        return f"Matricula {index}"
    return f"Campo {index}"


class LlmTaggingClient:
    def propose(self, structure: DocxStructure, document_type: str) -> dict:
        api_key = (os.environ.get("OPENAI_API_KEY") or "").strip()
        allow_fallback = (os.environ.get("ASSISTED_TAGGING_ALLOW_FALLBACK") or "").strip().lower() == "true"
        model = os.environ.get("ASSISTED_TAGGING_MODEL", "gpt-4o-mini")
        if not api_key:
            if allow_fallback:
                return self._fallback(structure, "OPENAI_API_KEY no configurada.", model)
            raise RuntimeError("OPENAI_API_KEY no configurada. El fallback local requiere ASSISTED_TAGGING_ALLOW_FALLBACK=true.")
        try:
            payload = self._propose_with_openai(structure, document_type, model)
            payload["_meta"] = {"llm_mode": "openai", "model": model}
            return payload
        except Exception as exc:
            if allow_fallback:
                return self._fallback(structure, f"Error llamando al LLM: {exc}", model)
            raise RuntimeError(f"Error llamando al LLM y fallback no permitido: {exc}") from exc

    def _propose_with_openai(self, structure: DocxStructure, document_type: str, model: str) -> dict:
        from openai import OpenAI

        client = OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=build_prompt(structure, document_type),
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        content = response.choices[0].message.content or "{}"
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            return {"fields": []}
        return parsed

    def _fallback(self, structure: DocxStructure, cause: str, model: str) -> dict:
        payload = self._deterministic_proposal(structure)
        payload["_meta"] = {
            "llm_mode": "fallback",
            "cause": cause,
            "model_not_used": model,
        }
        return payload

    def _deterministic_proposal(self, structure: DocxStructure) -> dict:
        proposals: list[TaggingFieldProposal] = []
        seen: set[str] = set()
        counters: dict[str, int] = {}

        for block in structure.blocks:
            for kind, regex, section in (
                ("valor", MONEY_RE, "valores"),
                ("documento", DOCUMENT_RE, "personas"),
                ("matricula", MATRICULA_RE, "inmueble"),
                ("fecha", DATE_RE, "fechas"),
                ("nombre", UPPER_NAME_RE, "personas"),
            ):
                for match in regex.finditer(block.text):
                    text = " ".join(match.group(0).split())
                    if len(text) < 3:
                        continue
                    if kind == "nombre":
                        words = set(_strip_accents(text).upper().split())
                        if words & STOP_UPPER or len(words) < 2:
                            continue
                    normalized = text.upper()
                    if normalized in seen:
                        continue
                    seen.add(normalized)
                    counters[kind] = counters.get(kind, 0) + 1
                    label = _label_from_text(text, kind, counters[kind])
                    proposals.append(
                        TaggingFieldProposal(
                            field_code=_field_code(label),
                            label=label,
                            text=text,
                            section=section,
                            confidence=0.72 if kind != "nombre" else 0.62,
                            block_id=block.id,
                            reason="Detectado por patron notarial local",
                            source="embedded",
                        )
                    )

        return {"fields": [proposal.to_dict() for proposal in proposals[:80]]}
