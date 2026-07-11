from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol

from pydantic import BaseModel, Field, ValidationError

from app.core.config import get_settings


class IntelligenceMode(str, Enum):
    OFF = "off"
    SHADOW = "shadow"
    ASSIST = "assist"
    GATED = "gated"


class LLMFieldDecision(BaseModel):
    field_code: str
    label: str
    value: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_block_ids: list[int] = Field(default_factory=list)
    fixed_variable_label: str = "unknown"
    requires_human_review: bool = True
    reason: str


class LLMFieldProposal(BaseModel):
    suggested_field_code: str
    label: str
    reason: str
    evidence_block_ids: list[int] = Field(default_factory=list)


class LLMDocumentDecision(BaseModel):
    document_type: str | None = None
    document_subtype: str | None = None
    acts: list[str] = Field(default_factory=list)
    fields: list[LLMFieldDecision] = Field(default_factory=list)
    proposed_fields: list[LLMFieldProposal] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


@dataclass
class LLMAudit:
    mode: str
    provider: str
    model: str
    prompt_version: str
    latency_ms: int
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost_usd: float = 0.0
    retries: int = 0
    circuit_state: str = "closed"
    error: str | None = None


@dataclass
class LLMResult:
    decision: LLMDocumentDecision | None
    audit: LLMAudit
    raw_json: dict[str, Any] = field(default_factory=dict)


class LLMProvider(Protocol):
    provider_name: str
    model_name: str
    prompt_version: str

    def complete_json(self, system_prompt: str, payload: dict[str, Any], *, timeout_seconds: int) -> dict[str, Any]:
        ...


class CircuitOpenError(RuntimeError):
    pass


_SHARED_BREAKER_STATE: dict[str, dict[str, float]] = {}


class InMemoryCircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_seconds: int = 120) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_seconds = recovery_seconds
        self.failures = 0
        self.opened_at: float | None = None

    def before_call(self) -> None:
        if self.opened_at is None:
            return
        if time.time() - self.opened_at >= self.recovery_seconds:
            self.failures = 0
            self.opened_at = None
            return
        raise CircuitOpenError("LLM circuit breaker is open.")

    def record_success(self) -> None:
        self.failures = 0
        self.opened_at = None

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.opened_at = time.time()

    @property
    def state(self) -> str:
        return "open" if self.opened_at is not None else "closed"


class RedisCircuitBreaker(InMemoryCircuitBreaker):
    def __init__(self, name: str, failure_threshold: int = 3, recovery_seconds: int = 120) -> None:
        super().__init__(failure_threshold=failure_threshold, recovery_seconds=recovery_seconds)
        self.name = name
        self._client = None
        _SHARED_BREAKER_STATE.setdefault(self.name, {"failures": 0.0, "opened_at": 0.0})
        settings = get_settings()
        if settings.redis_url:
            try:
                from redis import Redis

                self._client = Redis.from_url(settings.redis_url, socket_timeout=2, socket_connect_timeout=2)
            except Exception:
                self._client = None

    @property
    def _failures_key(self) -> str:
        return f"easypro2:circuit:{self.name}:failures"

    @property
    def _opened_key(self) -> str:
        return f"easypro2:circuit:{self.name}:opened_at"

    def before_call(self) -> None:
        if self._client is None:
            state = _SHARED_BREAKER_STATE[self.name]
            opened_at = state.get("opened_at") or 0.0
            if not opened_at:
                return
            if time.time() - opened_at >= self.recovery_seconds:
                state["failures"] = 0.0
                state["opened_at"] = 0.0
                return
            raise CircuitOpenError("LLM circuit breaker is open.")
        opened = self._client.get(self._opened_key)
        if not opened:
            return
        opened_at = float(opened)
        if time.time() - opened_at >= self.recovery_seconds:
            self._client.delete(self._opened_key, self._failures_key)
            return
        raise CircuitOpenError("LLM circuit breaker is open.")

    def record_success(self) -> None:
        if self._client is None:
            state = _SHARED_BREAKER_STATE[self.name]
            state["failures"] = 0.0
            state["opened_at"] = 0.0
            return
        self._client.delete(self._opened_key, self._failures_key)

    def record_failure(self) -> None:
        if self._client is None:
            state = _SHARED_BREAKER_STATE[self.name]
            state["failures"] = state.get("failures", 0.0) + 1
            if state["failures"] >= self.failure_threshold:
                state["opened_at"] = time.time()
            return
        failures = int(self._client.incr(self._failures_key))
        self._client.expire(self._failures_key, self.recovery_seconds)
        if failures >= self.failure_threshold:
            self._client.set(self._opened_key, time.time(), ex=self.recovery_seconds)

    @property
    def state(self) -> str:
        if self._client is None:
            return "open" if _SHARED_BREAKER_STATE[self.name].get("opened_at") else "closed"
        return "open" if self._client.get(self._opened_key) else "closed"


class OpenAINotarialLLMProvider:
    provider_name = "openai"
    prompt_version = "notarial-intelligence-v1"

    def __init__(self, model_name: str = "gpt-4o-mini") -> None:
        self.model_name = model_name

    def complete_json(self, system_prompt: str, payload: dict[str, Any], *, timeout_seconds: int) -> dict[str, Any]:
        settings = get_settings()
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for LLM modes shadow, assist or gated.")
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key, timeout=timeout_seconds)
        response = client.chat.completions.create(
            model=self.model_name,
            temperature=0.0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
        )
        content = response.choices[0].message.content or "{}"
        parsed = json.loads(content)
        usage = getattr(response, "usage", None)
        if usage is not None:
            parsed["_usage"] = {
                "input_tokens": int(getattr(usage, "prompt_tokens", 0) or 0),
                "output_tokens": int(getattr(usage, "completion_tokens", 0) or 0),
            }
        return parsed


class NotarialLLMService:
    def __init__(
        self,
        provider: LLMProvider | None = None,
        circuit_breaker: InMemoryCircuitBreaker | None = None,
        *,
        timeout_seconds: int = 45,
        max_retries: int = 2,
        max_input_chars: int = 16000,
        max_estimated_cost_usd: float = 0.25,
    ) -> None:
        self.provider = provider or OpenAINotarialLLMProvider()
        self.circuit_breaker = circuit_breaker or RedisCircuitBreaker(f"{self.provider.provider_name}:{self.provider.model_name}")
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.max_input_chars = max_input_chars
        self.max_estimated_cost_usd = max_estimated_cost_usd

    def analyze(
        self,
        payload: dict[str, Any],
        mode: IntelligenceMode,
        *,
        allowed_field_codes: set[str] | None = None,
        allowed_evidence_block_ids: set[int] | None = None,
    ) -> LLMResult:
        started = time.perf_counter()
        if mode == IntelligenceMode.OFF:
            return LLMResult(None, self._audit(mode, started, error="llm_disabled"))
        payload = _trim_payload(payload, self.max_input_chars)
        payload_size = len(json.dumps(payload, ensure_ascii=False))
        estimated_cost = _estimate_cost(payload_size)
        if payload_size > self.max_input_chars or estimated_cost > self.max_estimated_cost_usd:
            return LLMResult(None, self._audit(mode, started, estimated_cost_usd=estimated_cost, error="llm_budget_exceeded"))

        retries = 0
        last_error: str | None = None
        for attempt in range(self.max_retries + 1):
            retries = attempt
            try:
                self.circuit_breaker.before_call()
                raw = self.provider.complete_json(_system_prompt(self.provider.prompt_version), payload, timeout_seconds=self.timeout_seconds)
                usage = raw.pop("_usage", {}) if isinstance(raw, dict) else {}
                decision = LLMDocumentDecision.model_validate(raw)
                validation_error = _validate_decision(decision, allowed_field_codes or set(), allowed_evidence_block_ids or set())
                if validation_error:
                    raise RuntimeError(validation_error)
                self.circuit_breaker.record_success()
                return LLMResult(
                    decision=decision,
                    audit=self._audit(
                        mode,
                        started,
                        input_tokens=int(usage.get("input_tokens") or _estimate_tokens(payload_size)),
                        output_tokens=int(usage.get("output_tokens") or 0),
                        estimated_cost_usd=estimated_cost,
                        retries=retries,
                    ),
                    raw_json=raw,
                )
            except _openai_transient_errors() as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                self.circuit_breaker.record_failure()
                if attempt >= self.max_retries:
                    break
                time.sleep(min(2 ** attempt, 4))
            except CircuitOpenError as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                break
            except (RuntimeError, ValidationError, json.JSONDecodeError) as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                self.circuit_breaker.record_failure()
                break
        return LLMResult(None, self._audit(mode, started, estimated_cost_usd=estimated_cost, retries=retries, error=last_error))

    def _audit(
        self,
        mode: IntelligenceMode,
        started: float,
        *,
        input_tokens: int = 0,
        output_tokens: int = 0,
        estimated_cost_usd: float = 0.0,
        retries: int = 0,
        error: str | None = None,
    ) -> LLMAudit:
        return LLMAudit(
            mode=mode.value,
            provider=self.provider.provider_name,
            model=self.provider.model_name,
            prompt_version=self.provider.prompt_version,
            latency_ms=int((time.perf_counter() - started) * 1000),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost_usd=estimated_cost_usd,
            retries=retries,
            circuit_state=self.circuit_breaker.state,
            error=error,
        )


def _system_prompt(prompt_version: str) -> str:
    return (
        f"Prompt {prompt_version}. Devuelve exclusivamente JSON valido para decisiones notariales. "
        "Usa solo codigos canonicos permitidos, no redactes DOCX y usa solo evidence_block_ids enviados. "
        "Marca requires_human_review=true ante incertidumbre."
    )


def _estimate_tokens(chars: int) -> int:
    return max(1, chars // 4)


def _estimate_cost(chars: int) -> float:
    return (_estimate_tokens(chars) / 1000.0) * 0.0006


def _openai_transient_errors() -> tuple[type[BaseException], ...]:
    errors: list[type[BaseException]] = [TimeoutError, ConnectionError]
    try:
        from openai import APIConnectionError, APITimeoutError, RateLimitError, InternalServerError

        errors.extend([APIConnectionError, APITimeoutError, RateLimitError, InternalServerError])
    except Exception:
        pass
    return tuple(errors)


def _validate_decision(decision: LLMDocumentDecision, allowed_field_codes: set[str], allowed_evidence_block_ids: set[int]) -> str | None:
    if allowed_field_codes:
        invalid_codes = sorted({field.field_code for field in decision.fields if field.field_code not in allowed_field_codes})
        if invalid_codes:
            return f"invalid_field_code: {', '.join(invalid_codes)}"
    if allowed_evidence_block_ids:
        invalid_evidence = sorted(
            {
                block_id
                for field in decision.fields
                for block_id in field.evidence_block_ids
                if block_id not in allowed_evidence_block_ids
            }
        )
        if invalid_evidence:
            return f"invalid_evidence_block_ids: {invalid_evidence}"
    return None


def _trim_payload(payload: dict[str, Any], max_chars: int) -> dict[str, Any]:
    encoded = json.dumps(payload, ensure_ascii=False)
    if len(encoded) <= max_chars:
        return payload
    trimmed = dict(payload)
    evidence = list(trimmed.get("evidence") or [])
    rag = list(trimmed.get("rag") or [])
    while len(json.dumps(trimmed, ensure_ascii=False)) > max_chars and (evidence or rag):
        if len(evidence) >= len(rag) and evidence:
            evidence.pop()
        elif rag:
            rag.pop()
        trimmed["evidence"] = evidence
        trimmed["rag"] = rag
    return trimmed
