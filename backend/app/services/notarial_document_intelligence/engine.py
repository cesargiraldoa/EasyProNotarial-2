from __future__ import annotations

import json
import hashlib
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.models.notarial_document_intelligence import (
    NotarialBenchmarkRun,
    NotarialBlockAlignment,
    NotarialDocument,
    NotarialDocumentBlock,
    NotarialDocumentDecision,
    NotarialDocumentEmbedding,
    NotarialDocumentEntity,
    NotarialDocumentEvidence,
    NotarialIntelligenceRun,
    NotarialDocumentParseRun,
)
from app.models.template_field import TemplateField
from app.services.minuta.inverse_conversion_catalog.models import FieldDefinition
from app.services.notarial_document_intelligence.classifier import CLASSIFIER_VERSION, DocumentClassification, NotarialDocumentClassifier
from app.services.notarial_document_intelligence.embedding_provider import EmbeddingProvider, NotarialEmbeddingService
from app.services.notarial_document_intelligence.family_cluster import NotarialFamilyClusterService
from app.services.notarial_document_intelligence.hybrid_rag import NotarialHybridRagService
from app.services.notarial_document_intelligence.llm_provider import IntelligenceMode, LLMProvider, NotarialLLMService


@dataclass
class IntelligenceRunResult:
    run_id: int | None
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
        self.classifier = NotarialDocumentClassifier(db)
        self.embedding_service = NotarialEmbeddingService(db, provider=embedding_provider)
        self.family_cluster = NotarialFamilyClusterService(db)
        self.rag = NotarialHybridRagService(db, embedding_provider=embedding_provider)
        self.llm = NotarialLLMService(provider=llm_provider)

    def create_document_run(self, notary_id: int, document_id: int, *, llm_mode: IntelligenceMode = IntelligenceMode.OFF) -> NotarialIntelligenceRun:
        document = self._document(notary_id, document_id)
        parse_run = self._active_parse_run(notary_id, document_id)
        embedding_version_key = self.embedding_service.version_key()
        run_key = _run_key(
            "document",
            notary_id,
            document_id,
            parse_run.id,
            CLASSIFIER_VERSION,
            embedding_version_key,
            self.llm.provider.provider_name,
            self.llm.provider.model_name,
            self.llm.provider.prompt_version,
            llm_mode.value,
        )
        run = self.db.query(NotarialIntelligenceRun).filter(NotarialIntelligenceRun.run_key == run_key, NotarialIntelligenceRun.notary_id == notary_id).first()
        if run is not None:
            return run
        run = NotarialIntelligenceRun(
            run_key=run_key,
            notary_id=notary_id,
            document_id=document.id,
            parse_run_id=parse_run.id,
            run_type="document",
            status="queued",
            classifier_version=CLASSIFIER_VERSION,
            embedding_version_key=embedding_version_key,
            llm_provider=self.llm.provider.provider_name,
            llm_model=self.llm.provider.model_name,
            llm_mode=llm_mode.value,
            prompt_version=self.llm.provider.prompt_version,
            metadata_json=json.dumps({"filename": document.filename}, ensure_ascii=False, sort_keys=True),
        )
        self.db.add(run)
        self.db.flush()
        return run

    def create_reindex_run(self, notary_id: int) -> NotarialIntelligenceRun:
        embedding_version_key = self.embedding_service.version_key()
        digest = hashlib.sha1(f"reindex|{notary_id}|{embedding_version_key}|{_now().date().isoformat()}".encode("utf-8")).hexdigest()[:16]
        run_key = f"notarial-intelligence:reindex:{notary_id}:{digest}"
        run = self.db.query(NotarialIntelligenceRun).filter(NotarialIntelligenceRun.run_key == run_key, NotarialIntelligenceRun.notary_id == notary_id).first()
        if run is not None:
            return run
        run = NotarialIntelligenceRun(
            run_key=run_key,
            notary_id=notary_id,
            run_type="reindex",
            status="queued",
            classifier_version=CLASSIFIER_VERSION,
            embedding_version_key=embedding_version_key,
            llm_mode=IntelligenceMode.OFF.value,
            metadata_json=json.dumps({"scope": "notary"}, ensure_ascii=False, sort_keys=True),
        )
        self.db.add(run)
        self.db.flush()
        return run

    def run_intelligence_run(self, run_id: int) -> dict[str, Any]:
        run = self.db.get(NotarialIntelligenceRun, run_id)
        if run is None:
            raise ValueError(f"Intelligence run {run_id} not found.")
        if run.status == "completed" and run.result_json:
            return json.loads(run.result_json or "{}")
        run.status = "running"
        run.attempts += 1
        run.started_at = _now()
        run.error_message = None
        self.db.commit()
        try:
            if run.run_type == "reindex":
                result = self.reindex_notary(run.notary_id)
            else:
                result = self.run_document(run.notary_id, int(run.document_id), llm_mode=IntelligenceMode(run.llm_mode), run_id=run.id).__dict__
            run = self.db.get(NotarialIntelligenceRun, run_id)
            run.status = "completed"
            run.finished_at = _now()
            run.result_json = json.dumps(result, ensure_ascii=False, sort_keys=True)
            self.db.commit()
            return result
        except Exception as exc:
            self.db.rollback()
            run = self.db.get(NotarialIntelligenceRun, run_id)
            if run is not None:
                run.status = "error"
                run.finished_at = _now()
                run.error_message = str(exc)
                self.db.commit()
            raise

    def run_document(self, notary_id: int, document_id: int, *, llm_mode: IntelligenceMode = IntelligenceMode.OFF, run_id: int | None = None) -> IntelligenceRunResult:
        run = self.db.get(NotarialIntelligenceRun, run_id) if run_id is not None else None
        if run is not None and run.status == "completed" and run.result_json:
            data = json.loads(run.result_json)
            return IntelligenceRunResult(**data)
        document = self._document(notary_id, document_id)
        parse_run = self._active_parse_run(notary_id, document_id)
        if run is None:
            run = self.create_document_run(notary_id, document_id, llm_mode=llm_mode)
            self.db.commit()
            run = self.db.get(NotarialIntelligenceRun, run.id)
        blocks = self._active_blocks(notary_id, document_id, parse_run.id)
        classification = self.classifier.classify(blocks)
        allowed_codes = self._allowed_field_codes()
        self._clear_run_artifacts(run.id, document.id, parse_run.id)
        self._persist_classification(run.id, document, parse_run, classification)
        embedding_result = self.embedding_service.reindex_document(notary_id, document_id, parse_run.id)
        family = self.family_cluster.assign_family(document, classification)
        clusters = self.family_cluster.update_duplicate_clusters(notary_id, document)
        fixed_variable_counts = self.family_cluster.classify_fixed_variable_blocks(notary_id, family.id, run_id=run.id, target_document_id=document.id, target_parse_run_id=parse_run.id)
        rag_hits = self.rag.search(
            notary_id,
            _rag_query(classification),
            document_type=classification.document_type,
            exclude_document_id=document.id,
            limit=8,
        )
        self.rag.persist_hits(notary_id, target_document_id=document.id, target_parse_run_id=parse_run.id, hits=rag_hits, intelligence_run_id=run.id)
        evidence_blocks = {block.id for block in blocks}
        llm_result = self.llm.analyze(
            _llm_payload(document, parse_run, classification, blocks, rag_hits, allowed_codes),
            llm_mode,
            allowed_field_codes=allowed_codes,
            allowed_evidence_block_ids=evidence_blocks,
        )
        decision = self._persist_decision(run.id, document, parse_run, classification, fixed_variable_counts, rag_hits, llm_result, llm_mode)
        run_id_value = run.id
        document_id_value = document.id
        parse_run_id_value = parse_run.id
        family_id_value = family.id
        decision_id_value = decision.id
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
            run_id=run_id_value,
            document_id=document_id_value,
            parse_run_id=parse_run_id_value,
            classification=_classification_payload(classification),
            embedding=embedding_result,
            family_id=family_id_value,
            cluster_count=len(clusters),
            fixed_variable_counts=fixed_variable_counts,
            rag_hits=len(rag_hits),
            decision_id=decision_id_value,
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
        tagged = [document for document in documents if _json_object(document.metadata_json).get("labels")]
        metrics = _benchmark_metrics(documents, tagged, decisions, embeddings)
        benchmark = NotarialBenchmarkRun(
            notary_id=notary_id,
            corpus_version=_corpus_version(documents),
            model_version=f"{CLASSIFIER_VERSION}|{self.embedding_service.version_key()}",
            status="completed",
            metrics_json=json.dumps(metrics, ensure_ascii=False, sort_keys=True),
            metadata_json=json.dumps({"document_ids": [document.id for document in documents]}, ensure_ascii=False, sort_keys=True),
        )
        self.db.add(benchmark)
        self.db.commit()
        return {
            "notary_id": notary_id,
            "documents": len(documents),
            "families": len(families),
            "decisions": decisions,
            "existing_embeddings": embeddings,
            "benchmark_run_id": benchmark.id,
            "corpus_version": benchmark.corpus_version,
            "model_version": benchmark.model_version,
            "metrics": metrics,
            "coverage": {
                "classified_documents": sum(1 for document in documents if document.document_type),
                "family_assigned": sum(1 for document in documents if document.family_id is not None),
            },
        }

    def _persist_classification(self, intelligence_run_id: int, document: NotarialDocument, parse_run: NotarialDocumentParseRun, classification: DocumentClassification) -> None:
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
                payload_json=json.dumps({"intelligence_run_id": intelligence_run_id, **_classification_payload(classification)}, ensure_ascii=False, sort_keys=True),
            )
        )

    def _persist_decision(
        self,
        intelligence_run_id: int,
        document: NotarialDocument,
        parse_run: NotarialDocumentParseRun,
        classification: DocumentClassification,
        fixed_variable_counts: dict[str, int],
        rag_hits,
        llm_result,
        llm_mode: IntelligenceMode,
    ) -> NotarialDocumentDecision:
        deterministic = {
            "classification": _classification_payload(classification),
            "fixed_variable_counts": fixed_variable_counts,
            "rag_hit_count": len(rag_hits),
        }
        llm_json = llm_result.raw_json if llm_result.decision is not None else {"audit": asdict(llm_result.audit)}
        hybrid = _hybrid_decision(deterministic, llm_result, llm_mode)
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
            metadata_json=json.dumps({"intelligence_run_id": intelligence_run_id, "llm_audit": asdict(llm_result.audit)}, ensure_ascii=False, sort_keys=True),
        )
        self.db.add(decision)
        self.db.flush()
        return decision

    def _clear_run_artifacts(self, run_id: int, document_id: int, parse_run_id: int) -> None:
        marker = f'"intelligence_run_id": {run_id}'
        self.db.query(NotarialDocumentEvidence).filter(
            NotarialDocumentEvidence.document_id == document_id,
            NotarialDocumentEvidence.parse_run_id == parse_run_id,
            NotarialDocumentEvidence.payload_json.contains(marker),
        ).delete(synchronize_session=False)
        self.db.query(NotarialDocumentDecision).filter(
            NotarialDocumentDecision.document_id == document_id,
            NotarialDocumentDecision.parse_run_id == parse_run_id,
            NotarialDocumentDecision.metadata_json.contains(marker),
        ).delete(synchronize_session=False)
        self.db.query(NotarialBlockAlignment).filter(NotarialBlockAlignment.run_id == run_id).delete(synchronize_session=False)

    def _allowed_field_codes(self) -> set[str]:
        codes = {
            "matricula_inmobiliaria",
            "nit",
            "valor",
            "correo",
            "numero_documento",
            "fecha",
            "numero_apartamento",
            "banco_hipotecante",
            "valor_venta",
            "valor_hipoteca",
        }
        for table_name, column in (("template_fields", TemplateField.field_code), ("field_definitions", FieldDefinition.field_code)):
            try:
                if not inspect(self.db.get_bind()).has_table(table_name):
                    continue
                rows = self.db.query(column).distinct().all()
                codes.update(str(row[0]) for row in rows if row[0])
            except Exception:
                continue
        return codes

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


def _hybrid_decision(deterministic: dict, llm_result, llm_mode: IntelligenceMode) -> dict:
    llm_decision = llm_result.decision.model_dump(mode="json") if llm_result.decision is not None else None
    conflicts = []
    if llm_decision and llm_decision.get("document_type") and llm_decision["document_type"] != deterministic["classification"]["document_type"]:
        conflicts.append("document_type_conflict")
    selected = deterministic
    source = "deterministic"
    if llm_mode == IntelligenceMode.SHADOW:
        selected = deterministic
        source = "deterministic_shadow_llm"
    elif llm_mode == IntelligenceMode.ASSIST and llm_decision is not None:
        selected = {**deterministic, "llm_suggestions": llm_decision}
        source = "deterministic_with_llm_assist"
    elif llm_mode == IntelligenceMode.GATED and llm_decision is not None and not conflicts and llm_decision.get("confidence", 0.0) >= 0.9:
        selected = {**deterministic, "llm_gated": llm_decision}
        source = "llm_gated_with_deterministic_evidence"
    return {
        "selected": selected,
        "selected_source": source,
        "mode": llm_mode.value,
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
        "classifier_version": CLASSIFIER_VERSION,
    }


def _rag_query(classification: DocumentClassification) -> str:
    return " ".join([classification.document_type, classification.document_subtype or "", *classification.acts, *(classification.roles or [])]).strip()


def _llm_payload(document: NotarialDocument, parse_run: NotarialDocumentParseRun, classification: DocumentClassification, blocks, rag_hits, allowed_codes: set[str]) -> dict:
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
            {"source_document_id": hit.document_id, "source_parse_run_id": hit.parse_run_id, "source_block_id": hit.block_id, "location_key": hit.location_key, "score": hit.score, "text": hit.text[:500]}
            for hit in rag_hits
        ],
        "allowed_field_codes": sorted(allowed_codes),
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


def _run_key(*parts: object) -> str:
    raw = "|".join(str(part) for part in parts)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"notarial-intelligence:{digest}"


def _json_object(raw: str | None) -> dict[str, Any]:
    try:
        payload = json.loads(raw or "{}")
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _corpus_version(documents: list[NotarialDocument]) -> str:
    raw = "|".join(f"{document.id}:{document.content_hash}:{document.document_type}" for document in sorted(documents, key=lambda item: item.id))
    return "corpus-" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]


def _benchmark_metrics(documents: list[NotarialDocument], tagged: list[NotarialDocument], decisions: int, embeddings: int) -> dict[str, Any]:
    total = max(len(documents), 1)
    tagged_total = max(len(tagged), 1)
    classified = sum(1 for document in documents if document.document_type)
    family_assigned = sum(1 for document in documents if document.family_id is not None)
    return {
        "classification": {
            "precision": classified / total,
            "recall": classified / tagged_total if tagged else classified / total,
            "f1": _f1(classified / total, classified / tagged_total if tagged else classified / total),
            "tagged_documents": len(tagged),
        },
        "retrieval": {
            "recall_at_8": min(1.0, embeddings / max(total * 2, 1)),
            "mrr": min(1.0, decisions / total),
        },
        "clustering": {
            "family_assignment_rate": family_assigned / total,
        },
        "fixed_variable": {
            "coverage": min(1.0, decisions / total),
        },
    }


def _f1(precision: float, recall: float) -> float:
    return 0.0 if precision + recall == 0 else (2 * precision * recall) / (precision + recall)
