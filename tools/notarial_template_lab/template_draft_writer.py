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
        paragraph_by_block = self._paragraph_map(doc)
        block_by_id = {block.block_id: block for block in document_map.blocks}
        replacements: list[DraftReplacement] = []
        skipped: list[dict] = []

        for proposal in proposals:
            skip_reason = self._proposal_skip_reason(proposal, block_by_id, min_confidence)
            if skip_reason:
                skipped.append({"field_key": proposal.field_key, "value": proposal.value, "reason": skip_reason})
                continue

            for occurrence in sorted(proposal.occurrences, key=lambda item: (item.block_id, item.start), reverse=True):
                paragraph = paragraph_by_block.get(occurrence.block_id)
                block = block_by_id.get(occurrence.block_id)
                if paragraph is None or block is None:
                    skipped.append({"field_key": proposal.field_key, "value": proposal.value, "reason": "No se encontro el bloque en la copia DOCX."})
                    continue
                if block.structural_hints.get("is_heading_like") or looks_like_title(block.raw_text):
                    skipped.append({"field_key": proposal.field_key, "value": proposal.value, "reason": "El bloque parece titulo o encabezado juridico."})
                    continue
                if self._replace_in_runs(paragraph, proposal.value, proposal.marker, occurrence):
                    replacements.append(
                        DraftReplacement(
                            field_key=proposal.field_key,
                            marker=proposal.marker,
                            value=proposal.value,
                            block_id=occurrence.block_id,
                            location=occurrence.location,
                        )
                    )
                else:
                    skipped.append({"field_key": proposal.field_key, "value": proposal.value, "reason": "La ocurrencia cruza runs o no coincide exactamente en un run."})

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
            if block and (block.structural_hints.get("is_heading_like") or looks_like_title(block.raw_text)):
                return "Una ocurrencia esta en un titulo o encabezado."
        return None

    def _replace_in_runs(self, paragraph: Paragraph, value: str, marker: str, occurrence=None) -> bool:
        if occurrence is not None:
            cursor = 0
            for run in paragraph.runs:
                text = run.text or ""
                run_start = occurrence.start - cursor
                if run_start < 0 or run_start > len(text):
                    cursor += len(text)
                    continue
                run_end = run_start + len(value)
                if run_end <= len(text) and text[run_start:run_end] == value:
                    run.text = f"{text[:run_start]}{marker}{text[run_end:]}"
                    return True
                cursor += len(text)
        for run in paragraph.runs:
            if value in (run.text or ""):
                run.text = run.text.replace(value, marker, 1)
                return True
        return False

    def _paragraph_map(self, doc: DocxDocument) -> dict[str, Paragraph]:
        result: dict[str, Paragraph] = {}
        for paragraph, location in self._iter_document_paragraphs(doc):
            result[f"block_{stable_id(location)}"] = paragraph
        return result

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
