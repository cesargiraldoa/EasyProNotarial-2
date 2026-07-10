from __future__ import annotations

import tempfile
import unittest
import zipfile
from io import BytesIO
from pathlib import Path

from docx import Document
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes.notarial_document_intelligence import get_ingestion_service, router as intelligence_router
from app.core.deps import get_current_user, get_db
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
    BatchStatus,
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

    def test_queue_and_process_batch_is_recoverable_by_batch_id(self):
        db = self.Session()
        try:
            service = NotarialDocumentIngestionService(db, storage=self.storage)
            queued = service.queue_batch(
                IngestBatchRequest(
                    name="Lote async",
                    source_type="api_async",
                    documents=[
                        DocumentUpload(filename="async-1.docx", content=build_docx_bytes(apartment="1201")),
                        DocumentUpload(filename="async-2.docx", content=build_docx_bytes(apartment="1202", include_table=False)),
                    ],
                )
            )

            self.assertEqual(queued.status, BatchStatus.QUEUED)
            self.assertEqual(queued.total_documents, 2)
            self.assertEqual(db.query(NotarialDocumentBlock).count(), 0)

            processed = service.process_queued_batch(queued.batch_id)

            self.assertEqual(processed.status, BatchStatus.COMPLETED)
            self.assertEqual(processed.error_documents, 0)
            self.assertEqual(db.query(NotarialDocumentBlock).count(), 6)
            statuses = [item.status for item in db.query(NotarialDocumentBatchItem).order_by(NotarialDocumentBatchItem.item_index).all()]
            self.assertEqual(statuses, ["processed", "processed"])
        finally:
            db.close()

    def test_http_ingests_docx_and_returns_batch_detail(self):
        client = self._build_api_client()
        response = client.post(
            "/api/v1/notarial-intelligence/batches/ingest",
            data={"name": "Lote HTTP", "source_type": "test"},
            files=[
                (
                    "files",
                    (
                        "minuta-http.docx",
                        build_docx_bytes(apartment="901"),
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    ),
                )
            ],
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["total_documents"], 1)
        self.assertEqual(payload["unique_documents"], 1)
        self.assertEqual(payload["documents"][0]["block_count"], 4)

        detail = client.get(f"/api/v1/notarial-intelligence/batches/{payload['batch_id']}")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()["documents"][0]["filename"], "minuta_http.docx")

    def test_http_ingests_zip_without_persisting_zip(self):
        client = self._build_api_client()
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as archive:
            archive.writestr("lote/minuta-1.docx", build_docx_bytes(apartment="1001"))
            archive.writestr("lote/minuta-2.docx", build_docx_bytes(apartment="1002"))
            archive.writestr("lote/ignorar.txt", b"no docx")

        response = client.post(
            "/api/v1/notarial-intelligence/batches/ingest",
            data={"name": "Lote ZIP", "source_type": "zip"},
            files=[("files", ("lote.zip", zip_buffer.getvalue(), "application/zip"))],
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["total_documents"], 2)
        self.assertEqual(payload["unique_documents"], 2)
        self.assertEqual(payload["error_documents"], 0)
        stored_files = list((Path(self.tmp.name) / "storage").rglob("*"))
        self.assertFalse(any(path.name == "lote.zip" for path in stored_files))

    def test_http_reparse_document_rebuilds_blocks_from_storage(self):
        client = self._build_api_client()
        response = client.post(
            "/api/v1/notarial-intelligence/batches/ingest",
            data={"name": "Lote reparse", "source_type": "test"},
            files=[
                (
                    "files",
                    (
                        "minuta-reparse.docx",
                        build_docx_bytes(apartment="1101"),
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    ),
                )
            ],
        )
        self.assertEqual(response.status_code, 200)
        document = response.json()["documents"][0]
        Path(document["storage_path"]).write_bytes(build_docx_bytes(apartment="2202", include_table=False))

        reparse = client.post(f"/api/v1/notarial-intelligence/documents/{document['document_id']}/reparse")

        self.assertEqual(reparse.status_code, 200)
        self.assertEqual(reparse.json()["block_count"], 2)
        db = self.Session()
        try:
            texts = [
                row.text
                for row in db.query(NotarialDocumentBlock)
                .filter(NotarialDocumentBlock.document_id == document["document_id"])
                .all()
            ]
            self.assertIn("APARTAMENTO: 2202", texts)
            self.assertNotIn("APARTAMENTO: 1101", texts)
        finally:
            db.close()

    def _build_api_client(self) -> TestClient:
        app = FastAPI()
        app.include_router(intelligence_router, prefix="/api/v1")

        def override_get_db():
            session = self.Session()
            try:
                yield session
            finally:
                session.close()

        def override_service():
            session = self.Session()
            try:
                yield NotarialDocumentIngestionService(session, storage=self.storage)
            finally:
                session.close()

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_ingestion_service] = override_service
        app.dependency_overrides[get_current_user] = lambda: object()
        return TestClient(app)


if __name__ == "__main__":
    unittest.main()
