from __future__ import annotations

import re
from copy import deepcopy
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.shared import RGBColor
from docx.text.run import Run

from app.services.minuta.engine.models import PlaceholderAudit, RenderAudit
from app.services.minuta.engine.template_analyzer import iter_document_paragraphs
from app.services.minuta.rules.conditional_blocks import should_remove_si_aplica_block

RED_COLOR = RGBColor(0xFF, 0x00, 0x00)
TECHNICAL_TAB_TOKEN = "[[--]]"
AUXILIARY_TOKEN_PATTERN = re.compile(r"\[SI APLICA[^\]]*\]|\[NO APLICA[^\]]*\]|\[N[úu]mero\]|\[Informaci[óo]n\]", re.IGNORECASE)
DASH_SEQUENCE_PATTERN = re.compile(r"(?:-\s*){3,}|-{3,}")


def copy_run_format(source_run, target_run) -> None:
    if source_run is None or target_run is None:
        return
    if source_run._r.rPr is not None:
        target_run._r.insert(0, deepcopy(source_run._r.rPr))


def insert_run_after(paragraph, anchor_run, text: str, template_run=None, color: RGBColor | None = None):
    new_r = OxmlElement("w:r")
    anchor_run._r.addnext(new_r)
    new_run = Run(new_r, paragraph)
    if template_run is not None:
        copy_run_format(template_run, new_run)
    new_run.text = text
    if color is not None and text:
        new_run.font.color.rgb = color
    return new_run


def set_paragraph_text_preserving_first_run(paragraph, new_text: str) -> None:
    runs = list(paragraph.runs)
    if not runs:
        if new_text:
            paragraph.add_run(new_text)
        return
    runs[0].text = new_text
    for run in runs[1:]:
        run.text = ""


class DocxRenderer:
    def render(
        self,
        source_path: str | Path,
        destination_path: str | Path,
        marker_values: dict[str, str],
        marker_keys: dict[str, str | None],
        normalized_values: dict[str, str],
    ) -> RenderAudit:
        document = Document(str(source_path))
        audit = RenderAudit(structure_before=self._structure(document))

        for marker in sorted(marker_values, key=len, reverse=True):
            value = marker_values[marker]
            field_key = marker_keys.get(marker)
            marker_seen = False
            for paragraph, location in iter_document_paragraphs(document):
                audit_items = self._replace_marker_in_paragraph(paragraph, marker, value, field_key, location)
                if audit_items:
                    marker_seen = True
                for item in audit_items:
                    if not item.inserted_value:
                        audit.empty.append(item)
                    elif item.replaced:
                        audit.replaced.append(item)
                    else:
                        audit.missing.append(item)
            if not marker_seen:
                audit.missing.append(
                    PlaceholderAudit(
                        placeholder=marker,
                        field_key=field_key,
                        inserted_value=value,
                        location="document",
                        color_applied=None,
                        style_preserved=False,
                        replaced=False,
                    )
                )

        self._remove_conditional_blocks(document, normalized_values)
        audit.technical_tabs_resolved = self._resolve_technical_tabs(document)
        self._remove_auxiliary_tokens(document)
        self._normalize_known_gender_literals(document, normalized_values)
        audit.structure_after = self._structure(document)
        audit.notarial_dash_sequences_preserved = min(
            audit.structure_before.get("dash_sequences", 0),
            audit.structure_after.get("dash_sequences", 0),
        )
        document.save(str(destination_path))
        return audit

    def _replace_marker_in_paragraph(
        self,
        paragraph,
        marker: str,
        value: str,
        field_key: str | None,
        location: str,
        color: RGBColor | None = RED_COLOR,
    ) -> list[PlaceholderAudit]:
        text = paragraph.text or ""
        matches = list(re.finditer(re.escape(marker), text))
        if not matches:
            return []
        audits: list[PlaceholderAudit] = []
        for match in reversed(matches):
            affected = self._affected_runs(paragraph, match.start(), match.end())
            if not affected:
                continue
            self._replace_affected_runs(paragraph, affected, match.start(), match.end(), value, color)
            audits.append(
                PlaceholderAudit(
                    placeholder=marker,
                    field_key=field_key,
                    inserted_value=value,
                    location=location,
                    color_applied="FF0000" if value and color is not None else None,
                    style_preserved=True,
                    replaced=True,
                )
            )
        return audits

    def _affected_runs(self, paragraph, start: int, end: int) -> list[dict]:
        runs_info: list[dict] = []
        position = 0
        for run in paragraph.runs:
            run_end = position + len(run.text)
            runs_info.append({"run": run, "start": position, "end": run_end})
            position = run_end
        affected: list[dict] = []
        for info in runs_info:
            if info["end"] <= start:
                continue
            if info["start"] >= end:
                break
            affected.append(info)
        return affected

    def _replace_affected_runs(
        self,
        paragraph,
        affected: list[dict],
        start: int,
        end: int,
        value: str,
        color: RGBColor | None = RED_COLOR,
    ) -> None:
        first = affected[0]
        last = affected[-1]
        first_run = first["run"]
        last_run = last["run"]
        prefix = first_run.text[: start - first["start"]]
        suffix = last_run.text[end - last["start"] :]
        first_run.text = prefix
        for info in affected[1:]:
            info["run"].text = ""
        inserted = insert_run_after(paragraph, first_run, value, template_run=first_run, color=color)
        if suffix:
            insert_run_after(paragraph, inserted, suffix, template_run=last_run)

    def _remove_conditional_blocks(self, document: Document, normalized_values: dict[str, str]) -> None:
        for paragraph, _location in iter_document_paragraphs(document):
            if should_remove_si_aplica_block(normalized_values, paragraph.text or ""):
                set_paragraph_text_preserving_first_run(paragraph, "")

    def _resolve_technical_tabs(self, document: Document) -> int:
        resolved = 0
        for paragraph, _location in iter_document_paragraphs(document):
            audit_items = self._replace_marker_in_paragraph(paragraph, TECHNICAL_TAB_TOKEN, "\t", None, "technical-tab", color=None)
            resolved += len(audit_items)
        return resolved

    def _remove_auxiliary_tokens(self, document: Document) -> None:
        for paragraph, _location in iter_document_paragraphs(document):
            tokens = sorted(set(AUXILIARY_TOKEN_PATTERN.findall(paragraph.text or "")), key=len, reverse=True)
            for token in tokens:
                self._replace_marker_in_paragraph(paragraph, token, "", None, "cleanup", color=None)

    def _normalize_known_gender_literals(self, document: Document, normalized_values: dict[str, str]) -> None:
        buyer_1 = bool(normalized_values.get("nombre_comprador_1") or normalized_values.get("nombre_comprador"))
        buyer_2 = bool(normalized_values.get("nombre_comprador_2"))
        replacement = "identificados" if buyer_1 and buyer_2 else "identificado"
        if buyer_1 and not buyer_2 and normalized_values.get("comprador_es_hombre_o_mujer", "").lower() == "mujer":
            replacement = "identificada"
        for paragraph, _location in iter_document_paragraphs(document):
            for marker in ("identificado(a/s)", "identificado(a)", "comprador(a)(es)"):
                self._replace_marker_in_paragraph(paragraph, marker, replacement if "identificado" in marker else "compradores", None, "gender-literal-cleanup", color=None)

    def _structure(self, document: Document) -> dict[str, int]:
        dash_sequences = 0
        for paragraph, _location in iter_document_paragraphs(document):
            dash_sequences += len(DASH_SEQUENCE_PATTERN.findall(paragraph.text or ""))
        return {
            "paragraphs": len(document.paragraphs),
            "tables": len(document.tables),
            "sections": len(document.sections),
            "dash_sequences": dash_sequences,
        }
