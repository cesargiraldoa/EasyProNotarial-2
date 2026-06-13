from __future__ import annotations

from app.services.minuta.engine.models import RenderIssue, RenderSeverity, TemplateAnalysis
from app.services.minuta.rules.compraventa_rules import validate_required_actors
from app.services.minuta.rules.gender_rules import validate_gender_concordance


class RuleEngine:
    def pre_render_issues(self, analysis: TemplateAnalysis, normalized_values: dict[str, str]) -> list[RenderIssue]:
        issues: list[RenderIssue] = []
        issues.extend(validate_required_actors(analysis.required_actor_roles, normalized_values))
        issues.extend(validate_gender_concordance(normalized_values))
        return issues

    def required_value_issues(self, marker_to_value: dict[str, str]) -> list[RenderIssue]:
        issues: list[RenderIssue] = []
        for marker, value in marker_to_value.items():
            if value.strip():
                continue
            issues.append(
                RenderIssue(
                    code="empty_replacement_value",
                    message=f"El marcador {marker} no tiene valor diligenciado.",
                    severity=RenderSeverity.WARNING,
                    placeholder=marker,
                )
            )
        return issues
