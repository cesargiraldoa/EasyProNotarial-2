from __future__ import annotations

import json
import time
from dataclasses import asdict
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.services.biblioteca_motor.contracts import FieldDefinition
from app.services.biblioteca_motor.document_map import DocumentMap


DEFAULT_BIBLIOTECA_MODEL = "gpt-4o-mini"
PROMPT_VERSION = "biblioteca-llm-v1"


class LLMExtractorError(RuntimeError):
    code = "llm_error"


class LLMExtractorUnavailable(LLMExtractorError):
    code = "llm_unavailable"


class LLMExtractorTimeout(LLMExtractorError):
    code = "llm_timeout"


class LLMExtractorInvalidResponse(LLMExtractorError):
    code = "llm_invalid_response"


class LLMEntity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entity_ref: str = Field(min_length=1, max_length=120)
    entity_type: str = Field(min_length=1, max_length=80)
    display_name: str | None = Field(default=None, max_length=240)
    document_number: str | None = Field(default=None, max_length=120)
    nit: str | None = Field(default=None, max_length=120)
    attributes: dict[str, Any] = Field(default_factory=dict)


class LLMRole(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entity_ref: str = Field(min_length=1, max_length=120)
    role: str = Field(min_length=1, max_length=80)


class LLMFieldInstance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field_instance_ref: str = Field(min_length=1, max_length=120)
    entity_ref: str | None = Field(default=None, max_length=120)
    role: str | None = Field(default=None, max_length=80)
    candidate_type: str = Field(min_length=1, max_length=80)
    base_field_code: str = Field(min_length=1, max_length=120)
    suggested_field_code: str | None = Field(default=None, max_length=120)
    visible_code: str | None = Field(default=None, max_length=120)
    label: str | None = Field(default=None, max_length=200)
    category: str | None = Field(default=None, max_length=80)
    catalog_match: bool = False
    reason: str | None = Field(default=None, max_length=400)


class LLMOccurrence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    occurrence_ref: str = Field(min_length=1, max_length=120)
    field_instance_ref: str = Field(min_length=1, max_length=120)
    block_id: str = Field(min_length=1, max_length=120)
    exact_text: str = Field(min_length=1)
    occurrence_index: int = Field(ge=1)
    left_context: str = ""
    right_context: str = ""
    confidence: float = Field(ge=0, le=1)
    reason: str | None = Field(default=None, max_length=400)


class LLMUnmappedField(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field_instance_ref: str = Field(min_length=1, max_length=120)
    proposed_code: str = Field(min_length=1, max_length=120)
    label: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=80)
    field_type: str = Field(default="text", max_length=40)
    reason: str | None = Field(default=None, max_length=400)


class LLMExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_type: str = Field(min_length=1, max_length=120)
    entities: list[LLMEntity] = Field(default_factory=list)
    roles: list[LLMRole] = Field(default_factory=list)
    field_instances: list[LLMFieldInstance] = Field(default_factory=list)
    occurrences: list[LLMOccurrence] = Field(default_factory=list)
    unmapped_fields: list[LLMUnmappedField] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    reason: str | None = Field(default=None, max_length=1000)
    diagnostics: dict[str, Any] = Field(default_factory=dict)


class LLMExtractionAudit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str
    prompt_version: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    latency_ms: int
    cost_usd: float | None = None


class LLMExtractionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    extraction: LLMExtraction
    audit: LLMExtractionAudit


class BibliotecaLLMExtractor(Protocol):
    model: str
    prompt_version: str

    def extract(
        self,
        document_map: DocumentMap,
        fields: list[FieldDefinition],
        *,
        active_profile: dict[str, Any] | None = None,
        examples: list[dict[str, Any]] | None = None,
    ) -> LLMExtractionResult:
        ...

    def repair_occurrence(
        self,
        *,
        block_id: str,
        block_text: str,
        occurrence: LLMOccurrence,
    ) -> LLMOccurrence | None:
        ...


class StaticBibliotecaLLMExtractor:
    def __init__(self, extraction: dict[str, Any] | LLMExtraction, *, model: str = "static-test-model", prompt_version: str = PROMPT_VERSION) -> None:
        self.model = model
        self.prompt_version = prompt_version
        self._extraction = extraction

    def extract(
        self,
        document_map: DocumentMap,
        fields: list[FieldDefinition],
        *,
        active_profile: dict[str, Any] | None = None,
        examples: list[dict[str, Any]] | None = None,
    ) -> LLMExtractionResult:
        started = time.perf_counter()
        extraction = self._extraction if isinstance(self._extraction, LLMExtraction) else LLMExtraction.model_validate(self._extraction)
        return LLMExtractionResult(
            extraction=extraction,
            audit=LLMExtractionAudit(
                model=self.model,
                prompt_version=self.prompt_version,
                latency_ms=max(0, int((time.perf_counter() - started) * 1000)),
            ),
        )

    def repair_occurrence(self, *, block_id: str, block_text: str, occurrence: LLMOccurrence) -> LLMOccurrence | None:
        return None


class OpenAIBibliotecaExtractor:
    def __init__(self, api_key: str | None, *, model: str = DEFAULT_BIBLIOTECA_MODEL, prompt_version: str = PROMPT_VERSION, timeout_seconds: float = 30.0) -> None:
        self.api_key = (api_key or "").strip()
        self.model = model
        self.prompt_version = prompt_version
        self.timeout_seconds = timeout_seconds

    def extract(
        self,
        document_map: DocumentMap,
        fields: list[FieldDefinition],
        *,
        active_profile: dict[str, Any] | None = None,
        examples: list[dict[str, Any]] | None = None,
    ) -> LLMExtractionResult:
        if not self.api_key:
            raise LLMExtractorUnavailable("OPENAI_API_KEY no configurada para Motor de Biblioteca LLM.")
        started = time.perf_counter()
        response = self._chat_completion(_prompt_payload(document_map, fields, active_profile=active_profile, examples=examples))
        latency_ms = max(0, int((time.perf_counter() - started) * 1000))
        extraction = _parse_extraction_response(response)
        usage = getattr(response, "usage", None)
        return LLMExtractionResult(
            extraction=extraction,
            audit=LLMExtractionAudit(
                model=self.model,
                prompt_version=self.prompt_version,
                input_tokens=getattr(usage, "prompt_tokens", None),
                output_tokens=getattr(usage, "completion_tokens", None),
                latency_ms=latency_ms,
            ),
        )

    def repair_occurrence(self, *, block_id: str, block_text: str, occurrence: LLMOccurrence) -> LLMOccurrence | None:
        if not self.api_key:
            return None
        payload = {
            "instruction": "Corrige un anclaje dentro de un solo bloque. Devuelve JSON con occurrence o null. No inventes texto.",
            "block": {"block_id": block_id, "text": block_text},
            "occurrence": occurrence.model_dump(),
            "schema": {
                "occurrence": {
                    "occurrence_ref": "string",
                    "field_instance_ref": "string",
                    "block_id": block_id,
                    "exact_text": "texto literal existente en block.text",
                    "occurrence_index": "entero 1-based",
                    "left_context": "texto literal inmediatamente anterior cuando exista",
                    "right_context": "texto literal inmediatamente posterior cuando exista",
                    "confidence": "0..1",
                    "reason": "string",
                },
            },
        }
        try:
            response = self._chat_completion(payload)
            raw = json.loads(response.choices[0].message.content or "{}")
            item = raw.get("occurrence")
            return LLMOccurrence.model_validate(item) if item else None
        except Exception:
            return None

    def _chat_completion(self, payload: dict[str, Any]):
        try:
            from openai import APITimeoutError, OpenAI
        except Exception as exc:  # pragma: no cover
            raise LLMExtractorUnavailable("openai package unavailable") from exc
        client = OpenAI(api_key=self.api_key, timeout=self.timeout_seconds)
        try:
            return client.chat.completions.create(
                model=self.model,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres un extractor juridico notarial LLM-first. Debes leer el DocumentMap completo, "
                            "detectar datos variables juridicamente utiles, agrupar entidades y roles, y devolver "
                            "solo JSON valido segun el contrato. No calcules offsets ni modifiques documentos. "
                            "exact_text debe copiar texto literal existente en el block_id."
                        ),
                    },
                    {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
                ],
            )
        except (APITimeoutError, TimeoutError) as exc:
            raise LLMExtractorTimeout("timeout") from exc
        except LLMExtractorError:
            raise
        except Exception as exc:
            raise LLMExtractorUnavailable("provider_error") from exc


def _prompt_payload(
    document_map: DocumentMap,
    fields: list[FieldDefinition],
    *,
    active_profile: dict[str, Any] | None,
    examples: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    return {
        "prompt_version": PROMPT_VERSION,
        "instructions": {
            "extract_all_useful_fields": True,
            "catalog_is_available_assignments_not_detection_limit": True,
            "group_repeated_entities": True,
            "separate_people_with_same_role": True,
            "recognize_multiple_roles": True,
            "propose_unmapped_fields": True,
            "return_literal_anchors_only": True,
        },
        "catalog": [asdict(field) for field in fields],
        "active_notary_profile": active_profile or {},
        "historical_examples": examples or [],
        "document_map": document_map.to_prompt_payload(),
    }


def _parse_extraction_response(response: Any) -> LLMExtraction:
    try:
        content = response.choices[0].message.content or "{}"
        parsed = json.loads(content)
        return LLMExtraction.model_validate(parsed)
    except (json.JSONDecodeError, AttributeError, IndexError, TypeError, ValidationError) as exc:
        raise LLMExtractorInvalidResponse("invalid_llm_json") from exc
