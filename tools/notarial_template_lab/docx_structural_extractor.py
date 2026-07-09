from __future__ import annotations

import hashlib
import re
import unicodedata
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

from docx import Document
from docx.document import Document as DocxDocument
from docx.enum.text import WD_COLOR_INDEX
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph

from tools.notarial_template_lab.models import (
    BlockMap,
    DocumentMap,
    DocumentQuality,
    Occurrence,
    RunMap,
    RunStyle,
)


OCCURRENCE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("real_estate_registration", re.compile(r"\b\d{3}-\d{5,10}\b")),
    ("nit", re.compile(r"\b\d{3}(?:\.\d{3}){2}-\d\b")),
    ("dotted_document", re.compile(r"\b\d{1,3}(?:\.\d{3}){2,3}\b")),
    ("money", re.compile(r"\$\s*\d{1,3}(?:\.\d{3})+(?:,\d{2})?\b")),
    ("email", re.compile(r"\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b", re.IGNORECASE)),
    ("phone", re.compile(r"(?<!\d)(?:\+?57[\s.\-]?)?(?:3\d{2}|60[1-8])[\s.\-]?\d{3}[\s.\-]?\d{4}(?!\d)")),
    ("long_property_code", re.compile(r"\b\d{15,35}\b")),
    ("date", re.compile(r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+de\s+[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+\s+de\s+\d{4})\b", re.IGNORECASE)),
    ("uppercase_relevant_phrase", re.compile(r"\b[A-ZÁÉÍÓÚÜÑ]{3,}(?:\s+(?:DE|DEL|LA|LAS|LOS|Y|EN|CON|[A-ZÁÉÍÓÚÜÑ]{3,})){1,10}\b")),
]


class DocxStructuralExtractor:
    def extract(self, docx_path: str | Path) -> DocumentMap:
        path = Path(docx_path)
        document_id = self._document_id(path)
        doc = Document(str(path))
        blocks: list[BlockMap] = []
        all_runs: list[RunMap] = []

        for block in self._extract_body_blocks(doc):
            blocks.append(block)
            all_runs.extend(block.runs)

        for section_index, section in enumerate(doc.sections, start=1):
            for block in self._extract_header_footer_blocks(section.header, f"header section {section_index}"):
                blocks.append(block)
                all_runs.extend(block.runs)
            for block in self._extract_header_footer_blocks(section.footer, f"footer section {section_index}"):
                blocks.append(block)
                all_runs.extend(block.runs)

        occurrences_index = self._build_occurrences_index(blocks)
        total_occurrences = sum(len(items) for items in occurrences_index.values())
        quality = DocumentQuality(
            total_blocks=len(blocks),
            empty_blocks=sum(1 for block in blocks if block.is_empty),
            total_runs=len(all_runs),
            total_occurrences=total_occurrences,
            warnings=self._quality_warnings(blocks, all_runs, total_occurrences),
        )
        return DocumentMap(
            document_id=document_id,
            source_filename=path.name,
            quality=quality,
            blocks=blocks,
            runs=all_runs,
            occurrences_index=occurrences_index,
        )

    def _document_id(self, path: Path) -> str:
        digest = hashlib.sha1(path.read_bytes()).hexdigest()[:16]
        return f"doc_{digest}"

    def _extract_body_blocks(self, doc: DocxDocument) -> Iterable[BlockMap]:
        yield from self._iter_blocks(doc, part="body", prefix="body")

    def _extract_header_footer_blocks(self, part, label: str) -> Iterable[BlockMap]:
        yield from self._iter_blocks(part, part=label, prefix=label)

    def _iter_blocks(self, parent, part: str, prefix: str) -> Iterable[BlockMap]:
        paragraph_index = 0
        table_index = 0
        for child in self._iter_block_items(parent):
            if isinstance(child, Paragraph):
                paragraph_index += 1
                location = f"{prefix}/paragraph {paragraph_index}"
                yield self._paragraph_to_block(child, location, part, "paragraph")
            elif isinstance(child, Table):
                table_index += 1
                yield from self._iter_table(child, part, f"{prefix}/table {table_index}")

    def _iter_table(self, table: Table, part: str, prefix: str) -> Iterable[BlockMap]:
        seen_cells: set[int] = set()
        for row_index, row in enumerate(table.rows, start=1):
            for cell_index, cell in enumerate(row.cells, start=1):
                cell_id = id(cell._tc)
                if cell_id in seen_cells:
                    continue
                seen_cells.add(cell_id)
                cell_prefix = f"{prefix}/row {row_index}/cell {cell_index}"
                yield from self._iter_blocks(cell, part=part, prefix=cell_prefix)

    def _iter_block_items(self, parent) -> Iterable[Paragraph | Table]:
        if isinstance(parent, DocxDocument):
            parent_elm = parent.element.body
        elif isinstance(parent, _Cell):
            parent_elm = parent._tc
        else:
            parent_elm = getattr(parent, "_element", None)
            if parent_elm is None:
                return

        for child in parent_elm.iterchildren():
            if isinstance(child, CT_P) or child.tag.endswith("}p"):
                yield Paragraph(child, parent)
            elif isinstance(child, CT_Tbl) or child.tag.endswith("}tbl"):
                yield Table(child, parent)

    def _paragraph_to_block(self, paragraph: Paragraph, location: str, part: str, kind: str) -> BlockMap:
        raw_text = paragraph.text or ""
        normalized = normalize_text(raw_text)
        block_id = f"block_{stable_id(location)}"
        runs = self._runs_for_paragraph(paragraph, block_id)
        style_name = getattr(getattr(paragraph, "style", None), "name", None)
        structural_hints = {
            "part": part,
            "paragraph_style": style_name,
            "in_table": "/table " in location,
            "is_heading_like": bool(style_name and style_name.lower().startswith("heading")),
        }
        return BlockMap(
            block_id=block_id,
            kind=kind,
            location=location,
            raw_text=raw_text,
            normalized_text=normalized,
            char_count=len(raw_text),
            is_empty=not raw_text.strip(),
            structural_hints=structural_hints,
            runs=runs,
        )

    def _runs_for_paragraph(self, paragraph: Paragraph, block_id: str) -> list[RunMap]:
        runs: list[RunMap] = []
        cursor = 0
        for index, run in enumerate(paragraph.runs, start=1):
            text = run.text or ""
            start = cursor
            end = start + len(text)
            runs.append(
                RunMap(
                    run_id=f"{block_id}_run_{index:03d}",
                    block_id=block_id,
                    text=text,
                    start=start,
                    end=end,
                    style=RunStyle(
                        bold=run.bold,
                        italic=run.italic,
                        underline=bool(run.underline) if run.underline is not None else None,
                        highlight_color=enum_name(run.font.highlight_color, ignore={WD_COLOR_INDEX.AUTO}),
                        font_color=font_color(run),
                        font_size=float(run.font.size.pt) if run.font.size is not None else None,
                    ),
                )
            )
            cursor = end
        return runs

    def _build_occurrences_index(self, blocks: list[BlockMap]) -> dict[str, list[Occurrence]]:
        grouped: dict[str, list[Occurrence]] = defaultdict(list)
        counter = 0
        for block in blocks:
            text = block.raw_text or ""
            occupied: list[tuple[int, int, str]] = []
            for occurrence_type, pattern in OCCURRENCE_PATTERNS:
                for match in pattern.finditer(text):
                    if occurrence_type == "dotted_document" and self._is_inside_existing(match.start(), match.end(), occupied, {"nit", "money"}):
                        continue
                    if occurrence_type == "uppercase_relevant_phrase" and not self._valid_uppercase_phrase(match.group(0)):
                        continue
                    counter += 1
                    occurrence = Occurrence(
                        occurrence_id=f"occ_{counter:05d}",
                        occurrence_type=occurrence_type,
                        text=match.group(0).strip(),
                        block_id=block.block_id,
                        location=block.location,
                        start=match.start(),
                        end=match.end(),
                        before=collapse_spaces(text[max(0, match.start() - 100):match.start()]),
                        after=collapse_spaces(text[match.end():match.end() + 100]),
                    )
                    grouped[occurrence_type].append(occurrence)
                    occupied.append((match.start(), match.end(), occurrence_type))
        return dict(grouped)

    def _is_inside_existing(self, start: int, end: int, occupied: list[tuple[int, int, str]], types: set[str]) -> bool:
        return any(start >= left and end <= right and occurrence_type in types for left, right, occurrence_type in occupied)

    def _valid_uppercase_phrase(self, text: str) -> bool:
        stripped = collapse_spaces(text)
        if len(stripped) < 8 or len(stripped) > 120:
            return False
        words = stripped.split()
        if len(words) < 2:
            return False
        return any(len(word) >= 4 for word in words)

    def _quality_warnings(self, blocks: list[BlockMap], runs: list[RunMap], total_occurrences: int) -> list[str]:
        warnings: list[str] = []
        if not blocks:
            warnings.append("No se encontraron bloques de texto.")
        if not runs:
            warnings.append("No se encontraron runs; el documento puede no tener texto editable.")
        if total_occurrences == 0:
            warnings.append("No se encontraron ocurrencias tecnicas con los patrones generales.")
        return warnings


def stable_id(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:12]


def collapse_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text or "")
    return collapse_spaces(normalized)


def enum_name(value, ignore: set | None = None) -> str | None:
    if value is None:
        return None
    if ignore and value in ignore:
        return None
    return getattr(value, "name", str(value))


def font_color(run) -> str | None:
    color = getattr(run.font, "color", None)
    rgb = getattr(color, "rgb", None)
    return str(rgb) if rgb is not None else None
