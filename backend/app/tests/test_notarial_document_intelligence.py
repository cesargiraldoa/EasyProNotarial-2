from __future__ import annotations

import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from docx import Document
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models.notarial_document_intelligence import (
    NotarialDocument,
    NotarialDocumentBatch,
    NotarialDocumentBatchItem,
    NotarialDocumentBlock,
    NotarialDocumentCluster,
    NotarialDocumentClusterMember,
    NotarialDocumentDecision,
    NotarialDocumentEmbedding,
    NotarialDocumentEntity,
    NotarialDocumentEvidence,
    NotarialDocumentFamily,
    NotarialDocumentFamilyMember,
    NotarialDocumentSection,
    NotarialEmbeddingVersion,
)
from app.services.notarial_document_intelligence.contracts import (
    DocumentProcessingStatus,
    DocumentUpload,
    IngestBatchRequest,
)
from app.services.notarial_document_intelligence.ingestion import NotarialDocumentIngestionService
from app.services.notarial_document_intelligence.parser import NotarialDocumentParser
from app.services.notarial_document_intelligence.storage import NotarialIntelligenceStorage


TABLES = [
    NotarialDocumentBatch.__table__,
    NotarialDocumentFamily.__table__,
    NotarialDocument.__table__,
    NotarialDocumentBatchItem.__table__,
    NotarialDocumentSection.__table__,
    NotarialDocumentBlock.__table__,
    NotarialDocumentEntity.__table__,
    NotarialDocumentFamilyMember.__table__,
    NotarialDocumentCluster.__table__,
    NotarialDocumentClusterMember.__table__,
    NotarialEmbeddingVersion.__table__,
    NotarialDocumentEmbedding.__table__,
    NotarialDocumentEvidence.__table__,
    NotarialDocumentDecision.__table__,
]


def build_docx_bytes(title: str = "COMPRAVENTA", apartment: str = "804", include_table: bool = True) -> bytes:
    buffer = BytesIO()
    document = Document()
    document.add_paragraph(f"ESCRITURA DE {title}")
    document.add_paragraph(f"APARTAMENTO: {apartment}")
    if include_table:
        table = document.add_table(rows=1, cols=2)
        table.cell(0, 0).text = "MATRICULA"
        table.cell(0, 1).text = f"001-1528{apartment}"
    document.save(buffer)
    return buffer.getvalue()


class NotarialDocumentIntelligenceTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine, tables=TABLES)
        self.Session = sessionmaker(bind=self.engine)
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = NotarialIntelligenceStorage(local_root=Path(self.tmp.name) / "storage", use_supabase=False)

    def tearDown(self):
        Base.metadata.drop_all(self.engine, tables=TABLES)
        self.engine.dispose()
        self.tmp.cleanup()

    def test_parser_extracts_paragraphs_tables_and_stable_locations(self):
        parsed = NotarialDocumentParser().parse_bytes(build_docx_bytes(), filename="minuta.docx")

        locations = [block.location_key for block in parsed.blocks]
        texts = [block.text for block in parsed.blocks]

        self.assertIn("paragraph:1", locations)
        self.assertIn("paragraph:2", locations)
        self.assertIn("table:1/row:1/cell:1/paragraph:1", locations)
        self.assertIn("table:1/row:1/cell:2/paragraph:1", locations)
        self.assertIn("APARTAMENTO: 804", texts)
        self.assertTrue(parsed.parser_version.startswith("python-docx:"))

    def test_ingestion_stores_private_file_and_reuses_existing_document_by_hash(self):
        db = self.Session()
        try:
            content = build_docx_bytes()
            result = NotarialDocumentIngestionService(db, storage=self.storage).ingest_batch(
                IngestBatchRequest(
                    name="Lote idempotente",
                    documents=[
                        DocumentUpload(filename="minuta-a.docx", content=content),
                        DocumentUpload(filename="minuta-b.docx", content=content),
                    ],
                )
            )

            self.assertEqual(result.total_documents, 2)
            self.assertEqual(result.unique_documents, 1)
            self.assertEqual(result.duplicate_documents, 1)
            self.assertEqual(db.query(NotarialDocument).count(), 1)
            self.assertEqual(db.query(NotarialDocumentBatchItem).count(), 2)
            self.assertGreater(db.query(NotarialDocumentBlock).count(), 0)
            stored_path = Path(result.documents[0].storage_path)
            self.assertTrue(stored_path.exists())
            self.assertTrue(str(stored_path).startswith(str(Path(self.tmp.name) / "storage")))
            self.assertEqual(result.documents[1].status, DocumentProcessingStatus.REUSED)
        finally:
            db.close()

    def test_ingestion_processes_synthetic_batch_equivalent_to_hundreds(self):
        db = self.Session()
        try:
            documents = [
                DocumentUpload(
                    filename=f"minuta-{index:03d}.docx",
                    content=build_docx_bytes(apartment=str(800 + index), include_table=index % 2 == 0),
                    metadata={"synthetic": True, "index": index},
                )
                for index in range(1, 201)
            ]

            result = NotarialDocumentIngestionService(db, storage=self.storage).ingest_batch(
                IngestBatchRequest(name="Lote sintetico 200", source_type="synthetic", documents=documents)
            )

            self.assertEqual(result.total_documents, 200)
            self.assertEqual(result.error_documents, 0)
            self.assertEqual(result.unique_documents, 200)
            self.assertEqual(db.query(NotarialDocument).count(), 200)
            self.assertEqual(db.query(NotarialDocumentBatchItem).count(), 200)
            self.assertGreaterEqual(db.query(NotarialDocumentBlock).count(), 500)
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
