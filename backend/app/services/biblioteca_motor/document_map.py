from __future__ import annotations

import hashlib
import io
from dataclasses import asdict, dataclass
from typing import Any
import zipfile

from lxml import etree


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}


@dataclass(frozen=True)
class DocumentMapBlock:
    block_id: str
    block_type: str
    text: str
    block_hash: str
    order: int
    block_index: int
    paragraph_index: int | None = None
    table_index: int | None = None
    row_index: int | None = None
    cell_index: int | None = None


@dataclass(frozen=True)
class DocumentMap:
    document_sha256: str
    blocks: list[DocumentMapBlock]

    def block_by_id(self) -> dict[str, DocumentMapBlock]:
        return {block.block_id: block for block in self.blocks}

    def to_prompt_payload(self) -> dict[str, Any]:
        return {
            "document_sha256": self.document_sha256,
            "blocks": [asdict(block) for block in self.blocks],
        }


def build_document_map(docx_bytes: bytes) -> DocumentMap:
    root = _document_root(docx_bytes)
    body = root.find("w:body", NS)
    blocks: list[DocumentMapBlock] = []
    if body is None:
        return DocumentMap(hashlib.sha256(docx_bytes).hexdigest(), blocks)

    order = 0
    block_index = 0
    top_level_paragraph_index = 0
    table_index = 0
    for child in body:
        if child.tag == f"{{{W_NS}}}p":
            top_level_paragraph_index += 1
            text = _paragraph_text(child)
            if text:
                order += 1
                block_index += 1
                blocks.append(
                    _block(
                        block_id=f"p_{top_level_paragraph_index:04d}",
                        block_type="paragraph",
                        text=text,
                        order=order,
                        block_index=block_index,
                        paragraph_index=top_level_paragraph_index,
                    ),
                )
        elif child.tag == f"{{{W_NS}}}tbl":
            table_index += 1
            for row_index, row in enumerate(child.findall("w:tr", NS), start=1):
                for cell_index, cell in enumerate(row.findall("w:tc", NS), start=1):
                    for paragraph_index, paragraph in enumerate(cell.findall("w:p", NS), start=1):
                        text = _paragraph_text(paragraph)
                        if not text:
                            continue
                        order += 1
                        block_index += 1
                        blocks.append(
                            _block(
                                block_id=f"t_{table_index:04d}_r_{row_index:04d}_c_{cell_index:04d}_p_{paragraph_index:04d}",
                                block_type="table_cell",
                                text=text,
                                order=order,
                                block_index=block_index,
                                paragraph_index=paragraph_index,
                                table_index=table_index,
                                row_index=row_index,
                                cell_index=cell_index,
                            ),
                        )
    return DocumentMap(hashlib.sha256(docx_bytes).hexdigest(), blocks)


def _document_root(docx_bytes: bytes) -> etree._Element:
    with zipfile.ZipFile(io.BytesIO(docx_bytes), "r") as archive:
        return etree.fromstring(archive.read("word/document.xml"))


def _paragraph_text(paragraph: etree._Element) -> str:
    return "".join(paragraph.xpath(".//w:t/text()", namespaces=NS))


def _block(
    *,
    block_id: str,
    block_type: str,
    text: str,
    order: int,
    block_index: int,
    paragraph_index: int | None = None,
    table_index: int | None = None,
    row_index: int | None = None,
    cell_index: int | None = None,
) -> DocumentMapBlock:
    return DocumentMapBlock(
        block_id=block_id,
        block_type=block_type,
        text=text,
        block_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        order=order,
        block_index=block_index,
        paragraph_index=paragraph_index,
        table_index=table_index,
        row_index=row_index,
        cell_index=cell_index,
    )
