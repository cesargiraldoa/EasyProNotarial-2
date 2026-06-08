from __future__ import annotations

import re
import unicodedata
from collections import Counter, OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from docx import Document
from docx.document import Document as DocxDocument
from docx.enum.text import WD_COLOR_INDEX
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph


_WORD_RE = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+")
_TOKEN_RE = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+|\d+|#")
_BRACKET_RE = re.compile(r"\[\[\s*(.+?)\s*\]\]")
_PAREN_RE = re.compile(r"\(\s*([^()]{3,80}?)\s*\)")
_INDEX_RE = re.compile(r"(?:numero|num|nro|no|n°|n|#)\.?\s*(\d{1,4})\b")


_ALIAS_MAP = {
    "comprador": "comprador",
    "compradora": "comprador",
    "compradores": "comprador",
    "comprados": "comprador",
    "comparador": "comprador",
    "vendedor": "vendedor",
    "vendedora": "vendedor",
    "vendedores": "vendedor",
    "vendidos": "vendedor",
    "apoderado": "apoderado",
    "apoderada": "apoderado",
    "representante": "apoderado",
    "conyuge": "pareja_o_conyuge",
    "companero": "pareja_o_conyuge",
    "companera": "pareja_o_conyuge",
    "pareja": "pareja_o_conyuge",
    "documento": "documento",
    "cedula": "documento",
    "cédula": "documento",
    "cc": "documento",
    "identificacion": "documento",
    "identificación": "documento",
    "numero": "indice",
    "número": "indice",
    "num": "indice",
    "nro": "indice",
    "no": "indice",
    "n°": "indice",
    "#": "indice",
    "matricula": "matricula",
    "matrícula": "matricula",
    "direccion": "direccion",
    "dirección": "direccion",
    "notaria": "notaria",
    "notaría": "notaria",
    "genero": "genero",
    "género": "genero",
    "inmueble": "inmueble",
    "catastro": "catastro",
    "lindero": "lindero",
    "valor": "valor",
    "precio": "valor",
    "pago": "valor",
    "descuento": "valor",
    "iva": "valor",
    "fecha": "fecha",
    "escritura": "escritura",
    "identificado": "identificado",
    "domiciliado": "domiciliado",
    "concordancia": "concordancia",
    "banco": "banco",
    "acreedor": "acreedor",
    "deudor": "deudor",
    "notario": "notario",
    "nit": "nit",
    "nombre": "nombre",
    "pago": "valor",
}

_INDEX_ALIAS_WORDS = {"indice"}

_SECTION_RULES = [
    ("Compradores", {"comprador"}),
    ("Vendedores", {"vendedor"}),
    ("Inmueble", {"inmueble", "matricula", "catastro", "lindero", "direccion", "apartamento"}),
    ("Valores", {"valor"}),
    ("Fechas", {"fecha"}),
    ("Notaría", {"notaria", "notario", "escritura"}),
    ("Concordancia", {"identificado", "domiciliado", "genero", "concordancia"}),
    ("Entidades financieras", {"banco", "acreedor", "deudor"}),
    ("Apoderados", {"apoderado", "representante"}),
]

_PAREN_ALLOWED_WORDS = {
    "comprador",
    "vendedor",
    "documento",
    "cedula",
    "cédula",
    "nit",
    "nombre",
    "valor",
    "precio",
    "pago",
    "fecha",
    "escritura",
    "inmueble",
    "matricula",
    "matrícula",
    "catastro",
    "lindero",
    "direccion",
    "dirección",
    "notaria",
    "notaría",
    "notario",
    "genero",
    "género",
    "identificado",
    "domiciliado",
    "apoderado",
    "banco",
    "acreedor",
    "deudor",
    "representante",
}

_PAREN_GENERIC_ONLY = {
    "nombre",
    "nit",
    "escritura",
    "documento",
    "fecha",
}

_FALLBACK_KEYWORDS = (
    "comprador",
    "vendedor",
    "apoderado",
    "documento",
    "cedula",
    "cédula",
    "nit",
    "nombre",
    "valor",
    "precio",
    "pago",
    "fecha",
    "escritura",
    "inmueble",
    "matricula",
    "matrícula",
    "catastro",
    "lindero",
    "direccion",
    "dirección",
    "notaria",
    "notaría",
    "notario",
    "genero",
    "género",
    "identificado",
    "domiciliado",
    "banco",
    "acreedor",
    "deudor",
    "representante",
)

_PARTNER_KEYWORDS = (
    "conyuge",
    "companero",
    "companera",
    "pareja",
)

_PARTNER_FIELD_PREFIXES = (
    ("email", ("correo", "email", "mail")),
    ("celular", ("celular", "telefono", "tel")),
    ("direccion", ("direccion", "domicilio")),
    ("numero_documento", ("numero documento", "documento", "cedula", "identificacion")),
    ("nombre", ("nombre",)),
)


@dataclass
class NormalizedField:
    key: str
    label: str
    section: str


@dataclass
class FieldAccumulator:
    key: str
    label: str
    section: str
    occurrences: int = 0
    marker_types: set[str] = field(default_factory=set)
    raw_markers: list[str] = field(default_factory=list)
    _raw_seen: set[str] = field(default_factory=set)

    def add_occurrence(self, marker_type: str, raw_marker: str) -> None:
        self.occurrences += 1
        self.marker_types.add(marker_type)
        if raw_marker not in self._raw_seen:
            self.raw_markers.append(raw_marker)
            self._raw_seen.add(raw_marker)


def _strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def _collapse_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _normalize_for_match(text: str) -> str:
    text = _strip_accents(text).lower()
    text = text.replace("°", " ")
    text = text.replace("№", " ")
    text = re.sub(r"[\[\]\(\)\{\},;:\/\\\-–—]", " ", text)
    text = re.sub(r"[.]+", " ", text)
    return _collapse_spaces(text)


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text)


def _is_highlighted(run) -> bool:
    color = getattr(run.font, "highlight_color", None)
    if color is None:
        return False
    return color != WD_COLOR_INDEX.AUTO


def _iter_block_items(parent) -> Iterable[Paragraph | Table]:
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


def _iter_paragraphs(parent) -> Iterable[Paragraph]:
    for block in _iter_block_items(parent):
        if isinstance(block, Paragraph):
            yield block
        elif isinstance(block, Table):
            yield from _iter_paragraphs_in_table(block)


def _iter_paragraphs_in_table(table: Table) -> Iterable[Paragraph]:
    seen_cells: set[int] = set()
    for row in table.rows:
        for cell in row.cells:
            cell_id = id(cell._tc)
            if cell_id in seen_cells:
                continue
            seen_cells.add(cell_id)
            yield from _iter_paragraphs(cell)


def _extract_bracket_markers(text: str) -> list[str]:
    markers: list[str] = []
    for match in _BRACKET_RE.finditer(text):
        raw = match.group(1).strip()
        if not raw or re.fullmatch(r"[\s\-\–\—_.,;:\/\\|]+", raw):
            continue
        markers.append(f"[[{raw}]]")
    return markers


def _extract_curly_markers(text: str) -> list[str]:
    markers: list[str] = []
    for match in re.finditer(r"\{\{\s*(.+?)\s*\}\}", text):
        raw = match.group(1).strip()
        if not raw or re.fullmatch(r"[\s\-\–\—_.,;:\/\\|]+", raw):
            continue
        markers.append(f"{{{{{raw}}}}}")
    return markers


def _extract_parenthesis_markers(text: str) -> list[str]:
    matches: list[str] = []
    for match in _PAREN_RE.finditer(text):
        raw = match.group(1).strip()
        normalized = _normalize_for_match(raw)
        tokens = normalized.split()
        if len(raw) < 3 or len(raw) > 80:
            continue
        if not _WORD_RE.search(raw):
            continue
        if raw.endswith("."):
            continue
        if len(tokens) > 12:
            continue
        if not any(word in tokens for word in _PAREN_ALLOWED_WORDS):
            continue
        if normalized in _PAREN_GENERIC_ONLY:
            continue
        if tokens[0] in _PAREN_GENERIC_ONLY:
            continue
        matches.append(f"({raw})")
    return matches


def _extract_highlight_segments(paragraph: Paragraph) -> list[str]:
    segments: list[str] = []
    current: list[str] = []
    for run in paragraph.runs:
        if _is_highlighted(run):
            current.append(run.text)
        else:
            if current:
                raw = _collapse_spaces("".join(current))
                if raw:
                    segments.append(raw)
                current = []
    if current:
        raw = _collapse_spaces("".join(current))
        if raw:
                segments.append(raw)
    return segments


def _is_plausible_highlight_segment(segment: str) -> bool:
    cleaned = _collapse_spaces(segment)
    if len(cleaned) < 3 or len(cleaned) > 100:
        return False
    if not _WORD_RE.search(cleaned):
        return False
    if len(_normalize_for_match(cleaned).split()) > 15:
        return False
    if cleaned.endswith("."):
        return False
    if cleaned.count(".") > 1:
        return False
    if cleaned.count(",") > 2:
        return False
    return True


def _snake_key_and_label(raw_text: str) -> tuple[str, str] | None:
    tokens = [token for token in re.split(r"[^A-Za-z0-9]+", _strip_accents(raw_text)) if token]
    if not tokens:
        return None
    key = "_".join(token.lower() for token in tokens)
    label = " ".join([tokens[0].capitalize()] + [token.lower() for token in tokens[1:]])
    return key, label


def _extract_partner_field(raw_text: str) -> NormalizedField | None:
    cleaned = _normalize_for_match(raw_text)
    if not any(keyword in cleaned for keyword in _PARTNER_KEYWORDS):
        return None

    prefix = None
    for candidate_prefix, keywords in _PARTNER_FIELD_PREFIXES:
        if any(keyword in cleaned for keyword in keywords):
            prefix = candidate_prefix
            break

    if prefix is None:
        key = "pareja_o_conyuge"
        label = "Pareja o conyuge"
    else:
        key = f"{prefix}_pareja_o_conyuge"
        label = f"{prefix.replace('_', ' ').capitalize()} pareja o conyuge"

    return NormalizedField(key=key, label=label, section="Decisiones notariales")


def _extract_field_hint(raw_text: str, marker_type: str) -> NormalizedField | None:
    partner_field = _extract_partner_field(raw_text)
    if partner_field is not None:
        return partner_field

    if marker_type == "curly":
        snake = _snake_key_and_label(raw_text)
        if snake is None:
            return None
        key, label = snake
        cleaned = _normalize_for_match(raw_text)
        section = _classify_section(cleaned, key)
        return NormalizedField(key=key, label=label, section=section)

    cleaned = _normalize_for_match(raw_text)
    if not cleaned:
        return None

    tokens = _tokenize(cleaned)
    if not tokens:
        return None

    alias_root = None
    for token in tokens:
        mapped = _ALIAS_MAP.get(token)
        if mapped and mapped != "indice":
            alias_root = mapped
            break

    if alias_root is None:
        for keyword in _FALLBACK_KEYWORDS:
            if keyword in cleaned:
                alias_root = _ALIAS_MAP.get(keyword, keyword)
                break

    if alias_root is None:
        return None

    index = None
    index_match = _INDEX_RE.search(cleaned)
    if index_match:
        index = int(index_match.group(1))
    else:
        numeric_tokens = [int(token) for token in tokens if token.isdigit()]
        if len(numeric_tokens) == 1 and numeric_tokens[0] <= 9999:
            index = numeric_tokens[0]

    label_root = alias_root.replace("_", " ")
    label = label_root.capitalize()
    if index is not None:
        key = f"{alias_root}_{index}"
        label = f"{label} {index}"
    else:
        key = alias_root

    section = _classify_section(cleaned, alias_root)
    return NormalizedField(key=key, label=label, section=section)


def _classify_section(cleaned_text: str, alias_root: str) -> str:
    for section, keywords in _SECTION_RULES:
        if alias_root in keywords:
            return section
        if any(keyword in cleaned_text for keyword in keywords):
            return section
    return "Otros"


def _add_candidate(
    aggregations: OrderedDict[str, FieldAccumulator],
    raw_marker: str,
    marker_type: str,
) -> None:
    normalized = _extract_field_hint(raw_marker, marker_type)
    if normalized is None:
        return

    accumulator = aggregations.get(normalized.key)
    if accumulator is None:
        accumulator = FieldAccumulator(
            key=normalized.key,
            label=normalized.label,
            section=normalized.section,
        )
        aggregations[normalized.key] = accumulator
    accumulator.add_occurrence(marker_type, raw_marker)


def detect_marked_template(docx_path: str | Path) -> dict:
    path = Path(docx_path)
    doc = Document(str(path))
    aggregations: OrderedDict[str, FieldAccumulator] = OrderedDict()
    marker_type_counts: Counter[str] = Counter()

    for paragraph in _iter_paragraphs(doc):
        text = paragraph.text or ""
        for raw_marker in _extract_bracket_markers(text):
            marker_type_counts["bracket"] += 1
            _add_candidate(aggregations, raw_marker, "bracket")
        for raw_marker in _extract_curly_markers(text):
            marker_type_counts["curly"] += 1
            _add_candidate(aggregations, raw_marker, "curly")
        for raw_marker in _extract_parenthesis_markers(text):
            marker_type_counts["parenthesis"] += 1
            _add_candidate(aggregations, raw_marker, "parenthesis")
        for segment in _extract_highlight_segments(paragraph):
            if not segment:
                continue
            if not _is_plausible_highlight_segment(segment):
                continue
            marker_type_counts["highlight"] += 1
            _add_candidate(aggregations, segment, "highlight")

    fields = [
        {
            "key": accumulator.key,
            "label": accumulator.label,
            "section": accumulator.section,
            "occurrences": accumulator.occurrences,
            "marker_types": sorted(accumulator.marker_types),
            "raw_markers": accumulator.raw_markers,
        }
        for accumulator in aggregations.values()
    ]

    total_occurrences = sum(item["occurrences"] for item in fields)
    return {
        "fields": fields,
        "total_fields": len(fields),
        "total_occurrences": total_occurrences,
        "marker_types": {
            "bracket": marker_type_counts.get("bracket", 0),
            "curly": marker_type_counts.get("curly", 0),
            "parenthesis": marker_type_counts.get("parenthesis", 0),
            "highlight": marker_type_counts.get("highlight", 0),
        },
    }
