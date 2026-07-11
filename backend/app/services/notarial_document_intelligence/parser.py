from __future__ import annotations

import tempfile
from importlib import metadata
from pathlib import Path

from docx import Document
from docx.document import Document as DocxDocument
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph

from app.services.notarial_document_intelligence.contracts import BlockType, ParsedBlock, ParsedDocument
from app.services.notarial_document_intelligence.hashing import sha256_text


class NotarialDocumentParser:
    parser_name = "python-docx+unstructured"

    def parse_bytes(self, content: bytes, filename: str = "documento.docx") -> ParsedDocument:
        suffix = Path(filename).suffix or ".docx"
        with tempfile.TemporaryDirectory(prefix="easypro2-notarial-parse-") as tmp_dir:
            source = Path(tmp_dir) / f"source{suffix}"
            source.write_bytes(content)
            return self.parse_path(source)

    def parse_path(self, source_path: str | Path) -> ParsedDocument:
        source = Path(source_path)
        blocks = list(_iter_python_docx_blocks(source))
        warnings: list[str] = []
        unstructured_metadata = self._read_unstructured_elements(source, blocks, warnings)
        return ParsedDocument(
            parser_name=self.parser_name,
            parser_version=f"python-docx:{_package_version('python-docx')};unstructured:{unstructured_metadata.get('version', 'unavailable')}",
            blocks=blocks,
            warnings=warnings,
            metadata={"unstructured": unstructured_metadata},
        )

    @staticmethod
    def _read_unstructured_elements(source: Path, blocks: list[ParsedBlock], warnings: list[str]) -> dict[str, object]:
        try:
            from unstructured.partition.docx import partition_docx
        except Exception:
            warnings.append("unstructured_not_installed")
            return {"enabled": False, "elements_count": 0, "version": "unavailable"}

        try:
            elements = partition_docx(filename=str(source))
        except Exception as exc:
            warnings.append(f"unstructured_error:{type(exc).__name__}")
            return {"enabled": True, "elements_count": 0, "version": _package_version("unstructured"), "error": str(exc)}

        categories: dict[str, int] = {}
        semantic_elements: list[dict[str, object]] = []
        for element in elements:
            category = type(element).__name__
            categories[category] = categories.get(category, 0) + 1
            text = str(element).strip()
            metadata = getattr(element, "metadata", None)
            semantic_elements.append(
                {
                    "category": category,
                    "text": text,
                    "metadata": metadata.to_dict() if metadata is not None and hasattr(metadata, "to_dict") else {},
                }
            )
        _reconcile_unstructured_blocks(blocks, semantic_elements)
        return {
            "enabled": True,
            "elements_count": len(elements),
            "categories": categories,
            "reconciled_blocks": sum(1 for block in blocks if block.parser_source == "python-docx+unstructured"),
            "version": _package_version("unstructured"),
        }


def _iter_python_docx_blocks(source: Path) -> list[ParsedBlock]:
    document = Document(str(source))
    blocks: list[ParsedBlock] = []
    char_cursor = 0
    for location, block_type, text, indexes in _iter_blocks(document):
        normalized_text = text.strip()
        if not normalized_text:
            continue
        block_index = len(blocks) + 1
        char_start = char_cursor
        char_end = char_start + len(normalized_text)
        char_cursor = char_end + 1
        blocks.append(
            ParsedBlock(
                block_index=block_index,
                block_type=block_type,
                location_key=location,
                text=normalized_text,
                text_hash=sha256_text(normalized_text),
                table_index=indexes.get("table_index"),
                row_index=indexes.get("row_index"),
                cell_index=indexes.get("cell_index"),
                paragraph_index=indexes.get("paragraph_index"),
                metadata={"char_start": char_start, "char_end": char_end},
            )
        )
    return blocks


def _reconcile_unstructured_blocks(blocks: list[ParsedBlock], semantic_elements: list[dict[str, object]]) -> None:
    used_indexes: set[int] = set()
    for block in blocks:
        normalized_block = _normalize_text(block.text)
        if not normalized_block:
            continue
        best_index: int | None = None
        best_element: dict[str, object] | None = None
        for index, element in enumerate(semantic_elements):
            if index in used_indexes:
                continue
            semantic_text = _normalize_text(str(element.get("text") or ""))
            if not semantic_text:
                continue
            if normalized_block == semantic_text or normalized_block in semantic_text or semantic_text in normalized_block:
                best_index = index
                best_element = element
                break
        if best_index is None or best_element is None:
            continue

        category = str(best_element.get("category") or "")
        block.semantic_type = _semantic_type_for_category(category)
        block.semantic_title = block.text if block.semantic_type == "title" else None
        block.semantic_section = _probable_section(block.text, block.semantic_type)
        block.parser_source = "python-docx+unstructured"
        block.unstructured_category = category
        block.metadata["unstructured"] = {
            "category": category,
            "metadata": best_element.get("metadata") or {},
        }
        used_indexes.add(best_index)


def _semantic_type_for_category(category: str) -> str:
    normalized = category.lower()
    if "title" in normalized:
        return "title"
    if "narrative" in normalized:
        return "narrative"
    if "list" in normalized:
        return "list"
    if "table" in normalized:
        return "table"
    if "address" in normalized:
        return "address"
    return normalized or "unknown"


def _probable_section(text: str, semantic_type: str | None) -> str | None:
    normalized = text.strip().upper()
    if semantic_type == "title":
        return normalized[:160]
    for marker in ("COMPARECEN", "OBJETO", "INMUEBLE", "PRECIO", "HIPOTECA", "FIRMAS"):
        if marker in normalized:
            return marker.lower()
    return None


def _normalize_text(text: str) -> str:
    return " ".join(text.split()).casefold()


def _iter_blocks(parent, prefix: str = "", table_index: int | None = None):
    paragraph_index = 0
    table_count = 0
    for block in _iter_block_items(parent):
        if isinstance(block, Paragraph):
            paragraph_index += 1
            text = block.text or ""
            location = f"{prefix}paragraph:{paragraph_index}" if prefix else f"paragraph:{paragraph_index}"
            yield (
                location,
                BlockType.TABLE_CELL_PARAGRAPH if prefix else BlockType.PARAGRAPH,
                text,
                {"table_index": table_index, "paragraph_index": paragraph_index},
            )
        elif isinstance(block, Table):
            table_count += 1
            yield from _iter_table_blocks(block, table_count)


def _iter_table_blocks(table: Table, table_index: int):
    seen_cells: set[int] = set()
    for row_index, row in enumerate(table.rows, start=1):
        for cell_index, cell in enumerate(row.cells, start=1):
            cell_id = id(cell._tc)
            if cell_id in seen_cells:
                continue
            seen_cells.add(cell_id)
            prefix = f"table:{table_index}/row:{row_index}/cell:{cell_index}/"
            for location, block_type, text, indexes in _iter_blocks(cell, prefix=prefix, table_index=table_index):
                indexes.update({"row_index": row_index, "cell_index": cell_index})
                yield location, block_type, text, indexes


def _iter_block_items(parent):
    if isinstance(parent, DocxDocument):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        raise TypeError(f"Unsupported parent type: {type(parent)!r}")

    for child in parent_elm.iterchildren():
        if child.tag.endswith("}p"):
            yield Paragraph(child, parent)
        elif child.tag.endswith("}tbl"):
            yield Table(child, parent)


def _package_version(package_name: str) -> str:
    try:
        return metadata.version(package_name)
    except metadata.PackageNotFoundError:
        return "unavailable"
