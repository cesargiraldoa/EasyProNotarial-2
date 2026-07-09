from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_PATH = REPO_ROOT / "backend"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from tools.notarial_template_lab.docx_structural_extractor import DocxStructuralExtractor
from tools.notarial_template_lab.document_profiler_agent import DocumentProfilerAgent
from tools.notarial_template_lab.field_proposer import FieldProposer
from tools.notarial_template_lab.field_proposal_agent import FieldProposalAgent
from tools.notarial_template_lab.llm_client import JSONLLMClient, OpenAILLMClient
from tools.notarial_template_lab.human_review import apply_human_review, load_review_decisions
from tools.notarial_template_lab.models import DocumentProfile, FieldProposal, ProposalOccurrence
from tools.notarial_template_lab.prompt_contracts import (
    DEFAULT_MAX_BLOCKS,
    DEFAULT_MAX_BLOCKS_PER_BATCH,
    DEFAULT_MAX_BLOCK_CHARS,
    DEFAULT_SAFE_PAYLOAD_TOKENS,
    PayloadTooLargeError,
    write_debug_payload,
)
from tools.notarial_template_lab.report_writer import ReportWriter, safe_document_name, write_json
from tools.notarial_template_lab.roundtrip_validator import RoundtripValidator
from tools.notarial_template_lab.template_draft_writer import TemplateDraftWriter


class LabLLMExecutionError(RuntimeError):
    def __init__(self, message: str, artifacts_dir: Path):
        super().__init__(message)
        self.artifacts_dir = artifacts_dir


def run_lab(
    input_path: str | Path,
    artifacts_root: str | Path = REPO_ROOT / "artifacts" / "notarial_template_lab",
    use_llm: bool = False,
    llm_client: JSONLLMClient | None = None,
    review_file: str | Path | None = None,
    llm_max_blocks_per_batch: int = DEFAULT_MAX_BLOCKS_PER_BATCH,
    llm_max_block_chars: int = DEFAULT_MAX_BLOCK_CHARS,
    llm_debug_payloads: bool = False,
    llm_max_estimated_tokens: int = DEFAULT_SAFE_PAYLOAD_TOKENS,
    reuse_llm_artifacts: bool = False,
) -> dict:
    source = Path(input_path)
    if not source.exists():
        raise FileNotFoundError(f"No existe el archivo de entrada: {source}")
    if source.suffix.lower() != ".docx":
        raise ValueError("El archivo de entrada debe ser .docx")

    extractor = DocxStructuralExtractor()
    document_map = extractor.extract(source)
    proposals = FieldProposer().propose(document_map)

    output_dir = Path(artifacts_root) / safe_document_name(source.stem)
    output_dir.mkdir(parents=True, exist_ok=True)
    draft_path = output_dir / "06_template_draft.docx"
    draft_result = TemplateDraftWriter().write(source, draft_path, document_map, proposals)
    validation_result = RoundtripValidator().validate(draft_path)

    # ReportWriter owns the canonical JSON/HTML artifact names.
    report_writer = ReportWriter()
    artifacts_dir = report_writer.write_all(source, document_map, proposals, draft_result, validation_result, artifacts_root)
    # Keep draft result metadata available without adding a required named artifact.
    write_json(artifacts_dir / "04_draft_replacements.json", asdict(draft_result))
    cleanup_confirmed_artifacts(artifacts_dir)

    document_profile = None
    llm_proposals = None
    reused_llm_artifacts = False
    if reuse_llm_artifacts:
        try:
            document_profile, llm_proposals = load_existing_llm_artifacts(artifacts_dir)
            reused_llm_artifacts = True
            report_writer.write_all(
                source,
                document_map,
                proposals,
                draft_result,
                validation_result,
                artifacts_root,
                document_profile=document_profile,
                llm_proposals=llm_proposals,
            )
            write_json(artifacts_dir / "04_draft_replacements.json", asdict(draft_result))
        except FileNotFoundError as exc:
            raise LabLLMExecutionError(
                f"no existing LLM artifacts found in {artifacts_dir}. Detalle: {exc}",
                artifacts_dir,
            ) from exc
    elif use_llm:
        # The LLM layer consumes the persisted DocumentMap artifact as its contract input.
        document_map_path = artifacts_dir / "01_document_map.json"
        if not document_map_path.exists():
            raise LabLLMExecutionError(f"No existe {document_map_path}; no se puede ejecutar la capa LLM.", artifacts_dir)
        try:
            _ = json.loads(document_map_path.read_text(encoding="utf-8"))
            client = llm_client or OpenAILLMClient()
            profile_max_blocks = max(1, min(DEFAULT_MAX_BLOCKS, llm_max_blocks_per_batch * 3))
            profile_agent = DocumentProfilerAgent(client)
            profile_payload = profile_agent.build_payload(
                document_map,
                max_blocks=profile_max_blocks,
                max_block_chars=llm_max_block_chars,
            )
            if llm_debug_payloads:
                write_debug_payload(artifacts_dir / "02_llm_profile_payload.json", profile_payload)
            document_profile = profile_agent.run(
                document_map,
                max_blocks=profile_max_blocks,
                max_block_chars=llm_max_block_chars,
                max_estimated_tokens=llm_max_estimated_tokens,
            )
            field_agent = FieldProposalAgent(client)
            field_payloads = field_agent.build_payloads(
                document_map,
                document_profile,
                max_blocks_per_batch=llm_max_blocks_per_batch,
                max_block_chars=llm_max_block_chars,
            )
            if llm_debug_payloads:
                for index, payload in enumerate(field_payloads, start=1):
                    write_debug_payload(artifacts_dir / f"03_llm_field_payload_batch_{index:03d}.json", payload)
            llm_proposals = field_agent.run(
                document_map,
                document_profile,
                max_blocks_per_batch=llm_max_blocks_per_batch,
                max_block_chars=llm_max_block_chars,
                max_estimated_tokens=llm_max_estimated_tokens,
            )
            report_writer.write_all(
                source,
                document_map,
                proposals,
                draft_result,
                validation_result,
                artifacts_root,
                document_profile=document_profile,
                llm_proposals=llm_proposals,
            )
            write_json(artifacts_dir / "04_draft_replacements.json", asdict(draft_result))
        except PayloadTooLargeError as exc:
            raise LabLLMExecutionError(
                f"payload too large, reduce batch size. Artefactos base preservados en {artifacts_dir}. Detalle: {exc}",
                artifacts_dir,
            ) from exc
        except Exception as exc:
            raise LabLLMExecutionError(
                f"La capa LLM fallo de forma controlada. Artefactos base preservados en {artifacts_dir}. Detalle: {exc}",
                artifacts_dir,
            ) from exc

    human_review_result = None
    confirmed_draft_result = None
    confirmed_validation_result = None
    if review_file is not None:
        review_path = Path(review_file)
        decisions = load_review_decisions(review_path)
        review_source_proposals = llm_proposals if llm_proposals is not None else proposals
        human_review_result = apply_human_review(review_source_proposals, decisions, str(review_path))
        confirmed_path = artifacts_dir / "09_template_confirmed.docx"
        confirmed_draft_result = TemplateDraftWriter().write(
            source,
            confirmed_path,
            document_map,
            human_review_result.confirmed_proposals,
        )
        mark_human_review_applied(human_review_result, confirmed_draft_result)
        confirmed_validation_result = RoundtripValidator().validate(confirmed_path)
        write_json(artifacts_dir / "08_review_decisions_applied.json", asdict(human_review_result))
        write_json(artifacts_dir / "10_confirmed_validation_report.json", asdict(confirmed_validation_result))
        report_writer.write_all(
            source,
            document_map,
            proposals,
            draft_result,
            validation_result,
            artifacts_root,
            document_profile=document_profile,
            llm_proposals=llm_proposals,
            human_review_result=human_review_result,
            confirmed_draft_result=confirmed_draft_result,
            confirmed_validation_result=confirmed_validation_result,
        )
        write_json(artifacts_dir / "04_draft_replacements.json", asdict(draft_result))

    return {
        "artifacts_dir": str(artifacts_dir),
        "total_blocks": document_map.quality.total_blocks,
        "total_runs": document_map.quality.total_runs,
        "total_proposals": len(proposals),
        "total_llm_proposals": len(llm_proposals or []),
        "total_replacements": len(draft_result.replacements),
        "validation_passed": validation_result.passed,
        "marked_fields_count": validation_result.marked_fields_count,
        "marked_fields": validation_result.marked_fields,
        "used_llm": use_llm,
        "reused_llm_artifacts": reused_llm_artifacts,
        "review_file": str(review_file) if review_file is not None else None,
        "confirmed_replacements": len(confirmed_draft_result.replacements) if confirmed_draft_result else 0,
        "confirmed_validation_passed": confirmed_validation_result.passed if confirmed_validation_result else None,
        "confirmed_marked_fields_count": confirmed_validation_result.marked_fields_count if confirmed_validation_result else 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Sandbox de extraccion y construccion inversa de plantillas notariales.")
    parser.add_argument("--input", required=True, help="Ruta al DOCX diligenciado.")
    parser.add_argument("--artifacts-root", default=str(REPO_ROOT / "artifacts" / "notarial_template_lab"))
    parser.add_argument("--use-llm", action="store_true", help="Ejecuta DocumentProfilerAgent y FieldProposalAgent sobre 01_document_map.json.")
    parser.add_argument("--reuse-llm-artifacts", action="store_true", help="Carga 02/03 LLM existentes sin llamar API.")
    parser.add_argument("--review-file", help="JSON de decisiones humanas simuladas para generar 09_template_confirmed.docx.")
    parser.add_argument("--llm-max-blocks-per-batch", type=int, default=DEFAULT_MAX_BLOCKS_PER_BATCH)
    parser.add_argument("--llm-max-block-chars", type=int, default=DEFAULT_MAX_BLOCK_CHARS)
    parser.add_argument("--llm-debug-payloads", action="store_true", help="Guarda payloads compactos enviados a la capa LLM.")
    args = parser.parse_args()

    try:
        result = run_lab(
            args.input,
            args.artifacts_root,
            use_llm=args.use_llm,
            review_file=args.review_file,
            llm_max_blocks_per_batch=args.llm_max_blocks_per_batch,
            llm_max_block_chars=args.llm_max_block_chars,
            llm_debug_payloads=args.llm_debug_payloads,
            reuse_llm_artifacts=args.reuse_llm_artifacts,
        )
    except LabLLMExecutionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        print(f"artifacts: {exc.artifacts_dir}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"artifacts: {result['artifacts_dir']}")
    print(f"total blocks: {result['total_blocks']}")
    print(f"total runs: {result['total_runs']}")
    print(f"total proposals: {result['total_proposals']}")
    if result.get("used_llm") or result.get("reused_llm_artifacts"):
        print(f"total llm proposals: {result['total_llm_proposals']}")
    print(f"total replacements: {result['total_replacements']}")
    print(f"validation: {'PASS' if result['validation_passed'] else 'FAIL'}")
    print(f"marked fields detected: {result['marked_fields_count']}")
    if result.get("review_file"):
        print(f"confirmed replacements: {result['confirmed_replacements']}")
        print(f"confirmed validation: {'PASS' if result['confirmed_validation_passed'] else 'FAIL'}")
        print(f"confirmed marked fields detected: {result['confirmed_marked_fields_count']}")
    print(json.dumps(result["marked_fields"], ensure_ascii=False, indent=2))
    return 0 if result["validation_passed"] else 2


def cleanup_confirmed_artifacts(artifacts_dir: Path) -> None:
    for filename in (
        "08_review_decisions_applied.json",
        "09_template_confirmed.docx",
        "10_confirmed_validation_report.json",
    ):
        path = artifacts_dir / filename
        if path.exists():
            path.unlink()


def mark_human_review_applied(human_review_result, draft_result) -> None:
    replacement_counts: dict[tuple[str, str, str], int] = {}
    replacement_counts_by_field_marker: dict[tuple[str, str], int] = {}
    for replacement in draft_result.replacements:
        key = (replacement.field_key, replacement.value, replacement.marker)
        replacement_counts[key] = replacement_counts.get(key, 0) + 1
        field_marker_key = (replacement.field_key, replacement.marker)
        replacement_counts_by_field_marker[field_marker_key] = replacement_counts_by_field_marker.get(field_marker_key, 0) + 1

    skipped_by_key: dict[tuple[str, str, str], list[dict]] = {}
    skipped_by_field_marker: dict[tuple[str, str], list[dict]] = {}
    for item in draft_result.skipped:
        key = (str(item.get("field_key") or ""), str(item.get("value") or ""), str(item.get("marker") or ""))
        field_marker_key = (key[0], key[2])
        payload = failed_occurrence_payload(item)
        skipped_by_key.setdefault(key, []).append(payload)
        skipped_by_field_marker.setdefault(field_marker_key, []).append(payload)

    for decision in human_review_result.applied_decisions:
        decision.expected_count = len(decision.selected_occurrence_ids) if decision.selected_occurrence_ids else (1 if decision.replaceable else 0)
        if not decision.replaceable:
            decision.applied = False
            decision.applied_count = 0
            decision.partial = False
            continue
        key = (decision.field_key, decision.value, decision.final_marker)
        field_marker_key = (decision.field_key, decision.final_marker)
        applied_count = replacement_counts.get(key, replacement_counts_by_field_marker.get(field_marker_key, 0))
        decision.applied_count = applied_count
        decision.applied = applied_count >= decision.expected_count
        decision.partial = 0 < applied_count < decision.expected_count
        decision.failed_occurrences = skipped_by_key.get(key, skipped_by_field_marker.get(field_marker_key, []))
        if not decision.applied:
            decision.block_reason = first_failure_reason(decision.failed_occurrences) or "No matching writer result for confirmed occurrence."


def failed_occurrence_payload(item: dict) -> dict:
    return {
        "block_id": item.get("block_id") or "",
        "location": item.get("location") or "",
        "start": item.get("start"),
        "end": item.get("end"),
        "expected_value": item.get("expected_value") or item.get("value") or "",
        "marker": item.get("marker") or "",
        "failure_reason": item.get("failure_reason") or item.get("reason") or "",
    }


def first_failure_reason(failed_occurrences: list[dict]) -> str | None:
    for item in failed_occurrences:
        if item.get("failure_reason"):
            return str(item["failure_reason"])
    return None


def load_existing_llm_artifacts(artifacts_dir: Path) -> tuple[DocumentProfile, list[FieldProposal]]:
    profile_path = artifacts_dir / "02_document_profile.json"
    proposals_path = artifacts_dir / "03_field_proposals_llm.json"
    if not profile_path.exists() or not proposals_path.exists():
        missing = [str(path.name) for path in (profile_path, proposals_path) if not path.exists()]
        raise FileNotFoundError(", ".join(missing))
    profile = document_profile_from_dict(json.loads(profile_path.read_text(encoding="utf-8")))
    proposals = [
        field_proposal_from_dict(item)
        for item in json.loads(proposals_path.read_text(encoding="utf-8"))
        if isinstance(item, dict)
    ]
    return profile, proposals


def document_profile_from_dict(data: dict) -> DocumentProfile:
    return DocumentProfile(
        document_type=str(data.get("document_type") or "no_determinado"),
        recommended_mode=coerce_recommended_mode(data.get("recommended_mode")),
        acts_detected=string_list(data.get("acts_detected")),
        structural_sections=dict_list(data.get("structural_sections")),
        parties_summary=dict_list(data.get("parties_summary")),
        property_summary=data.get("property_summary") if isinstance(data.get("property_summary"), dict) else {},
        money_summary=dict_list(data.get("money_summary")),
        risk_notes=string_list(data.get("risk_notes")),
        confidence=coerce_float(data.get("confidence")),
        evidence=dict_list(data.get("evidence")),
    )


def field_proposal_from_dict(data: dict) -> FieldProposal:
    return FieldProposal(
        field_key=str(data.get("field_key") or "campo_revision"),
        label=str(data.get("label") or data.get("field_key") or "Campo revision"),
        marker=str(data.get("marker") or f"{{{{{data.get('field_key') or 'campo_revision'}}}}}"),
        value=str(data.get("value") or ""),
        confidence=coerce_float(data.get("confidence")),
        proposal_type=coerce_proposal_type(data.get("proposal_type")),  # type: ignore[arg-type]
        occurrences=[
            proposal_occurrence_from_dict(item)
            for item in data.get("occurrences", [])
            if isinstance(item, dict)
        ],
        apply_strategy=coerce_apply_strategy(data.get("apply_strategy")),  # type: ignore[arg-type]
        reason=str(data.get("reason") or ""),
        role=str(data.get("role")) if data.get("role") is not None else None,
        scope=str(data.get("scope")) if data.get("scope") is not None else None,
        evidence=string_list(data.get("evidence")),
    )


def proposal_occurrence_from_dict(data: dict) -> ProposalOccurrence:
    return ProposalOccurrence(
        occurrence_id=str(data.get("occurrence_id") or ""),
        block_id=str(data.get("block_id") or ""),
        location=str(data.get("location") or ""),
        text=str(data.get("text") or ""),
        start=coerce_int(data.get("start")),
        end=coerce_int(data.get("end")),
        before=str(data.get("before") or ""),
        after=str(data.get("after") or ""),
    )


def coerce_recommended_mode(value) -> str:
    mode = str(value or "no_determinado")
    if mode not in {"documento_individual", "proyecto_inmobiliario", "no_determinado"}:
        return "no_determinado"
    return mode


def coerce_proposal_type(value) -> str:
    proposal_type = str(value or "review_required")
    if proposal_type not in {"project_field", "document_field", "derived_field", "review_required", "fixed_text"}:
        return "review_required"
    return proposal_type


def coerce_apply_strategy(value) -> str:
    strategy = str(value or "review_required")
    if strategy not in {"all_occurrences", "selected_occurrences", "review_required"}:
        return "review_required"
    return strategy


def string_list(value) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if item is not None]


def dict_list(value) -> list[dict]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def coerce_float(value) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return min(1.0, max(0.0, number))


def coerce_int(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
