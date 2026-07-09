from __future__ import annotations

import io
import re
from collections import OrderedDict
from pathlib import Path

from docx import Document

from app.services.minuta.assisted_tagging.models import ApprovedTemplateResult, TaggingFieldProposal
from app.services.minuta.engine.template_analyzer import iter_document_paragraphs


def _is_red(run) -> bool:
    color = getattr(run.font.color, "rgb", None)
    return color is not None and str(color).upper() == "FF0000"


def _label(value: str, index: int) -> str:
    clean = " ".join((value or "").split())
    if len(clean) > 45:
        clean = clean[:45].rstrip()
    return clean or f"Campo {index}"


class ApprovedTemplateParser:
    def parse(self, docx_path: str | Path, known_fields: list[TaggingFieldProposal] | None = None) -> ApprovedTemplateResult:
        document = Document(str(docx_path))
        warnings: list[str] = []
        segment_to_code: OrderedDict[str, str] = OrderedDict()
        known_by_text = self._known_by_text(known_fields or [])
        fields: list[TaggingFieldProposal] = []
        human_counter = 0

        for paragraph, _location in iter_document_paragraphs(document):
            red_groups = self._red_run_groups(paragraph)
            for group in red_groups:
                text = " ".join("".join(run.text or "" for run in group).split())
                if len(text) < 2:
                    continue
                if text not in segment_to_code:
                    known = known_by_text.get(text)
                    if known is not None:
                        code = self._unique_code(known.field_code, set(segment_to_code.values()))
                        label = known.label
                        section = known.section
                        source = "approved_from_proposal"
                    else:
                        human_counter += 1
                        code = self._unique_code(f"campo_humano_{human_counter}", set(segment_to_code.values()))
                        label = f"Campo humano {human_counter}"
                        section = "general"
                        source = "human_red"
                    segment_to_code[text] = code
                    fields.append(
                        TaggingFieldProposal(
                            field_code=code,
                            label=label or _label(text, len(fields) + 1),
                            text=text,
                            section=section or "general",
                            confidence=1.0,
                            source=source,
                            occurrences=1,
                        )
                    )
                else:
                    code = segment_to_code[text]
                    for field in fields:
                        if field.field_code == code:
                            field.occurrences += 1
                            break
                group[0].text = f"{{{{{code.upper()}}}}}"
                for run in group[1:]:
                    run.text = ""

        if not fields:
            warnings.append("El DOCX aprobado no contiene texto rojo interpretable como variable.")

        buffer = io.BytesIO()
        document.save(buffer)
        return ApprovedTemplateResult(
            fields=fields,
            warnings=warnings,
            technical_docx=buffer.getvalue(),
            variable_count=sum(field.occurrences for field in fields),
        )

    def _red_run_groups(self, paragraph) -> list[list]:
        groups: list[list] = []
        current: list = []
        for run in paragraph.runs:
            if _is_red(run) and (run.text or "").strip():
                current.append(run)
            else:
                if current:
                    groups.append(current)
                    current = []
        if current:
            groups.append(current)
        return groups

    def _unique_code(self, base: str, used: set[str]) -> str:
        code = base
        suffix = 2
        while code in used:
            code = f"{base}_{suffix}"
            suffix += 1
        return code

    def _known_by_text(self, fields: list[TaggingFieldProposal]) -> dict[str, TaggingFieldProposal]:
        result: dict[str, TaggingFieldProposal] = {}
        for field in fields:
            text = " ".join((field.text or "").split())
            if text and text not in result:
                result[text] = field
        return result
