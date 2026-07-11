from __future__ import annotations

import hashlib
import json
import re
from difflib import SequenceMatcher
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.notarial_document_intelligence import (
    NotarialBlockAlignment,
    NotarialDocument,
    NotarialDocumentBlock,
    NotarialDocumentCluster,
    NotarialDocumentClusterMember,
    NotarialDocumentFamily,
    NotarialDocumentFamilyMember,
    NotarialDocumentParseRun,
    NotarialDocumentEmbedding,
    NotarialEmbeddingVersion,
)
from app.services.notarial_document_intelligence.classifier import DocumentClassification
from app.services.notarial_document_intelligence.vector_store import NotarialVectorStore


@dataclass(frozen=True)
class AlignmentSummary:
    fixed: int
    variable: int
    optional: int
    unknown: int


class NotarialFamilyClusterService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def assign_family(self, document: NotarialDocument, classification: DocumentClassification) -> NotarialDocumentFamily:
        key_parts = [
            classification.document_type or "documento",
            classification.document_subtype or "general",
            classification.bank_name or "sin_banco",
            classification.project_name or "sin_proyecto",
        ]
        family_key = "fam_" + hashlib.sha1("|".join(_slug(part) for part in key_parts).encode("utf-8")).hexdigest()[:16]
        family = (
            self.db.query(NotarialDocumentFamily)
            .filter(NotarialDocumentFamily.notary_id == document.notary_id, NotarialDocumentFamily.family_key == family_key)
            .first()
        )
        if family is None:
            family = NotarialDocumentFamily(
                notary_id=document.notary_id,
                family_key=family_key,
                label=" / ".join(part for part in key_parts if part),
                document_type=classification.document_type,
                notary_name=classification.notary_name,
                project_name=classification.project_name,
                bank_name=classification.bank_name,
                status="suggested",
                confidence=classification.confidence,
                metadata_json=json.dumps({"acts": classification.acts, "roles": classification.roles}, ensure_ascii=False, sort_keys=True),
            )
            self.db.add(family)
            self.db.flush()
        else:
            family.confidence = max(float(family.confidence or 0.0), classification.confidence)
        document.family_id = family.id
        self._ensure_family_member(family, document, classification.confidence)
        return family

    def update_duplicate_clusters(self, notary_id: int, document: NotarialDocument, near_duplicate_threshold: float = 0.92) -> list[NotarialDocumentCluster]:
        clusters: list[NotarialDocumentCluster] = []
        exact_cluster = self._cluster(
            notary_id,
            "exact_duplicate",
            f"exact:{document.content_hash}",
            f"Duplicados exactos {document.content_hash[:10]}",
            algorithm="sha256",
        )
        self._ensure_cluster_member(exact_cluster, document.id, 1.0, {"content_hash": document.content_hash})
        clusters.append(exact_cluster)

        current_text = self._active_text(notary_id, document.id)
        if not current_text:
            return clusters
        candidate_ids = self._candidate_document_ids(notary_id, document.id)
        near_members = {document.id: 1.0}
        for other in self.db.query(NotarialDocument).filter(NotarialDocument.id.in_(candidate_ids or [0])).all():
            score = SequenceMatcher(None, current_text, self._active_text(notary_id, other.id)).ratio()
            if score >= near_duplicate_threshold:
                near_members[other.id] = score
        if len(near_members) > 1:
            representative = min(near_members)
            key = "near:" + hashlib.sha1("|".join(str(item) for item in sorted(near_members)).encode("utf-8")).hexdigest()[:16]
            cluster = self._cluster(notary_id, "near_duplicate", key, f"Casi duplicados grupo {representative}", algorithm="pgvector+structural-rerank")
            for document_id, score in near_members.items():
                self._ensure_cluster_member(cluster, document_id, score, {"representative_document_id": representative})
            clusters.append(cluster)
        return clusters

    def classify_fixed_variable_blocks(self, notary_id: int, family_id: int, *, run_id: int | None = None, target_document_id: int | None = None, target_parse_run_id: int | None = None) -> dict[str, int]:
        documents = (
            self.db.query(NotarialDocument.id)
            .filter(NotarialDocument.notary_id == notary_id, NotarialDocument.family_id == family_id)
            .order_by(NotarialDocument.id.asc())
            .all()
        )
        document_ids = [int(row[0]) for row in documents]
        if not document_ids:
            return {"fixed": 0, "variable": 0, "optional": 0, "unknown": 0}
        blocks_by_doc = {document_id: self._active_blocks(notary_id, document_id) for document_id in document_ids}
        values_by_location: dict[str, dict[int, str]] = {}
        for document_id, blocks in blocks_by_doc.items():
            for block in blocks:
                values_by_location.setdefault(_alignment_key(block), {})[document_id] = _normalize_text(block.text)

        counts = {"fixed": 0, "variable": 0, "optional": 0, "unknown": 0}
        for document_id, blocks in blocks_by_doc.items():
            for block in blocks:
                values = values_by_location.get(_alignment_key(block), {})
                unique_values = {value for value in values.values() if value}
                if len(values) < len(document_ids):
                    label = "optional"
                elif len(unique_values) == 1 and len(document_ids) > 1:
                    label = "fixed"
                elif len(unique_values) > 1:
                    label = "variable"
                else:
                    label = "unknown"
                block.fixed_variable_label = label
                counts[label] += 1
        if run_id is not None and target_document_id is not None and target_parse_run_id is not None:
            self._persist_alignments(notary_id, run_id, target_document_id, target_parse_run_id, blocks_by_doc)
        return counts

    def _persist_alignments(self, notary_id: int, run_id: int, target_document_id: int, target_parse_run_id: int, blocks_by_doc: dict[int, list[NotarialDocumentBlock]]) -> None:
        target_blocks = blocks_by_doc.get(target_document_id, [])
        source_blocks = [block for document_id, blocks in blocks_by_doc.items() if document_id != target_document_id for block in blocks]
        self.db.query(NotarialBlockAlignment).filter(NotarialBlockAlignment.run_id == run_id).delete(synchronize_session=False)
        for target in target_blocks:
            candidates = sorted(
                (
                    (_combined_alignment_score(target, source), source)
                    for source in source_blocks
                    if _alignment_key(source) == _alignment_key(target) or _combined_alignment_score(target, source) >= 0.72
                ),
                key=lambda item: item[0],
                reverse=True,
            )[:3]
            for score, source in candidates:
                self.db.add(
                    NotarialBlockAlignment(
                        run_id=run_id,
                        notary_id=notary_id,
                        target_document_id=target_document_id,
                        target_parse_run_id=target_parse_run_id,
                        target_block_id=target.id,
                        source_document_id=source.document_id,
                        source_parse_run_id=source.parse_run_id,
                        source_block_id=source.id,
                        alignment_key=_alignment_key(target),
                        structural_score=_structural_alignment_score(target, source),
                        lexical_score=_lexical_similarity(target.text, source.text),
                        combined_score=score,
                        label=target.fixed_variable_label,
                        metadata_json=json.dumps({"target_location": target.location_key, "source_location": source.location_key}, ensure_ascii=False, sort_keys=True),
                    )
                )

    def _candidate_document_ids(self, notary_id: int, document_id: int, limit: int = 80) -> list[int]:
        version = (
            self.db.query(NotarialEmbeddingVersion)
            .filter(NotarialEmbeddingVersion.provider.in_(["sentence-transformers", "hash-fixture"]))
            .order_by(NotarialEmbeddingVersion.id.desc())
            .first()
        )
        if version is None:
            rows = self.db.query(NotarialDocument.id).filter(NotarialDocument.notary_id == notary_id, NotarialDocument.id != document_id).limit(limit).all()
            return [int(row[0]) for row in rows]
        representative = (
            self.db.query(NotarialDocumentEmbedding)
            .filter(
                NotarialDocumentEmbedding.notary_id == notary_id,
                NotarialDocumentEmbedding.embedding_version_id == version.id,
                NotarialDocumentEmbedding.document_id == document_id,
                NotarialDocumentEmbedding.source_type == "block",
                NotarialDocumentEmbedding.embedding.isnot(None),
            )
            .order_by(NotarialDocumentEmbedding.source_id.asc())
            .first()
        )
        if representative is None:
            return []
        query_vector = json.loads(representative.embedding or "[]")
        store = NotarialVectorStore(self.db, dimensions=version.dimensions)
        rows = store.search(
            notary_id,
            query_vector,
            embedding_version_id=version.id,
            source_type="block",
            exclude_document_id=document_id,
            limit=max(limit * 8, 40),
        )
        best_by_document: dict[int, float] = {}
        embedding_ids = [row.embedding_id for row in rows]
        if not embedding_ids:
            return []
        embeddings_by_id = {
            row.id: row
            for row in self.db.query(NotarialDocumentEmbedding)
            .filter(NotarialDocumentEmbedding.id.in_(embedding_ids), NotarialDocumentEmbedding.document_id.isnot(None))
            .all()
        }
        for row in rows:
            embedding = embeddings_by_id.get(row.embedding_id)
            if embedding is None or embedding.document_id is None or embedding.document_id == document_id:
                continue
            current = best_by_document.get(int(embedding.document_id))
            if current is None or row.distance < current:
                best_by_document[int(embedding.document_id)] = row.distance
        return [document_id for document_id, _distance in sorted(best_by_document.items(), key=lambda item: (item[1], item[0]))[:limit]]

    def _ensure_family_member(self, family: NotarialDocumentFamily, document: NotarialDocument, confidence: float) -> None:
        member = (
            self.db.query(NotarialDocumentFamilyMember)
            .filter(NotarialDocumentFamilyMember.family_id == family.id, NotarialDocumentFamilyMember.document_id == document.id)
            .first()
        )
        if member is None:
            self.db.add(
                NotarialDocumentFamilyMember(
                    family_id=family.id,
                    document_id=document.id,
                    confidence=confidence,
                    source="hybrid",
                    metadata_json=json.dumps({"document_type": document.document_type}, ensure_ascii=False, sort_keys=True),
                )
            )
        else:
            member.confidence = max(float(member.confidence or 0.0), confidence)

    def _cluster(self, notary_id: int, cluster_type: str, raw_key: str, label: str, algorithm: str) -> NotarialDocumentCluster:
        cluster_key = f"{cluster_type}_{hashlib.sha1(raw_key.encode('utf-8')).hexdigest()[:16]}"
        cluster = (
            self.db.query(NotarialDocumentCluster)
            .filter(NotarialDocumentCluster.notary_id == notary_id, NotarialDocumentCluster.cluster_key == cluster_key)
            .first()
        )
        if cluster is None:
            cluster = NotarialDocumentCluster(
                notary_id=notary_id,
                cluster_key=cluster_key,
                label=label,
                cluster_type=cluster_type,
                status="suggested",
                algorithm=algorithm,
                metadata_json=json.dumps({"raw_key": raw_key}, ensure_ascii=False, sort_keys=True),
            )
            self.db.add(cluster)
            self.db.flush()
        return cluster

    def _ensure_cluster_member(self, cluster: NotarialDocumentCluster, document_id: int, score: float, metadata: dict) -> None:
        member = (
            self.db.query(NotarialDocumentClusterMember)
            .filter(NotarialDocumentClusterMember.cluster_id == cluster.id, NotarialDocumentClusterMember.document_id == document_id)
            .first()
        )
        if member is None:
            self.db.add(
                NotarialDocumentClusterMember(
                    cluster_id=cluster.id,
                    document_id=document_id,
                    similarity_score=score,
                    metadata_json=json.dumps(metadata, ensure_ascii=False, sort_keys=True),
                )
            )
        else:
            member.similarity_score = max(float(member.similarity_score or 0.0), score)

    def _active_blocks(self, notary_id: int, document_id: int) -> list[NotarialDocumentBlock]:
        return (
            self.db.query(NotarialDocumentBlock)
            .join(NotarialDocumentParseRun, NotarialDocumentParseRun.id == NotarialDocumentBlock.parse_run_id)
            .filter(
                NotarialDocumentBlock.notary_id == notary_id,
                NotarialDocumentBlock.document_id == document_id,
                NotarialDocumentParseRun.is_active.is_(True),
                NotarialDocumentParseRun.status == "completed",
            )
            .order_by(NotarialDocumentBlock.block_index.asc())
            .all()
        )

    def _active_text(self, notary_id: int, document_id: int) -> str:
        return "\n".join(_normalize_text(block.text) for block in self._active_blocks(notary_id, document_id))


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", _normalize_text(value)).strip("-") or "sin-dato"


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").lower()).strip()


def _alignment_key(block: NotarialDocumentBlock) -> str:
    normalized = _normalize_text(block.text)
    stable = re.sub(r"\b\d{1,4}(?:[.-]\d{1,10})*\b", "<num>", normalized)
    stable = re.sub(r"\$\s*[\d.,]+", "<money>", stable)
    location_family = "table" if block.table_index is not None else "paragraph"
    semantic = block.semantic_type or block.unstructured_category or location_family
    return hashlib.sha1(f"{semantic}|{stable[:120]}".encode("utf-8")).hexdigest()[:20]


def _structural_alignment_score(left: NotarialDocumentBlock, right: NotarialDocumentBlock) -> float:
    score = 0.0
    if left.block_type == right.block_type:
        score += 0.25
    if (left.semantic_type or left.unstructured_category) == (right.semantic_type or right.unstructured_category):
        score += 0.25
    if left.table_index is not None and right.table_index is not None and left.cell_index == right.cell_index:
        score += 0.25
    if _alignment_key(left) == _alignment_key(right):
        score += 0.25
    return min(score, 1.0)


def _lexical_similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, _normalize_text(left), _normalize_text(right)).ratio()


def _combined_alignment_score(left: NotarialDocumentBlock, right: NotarialDocumentBlock) -> float:
    return (0.55 * _structural_alignment_score(left, right)) + (0.45 * _lexical_similarity(left.text, right.text))
