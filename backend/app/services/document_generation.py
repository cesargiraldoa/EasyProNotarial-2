from __future__ import annotations

import html
import json
import re
import zipfile
from pathlib import Path

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
                data = text.encode("utf-8")
            dest_zip.writestr(item, data)


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
