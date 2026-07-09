from __future__ import annotations

import json
import re
from dataclasses import asdict
from pathlib import Path

from tools.notarial_template_lab.models import (
    AppliedHumanReviewDecision,
    FieldProposal,
    HumanReviewDecision,
    HumanReviewResult,
    ProposalOccurrence,
)


VALID_DECISIONS = {"confirm", "reject", "review_required"}
VALID_STRATEGIES = {"all_occurrences", "selected_occurrences", "review_required"}


class HumanReviewError(ValueError):
    pass


def load_review_decisions(path: str | Path) -> list[HumanReviewDecision]:
    review_path = Path(path)
    payload = json.loads(review_path.read_text(encoding="utf-8-sig"))
    raw_items = payload.get("decisions") if isinstance(payload, dict) else payload
    if not isinstance(raw_items, list):
        raise HumanReviewError("El archivo de revision debe ser una lista o un objeto con clave 'decisions'.")
    return [normalize_decision(item) for item in raw_items if isinstance(item, dict)]


def apply_human_review(
    proposals: list[FieldProposal],
    decisions: list[HumanReviewDecision],
    source_review_file: str | None = None,
    min_confidence: float = 0.8,
) -> HumanReviewResult:
    applied: list[AppliedHumanReviewDecision] = []
    confirmed: list[FieldProposal] = []
    matched_ids: set[int] = set()

    for decision in decisions:
        proposal = find_matching_proposal(proposals, decision)
        if proposal is None:
            applied.append(
                AppliedHumanReviewDecision(
                    field_key=decision.field_key,
                    value=decision.value or "",
                    original_marker="",
                    final_marker=normalize_marker(decision.marker, decision.field_key),
                    decision=decision.decision,
                    replaceable=False,
                    block_reason="No se encontro una propuesta que coincida con la decision humana.",
                    selected_occurrence_ids=decision.occurrence_ids,
                    original_proposal={},
                    human_decision=asdict(decision),
                )
            )
            continue

        matched_ids.add(id(proposal))
        final_marker = normalize_marker(decision.marker, proposal.field_key)
        selected_occurrences = select_occurrences(proposal, decision)
        block_reason = replacement_block_reason(proposal, decision, selected_occurrences, min_confidence)
        replaceable = block_reason is None
        applied.append(
            AppliedHumanReviewDecision(
                field_key=proposal.field_key,
                value=proposal.value,
                original_marker=proposal.marker,
                final_marker=final_marker,
                decision=decision.decision,
                replaceable=replaceable,
                block_reason=block_reason,
                selected_occurrence_ids=[occurrence.occurrence_id for occurrence in selected_occurrences],
                original_proposal=asdict(proposal),
                human_decision=asdict(decision),
            )
        )
        if replaceable:
            confirmed.append(
                FieldProposal(
                    field_key=proposal.field_key,
                    label=proposal.label,
                    marker=final_marker,
                    value=proposal.value,
                    confidence=proposal.confidence,
                    proposal_type=proposal.proposal_type,
                    occurrences=selected_occurrences,
                    apply_strategy=decision.apply_strategy or proposal.apply_strategy,
                    reason=proposal.reason,
                    role=proposal.role,
                    scope=proposal.scope,
                    evidence=proposal.evidence,
                )
            )

    for proposal in proposals:
        if id(proposal) in matched_ids:
            continue
        applied.append(
            AppliedHumanReviewDecision(
                field_key=proposal.field_key,
                value=proposal.value,
                original_marker=proposal.marker,
                final_marker=proposal.marker,
                decision="not_reviewed",
                replaceable=False,
                block_reason="Sin decision humana confirmatoria.",
                selected_occurrence_ids=[],
                original_proposal=asdict(proposal),
                human_decision=None,
            )
        )

    return HumanReviewResult(
        source_review_file=source_review_file,
        applied_decisions=applied,
        confirmed_proposals=confirmed,
    )


def normalize_decision(raw: dict) -> HumanReviewDecision:
    field_key = str(raw.get("field_key") or raw.get("key") or "").strip()
    if not field_key:
        raise HumanReviewError("Cada decision debe incluir field_key.")
    decision = str(raw.get("decision") or raw.get("status") or "").strip().lower()
    if decision not in VALID_DECISIONS:
        decision = "review_required"
    strategy = raw.get("apply_strategy")
    if strategy is not None:
        strategy = str(strategy).strip()
        if strategy not in VALID_STRATEGIES:
            strategy = "review_required"
    occurrence_ids = raw.get("occurrence_ids") or raw.get("selected_occurrence_ids") or []
    if not isinstance(occurrence_ids, list):
        occurrence_ids = []
    return HumanReviewDecision(
        field_key=field_key,
        decision=decision,  # type: ignore[arg-type]
        value=str(raw.get("value")) if raw.get("value") is not None else None,
        marker=str(raw.get("marker") or raw.get("final_marker")) if (raw.get("marker") or raw.get("final_marker")) else None,
        apply_strategy=strategy,  # type: ignore[arg-type]
        occurrence_ids=[str(item) for item in occurrence_ids],
        notes=str(raw.get("notes")) if raw.get("notes") is not None else None,
    )


def find_matching_proposal(proposals: list[FieldProposal], decision: HumanReviewDecision) -> FieldProposal | None:
    candidates = [proposal for proposal in proposals if proposal.field_key == decision.field_key]
    if decision.value is not None:
        exact = [proposal for proposal in candidates if proposal.value == decision.value]
        if exact:
            return exact[0]
    return candidates[0] if candidates else None


def select_occurrences(proposal: FieldProposal, decision: HumanReviewDecision) -> list[ProposalOccurrence]:
    strategy = decision.apply_strategy or proposal.apply_strategy
    if strategy == "selected_occurrences":
        selected = set(decision.occurrence_ids)
        return [occurrence for occurrence in proposal.occurrences if occurrence.occurrence_id in selected]
    if strategy == "all_occurrences":
        return list(proposal.occurrences)
    return []


def replacement_block_reason(
    proposal: FieldProposal,
    decision: HumanReviewDecision,
    selected_occurrences: list[ProposalOccurrence],
    min_confidence: float,
) -> str | None:
    if decision.decision != "confirm":
        return "La decision humana no confirma reemplazo."
    if proposal.proposal_type in {"review_required", "fixed_text"}:
        return f"La propuesta es {proposal.proposal_type}, no reemplazable."
    if proposal.confidence < min_confidence:
        return "Confianza insuficiente para plantilla confirmada."
    strategy = decision.apply_strategy or proposal.apply_strategy
    if strategy not in {"all_occurrences", "selected_occurrences"}:
        return "Estrategia humana no reemplazable."
    if strategy == "selected_occurrences" and not decision.occurrence_ids:
        return "selected_occurrences requiere occurrence_ids."
    if not selected_occurrences:
        return "No hay ocurrencias seleccionadas reemplazables."
    if any(not occurrence.block_id or not occurrence.location for occurrence in selected_occurrences):
        return "Una ocurrencia no tiene block_id o location."
    return None


def normalize_marker(marker: str | None, field_key: str) -> str:
    if marker:
        cleaned = marker.strip()
        if cleaned.startswith("{{") and cleaned.endswith("}}"):
            return cleaned
        key = safe_key(cleaned)
    else:
        key = safe_key(field_key)
    return f"{{{{{key}}}}}"


def safe_key(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", value.lower()).strip("_")
    return cleaned or "campo_confirmado"
