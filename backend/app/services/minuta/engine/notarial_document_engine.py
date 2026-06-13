from __future__ import annotations

from pathlib import Path
from typing import Any

from app.services.minuta.engine.context_builder import ContextBuilder
from app.services.minuta.engine.docx_renderer import DocxRenderer
from app.services.minuta.engine.models import NotarialRenderResult, RenderAudit, RenderIssue
from app.services.minuta.engine.quality_auditor import QualityAuditor
from app.services.minuta.engine.rule_engine import RuleEngine
from app.services.minuta.engine.template_analyzer import TemplateAnalyzer
from app.services.minuta.rules.common_rules import normalize_key, normalize_value


class NotarialRenderBlockedError(Exception):
    def __init__(self, issues: list[RenderIssue]):
        super().__init__("La plantilla no es compatible con los datos diligenciados.")
        self.issues = issues


class NotarialDocumentEngine:
    def __init__(self) -> None:
        self.analyzer = TemplateAnalyzer()
        self.context_builder = ContextBuilder()
        self.rule_engine = RuleEngine()
        self.renderer = DocxRenderer()
        self.auditor = QualityAuditor()

    def render_marked_template(
        self,
        source_path: str | Path,
        destination_path: str | Path,
        values: dict[str, Any],
        fields: list[dict] | None = None,
    ) -> NotarialRenderResult:
        fields_list = fields or []
        analysis = self.analyzer.analyze(source_path, fields_list)
        context = self.context_builder.build(values, fields_list)
        issues = self.rule_engine.pre_render_issues(analysis, context.normalized_values)
        blockers = [issue for issue in issues if issue.severity.value == "blocker"]
        if blockers:
            raise NotarialRenderBlockedError(issues)

        marker_values, marker_keys = self._marker_values(fields_list, context.normalized_values)
        issues.extend(self.rule_engine.required_value_issues(marker_values))

        audit = self.renderer.render(
            source_path=source_path,
            destination_path=destination_path,
            marker_values=marker_values,
            marker_keys=marker_keys,
            normalized_values=context.normalized_values,
        )
        audit.issues.extend(issues)
        audit = self.auditor.audit_post_render(destination_path, audit)
        post_blockers = [issue for issue in audit.issues if issue.severity.value == "blocker"]
        if post_blockers:
            raise NotarialRenderBlockedError(audit.issues)
        return NotarialRenderResult(
            output_path=Path(destination_path),
            audit=audit,
            statistics=self._statistics(audit),
        )

    def _marker_values(self, fields: list[dict], normalized_values: dict[str, str]) -> tuple[dict[str, str], dict[str, str | None]]:
        marker_values: dict[str, str] = {}
        marker_keys: dict[str, str | None] = {}
        for field in fields:
            if not isinstance(field, dict):
                continue
            key = str(field.get("key") or "").strip()
            normalized_key = normalize_key(key)
            value = normalize_value(normalized_values.get(normalized_key, ""))
            raw_markers = field.get("raw_markers") or []
            if not isinstance(raw_markers, list):
                continue
            for marker in raw_markers:
                marker_text = str(marker or "").strip()
                if not marker_text:
                    continue
                marker_values[marker_text] = value
                marker_keys[marker_text] = key
        return marker_values, marker_keys

    def _statistics(self, audit: RenderAudit) -> dict[str, Any]:
        return {
            "total_replacements": len(audit.replaced),
            "by_key": self._by_key(audit),
            "empty_count": len(audit.empty),
            "missing_count": len(audit.missing),
            "unresolved_placeholders_count": len(audit.unresolved_placeholders),
            "residual_tokens_count": len(audit.residual_tokens),
            "warnings_count": len(audit.warnings),
            "blockers_count": len(audit.blockers),
            "technical_tabs_resolved": audit.technical_tabs_resolved,
            "notarial_dash_sequences_preserved": audit.notarial_dash_sequences_preserved,
            "red_runs_detected": audit.red_runs_detected,
            "empty_signature_blocks_detected": audit.empty_signature_blocks_detected,
            "empty_signature_blocks_removed": audit.empty_signature_blocks_removed,
            "optional_segments_omitted": audit.optional_segments_omitted,
            "optional_segments_omitted_keys": audit.optional_segments_omitted_keys,
        }

    def _by_key(self, audit: RenderAudit) -> dict[str, int]:
        result: dict[str, int] = {}
        for item in audit.replaced:
            key = item.field_key or item.placeholder
            result[key] = result.get(key, 0) + 1
        return result
