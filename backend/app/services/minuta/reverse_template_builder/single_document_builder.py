from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.document import Document as DocxDocument
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph

from app.services.minuta.reverse_template_builder.candidate_detector import detect_candidates
from app.services.minuta.reverse_template_builder.candidate_grouper import group_candidates
from app.services.minuta.reverse_template_builder.models import TextBlock


class SingleDocumentReverseTemplateBuilder:
    def analyze(self, docx_path: str | Path, filename: str | None = None) -> dict:
        blocks = list(iter_docx_text_blocks(docx_path))
        occurrences = detect_candidates(blocks)
        candidates = group_candidates(occurrences)
        summary = build_summary(candidates)

        return {
            "mode": "single",
            "filename": filename or Path(docx_path).name,
            "candidates": [candidate.to_dict() for candidate in candidates],
            "summary": summary,
        }


def build_summary(candidates) -> dict:
    high = sum(1 for candidate in candidates if candidate.confidence >= 0.8)
    medium = sum(1 for candidate in candidates if 0.5 <= candidate.confidence < 0.8)
    low = sum(1 for candidate in candidates if candidate.confidence < 0.5)
    return {
        "total_candidates": len(candidates),
        "high_confidence": high,
        "medium_confidence": medium,
        "low_confidence": low,
    }


def iter_docx_text_blocks(docx_path: str | Path):
    doc = Document(str(docx_path))
    yield from _iter_blocks(doc)


def _iter_blocks(parent, prefix: str = ""):
    paragraph_index = 0
    table_index = 0
    for block in _iter_block_items(parent):
        if isinstance(block, Paragraph):
            paragraph_index += 1
            text = block.text.strip()
            if text:
                location = f"{prefix}paragraph {paragraph_index}" if prefix else f"paragraph {paragraph_index}"
                yield TextBlock(text=text, location=location)
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
