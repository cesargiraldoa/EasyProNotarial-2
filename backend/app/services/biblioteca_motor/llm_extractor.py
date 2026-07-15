from __future__ import annotations

import json
import os
import time
from dataclasses import asdict
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.services.biblioteca_motor.contracts import FieldDefinition
from app.services.biblioteca_motor.document_map import DocumentMap


DEFAULT_BIBLIOTECA_MODEL = "gpt-4o-mini"
PROMPT_VERSION = "biblioteca-llm-v2-structured"
DEFAULT_TIMEOUT_SECONDS = 120.0
DEFAULT_MAX_OUTPUT_TOKENS = 16384


class LLMExtractorError(RuntimeError):
    code = "llm_error"


class LLMExtractorUnavailable(LLMExtractorError):
    code = "llm_unavailable"


class LLMExtractorTimeout(LLMExtractorError):
    code = "llm_timeout"


class LLMExtractorInvalidResponse(LLMExtractorError):
    code = "llm_invalid_response"


class LLMExtractorTruncated(LLMExtractorInvalidResponse):
    code = "llm_output_truncated"


class LLMKeyValue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(min_length=1, max_length=120)
    value: str = Field(max_length=1000)


class LLMEntity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entity_ref: str = Field(min_length=1, max_length=120)
    entity_type: str = Field(min_length=1, max_length=80)
    display_name: str | None = Field(default=None, max_length=240)
    document_number: str | None = Field(default=None, max_length=120)
    nit: str | None = Field(default=None, max_length=120)
    attributes: list[LLMKeyValue] = Field(default_factory=list)

    @field_validator("attributes", mode="before")
    @classmethod
    def _normalize_attributes(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return [{"key": str(key), "value": str(item)} for key, item in value.items()]
        return value


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
    diagnostics: list[LLMKeyValue] = Field(default_factory=list)

    @field_validator("diagnostics", mode="before")
    @classmethod
    def _normalize_diagnostics(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return [{"key": str(key), "value": str(item)} for key, item in value.items()]
        return value


class LLMOccurrenceRepair(BaseModel):
    model_config = ConfigDict(extra="forbid")

    occurrence: LLMOccurrence | None


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
    def __init__(
        self,
        extraction: dict[str, Any] | LLMExtraction,
        *,
        model: str = "static-test-model",
        prompt_version: str = PROMPT_VERSION,
    ) -> None:
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
        extraction = (
            self._extraction
            if isinstance(self._extraction, LLMExtraction)
            else LLMExtraction.model_validate(self._extraction)
        )
        return LLMExtractionResult(
            extraction=extraction,
            audit=LLMExtractionAudit(
                model=self.model,
                prompt_version=self.prompt_version,
                latency_ms=max(0, int((time.perf_counter() - started) * 1000)),
            ),
        )

    def repair_occurrence(
        self,
        *,
        block_id: str,
        block_text: str,
        occurrence: LLMOccurrence,
    ) -> LLMOccurrence | None:
        return None


class OpenAIBibliotecaExtractor:
    def __init__(
        self,
        api_key: str | None,
        *,
        model: str | None = None,
        prompt_version: str = PROMPT_VERSION,
        timeout_seconds: float | None = None,
        max_output_tokens: int | None = None,
    ) -> None:
        self.api_key = (
            (api_key or "").strip()
            or os.getenv("OPENAI_API_KEY", "").strip()
            or os.getenv("OPENAI_KEY", "").strip()
            or os.getenv("OPENAI_TOKEN", "").strip()
        )
        self.model = (
            model
            or os.getenv("BIBLIOTECA_LLM_MODEL")
            or DEFAULT_BIBLIOTECA_MODEL
        ).strip()
        self.prompt_version = prompt_version
        self.timeout_seconds = float(
            timeout_seconds
            or os.getenv("BIBLIOTECA_LLM_TIMEOUT_SECONDS")
            or DEFAULT_TIMEOUT_SECONDS
        )
        self.max_output_tokens = int(
            max_output_tokens
            or os.getenv("BIBLIOTECA_LLM_MAX_OUTPUT_TOKENS")
            or DEFAULT_MAX_OUTPUT_TOKENS
        )

    def extract(
        self,
        document_map: DocumentMap,
        fields: list[FieldDefinition],
        *,
        active_profile: dict[str, Any] | None = None,
        examples: list[dict[str, Any]] | None = None,
    ) -> LLMExtractionResult:
        if not self.api_key:
            raise LLMExtractorUnavailable(
                "OPENAI_API_KEY no configurada para Motor de Biblioteca LLM."
            )
        started = time.perf_counter()
        completion = self._parse_completion(
            _prompt_payload(
                document_map,
                fields,
                active_profile=active_profile,
                examples=examples,
            ),
            response_model=LLMExtraction,
        )
        latency_ms = max(0, int((time.perf_counter() - started) * 1000))
        choice = completion.choices[0]
        if getattr(choice, "finish_reason", None) not in {None, "stop"}:
            raise LLMExtractorTruncated(
                f"finish_reason={getattr(choice, 'finish_reason', None)}"
            )
        extraction = getattr(choice.message, "parsed", None)
        if not isinstance(extraction, LLMExtraction):
            raise LLMExtractorInvalidResponse("missing_parsed_extraction")
        usage = getattr(completion, "usage", None)
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

    def repair_occurrence(
        self,
        *,
        block_id: str,
        block_text: str,
        occurrence: LLMOccurrence,
    ) -> LLMOccurrence | None:
        if not self.api_key:
            return None
        payload = {
            "instruction": (
                "Corrige un anclaje dentro de un solo bloque. "
                "No inventes texto ni cambies field_instance_ref. "
                "Devuelve occurrence=null cuando no exista un anclaje literal inequívoco."
            ),
            "block": {"block_id": block_id, "text": block_text},
            "occurrence": occurrence.model_dump(mode="json"),
        }
        try:
            completion = self._parse_completion(
                payload,
                response_model=LLMOccurrenceRepair,
                max_output_tokens=min(self.max_output_tokens, 2048),
            )
            choice = completion.choices[0]
            if getattr(choice, "finish_reason", None) not in {None, "stop"}:
                return None
            parsed = getattr(choice.message, "parsed", None)
            if not isinstance(parsed, LLMOccurrenceRepair):
                return None
            repaired = parsed.occurrence
            if repaired is not None and repaired.field_instance_ref != occurrence.field_instance_ref:
                return None
            return repaired
        except Exception:
            return None

    def _parse_completion(
        self,
        payload: dict[str, Any],
        *,
        response_model: type[BaseModel],
        max_output_tokens: int | None = None,
    ):
        try:
            from openai import APITimeoutError, OpenAI
        except Exception as exc:  # pragma: no cover
            raise LLMExtractorUnavailable("openai package unavailable") from exc

        client = OpenAI(api_key=self.api_key, timeout=self.timeout_seconds)
        try:
            return client.chat.completions.parse(
                model=self.model,
                temperature=0,
                max_tokens=max_output_tokens or self.max_output_tokens,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres un extractor juridico notarial LLM-first. "
                            "Lee todo el DocumentMap recibido. Detecta todos los datos variables "
                            "juridicamente utiles, agrupa entidades y roles, distingue personas "
                            "diferentes con el mismo rol y conserva todas las apariciones repetidas. "
                            "El catalogo es una lista de asignaciones disponibles, no limita la deteccion. "
                            "No calcules offsets ni modifiques documentos. block_id debe existir y "
                            "exact_text debe copiar texto literal completo del bloque."
                        ),
                    },
                    {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
                ],
                response_format=response_model,
            )
        except (APITimeoutError, TimeoutError) as exc:
            raise LLMExtractorTimeout("timeout") from exc
        except LLMExtractorError:
            raise
        except ValidationError as exc:
            raise LLMExtractorInvalidResponse("invalid_structured_output") from exc
        except Exception as exc:
            message = str(exc).lower()
            if "timeout" in message:
                raise LLMExtractorTimeout("timeout") from exc
            if "response_format" in message or "schema" in message or "parse" in message:
                raise LLMExtractorInvalidResponse("structured_output_error") from exc
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
            "read_every_block": True,
            "extract_all_useful_fields": True,
            "catalog_is_available_assignments_not_detection_limit": True,
            "group_repeated_entities": True,
            "separate_people_with_same_role": True,
            "recognize_multiple_roles": True,
            "propose_unmapped_fields": True,
            "return_literal_anchors_only": True,
            "do_not_omit_repeated_occurrences": True,
            "do_not_extract_fixed_legal_text_or_normative_references": True,
        },
        "catalog": [asdict(field) for field in fields],
        "active_notary_profile": active_profile or {},
        "historical_examples": examples or [],
        "document_map": document_map.to_prompt_payload(),
    }


__all__ = [
    "BibliotecaLLMExtractor",
    "DEFAULT_BIBLIOTECA_MODEL",
    "LLMEntity",
    "LLMExtraction",
    "LLMExtractionAudit",
    "LLMExtractionResult",
    "LLMExtractorError",
    "LLMExtractorInvalidResponse",
    "LLMExtractorTimeout",
    "LLMExtractorTruncated",
    "LLMExtractorUnavailable",
    "LLMFieldInstance",
    "LLMKeyValue",
    "LLMOccurrence",
    "LLMOccurrenceRepair",
    "LLMRole",
    "LLMUnmappedField",
    "OpenAIBibliotecaExtractor",
    "PROMPT_VERSION",
    "StaticBibliotecaLLMExtractor",
]
