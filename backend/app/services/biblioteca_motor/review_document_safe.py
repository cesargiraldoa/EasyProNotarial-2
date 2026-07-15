from __future__ import annotations

from collections import defaultdict
from typing import Any

from app.services.biblioteca_motor.review_document import (
    ReviewDocumentResult,
    prepare_review_document as _prepare_review_document,
    visible_text_from_docx,
)

VISIBLE_TEXT_ERROR = "La version de revision altero el texto visible."
VISIBLE_TEXT_SKIP_REASON = "visible_text_guard"


def prepare_review_document_safe(
    docx_bytes: bytes,
    suggestions: list[dict[str, Any]],
    *,
    analysis_id: str,
) -> ReviewDocumentResult:
    """Prepare a review DOCX without ever changing its visible source text.

    The normal path remains a single full-document mutation. When an unusual
    OOXML inline structure causes the legacy mutator to reorder visible text,
    this guard isolates the incompatible suggestion and preserves every safe
    suggestion instead of failing the whole analysis job.
    """

    try:
        return _prepare_review_document(
            docx_bytes,
            suggestions,
            analysis_id=analysis_id,
        )
    except ValueError as exc:
        if VISIBLE_TEXT_ERROR not in str(exc):
            raise

    candidates, incompatible = _safe_candidates(
        docx_bytes,
        suggestions,
        analysis_id=analysis_id,
    )
    result = _prepare_review_document(
        docx_bytes,
        candidates,
        analysis_id=analysis_id,
    )
    if visible_text_from_docx(result.docx_bytes) != visible_text_from_docx(docx_bytes):
        raise ValueError(VISIBLE_TEXT_ERROR)

    skipped = list(result.skipped)
    known = {str(item.get("suggestion_id") or "") for item in skipped}
    for suggestion in incompatible:
        suggestion_id = str(suggestion.get("suggestion_id") or "")
        if suggestion_id and suggestion_id not in known:
            skipped.append(
                {
                    "suggestion_id": suggestion_id,
                    "reason": VISIBLE_TEXT_SKIP_REASON,
                }
            )
            known.add(suggestion_id)

    return ReviewDocumentResult(
        docx_bytes=result.docx_bytes,
        groups=result.groups,
        wrapped_count=result.wrapped_count,
        skipped=skipped,
    )


def _safe_candidates(
    docx_bytes: bytes,
    suggestions: list[dict[str, Any]],
    *,
    analysis_id: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for suggestion in suggestions:
        grouped[_paragraph_key(suggestion)].append(suggestion)

    candidates: list[dict[str, Any]] = []
    incompatible: list[dict[str, Any]] = []
    for group in grouped.values():
        if _preserves_visible_text(docx_bytes, group, analysis_id=analysis_id):
            candidates.extend(group)
            continue
        for suggestion in group:
            if _preserves_visible_text(docx_bytes, [suggestion], analysis_id=analysis_id):
                candidates.append(suggestion)
            else:
                incompatible.append(suggestion)

    if _preserves_visible_text(docx_bytes, candidates, analysis_id=analysis_id):
        return candidates, incompatible

    accepted: list[dict[str, Any]] = []
    for suggestion in candidates:
        trial = [*accepted, suggestion]
        if _preserves_visible_text(docx_bytes, trial, analysis_id=analysis_id):
            accepted.append(suggestion)
        else:
            incompatible.append(suggestion)
    return accepted, incompatible


def _preserves_visible_text(
    docx_bytes: bytes,
    suggestions: list[dict[str, Any]],
    *,
    analysis_id: str,
) -> bool:
    try:
        result = _prepare_review_document(
            docx_bytes,
            suggestions,
            analysis_id=analysis_id,
        )
    except ValueError as exc:
        if VISIBLE_TEXT_ERROR in str(exc):
            return False
        raise
    return visible_text_from_docx(result.docx_bytes) == visible_text_from_docx(docx_bytes)


def _paragraph_key(suggestion: dict[str, Any]) -> tuple[Any, ...]:
    location = suggestion.get("location") if isinstance(suggestion.get("location"), dict) else {}
    return (
        location.get("block_type"),
        location.get("paragraph_index"),
        location.get("table_index"),
        location.get("row_index"),
        location.get("cell_index"),
    )


__all__ = [
    "VISIBLE_TEXT_ERROR",
    "VISIBLE_TEXT_SKIP_REASON",
    "prepare_review_document_safe",
]
