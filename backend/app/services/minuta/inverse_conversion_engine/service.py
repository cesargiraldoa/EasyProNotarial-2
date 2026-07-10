from __future__ import annotations

import json
from dataclasses import fields
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.minuta.inverse_conversion_engine.audit import InverseConversionAuditLog
from app.services.minuta.inverse_conversion_engine.llm_contracts import CandidateDecision, EngineFinalResult, ValidationWarning
from app.services.minuta.inverse_conversion_engine.models import EngineCandidate, EngineOptions
from app.services.minuta.inverse_conversion_engine.orchestrator import InverseConversionOrchestrator
from app.services.minuta.inverse_conversion_engine.state import InverseConversionState


class InverseConversionEngineService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.audit = InverseConversionAuditLog(db)

    def analyze_text(self, text_value: str, options: EngineOptions | None = None) -> EngineFinalResult:
        options = options or EngineOptions()
        run_id = self._create_run("text", text_value, options)
        state = InverseConversionState(run_id=run_id, input_type="text", input_text=text_value)
        return self._run(state, options)

    def analyze_marker(
        self,
        raw_marker: str,
        context_before: str | None = None,
        context_after: str | None = None,
        options: EngineOptions | None = None,
    ) -> EngineFinalResult:
        options = options or EngineOptions()
        payload = json.dumps(
            {"marker": raw_marker, "context_before": context_before, "context_after": context_after},
            ensure_ascii=False,
        )
        run_id = self._create_run("marker", payload, options)
        state = InverseConversionState(
            run_id=run_id,
            input_type="marker",
            raw_marker=raw_marker,
            context_before=context_before,
            context_after=context_after,
        )
        return self._run(state, options)

    def analyze_document_path(self, path: str, options: EngineOptions | None = None) -> EngineFinalResult:
        options = options or EngineOptions()
        run_id = self._create_run("document_path", path, options)
        state = InverseConversionState(run_id=run_id, input_type="document_path", input_document_path=path)
        return self._run(state, options)

    def get_run(self, run_id: int) -> dict[str, Any] | None:
        row = self.db.execute(text("select * from inverse_conversion_runs where id = :run_id"), {"run_id": run_id}).mappings().first()
        return dict(row) if row else None

    def list_run_steps(self, run_id: int) -> list[dict[str, Any]]:
        rows = self.db.execute(
            text("select * from inverse_conversion_run_steps where run_id = :run_id order by id asc"),
            {"run_id": run_id},
        ).mappings().all()
        return [dict(row) for row in rows]

    def _create_run(self, input_type: str, payload: str, options: EngineOptions) -> int | None:
        if not options.persist_audit:
            return None
        return self.audit.create_run(input_type, payload, metadata={"use_llm": options.use_llm, "use_semantic": options.use_semantic})

    def _run(self, state: InverseConversionState, options: EngineOptions) -> EngineFinalResult:
        try:
            final_state = InverseConversionOrchestrator(self.db, options).run(state)
            final_state = self._normalize_state(final_state)
        except Exception as exc:
            if options.persist_audit:
                self.audit.finish_run(state.run_id, "error", str(exc))
            raise
        return self._to_final_result(final_state)

    @staticmethod
    def _normalize_state(value: InverseConversionState | dict[str, Any]) -> InverseConversionState:
        if isinstance(value, InverseConversionState):
            return value
        if isinstance(value, dict):
            # LangGraph may return the typed state as a plain dict after graph execution.
            state_fields = {field.name for field in fields(InverseConversionState)}
            data = {key: state_value for key, state_value in value.items() if key in state_fields}
            candidates = data.get("validated_candidates")
            if isinstance(candidates, list):
                data["validated_candidates"] = [
                    EngineCandidate(**candidate) if isinstance(candidate, dict) else candidate for candidate in candidates
                ]
            return InverseConversionState(**data)
        raise TypeError(f"Unsupported inverse conversion state type: {type(value).__name__}")

    @staticmethod
    def _to_final_result(state: InverseConversionState) -> EngineFinalResult:
        candidates = [InverseConversionEngineService._candidate_decision(candidate) for candidate in state.validated_candidates]
        return EngineFinalResult(
            run_id=state.run_id,
            status="completed" if not state.errors else "error",
            requires_human_review=state.requires_human_review,
            candidates=candidates,
            warnings=list(dict.fromkeys(state.warnings)),
            errors=state.errors,
            metadata=state.final_result.get("metadata", {}) if state.final_result else {},
        )

    @staticmethod
    def _candidate_decision(candidate: EngineCandidate) -> CandidateDecision:
        warnings = []
        for warning in candidate.warnings:
            code, _, message = warning.partition(":")
            warnings.append(ValidationWarning(code=code, message=message or warning))
        return CandidateDecision(
            candidate_field_code=candidate.candidate_field_code,
            canonical_field_code=candidate.canonical_field_code,
            status=candidate.status,
            confidence_score=candidate.confidence_score,
            requires_human_review=candidate.requires_human_review,
            warnings=warnings,
        )
