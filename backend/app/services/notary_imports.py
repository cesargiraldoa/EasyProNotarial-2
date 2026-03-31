from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

DEFAULT_ANTIOQUIA_SOURCE_PATH = Path(r"C:\EasyProNotarial-2\Archivos_referencia\Notarias_Antioquia_EasyProNotarial.xlsx")
REQUIRED_COLUMNS = [
    "MUNICIPIO",
    "NOTARÍA",
    "DIRECCIÓN",
    "TELÉFONO",
    "CORREO ELECTRÓNICO",
    "NOTARIO/A",
    "HORARIO",
]

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


@dataclass
class WorkbookSheetData:
    sheet_name: str
    rows: list[dict[str, str]]


class NotaryImportFileError(ValueError):
    pass


def validate_source_file(source_path: str | Path) -> Path:
    path = Path(source_path)
    if not path.exists():
        raise NotaryImportFileError(f"Archivo no encontrado: {path}")
    if path.suffix.lower() != ".xlsx":
        raise NotaryImportFileError("El archivo de importación debe ser .xlsx")
    return path


def _read_shared_strings(workbook: ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in workbook.namelist():
        return []
    root = ET.fromstring(workbook.read("xl/sharedStrings.xml"))
    strings: list[str] = []
    for item in root.findall(f"{{{MAIN_NS}}}si"):
        fragments = [node.text or "" for node in item.iter(f"{{{MAIN_NS}}}t")]
        strings.append("".join(fragments))
    return strings


def _resolve_first_sheet(workbook: ZipFile) -> tuple[str, str]:
    wb = ET.fromstring(workbook.read("xl/workbook.xml"))
    sheets = wb.find(f"{{{MAIN_NS}}}sheets")
    if sheets is None or not list(sheets):
        raise NotaryImportFileError("El workbook no contiene hojas disponibles.")
    first_sheet = list(sheets)[0]
    sheet_name = first_sheet.attrib.get("name", "Sheet1")
    rel_id = first_sheet.attrib.get(f"{{{REL_NS}}}id")
    if not rel_id:
        raise NotaryImportFileError("No fue posible resolver la relación de la hoja principal.")

    rels = ET.fromstring(workbook.read("xl/_rels/workbook.xml.rels"))
    for relation in rels.findall(f"{{{PKG_REL_NS}}}Relationship"):
        if relation.attrib.get("Id") == rel_id:
            return sheet_name, f"xl/{relation.attrib['Target']}"
    raise NotaryImportFileError("No fue posible localizar la hoja principal dentro del archivo.")


def _read_cell_value(cell: ET.Element, shared_strings: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        fragments = [node.text or "" for node in cell.iter(f"{{{MAIN_NS}}}t")]
        return "".join(fragments)

    value_node = cell.find(f"{{{MAIN_NS}}}v")
    if value_node is None:
        return ""
    raw_value = value_node.text or ""
    if cell_type == "s":
        return shared_strings[int(raw_value)]
    return raw_value


def load_xlsx_rows(source_path: str | Path) -> WorkbookSheetData:
    path = validate_source_file(source_path)
    with ZipFile(path) as workbook:
        shared_strings = _read_shared_strings(workbook)
        sheet_name, sheet_target = _resolve_first_sheet(workbook)
        sheet = ET.fromstring(workbook.read(sheet_target))

    sheet_data = sheet.find(f"{{{MAIN_NS}}}sheetData")
    if sheet_data is None:
        raise NotaryImportFileError("La hoja principal no contiene datos.")

    parsed_rows: list[dict[str, str]] = []
    headers: dict[str, str] | None = None

    for row in list(sheet_data):
        row_values: dict[str, str] = {}
        for cell in list(row):
            ref = cell.attrib.get("r", "")
            column = "".join(character for character in ref if character.isalpha())
            row_values[column] = _read_cell_value(cell, shared_strings).strip()

        if not row_values:
            continue

        if headers is None:
            headers = row_values
            continue

        mapped_row = {
            header_name: row_values.get(column_name, "")
            for column_name, header_name in headers.items()
            if header_name
        }
        if any(value for value in mapped_row.values()):
            parsed_rows.append(mapped_row)

    if headers is None:
        raise NotaryImportFileError("No se encontró la fila de encabezados.")

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in headers.values()]
    if missing_columns:
        raise NotaryImportFileError(f"Faltan columnas requeridas: {', '.join(missing_columns)}")

    return WorkbookSheetData(sheet_name=sheet_name, rows=parsed_rows)
