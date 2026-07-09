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
    if use_llm:
        # The LLM layer consumes the persisted DocumentMap artifact as its contract input.
        document_map_path = artifacts_dir / "01_document_map.json"
        if not document_map_path.exists():
            raise LabLLMExecutionError(f"No existe {document_map_path}; no se puede ejecutar la capa LLM.", artifacts_dir)
        try:
            _ = json.loads(document_map_path.read_text(encoding="utf-8"))
            client = llm_client or OpenAILLMClient()
            document_profile = DocumentProfilerAgent(client).run(document_map)
            llm_proposals = FieldProposalAgent(client).run(document_map, document_profile)
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
    parser.add_argument("--review-file", help="JSON de decisiones humanas simuladas para generar 09_template_confirmed.docx.")
    args = parser.parse_args()

    try:
        result = run_lab(args.input, args.artifacts_root, use_llm=args.use_llm, review_file=args.review_file)
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
    if result.get("used_llm"):
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


if __name__ == "__main__":
    raise SystemExit(main())
