from __future__ import annotations

import json
import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from docx import Document
from docx.shared import RGBColor
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes.inverse_conversion_engine import router as inverse_conversion_router
from app.services.minuta.inverse_conversion_writer import DocxMarkedWriter, MarkedCandidate, MarkedCandidateContext


RED = RGBColor(0xFF, 0x00, 0x00)


class InverseConversionWriterTests(unittest.TestCase):
    def _build_docx_bytes(self) -> bytes:
        buffer = BytesIO()
        document = Document()
        document.add_paragraph(
            "EL COMPRADOR identificado con C.C. 1.037.657.164, celular 3001234567 y correo juan@example.com."
        )
        document.add_paragraph("Texto juridico fijo que debe permanecer sin marcas.")
        document.save(buffer)
        return buffer.getvalue()

    def _write_source(self, directory: str) -> Path:
        source = Path(directory) / "Salida del pais.docx"
        source.write_bytes(self._build_docx_bytes())
        return source

    def _candidate(self, text: str, status: str = "accepted") -> MarkedCandidate:
        return MarkedCandidate(
            id=f"cand-{text}",
            text=text,
            suggested_key="campo_detectado",
            label="Campo detectado",
            status=status,
            confidence=0.95,
            occurrences=1,
            contexts=(MarkedCandidateContext(location="paragraph 1"),),
        )

    def _runs_for_text(self, path: Path, text: str):
        document = Document(str(path))
        return [run for paragraph in document.paragraphs for run in paragraph.runs if run.text == text]

    def test_writer_generates_new_file_and_does_not_modify_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = self._write_source(tmp)
            original_bytes = source.read_bytes()
            output = Path(tmp) / "marked.docx"

            result = DocxMarkedWriter().write(source, output, [self._candidate("juan@example.com")])

            self.assertTrue(output.exists())
            self.assertEqual(result.marked_occurrences, 1)
            self.assertEqual(source.read_bytes(), original_bytes)

    def test_writer_marks_accepted_texts_red_and_ignores_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = self._write_source(tmp)
            output = Path(tmp) / "marked.docx"

            DocxMarkedWriter().write(
                source,
                output,
                [
                    self._candidate("juan@example.com", status="accepted"),
                    self._candidate("1.037.657.164", status="accepted"),
                    self._candidate("3001234567", status="rejected"),
                ],
            )

            self.assertTrue(any(run.font.color.rgb == RED for run in self._runs_for_text(output, "juan@example.com")))
            self.assertTrue(any(run.font.color.rgb == RED for run in self._runs_for_text(output, "1.037.657.164")))
            self.assertFalse(any(run.font.color.rgb == RED for run in self._runs_for_text(output, "3001234567")))

    def test_writer_rejects_without_accepted_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = self._write_source(tmp)
            output = Path(tmp) / "marked.docx"

            with self.assertRaises(ValueError):
                DocxMarkedWriter().write(source, output, [self._candidate("juan@example.com", status="rejected")])

    def test_endpoint_generates_downloadable_docx(self):
        app = FastAPI()
        app.include_router(inverse_conversion_router, prefix="/api/v1")
        client = TestClient(app)
        candidates = [
            {
                "id": "cand_001",
                "text": "juan@example.com",
                "suggested_key": "email_comprador",
                "label": "Email comprador",
                "status": "accepted",
                "confidence": 0.95,
                "occurrences": 1,
                "contexts": [{"location": "paragraph 1", "before": "correo", "after": "."}],
            }
        ]

        response = client.post(
            "/api/v1/inverse-conversion/generate-marked-docx",
            files={
                "archivo": (
                    "Salida del pais.docx",
                    self._build_docx_bytes(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
            data={"candidates": json.dumps(candidates)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        self.assertIn("Salida%20del%20pais%20-%20marcado.docx", response.headers["content-disposition"])
        self.assertGreater(len(response.content), 0)

    def test_endpoint_returns_controlled_error_without_accepted_candidates(self):
        app = FastAPI()
        app.include_router(inverse_conversion_router, prefix="/api/v1")
        client = TestClient(app)
        candidates = [{"id": "cand_001", "text": "juan@example.com", "status": "rejected"}]

        response = client.post(
            "/api/v1/inverse-conversion/generate-marked-docx",
            files={
                "archivo": (
                    "Salida del pais.docx",
                    self._build_docx_bytes(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
            data={"candidates": json.dumps(candidates)},
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("aceptar al menos un candidato", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
