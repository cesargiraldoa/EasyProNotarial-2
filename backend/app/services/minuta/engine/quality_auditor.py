from __future__ import annotations

from pathlib import Path

from docx import Document

from app.services.minuta.engine.models import RenderAudit, RenderIssue, RenderSeverity
from app.services.minuta.engine.template_analyzer import RESIDUAL_TOKEN_PATTERN, TemplateAnalyzer, iter_document_paragraphs


class QualityAuditor:
    def audit_post_render(self, output_path: str | Path, audit: RenderAudit) -> RenderAudit:
        analysis = TemplateAnalyzer().analyze(output_path)
        audit.unresolved_placeholders = analysis.unresolved_placeholders
        audit.residual_tokens = sorted(set(analysis.residual_tokens))

        for placeholder in audit.unresolved_placeholders:
            audit.issues.append(
                RenderIssue(
                    code="unresolved_placeholder",
                    message=f"Quedó placeholder sin resolver: {placeholder}",
                    severity=RenderSeverity.BLOCKER,
                    placeholder=placeholder,
                )
            )

        for token in audit.residual_tokens:
            audit.issues.append(
                RenderIssue(
                    code="residual_token",
                    message=f"Quedó token residual: {token}",
                    severity=RenderSeverity.BLOCKER,
                    details={"token": token},
                )
            )

        self._verify_red_replacements(output_path, audit)
        self._verify_structure(audit)
        return audit

    def _verify_red_replacements(self, output_path: str | Path, audit: RenderAudit) -> None:
        document = Document(str(output_path))
        red_values = {
            item.inserted_value
            for item in audit.replaced
            if item.inserted_value
        }
        if not red_values:
            return

        found_red: set[str] = set()
        red_runs_detected = 0
        for paragraph, _location in iter_document_paragraphs(document):
            for run in paragraph.runs:
                if run.font.color.rgb and str(run.font.color.rgb).upper() == "FF0000" and run.text.strip():
                    red_runs_detected += 1
                    if run.text in red_values:
                        found_red.add(run.text)
        audit.red_runs_detected = red_runs_detected

        for item in audit.replaced:
            if not item.inserted_value:
                continue
            if item.inserted_value in found_red:
                continue
            audit.issues.append(
                RenderIssue(
                    code="replacement_not_red",
                    message=f"El valor insertado no quedó en rojo: {item.placeholder}",
                    severity=RenderSeverity.ERROR,
                    placeholder=item.placeholder,
                    field_key=item.field_key,
                    location=item.location,
                )
            )

    def _verify_structure(self, audit: RenderAudit) -> None:
        before = audit.structure_before
        after = audit.structure_after
        if not before or not after:
            return
        if after.get("paragraphs", 0) < max(1, before.get("paragraphs", 0) // 2):
            audit.issues.append(
                RenderIssue(
                    code="structure_changed_too_much",
                    message="El documento generado perdió demasiados párrafos frente al modelo.",
                    severity=RenderSeverity.WARNING,
                    details={"before": before, "after": after},
                )
            )
        if after.get("dash_sequences", 0) < before.get("dash_sequences", 0):
            audit.issues.append(
                RenderIssue(
                    code="notarial_dash_sequences_lost",
                    message="El documento generado perdiÃ³ secuencias de guiones notariales frente al modelo.",
                    severity=RenderSeverity.WARNING,
                    details={"before": before, "after": after},
                )
            )
