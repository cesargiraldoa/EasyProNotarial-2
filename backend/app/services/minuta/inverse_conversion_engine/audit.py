from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.minuta.inverse_conversion_engine.models import EngineCandidate


class InverseConversionAuditLog:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_run(self, input_type: str, input_payload: str, metadata: dict[str, Any] | None = None) -> int:
        row = self.db.execute(
            text(
                """
                insert into inverse_conversion_runs (input_type, input_hash, status, metadata_json)
                values (:input_type, :input_hash, 'running', :metadata_json)
                returning id
                """
            ),
            {
                "input_type": input_type,
                "input_hash": hashlib.sha256(input_payload.encode("utf-8")).hexdigest(),
                "metadata_json": json.dumps(metadata or {}, ensure_ascii=False),
            },
        ).first()
        self.db.commit()
        return int(row.id)

    def record_step(self, run_id: int | None, step_name: str, status: str, input_data: dict[str, Any] | None = None, output_data: dict[str, Any] | None = None, warnings: list[str] | None = None) -> None:
        if run_id is None:
            return
        self.db.execute(
            text(
                """
                insert into inverse_conversion_run_steps
                (run_id, step_name, status, input_json, output_json, warnings_json)
                values (:run_id, :step_name, :status, :input_json, :output_json, :warnings_json)
                """
            ),
            {
                "run_id": run_id,
                "step_name": step_name,
                "status": status,
                "input_json": json.dumps(input_data or {}, ensure_ascii=False, default=str),
                "output_json": json.dumps(output_data or {}, ensure_ascii=False, default=str),
                "warnings_json": json.dumps(warnings or [], ensure_ascii=False),
            },
        )
        self.db.commit()

    def persist_candidate(self, run_id: int | None, candidate: EngineCandidate) -> None:
        if run_id is None:
            return
        self.db.execute(
            text(
                """
                insert into inverse_conversion_candidates
                (run_id, raw_marker, context_before, context_after, candidate_field_code, canonical_field_code,
                 confidence_score, status, evidence_json, warnings_json, requires_human_review)
                values
                (:run_id, :raw_marker, :context_before, :context_after, :candidate_field_code, :canonical_field_code,
                 :confidence_score, :status, :evidence_json, :warnings_json, :requires_human_review)
                """
            ),
            {
                "run_id": run_id,
                "raw_marker": candidate.raw_marker,
                "context_before": candidate.context_before,
                "context_after": candidate.context_after,
                "candidate_field_code": candidate.candidate_field_code,
                "canonical_field_code": candidate.canonical_field_code,
                "confidence_score": candidate.confidence_score,
                "status": candidate.status,
                "evidence_json": json.dumps(candidate.evidence, ensure_ascii=False, default=str),
                "warnings_json": json.dumps(list(candidate.warnings), ensure_ascii=False),
                "requires_human_review": candidate.requires_human_review,
            },
        )
        self.db.commit()

    def finish_run(self, run_id: int | None, status: str, error_message: str | None = None) -> None:
        if run_id is None:
            return
        self.db.execute(
            text(
                """
                update inverse_conversion_runs
                set status=:status, finished_at=:finished_at, error_message=:error_message
                where id=:run_id
                """
            ),
            {
                "run_id": run_id,
                "status": status,
                "finished_at": datetime.now(timezone.utc),
                "error_message": error_message,
            },
        )
        self.db.commit()
