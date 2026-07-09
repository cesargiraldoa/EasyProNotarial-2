from __future__ import annotations

import re

from tools.notarial_template_lab.document_profiler_agent import clamp_float, dict_list, string_list
from tools.notarial_template_lab.llm_client import JSONLLMClient
from tools.notarial_template_lab.models import (
    DocumentMap,
    DocumentProfile,
    FieldProposal,
    ProposalOccurrence,
)
from tools.notarial_template_lab.prompt_contracts import FIELD_PROPOSAL_SYSTEM_PROMPT, compact_document_map


VALID_PROPOSAL_TYPES = {"project_field", "document_field", "derived_field", "review_required", "fixed_text"}
VALID_APPLY_STRATEGIES = {"all_occurrences", "selected_occurrences", "review_required"}


class FieldProposalAgent:
    def __init__(self, llm_client: JSONLLMClient):
        self.llm_client = llm_client

    def run(self, document_map: DocumentMap, document_profile: DocumentProfile) -> list[FieldProposal]:
        payload = {
            "document_map": compact_document_map(document_map),
            "document_profile": document_profile.__dict__,
        }
        raw = self.llm_client.complete_json(FIELD_PROPOSAL_SYSTEM_PROMPT, payload)
        return normalize_field_proposals(raw, document_map)


def normalize_field_proposals(raw: dict, document_map: DocumentMap) -> list[FieldProposal]:
    raw_items = raw.get("proposals") if isinstance(raw.get("proposals"), list) else []
    block_lookup = {block.block_id: block for block in document_map.blocks}
    proposals: list[FieldProposal] = []

    for item in raw_items:
        if not isinstance(item, dict):
            continue
        field_key = safe_key(item.get("field_key") or item.get("label") or "campo_revision")
        proposal_type = str(item.get("proposal_type") or "review_required")
        if proposal_type not in VALID_PROPOSAL_TYPES:
            proposal_type = "review_required"
        apply_strategy = str(item.get("apply_strategy") or "review_required")
        if apply_strategy not in VALID_APPLY_STRATEGIES:
            apply_strategy = "review_required"
        value = str(item.get("value") or "")
        occurrences = normalize_occurrences(dict_list(item.get("occurrences")), value, block_lookup)

        if not occurrences or proposal_type == "review_required":
            apply_strategy = "review_required"
            proposal_type = "review_required"

        proposals.append(
            FieldProposal(
                field_key=field_key,
                label=str(item.get("label") or human_label(field_key)),
                marker=str(item.get("marker") or f"{{{{{field_key}}}}}"),
                value=value,
                confidence=clamp_float(item.get("confidence"), default=0.0),
                proposal_type=proposal_type,  # type: ignore[arg-type]
                occurrences=occurrences,
                apply_strategy=apply_strategy,  # type: ignore[arg-type]
                reason=str(item.get("reason") or ""),
                role=str(item.get("role")) if item.get("role") is not None else None,
                scope=str(item.get("scope")) if item.get("scope") is not None else None,
                evidence=string_list(item.get("evidence")),
            )
        )

    return proposals


def normalize_occurrences(raw_occurrences: list[dict], value: str, block_lookup: dict) -> list[ProposalOccurrence]:
    occurrences: list[ProposalOccurrence] = []
    for raw in raw_occurrences:
        block_id = str(raw.get("block_id") or "")
        block = block_lookup.get(block_id)
        if block is None:
            continue
        try:
            start = int(raw.get("start"))
            end = int(raw.get("end"))
        except (TypeError, ValueError):
            continue
        if start < 0 or end <= start or end > len(block.raw_text):
            continue
        text_at_location = block.raw_text[start:end]
        if value and text_at_location != value:
            # The proposal remains auditable only if offsets point to the exact value.
            continue
        occurrences.append(
            ProposalOccurrence(
                occurrence_id=str(raw.get("occurrence_id") or ""),
                block_id=block_id,
                location=str(raw.get("location") or block.location),
                text=text_at_location,
                start=start,
                end=end,
                before=block.raw_text[max(0, start - 100):start].strip(),
                after=block.raw_text[end:end + 100].strip(),
            )
        )
    return occurrences


def safe_key(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "_", str(value).lower()).strip("_")
    return value or "campo_revision"


def human_label(key: str) -> str:
    words = key.split("_")
    return " ".join([words[0].capitalize()] + [word.lower() for word in words[1:]])
