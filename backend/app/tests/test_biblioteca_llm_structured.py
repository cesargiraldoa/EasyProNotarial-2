from __future__ import annotations

from types import SimpleNamespace
import os
import unittest
from unittest.mock import patch

from app.services.biblioteca_motor.contracts import FieldDefinition
from app.services.biblioteca_motor.document_map import DocumentMap, DocumentMapBlock
from app.services.biblioteca_motor.llm_extractor import (
    LLMExtraction,
    LLMExtractorTruncated,
    OpenAIBibliotecaExtractor,
    PROMPT_VERSION,
)


def _document_map() -> DocumentMap:
    block = DocumentMapBlock(
        block_id="p_0001",
        block_type="paragraph",
        text="LOS COMPRADORES: DANIELA CAMPO.",
        block_hash="abc",
        order=1,
        block_index=1,
        paragraph_index=1,
    )
    return DocumentMap(document_sha256="doc-sha", blocks=[block])


def _extraction() -> LLMExtraction:
    return LLMExtraction.model_validate(
        {
            "document_type": "compraventa_simple",
            "entities": [
                {
                    "entity_ref": "ent_1",
                    "entity_type": "natural_person",
                    "display_name": "DANIELA CAMPO",
                    "attributes": {"source": "comparecencia"},
                }
            ],
            "roles": [{"entity_ref": "ent_1", "role": "COMPRADOR"}],
            "field_instances": [
                {
                    "field_instance_ref": "fi_1",
                    "entity_ref": "ent_1",
                    "role": "COMPRADOR",
                    "candidate_type": "person_name",
                    "base_field_code": "NOMBRE",
                    "suggested_field_code": "COMPRADOR_1",
                    "visible_code": "COMPRADOR_1",
                    "catalog_match": True,
                }
            ],
            "occurrences": [
                {
                    "occurrence_ref": "occ_1",
                    "field_instance_ref": "fi_1",
                    "block_id": "p_0001",
                    "exact_text": "DANIELA CAMPO",
                    "occurrence_index": 1,
                    "left_context": "LOS COMPRADORES: ",
                    "right_context": ".",
                    "confidence": 0.98,
                }
            ],
            "unmapped_fields": [],
            "confidence": 0.98,
            "diagnostics": {"coverage": "complete"},
        }
    )


class _FakeCompletions:
    def __init__(self, parsed, finish_reason="stop") -> None:
        self.parsed = parsed
        self.finish_reason = finish_reason
        self.calls = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    finish_reason=self.finish_reason,
                    message=SimpleNamespace(parsed=self.parsed),
                )
            ],
            usage=SimpleNamespace(prompt_tokens=100, completion_tokens=50),
        )


class _FakeOpenAI:
    def __init__(self, completions: _FakeCompletions) -> None:
        self.chat = SimpleNamespace(completions=completions)


class BibliotecaStructuredLLMTests(unittest.TestCase):
    def test_legacy_dict_metadata_is_normalized_to_strict_key_values(self):
        extraction = _extraction()

        self.assertEqual(extraction.entities[0].attributes[0].key, "source")
        self.assertEqual(extraction.diagnostics[0].key, "coverage")

    def test_provider_uses_pydantic_structured_output_and_full_document_map(self):
        completions = _FakeCompletions(_extraction())
        fake_client = _FakeOpenAI(completions)
        extractor = OpenAIBibliotecaExtractor("test-key")
        fields = [FieldDefinition("COMPRADOR_1", "Comprador 1", "persona")]

        with patch("openai.OpenAI", return_value=fake_client):
            result = extractor.extract(_document_map(), fields)

        self.assertEqual(result.extraction.document_type, "compraventa_simple")
        self.assertEqual(result.audit.prompt_version, PROMPT_VERSION)
        call = completions.calls[0]
        self.assertIs(call["response_format"], LLMExtraction)
        self.assertEqual(call["max_tokens"], 16384)
        self.assertIn("p_0001", call["messages"][1]["content"])
        self.assertIn("DANIELA CAMPO", call["messages"][1]["content"])

    def test_non_stop_finish_reason_is_reported_as_truncation(self):
        completions = _FakeCompletions(_extraction(), finish_reason="length")
        fake_client = _FakeOpenAI(completions)
        extractor = OpenAIBibliotecaExtractor("test-key")

        with patch("openai.OpenAI", return_value=fake_client):
            with self.assertRaises(LLMExtractorTruncated):
                extractor.extract(_document_map(), [])

    def test_api_key_can_be_resolved_from_supported_environment_alias(self):
        with patch.dict(os.environ, {"OPENAI_KEY": "alias-key"}, clear=True):
            extractor = OpenAIBibliotecaExtractor(None)

        self.assertEqual(extractor.api_key, "alias-key")


if __name__ == "__main__":
    unittest.main()
