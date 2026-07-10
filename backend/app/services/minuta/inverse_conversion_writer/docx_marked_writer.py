from __future__ import annotations

import re
from copy import deepcopy
from pathlib import Path

from docx import Document
from docx.document import Document as DocxDocument
from docx.oxml import OxmlElement
from docx.shared import RGBColor
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph
from docx.text.run import Run

from app.services.minuta.inverse_conversion_writer.models import MarkedCandidate, MarkedDocxWriteResult

RED_COLOR = RGBColor(0xFF, 0x00, 0x00)


class DocxMarkedWriter:
    def write(
        self,
        source_path: str | Path,
        destination_path: str | Path,
        candidates: list[MarkedCandidate],
        output_filename: str | None = None,
    ) -> MarkedDocxWriteResult:
        accepted = [candidate for candidate in candidates if candidate.is_accepted]
        if not accepted:
            raise ValueError("No hay candidatos aceptados para marcar.")

        document = Document(str(source_path))
        marked_occurrences = 0
        for candidate in self._dedupe_candidates(accepted):
            marked_occurrences += self._mark_candidate(document, candidate)

        destination = Path(destination_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        document.save(str(destination))
        return MarkedDocxWriteResult(
            output_path=destination,
            filename=output_filename or marked_docx_filename(Path(source_path).name),
            accepted_candidates=len(accepted),
            marked_occurrences=marked_occurrences,
            skipped_candidates=len(candidates) - len(accepted),
        )

    def _dedupe_candidates(self, candidates: list[MarkedCandidate]) -> list[MarkedCandidate]:
        seen: set[tuple[str, tuple[str, ...]]] = set()
        deduped: list[MarkedCandidate] = []
        for candidate in candidates:
            locations = tuple(sorted({context.location for context in candidate.contexts if context.location}))
            key = (candidate.text, locations)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(candidate)
        return sorted(deduped, key=lambda item: len(item.text), reverse=True)

    def _mark_candidate(self, document, candidate: MarkedCandidate) -> int:
        locations = {context.location for context in candidate.contexts if context.location}
        total = 0
        for paragraph, location in iter_docx_paragraphs(document):
            if locations and location not in locations:
                continue
            total += mark_text_in_paragraph(paragraph, candidate.text)
        return total


def marked_docx_filename(original_filename: str) -> str:
    path = Path(original_filename)
    stem = path.stem or "documento"
    return f"{stem} - marcado.docx"


def iter_docx_paragraphs(docx_document):
    yield from _iter_blocks(docx_document)


def _iter_blocks(parent, prefix: str = ""):
    paragraph_index = 0
    table_index = 0
    for block in _iter_block_items(parent):
        if isinstance(block, Paragraph):
            paragraph_index += 1
            location = f"{prefix}paragraph {paragraph_index}" if prefix else f"paragraph {paragraph_index}"
            yield block, location
        elif isinstance(block, Table):
            table_index += 1
            yield from _iter_table_blocks(block, table_index)


def _iter_table_blocks(table: Table, table_index: int):
    seen_cells: set[int] = set()
    for row_index, row in enumerate(table.rows, start=1):
        for cell_index, cell in enumerate(row.cells, start=1):
            cell_id = id(cell._tc)
            if cell_id in seen_cells:
                continue
            seen_cells.add(cell_id)
            prefix = f"table {table_index} row {row_index} cell {cell_index} "
            yield from _iter_blocks(cell, prefix=prefix)


def _iter_block_items(parent):
    if isinstance(parent, DocxDocument):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        raise TypeError(f"Unsupported parent type: {type(parent)!r}")

    for child in parent_elm.iterchildren():
        if child.tag.endswith("}p"):
            yield Paragraph(child, parent)
        elif child.tag.endswith("}tbl"):
            yield Table(child, parent)


def mark_text_in_paragraph(paragraph, text: str) -> int:
    target = text.strip()
    if not target:
        return 0
    matches = list(re.finditer(re.escape(target), paragraph.text or ""))
    marked = 0
    for match in reversed(matches):
        affected = _affected_runs(paragraph, match.start(), match.end())
        if not affected:
            continue
        _replace_affected_runs(paragraph, affected, match.start(), match.end(), target, RED_COLOR)
        marked += 1
    return marked


def _affected_runs(paragraph, start: int, end: int) -> list[dict]:
    runs_info: list[dict] = []
    position = 0
    for run in paragraph.runs:
        run_end = position + len(run.text)
        runs_info.append({"run": run, "start": position, "end": run_end})
        position = run_end
    return [info for info in runs_info if info["end"] > start and info["start"] < end]


def _replace_affected_runs(paragraph, affected: list[dict], start: int, end: int, value: str, color: RGBColor) -> None:
    first = affected[0]
    last = affected[-1]
    first_run = first["run"]
    last_run = last["run"]
    prefix = first_run.text[: start - first["start"]]
    suffix = last_run.text[end - last["start"] :]
    first_run.text = prefix
    for info in affected[1:]:
        info["run"].text = ""
    inserted = _insert_run_after(paragraph, first_run, value, template_run=first_run, color=color)
    if suffix:
        _insert_run_after(paragraph, inserted, suffix, template_run=last_run)


def _insert_run_after(paragraph, anchor_run, text: str, template_run=None, color: RGBColor | None = None):
    new_r = OxmlElement("w:r")
    anchor_run._r.addnext(new_r)
    new_run = Run(new_r, paragraph)
    if template_run is not None and template_run._r.rPr is not None:
        new_run._r.insert(0, deepcopy(template_run._r.rPr))
    new_run.text = text
    if color is not None and text:
        new_run.font.color.rgb = color
    return new_run
