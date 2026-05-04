from __future__ import annotations

import argparse
import json
import unicodedata
from collections import OrderedDict
from pathlib import Path


DEFAULT_INPUT = Path(r"C:\EasyPro_1\proyecto notarios\proyecto-notarios_07012026\easypro1_tablemaster_raw.sql")
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "frontend" / "lib" / "easypro1-notarial-catalogs.ts"


def parse_insert_tuples(sql_text: str) -> list[list[str | None]]:
    marker = "INSERT INTO `web_tablemaster` VALUES"
    start = sql_text.find(marker)
    if start < 0:
        raise ValueError("No se encontro el INSERT de web_tablemaster.")

    values_start = sql_text.find("(", start)
    values_end = sql_text.rfind(");")
    if values_start < 0 or values_end < 0 or values_end <= values_start:
        raise ValueError("No se pudieron ubicar los valores de web_tablemaster.")

    values_text = sql_text[values_start : values_end + 1]
    tuples: list[list[str | None]] = []

    depth = 0
    in_string = False
    current: list[str] = []
    field_buffer: list[str] = []

    i = 0
    while i < len(values_text):
        ch = values_text[i]

        if in_string:
            if ch == "'":
                if i + 1 < len(values_text) and values_text[i + 1] == "'":
                    field_buffer.append("'")
                    i += 2
                    continue
                in_string = False
                i += 1
                continue
            field_buffer.append(ch)
            i += 1
            continue

        if ch == "'":
            in_string = True
            i += 1
            continue

        if ch == "(":
            depth += 1
            if depth == 1:
                current = []
                field_buffer = []
            else:
                field_buffer.append(ch)
            i += 1
            continue

        if ch == ")":
            if depth == 1:
                current.append("".join(field_buffer).strip())
                tuples.append([None if value == "NULL" else value for value in current])
                current = []
                field_buffer = []
                depth -= 1
                i += 1
                continue
            if depth > 1:
                field_buffer.append(ch)
                depth -= 1
                i += 1
                continue
            i += 1
            continue

        if ch == "," and depth == 1:
            current.append("".join(field_buffer).strip())
            field_buffer = []
            i += 1
            continue

        if depth >= 1:
            field_buffer.append(ch)
        i += 1

    return tuples


def build_catalogs(rows: list[list[str | None]]) -> OrderedDict[str, list[str]]:
    catalogs: OrderedDict[str, list[str]] = OrderedDict()
    seen_values: dict[str, set[str]] = {}

    for row in rows:
        if len(row) < 6:
            continue
        table_name = (row[3] or "").strip()
        value = (row[4] or "").strip()
        status = (row[5] or "").strip()
        if not table_name or not value or status != "1":
            continue

        if table_name not in catalogs:
            catalogs[table_name] = []
            seen_values[table_name] = set()

        if value in seen_values[table_name]:
            continue

        catalogs[table_name].append(value)
        seen_values[table_name].add(value)

    return catalogs


def normalize_name(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value.strip().upper())
    return "".join(character for character in normalized if unicodedata.category(character) != "Mn")


def write_catalog_file(catalogs: OrderedDict[str, list[str]], output_path: Path) -> None:
    normalized_index: OrderedDict[str, list[str]] = OrderedDict()
    for table_name in catalogs.keys():
        normalized_key = normalize_name(table_name)
        normalized_index.setdefault(normalized_key, []).append(table_name)

    lines: list[str] = []
    lines.append("export type NotarialCatalogKey = string;")
    lines.append("")
    lines.append("export type NotarialCatalogOption = {")
    lines.append("  value: string;")
    lines.append("  label: string;")
    lines.append("};")
    lines.append("")
    lines.append("export const EASYPRO1_NOTARIAL_CATALOGS: Record<string, NotarialCatalogOption[]> = {")
    for table_name, values in catalogs.items():
        lines.append(f"  {json.dumps(table_name, ensure_ascii=False)}: [")
        for value in values:
            escaped = json.dumps(value, ensure_ascii=False)
            lines.append(f"    {{ value: {escaped}, label: {escaped} }},")
        lines.append("  ],")
    lines.append("};")
    lines.append("")
    lines.append("const EASYPRO1_NOTARIAL_CATALOG_INDEX: Record<string, string[]> = {")
    for normalized_key, table_names in normalized_index.items():
        serialized = ", ".join(json.dumps(name, ensure_ascii=False) for name in table_names)
        lines.append(f"  {json.dumps(normalized_key, ensure_ascii=False)}: [{serialized}],")
    lines.append("};")
    lines.append("")
    lines.append("function normalizeCatalogName(catalogName: string) {")
    lines.append("  return catalogName")
    lines.append("    .trim()")
    lines.append("    .toUpperCase()")
    lines.append("    .normalize(\"NFD\")")
    lines.append("    .replace(/[\\u0300-\\u036f]/g, \"\");")
    lines.append("}")
    lines.append("")
    lines.append("export function getEasyPro1CatalogOptions(catalogName: string): NotarialCatalogOption[] {")
    lines.append("  if (!catalogName) {")
    lines.append("    return [];")
    lines.append("  }")
    lines.append("")
    lines.append("  const exact = EASYPRO1_NOTARIAL_CATALOGS[catalogName];")
    lines.append("  if (exact) {")
    lines.append("    return exact;")
    lines.append("  }")
    lines.append("")
    lines.append("  const normalized = normalizeCatalogName(catalogName);")
    lines.append("  if (!normalized) {")
    lines.append("    return [];")
    lines.append("  }")
    lines.append("")
    lines.append("  const directMatch = Object.keys(EASYPRO1_NOTARIAL_CATALOGS).find((key) => normalizeCatalogName(key) === normalized);")
    lines.append("  if (directMatch) {")
    lines.append("    return EASYPRO1_NOTARIAL_CATALOGS[directMatch];")
    lines.append("  }")
    lines.append("")
    lines.append("  const catalogNames = EASYPRO1_NOTARIAL_CATALOG_INDEX[normalized];")
    lines.append("  if (!catalogNames?.length) {")
    lines.append("    return [];")
    lines.append("  }")
    lines.append("")
    lines.append("  const seen = new Set<string>();")
    lines.append("  const options: NotarialCatalogOption[] = [];")
    lines.append("  for (const name of catalogNames) {")
    lines.append("    for (const option of EASYPRO1_NOTARIAL_CATALOGS[name] ?? []) {")
    lines.append("      if (seen.has(option.value)) {")
    lines.append("        continue;")
    lines.append("      }")
    lines.append("      seen.add(option.value);")
    lines.append("      options.push(option);")
    lines.append("    }")
    lines.append("  }")
    lines.append("  return options;")
    lines.append("}")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Convierte web_tablemaster de EasyPro 1 en catalogos TS.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    sql_text = args.input.read_text(encoding="utf-8")
    rows = parse_insert_tuples(sql_text)
    catalogs = build_catalogs(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_catalog_file(catalogs, args.output)

    total_options = sum(len(values) for values in catalogs.values())
    print(f"Catalogos generados: {len(catalogs)}")
    print(f"Opciones generadas: {total_options}")
    print(f"Archivo escrito: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
