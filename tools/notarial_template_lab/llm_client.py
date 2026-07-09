from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Protocol


class LLMError(RuntimeError):
    pass


class LLMUnavailableError(LLMError):
    pass


class JSONLLMClient(Protocol):
    def complete_json(self, system_prompt: str, payload: dict) -> dict:
        ...


@dataclass
class OpenAILLMClient:
    model: str | None = None
    api_key: str | None = None

    def complete_json(self, system_prompt: str, payload: dict) -> dict:
        api_key = self.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise LLMUnavailableError("OPENAI_API_KEY no esta configurada; no se puede ejecutar --use-llm.")

        try:
            from openai import OpenAI
        except Exception as exc:
            raise LLMUnavailableError(f"No fue posible importar el cliente OpenAI: {exc}") from exc

        model = self.model or os.getenv("NOTARIAL_TEMPLATE_LAB_MODEL") or "gpt-4o-mini"
        try:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or "{}"
        except Exception as exc:
            raise LLMError(f"Fallo la llamada LLM: {exc}") from exc

        return parse_json_response(content)


def parse_json_response(content: str) -> dict:
    content = (content or "").strip()
    if not content:
        raise LLMError("El LLM devolvio una respuesta vacia.")
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise LLMError(f"El LLM no devolvio JSON valido: {exc}") from exc
    if not isinstance(parsed, dict):
        raise LLMError("El LLM debe devolver un objeto JSON en la raiz.")
    return parsed
