from __future__ import annotations

import hashlib
import json
import re
from difflib import SequenceMatcher

from sqlalchemy.orm import Session

from app.models.notarial_document_intelligence import (
    NotarialDocument,
    NotarialDocumentBlock,
    NotarialDocumentCluster,
    NotarialDocumentClusterMember,
    NotarialDocumentFamily,
    NotarialDocumentFamilyMember,
    NotarialDocumentParseRun,
)
from app.services.notarial_document_intelligence.classifier import DocumentClassification


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
        for other in (
            self.db.query(NotarialDocument)
            .filter(NotarialDocument.notary_id == notary_id, NotarialDocument.id != document.id)
            .order_by(NotarialDocument.id.asc())
            .all()
        ):
            score = SequenceMatcher(None, current_text, self._active_text(notary_id, other.id)).ratio()
            if score >= near_duplicate_threshold:
                key = "near:" + hashlib.sha1("|".join(str(item) for item in sorted([document.id, other.id])).encode("utf-8")).hexdigest()[:16]
                cluster = self._cluster(notary_id, "near_duplicate", key, f"Casi duplicados {document.id}-{other.id}", algorithm="sequence-matcher")
                self._ensure_cluster_member(cluster, document.id, score, {"compared_to": other.id})
                self._ensure_cluster_member(cluster, other.id, score, {"compared_to": document.id})
                clusters.append(cluster)
        return clusters

    def classify_fixed_variable_blocks(self, notary_id: int, family_id: int) -> dict[str, int]:
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
                values_by_location.setdefault(block.location_key, {})[document_id] = _normalize_text(block.text)

        counts = {"fixed": 0, "variable": 0, "optional": 0, "unknown": 0}
        for document_id, blocks in blocks_by_doc.items():
            for block in blocks:
                values = values_by_location.get(block.location_key, {})
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
        return counts

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
