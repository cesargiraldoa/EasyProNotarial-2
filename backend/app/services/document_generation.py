from __future__ import annotations

import html
import json
import re
import unicodedata
import zipfile
from pathlib import Path

from docx import Document
from docx.enum.text import WD_COLOR_INDEX

PLACEHOLDER_PATTERN = re.compile(r"\{\{.*?\}\}", re.DOTALL)
XML_TAG_PATTERN = re.compile(r"<[^>]+>")


def normalize_placeholder(raw: str) -> str:
    plain = XML_TAG_PATTERN.sub("", raw)
    plain = plain.replace("\n", "").replace("\r", "").replace("\t", "")
    plain = re.sub(r"\s+", "", plain)
    return plain


def render_docx_template(source_path: str | Path, destination_path: str | Path, replacements: dict[str, str]) -> None:
    source = Path(source_path)
    destination = Path(destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source, "r") as source_zip, zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as dest_zip:
        for item in source_zip.infolist():
            data = source_zip.read(item.filename)
            if item.filename.endswith(".xml"):
                text = data.decode("utf-8", errors="ignore")

                def replace_match(match: re.Match[str]) -> str:
                    token = normalize_placeholder(match.group(0))
                    if token in replacements:
                        return html.escape(str(replacements[token] or ""))
                    return match.group(0)

                text = PLACEHOLDER_PATTERN.sub(replace_match, text)
                import re as _re

                LONGITUD_LINEA = 95

                def reemplazar_guiones(xml_parrafo: str) -> str:
                    if "[[--]]" not in xml_parrafo:
                        return xml_parrafo
                    texto_visible = _re.sub(r"<[^>]+>", "", xml_parrafo)
                    texto_visible = texto_visible.replace("[[--]]", "").strip()
                    espacio = LONGITUD_LINEA - len(texto_visible)
                    if espacio < 4:
                        guiones = " -"
                    else:
                        guiones = ""
                        while len(guiones) + 2 <= espacio:
                            guiones += "- "
                        guiones = " " + guiones.rstrip()
                    return xml_parrafo.replace("[[--]]", guiones)

                text = _re.sub(
                    r"(<w:p[ >].*?</w:p>)",
                    lambda m: reemplazar_guiones(m.group(1)),
                    text,
                    flags=_re.DOTALL,
                )
                data = text.encode("utf-8")
            dest_zip.writestr(item, data)


def recalculate_dash_fills(docx_path: str | Path) -> None:
    """
    Después de render_docx_template(), recorre cada párrafo del docx
    y ajusta los runs de guiones '- - -' al final para que llenen
    exactamente hasta el margen derecho (seguridad antifraude notarial).

    Lógica:
    - Cada párrafo notarial termina con un run de guiones "- - - - -"
    - Detectar runs que son SOLO guiones y espacios al final del párrafo
    - Calcular el texto real del párrafo sin los guiones finales
    - Calcular cuántos guiones caben para llegar a LONGITUD_OBJETIVO = 90 chars
    - Reemplazar el run de guiones con la cantidad correcta
    """
    LONGITUD_OBJETIVO = 90
    PATRON_GUIONES = re.compile(r"^[\s\-]+$")

    doc = Document(str(docx_path))

    for para in doc.paragraphs:
        runs = para.runs
        if not runs:
            continue

        last_dash_run = None
        last_dash_idx = -1
        candidates = runs[-2:] if len(runs) >= 2 else runs[-1:]
        for i, run in enumerate(candidates):
            real_idx = len(runs) - len(candidates) + i
            text = run.text.strip()
            if PATRON_GUIONES.match(run.text) and len(text) > 6:
                last_dash_run = run
                last_dash_idx = real_idx

        if last_dash_run is None:
            continue

        texto_sin_guiones = "".join(
            r.text for i, r in enumerate(runs) if i != last_dash_idx
        ).rstrip()

        espacio_disponible = LONGITUD_OBJETIVO - len(texto_sin_guiones)
        if espacio_disponible < 4:
            last_dash_run.text = " -"
            continue

        guiones = ""
        while len(guiones) + 2 <= espacio_disponible:
            guiones += "- "

        last_dash_run.text = " " + guiones.rstrip()

    doc.save(str(docx_path))


def extract_text_from_docx(source_path: str | Path) -> str:
    """
    Extrae el texto plano del Word para usarlo como referencia para Gari.
    """
    source = Path(source_path)
    text_parts: list[str] = []
    with zipfile.ZipFile(source, "r") as zf:
        if "word/document.xml" in zf.namelist():
            xml_content = zf.read("word/document.xml").decode("utf-8", errors="ignore")
            clean = re.sub(r"<[^>]+>", " ", xml_content)
            clean = re.sub(r"\s+", " ", clean).strip()
            text_parts.append(clean)
    return "\n".join(text_parts)


def generate_plain_pdf(destination_path: str | Path, title: str, lines: list[str]) -> None:
    escaped_lines: list[str] = []
    for raw in [title, *lines]:
        text = (raw or "").replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        escaped_lines.append(text)

    content_lines = ["BT", "/F1 12 Tf", "50 800 Td"]
    first = True
    for line in escaped_lines:
        if first:
            content_lines.append(f"({line}) Tj")
            first = False
        else:
            content_lines.append("0 -16 Td")
            content_lines.append(f"({line}) Tj")
    content_lines.append("ET")
    stream = "\n".join(content_lines).encode("latin-1", errors="replace")

    objects = [
        b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n",
        b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n",
        b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>endobj\n",
        f"4 0 obj<< /Length {len(stream)} >>stream\n".encode("ascii") + stream + b"\nendstream endobj\n",
        b"5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n",
    ]

    destination = Path(destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as handle:
        handle.write(b"%PDF-1.4\n")
        offsets = [0]
        for obj in objects:
            offsets.append(handle.tell())
            handle.write(obj)
        xref_start = handle.tell()
        handle.write(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
        handle.write(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            handle.write(f"{offset:010d} 00000 n \n".encode("ascii"))
        handle.write(f"trailer<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF".encode("ascii"))


def build_case_text_snapshot(case_number: str, act_type: str, participants: list[dict], act_data: dict) -> list[str]:
    lines = [
        f"Caso: {case_number}",
        f"Acto: {act_type}",
        "Intervinientes:",
    ]
    for item in participants:
        lines.append(f"- {item.get('role_label')}: {item.get('full_name')} ({item.get('document_type')} {item.get('document_number')})")
    lines.append("Datos del acto:")
    for key, value in act_data.items():
        lines.append(f"- {key}: {value}")
    return lines


def serialize_placeholder_snapshot(replacements: dict[str, str]) -> str:
    return json.dumps(replacements, ensure_ascii=False, indent=2)


def extract_highlighted_fields_from_docx(source_path: str | Path) -> list[dict]:
    from docx import Document
    from docx.enum.text import WD_COLOR_INDEX
    import re

    source = Path(source_path)
    doc = Document(str(source))

    VALID_HIGHLIGHTS = {WD_COLOR_INDEX.TURQUOISE, WD_COLOR_INDEX.YELLOW}

    # PASO 1: buscar etiquetas {{CAMPO}} - prioridad alta
    seen_codes: dict[str, int] = {}
    etiqueta_fields: list[dict] = []
    order = 1

    for para in doc.paragraphs:
        matches = re.findall(r"\{\{([^}]+)\}\}", para.text)
        for match in matches:
            raw = match.strip()
            if not raw or len(raw) < 2:
                continue
            if re.match(r"^[\s\.\-\_\,\;\:]+$", raw):
                continue
            field_code = re.sub(r"[^a-z0-9]+", "_", raw.lower()).strip("_")
            if not field_code or field_code in seen_codes:
                continue
            label = raw.replace("_", " ").title().strip()
            if len(label) < 2:
                continue
            seen_codes[field_code] = order
            etiqueta_fields.append({
                "field_code": field_code,
                "label": label,
                "display_order": order,
                "highlight_color": "none",
            })
            order += 1

    if etiqueta_fields:
        return etiqueta_fields

    # PASO 2: fallback - buscar highlights turquesa o amarillo
    seen_codes = {}
    highlight_fields: list[dict] = []
    order = 1

    for para in doc.paragraphs:
        for run in para.runs:
            if run.font.highlight_color not in VALID_HIGHLIGHTS:
                continue
            raw = (run.text or "").strip()
            if not raw or len(raw) < 2:
                continue
            if re.match(r"^[\s\.\-\_\,\;\:]+$", raw):
                continue
            field_code = re.sub(r"[^a-z0-9]+", "_", raw.lower()).strip("_")
            if not field_code or field_code in seen_codes:
                continue
            label = raw.replace("_", " ").strip()
            if len(label) < 2:
                continue
            color_name = "turquoise" if run.font.highlight_color == WD_COLOR_INDEX.TURQUOISE else "yellow"
            seen_codes[field_code] = order
            highlight_fields.append({
                "field_code": field_code,
                "label": label,
                "display_order": order,
                "highlight_color": color_name,
            })
            order += 1

    return highlight_fields
