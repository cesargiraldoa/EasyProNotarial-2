from __future__ import annotations

import hashlib
import re
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
    def repair_occurrence(
        self,
        *,
        block_id: str,
        block_text: str,
        occurrence: LLMOccurrence,
    ) -> LLMOccurrence | None:
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
                start, end, actual_occurrence_index = resolved
                if _overlaps(occupied.setdefault(block.block_id, []), start, end):
                    skipped.append(_skip(current, "overlap_detected"))
                    break
                occupied[block.block_id].append((start, end))
                anchored.append(
                    _anchored(
                        block,
                        current,
                        start,
                        end,
                        actual_occurrence_index,
                    ),
                )
                break
            if (
                attempt == 0
                and repairer is not None
                and block is not None
                and current.occurrence_ref not in repaired_refs
            ):
                repaired_refs.add(current.occurrence_ref)
                repaired = repairer.repair_occurrence(
                    block_id=block.block_id,
                    block_text=block.text,
                    occurrence=current,
                )
                if repaired is not None:
                    current = repaired
                    continue
            skipped.append(_skip(current, reason or "anchor_not_verified"))
            break
    return AnchorResolutionResult(anchored=anchored, skipped=skipped)


def _resolve_single(
    block: DocumentMapBlock,
    occurrence: LLMOccurrence,
) -> tuple[tuple[int, int, int] | None, str | None]:
    if not occurrence.exact_text:
        return None, "empty_exact_text"
    matches = _find_all(block.text, occurrence.exact_text)
    if not matches:
        return None, "exact_text_not_found"

    # A single literal match is already an unambiguous, backend-verifiable anchor.
    # LLM context remains audit metadata and must not reject an otherwise exact match.
    if len(matches) == 1:
        start, end = matches[0]
        return (start, end, 1), None

    preferred_index = occurrence.occurrence_index - 1
    preferred_valid = 0 <= preferred_index < len(matches)
    if preferred_valid:
        preferred_start, preferred_end = matches[preferred_index]
        if _contexts_match(
            block.text,
            preferred_start,
            preferred_end,
            occurrence.left_context,
            occurrence.right_context,
        ):
            return (preferred_start, preferred_end, preferred_index + 1), None

    scored = [
        (
            _context_score(
                block.text,
                start,
                end,
                occurrence.left_context,
                occurrence.right_context,
            ),
            index,
            start,
            end,
        )
        for index, (start, end) in enumerate(matches)
    ]
    scored.sort(key=lambda item: (-item[0], item[1]))
    best = scored[0]
    second_score = scored[1][0] if len(scored) > 1 else -1
    if best[0] > 0 and best[0] > second_score:
        return (best[2], best[3], best[1] + 1), None

    # When the model supplied a valid occurrence index and no useful context,
    # the index is the deterministic disambiguator.
    if preferred_valid and not occurrence.left_context and not occurrence.right_context:
        start, end = matches[preferred_index]
        return (start, end, preferred_index + 1), None

    if not preferred_valid:
        return None, "occurrence_index_out_of_range"
    return None, "ambiguous_exact_text"


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


def _contexts_match(
    text: str,
    start: int,
    end: int,
    left_context: str,
    right_context: str,
) -> bool:
    return _left_context_score(text, start, left_context) > 0 and _right_context_score(
        text,
        end,
        right_context,
    ) > 0 if left_context and right_context else (
        _left_context_score(text, start, left_context) > 0
        if left_context
        else _right_context_score(text, end, right_context) > 0
        if right_context
        else True
    )


def _context_score(
    text: str,
    start: int,
    end: int,
    left_context: str,
    right_context: str,
) -> int:
    return _left_context_score(text, start, left_context) + _right_context_score(
        text,
        end,
        right_context,
    )


def _left_context_score(text: str, start: int, left_context: str) -> int:
    context = str(left_context or "")
    if not context:
        return 0
    actual = text[:start]
    if actual.endswith(context):
        return 1000 + len(context)
    normalized_context = _normalize_context(context)
    normalized_actual = _normalize_context(actual[-max(240, len(context) * 3) :])
    if normalized_context and normalized_actual.endswith(normalized_context):
        return 500 + len(normalized_context)
    return _token_overlap_score(actual[-240:], context)


def _right_context_score(text: str, end: int, right_context: str) -> int:
    context = str(right_context or "")
    if not context:
        return 0
    actual = text[end:]
    if actual.startswith(context):
        return 1000 + len(context)
    normalized_context = _normalize_context(context)
    normalized_actual = _normalize_context(actual[: max(240, len(context) * 3)])
    if normalized_context and normalized_actual.startswith(normalized_context):
        return 500 + len(normalized_context)
    return _token_overlap_score(actual[:240], context)


def _token_overlap_score(actual: str, expected: str) -> int:
    actual_tokens = _tokens(actual)
    expected_tokens = _tokens(expected)
    if not actual_tokens or not expected_tokens:
        return 0
    max_width = min(8, len(expected_tokens), len(actual_tokens))
    score = 0
    for width in range(1, max_width + 1):
        expected_prefix = expected_tokens[:width]
        expected_suffix = expected_tokens[-width:]
        if actual_tokens[:width] == expected_prefix or actual_tokens[-width:] == expected_suffix:
            score = max(score, width * 20)
    return score


def _tokens(value: str) -> list[str]:
    return re.findall(r"[A-Z0-9ÁÉÍÓÚÜÑ]+", str(value or "").upper())


def _normalize_context(value: str) -> str:
    return " ".join(_tokens(value))


def _overlaps(spans: list[tuple[int, int]], start: int, end: int) -> bool:
    return any(start < other_end and other_start < end for other_start, other_end in spans)


def _anchored(
    block: DocumentMapBlock,
    occurrence: LLMOccurrence,
    start: int,
    end: int,
    occurrence_index: int,
) -> AnchoredOccurrence:
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
        "occurrence_index": occurrence_index,
        "location_key": _location_key(block, start, end, occurrence_index),
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


def _location_key(
    block: DocumentMapBlock,
    start: int,
    end: int,
    occurrence_index: int,
) -> str:
    if block.block_type == "paragraph":
        return f"paragraph:{block.paragraph_index}:{start}:{end}:{occurrence_index}"
    return (
        f"table_cell:{block.table_index}:{block.row_index}:{block.cell_index}:"
        f"{block.paragraph_index}:{start}:{end}:{occurrence_index}"
    )


def _skip(occurrence: LLMOccurrence, reason: str) -> AnchorSkip:
    return AnchorSkip(
        occurrence_ref=occurrence.occurrence_ref,
        field_instance_ref=occurrence.field_instance_ref,
        block_id=occurrence.block_id,
        exact_text_sha256=hashlib.sha256(
            str(occurrence.exact_text or "").encode("utf-8"),
        ).hexdigest(),
        reason=reason,
    )
