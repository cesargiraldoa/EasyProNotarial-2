from __future__ import annotations

import hashlib
import unittest

from app.services.biblioteca_motor.anchor_resolver import resolve_anchors
from app.services.biblioteca_motor.comprehensive_extractor import (
    ComprehensiveBibliotecaExtractor,
    chunk_document_map,
)
from app.services.biblioteca_motor.document_map import DocumentMap, DocumentMapBlock
from app.services.biblioteca_motor.llm_extractor import (
    LLMExtraction,
    LLMExtractionAudit,
    LLMExtractionResult,
    LLMOccurrence,
)


def _block(index: int, text: str) -> DocumentMapBlock:
    return DocumentMapBlock(
        block_id=f"p_{index:04d}",
        block_type="paragraph",
        text=text,
        block_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        order=index,
        block_index=index,
        paragraph_index=index,
    )


def _map(*texts: str) -> DocumentMap:
    blocks = [_block(index, text) for index, text in enumerate(texts, start=1)]
    digest = hashlib.sha256("|".join(texts).encode("utf-8")).hexdigest()
    return DocumentMap(digest, blocks)


class _FakeChunkExtractor:
    model = "fake-model"
    prompt_version = "fake-v1"

    def __init__(self) -> None:
        self.calls: list[tuple[list[str], dict]] = []

    def extract(self, document_map, fields, *, active_profile=None, examples=None):
        profile = active_profile or {}
        self.calls.append(([block.block_id for block in document_map.blocks], profile))
        entities = []
        roles = []
        field_instances = []
        occurrences = []
        occurrence_counter = 0
        for block in document_map.blocks:
            cursor = 0
            local_index = 0
            while True:
                start = block.text.find("ANA LOPEZ", cursor)
                if start < 0:
                    break
                local_index += 1
                occurrence_counter += 1
                cursor = start + len("ANA LOPEZ")
                entities = [
                    {
                        "entity_ref": f"local_entity_{len(self.calls)}",
                        "entity_type": "natural_person",
                        "display_name": "ANA LOPEZ",
                        "document_number": "1.111.111",
                    },
                ]
                roles = [
                    {
                        "entity_ref": f"local_entity_{len(self.calls)}",
                        "role": "COMPRADOR",
                    },
                ]
                field_instances = [
                    {
                        "field_instance_ref": f"local_field_{len(self.calls)}",
                        "entity_ref": f"local_entity_{len(self.calls)}",
                        "role": "COMPRADOR",
                        "candidate_type": "person_name",
                        "base_field_code": "NOMBRE",
                        "suggested_field_code": "COMPRADOR_1",
                        "visible_code": "COMPRADOR_1",
                        "label": "Comprador 1",
                        "category": "persona",
                        "catalog_match": True,
                    },
                ]
                occurrences.append(
                    {
                        "occurrence_ref": f"local_occ_{len(self.calls)}_{occurrence_counter}",
                        "field_instance_ref": f"local_field_{len(self.calls)}",
                        "block_id": block.block_id,
                        "exact_text": "ANA LOPEZ",
                        "occurrence_index": local_index,
                        "left_context": block.text[max(0, start - 12) : start],
                        "right_context": block.text[start + len("ANA LOPEZ") : start + len("ANA LOPEZ") + 12],
                        "confidence": 0.95,
                    },
                )
        extraction = LLMExtraction.model_validate(
            {
                "document_type": "compraventa",
                "entities": entities,
                "roles": roles,
                "field_instances": field_instances,
                "occurrences": occurrences,
                "unmapped_fields": [],
                "confidence": 0.95,
                "reason": "fake",
                "diagnostics": {"call": len(self.calls)},
            },
        )
        return LLMExtractionResult(
            extraction=extraction,
            audit=LLMExtractionAudit(
                model=self.model,
                prompt_version=self.prompt_version,
                input_tokens=100,
                output_tokens=50,
                latency_ms=1,
            ),
        )

    def repair_occurrence(self, *, block_id, block_text, occurrence):
        return None


class _SparseRetryExtractor(_FakeChunkExtractor):
    def extract(self, document_map, fields, *, active_profile=None, examples=None):
        result = super().extract(
            document_map,
            fields,
            active_profile=active_profile,
            examples=examples,
        )
        contract = (active_profile or {}).get("runtime_extraction_contract") or {}
        if contract.get("mode") != "coverage_retry":
            extraction = result.extraction.model_copy(update={"occurrences": result.extraction.occurrences[:1]})
            return result.model_copy(update={"extraction": extraction})
        return result


class BibliotecaComprehensiveExtractorTests(unittest.TestCase):
    def test_chunk_document_map_covers_every_block(self):
        document_map = _map(*[(f"BLOQUE {index} " + ("x" * 850)) for index in range(1, 8)])

        chunks = chunk_document_map(document_map, max_chars=2000, long_block_overlap=100)
        covered = {block.block_id for chunk in chunks for block in chunk.document_map.blocks}

        self.assertGreater(len(chunks), 1)
        self.assertEqual(covered, {block.block_id for block in document_map.blocks})
        self.assertEqual(sum(len(chunk.document_map.blocks) for chunk in chunks), len(document_map.blocks))

    def test_merges_same_entity_and_field_across_chunks(self):
        document_map = _map(
            "COMPRADOR ANA LOPEZ " + ("a" * 1400),
            "FIRMA ANA LOPEZ " + ("b" * 1400),
        )
        inner = _FakeChunkExtractor()
        extractor = ComprehensiveBibliotecaExtractor(
            inner,
            chunk_chars=2000,
            max_workers=1,
            retry_sparse=False,
        )

        result = extractor.extract(document_map, [])

        self.assertEqual(len(inner.calls), 2)
        self.assertEqual(len(result.extraction.entities), 1)
        self.assertEqual(len(result.extraction.field_instances), 1)
        self.assertEqual(len(result.extraction.occurrences), 2)
        self.assertEqual(
            len({item.field_instance_ref for item in result.extraction.occurrences}),
            1,
        )
        self.assertEqual(result.audit.input_tokens, 200)
        self.assertEqual(result.audit.output_tokens, 100)

    def test_long_block_segments_preserve_global_occurrence_indexes(self):
        text = "ANA LOPEZ inicio " + ("x" * 2300) + " ANA LOPEZ final"
        document_map = _map(text)
        inner = _FakeChunkExtractor()
        extractor = ComprehensiveBibliotecaExtractor(
            inner,
            chunk_chars=2000,
            long_block_overlap=200,
            max_workers=1,
            retry_sparse=False,
        )

        result = extractor.extract(document_map, [])

        self.assertGreater(len(inner.calls), 1)
        self.assertEqual(
            {item.occurrence_index for item in result.extraction.occurrences},
            {1, 2},
        )
        self.assertEqual(len(result.extraction.occurrences), 2)

    def test_sparse_chunk_is_retried_and_keeps_better_coverage(self):
        document_map = _map(
            "ANA LOPEZ " + ("x" * 1250) + " ANA LOPEZ",
        )
        inner = _SparseRetryExtractor()
        extractor = ComprehensiveBibliotecaExtractor(
            inner,
            chunk_chars=2000,
            max_workers=1,
            retry_sparse=True,
        )

        result = extractor.extract(document_map, [])

        self.assertEqual(len(inner.calls), 2)
        self.assertEqual(len(result.extraction.occurrences), 2)
        self.assertEqual(
            inner.calls[1][1]["runtime_extraction_contract"]["mode"],
            "coverage_retry",
        )

    def test_single_literal_anchor_does_not_fail_for_imperfect_context(self):
        document_map = _map("COMPRADOR ANA LOPEZ identificada")
        occurrence = LLMOccurrence(
            occurrence_ref="occ_1",
            field_instance_ref="field_1",
            block_id="p_0001",
            exact_text="ANA LOPEZ",
            occurrence_index=1,
            left_context="contexto que no coincide",
            right_context="otro contexto",
            confidence=0.9,
        )

        resolved = resolve_anchors(document_map, [occurrence])

        self.assertEqual(len(resolved.anchored), 1)
        self.assertEqual(resolved.skipped, [])
        self.assertEqual(resolved.anchored[0].exact_text, "ANA LOPEZ")

    def test_repeated_literal_uses_context_to_select_correct_occurrence(self):
        document_map = _map("ANA LOPEZ representada por ANA LOPEZ firma")
        occurrence = LLMOccurrence(
            occurrence_ref="occ_2",
            field_instance_ref="field_1",
            block_id="p_0001",
            exact_text="ANA LOPEZ",
            occurrence_index=1,
            left_context="representada por ",
            right_context=" firma",
            confidence=0.9,
        )

        resolved = resolve_anchors(document_map, [occurrence])

        self.assertEqual(len(resolved.anchored), 1)
        self.assertEqual(resolved.anchored[0].location["occurrence_index"], 2)
        self.assertEqual(resolved.anchored[0].location["char_start"], 27)


if __name__ == "__main__":
    unittest.main()
