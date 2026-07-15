from __future__ import annotations

import hashlib
import time
from collections import Counter
from typing import Any

from app.services.biblioteca_motor.anchor_resolver import resolve_anchors
from app.services.biblioteca_motor.comprehensive_extractor import ComprehensiveBibliotecaExtractor
from app.services.biblioteca_motor.contracts import FieldDefinition
from app.services.biblioteca_motor.document_map import DocumentMap, build_document_map
from app.services.biblioteca_motor.field_instance_service import resolve_field_instances
from app.services.biblioteca_motor.llm_extractor import (
    BibliotecaLLMExtractor,
    LLMExtractionResult,
    LLMExtractorError,
    LLMExtractorInvalidResponse,
    LLMExtractorTimeout,
    LLMExtractorUnavailable,
    OpenAIBibliotecaExtractor,
    PROMPT_VERSION,
)


MAX_OPERATIONAL_SUGGESTIONS = 1000
ANALYSIS_TOTAL_BUDGET_SECONDS = 300.0


def analyze_biblioteca_document(
    docx_bytes: bytes,
    fields: list[Any],
    *,
    extractor: BibliotecaLLMExtractor | None = None,
    notary_id: int | None = None,
    active_profile: dict[str, Any] | None = None,
    profile_version: int | None = None,
    examples: list[dict[str, Any]] | None = None,
    max_suggestions: int = MAX_OPERATIONAL_SUGGESTIONS,
) -> dict[str, Any]:
    started = time.perf_counter()
    field_defs = [_field_definition(item) for item in fields]
    map_started = time.perf_counter()
    document_map = build_document_map(docx_bytes)
    document_map_ms = _elapsed_ms(map_started)
    if extractor is None:
        raise LLMExtractorUnavailable("El Motor de Biblioteca requiere extractor LLM configurado.")
    if isinstance(extractor, OpenAIBibliotecaExtractor):
        extractor = ComprehensiveBibliotecaExtractor(extractor)

    llm_started = time.perf_counter()
    llm_result = extractor.extract(
        document_map,
        field_defs,
        active_profile=active_profile,
        examples=examples,
    )
    llm_ms = _elapsed_ms(llm_started)

    anchor_started = time.perf_counter()
    anchors = resolve_anchors(document_map, llm_result.extraction.occurrences, repairer=extractor)
    anchor_ms = _elapsed_ms(anchor_started)

    instance_started = time.perf_counter()
    resolved = resolve_field_instances(
        llm_result.extraction,
        anchors.anchored,
        field_defs,
        document_sha256=document_map.document_sha256,
        max_suggestions=max_suggestions,
    )
    instance_ms = _elapsed_ms(instance_started)

    suggestions = resolved.suggestions
    omitted = max(0, len(anchors.anchored) - len(suggestions))
    skipped_reasons = Counter(item.reason for item in anchors.skipped)
    provisional_total = sum(1 for item in suggestions if item["catalog_status"] == "unmapped")
    catalogued_total = sum(1 for item in suggestions if item["catalog_status"] == "matched")
    total_ms = _elapsed_ms(started)
    anchor_denominator = len(anchors.anchored) + len(anchors.skipped)

    return {
        "analysis_id": "analysis_"
        + hashlib.sha256(
            f"{document_map.document_sha256}:{llm_result.audit.model}:{llm_result.audit.prompt_version}".encode("utf-8"),
        ).hexdigest()[:16],
        "mode": "llm_first",
        "status": "completed_llm",
        "document_type": llm_result.extraction.document_type,
        "notary_id": notary_id,
        "prompt_version": llm_result.audit.prompt_version,
        "profile_version": profile_version,
        "model": llm_result.audit.model,
        "document_sha256": document_map.document_sha256,
        "suggestions": suggestions,
        "stats": {
            "document_map_blocks": len(document_map.blocks),
            "document_map_chars": sum(len(block.text) for block in document_map.blocks),
            "llm_field_instances": len(llm_result.extraction.field_instances),
            "llm_occurrences": len(llm_result.extraction.occurrences),
            "detected_candidates": len(llm_result.extraction.occurrences),
            "classified_candidates": catalogued_total,
            "catalogued_suggestions": catalogued_total,
            "provisional_suggestions": provisional_total,
            "anchored_suggestions": len(anchors.anchored),
            "skipped_suggestions": len(anchors.skipped),
            "suggestions": len(suggestions),
            "omitted_suggestions": omitted,
            "anchor_success_rate_applied": (
                len(anchors.anchored) / anchor_denominator if anchor_denominator else 0.0
            ),
        },
        "diagnostics": {
            "llm": _llm_diagnostics(llm_result),
            "anchor": {
                "skipped": [
                    {
                        "occurrence_ref": item.occurrence_ref,
                        "field_instance_ref": item.field_instance_ref,
                        "block_id": item.block_id,
                        "exact_text_sha256": item.exact_text_sha256,
                        "reason": item.reason,
                    }
                    for item in anchors.skipped
                ],
                "skipped_by_reason": dict(skipped_reasons),
            },
        },
        "timing": {
            "download_ms": 0,
            "document_map_ms": document_map_ms,
            "llm_ms": llm_ms,
            "anchor_ms": anchor_ms,
            "field_instance_ms": instance_ms,
            "total_ms": total_ms,
        },
        "usage": {
            "input_tokens": llm_result.audit.input_tokens,
            "output_tokens": llm_result.audit.output_tokens,
            "cost_usd": llm_result.audit.cost_usd,
        },
    }


def build_analysis_failure_payload(exc: LLMExtractorError) -> tuple[str, int]:
    if isinstance(exc, LLMExtractorTimeout):
        return exc.code, 504
    if isinstance(exc, LLMExtractorInvalidResponse):
        return exc.code, 422
    if isinstance(exc, LLMExtractorUnavailable):
        return exc.code, 503
    return exc.code, 503


def _llm_diagnostics(result: LLMExtractionResult) -> dict[str, Any]:
    return {
        "status": "completed",
        "model": result.audit.model,
        "prompt_version": result.audit.prompt_version,
        "input_tokens": result.audit.input_tokens,
        "output_tokens": result.audit.output_tokens,
        "latency_ms": result.audit.latency_ms,
        "diagnostics": [item.model_dump(mode="json") for item in result.extraction.diagnostics],
    }


def _field_definition(item: Any) -> FieldDefinition:
    if isinstance(item, dict):
        raw_code = item.get("code", "")
        raw_label = item.get("label", "")
        raw_category = item.get("category", "otro")
        raw_field_type = item.get("field_type", "text")
    else:
        raw_code = getattr(item, "code", "")
        raw_label = getattr(item, "label", "")
        raw_category = getattr(item, "category", "otro")
        raw_field_type = getattr(item, "field_type", "text")
    return FieldDefinition(
        code=str(raw_code or "").strip(),
        label=str(raw_label or raw_code or "").strip(),
        category=str(raw_category or "otro").strip() or "otro",
        field_type=str(raw_field_type or "text").strip() or "text",
    )


def _elapsed_ms(started: float) -> int:
    return max(0, int((time.perf_counter() - started) * 1000))


__all__ = [
    "ANALYSIS_TOTAL_BUDGET_SECONDS",
    "MAX_OPERATIONAL_SUGGESTIONS",
    "OpenAIBibliotecaExtractor",
    "PROMPT_VERSION",
    "analyze_biblioteca_document",
    "build_analysis_failure_payload",
    "build_document_map",
]
