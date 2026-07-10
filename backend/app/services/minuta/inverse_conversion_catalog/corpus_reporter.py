from __future__ import annotations

import csv
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Iterable

from app.services.minuta.inverse_conversion_catalog.models import ImportResult


class CorpusReporter:
    """Write human-reviewable JSON and CSV reports for corpus import/catalog work."""

    def write_import_reports(self, result: ImportResult, output_dir: str | Path) -> dict[str, Path]:
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)

        summary_rows = [self._summary(result)]
        field_frequency_rows = [
            {"raw_field_code": code, "frequency": frequency}
            for code, frequency in sorted(result.field_frequency.items(), key=lambda item: (-item[1], item[0]))
        ]
        alias_rows = [self._row(alias) for alias in result.aliases]
        pattern_rows = [self._pattern_row(pattern) for pattern in result.patterns]
        error_rows = result.errors

        written: dict[str, Path] = {}
        written.update(self._write_pair(output, "import_summary", summary_rows))
        written.update(self._write_pair(output, "field_frequency", field_frequency_rows))
        written.update(self._write_pair(output, "field_aliases_suggested", alias_rows))
        written.update(self._write_pair(output, "field_patterns", pattern_rows))
        written.update(self._write_pair(output, "import_errors", error_rows))
        return written

    def write_catalog_report(self, payload: dict[str, Any], output_dir: str | Path, stem: str = "field_catalog_report") -> dict[str, Path]:
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        rows = self._flatten_catalog_payload(payload)
        return self._write_pair(output, stem, rows)

    def _write_pair(self, output: Path, stem: str, rows: list[dict[str, Any]]) -> dict[str, Path]:
        json_path = output / f"{stem}.json"
        csv_path = output / f"{stem}.csv"
        json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        self._write_csv(csv_path, rows)
        return {f"{stem}.json": json_path, f"{stem}.csv": csv_path}

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        fieldnames = sorted({key for row in rows for key in row.keys()})
        if not fieldnames:
            fieldnames = ["empty"]
            rows = [{"empty": ""}]
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({key: CorpusReporter._csv_value(row.get(key)) for key in fieldnames})

    @staticmethod
    def _summary(result: ImportResult) -> dict[str, Any]:
        total_documents = len(result.documents)
        return {
            "total_documents": total_documents,
            "total_documents_processed": result.processed_count,
            "total_documents_with_error": result.error_count,
            "total_documents_tagged": sum(1 for document in result.documents if document.is_tagged),
            "total_unique_fields": len(result.field_frequency),
            "total_suggested_normalized_fields": len({alias.canonical_field_code for alias in result.aliases}),
            "total_patterns": len(result.patterns),
            "top_fields_by_frequency": json.dumps(
                sorted(result.field_frequency.items(), key=lambda item: (-item[1], item[0]))[:20],
                ensure_ascii=False,
            ),
        }

    @staticmethod
    def _pattern_row(pattern) -> dict[str, Any]:
        row = CorpusReporter._row(pattern)
        row["location"] = pattern.location.label()
        row.pop("location", None)
        return {
            "raw_field_code": pattern.raw_field_code,
            "canonical_field_code": pattern.canonical_field_code,
            "text_before": pattern.text_before,
            "text_after": pattern.text_after,
            "location": pattern.location.label(),
            "confidence": pattern.confidence,
            "pattern_source_file": pattern.pattern_source_file,
        }

    @staticmethod
    def _row(value: Any) -> dict[str, Any]:
        if is_dataclass(value):
            data = asdict(value)
        elif isinstance(value, dict):
            data = dict(value)
        else:
            data = {"value": value}
        return {key: CorpusReporter._json_safe(item) for key, item in data.items()}

    @staticmethod
    def _json_safe(value: Any) -> Any:
        if is_dataclass(value):
            return asdict(value)
        if isinstance(value, tuple):
            return list(value)
        if isinstance(value, Path):
            return str(value)
        return value

    @staticmethod
    def _csv_value(value: Any) -> Any:
        if isinstance(value, (dict, list, tuple)):
            return json.dumps(value, ensure_ascii=False)
        return "" if value is None else value

    @staticmethod
    def _flatten_catalog_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for section, items in payload.items():
            if not isinstance(items, Iterable) or isinstance(items, (str, bytes, dict)):
                rows.append({"section": section, "value": items})
                continue
            for item in items:
                row = CorpusReporter._row(item)
                row["section"] = section
                rows.append(row)
        return rows
