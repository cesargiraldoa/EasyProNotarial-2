from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from docx import Document


def _iter_paragraphs_in_table(table) -> Iterable:
    seen_cells: set[int] = set()
    for row in table.rows:
        for cell in row.cells:
            cell_id = id(cell._tc)
            if cell_id in seen_cells:
                continue
            seen_cells.add(cell_id)
            for paragraph in cell.paragraphs:
                yield paragraph
            for nested_table in cell.tables:
                yield from _iter_paragraphs_in_table(nested_table)


def _iter_paragraphs_in_container(container) -> Iterable:
    for paragraph in container.paragraphs:
        yield paragraph
    for table in container.tables:
        yield from _iter_paragraphs_in_table(table)


def _iter_document_paragraphs(document: Document) -> Iterable:
    yield from _iter_paragraphs_in_container(document)
    for section in document.sections:
        yield from _iter_paragraphs_in_container(section.header)
        yield from _iter_paragraphs_in_container(section.footer)


def _replace_literal_in_paragraph(paragraph, old: str, new: str) -> int:
    if not old or paragraph is None or not paragraph.text:
        return 0

    matches = list(re.finditer(re.escape(old), paragraph.text))
    if not matches:
        return 0

    replacements = 0
    for match in reversed(matches):
        match_start = match.start()
        match_end = match.end()

        runs_info = []
        position = 0
        for run in paragraph.runs:
            runs_info.append({
                "run": run,
                "start": position,
                "end": position + len(run.text),
            })
            position += len(run.text)

        affected = []
        for info in runs_info:
            if info["end"] <= match_start:
                continue
            if info["start"] >= match_end:
                break
            affected.append(info)

        if not affected:
            continue

        if len(affected) == 1:
            info = affected[0]
            run = info["run"]
            start_local = match_start - info["start"]
            end_local = match_end - info["start"]
            run.text = run.text[:start_local] + new + run.text[end_local:]
            replacements += 1
            continue

        first = affected[0]
        last = affected[-1]
        prefix = first["run"].text[: match_start - first["start"]]
        suffix = last["run"].text[match_end - last["start"]:]

        first["run"].text = prefix + new
        for info in affected[1:-1]:
            info["run"].text = ""
        if first is not last:
            last["run"].text = suffix

        replacements += 1

    return replacements


def _normalize_value(value) -> str:
    if value is None:
        return ""
    return str(value)


def apply_marked_template_replacements(
    docx_path_origen: str | Path,
    docx_path_destino: str | Path,
    values: dict,
    fields: list[dict] | None = None,
) -> dict:
    """
    Reemplaza marcadores exactos de plantilla marcada usando la metadata detectada.
    No usa IA ni concordancia.
    """

    document = Document(str(docx_path_origen))
    values_map = {str(key): _normalize_value(value) for key, value in (values or {}).items()}
    fields_list = fields or []

    replacement_targets: list[tuple[str, str, str]] = []
    for field in fields_list:
        if not isinstance(field, dict):
            continue
        key = str(field.get("key") or "").strip()
        if not key:
            continue
        replacement_value = values_map.get(key, "")
        raw_markers = field.get("raw_markers") or []
        if not isinstance(raw_markers, list):
            continue
        for raw_marker in raw_markers:
            marker = str(raw_marker or "").strip()
            if not marker or marker == "[[--]]":
                continue
            replacement_targets.append((marker, key, replacement_value))

    replacement_targets.sort(key=lambda item: len(item[0]), reverse=True)

    stats = {
        "total_replacements": 0,
        "by_key": {},
        "not_found": [],
    }

    seen_markers: set[str] = set()
    for marker, key, replacement_value in replacement_targets:
        if marker in seen_markers:
            continue
        seen_markers.add(marker)

        count = 0
        for paragraph in _iter_document_paragraphs(document):
            count += _replace_literal_in_paragraph(paragraph, marker, replacement_value)

        if count == 0:
            stats["not_found"].append({
                "key": key,
                "old": marker,
                "new": replacement_value,
            })
        else:
            stats["by_key"][key] = stats["by_key"].get(key, 0) + count
            stats["total_replacements"] += count

    document.save(str(docx_path_destino))
    return stats
