from __future__ import annotations

import html
import json
import re
from dataclasses import asdict
from pathlib import Path

from tools.notarial_template_lab.models import (
    DocumentMap,
    DocumentProfile,
    DraftResult,
    FieldProposal,
    HumanReviewResult,
    ValidationResult,
)


class ReportWriter:
    def write_all(
        self,
        source_docx: str | Path,
        document_map: DocumentMap,
        proposals: list[FieldProposal],
        draft_result: DraftResult,
        validation_result: ValidationResult,
        artifacts_root: str | Path = "artifacts/notarial_template_lab",
        document_profile: DocumentProfile | None = None,
        llm_proposals: list[FieldProposal] | None = None,
        human_review_result: HumanReviewResult | None = None,
        confirmed_draft_result: DraftResult | None = None,
        confirmed_validation_result: ValidationResult | None = None,
    ) -> Path:
        source_path = Path(source_docx)
        output_dir = Path(artifacts_root) / safe_document_name(source_path.stem)
        output_dir.mkdir(parents=True, exist_ok=True)

        write_json(output_dir / "01_document_map.json", document_map.to_dict())
        write_json(output_dir / "03_field_proposals.json", [asdict(proposal) for proposal in proposals])
        if document_profile is not None:
            write_json(output_dir / "02_document_profile.json", asdict(document_profile))
        if llm_proposals is not None:
            write_json(output_dir / "03_field_proposals_llm.json", [asdict(proposal) for proposal in llm_proposals])
        write_json(output_dir / "07_validation_report.json", asdict(validation_result))
        (output_dir / "05_review_report.html").write_text(
            self._html(
                document_map,
                proposals,
                draft_result,
                validation_result,
                document_profile,
                llm_proposals,
                human_review_result,
                confirmed_draft_result,
                confirmed_validation_result,
            ),
            encoding="utf-8",
        )
        return output_dir

    def _html(
        self,
        document_map: DocumentMap,
        proposals: list[FieldProposal],
        draft_result: DraftResult,
        validation_result: ValidationResult,
        document_profile: DocumentProfile | None = None,
        llm_proposals: list[FieldProposal] | None = None,
        human_review_result: HumanReviewResult | None = None,
        confirmed_draft_result: DraftResult | None = None,
        confirmed_validation_result: ValidationResult | None = None,
    ) -> str:
        occurrence_rows = []
        for occurrence_type, occurrences in document_map.occurrences_index.items():
            for occurrence in occurrences:
                occurrence_rows.append(
                    f"<tr><td>{esc(occurrence_type)}</td><td>{esc(occurrence.text)}</td><td>{esc(occurrence.location)}</td><td>{esc(occurrence.before)} <strong>{esc(occurrence.text)}</strong> {esc(occurrence.after)}</td></tr>"
                )

        proposal_rows = [
            "<tr>"
            f"<td>{esc(item.field_key)}</td>"
            f"<td>{esc(item.label)}</td>"
            f"<td>{esc(item.marker)}</td>"
            f"<td>{esc(item.value)}</td>"
            f"<td>{item.confidence:.2f}</td>"
            f"<td>{esc(item.proposal_type)}</td>"
            f"<td>{esc(item.apply_strategy)}</td>"
            f"<td>{len(item.occurrences)}</td>"
            f"<td>{esc(item.reason)}</td>"
            "</tr>"
            for item in proposals
        ]
        llm_proposal_rows = [
            "<tr>"
            f"<td>{esc(item.field_key)}</td>"
            f"<td>{esc(item.label)}</td>"
            f"<td>{esc(item.marker)}</td>"
            f"<td>{esc(item.value)}</td>"
            f"<td>{item.confidence:.2f}</td>"
            f"<td>{esc(item.proposal_type)}</td>"
            f"<td>{esc(item.role)}</td>"
            f"<td>{esc(item.scope)}</td>"
            f"<td>{esc(item.apply_strategy)}</td>"
            f"<td>{len(item.occurrences)}</td>"
            f"<td>{esc(item.reason)}</td>"
            "</tr>"
            for item in (llm_proposals or [])
        ]
        review_rows = [
            f"<li><strong>{esc(item.field_key)}</strong>: {esc(item.value)} — {esc(item.reason)}</li>"
            for item in proposals
            if item.proposal_type == "review_required" or item.apply_strategy == "review_required"
        ]
        skipped_rows = [
            f"<li><strong>{esc(item.get('field_key', ''))}</strong>: {esc(item.get('value', ''))} — {esc(item.get('reason', ''))}</li>"
            for item in draft_result.skipped
        ]
        block_rows = [
            "<tr>"
            f"<td>{esc(block.block_id)}</td>"
            f"<td>{esc(block.kind)}</td>"
            f"<td>{esc(block.location)}</td>"
            f"<td>{block.char_count}</td>"
            f"<td>{'si' if block.is_empty else 'no'}</td>"
            f"<td>{esc(block.raw_text[:300])}</td>"
            "</tr>"
            for block in document_map.blocks
        ]
        human_review_rows = [
            "<tr>"
            f"<td>{esc(item.field_key)}</td>"
            f"<td>{esc(item.value)}</td>"
            f"<td>{esc(item.original_marker)}</td>"
            f"<td>{esc(item.decision)}</td>"
            f"<td>{esc(item.final_marker)}</td>"
            f"<td>{'si' if item.replaceable else 'no'}</td>"
            f"<td>{esc(item.block_reason)}</td>"
            f"<td>{', '.join(esc(value) for value in item.selected_occurrence_ids)}</td>"
            "</tr>"
            for item in (human_review_result.applied_decisions if human_review_result else [])
        ]

        return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <title>Notarial Template Lab</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #10213f; }}
    h1, h2 {{ color: #0b2e63; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 28px; font-size: 12px; }}
    th, td {{ border: 1px solid #d9e2ef; padding: 8px; vertical-align: top; }}
    th {{ background: #eef4fb; text-align: left; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }}
    .card {{ background: #f5f8fc; border: 1px solid #d9e2ef; border-radius: 8px; padding: 12px; }}
    .ok {{ color: #047857; font-weight: 700; }}
    .fail {{ color: #be123c; font-weight: 700; }}
    code {{ background: #eef4fb; padding: 2px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>Notarial Template Lab</h1>
  <p>Documento: <strong>{esc(document_map.source_filename)}</strong></p>
  <div class="grid">
    <div class="card"><strong>{document_map.quality.total_blocks}</strong><br/>Bloques</div>
    <div class="card"><strong>{document_map.quality.total_runs}</strong><br/>Runs</div>
    <div class="card"><strong>{document_map.quality.total_occurrences}</strong><br/>Ocurrencias</div>
    <div class="card"><strong>{len(proposals)}</strong><br/>Propuestas</div>
  </div>

  <h2>Calidad</h2>
  <ul>{''.join(f'<li>{esc(warning)}</li>' for warning in document_map.quality.warnings) or '<li>Sin advertencias estructurales.</li>'}</ul>

  <h2>Perfil documental LLM</h2>
  {profile_html(document_profile)}

  <h2>DOCX experimental</h2>
  <p>Ruta: <code>{esc(draft_result.output_path)}</code></p>
  <p>Reemplazos aplicados: <strong>{len(draft_result.replacements)}</strong></p>
  <p>Validacion: <span class="{'ok' if validation_result.passed else 'fail'}">{'PASS' if validation_result.passed else 'FAIL'}</span></p>
  <p>Campos detectados por marked_template_detector: <strong>{validation_result.marked_fields_count}</strong></p>

  <h2>Plantilla confirmada por revision humana</h2>
  {confirmed_template_html(human_review_result, confirmed_draft_result, confirmed_validation_result)}

  <h2>Bloques</h2>
  <table><thead><tr><th>ID</th><th>Tipo</th><th>Ubicacion</th><th>Chars</th><th>Vacio</th><th>Texto</th></tr></thead><tbody>{''.join(block_rows)}</tbody></table>

  <h2>Ocurrencias tecnicas</h2>
  <table><thead><tr><th>Tipo</th><th>Texto</th><th>Ubicacion</th><th>Contexto</th></tr></thead><tbody>{''.join(occurrence_rows)}</tbody></table>

  <h2>Propuestas</h2>
  <table><thead><tr><th>Field key</th><th>Label</th><th>Marker</th><th>Valor</th><th>Conf.</th><th>Tipo</th><th>Estrategia</th><th>Ocurr.</th><th>Razon</th></tr></thead><tbody>{''.join(proposal_rows)}</tbody></table>

  <h2>Propuestas LLM</h2>
  <table><thead><tr><th>Field key</th><th>Label</th><th>Marker</th><th>Valor</th><th>Conf.</th><th>Tipo</th><th>Rol</th><th>Scope</th><th>Estrategia</th><th>Ocurr.</th><th>Razon</th></tr></thead><tbody>{''.join(llm_proposal_rows) or '<tr><td colspan="11">No se ejecuto la capa LLM.</td></tr>'}</tbody></table>

  <h2>Decisiones humanas aplicadas</h2>
  <table><thead><tr><th>Field key</th><th>Valor</th><th>Marcador original</th><th>Decision</th><th>Marcador final</th><th>Reemplazable</th><th>Motivo bloqueo</th><th>Ocurrencias</th></tr></thead><tbody>{''.join(human_review_rows) or '<tr><td colspan="8">No se cargo review-file.</td></tr>'}</tbody></table>

  <h2>Review required</h2>
  <ul>{''.join(review_rows) or '<li>No hay campos pendientes de revision.</li>'}</ul>

  <h2>Descartes / saltos del borrador</h2>
  <ul>{''.join(skipped_rows) or '<li>No hubo descartes.</li>'}</ul>

  <h2>Advertencias de validacion</h2>
  <ul>{''.join(f'<li>{esc(error)}</li>' for error in validation_result.errors) or '<li>Sin errores de validacion.</li>'}</ul>
</body>
</html>"""


def safe_document_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._-")
    return cleaned[:80] or "documento"


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def esc(value) -> str:
    return html.escape(str(value or ""))


def profile_html(profile: DocumentProfile | None) -> str:
    if profile is None:
        return "<p>No se ejecuto la capa LLM.</p>"
    evidence = "".join(
        f"<li>{esc(item.get('block_id'))} / {esc(item.get('location'))}: {esc(item.get('reason'))}</li>"
        for item in profile.evidence
        if isinstance(item, dict)
    )
    acts = ", ".join(profile.acts_detected) or "No determinados"
    risks = "".join(f"<li>{esc(item)}</li>" for item in profile.risk_notes) or "<li>Sin notas.</li>"
    return (
        f"<div class=\"card\"><p><strong>Tipo:</strong> {esc(profile.document_type)}</p>"
        f"<p><strong>Modo recomendado:</strong> {esc(profile.recommended_mode)}</p>"
        f"<p><strong>Confianza:</strong> {profile.confidence:.2f}</p>"
        f"<p><strong>Actos:</strong> {esc(acts)}</p>"
        f"<p><strong>Riesgos:</strong></p><ul>{risks}</ul>"
        f"<p><strong>Evidencia:</strong></p><ul>{evidence or '<li>Sin evidencia citada.</li>'}</ul></div>"
    )


def confirmed_template_html(
    human_review_result: HumanReviewResult | None,
    draft_result: DraftResult | None,
    validation_result: ValidationResult | None,
) -> str:
    if human_review_result is None:
        return "<p>No se cargo review-file; no se genero plantilla confirmada.</p>"
    output = esc(draft_result.output_path if draft_result else "")
    replacements = len(draft_result.replacements) if draft_result else 0
    validation = "PASS" if validation_result and validation_result.passed else "FAIL"
    fields = validation_result.marked_fields_count if validation_result else 0
    errors = "".join(f"<li>{esc(error)}</li>" for error in (validation_result.errors if validation_result else []))
    return (
        f"<p>Review file: <code>{esc(human_review_result.source_review_file)}</code></p>"
        f"<p>Ruta: <code>{output}</code></p>"
        f"<p>Reemplazos confirmados: <strong>{replacements}</strong></p>"
        f"<p>Validacion confirmada: <span class=\"{'ok' if validation == 'PASS' else 'fail'}\">{validation}</span></p>"
        f"<p>Campos detectados en confirmada: <strong>{fields}</strong></p>"
        f"<ul>{errors or '<li>Sin errores de validacion confirmada.</li>'}</ul>"
    )
