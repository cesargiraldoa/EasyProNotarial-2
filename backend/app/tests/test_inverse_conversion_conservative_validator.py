from __future__ import annotations

import unittest

from app.services.minuta.inverse_conversion_engine.conservative_validator import ConservativeCandidateValidator
from app.services.minuta.inverse_conversion_engine.llm_contracts import FieldProposal, FieldProposalEvidence


class ConservativeValidatorTests(unittest.TestCase):
    def proposal(self, candidate: str, canonical: str, score: float = 80, warnings: list[str] | None = None) -> FieldProposal:
        return FieldProposal(
            candidate_field_code=candidate,
            canonical_field_code=canonical,
            confidence_score=score,
            requires_human_review=False,
            warnings=warnings or [],
            evidence=[FieldProposalEvidence(evidence_type="fixture", score=score)],
        )

    def test_blocks_tipo_documento_vs_numero_documento(self):
        result = ConservativeCandidateValidator().validate(
            self.proposal("TIPO_DOCUMENTO_COMPRADOR", "NUMERO_DOCUMENTO_COMPRADOR")
        )
        self.assertEqual(result.status, "blocked")

    def test_blocks_dia_mes_ano_mixed(self):
        result = ConservativeCandidateValidator().validate(self.proposal("DIA_ESCRITURA", "MES_ESCRITURA"))
        self.assertEqual(result.status, "blocked")

    def test_blocks_comprador_ordinals(self):
        result = ConservativeCandidateValidator().validate(self.proposal("NOMBRE_COMPRADOR_1", "NOMBRE_COMPRADOR_2"))
        self.assertEqual(result.status, "blocked")

    def test_blocks_comprador_ordinal_to_base(self):
        result = ConservativeCandidateValidator().validate(self.proposal("NOMBRE_COMPRADOR_1", "NOMBRE_COMPRADOR"))
        self.assertEqual(result.status, "blocked")

    def test_blocks_numero_escritura_letras_vs_numeros(self):
        result = ConservativeCandidateValidator().validate(
            self.proposal("NUMERO_ESCRITURA_EN_LETRAS", "NUMERO_ESCRITURA_EN_NUMEROS")
        )
        self.assertEqual(result.status, "blocked")

    def test_proposal_without_evidence_requires_review(self):
        result = ConservativeCandidateValidator().validate(
            FieldProposal(candidate_field_code="VALOR_VENTA", canonical_field_code="VALOR_VENTA", confidence_score=80)
        )
        self.assertTrue(result.requires_human_review)
        self.assertIn("missing_evidence", "".join(result.warnings))

    def test_conflict_requires_review(self):
        result = ConservativeCandidateValidator().validate(
            self.proposal("CAMPO_CONFLICTO", "CAMPO_CONFLICTO", warnings=["conflict"])
        )
        self.assertEqual(result.status, "needs_human_review")

    def test_unknown_canonical_is_conflict(self):
        result = ConservativeCandidateValidator(known_field_codes={"VALOR_VENTA"}).validate(
            self.proposal("NUMERO_MATRICULA", "NUMERO_MATRICULA")
        )
        self.assertEqual(result.status, "conflict")


if __name__ == "__main__":
    unittest.main()
