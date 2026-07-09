from __future__ import annotations

import io
import re
import unicodedata
from collections import OrderedDict
from pathlib import Path

from docx import Document

from app.services.minuta.assisted_tagging.models import ApprovedTemplateResult, TaggingFieldProposal
from app.services.minuta.engine.template_analyzer import iter_document_paragraphs


def _is_red(run) -> bool:
    color = getattr(run.font.color, "rgb", None)
    return color is not None and str(color).upper() == "FF0000"


def _normalize_code(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_value = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    code = re.sub(r"[^a-zA-Z0-9]+", "_", ascii_value.lower()).strip("_")
    if not code:
        code = "campo"
    if code[0].isdigit():
        code = f"campo_{code}"
    return code[:80]


def _label(value: str, index: int) -> str:
    clean = " ".join((value or "").split())
    if len(clean) > 45:
        clean = clean[:45].rstrip()
    return clean or f"Campo {index}"


class ApprovedTemplateParser:
    def parse(self, docx_path: str | Path) -> ApprovedTemplateResult:
        document = Document(str(docx_path))
        warnings: list[str] = []
        segment_to_code: OrderedDict[str, str] = OrderedDict()
        fields: list[TaggingFieldProposal] = []

        for paragraph, _location in iter_document_paragraphs(document):
            red_groups = self._red_run_groups(paragraph)
            for group in red_groups:
                text = " ".join("".join(run.text or "" for run in group).split())
                if len(text) < 2:
                    continue
                if text not in segment_to_code:
                    code = self._unique_code(_normalize_code(text), set(segment_to_code.values()))
                    segment_to_code[text] = code
                    fields.append(
                        TaggingFieldProposal(
                            field_code=code,
                            label=_label(text, len(fields) + 1),
                            text=text,
                            section="general",
                            confidence=1.0,
                            source="human_red",
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
