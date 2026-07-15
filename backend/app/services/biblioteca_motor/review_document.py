from __future__ import annotations

import copy
import hashlib
import io
import re
import zipfile
from dataclasses import dataclass
from typing import Any

from lxml import etree


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}
W = f"{{{W_NS}}}"
SUGGESTION_TAG_PREFIX = "easypro:suggestion:v1:"
FIELD_TAG_PREFIX = "easypro:field:v1:"


@dataclass(frozen=True)
class ReviewDocumentResult:
    docx_bytes: bytes
    groups: list[dict[str, Any]]
    wrapped_count: int
    skipped: list[dict[str, str]]


@dataclass(frozen=True)
class _RunSegment:
    run: etree._Element
    start: int
    end: int
    text: str


def prepare_review_document(
    docx_bytes: bytes,
    suggestions: list[dict[str, Any]],
    *,
    analysis_id: str,
) -> ReviewDocumentResult:
    source_text = visible_text_from_docx(docx_bytes)
    root, entries = _load_document_xml(docx_bytes)
    groups = build_review_groups(suggestions, analysis_id=analysis_id)
    occurrence_by_suggestion = {
        occurrence["suggestion_id"]: (group, occurrence)
        for group in groups
        for occurrence in group["occurrences"]
    }
    paragraphs = _top_level_paragraphs(root)
    cells = _table_cells(root)
    operations_by_paragraph: dict[int, list[dict[str, Any]]] = {}
    skipped: list[dict[str, str]] = []

    for suggestion in suggestions:
        suggestion_id = str(suggestion.get("suggestion_id") or "")
        linked = occurrence_by_suggestion.get(suggestion_id)
        if not linked:
            continue
        group, occurrence = linked
        original_text = str(suggestion.get("original_text") or "")
        location = suggestion.get("location") if isinstance(suggestion.get("location"), dict) else {}
        paragraph, start, end, reason = _resolve_target(paragraphs, cells, location, original_text)
        if paragraph is None or start is None or end is None:
            _skip(skipped, occurrence, suggestion_id, reason or "location_not_verified")
            continue
        if _contains_easypro_control(paragraph):
            _skip(skipped, occurrence, suggestion_id, "existing_easypro_control")
            continue
        operations_by_paragraph.setdefault(id(paragraph), []).append(
            {
                "paragraph": paragraph,
                "start": start,
                "end": end,
                "tag": _suggestion_tag(analysis_id, suggestion, group["group_id"], occurrence["occurrence_id"]),
                "alias": f"EasyPro sugerencia - {suggestion.get('field_code')}",
                "suggestion_id": suggestion_id,
                "occurrence": occurrence,
            },
        )

    wrapped_count = 0
    for operations in operations_by_paragraph.values():
        operations.sort(key=lambda item: item["start"], reverse=True)
        for operation in operations:
            if _wrap_paragraph_span(
                operation["paragraph"],
                operation["start"],
                operation["end"],
                tag=operation["tag"],
                alias=operation["alias"],
            ):
                operation["occurrence"]["status"] = "prepared"
                operation["occurrence"]["tag"] = operation["tag"]
                wrapped_count += 1
            else:
                _skip(skipped, operation["occurrence"], operation["suggestion_id"], "run_split_failed")

    result_bytes = _write_document_xml(entries, root)
    if visible_text_from_docx(result_bytes) != source_text:
        raise ValueError("La version de revision altero el texto visible.")
    return ReviewDocumentResult(result_bytes, groups, wrapped_count, skipped)


def build_review_groups(suggestions: list[dict[str, Any]], *, analysis_id: str) -> list[dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = {}
    occurrence_count = 0
    for suggestion in suggestions:
        field_code = str(suggestion.get("field_code") or "").strip()
        original_text = str(suggestion.get("original_text") or "").strip()
        suggestion_id = str(suggestion.get("suggestion_id") or "").strip()
        candidate_id = str(suggestion.get("candidate_id") or "").strip()
        if not field_code or not original_text or not suggestion_id or not candidate_id:
            continue
        group_id = "grp_" + hashlib.sha256(
            f"{field_code}|{_canonical_value(original_text)}|{suggestion.get('category') or ''}".encode("utf-8"),
        ).hexdigest()[:16]
        group = groups.setdefault(
            group_id,
            {
                "group_id": group_id,
                "field_instance_id": field_code,
                "field_code": field_code,
                "field_label": suggestion.get("field_label") or field_code,
                "detected_value": original_text,
                "category": suggestion.get("category") or "otro",
                "confidence": float(suggestion.get("confidence") or 0),
                "source": suggestion.get("source") or "deterministic",
                "occurrences": [],
            },
        )
        group["confidence"] = max(float(group["confidence"]), float(suggestion.get("confidence") or 0))
        occurrence_count += 1
        group["occurrences"].append(
            {
                "occurrence_id": f"occ_{occurrence_count:03d}",
                "suggestion_id": suggestion_id,
                "candidate_id": candidate_id,
                "field_code": field_code,
                "field_instance_id": field_code,
                "original_text": original_text,
                "location": suggestion.get("location") or {},
                "context_before": suggestion.get("context_before") or "",
                "context_after": suggestion.get("context_after") or "",
                "status": "pending_review",
                "tag": None,
            },
        )
    return list(groups.values())


def accept_suggestions_in_docx(docx_bytes: bytes, accepted: list[dict[str, str]]) -> bytes:
    root, entries = _load_document_xml(docx_bytes)
    actions = {str(item.get("suggestion_tag") or ""): item for item in accepted}
    for sdt in _iter_easypro_controls(root, SUGGESTION_TAG_PREFIX):
        action = actions.get(_control_tag(sdt) or "")
        if not action:
            continue
        field_instance_id = _safe_component(action.get("field_instance_id") or "")
        occurrence_id = _safe_component(action.get("occurrence_id") or "")
        if not field_instance_id or not occurrence_id:
            continue
        _set_control_tag(sdt, f"{FIELD_TAG_PREFIX}{field_instance_id}:{occurrence_id}")
        _set_control_alias(sdt, f"EasyPro campo - {field_instance_id}")
        _replace_control_text(sdt, f"{{{{{field_instance_id}}}}}")
        _remove_highlight(sdt)
    return _write_document_xml(entries, root)


def reject_suggestions_in_docx(docx_bytes: bytes, suggestion_tags: list[str]) -> bytes:
    root, entries = _load_document_xml(docx_bytes)
    tags = set(suggestion_tags)
    for sdt in list(_iter_easypro_controls(root, SUGGESTION_TAG_PREFIX)):
        if _control_tag(sdt) in tags:
            _remove_highlight(sdt)
            _unwrap_control(sdt)
    return _write_document_xml(entries, root)


def cascade_field_controls_in_docx(docx_bytes: bytes, field_instance_id: str, value: str) -> tuple[bytes, int]:
    safe_field = _safe_component(field_instance_id)
    if not safe_field:
        raise ValueError("field_instance_id requerido")
    root, entries = _load_document_xml(docx_bytes)
    updated = 0
    for sdt in _iter_easypro_controls(root, FIELD_TAG_PREFIX):
        tag = _control_tag(sdt) or ""
        parts = tag.split(":")
        if len(parts) >= 4 and parts[3] == safe_field:
            _replace_control_text(sdt, value)
            updated += 1
    return _write_document_xml(entries, root), updated


def visible_text_from_docx(docx_bytes: bytes) -> str:
    root, _entries = _load_document_xml(docx_bytes)
    return "".join(root.xpath(".//w:t/text()", namespaces=NS))


def _load_document_xml(docx_bytes: bytes) -> tuple[etree._Element, dict[str, bytes]]:
    with zipfile.ZipFile(io.BytesIO(docx_bytes), "r") as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    if "word/document.xml" not in entries:
        raise ValueError("DOCX sin word/document.xml")
    return etree.fromstring(entries["word/document.xml"]), entries


def _write_document_xml(entries: dict[str, bytes], root: etree._Element) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in entries.items():
            archive.writestr(
                name,
                etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone="yes")
                if name == "word/document.xml"
                else content,
            )
    return output.getvalue()


def _top_level_paragraphs(root: etree._Element) -> dict[int, etree._Element]:
    body = root.find("w:body", NS)
    if body is None:
        return {}
    return {index: item for index, item in enumerate(body.findall("w:p", NS), start=1)}


def _table_cells(root: etree._Element) -> dict[tuple[int, int, int], etree._Element]:
    body = root.find("w:body", NS)
    cells: dict[tuple[int, int, int], etree._Element] = {}
    if body is None:
        return cells
    for table_index, table in enumerate(body.findall("w:tbl", NS), start=1):
        for row_index, row in enumerate(table.findall("w:tr", NS), start=1):
            for cell_index, cell in enumerate(row.findall("w:tc", NS), start=1):
                cells[(table_index, row_index, cell_index)] = cell
    return cells


def _resolve_target(
    paragraphs: dict[int, etree._Element],
    cells: dict[tuple[int, int, int], etree._Element],
    location: dict[str, Any],
    original_text: str,
) -> tuple[etree._Element | None, int | None, int | None, str | None]:
    start = _int_or_none(location.get("char_start"))
    end = _int_or_none(location.get("char_end"))
    if start is None or end is None or end <= start:
        return None, None, None, "invalid_offsets"
    if location.get("block_type") == "paragraph":
        paragraph = paragraphs.get(_int_or_none(location.get("paragraph_index")) or -1)
        if paragraph is None:
            return None, None, None, "paragraph_not_found"
        text = _paragraph_text(paragraph)
        return _validate_block(paragraph, text, start, end, original_text, location)
    if location.get("block_type") == "table_cell":
        cell = cells.get(
            (
                _int_or_none(location.get("table_index")) or -1,
                _int_or_none(location.get("row_index")) or -1,
                _int_or_none(location.get("cell_index")) or -1,
            ),
        )
        if cell is None:
            return None, None, None, "table_cell_not_found"
        cell_text = _cell_text(cell)
        ok, reason = _validate_text(cell_text, start, end, original_text, location)
        if not ok:
            return None, None, None, reason
        mapped = _map_cell_offsets_to_paragraph(cell, start, end)
        if mapped is None:
            return None, None, None, "span_crosses_cell_paragraphs"
        paragraph, mapped_start, mapped_end = mapped
        return paragraph, mapped_start, mapped_end, None
    return None, None, None, "unsupported_block_type"


def _validate_block(
    paragraph: etree._Element,
    text: str,
    start: int,
    end: int,
    original_text: str,
    location: dict[str, Any],
) -> tuple[etree._Element | None, int | None, int | None, str | None]:
    ok, reason = _validate_text(text, start, end, original_text, location)
    if not ok:
        return None, None, None, reason
    return paragraph, start, end, None


def _validate_text(text: str, start: int, end: int, original_text: str, location: dict[str, Any]) -> tuple[bool, str | None]:
    if start < 0 or end > len(text) or text[start:end] != original_text:
        return False, "substring_mismatch"
    expected_hash = location.get("block_hash")
    if expected_hash and hashlib.sha256(text.encode("utf-8")).hexdigest() != expected_hash:
        return False, "block_hash_mismatch"
    return True, None


def _paragraph_text(paragraph: etree._Element) -> str:
    return "".join(paragraph.xpath(".//w:t/text()", namespaces=NS))


def _cell_text(cell: etree._Element) -> str:
    return "\n".join(text for text in (_paragraph_text(p) for p in cell.findall("w:p", NS)) if text)


def _map_cell_offsets_to_paragraph(cell: etree._Element, start: int, end: int) -> tuple[etree._Element, int, int] | None:
    cursor = 0
    for paragraph in cell.findall("w:p", NS):
        text = _paragraph_text(paragraph)
        if not text:
            continue
        paragraph_end = cursor + len(text)
        if start >= cursor and end <= paragraph_end:
            return paragraph, start - cursor, end - cursor
        cursor = paragraph_end + 1
    return None


def _wrap_paragraph_span(paragraph: etree._Element, start: int, end: int, *, tag: str, alias: str) -> bool:
    text = _paragraph_text(paragraph)
    if start < 0 or end > len(text) or start >= end:
        return False
    segments = _paragraph_segments(paragraph)
    affected = [segment for segment in segments if segment.start < end and start < segment.end]
    if not affected:
        return False
    affected_ids = {id(segment.run) for segment in affected}
    first_id = id(affected[0].run)
    sdt = _create_sdt(tag, alias)
    content = sdt.find("w:sdtContent", NS)
    if content is None:
        return False
    new_children: list[etree._Element] = []
    inserted = False
    for child in list(paragraph):
        segment = next((item for item in affected if item.run is child), None)
        if id(child) not in affected_ids or segment is None:
            new_children.append(child)
            continue
        local_start = max(0, start - segment.start)
        local_end = min(segment.end, end) - segment.start
        before = segment.text[:local_start]
        middle = segment.text[local_start:local_end]
        after = segment.text[local_end:]
        if before:
            new_children.append(_clone_run(child, before, highlight=False))
        if id(child) == first_id and not inserted:
            new_children.append(sdt)
            inserted = True
        if middle:
            content.append(_clone_run(child, middle, highlight=True))
        if after:
            new_children.append(_clone_run(child, after, highlight=False))
    paragraph[:] = new_children
    return True


def _paragraph_segments(paragraph: etree._Element) -> list[_RunSegment]:
    cursor = 0
    segments: list[_RunSegment] = []
    for child in paragraph:
        if child.tag != f"{W}r":
            continue
        text = "".join(child.xpath(".//w:t/text()", namespaces=NS))
        if not text:
            continue
        segments.append(_RunSegment(child, cursor, cursor + len(text), text))
        cursor += len(text)
    return segments


def _clone_run(run: etree._Element, text: str, *, highlight: bool) -> etree._Element:
    new_run = etree.Element(f"{W}r")
    rpr = run.find("w:rPr", NS)
    if rpr is not None:
        new_run.append(copy.deepcopy(rpr))
    if highlight:
        _ensure_highlight(new_run)
    text_el = etree.SubElement(new_run, f"{W}t")
    if text[:1].isspace() or text[-1:].isspace():
        text_el.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    text_el.text = text
    return new_run


def _create_sdt(tag: str, alias: str) -> etree._Element:
    sdt = etree.Element(f"{W}sdt")
    pr = etree.SubElement(sdt, f"{W}sdtPr")
    tag_el = etree.SubElement(pr, f"{W}tag")
    tag_el.set(f"{W}val", tag)
    alias_el = etree.SubElement(pr, f"{W}alias")
    alias_el.set(f"{W}val", alias)
    etree.SubElement(sdt, f"{W}sdtContent")
    return sdt


def _ensure_highlight(run: etree._Element) -> None:
    rpr = run.find("w:rPr", NS)
    if rpr is None:
        rpr = etree.Element(f"{W}rPr")
        run.insert(0, rpr)
    for existing in list(rpr.findall("w:highlight", NS)):
        rpr.remove(existing)
    highlight = etree.SubElement(rpr, f"{W}highlight")
    highlight.set(f"{W}val", "yellow")


def _remove_highlight(element: etree._Element) -> None:
    for highlight in list(element.findall(".//w:highlight", NS)):
        parent = highlight.getparent()
        if parent is not None:
            parent.remove(highlight)


def _replace_control_text(sdt: etree._Element, value: str) -> None:
    content = sdt.find("w:sdtContent", NS)
    if content is None:
        return
    first_run = content.find(".//w:r", NS)
    rpr = copy.deepcopy(first_run.find("w:rPr", NS)) if first_run is not None and first_run.find("w:rPr", NS) is not None else None
    for child in list(content):
        content.remove(child)
    run = etree.SubElement(content, f"{W}r")
    if rpr is not None:
        run.append(rpr)
    text = etree.SubElement(run, f"{W}t")
    text.text = value


def _unwrap_control(sdt: etree._Element) -> None:
    parent = sdt.getparent()
    content = sdt.find("w:sdtContent", NS)
    if parent is None or content is None:
        return
    index = parent.index(sdt)
    parent.remove(sdt)
    for child in reversed(list(content)):
        parent.insert(index, child)


def _contains_easypro_control(paragraph: etree._Element) -> bool:
    return any((_control_tag(sdt) or "").startswith((SUGGESTION_TAG_PREFIX, FIELD_TAG_PREFIX)) for sdt in paragraph.findall(".//w:sdt", NS))


def _iter_easypro_controls(root: etree._Element, prefix: str):
    for sdt in root.findall(".//w:sdt", NS):
        tag = _control_tag(sdt)
        if tag and tag.startswith(prefix):
            yield sdt


def _control_tag(sdt: etree._Element) -> str | None:
    tag = sdt.find("w:sdtPr/w:tag", NS)
    return tag.get(f"{W}val") if tag is not None else None


def _set_control_tag(sdt: etree._Element, value: str) -> None:
    pr = sdt.find("w:sdtPr", NS)
    if pr is None:
        pr = etree.Element(f"{W}sdtPr")
        sdt.insert(0, pr)
    tag = pr.find("w:tag", NS)
    if tag is None:
        tag = etree.SubElement(pr, f"{W}tag")
    tag.set(f"{W}val", value)


def _set_control_alias(sdt: etree._Element, value: str) -> None:
    pr = sdt.find("w:sdtPr", NS)
    if pr is None:
        pr = etree.Element(f"{W}sdtPr")
        sdt.insert(0, pr)
    alias = pr.find("w:alias", NS)
    if alias is None:
        alias = etree.SubElement(pr, f"{W}alias")
    alias.set(f"{W}val", value)


def _suggestion_tag(analysis_id: str, suggestion: dict[str, Any], group_id: str, occurrence_id: str) -> str:
    return ":".join(
        [
            SUGGESTION_TAG_PREFIX.rstrip(":"),
            _safe_component(analysis_id),
            _safe_component(suggestion.get("suggestion_id") or ""),
            _safe_component(suggestion.get("candidate_id") or ""),
            _safe_component(suggestion.get("field_code") or ""),
            _safe_component(group_id),
            _safe_component(occurrence_id),
        ],
    )


def _skip(skipped: list[dict[str, str]], occurrence: dict[str, Any], suggestion_id: str, reason: str) -> None:
    occurrence["status"] = "skipped"
    occurrence["skip_reason"] = reason
    skipped.append({"suggestion_id": suggestion_id, "reason": reason})


def _canonical_value(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().upper())


def _safe_component(value: Any) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", str(value or "").strip())[:80]


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
