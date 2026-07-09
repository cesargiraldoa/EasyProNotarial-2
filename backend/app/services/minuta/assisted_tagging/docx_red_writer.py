from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.shared import RGBColor

from app.services.minuta.assisted_tagging.models import TaggingFieldProposal
from app.services.minuta.engine.docx_renderer import DocxRenderer
from app.services.minuta.engine.template_analyzer import iter_document_paragraphs

RED_COLOR = RGBColor(0xFF, 0x00, 0x00)


class DocxRedWriter:
    def write(self, source_path: str | Path, destination_path: str | Path, fields: list[TaggingFieldProposal]) -> dict:
        document = Document(str(source_path))
        renderer = DocxRenderer()
        marked = 0
        texts = sorted({field.text for field in fields if field.text}, key=len, reverse=True)

        for paragraph, _location in iter_document_paragraphs(document):
            paragraph_text = paragraph.text or ""
            if not paragraph_text:
                continue
            occupied: list[tuple[int, int]] = []
            for text in texts:
                start = 0
                while True:
                    index = paragraph_text.find(text, start)
                    if index < 0:
                        break
                    end = index + len(text)
                    start = end
                    if any(not (end <= taken_start or index >= taken_end) for taken_start, taken_end in occupied):
                        continue
                    affected = renderer._affected_runs(paragraph, index, end)
                    if not affected:
                        continue
                    renderer._replace_affected_runs(paragraph, affected, index, end, text, RED_COLOR)
                    occupied.append((index, end))
                    marked += 1

        destination = Path(destination_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        document.save(str(destination))
        return {"red_runs_written": marked, "field_count": len(fields)}
