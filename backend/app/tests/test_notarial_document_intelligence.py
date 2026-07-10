from __future__ import annotations

import importlib.util
import tempfile
import threading
import unittest
import zipfile
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

from docx import Document
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes import notarial_document_intelligence as route_module
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
    NotarialDocumentParseRun,
    NotarialDocumentSection,
    NotarialEmbeddingVersion,
)
from app.models.notary import Notary
from app.services.notarial_document_intelligence.contracts import (
    ParsedDocument,
    BatchStatus,
    DocumentProcessingStatus,
    DocumentUpload,
    IngestBatchRequest,
)
from app.services.notarial_document_intelligence.ingestion import NotarialDocumentIngestionService, TransientDocumentProcessingError
from app.services.notarial_document_intelligence.parser import NotarialDocumentParser
from app.services.notarial_document_intelligence.storage import NotarialIntelligenceStorage
from app.services.notarial_document_intelligence.vector_store import NotarialVectorStore


TABLES = [
    Notary.__table__,
    NotarialDocumentBatch.__table__,
    NotarialDocumentFamily.__table__,
    NotarialDocument.__table__,
    NotarialDocumentBatchItem.__table__,
    NotarialDocumentParseRun.__table__,
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
        self.notary_id = 1
        self._seed_notaries()

    def tearDown(self):
        Base.metadata.drop_all(self.engine, tables=TABLES)
        self.engine.dispose()
        self.tmp.cleanup()

    def _seed_notaries(self):
        db = self.Session()
        try:
            db.add_all(
                [
                    _notary(1, "notaria-uno"),
                    _notary(2, "notaria-dos"),
                ]
            )
            db.commit()
        finally:
            db.close()

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

    @unittest.skipUnless(importlib.util.find_spec("unstructured"), "unstructured no esta instalado en el entorno local")
    def test_parser_reconciles_unstructured_semantics_when_available(self):
        parsed = NotarialDocumentParser().parse_bytes(build_docx_bytes(title="COMPRAVENTA INMUEBLE"), filename="minuta.docx")

        self.assertTrue(parsed.metadata["unstructured"]["enabled"])
        self.assertGreater(parsed.metadata["unstructured"]["reconciled_blocks"], 0)
        self.assertTrue(any(block.parser_source == "python-docx+unstructured" for block in parsed.blocks))

    def test_ingestion_stores_private_file_and_reuses_existing_document_by_hash(self):
        db = self.Session()
        try:
            content = build_docx_bytes()
            result = NotarialDocumentIngestionService(db, notary_id=1, storage=self.storage).ingest_batch(
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

            result = NotarialDocumentIngestionService(db, notary_id=1, storage=self.storage).ingest_batch(
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
            service = NotarialDocumentIngestionService(db, notary_id=1, storage=self.storage)
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

    def test_same_hash_is_deduplicated_per_notary_without_cross_tenant_leak(self):
        content = build_docx_bytes(apartment="1301")
        db = self.Session()
        try:
            first = NotarialDocumentIngestionService(db, notary_id=1, storage=self.storage).ingest_batch(
                IngestBatchRequest(name="Notaria 1", documents=[DocumentUpload(filename="mismo.docx", content=content)])
            )
            second = NotarialDocumentIngestionService(db, notary_id=2, storage=self.storage).ingest_batch(
                IngestBatchRequest(name="Notaria 2", documents=[DocumentUpload(filename="mismo.docx", content=content)])
            )

            self.assertEqual(first.unique_documents, 1)
            self.assertEqual(second.unique_documents, 1)
            self.assertEqual(db.query(NotarialDocument).count(), 2)
            self.assertNotEqual(first.documents[0].document_id, second.documents[0].document_id)
            self.assertIn("notary_1", first.documents[0].storage_path)
            self.assertIn("notary_2", second.documents[0].storage_path)
        finally:
            db.close()

    def test_vector_store_filters_by_notary_and_orders_by_distance_in_sqlite_fallback(self):
        db = self.Session()
        try:
            version = NotarialEmbeddingVersion(version_key="test-3d", provider="test", model_name="mini", dimensions=3)
            db.add(version)
            db.flush()
            store = NotarialVectorStore(db, dimensions=3)
            db.add_all(
                [
                    NotarialDocumentEmbedding(
                        notary_id=1,
                        embedding_version_id=version.id,
                        source_type="block",
                        source_id=1,
                        content_hash="a" * 64,
                        embedding_dimensions=3,
                        embedding=store.encode_vector([1.0, 0.0, 0.0]),
                    ),
                    NotarialDocumentEmbedding(
                        notary_id=1,
                        embedding_version_id=version.id,
                        source_type="block",
                        source_id=2,
                        content_hash="b" * 64,
                        embedding_dimensions=3,
                        embedding=store.encode_vector([0.0, 1.0, 0.0]),
                    ),
                    NotarialDocumentEmbedding(
                        notary_id=2,
                        embedding_version_id=version.id,
                        source_type="block",
                        source_id=3,
                        content_hash="c" * 64,
                        embedding_dimensions=3,
                        embedding=store.encode_vector([1.0, 0.0, 0.0]),
                    ),
                ]
            )
            db.commit()

            results = store.search(1, [0.9, 0.1, 0.0], embedding_version_id=version.id, limit=10)

            self.assertEqual([item.source_id for item in results], [1, 2])
            self.assertTrue(results[0].distance < results[1].distance)
        finally:
            db.close()

    def test_vector_store_rejects_incompatible_dimensions(self):
        db = self.Session()
        try:
            store = NotarialVectorStore(db, dimensions=3)
            with self.assertRaises(ValueError):
                store.encode_vector([1.0, 0.0])
        finally:
            db.close()

    def test_reparse_keeps_previous_parse_run_and_switches_active_on_success(self):
        db = self.Session()
        try:
            service = NotarialDocumentIngestionService(db, notary_id=1, storage=self.storage)
            result = service.ingest_batch(
                IngestBatchRequest(name="Versionado", documents=[DocumentUpload(filename="version.docx", content=build_docx_bytes(apartment="1401"))])
            )
            document_id = result.documents[0].document_id
            Path(result.documents[0].storage_path).write_bytes(build_docx_bytes(apartment="1402", include_table=False))

            reparsed = service.reparse_document(document_id)

            self.assertEqual(reparsed.block_count, 2)
            runs = db.query(NotarialDocumentParseRun).filter(NotarialDocumentParseRun.document_id == document_id).order_by(NotarialDocumentParseRun.parse_version).all()
            self.assertEqual([run.parse_version for run in runs], [1, 2])
            self.assertEqual([run.is_active for run in runs], [False, True])
            self.assertEqual(db.query(NotarialDocumentBlock).filter(NotarialDocumentBlock.document_id == document_id).count(), 6)
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

    def test_http_async_ingest_returns_accepted_batch_contract(self):
        original_task = route_module.process_queued_document_batch_task

        class FakeTask:
            @staticmethod
            def delay(batch_id: int, notary_id: int):
                return type("FakeAsyncResult", (), {"id": f"task-{batch_id}-{notary_id}"})()

        route_module.process_queued_document_batch_task = FakeTask()
        self.addCleanup(lambda: setattr(route_module, "process_queued_document_batch_task", original_task))
        client = self._build_api_client()

        response = client.post(
            "/api/v1/notarial-intelligence/batches/ingest",
            data={"name": "Lote async HTTP", "source_type": "test", "async_processing": "true"},
            files=[("files", ("async-http.docx", build_docx_bytes(apartment="1901"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))],
        )

        self.assertEqual(response.status_code, 202)
        payload = response.json()
        self.assertEqual(payload["status"], "queued")
        self.assertEqual(payload["task_id"], f"task-{payload['batch_id']}-1")
        self.assertIn(f"/notarial-intelligence/batches/{payload['batch_id']}", payload["status_url"])
        detail = client.get(f"/api/v1/notarial-intelligence/batches/{payload['batch_id']}")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()["metadata"]["celery"]["task_id"], payload["task_id"])

    def test_http_async_ingest_marks_publication_failed_when_celery_publish_fails(self):
        original_task = route_module.process_queued_document_batch_task

        class FailingTask:
            @staticmethod
            def delay(batch_id: int, notary_id: int):
                raise ConnectionError("broker offline")

        route_module.process_queued_document_batch_task = FailingTask()
        self.addCleanup(lambda: setattr(route_module, "process_queued_document_batch_task", original_task))
        client = self._build_api_client()

        response = client.post(
            "/api/v1/notarial-intelligence/batches/ingest",
            data={"name": "Lote async fallido", "source_type": "test", "async_processing": "true"},
            files=[("files", ("async-fail.docx", build_docx_bytes(apartment="1902"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))],
        )

        self.assertEqual(response.status_code, 503)
        db = self.Session()
        try:
            batch = db.query(NotarialDocumentBatch).one()
            self.assertEqual(batch.status, BatchStatus.PUBLICATION_FAILED.value)
            self.assertIn("publication_failed", batch.error_message)
        finally:
            db.close()

    def test_http_ingests_zip_without_persisting_zip(self):
        client = self._build_api_client()
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as archive:
            archive.writestr("lote/minuta-1.docx", build_docx_bytes(apartment="1001"))
            archive.writestr("lote/minuta-2.docx", build_docx_bytes(apartment="1002"))

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

    def test_http_rejects_unsupported_zip_entry(self):
        client = self._build_api_client()
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as archive:
            archive.writestr("lote/minuta.docx", build_docx_bytes(apartment="1003"))
            archive.writestr("lote/ignorar.txt", b"no docx")

        response = client.post(
            "/api/v1/notarial-intelligence/batches/ingest",
            data={"name": "Lote ZIP inseguro", "source_type": "zip"},
            files=[("files", ("lote.zip", zip_buffer.getvalue(), "application/zip"))],
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("Entrada no soportada", response.json()["detail"])

    def test_http_rejects_unsafe_zip_path(self):
        client = self._build_api_client()
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as archive:
            archive.writestr("../minuta.docx", build_docx_bytes(apartment="1004"))

        response = client.post(
            "/api/v1/notarial-intelligence/batches/ingest",
            data={"name": "Lote ZIP ruta insegura", "source_type": "zip"},
            files=[("files", ("lote.zip", zip_buffer.getvalue(), "application/zip"))],
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("Ruta insegura", response.json()["detail"])

    def test_http_rejects_zip_bomb_ratio(self):
        client = self._build_api_client()
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("lote/minuta.docx", b"0" * 1024 * 1024)

        response = client.post(
            "/api/v1/notarial-intelligence/batches/ingest",
            data={"name": "Lote ZIP bomb", "source_type": "zip"},
            files=[("files", ("lote.zip", zip_buffer.getvalue(), "application/zip"))],
        )

        self.assertEqual(response.status_code, 413)
        self.assertIn("ZIP bomb", response.json()["detail"])

    def test_http_rejects_invalid_docx(self):
        client = self._build_api_client()
        response = client.post(
            "/api/v1/notarial-intelligence/batches/ingest",
            data={"name": "DOCX invalido", "source_type": "test"},
            files=[("files", ("minuta.docx", b"no es docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))],
        )

        self.assertEqual(response.status_code, 422)
        self.assertIn("DOCX invalido", response.json()["detail"])

    def test_http_reparse_document_returns_accepted_and_worker_rebuilds_blocks_from_storage(self):
        original_task = route_module.reparse_document_task

        class FakeTask:
            @staticmethod
            def delay(document_id: int, notary_id: int, parse_run_id: int):
                return type("FakeAsyncResult", (), {"id": f"reparse-{document_id}-{parse_run_id}"})()

        route_module.reparse_document_task = FakeTask()
        self.addCleanup(lambda: setattr(route_module, "reparse_document_task", original_task))
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

        self.assertEqual(reparse.status_code, 202)
        accepted = reparse.json()
        self.assertEqual(accepted["status"], "queued")
        self.assertEqual(accepted["task_id"], f"reparse-{document['document_id']}-{accepted['parse_run_id']}")
        db = self.Session()
        try:
            service = NotarialDocumentIngestionService(db, notary_id=1, storage=self.storage)
            result = service.reparse_document(document["document_id"], parse_run_id=accepted["parse_run_id"])
            self.assertEqual(result.block_count, 2)
            texts = [
                row.text
                for row in db.query(NotarialDocumentBlock)
                .join(NotarialDocumentParseRun, NotarialDocumentParseRun.id == NotarialDocumentBlock.parse_run_id)
                .filter(
                    NotarialDocumentBlock.document_id == document["document_id"],
                    NotarialDocumentParseRun.is_active.is_(True),
                )
                .all()
            ]
            self.assertIn("APARTAMENTO: 2202", texts)
            self.assertNotIn("APARTAMENTO: 1101", texts)
        finally:
            db.close()

    def test_http_reparse_requires_role_permission(self):
        client = self._build_api_client(role_code="client")
        response = client.post(
            "/api/v1/notarial-intelligence/batches/ingest",
            data={"name": "Sin permiso", "source_type": "test"},
            files=[("files", ("sin-permiso.docx", build_docx_bytes(apartment="1701"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))],
        )

        self.assertEqual(response.status_code, 403)

    def test_http_requires_permission_in_active_notary_scope(self):
        client = self._build_api_client(notary_id=1, role_code="protocolist", assignment_notary_id=2)
        response = client.post(
            "/api/v1/notarial-intelligence/batches/ingest",
            data={"name": "Rol en otra notaria", "source_type": "test"},
            files=[("files", ("otra-notaria.docx", build_docx_bytes(apartment="1702"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))],
        )

        self.assertEqual(response.status_code, 403)

    def test_http_blocks_cross_notary_batch_and_reparse_access(self):
        client_1 = self._build_api_client(notary_id=1)
        response = client_1.post(
            "/api/v1/notarial-intelligence/batches/ingest",
            data={"name": "Privado", "source_type": "test"},
            files=[("files", ("privado.docx", build_docx_bytes(apartment="1501"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))],
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()

        client_2 = self._build_api_client(notary_id=2)
        detail = client_2.get(f"/api/v1/notarial-intelligence/batches/{payload['batch_id']}")
        reparse = client_2.post(f"/api/v1/notarial-intelligence/documents/{payload['documents'][0]['document_id']}/reparse")

        self.assertEqual(detail.status_code, 404)
        self.assertEqual(reparse.status_code, 404)

    def test_failed_parse_run_from_worker_is_persisted_after_batch_rollback(self):
        class FailingParser(NotarialDocumentParser):
            def parse_bytes(self, content: bytes, filename: str) -> ParsedDocument:
                raise ValueError("documento deterministico invalido")

        db = self.Session()
        try:
            service = NotarialDocumentIngestionService(db, notary_id=1, storage=self.storage)
            queued = service.queue_batch(
                IngestBatchRequest(name="Fallo worker", documents=[DocumentUpload(filename="fallo.docx", content=build_docx_bytes(apartment="1801"))])
            )
            failing_service = NotarialDocumentIngestionService(db, notary_id=1, storage=self.storage, parser=FailingParser())
            result = failing_service.process_queued_batch(queued.batch_id)

            self.assertEqual(result.status, BatchStatus.ERROR)
            run = db.query(NotarialDocumentParseRun).one()
            self.assertEqual(run.status, "error")
            self.assertIn("documento deterministico invalido", run.error_message)
        finally:
            db.close()

    def test_transient_parse_error_is_persisted_and_bubbles_for_celery_retry(self):
        class TransientParser(NotarialDocumentParser):
            def parse_bytes(self, content: bytes, filename: str) -> ParsedDocument:
                raise TimeoutError("storage temporalmente no disponible")

        db = self.Session()
        try:
            service = NotarialDocumentIngestionService(db, notary_id=1, storage=self.storage)
            queued = service.queue_batch(
                IngestBatchRequest(name="Retry worker", documents=[DocumentUpload(filename="retry.docx", content=build_docx_bytes(apartment="1802"))])
            )
            retrying_service = NotarialDocumentIngestionService(db, notary_id=1, storage=self.storage, parser=TransientParser())

            with self.assertRaises(TransientDocumentProcessingError):
                retrying_service.process_queued_batch(queued.batch_id)

            item = db.query(NotarialDocumentBatchItem).one()
            run = db.query(NotarialDocumentParseRun).one()
            batch = db.query(NotarialDocumentBatch).one()
            self.assertEqual(item.status, "queued")
            self.assertEqual(run.status, "error")
            self.assertIn("storage temporalmente no disponible", run.error_message)
            self.assertEqual(batch.status, BatchStatus.RUNNING.value)
            self.assertIsNone(batch.finished_at)
        finally:
            db.close()

    def test_http_reparse_publish_failure_persists_failed_parse_run(self):
        original_task = route_module.reparse_document_task

        class FailingTask:
            @staticmethod
            def delay(document_id: int, notary_id: int, parse_run_id: int):
                raise ConnectionError("broker offline")

        route_module.reparse_document_task = FailingTask()
        self.addCleanup(lambda: setattr(route_module, "reparse_document_task", original_task))
        client = self._build_api_client()
        response = client.post(
            "/api/v1/notarial-intelligence/batches/ingest",
            data={"name": "Reparse publish fail", "source_type": "test"},
            files=[("files", ("publish-fail.docx", build_docx_bytes(apartment="1850"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))],
        )
        self.assertEqual(response.status_code, 200)
        document_id = response.json()["documents"][0]["document_id"]

        reparse = client.post(f"/api/v1/notarial-intelligence/documents/{document_id}/reparse")

        self.assertEqual(reparse.status_code, 503)
        db = self.Session()
        try:
            failed_run = db.query(NotarialDocumentParseRun).order_by(NotarialDocumentParseRun.parse_version.desc()).first()
            self.assertEqual(failed_run.status, "error")
            self.assertIn("publication_failed", failed_run.error_message)
        finally:
            db.close()

    def test_concurrent_reparse_queue_assigns_unique_parse_versions(self):
        content = build_docx_bytes(apartment="1651")
        db_path = Path(self.tmp.name) / "parse-version-concurrency.db"
        engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False, "timeout": 30},
        )
        Base.metadata.create_all(engine, tables=TABLES)
        Session = sessionmaker(bind=engine)
        seed = Session()
        try:
            seed.add(_notary(1, "notaria-versiones"))
            result = NotarialDocumentIngestionService(seed, notary_id=1, storage=self.storage).ingest_batch(
                IngestBatchRequest(name="Base", documents=[DocumentUpload(filename="base.docx", content=content)])
            )
            document_id = result.documents[0].document_id
        finally:
            seed.close()

        barrier = threading.Barrier(2)
        errors: list[BaseException] = []

        def queue_reparse() -> None:
            session = Session()
            try:
                barrier.wait(timeout=5)
                NotarialDocumentIngestionService(session, notary_id=1, storage=self.storage).queue_reparse_document(document_id)
            except BaseException as exc:
                errors.append(exc)
            finally:
                session.close()

        threads = [threading.Thread(target=queue_reparse) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)

        self.assertEqual(errors, [])
        db = Session()
        try:
            versions = [
                row.parse_version
                for row in db.query(NotarialDocumentParseRun)
                .filter(NotarialDocumentParseRun.document_id == document_id)
                .order_by(NotarialDocumentParseRun.parse_version)
                .all()
            ]
            self.assertEqual(versions, [1, 2, 3])
        finally:
            db.close()
            engine.dispose()

    def test_http_rejects_zip_global_uncompressed_limit_across_multiple_zip_files(self):
        original_limit = route_module.MAX_ZIP_UNCOMPRESSED_BYTES
        docx_bytes = build_docx_bytes(apartment="2001")
        route_module.MAX_ZIP_UNCOMPRESSED_BYTES = len(docx_bytes) + 1
        self.addCleanup(lambda: setattr(route_module, "MAX_ZIP_UNCOMPRESSED_BYTES", original_limit))
        client = self._build_api_client()
        files = []
        for index in range(2):
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as archive:
                archive.writestr(f"lote/minuta-{index}.docx", docx_bytes)
            files.append(("files", (f"lote-{index}.zip", zip_buffer.getvalue(), "application/zip")))

        response = client.post(
            "/api/v1/notarial-intelligence/batches/ingest",
            data={"name": "Lote ZIP global", "source_type": "zip"},
            files=files,
        )

        self.assertEqual(response.status_code, 413)
        self.assertIn("limite global", response.json()["detail"])

    def test_http_rejects_zip_entry_larger_than_single_file_limit(self):
        original_file_limit = route_module.MAX_FILE_BYTES
        original_ratio = route_module.MAX_ZIP_COMPRESSION_RATIO
        route_module.MAX_FILE_BYTES = 250
        route_module.MAX_ZIP_COMPRESSION_RATIO = 10_000
        self.addCleanup(lambda: setattr(route_module, "MAX_FILE_BYTES", original_file_limit))
        self.addCleanup(lambda: setattr(route_module, "MAX_ZIP_COMPRESSION_RATIO", original_ratio))
        client = self._build_api_client()
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("lote/grande.docx", b"0" * 300)

        response = client.post(
            "/api/v1/notarial-intelligence/batches/ingest",
            data={"name": "Entrada grande", "source_type": "zip"},
            files=[("files", ("entrada-grande.zip", zip_buffer.getvalue(), "application/zip"))],
        )

        self.assertEqual(response.status_code, 413)
        self.assertIn("Entrada DOCX demasiado grande", response.json()["detail"])

    def test_postgresql_vector_search_uses_cosine_operator(self):
        captured = {}

        class FakeDialect:
            name = "postgresql"

        class FakeBind:
            dialect = FakeDialect()

        class FakeResult:
            def all(self):
                return [SimpleNamespace(id=1, source_type="block", source_id=7, distance=0.125)]

        class FakeSession:
            bind = FakeBind()

            def execute(self, statement, params):
                captured["sql"] = str(statement)
                captured["params"] = params
                return FakeResult()

        results = NotarialVectorStore(FakeSession(), dimensions=3).search(
            1,
            [1.0, 0.0, 0.0],
            embedding_version_id=9,
            limit=5,
        )

        self.assertEqual(results[0].distance, 0.125)
        self.assertIn("<=>", captured["sql"])
        self.assertNotIn("<->", captured["sql"])

    def test_concurrent_same_hash_creates_one_document_and_two_batch_items(self):
        content = build_docx_bytes(apartment="1601")
        db_path = Path(self.tmp.name) / "concurrency.db"
        engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False, "timeout": 30},
        )
        Base.metadata.create_all(engine, tables=TABLES)
        Session = sessionmaker(bind=engine)
        seed = Session()
        try:
            seed.add_all([_notary(1, "notaria-uno-concurrente"), _notary(2, "notaria-dos-concurrente")])
            seed.commit()
        finally:
            seed.close()

        barrier = threading.Barrier(2)
        errors: list[BaseException] = []

        def ingest_one(name: str) -> None:
            session = Session()
            try:
                barrier.wait(timeout=5)
                NotarialDocumentIngestionService(session, notary_id=1, storage=self.storage).queue_batch(
                    IngestBatchRequest(name=name, documents=[DocumentUpload(filename=f"{name}.docx", content=content)])
                )
            except BaseException as exc:
                errors.append(exc)
            finally:
                session.close()

        threads = [threading.Thread(target=ingest_one, args=(f"concurrente-{index}",)) for index in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)

        self.assertEqual(errors, [])
        self.assertFalse(any(thread.is_alive() for thread in threads))
        db = Session()
        try:
            self.assertEqual(db.query(NotarialDocument).filter(NotarialDocument.notary_id == 1).count(), 1)
            self.assertEqual(db.query(NotarialDocumentBatchItem).filter(NotarialDocumentBatchItem.notary_id == 1).count(), 2)
        finally:
            db.close()
            engine.dispose()

    def _build_api_client(self, notary_id: int | None = None, role_code: str = "protocolist", assignment_notary_id: int | None = None) -> TestClient:
        active_notary_id = notary_id or self.notary_id
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
                yield NotarialDocumentIngestionService(session, notary_id=active_notary_id, storage=self.storage)
            finally:
                session.close()

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_ingestion_service] = override_service
        app.dependency_overrides[get_current_user] = lambda: _user(active_notary_id, role_code, assignment_notary_id)
        client = TestClient(app)
        self.addCleanup(client.close)
        return client


def _user(notary_id: int, role_code: str = "protocolist", assignment_notary_id: int | None = None):
    role = SimpleNamespace(code=role_code)
    assignment = SimpleNamespace(role=role, notary_id=assignment_notary_id if assignment_notary_id is not None else notary_id)
    return type("UserStub", (), {"default_notary_id": notary_id, "role_assignments": [assignment]})()


def _notary(notary_id: int, slug: str) -> Notary:
    return Notary(
        id=notary_id,
        slug=slug,
        catalog_identity_key=f"{slug}-identity",
        commercial_name=slug,
        legal_name=slug,
        municipality="Medellin",
        notary_label=slug,
        city="Medellin",
    )


if __name__ == "__main__":
    unittest.main()
