from __future__ import annotations

import shutil
from pathlib import Path

from docx import Document
from docx.document import Document as DocxDocument
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph

from tools.notarial_template_lab.docx_structural_extractor import stable_id
from tools.notarial_template_lab.field_proposer import looks_like_title
from tools.notarial_template_lab.models import (
    DocumentMap,
    DraftReplacement,
    DraftResult,
    FieldProposal,
)


class TemplateDraftWriter:
    def write(
        self,
        source_docx: str | Path,
        output_docx: str | Path,
        document_map: DocumentMap,
        proposals: list[FieldProposal],
        min_confidence: float = 0.8,
    ) -> DraftResult:
        source_path = Path(source_docx)
        output_path = Path(output_docx)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, output_path)

        doc = Document(str(output_path))
        paragraph_indexes = self._paragraph_indexes(doc)
        block_by_id = {block.block_id: block for block in document_map.blocks}
        replacements: list[DraftReplacement] = []
        skipped: list[dict] = []
        pending_by_block: dict[str, list[dict]] = {}

        for proposal in proposals:
            skip_reason = self._proposal_skip_reason(proposal, block_by_id, min_confidence)
            if skip_reason:
                if proposal.occurrences:
                    for occurrence in proposal.occurrences:
                        skipped.append(self._skip_item(proposal, occurrence, skip_reason))
                else:
                    skipped.append(
                        {
                            "field_key": proposal.field_key,
                            "marker": proposal.marker,
                            "value": proposal.value,
                            "block_id": "",
                            "location": "",
                            "start": None,
                            "end": None,
                            "expected_value": proposal.value,
                            "reason": skip_reason,
                            "failure_reason": skip_reason,
                            "applied": False,
                        }
                    )
                continue

            for occurrence in proposal.occurrences:
                block = block_by_id.get(occurrence.block_id)
                if block is None:
                    skipped.append(self._skip_item(proposal, occurrence, "block_id not found in DocumentMap."))
                    continue
                paragraph, lookup_failure = self._find_paragraph(occurrence, paragraph_indexes)
                if paragraph is None:
                    skipped.append(self._skip_item(proposal, occurrence, lookup_failure or "location not found in DOCX copy."))
                    continue
                block_skip_reason = self._block_skip_reason(block.raw_text, proposal.value, block.structural_hints)
                if block_skip_reason:
                    skipped.append(self._skip_item(proposal, occurrence, block_skip_reason))
                    continue
                pending_by_block.setdefault(occurrence.block_id, []).append(
                    {
                        "proposal": proposal,
                        "occurrence": occurrence,
                        "paragraph": paragraph,
                    }
                )

        for block_id, items in pending_by_block.items():
            block_replacements, block_skipped = self._apply_block_replacements(block_id, items)
            replacements.extend(block_replacements)
            skipped.extend(block_skipped)

        doc.save(str(output_path))
        return DraftResult(output_path=str(output_path), replacements=replacements, skipped=skipped)

    def _proposal_skip_reason(self, proposal: FieldProposal, block_by_id: dict, min_confidence: float) -> str | None:
        if proposal.confidence < min_confidence:
            return "Confianza insuficiente para reemplazo automatico."
        if proposal.proposal_type == "review_required" or proposal.apply_strategy == "review_required":
            return "La propuesta requiere revision."
        if proposal.proposal_type == "fixed_text":
            return "La propuesta describe texto fijo, no campo reemplazable."
        if proposal.apply_strategy not in {"all_occurrences", "selected_occurrences"}:
            return "Estrategia de aplicacion no reemplazable."
        if not proposal.occurrences:
            return "La propuesta no tiene ubicacion exacta."
        if looks_like_title(proposal.value):
            return "El valor parece frase larga, clausula o titulo."
        if len(proposal.value.split()) > 8:
            return "El valor es una frase larga y no se reemplaza automaticamente."
        for occurrence in proposal.occurrences:
            if not occurrence.block_id or not occurrence.location:
                return "Una ocurrencia no tiene block_id o location."
            block = block_by_id.get(occurrence.block_id)
            if block:
                block_skip_reason = self._block_skip_reason(block.raw_text, occurrence.text or proposal.value, block.structural_hints)
                if block_skip_reason:
                    return block_skip_reason
        return None

    def _block_skip_reason(self, block_text: str, value: str, structural_hints: dict) -> str | None:
        text = (block_text or "").strip()
        value = (value or "").strip()
        if not text:
            return None
        value_covers_block = bool(value) and len(value) >= max(12, int(len(text) * 0.8))
        short_heading_block = len(text) <= 180 and (structural_hints.get("is_heading_like") or looks_like_title(text))
        if short_heading_block and value_covers_block:
            return "occurrence is inside a title-like block"
        return None

    def _apply_block_replacements(self, block_id: str, items: list[dict]) -> tuple[list[DraftReplacement], list[dict]]:
        if not items:
            return [], []
        paragraph = items[0]["paragraph"]
        original_text = paragraph.text or ""
        updated_text = original_text
        replacements: list[DraftReplacement] = []
        skipped: list[dict] = []
        resolved_items: list[dict] = []

        for item in items:
            proposal: FieldProposal = item["proposal"]
            occurrence = item["occurrence"]
            expected = occurrence.text or proposal.value
            resolved = self._resolve_occurrence_range(original_text, occurrence.start, occurrence.end, expected)
            if resolved["failure_reason"]:
                skipped.append(self._skip_item(proposal, occurrence, resolved["failure_reason"]))
                continue
            resolved_items.append({**item, **resolved, "expected": expected})

        applied_ranges: list[tuple[int, int]] = []
        for item in sorted(resolved_items, key=lambda entry: entry["resolved_start"], reverse=True):
            proposal: FieldProposal = item["proposal"]
            occurrence = item["occurrence"]
            resolved_start = item["resolved_start"]
            resolved_end = item["resolved_end"]
            overlap = self._overlap_reason(resolved_start, resolved_end, applied_ranges)
            if overlap:
                skipped.append(self._skip_item(proposal, occurrence, overlap))
                continue
            updated_text = f"{updated_text[:resolved_start]}{proposal.marker}{updated_text[resolved_end:]}"
            applied_ranges.append((resolved_start, resolved_end))
            replacements.append(
                DraftReplacement(
                    field_key=proposal.field_key,
                    marker=proposal.marker,
                    value=item["expected"],
                    block_id=block_id,
                    location=occurrence.location,
                    applied=True,
                    reason=item["applied_reason"],
                )
            )

        if replacements and updated_text != original_text:
            self._replace_paragraph_text(paragraph, updated_text)
        return replacements, skipped

    def _resolve_occurrence_range(
        self,
        original_text: str,
        start: int,
        end: int,
        expected: str,
    ) -> dict:
        if start < 0 or end <= start or end > len(original_text):
            return self._fallback_range(original_text, expected, "offset range invalid")
        if original_text[start:end] == expected:
            return {
                "resolved_start": start,
                "resolved_end": end,
                "applied_reason": "offset exact match",
                "failure_reason": None,
            }
        return self._fallback_range(original_text, expected, "offset text mismatch")

    def _fallback_range(self, original_text: str, expected: str, base_reason: str) -> dict:
        if not expected:
            return self._failed_range(f"{base_reason}; expected value is empty")
        matches = []
        cursor = 0
        while True:
            index = original_text.find(expected, cursor)
            if index < 0:
                break
            matches.append((index, index + len(expected)))
            cursor = index + max(1, len(expected))
        if len(matches) == 1:
            start, end = matches[0]
            return {
                "resolved_start": start,
                "resolved_end": end,
                "applied_reason": f"{base_reason}; applied by unique text fallback",
                "failure_reason": None,
            }
        if len(matches) > 1:
            return self._failed_range(f"{base_reason}; expected text appears multiple times; occurrence ambiguous")
        return self._failed_range(f"{base_reason}; expected text not found in paragraph")

    def _failed_range(self, reason: str) -> dict:
        return {
            "resolved_start": None,
            "resolved_end": None,
            "applied_reason": None,
            "failure_reason": reason,
        }

    def _overlap_reason(self, start: int, end: int, applied_ranges: list[tuple[int, int]]) -> str | None:
        if any(start < applied_end and end > applied_start for applied_start, applied_end in applied_ranges):
            return "resolved occurrence overlaps another applied replacement"
        return None

    def _replace_paragraph_text(self, paragraph: Paragraph, text: str) -> None:
        base = self._base_run_style(paragraph)
        paragraph.text = text
        if paragraph.runs and base:
            run = paragraph.runs[0]
            run.style = base["style"]
            run.bold = base["bold"]
            run.italic = base["italic"]
            run.underline = base["underline"]
            run.font.size = base["font_size"]
            if base["font_color"] is not None:
                run.font.color.rgb = base["font_color"]
            if base["highlight_color"] is not None:
                run.font.highlight_color = base["highlight_color"]

    def _base_run_style(self, paragraph: Paragraph) -> dict | None:
        if not paragraph.runs:
            return None
        run = paragraph.runs[0]
        return {
            "style": run.style,
            "bold": run.bold,
            "italic": run.italic,
            "underline": run.underline,
            "font_size": run.font.size,
            "font_color": run.font.color.rgb,
            "highlight_color": run.font.highlight_color,
        }

    def _skip_item(self, proposal: FieldProposal, occurrence, reason: str) -> dict:
        return {
            "field_key": proposal.field_key,
            "marker": proposal.marker,
            "value": occurrence.text or proposal.value if occurrence is not None else proposal.value,
            "block_id": occurrence.block_id if occurrence is not None else "",
            "location": occurrence.location if occurrence is not None else "",
            "start": occurrence.start if occurrence is not None else None,
            "end": occurrence.end if occurrence is not None else None,
            "expected_value": occurrence.text or proposal.value if occurrence is not None else proposal.value,
            "applied": False,
            "reason": reason,
            "failure_reason": reason,
        }

    def _paragraph_indexes(self, doc: DocxDocument) -> dict[str, dict[str, Paragraph]]:
        by_block_id: dict[str, Paragraph] = {}
        by_location: dict[str, Paragraph] = {}
        by_normalized_location: dict[str, Paragraph] = {}
        for paragraph, location in self._iter_document_paragraphs(doc):
            by_block_id[f"block_{stable_id(location)}"] = paragraph
            by_location[location] = paragraph
            by_normalized_location[normalize_location(location)] = paragraph
        return {
            "by_block_id": by_block_id,
            "by_location": by_location,
            "by_normalized_location": by_normalized_location,
        }

    def _find_paragraph(self, occurrence, indexes: dict[str, dict[str, Paragraph]]) -> tuple[Paragraph | None, str | None]:
        if occurrence.block_id in indexes["by_block_id"]:
            return indexes["by_block_id"][occurrence.block_id], None
        if occurrence.location in indexes["by_location"]:
            return indexes["by_location"][occurrence.location], None
        normalized_location = normalize_location(occurrence.location)
        if normalized_location in indexes["by_normalized_location"]:
            return indexes["by_normalized_location"][normalized_location], None
        if occurrence.block_id:
            return None, "block_id not found in DOCX copy; location not found"
        return None, "location not found in DOCX copy"

    def _iter_document_paragraphs(self, doc: DocxDocument):
        yield from self._iter_blocks(doc, "body")
        for section_index, section in enumerate(doc.sections, start=1):
            yield from self._iter_blocks(section.header, f"header section {section_index}")
            yield from self._iter_blocks(section.footer, f"footer section {section_index}")

    def _iter_blocks(self, parent, prefix: str):
        paragraph_index = 0
        table_index = 0
        for child in self._iter_block_items(parent):
            if isinstance(child, Paragraph):
                paragraph_index += 1
                yield child, f"{prefix}/paragraph {paragraph_index}"
            elif isinstance(child, Table):
                table_index += 1
                yield from self._iter_table(child, f"{prefix}/table {table_index}")

    def _iter_table(self, table: Table, prefix: str):
        seen_cells: set[int] = set()
        for row_index, row in enumerate(table.rows, start=1):
            for cell_index, cell in enumerate(row.cells, start=1):
                cell_id = id(cell._tc)
                if cell_id in seen_cells:
                    continue
                seen_cells.add(cell_id)
                yield from self._iter_blocks(cell, f"{prefix}/row {row_index}/cell {cell_index}")

    def _iter_block_items(self, parent):
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


def normalize_location(value: str) -> str:
    return " ".join(str(value or "").replace("\\", "/").lower().split())
