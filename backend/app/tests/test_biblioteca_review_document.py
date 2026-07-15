from __future__ import annotations

import hashlib
import io
import zipfile
import unittest

from docx import Document
from lxml import etree

from app.services.biblioteca_motor.review_document import (
    FIELD_TAG_PREFIX,
    SUGGESTION_TAG_PREFIX,
    accept_suggestions_in_docx,
    cascade_field_controls_in_docx,
    prepare_review_document,
    reject_suggestions_in_docx,
    visible_text_from_docx,
)


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}
W = f"{{{W_NS}}}"


def _docx_with_split_runs() -> bytes:
    doc = Document()
    paragraph = doc.add_paragraph()
    paragraph.add_run("LOS COMPRADORES: ")
    bold = paragraph.add_run("Daniela")
    bold.bold = True
    italic = paragraph.add_run(" Campo")
    italic.italic = True
    paragraph.add_run(" firma.")
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def _docx_with_table() -> bytes:
    doc = Document()
    table = doc.add_table(rows=1, cols=1)
    table.cell(0, 0).text = "MATRICULA INMOBILIARIA 050-123456"
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def _document_xml(docx_bytes: bytes) -> etree._Element:
    with zipfile.ZipFile(io.BytesIO(docx_bytes), "r") as archive:
        return etree.fromstring(archive.read("word/document.xml"))


def _tags(docx_bytes: bytes) -> list[str]:
    root = _document_xml(docx_bytes)
    return [item.get(f"{W}val") for item in root.findall(".//w:sdtPr/w:tag", NS)]


def _suggestion(original: str, start: int, end: int, text: str, **location_overrides):
    location = {
        "block_type": "paragraph",
        "block_index": 1,
        "paragraph_index": 1,
        "table_index": None,
        "row_index": None,
        "cell_index": None,
        "char_start": start,
        "char_end": end,
        "occurrence_index": 1,
        "location_key": f"paragraph:1:{start}:{end}:1",
        "block_hash": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }
    location.update(location_overrides)
    return {
        "suggestion_id": "sug_1",
        "candidate_id": "cand_1",
        "original_text": original,
        "field_code": "COMPRADOR_1",
        "field_label": "Comprador 1",
        "category": "persona",
        "confidence": 0.97,
        "source": "deterministic",
        "location": location,
        "context_before": "",
        "context_after": "",
    }


class BibliotecaReviewDocumentTests(unittest.TestCase):
    def test_wraps_exact_paragraph_span_in_content_control_preserving_visible_text(self):
        docx = _docx_with_split_runs()
        text = "LOS COMPRADORES: Daniela Campo firma."
        start = text.index("Daniela Campo")
        end = start + len("Daniela Campo")
        result = prepare_review_document(docx, [_suggestion("Daniela Campo", start, end, text)], analysis_id="analysis_1")
        root = _document_xml(result.docx_bytes)

        self.assertEqual(visible_text_from_docx(result.docx_bytes), visible_text_from_docx(docx))
        self.assertEqual(result.wrapped_count, 1)
        self.assertEqual(len(root.findall(".//w:sdt", NS)), 1)
        self.assertTrue(_tags(result.docx_bytes)[0].startswith(SUGGESTION_TAG_PREFIX))
        self.assertEqual(len(root.findall(".//w:highlight[@w:val='yellow']", NS)), 2)
        self.assertTrue(root.findall(".//w:sdtContent//w:b", NS))
        self.assertTrue(root.findall(".//w:sdtContent//w:i", NS))

    def test_wraps_table_cell_span(self):
        docx = _docx_with_table()
        text = "MATRICULA INMOBILIARIA 050-123456"
        start = text.index("050-123456")
        suggestion = _suggestion(
            "050-123456",
            start,
            start + len("050-123456"),
            text,
            block_type="table_cell",
            paragraph_index=None,
            table_index=1,
            row_index=1,
            cell_index=1,
            location_key=f"table_cell:1:1:1:{start}:{start + len('050-123456')}:1",
        )
        suggestion["field_code"] = "MATRICULA_INMOBILIARIA"

        result = prepare_review_document(docx, [suggestion], analysis_id="analysis_1")

        self.assertEqual(result.wrapped_count, 1)
        self.assertIn("MATRICULA INMOBILIARIA 050-123456", visible_text_from_docx(result.docx_bytes))
        self.assertTrue(_tags(result.docx_bytes)[0].startswith(SUGGESTION_TAG_PREFIX))

    def test_accept_transforms_suggestion_to_field_control_and_replaces_visible_value(self):
        docx = _docx_with_split_runs()
        text = "LOS COMPRADORES: Daniela Campo firma."
        start = text.index("Daniela Campo")
        result = prepare_review_document(docx, [_suggestion("Daniela Campo", start, start + 13, text)], analysis_id="analysis_1")
        tag = _tags(result.docx_bytes)[0]

        accepted = accept_suggestions_in_docx(
            result.docx_bytes,
            [{"suggestion_tag": tag, "field_instance_id": "COMPRADOR_1", "occurrence_id": "occ_001"}],
        )

        self.assertIn("{{COMPRADOR_1}}", visible_text_from_docx(accepted))
        self.assertFalse([item for item in _tags(accepted) if item.startswith(SUGGESTION_TAG_PREFIX)])
        self.assertTrue([item for item in _tags(accepted) if item.startswith(FIELD_TAG_PREFIX)])
        self.assertFalse(_document_xml(accepted).findall(".//w:highlight", NS))

    def test_reject_unwraps_suggestion_and_keeps_original_text(self):
        docx = _docx_with_split_runs()
        text = "LOS COMPRADORES: Daniela Campo firma."
        start = text.index("Daniela Campo")
        result = prepare_review_document(docx, [_suggestion("Daniela Campo", start, start + 13, text)], analysis_id="analysis_1")
        rejected = reject_suggestions_in_docx(result.docx_bytes, [_tags(result.docx_bytes)[0]])

        self.assertEqual(visible_text_from_docx(rejected), visible_text_from_docx(docx))
        self.assertFalse(_document_xml(rejected).findall(".//w:sdt", NS))

    def test_backend_cascade_updates_only_matching_field_instance(self):
        docx = _docx_with_split_runs()
        text = "LOS COMPRADORES: Daniela Campo firma."
        start = text.index("Daniela Campo")
        result = prepare_review_document(docx, [_suggestion("Daniela Campo", start, start + 13, text)], analysis_id="analysis_1")
        field_docx = accept_suggestions_in_docx(
            result.docx_bytes,
            [{"suggestion_tag": _tags(result.docx_bytes)[0], "field_instance_id": "COMPRADOR_1", "occurrence_id": "occ_001"}],
        )

        cascaded, updated = cascade_field_controls_in_docx(field_docx, "COMPRADOR_1", "Maria Perez")

        self.assertEqual(updated, 1)
        self.assertIn("Maria Perez", visible_text_from_docx(cascaded))


if __name__ == "__main__":
    unittest.main()
