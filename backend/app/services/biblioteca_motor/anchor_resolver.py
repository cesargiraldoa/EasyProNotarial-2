from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Protocol

from app.services.biblioteca_motor.document_map import DocumentMap, DocumentMapBlock
from app.services.biblioteca_motor.llm_extractor import LLMOccurrence


@dataclass(frozen=True)
class AnchoredOccurrence:
    occurrence_ref: str
    field_instance_ref: str
    exact_text: str
    confidence: float
    reason: str | None
    location: dict
    context_before: str
    context_after: str


@dataclass(frozen=True)
class AnchorSkip:
    occurrence_ref: str
    field_instance_ref: str
    block_id: str
    exact_text_sha256: str
    reason: str


@dataclass(frozen=True)
class AnchorResolutionResult:
    anchored: list[AnchoredOccurrence]
    skipped: list[AnchorSkip]


class AnchorRepairer(Protocol):
    def repair_occurrence(self, *, block_id: str, block_text: str, occurrence: LLMOccurrence) -> LLMOccurrence | None:
        ...


def resolve_anchors(
    document_map: DocumentMap,
    occurrences: list[LLMOccurrence],
    *,
    repairer: AnchorRepairer | None = None,
) -> AnchorResolutionResult:
    blocks = document_map.block_by_id()
    anchored: list[AnchoredOccurrence] = []
    skipped: list[AnchorSkip] = []
    occupied: dict[str, list[tuple[int, int]]] = {}
    repaired_refs: set[str] = set()

    for occurrence in occurrences:
        current = occurrence
        for attempt in range(2):
            block = blocks.get(current.block_id)
            if block is None:
                reason = "block_not_found"
                resolved = None
            else:
                resolved, reason = _resolve_single(block, current)
            if resolved is not None:
                start, end = resolved
                if _overlaps(occupied.setdefault(block.block_id, []), start, end):
                    skipped.append(_skip(current, "overlap_detected"))
                    break
                occupied[block.block_id].append((start, end))
                anchored.append(_anchored(block, current, start, end))
                break
            if attempt == 0 and repairer is not None and block is not None and current.occurrence_ref not in repaired_refs:
                repaired_refs.add(current.occurrence_ref)
                repaired = repairer.repair_occurrence(block_id=block.block_id, block_text=block.text, occurrence=current)
                if repaired is not None:
                    current = repaired
                    continue
            skipped.append(_skip(current, reason or "anchor_not_verified"))
            break
    return AnchorResolutionResult(anchored=anchored, skipped=skipped)


def _resolve_single(block: DocumentMapBlock, occurrence: LLMOccurrence) -> tuple[tuple[int, int] | None, str | None]:
    if not occurrence.exact_text:
        return None, "empty_exact_text"
    matches = _find_all(block.text, occurrence.exact_text)
    if not matches:
        return None, "exact_text_not_found"
    if occurrence.occurrence_index < 1 or occurrence.occurrence_index > len(matches):
        return None, "occurrence_index_out_of_range"
    start, end = matches[occurrence.occurrence_index - 1]
    if not _left_context_ok(block.text, start, occurrence.left_context):
        return None, "left_context_mismatch"
    if not _right_context_ok(block.text, end, occurrence.right_context):
        return None, "right_context_mismatch"
    return (start, end), None


def _find_all(text: str, needle: str) -> list[tuple[int, int]]:
    positions: list[tuple[int, int]] = []
    cursor = 0
    while True:
        index = text.find(needle, cursor)
        if index < 0:
            break
        positions.append((index, index + len(needle)))
        cursor = index + max(1, len(needle))
    return positions


def _left_context_ok(text: str, start: int, left_context: str) -> bool:
    context = str(left_context or "")
    return not context or text[:start].endswith(context)


def _right_context_ok(text: str, end: int, right_context: str) -> bool:
    context = str(right_context or "")
    return not context or text[end:].startswith(context)


def _overlaps(spans: list[tuple[int, int]], start: int, end: int) -> bool:
    return any(start < other_end and other_start < end for other_start, other_end in spans)


def _anchored(block: DocumentMapBlock, occurrence: LLMOccurrence, start: int, end: int) -> AnchoredOccurrence:
    location = {
        "block_id": block.block_id,
        "block_type": block.block_type,
        "block_index": block.block_index,
        "paragraph_index": block.paragraph_index,
        "table_index": block.table_index,
        "row_index": block.row_index,
        "cell_index": block.cell_index,
        "char_start": start,
        "char_end": end,
        "occurrence_index": occurrence.occurrence_index,
        "location_key": _location_key(block, start, end, occurrence.occurrence_index),
        "block_hash": block.block_hash,
    }
    return AnchoredOccurrence(
        occurrence_ref=occurrence.occurrence_ref,
        field_instance_ref=occurrence.field_instance_ref,
        exact_text=occurrence.exact_text,
        confidence=occurrence.confidence,
        reason=occurrence.reason,
        location=location,
        context_before=block.text[max(0, start - 180) : start],
        context_after=block.text[end : end + 180],
    )


def _location_key(block: DocumentMapBlock, start: int, end: int, occurrence_index: int) -> str:
    if block.block_type == "paragraph":
        return f"paragraph:{block.paragraph_index}:{start}:{end}:{occurrence_index}"
    return f"table_cell:{block.table_index}:{block.row_index}:{block.cell_index}:{block.paragraph_index}:{start}:{end}:{occurrence_index}"


def _skip(occurrence: LLMOccurrence, reason: str) -> AnchorSkip:
    return AnchorSkip(
        occurrence_ref=occurrence.occurrence_ref,
        field_instance_ref=occurrence.field_instance_ref,
        block_id=occurrence.block_id,
        exact_text_sha256=hashlib.sha256(str(occurrence.exact_text or "").encode("utf-8")).hexdigest(),
        reason=reason,
    )
