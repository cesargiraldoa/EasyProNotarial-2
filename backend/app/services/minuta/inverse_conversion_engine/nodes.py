from __future__ import annotations

import re
from dataclasses import asdict
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.minuta.inverse_conversion_catalog.docx_marker_extractor import DocxMarkerExtractor
from app.services.minuta.inverse_conversion_catalog.field_code_normalizer import FieldCodeNormalizer
from app.services.minuta.inverse_conversion_engine.audit import InverseConversionAuditLog
from app.services.minuta.inverse_conversion_engine.conservative_validator import ConservativeCandidateValidator
from app.services.minuta.inverse_conversion_engine.llm_contracts import LLMProposalRequest
from app.services.minuta.inverse_conversion_engine.models import EngineCandidate, EngineOptions, ExtractedContext
from app.services.minuta.inverse_conversion_engine.pydantic_ai_client import PydanticAIProposalClient
from app.services.minuta.inverse_conversion_engine.semantic_repository import SemanticRepository
from app.services.minuta.inverse_conversion_engine.state import InverseConversionState
from app.services.minuta.inverse_conversion_rag.repository import InverseConversionReadOnlyRepository
from app.services.minuta.inverse_conversion_rag.retriever import InverseConversionRetriever


MARKER_PATTERN = re.compile(r"\{\{\s*([^{}]+?)\s*\}\}")


class EngineNodes:
    def __init__(
        self,
        db: Session,
        options: EngineOptions | None = None,
        llm_client: PydanticAIProposalClient | None = None,
        audit_log: InverseConversionAuditLog | None = None,
    ) -> None:
        self.db = db
        self.options = options or EngineOptions()
        self.normalizer = FieldCodeNormalizer()
        self.llm_client = llm_client or PydanticAIProposalClient(enabled=self.options.use_llm)
        self.audit_log = audit_log or InverseConversionAuditLog(db)

    def initialize_run(self, state: InverseConversionState) -> InverseConversionState:
        self._record_step(state, "initialize_run", {"input_type": state.input_type}, {"run_id": state.run_id})
        return state

    def extract_contexts(self, state: InverseConversionState) -> InverseConversionState:
        contexts: list[ExtractedContext] = []
        if state.raw_marker:
            contexts.append(
                ExtractedContext(
                    raw_marker=self.normalizer.normalize(state.raw_marker),
                    text_before=state.context_before or "",
                    text_after=state.context_after or "",
                    source="marker",
                )
            )
        if state.input_text:
            contexts.extend(self._contexts_from_text(state.input_text))
        if state.input_document_path:
            contexts.extend(self._contexts_from_docx(state.input_document_path, state))
        if not contexts and state.input_text:
            contexts.append(ExtractedContext(raw_marker=None, text_before=state.input_text[:240], text_after="", source="text"))
        state.extracted_contexts = contexts
        self._record_step(state, "extract_contexts", {}, {"contexts": [asdict(item) for item in contexts]}, list(state.warnings))
        return state

    def retrieve_lexical_evidence(self, state: InverseConversionState) -> InverseConversionState:
        repository = InverseConversionReadOnlyRepository(self.db, enforce_read_only=False)
        retriever = InverseConversionRetriever(repository)
        evidence: list[dict[str, Any]] = []
        try:
            for context in state.extracted_contexts:
                if context.raw_marker:
                    result = retriever.retrieve_candidates_for_marker(
                        context.raw_marker,
                        context.text_before,
                        context.text_after,
                        limit=self.options.limit,
                    )
                elif context.text_before or context.text_after:
                    result = retriever.retrieve_by_before_after(context.text_before, context.text_after, limit=self.options.limit)
                else:
                    result = retriever.retrieve_by_text_context(state.input_text or "", limit=self.options.limit)
                for candidate in result.candidates:
                    payload = asdict(candidate)
                    payload["raw_marker"] = context.raw_marker
                    payload["context_before"] = context.text_before
                    payload["context_after"] = context.text_after
                    evidence.append(payload)
        finally:
            repository.close()
        state.lexical_evidence = evidence[: self.options.limit * max(1, len(state.extracted_contexts))]
        self._record_step(state, "retrieve_lexical_evidence", {}, {"count": len(state.lexical_evidence)})
        return state

    def retrieve_semantic_evidence(self, state: InverseConversionState) -> InverseConversionState:
        if not self.options.use_semantic:
            state.warnings.append("semantic_disabled")
            self._record_step(state, "retrieve_semantic_evidence", {}, {"count": 0}, ["semantic_disabled"])
            return state
        repository = SemanticRepository(self.db)
        evidence: list[dict[str, Any]] = []
        queries = []
        if state.input_text:
            queries.append(state.input_text)
        for context in state.extracted_contexts:
            queries.append(" ".join(part for part in (context.raw_marker, context.text_before, context.text_after) if part))
        for query in queries:
            for hit in repository.semantic_search(query, limit=self.options.limit):
                evidence.append(asdict(hit))
        if not repository.has_embeddings():
            state.warnings.append("semantic_embeddings_unavailable_using_lexical_fallback")
        state.semantic_evidence = evidence[: self.options.limit]
        self._record_step(state, "retrieve_semantic_evidence", {}, {"count": len(state.semantic_evidence)}, list(state.warnings))
        return state

    def propose_candidates(self, state: InverseConversionState) -> InverseConversionState:
        proposals = []
        contexts = state.extracted_contexts or [ExtractedContext(raw_marker=None, text_before=state.input_text or "", text_after="")]
        for context in contexts:
            request = LLMProposalRequest(
                raw_marker=context.raw_marker,
                context_before=context.text_before,
                context_after=context.text_after,
                lexical_evidence=self._evidence_for_context(state.lexical_evidence, context),
                semantic_evidence=state.semantic_evidence,
            )
            response = self.llm_client.propose(request)
            state.warnings.extend(response.warnings)
            for proposal in response.proposals:
                proposals.append(
                    {
                        "proposal": proposal,
                        "raw_marker": context.raw_marker,
                        "context_before": context.text_before,
                        "context_after": context.text_after,
                    }
                )
        state.llm_proposals = proposals
        self._record_step(state, "propose_candidates", {}, {"count": len(proposals)}, list(state.warnings))
        return state

    def validate_candidates(self, state: InverseConversionState) -> InverseConversionState:
        validator = ConservativeCandidateValidator(known_field_codes=self._known_field_codes())
        validated: list[EngineCandidate] = []
        for item in state.llm_proposals:
            validated.append(
                validator.validate(
                    item["proposal"],
                    raw_marker=item.get("raw_marker"),
                    context_before=item.get("context_before"),
                    context_after=item.get("context_after"),
                )
            )
        state.validated_candidates = sorted(validated, key=lambda item: (-item.confidence_score, item.canonical_field_code))[: self.options.limit]
        state.requires_human_review = any(candidate.requires_human_review for candidate in state.validated_candidates)
        self._record_step(state, "validate_candidates", {}, {"count": len(state.validated_candidates)})
        return state

    def build_auditable_result(self, state: InverseConversionState) -> InverseConversionState:
        state.final_result = {
            "run_id": state.run_id,
            "status": "completed" if not state.errors else "error",
            "requires_human_review": state.requires_human_review,
            "candidates": [candidate.to_dict() for candidate in state.validated_candidates],
            "warnings": list(dict.fromkeys(state.warnings)),
            "errors": state.errors,
            "metadata": {
                "contexts": len(state.extracted_contexts),
                "lexical_evidence": len(state.lexical_evidence),
                "semantic_evidence": len(state.semantic_evidence),
                "llm_enabled": self.options.use_llm,
                "semantic_enabled": self.options.use_semantic,
            },
        }
        self._record_step(state, "build_auditable_result", {}, state.final_result, list(state.warnings))
        return state

    def persist_audit(self, state: InverseConversionState) -> InverseConversionState:
        if not self.options.persist_audit:
            return state
        for candidate in state.validated_candidates:
            self.audit_log.persist_candidate(state.run_id, candidate)
        self.audit_log.finish_run(state.run_id, "completed" if not state.errors else "error", "\n".join(state.errors) or None)
        self._record_step(state, "persist_audit", {}, {"candidates": len(state.validated_candidates)})
        return state

    def _contexts_from_text(self, text_value: str) -> list[ExtractedContext]:
        contexts = []
        for match in MARKER_PATTERN.finditer(text_value):
            contexts.append(
                ExtractedContext(
                    raw_marker=self.normalizer.normalize(match.group(1)),
                    text_before=text_value[max(0, match.start() - 180) : match.start()].strip(),
                    text_after=text_value[match.end() : match.end() + 180].strip(),
                    source="text_marker",
                )
            )
        return contexts

    def _contexts_from_docx(self, path_value: str, state: InverseConversionState) -> list[ExtractedContext]:
        path = Path(path_value)
        if path.suffix.lower() != ".docx":
            state.warnings.append("document_path_not_docx")
            return []
        try:
            markers = DocxMarkerExtractor().extract_from_docx(path)
        except Exception as exc:
            state.errors.append(f"document_extract_error:{exc}")
            return []
        return [
            ExtractedContext(
                raw_marker=self.normalizer.normalize(marker.raw_field_code),
                text_before=marker.text_before,
                text_after=marker.text_after,
                source=f"docx:{marker.location.label()}",
            )
            for marker in markers
        ]

    @staticmethod
    def _evidence_for_context(evidence: list[dict[str, Any]], context: ExtractedContext) -> list[dict[str, Any]]:
        if not context.raw_marker:
            return evidence
        matched = [item for item in evidence if item.get("raw_marker") == context.raw_marker]
        return matched or evidence

    def _known_field_codes(self) -> set[str]:
        try:
            rows = self.db.execute(text("select field_code from field_definitions")).fetchall()
            return {row.field_code for row in rows}
        except Exception:
            return set()

    def _record_step(
        self,
        state: InverseConversionState,
        step_name: str,
        input_data: dict[str, Any],
        output_data: dict[str, Any],
        warnings: list[str] | None = None,
    ) -> None:
        if self.options.persist_audit:
            self.audit_log.record_step(state.run_id, step_name, "completed", input_data, output_data, warnings)
