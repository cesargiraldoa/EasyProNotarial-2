from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.notarial_document_intelligence import (
    NotarialDocument,
    NotarialDocumentBlock,
    NotarialDocumentDecision,
    NotarialDocumentEmbedding,
    NotarialDocumentEntity,
    NotarialDocumentEvidence,
    NotarialDocumentParseRun,
)
from app.services.notarial_document_intelligence.classifier import DocumentClassification, NotarialDocumentClassifier
from app.services.notarial_document_intelligence.embedding_provider import EmbeddingProvider, NotarialEmbeddingService
from app.services.notarial_document_intelligence.family_cluster import NotarialFamilyClusterService
from app.services.notarial_document_intelligence.hybrid_rag import NotarialHybridRagService
from app.services.notarial_document_intelligence.llm_provider import IntelligenceMode, LLMProvider, NotarialLLMService


@dataclass
class IntelligenceRunResult:
    document_id: int
    parse_run_id: int
    classification: dict[str, Any]
    embedding: dict[str, int | str]
    family_id: int | None
    cluster_count: int
    fixed_variable_counts: dict[str, int]
    rag_hits: int
    decision_id: int
    llm_mode: str
    llm_error: str | None


class NotarialIntelligenceEngine:
    def __init__(
        self,
        db: Session,
        *,
        embedding_provider: EmbeddingProvider | None = None,
        llm_provider: LLMProvider | None = None,
    ) -> None:
        self.db = db
        self.classifier = NotarialDocumentClassifier()
        self.embedding_service = NotarialEmbeddingService(db, provider=embedding_provider)
        self.family_cluster = NotarialFamilyClusterService(db)
        self.rag = NotarialHybridRagService(db, embedding_provider=embedding_provider)
        self.llm = NotarialLLMService(provider=llm_provider)

    def run_document(self, notary_id: int, document_id: int, *, llm_mode: IntelligenceMode = IntelligenceMode.OFF) -> IntelligenceRunResult:
        document = self._document(notary_id, document_id)
        parse_run = self._active_parse_run(notary_id, document_id)
        blocks = self._active_blocks(notary_id, document_id, parse_run.id)
        classification = self.classifier.classify(blocks)
        self._persist_classification(document, parse_run, classification)
        embedding_result = self.embedding_service.reindex_document(notary_id, document_id, parse_run.id)
        family = self.family_cluster.assign_family(document, classification)
        clusters = self.family_cluster.update_duplicate_clusters(notary_id, document)
        fixed_variable_counts = self.family_cluster.classify_fixed_variable_blocks(notary_id, family.id)
        rag_hits = self.rag.search(
            notary_id,
            _rag_query(classification),
            document_type=classification.document_type,
            limit=8,
        )
        self.rag.persist_hits(notary_id, parse_run.id, rag_hits)
        llm_result = self.llm.analyze(_llm_payload(document, parse_run, classification, blocks, rag_hits), llm_mode)
        decision = self._persist_decision(document, parse_run, classification, fixed_variable_counts, rag_hits, llm_result)
        document.metadata_json = _merge_json(
            document.metadata_json,
            {
                "intelligence": {
                    "last_run_at": _now().isoformat(),
                    "decision_id": decision.id,
                    "embedding": embedding_result,
                    "fixed_variable_counts": fixed_variable_counts,
                    "llm_audit": asdict(llm_result.audit),
                }
            },
        )
        self.db.commit()
        return IntelligenceRunResult(
            document_id=document.id,
            parse_run_id=parse_run.id,
            classification=_classification_payload(classification),
            embedding=embedding_result,
            family_id=family.id,
            cluster_count=len(clusters),
            fixed_variable_counts=fixed_variable_counts,
            rag_hits=len(rag_hits),
            decision_id=decision.id,
            llm_mode=llm_mode.value,
            llm_error=llm_result.audit.error,
        )

    def reindex_notary(self, notary_id: int) -> dict[str, Any]:
        documents = self.db.query(NotarialDocument).filter(NotarialDocument.notary_id == notary_id).order_by(NotarialDocument.id.asc()).all()
        results = [self.embedding_service.reindex_document(notary_id, document.id) for document in documents]
        self.db.commit()
        return {
            "notary_id": notary_id,
            "documents": len(results),
            "indexed": sum(int(item["indexed"]) for item in results),
            "skipped": sum(int(item["skipped"]) for item in results),
            "version_key": self.embedding_service.version_key(),
        }

    def benchmark_notary(self, notary_id: int) -> dict[str, Any]:
        documents = self.db.query(NotarialDocument).filter(NotarialDocument.notary_id == notary_id).all()
        families = {document.family_id for document in documents if document.family_id is not None}
        decisions = self.db.query(NotarialDocumentDecision).filter(NotarialDocumentDecision.notary_id == notary_id).count()
        embeddings = self.db.query(NotarialDocumentEmbedding).filter(NotarialDocumentEmbedding.notary_id == notary_id).count()
        return {
            "notary_id": notary_id,
            "documents": len(documents),
            "families": len(families),
            "decisions": decisions,
            "existing_embeddings": embeddings,
            "coverage": {
                "classified_documents": sum(1 for document in documents if document.document_type),
                "family_assigned": sum(1 for document in documents if document.family_id is not None),
            },
        }

    def _persist_classification(self, document: NotarialDocument, parse_run: NotarialDocumentParseRun, classification: DocumentClassification) -> None:
        document.document_type = classification.document_type
        document.document_subtype = classification.document_subtype
        document.notary_name = classification.notary_name
        document.project_name = classification.project_name
        document.bank_name = classification.bank_name
        document.metadata_json = _merge_json(document.metadata_json, {"classification": _classification_payload(classification)})
        for entity in classification.entities:
            existing = (
                self.db.query(NotarialDocumentEntity)
                .filter(
                    NotarialDocumentEntity.notary_id == document.notary_id,
                    NotarialDocumentEntity.document_id == document.id,
                    NotarialDocumentEntity.parse_run_id == parse_run.id,
                    NotarialDocumentEntity.block_id == entity.block_id,
                    NotarialDocumentEntity.entity_type == entity.entity_type,
                    NotarialDocumentEntity.text == entity.text,
                )
                .first()
            )
            if existing is None:
                self.db.add(
                    NotarialDocumentEntity(
                        notary_id=document.notary_id,
                        document_id=document.id,
                        parse_run_id=parse_run.id,
                        block_id=entity.block_id,
                        entity_type=entity.entity_type,
                        canonical_field_code=entity.canonical_field_code,
                        text=entity.text,
                        normalized_text=entity.normalized_text,
                        role=entity.role,
                        confidence=entity.confidence,
                        source="deterministic",
                        requires_human_review=entity.confidence < 0.95,
                        metadata_json=json.dumps({"classifier": "deterministic-v1"}, ensure_ascii=False, sort_keys=True),
                    )
                )
        self.db.add(
            NotarialDocumentEvidence(
                notary_id=document.notary_id,
                document_id=document.id,
                parse_run_id=parse_run.id,
                evidence_type="document_classification",
                source="deterministic",
                score=classification.confidence,
                payload_json=json.dumps(_classification_payload(classification), ensure_ascii=False, sort_keys=True),
            )
        )

    def _persist_decision(
        self,
        document: NotarialDocument,
        parse_run: NotarialDocumentParseRun,
        classification: DocumentClassification,
        fixed_variable_counts: dict[str, int],
        rag_hits,
        llm_result,
    ) -> NotarialDocumentDecision:
        deterministic = {
            "classification": _classification_payload(classification),
            "fixed_variable_counts": fixed_variable_counts,
            "rag_hit_count": len(rag_hits),
        }
        llm_json = llm_result.raw_json if llm_result.decision is not None else {"audit": asdict(llm_result.audit)}
        hybrid = _hybrid_decision(deterministic, llm_result)
        decision = NotarialDocumentDecision(
            notary_id=document.notary_id,
            document_id=document.id,
            parse_run_id=parse_run.id,
            decision_type="hybrid_document_intelligence",
            deterministic_decision_json=json.dumps(deterministic, ensure_ascii=False, sort_keys=True),
            llm_decision_json=json.dumps(llm_json, ensure_ascii=False, sort_keys=True),
            hybrid_decision_json=json.dumps(hybrid, ensure_ascii=False, sort_keys=True),
            human_decision_json="{}",
            status="pending",
            metadata_json=json.dumps({"llm_audit": asdict(llm_result.audit)}, ensure_ascii=False, sort_keys=True),
        )
        self.db.add(decision)
        self.db.flush()
        return decision

    def _document(self, notary_id: int, document_id: int) -> NotarialDocument:
        document = self.db.get(NotarialDocument, document_id)
        if document is None or document.notary_id != notary_id:
            raise ValueError(f"Document {document_id} not found.")
        return document

    def _active_parse_run(self, notary_id: int, document_id: int) -> NotarialDocumentParseRun:
        parse_run = (
            self.db.query(NotarialDocumentParseRun)
            .filter(
                NotarialDocumentParseRun.notary_id == notary_id,
                NotarialDocumentParseRun.document_id == document_id,
                NotarialDocumentParseRun.is_active.is_(True),
                NotarialDocumentParseRun.status == "completed",
            )
            .first()
        )
        if parse_run is None:
            raise ValueError(f"Document {document_id} does not have an active completed parse run.")
        return parse_run

    def _active_blocks(self, notary_id: int, document_id: int, parse_run_id: int) -> list[NotarialDocumentBlock]:
        return (
            self.db.query(NotarialDocumentBlock)
            .filter(
                NotarialDocumentBlock.notary_id == notary_id,
                NotarialDocumentBlock.document_id == document_id,
                NotarialDocumentBlock.parse_run_id == parse_run_id,
            )
            .order_by(NotarialDocumentBlock.block_index.asc())
            .all()
        )


def _hybrid_decision(deterministic: dict, llm_result) -> dict:
    llm_decision = llm_result.decision.model_dump(mode="json") if llm_result.decision is not None else None
    conflicts = []
    if llm_decision and llm_decision.get("document_type") and llm_decision["document_type"] != deterministic["classification"]["document_type"]:
        conflicts.append("document_type_conflict")
    return {
        "selected": deterministic,
        "llm": llm_decision,
        "confidence": deterministic["classification"]["confidence"],
        "conflicts": conflicts,
        "requires_human_review": bool(conflicts) or deterministic["classification"]["confidence"] < 0.9,
    }


def _classification_payload(classification: DocumentClassification) -> dict[str, Any]:
    return {
        "document_type": classification.document_type,
        "document_subtype": classification.document_subtype,
        "acts": classification.acts,
        "notary_name": classification.notary_name,
        "project_name": classification.project_name,
        "bank_name": classification.bank_name,
        "roles": classification.roles,
        "confidence": classification.confidence,
        "evidence": classification.evidence,
    }


def _rag_query(classification: DocumentClassification) -> str:
    return " ".join([classification.document_type, classification.document_subtype or "", *classification.acts, *(classification.roles or [])]).strip()


def _llm_payload(document: NotarialDocument, parse_run: NotarialDocumentParseRun, classification: DocumentClassification, blocks, rag_hits) -> dict:
    return {
        "document": {
            "id": document.id,
            "filename": document.filename,
            "parse_run_id": parse_run.id,
            "classification": _classification_payload(classification),
        },
        "evidence": [
            {"block_id": block.id, "location_key": block.location_key, "text": (block.text or "")[:800]}
            for block in blocks[:40]
        ],
        "rag": [
            {"block_id": hit.block_id, "location_key": hit.location_key, "score": hit.score, "text": hit.text[:500]}
            for hit in rag_hits
        ],
    }


def _merge_json(raw: str | None, patch: dict) -> str:
    try:
        payload = json.loads(raw or "{}")
    except json.JSONDecodeError:
        payload = {}
    payload.update(patch)
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _now() -> datetime:
    return datetime.now(timezone.utc)
