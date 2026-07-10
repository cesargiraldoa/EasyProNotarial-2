from __future__ import annotations

import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.services.minuta.inverse_conversion_catalog.models import (
    CorpusDocument,
    CorpusDocumentField,
    FieldAlias,
    FieldDefinition,
    FieldPattern,
)
from app.services.minuta.inverse_conversion_engine.models import InverseConversionEmbedding
from app.services.minuta.inverse_conversion_engine.semantic_indexer import SemanticIndexer
from app.services.minuta.inverse_conversion_engine.semantic_repository import SemanticRepository


TABLES = [
    FieldDefinition.__table__,
    FieldAlias.__table__,
    CorpusDocument.__table__,
    CorpusDocumentField.__table__,
    FieldPattern.__table__,
    InverseConversionEmbedding.__table__,
]


class SemanticRagTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine, tables=TABLES)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()
        self._seed()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine, tables=TABLES)
        self.engine.dispose()

    def _seed(self):
        self.db.add(FieldDefinition(field_code="NUMERO_MATRICULA", display_name="Numero Matricula", status="suggested", confidence=0.8))
        self.db.add(FieldAlias(raw_field_code="VALOR_DE_LA_VENTA_EN_NUMEROS", canonical_field_code="VALOR_VENTA", frequency=3, status="suggested"))
        doc = CorpusDocument(filename="fixture.docx", source_path="fixture.docx", marker_count=1, processing_status="suggested")
        self.db.add(doc)
        self.db.flush()
        self.db.add(CorpusDocumentField(corpus_document_id=doc.id, raw_field_code="NUMERO_MATRICULA", occurrences=1, status="draft"))
        self.db.add(
            FieldPattern(
                raw_field_code="NUMERO_MATRICULA",
                canonical_field_code="NUMERO_MATRICULA",
                text_before="MATRICULA:",
                text_after="DEL INMUEBLE",
                frequency=1,
                confidence=0.8,
                status="draft",
            )
        )
        self.db.commit()

    def test_dry_run_does_not_write_embeddings(self):
        result = SemanticIndexer(self.db).index_sources(commit=False)
        self.assertGreater(result.prepared, 0)
        self.assertEqual(self.db.query(InverseConversionEmbedding).count(), 0)

    def test_commit_writes_only_embedding_records_with_null_embedding(self):
        result = SemanticIndexer(self.db).index_sources(commit=True, limit=2)
        self.assertEqual(result.committed, True)
        self.assertEqual(self.db.query(InverseConversionEmbedding).count(), 2)
        self.assertTrue(all(row.embedding is None for row in self.db.query(InverseConversionEmbedding).all()))

    def test_semantic_search_degrades_to_lexical_without_embeddings(self):
        SemanticIndexer(self.db).index_sources(commit=True)
        hits = SemanticRepository(self.db).semantic_search("MATRICULA", limit=5)
        self.assertTrue(any(hit.field_code == "NUMERO_MATRICULA" for hit in hits))

    def test_has_embeddings_false_without_provider_vectors(self):
        SemanticIndexer(self.db).index_sources(commit=True)
        self.assertFalse(SemanticRepository(self.db).has_embeddings())


if __name__ == "__main__":
    unittest.main()
