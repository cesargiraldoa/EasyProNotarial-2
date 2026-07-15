from __future__ import annotations

import hashlib
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, replace
from typing import Any

from app.services.biblioteca_motor.contracts import FieldDefinition
from app.services.biblioteca_motor.document_map import DocumentMap, DocumentMapBlock
from app.services.biblioteca_motor.llm_extractor import (
    BibliotecaLLMExtractor,
    LLMEntity,
    LLMExtraction,
    LLMExtractionAudit,
    LLMExtractionResult,
    LLMFieldInstance,
    LLMKeyValue,
    LLMOccurrence,
    LLMRole,
    LLMUnmappedField,
)


COMPREHENSIVE_PROMPT_VERSION = "biblioteca-llm-v3-comprehensive"
DEFAULT_CHUNK_CHARS = 8000
DEFAULT_LONG_BLOCK_OVERLAP = 400
DEFAULT_MAX_WORKERS = 3
DEFAULT_SPARSE_RETRY_MIN_CHARS = 1200


@dataclass(frozen=True)
class DocumentMapChunk:
    index: int
    document_map: DocumentMap
    block_offsets: dict[str, int]
    char_count: int


class ComprehensiveBibliotecaExtractor:
    """Runs exhaustive LLM extraction over every DocumentMap block and merges the results.

    Chunking is only a transport strategy. The semantic detector remains the LLM and the
    backend still validates every returned literal anchor against the original document.
    """

    def __init__(
        self,
        inner: BibliotecaLLMExtractor,
        *,
        chunk_chars: int | None = None,
        long_block_overlap: int | None = None,
        max_workers: int | None = None,
        retry_sparse: bool = True,
    ) -> None:
        self.inner = inner
        self.model = inner.model
        self.prompt_version = COMPREHENSIVE_PROMPT_VERSION
        self.chunk_chars = max(
            2000,
            int(chunk_chars or os.getenv("BIBLIOTECA_LLM_CHUNK_CHARS") or DEFAULT_CHUNK_CHARS),
        )
        self.long_block_overlap = max(
            0,
            int(
                long_block_overlap
                if long_block_overlap is not None
                else os.getenv("BIBLIOTECA_LLM_LONG_BLOCK_OVERLAP") or DEFAULT_LONG_BLOCK_OVERLAP
            ),
        )
        self.max_workers = max(
            1,
            int(max_workers or os.getenv("BIBLIOTECA_LLM_MAX_WORKERS") or DEFAULT_MAX_WORKERS),
        )
        self.retry_sparse = retry_sparse

    def extract(
        self,
        document_map: DocumentMap,
        fields: list[FieldDefinition],
        *,
        active_profile: dict[str, Any] | None = None,
        examples: list[dict[str, Any]] | None = None,
    ) -> LLMExtractionResult:
        started = time.perf_counter()
        chunks = chunk_document_map(
            document_map,
            max_chars=self.chunk_chars,
            long_block_overlap=self.long_block_overlap,
        )
        if not chunks:
            return self.inner.extract(
                document_map,
                fields,
                active_profile=active_profile,
                examples=examples,
            )

        results: list[LLMExtractionResult | None] = [None] * len(chunks)
        workers = min(self.max_workers, len(chunks))
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_map = {
                executor.submit(
                    self._extract_chunk,
                    chunk,
                    len(chunks),
                    fields,
                    active_profile,
                    examples,
                ): chunk.index
                for chunk in chunks
            }
            for future in as_completed(future_map):
                results[future_map[future]] = future.result()

        completed = [item for item in results if item is not None]
        if len(completed) != len(chunks):
            raise RuntimeError("biblioteca_chunk_result_missing")
        return merge_chunk_results(
            document_map,
            chunks,
            completed,
            model=self.model,
            prompt_version=self.prompt_version,
            latency_ms=max(0, int((time.perf_counter() - started) * 1000)),
        )

    def _extract_chunk(
        self,
        chunk: DocumentMapChunk,
        total_chunks: int,
        fields: list[FieldDefinition],
        active_profile: dict[str, Any] | None,
        examples: list[dict[str, Any]] | None,
    ) -> LLMExtractionResult:
        profile = _runtime_profile(
            active_profile,
            chunk_index=chunk.index,
            total_chunks=total_chunks,
            retry=False,
        )
        first = self.inner.extract(
            chunk.document_map,
            fields,
            active_profile=profile,
            examples=examples,
        )
        if not self.retry_sparse or not _is_sparse(chunk, first.extraction):
            return first

        retry_profile = _runtime_profile(
            active_profile,
            chunk_index=chunk.index,
            total_chunks=total_chunks,
            retry=True,
        )
        second = self.inner.extract(
            chunk.document_map,
            fields,
            active_profile=retry_profile,
            examples=examples,
        )
        return second if len(second.extraction.occurrences) > len(first.extraction.occurrences) else first

    def repair_occurrence(
        self,
        *,
        block_id: str,
        block_text: str,
        occurrence: LLMOccurrence,
    ) -> LLMOccurrence | None:
        return self.inner.repair_occurrence(
            block_id=block_id,
            block_text=block_text,
            occurrence=occurrence,
        )


def chunk_document_map(
    document_map: DocumentMap,
    *,
    max_chars: int = DEFAULT_CHUNK_CHARS,
    long_block_overlap: int = DEFAULT_LONG_BLOCK_OVERLAP,
) -> list[DocumentMapChunk]:
    max_chars = max(2000, int(max_chars))
    units: list[tuple[DocumentMapBlock, int]] = []
    for block in document_map.blocks:
        units.extend(_segment_block(block, max_chars=max_chars, overlap=long_block_overlap))

    chunks: list[DocumentMapChunk] = []
    current: list[DocumentMapBlock] = []
    offsets: dict[str, int] = {}
    char_count = 0

    def flush() -> None:
        nonlocal current, offsets, char_count
        if not current:
            return
        chunks.append(
            DocumentMapChunk(
                index=len(chunks),
                document_map=DocumentMap(document_map.document_sha256, list(current)),
                block_offsets=dict(offsets),
                char_count=char_count,
            ),
        )
        current = []
        offsets = {}
        char_count = 0

    for prompt_block, source_offset in units:
        # A block split into multiple prompt segments must not share a chunk because
        # DocumentMap.block_by_id() intentionally has one record per block_id.
        if current and (
            char_count + len(prompt_block.text) > max_chars
            or prompt_block.block_id in offsets
        ):
            flush()
        current.append(prompt_block)
        offsets[prompt_block.block_id] = source_offset
        char_count += len(prompt_block.text)
    flush()
    return chunks


def merge_chunk_results(
    original_map: DocumentMap,
    chunks: list[DocumentMapChunk],
    results: list[LLMExtractionResult],
    *,
    model: str,
    prompt_version: str,
    latency_ms: int,
) -> LLMExtractionResult:
    if len(chunks) != len(results):
        raise ValueError("chunk_result_count_mismatch")

    entity_ref_maps: list[dict[str, str]] = []
    canonical_entities: dict[str, LLMEntity] = {}
    entity_by_strong_key: dict[tuple[str, str], str] = {}
    entity_by_name_key: dict[tuple[str, str], str] = {}

    for extraction_result in results:
        local_map: dict[str, str] = {}
        for entity in extraction_result.extraction.entities:
            strong_keys = _strong_entity_keys(entity)
            name_key = _name_entity_key(entity)
            canonical_ref = next(
                (entity_by_strong_key[key] for key in strong_keys if key in entity_by_strong_key),
                None,
            )
            if canonical_ref is None and name_key is not None:
                canonical_ref = entity_by_name_key.get(name_key)
            if canonical_ref is None:
                canonical_ref = f"entity_{len(canonical_entities) + 1:04d}"
                canonical_entities[canonical_ref] = entity.model_copy(
                    update={"entity_ref": canonical_ref},
                    deep=True,
                )
            else:
                canonical_entities[canonical_ref] = _merge_entity(
                    canonical_entities[canonical_ref],
                    entity,
                    canonical_ref,
                )
            for key in strong_keys:
                entity_by_strong_key[key] = canonical_ref
            if name_key is not None:
                entity_by_name_key[name_key] = canonical_ref
            local_map[entity.entity_ref] = canonical_ref
        entity_ref_maps.append(local_map)

    roles: list[LLMRole] = []
    seen_roles: set[tuple[str, str]] = set()
    for result_index, extraction_result in enumerate(results):
        for role in extraction_result.extraction.roles:
            entity_ref = entity_ref_maps[result_index].get(role.entity_ref)
            if not entity_ref:
                continue
            safe_role = _safe_code(role.role)
            key = (entity_ref, safe_role)
            if key in seen_roles:
                continue
            seen_roles.add(key)
            roles.append(LLMRole(entity_ref=entity_ref, role=safe_role or role.role))

    field_ref_maps: list[dict[str, str]] = []
    canonical_fields: dict[str, LLMFieldInstance] = {}
    field_by_key: dict[tuple[str, ...], str] = {}

    for result_index, extraction_result in enumerate(results):
        values_by_field: dict[str, list[str]] = {}
        for occurrence in extraction_result.extraction.occurrences:
            values_by_field.setdefault(occurrence.field_instance_ref, []).append(occurrence.exact_text)

        local_map: dict[str, str] = {}
        for field in extraction_result.extraction.field_instances:
            entity_ref = entity_ref_maps[result_index].get(field.entity_ref or "")
            value_signature = ""
            if entity_ref is None:
                normalized_values = sorted(
                    {_normalize_text(item) for item in values_by_field.get(field.field_instance_ref, []) if item},
                )
                value_signature = "|".join(normalized_values[:6])
            field_key = (
                entity_ref or "entityless",
                _safe_code(field.role or ""),
                _safe_code(field.candidate_type),
                _safe_code(field.base_field_code),
                _safe_code(field.suggested_field_code or field.visible_code or ""),
                value_signature,
            )
            canonical_ref = field_by_key.get(field_key)
            normalized_field = field.model_copy(
                update={
                    "field_instance_ref": canonical_ref or "",
                    "entity_ref": entity_ref,
                    "role": _safe_code(field.role or "") or None,
                },
                deep=True,
            )
            if canonical_ref is None:
                canonical_ref = f"field_{len(canonical_fields) + 1:05d}"
                field_by_key[field_key] = canonical_ref
                canonical_fields[canonical_ref] = normalized_field.model_copy(
                    update={"field_instance_ref": canonical_ref},
                    deep=True,
                )
            else:
                canonical_fields[canonical_ref] = _merge_field(
                    canonical_fields[canonical_ref],
                    normalized_field,
                    canonical_ref,
                )
            local_map[field.field_instance_ref] = canonical_ref
        field_ref_maps.append(local_map)

    occurrences: list[LLMOccurrence] = []
    seen_occurrences: set[tuple[str, str, str, int]] = set()
    for result_index, extraction_result in enumerate(results):
        chunk = chunks[result_index]
        for occurrence in extraction_result.extraction.occurrences:
            canonical_field_ref = field_ref_maps[result_index].get(occurrence.field_instance_ref)
            if not canonical_field_ref:
                continue
            normalized = _normalize_occurrence_index(original_map, chunk, occurrence)
            key = (
                canonical_field_ref,
                normalized.block_id,
                normalized.exact_text,
                normalized.occurrence_index,
            )
            if key in seen_occurrences:
                continue
            seen_occurrences.add(key)
            occurrences.append(
                normalized.model_copy(
                    update={
                        "occurrence_ref": f"occurrence_{len(occurrences) + 1:06d}",
                        "field_instance_ref": canonical_field_ref,
                    },
                    deep=True,
                ),
            )

    unmapped_fields: list[LLMUnmappedField] = []
    seen_unmapped: set[str] = set()
    for result_index, extraction_result in enumerate(results):
        for item in extraction_result.extraction.unmapped_fields:
            canonical_field_ref = field_ref_maps[result_index].get(item.field_instance_ref)
            if not canonical_field_ref or canonical_field_ref in seen_unmapped:
                continue
            seen_unmapped.add(canonical_field_ref)
            unmapped_fields.append(
                item.model_copy(update={"field_instance_ref": canonical_field_ref}, deep=True),
            )

    best_result = max(results, key=lambda item: item.extraction.confidence)
    weighted_confidence_numerator = 0.0
    weighted_confidence_denominator = 0
    for item in results:
        weight = max(1, len(item.extraction.occurrences))
        weighted_confidence_numerator += item.extraction.confidence * weight
        weighted_confidence_denominator += weight

    diagnostics = [
        LLMKeyValue(key="pipeline", value="full_document_chunked"),
        LLMKeyValue(key="chunk_count", value=str(len(chunks))),
        LLMKeyValue(key="document_block_count", value=str(len(original_map.blocks))),
        LLMKeyValue(key="document_char_count", value=str(sum(len(block.text) for block in original_map.blocks))),
        LLMKeyValue(key="merged_entity_count", value=str(len(canonical_entities))),
        LLMKeyValue(key="merged_field_instance_count", value=str(len(canonical_fields))),
        LLMKeyValue(key="merged_occurrence_count", value=str(len(occurrences))),
    ]

    input_tokens = _sum_optional(item.audit.input_tokens for item in results)
    output_tokens = _sum_optional(item.audit.output_tokens for item in results)
    costs = [item.audit.cost_usd for item in results if item.audit.cost_usd is not None]

    extraction = LLMExtraction(
        document_type=best_result.extraction.document_type,
        entities=list(canonical_entities.values()),
        roles=roles,
        field_instances=list(canonical_fields.values()),
        occurrences=occurrences,
        unmapped_fields=unmapped_fields,
        confidence=(
            weighted_confidence_numerator / weighted_confidence_denominator
            if weighted_confidence_denominator
            else best_result.extraction.confidence
        ),
        reason=f"Extraccion exhaustiva del documento completo en {len(chunks)} segmento(s).",
        diagnostics=diagnostics,
    )
    return LLMExtractionResult(
        extraction=extraction,
        audit=LLMExtractionAudit(
            model=model,
            prompt_version=prompt_version,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            cost_usd=sum(costs) if costs else None,
        ),
    )


def _runtime_profile(
    active_profile: dict[str, Any] | None,
    *,
    chunk_index: int,
    total_chunks: int,
    retry: bool,
) -> dict[str, Any]:
    profile = dict(active_profile or {})
    profile["runtime_extraction_contract"] = {
        "mode": "coverage_retry" if retry else "exhaustive_chunk",
        "chunk_number": chunk_index + 1,
        "total_chunks": total_chunks,
        "mandatory": [
            "Revisar todos los bloques recibidos antes de responder.",
            "Extraer cada dato variable juridicamente util y cada una de sus apariciones.",
            "Incluir personas, documentos, NIT, razones sociales, roles, inmuebles, matriculas, cedulas catastrales, areas, valores, fechas, numeros de escritura, direcciones, correos y telefonos cuando aparezcan.",
            "Proponer campos nuevos cuando el catalogo no tenga una asignacion adecuada.",
            "No extraer articulos, leyes, numerales normativos ni texto juridico fijo.",
            "exact_text debe ser el valor literal minimo completo, no el parrafo entero.",
            "No devolver una muestra: devolver el inventario completo del segmento.",
        ],
    }
    if retry:
        profile["runtime_extraction_contract"]["retry_reason"] = (
            "La primera lectura produjo una cobertura anormalmente baja. Releer bloque por bloque y devolver todo lo omitido."
        )
    return profile


def _is_sparse(chunk: DocumentMapChunk, extraction: LLMExtraction) -> bool:
    if chunk.char_count < DEFAULT_SPARSE_RETRY_MIN_CHARS:
        return False
    minimum = max(2, min(8, len(chunk.document_map.blocks) // 2))
    return len(extraction.occurrences) < minimum


def _segment_block(
    block: DocumentMapBlock,
    *,
    max_chars: int,
    overlap: int,
) -> list[tuple[DocumentMapBlock, int]]:
    if len(block.text) <= max_chars:
        return [(block, 0)]
    result: list[tuple[DocumentMapBlock, int]] = []
    start = 0
    text_length = len(block.text)
    while start < text_length:
        end = min(text_length, start + max_chars)
        if end < text_length:
            search_from = start + int(max_chars * 0.70)
            boundary = max(
                block.text.rfind("\n", search_from, end),
                block.text.rfind(". ", search_from, end),
                block.text.rfind("; ", search_from, end),
                block.text.rfind(" ", search_from, end),
            )
            if boundary > start:
                end = boundary + 1
        segment_text = block.text[start:end]
        result.append(
            (
                replace(
                    block,
                    text=segment_text,
                    block_hash=hashlib.sha256(segment_text.encode("utf-8")).hexdigest(),
                ),
                start,
            ),
        )
        if end >= text_length:
            break
        next_start = max(start + 1, end - overlap)
        start = next_start
    return result


def _normalize_occurrence_index(
    original_map: DocumentMap,
    chunk: DocumentMapChunk,
    occurrence: LLMOccurrence,
) -> LLMOccurrence:
    original_block = original_map.block_by_id().get(occurrence.block_id)
    prompt_block = chunk.document_map.block_by_id().get(occurrence.block_id)
    if original_block is None or prompt_block is None:
        return occurrence
    local_matches = _find_all(prompt_block.text, occurrence.exact_text)
    if not local_matches:
        return occurrence
    local_index = occurrence.occurrence_index - 1
    if local_index < 0 or local_index >= len(local_matches):
        local_index = 0
    global_start = chunk.block_offsets.get(occurrence.block_id, 0) + local_matches[local_index][0]
    full_matches = _find_all(original_block.text, occurrence.exact_text)
    if not full_matches:
        return occurrence
    nearest_index = min(
        range(len(full_matches)),
        key=lambda index: abs(full_matches[index][0] - global_start),
    )
    return occurrence.model_copy(update={"occurrence_index": nearest_index + 1}, deep=True)


def _strong_entity_keys(entity: LLMEntity) -> list[tuple[str, str]]:
    keys: list[tuple[str, str]] = []
    if entity.nit:
        keys.append(("nit", _normalize_identifier(entity.nit)))
    if entity.document_number:
        keys.append(("document", _normalize_identifier(entity.document_number)))
    return [key for key in keys if key[1]]


def _name_entity_key(entity: LLMEntity) -> tuple[str, str] | None:
    normalized_name = _normalize_text(entity.display_name or "")
    if not normalized_name:
        return None
    return (_safe_code(entity.entity_type), normalized_name)


def _merge_entity(existing: LLMEntity, incoming: LLMEntity, canonical_ref: str) -> LLMEntity:
    attributes = {item.key: item.value for item in existing.attributes}
    for item in incoming.attributes:
        attributes.setdefault(item.key, item.value)
    return existing.model_copy(
        update={
            "entity_ref": canonical_ref,
            "display_name": existing.display_name or incoming.display_name,
            "document_number": existing.document_number or incoming.document_number,
            "nit": existing.nit or incoming.nit,
            "attributes": [LLMKeyValue(key=key, value=value) for key, value in attributes.items()],
        },
        deep=True,
    )


def _merge_field(
    existing: LLMFieldInstance,
    incoming: LLMFieldInstance,
    canonical_ref: str,
) -> LLMFieldInstance:
    prefer_incoming = incoming.catalog_match and not existing.catalog_match
    primary = incoming if prefer_incoming else existing
    secondary = existing if prefer_incoming else incoming
    return primary.model_copy(
        update={
            "field_instance_ref": canonical_ref,
            "entity_ref": primary.entity_ref or secondary.entity_ref,
            "role": primary.role or secondary.role,
            "suggested_field_code": primary.suggested_field_code or secondary.suggested_field_code,
            "visible_code": primary.visible_code or secondary.visible_code,
            "label": primary.label or secondary.label,
            "category": primary.category or secondary.category,
            "catalog_match": primary.catalog_match or secondary.catalog_match,
            "reason": primary.reason or secondary.reason,
        },
        deep=True,
    )


def _find_all(text: str, needle: str) -> list[tuple[int, int]]:
    if not needle:
        return []
    positions: list[tuple[int, int]] = []
    cursor = 0
    while True:
        index = text.find(needle, cursor)
        if index < 0:
            return positions
        positions.append((index, index + len(needle)))
        cursor = index + max(1, len(needle))


def _sum_optional(values) -> int | None:
    items = [int(value) for value in values if value is not None]
    return sum(items) if items else None


def _safe_code(value: str) -> str:
    return re.sub(r"[^A-Z0-9_]+", "_", str(value or "").strip().upper()).strip("_")[:120]


def _normalize_identifier(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(value or "").upper())


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().upper())


__all__ = [
    "COMPREHENSIVE_PROMPT_VERSION",
    "ComprehensiveBibliotecaExtractor",
    "DocumentMapChunk",
    "chunk_document_map",
    "merge_chunk_results",
]
