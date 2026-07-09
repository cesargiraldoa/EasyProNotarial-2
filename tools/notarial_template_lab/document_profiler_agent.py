from __future__ import annotations

from tools.notarial_template_lab.llm_client import JSONLLMClient
from tools.notarial_template_lab.models import DocumentMap, DocumentProfile
from tools.notarial_template_lab.prompt_contracts import (
    DEFAULT_MAX_BLOCK_CHARS,
    DEFAULT_MAX_BLOCKS,
    DEFAULT_SAFE_PAYLOAD_TOKENS,
    DOCUMENT_PROFILER_SYSTEM_PROMPT,
    assert_payload_within_limit,
    build_profile_payload,
)


class DocumentProfilerAgent:
    def __init__(self, llm_client: JSONLLMClient):
        self.llm_client = llm_client

    def build_payload(
        self,
        document_map: DocumentMap,
        max_blocks: int = DEFAULT_MAX_BLOCKS,
        max_block_chars: int = DEFAULT_MAX_BLOCK_CHARS,
    ) -> dict:
        return build_profile_payload(document_map, max_blocks=max_blocks, max_block_chars=max_block_chars)

    def run(
        self,
        document_map: DocumentMap,
        max_blocks: int = DEFAULT_MAX_BLOCKS,
        max_block_chars: int = DEFAULT_MAX_BLOCK_CHARS,
        max_estimated_tokens: int = DEFAULT_SAFE_PAYLOAD_TOKENS,
    ) -> DocumentProfile:
        payload = self.build_payload(document_map, max_blocks=max_blocks, max_block_chars=max_block_chars)
        assert_payload_within_limit(payload, max_estimated_tokens, "profile")
        raw = self.llm_client.complete_json(DOCUMENT_PROFILER_SYSTEM_PROMPT, payload)
        return normalize_document_profile(raw)


def normalize_document_profile(raw: dict) -> DocumentProfile:
    mode = str(raw.get("recommended_mode") or "no_determinado")
    if mode not in {"documento_individual", "proyecto_inmobiliario", "no_determinado"}:
        mode = "no_determinado"
    return DocumentProfile(
        document_type=str(raw.get("document_type") or "no_determinado"),
        recommended_mode=mode,  # type: ignore[arg-type]
        acts_detected=string_list(raw.get("acts_detected")),
        structural_sections=dict_list(raw.get("structural_sections")),
        parties_summary=dict_list(raw.get("parties_summary")),
        property_summary=raw.get("property_summary") if isinstance(raw.get("property_summary"), dict) else {},
        money_summary=dict_list(raw.get("money_summary")),
        risk_notes=string_list(raw.get("risk_notes")),
        confidence=clamp_float(raw.get("confidence"), default=0.0),
        evidence=dict_list(raw.get("evidence")),
    )


def string_list(value) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if item is not None]


def dict_list(value) -> list[dict]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def clamp_float(value, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return min(1.0, max(0.0, number))
