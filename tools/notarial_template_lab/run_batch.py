from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_PATH = REPO_ROOT / "backend"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from tools.notarial_template_lab.human_review_writer import write_human_review_html
from tools.notarial_template_lab.llm_client import JSONLLMClient
from tools.notarial_template_lab.prompt_contracts import DEFAULT_MAX_BLOCKS_PER_BATCH, DEFAULT_MAX_BLOCK_CHARS
from tools.notarial_template_lab.report_writer import safe_document_name, write_json
from tools.notarial_template_lab.run_lab import run_lab


DEFAULT_ARTIFACTS_ROOT = REPO_ROOT / "artifacts" / "notarial_template_lab"


def run_batch(
    input_dir: str | Path,
    artifacts_root: str | Path = DEFAULT_ARTIFACTS_ROOT,
    use_llm: bool = False,
    reuse_llm_artifacts: bool = False,
    llm_debug_payloads: bool = False,
    llm_max_blocks_per_batch: int = DEFAULT_MAX_BLOCKS_PER_BATCH,
    llm_max_block_chars: int = DEFAULT_MAX_BLOCK_CHARS,
    llm_client: JSONLLMClient | None = None,
) -> dict:
    source_dir = Path(input_dir)
    if not source_dir.exists() or not source_dir.is_dir():
        raise FileNotFoundError(f"No existe el directorio de entrada: {source_dir}")
    output_root = Path(artifacts_root)
    output_root.mkdir(parents=True, exist_ok=True)

    rows = []
    for source in sorted(source_dir.glob("*.docx")):
        row = process_document(
            source,
            output_root,
            use_llm=use_llm,
            reuse_llm_artifacts=reuse_llm_artifacts,
            llm_debug_payloads=llm_debug_payloads,
            llm_max_blocks_per_batch=llm_max_blocks_per_batch,
            llm_max_block_chars=llm_max_block_chars,
            llm_client=llm_client,
        )
        rows.append(row)

    summary = {
        "input_dir": str(source_dir),
        "artifacts_root": str(output_root),
        "total_documents": len(rows),
        "ok": len([row for row in rows if row["status"] == "ok"]),
        "error": len([row for row in rows if row["status"] == "error"]),
        "documents": rows,
    }
    write_json(output_root / "batch_summary.json", summary)
    (output_root / "batch_summary.html").write_text(render_batch_summary_html(summary), encoding="utf-8")
    return summary


def process_document(
    source: Path,
    artifacts_root: Path,
    use_llm: bool,
    reuse_llm_artifacts: bool,
    llm_debug_payloads: bool,
    llm_max_blocks_per_batch: int,
    llm_max_block_chars: int,
    llm_client: JSONLLMClient | None,
) -> dict:
    artifact_dir = artifacts_root / safe_document_name(source.stem)
    row = base_row(source, artifact_dir)
    try:
        result = run_lab(
            source,
            artifacts_root=artifacts_root,
            use_llm=use_llm,
            reuse_llm_artifacts=reuse_llm_artifacts,
            llm_debug_payloads=llm_debug_payloads,
            llm_max_blocks_per_batch=llm_max_blocks_per_batch,
            llm_max_block_chars=llm_max_block_chars,
            llm_client=llm_client,
        )
        artifact_dir = Path(result["artifacts_dir"])
        write_human_review_html(artifact_dir)
        row.update(success_row(source, artifact_dir, result))
        write_original_summary(artifact_dir, row)
    except Exception as exc:
        artifact_dir.mkdir(parents=True, exist_ok=True)
        row["status"] = "error"
        row["error"] = str(exc)
        row.update(artifact_stats(artifact_dir))
        write_human_review_html(artifact_dir)
        write_original_summary(artifact_dir, row)
    return row


def base_row(source: Path, artifact_dir: Path) -> dict:
    return {
        "filename": source.name,
        "artifact_dir": str(artifact_dir),
        "status": "pending",
        "error": "",
        "total_blocks": 0,
        "total_runs": 0,
        "total_llm_proposals": 0,
        "document_type": "",
        "recommended_mode": "",
        "acts_detected": [],
        "validation_status": "",
        "confirmed_validation_status": "",
        "confirmed_marked_fields": 0,
    }


def success_row(source: Path, artifact_dir: Path, result: dict) -> dict:
    stats = artifact_stats(artifact_dir)
    stats.update(
        {
            "filename": source.name,
            "artifact_dir": str(artifact_dir),
            "status": "ok",
            "error": "",
            "total_blocks": result.get("total_blocks", stats.get("total_blocks", 0)),
            "total_runs": result.get("total_runs", stats.get("total_runs", 0)),
            "total_llm_proposals": result.get("total_llm_proposals", stats.get("total_llm_proposals", 0)),
        }
    )
    return stats


def artifact_stats(artifact_dir: Path) -> dict:
    document_map = read_json(artifact_dir / "01_document_map.json", {})
    profile = read_json(artifact_dir / "02_document_profile.json", {})
    proposals = read_json(artifact_dir / "03_field_proposals_llm.json", [])
    validation = read_json(artifact_dir / "07_validation_report.json", {})
    confirmed_validation = read_json(artifact_dir / "10_confirmed_validation_report.json", {})
    quality = document_map.get("quality") if isinstance(document_map.get("quality"), dict) else {}
    return {
        "total_blocks": quality.get("total_blocks", 0),
        "total_runs": quality.get("total_runs", 0),
        "total_llm_proposals": len(proposals) if isinstance(proposals, list) else 0,
        "document_type": profile.get("document_type", ""),
        "recommended_mode": profile.get("recommended_mode", ""),
        "acts_detected": profile.get("acts_detected", []),
        "validation_status": pass_fail(validation.get("passed")),
        "confirmed_validation_status": pass_fail(confirmed_validation.get("passed")) if confirmed_validation else "",
        "confirmed_marked_fields": confirmed_validation.get("marked_fields_count", 0) if confirmed_validation else 0,
    }


def write_original_summary(artifact_dir: Path, row: dict) -> None:
    lines = [
        f"filename: {row.get('filename', '')}",
        f"artifact_dir: {row.get('artifact_dir', '')}",
        f"status: {row.get('status', '')}",
        f"error: {row.get('error', '')}",
        f"total_blocks: {row.get('total_blocks', 0)}",
        f"total_runs: {row.get('total_runs', 0)}",
        f"total_llm_proposals: {row.get('total_llm_proposals', 0)}",
        f"document_type: {row.get('document_type', '')}",
        f"recommended_mode: {row.get('recommended_mode', '')}",
        f"acts_detected: {', '.join(row.get('acts_detected') or [])}",
        f"validation_status: {row.get('validation_status', '')}",
        f"confirmed_validation_status: {row.get('confirmed_validation_status', '')}",
        f"confirmed_marked_fields: {row.get('confirmed_marked_fields', 0)}",
    ]
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "original_summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_batch_summary_html(summary: dict) -> str:
    rows = []
    for item in summary["documents"]:
        rows.append(
            "<tr>"
            f"<td>{esc(item.get('filename'))}</td>"
            f"<td>{esc(item.get('status'))}</td>"
            f"<td>{esc(item.get('error'))}</td>"
            f"<td><code>{esc(item.get('artifact_dir'))}</code></td>"
            f"<td>{esc(item.get('total_blocks'))}</td>"
            f"<td>{esc(item.get('total_runs'))}</td>"
            f"<td>{esc(item.get('total_llm_proposals'))}</td>"
            f"<td>{esc(item.get('document_type'))}</td>"
            f"<td>{esc(item.get('recommended_mode'))}</td>"
            f"<td>{esc(', '.join(item.get('acts_detected') or []))}</td>"
            f"<td>{esc(item.get('validation_status'))}</td>"
            f"<td>{esc(item.get('confirmed_validation_status'))}</td>"
            f"<td>{esc(item.get('confirmed_marked_fields'))}</td>"
            "</tr>"
        )
    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <title>Notarial Template Lab - Batch</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 28px; color: #172033; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 12px; }}
    th, td {{ border: 1px solid #d8e0ea; padding: 8px; vertical-align: top; }}
    th {{ background: #eef4fb; text-align: left; }}
    .ok {{ color: #047857; font-weight: 700; }}
    .error {{ color: #be123c; font-weight: 700; }}
  </style>
</head>
<body>
  <h1>Batch Notarial Template Lab</h1>
  <p>Input: <code>{esc(summary.get('input_dir'))}</code></p>
  <p>Artifacts: <code>{esc(summary.get('artifacts_root'))}</code></p>
  <p>Total: <strong>{summary.get('total_documents')}</strong> | OK: <strong>{summary.get('ok')}</strong> | Error: <strong>{summary.get('error')}</strong></p>
  <table>
    <thead><tr><th>filename</th><th>status</th><th>error</th><th>artifact_dir</th><th>blocks</th><th>runs</th><th>llm proposals</th><th>document_type</th><th>recommended_mode</th><th>acts_detected</th><th>validation</th><th>confirmed validation</th><th>confirmed fields</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
</body>
</html>"""


def pass_fail(value) -> str:
    if value is True:
        return "PASS"
    if value is False:
        return "FAIL"
    return ""


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value) -> str:
    return html.escape(str(value or ""))


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch universal del Notarial Template Lab.")
    parser.add_argument("--input-dir", required=True, help="Directorio con DOCX diligenciados.")
    parser.add_argument("--artifacts-root", default=str(DEFAULT_ARTIFACTS_ROOT))
    parser.add_argument("--use-llm", action="store_true")
    parser.add_argument("--reuse-llm-artifacts", action="store_true")
    parser.add_argument("--llm-debug-payloads", action="store_true")
    parser.add_argument("--llm-max-blocks-per-batch", type=int, default=DEFAULT_MAX_BLOCKS_PER_BATCH)
    parser.add_argument("--llm-max-block-chars", type=int, default=DEFAULT_MAX_BLOCK_CHARS)
    args = parser.parse_args()

    summary = run_batch(
        args.input_dir,
        artifacts_root=args.artifacts_root,
        use_llm=args.use_llm,
        reuse_llm_artifacts=args.reuse_llm_artifacts,
        llm_debug_payloads=args.llm_debug_payloads,
        llm_max_blocks_per_batch=args.llm_max_blocks_per_batch,
        llm_max_block_chars=args.llm_max_block_chars,
    )
    print(f"batch summary: {Path(args.artifacts_root) / 'batch_summary.json'}")
    print(f"batch summary html: {Path(args.artifacts_root) / 'batch_summary.html'}")
    print(f"documents: {summary['total_documents']} ok: {summary['ok']} error: {summary['error']}")
    return 0 if summary["error"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
