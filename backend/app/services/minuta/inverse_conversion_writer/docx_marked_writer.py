from __future__ import annotations

import re
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

from docx import Document
from docx.document import Document as DocxDocument
from docx.oxml import OxmlElement
from docx.shared import RGBColor
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph
from docx.text.run import Run

from app.services.minuta.inverse_conversion_catalog.field_code_normalizer import FieldCodeNormalizer
from app.services.minuta.inverse_conversion_writer.models import MarkedCandidate, MarkedDocxWriteResult

RED_COLOR = RGBColor(0xFF, 0x00, 0x00)
FIELD_CODE_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*$")


@dataclass(frozen=True)
class PreparedCandidate:
    candidate: MarkedCandidate
    marker: str
    locations: frozenset[str]


@dataclass(frozen=True)
class PlannedReplacement:
    start: int
    end: int
    marker: str
    candidate_id: str
    original_text: str


class DocxMarkedWriter:
    def __init__(self, normalizer: FieldCodeNormalizer | None = None) -> None:
        self.normalizer = normalizer or FieldCodeNormalizer()

    def write(
        self,
        source_path: str | Path,
        destination_path: str | Path,
        candidates: list[MarkedCandidate],
        output_filename: str | None = None,
        allowed_field_codes: set[str] | None = None,
        field_aliases: dict[str, str] | None = None,
        ambiguous_field_aliases: dict[str, set[str]] | None = None,
    ) -> MarkedDocxWriteResult:
        accepted = [candidate for candidate in candidates if candidate.is_accepted]
        if not accepted:
            raise ValueError("No hay candidatos aceptados para marcar.")

        prepared_candidates = self._prepare_candidates(
            accepted,
            allowed_field_codes or set(),
            field_aliases or {},
            ambiguous_field_aliases or {},
        )

        document = Document(str(source_path))
        marked_occurrences = self._mark_candidates(document, prepared_candidates)
        if marked_occurrences == 0:
            raise ValueError(
                "Ningun candidato aceptado pudo ubicarse en el documento con la location y el contexto suministrados."
            )

        destination = Path(destination_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        document.save(str(destination))
        return MarkedDocxWriteResult(
            output_path=destination,
            filename=output_filename or marked_docx_filename(Path(source_path).name),
            accepted_candidates=len(accepted),
            marked_occurrences=marked_occurrences,
            skipped_candidates=len(candidates) - len(accepted),
        )

    def _dedupe_candidates(self, candidates: list[MarkedCandidate]) -> list[MarkedCandidate]:
        seen: set[tuple[str, str, str, tuple[tuple[str, str, str], ...]]] = set()
        deduped: list[MarkedCandidate] = []
        for candidate in candidates:
            contexts = tuple(sorted((context.location, context.before, context.after) for context in candidate.contexts))
            key = (
                candidate.text,
                candidate.canonical_field_code,
                candidate.suggested_key,
                contexts,
            )
            if key in seen:
                continue
            seen.add(key)
            deduped.append(candidate)
        return sorted(deduped, key=lambda item: len(item.text), reverse=True)

    def _prepare_candidates(
        self,
        candidates: list[MarkedCandidate],
        allowed_field_codes: set[str],
        field_aliases: dict[str, str],
        ambiguous_field_aliases: dict[str, set[str]],
    ) -> list[PreparedCandidate]:
        allowed = {self.normalizer.normalize(code) for code in allowed_field_codes if self.normalizer.normalize(code)}
        if not allowed:
            raise ValueError("No hay catalogo de field_definitions disponible para validar marcadores.")
        aliases = {
            self.normalizer.normalize(raw): self.normalizer.normalize(canonical)
            for raw, canonical in field_aliases.items()
            if self.normalizer.normalize(raw) and self.normalizer.normalize(canonical)
        }
        ambiguous_aliases = {
            self.normalizer.normalize(raw): {self.normalizer.normalize(canonical) for canonical in canonicals}
            for raw, canonicals in ambiguous_field_aliases.items()
            if self.normalizer.normalize(raw)
        }

        prepared: list[PreparedCandidate] = []
        for candidate in self._dedupe_candidates(candidates):
            code = self._resolve_canonical_code(candidate, allowed, aliases, ambiguous_aliases)
            marker = f"{{{{{code}}}}}"
            locations = frozenset(context.location for context in candidate.contexts if context.location)
            prepared.append(PreparedCandidate(candidate=candidate, marker=marker, locations=locations))
        return prepared

    def _resolve_canonical_code(
        self,
        candidate: MarkedCandidate,
        allowed_field_codes: set[str],
        field_aliases: dict[str, str],
        ambiguous_field_aliases: dict[str, set[str]],
    ) -> str:
        explicit = self.normalizer.normalize(candidate.canonical_field_code)
        if explicit:
            self._validate_code(explicit, allowed_field_codes, candidate)
            return explicit

        source = self.normalizer.normalize(candidate.suggested_key)
        if not source:
            raise ValueError(f"El candidato {candidate.id or candidate.text!r} no tiene codigo canonico aprobado.")
        if source in ambiguous_field_aliases:
            targets = ", ".join(sorted(ambiguous_field_aliases[source]))
            raise ValueError(
                f"Alias ambiguo para {source}: apunta a multiples codigos canonicos permitidos ({targets})."
            )

        for option in (source, field_aliases.get(source), self.normalizer.suggest_canonical(source, allowed_field_codes)[0]):
            normalized = self.normalizer.normalize(option)
            if normalized and normalized in allowed_field_codes:
                self._validate_code(normalized, allowed_field_codes, candidate)
                return normalized

        compatible = sorted(code for code in allowed_field_codes if self.normalizer.can_alias(source, code))
        if len(compatible) == 1:
            self._validate_code(compatible[0], allowed_field_codes, candidate)
            return compatible[0]

        raise ValueError(
            f"El candidato {candidate.id or candidate.text!r} no tiene un canonical_field_code valido en field_definitions."
        )

    @staticmethod
    def _validate_code(code: str, allowed_field_codes: set[str], candidate: MarkedCandidate) -> None:
        if not FIELD_CODE_PATTERN.fullmatch(code):
            raise ValueError(f"Codigo canonico invalido para candidato {candidate.id or candidate.text!r}: {code!r}.")
        if code not in allowed_field_codes:
            raise ValueError(f"Codigo canonico fuera del catalogo field_definitions: {code}.")

    def _mark_candidates(self, document, candidates: list[PreparedCandidate]) -> int:
        total = 0
        for paragraph, location in iter_docx_paragraphs(document):
            replacements = plan_replacements_for_paragraph(paragraph.text or "", location, candidates)
            for replacement in reversed(replacements):
                affected = _affected_runs(paragraph, replacement.start, replacement.end)
                if not affected:
                    continue
                _replace_affected_runs(paragraph, affected, replacement.start, replacement.end, replacement.marker, RED_COLOR)
                total += 1
        return total


def plan_replacements_for_paragraph(
    paragraph_text: str,
    location: str,
    candidates: list[PreparedCandidate],
) -> list[PlannedReplacement]:
    planned: list[PlannedReplacement] = []
    for prepared in candidates:
        if prepared.locations and location not in prepared.locations:
            continue
        planned.extend(_candidate_replacements(paragraph_text, location, prepared))
    return _without_overlaps(planned)


def _candidate_replacements(paragraph_text: str, location: str, prepared: PreparedCandidate) -> list[PlannedReplacement]:
    candidate = prepared.candidate
    target = candidate.text.strip()
    if not target:
        return []
    matches = [
        match
        for match in re.finditer(re.escape(target), paragraph_text)
        if not _inside_existing_curly_marker(paragraph_text, match.start(), match.end())
    ]
    if not matches:
        return []

    contexts = [context for context in candidate.contexts if not context.location or context.location == location]
    selected = []
    if contexts:
        for match in matches:
            if any(_context_matches(paragraph_text, match.start(), match.end(), context.before, context.after) for context in contexts):
                selected.append(match)
        if not selected:
            return []
    elif len(matches) == 1 or int(candidate.occurrences or 0) > 1:
        selected = matches
    else:
        return []

    return [
        PlannedReplacement(
            start=match.start(),
            end=match.end(),
            marker=prepared.marker,
            candidate_id=candidate.id,
            original_text=target,
        )
        for match in selected
    ]


def _context_matches(paragraph_text: str, start: int, end: int, before: str, after: str) -> bool:
    before = _collapse_context(before)
    after = _collapse_context(after)
    if not before and not after:
        return True
    paragraph_before = _collapse_context(paragraph_text[:start])
    paragraph_after = _collapse_context(paragraph_text[end:])
    before_ok = not before or paragraph_before.endswith(before)
    after_ok = not after or paragraph_after.startswith(after)
    return before_ok and after_ok


def _collapse_context(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _inside_existing_curly_marker(text: str, start: int, end: int) -> bool:
    marker_start = text.rfind("{{", 0, start)
    marker_end_before = text.rfind("}}", 0, start)
    if marker_start <= marker_end_before:
        return False
    marker_end_after = text.find("}}", end)
    return marker_end_after != -1


def _without_overlaps(replacements: list[PlannedReplacement]) -> list[PlannedReplacement]:
    _raise_on_exact_marker_conflicts(replacements)
    ordered = sorted(replacements, key=lambda item: (item.start, -(item.end - item.start), item.marker))
    accepted: list[PlannedReplacement] = []
    occupied: list[tuple[int, int]] = []
    seen_exact: set[tuple[int, int, str]] = set()
    for replacement in ordered:
        exact_key = (replacement.start, replacement.end, replacement.marker)
        if exact_key in seen_exact:
            continue
        if any(not (replacement.end <= start or replacement.start >= end) for start, end in occupied):
            continue
        seen_exact.add(exact_key)
        occupied.append((replacement.start, replacement.end))
        accepted.append(replacement)
    return sorted(accepted, key=lambda item: item.start)


def _raise_on_exact_marker_conflicts(replacements: list[PlannedReplacement]) -> None:
    by_range: dict[tuple[int, int], list[PlannedReplacement]] = {}
    for replacement in replacements:
        by_range.setdefault((replacement.start, replacement.end), []).append(replacement)
    for (start, end), items in by_range.items():
        markers = {item.marker for item in items}
        if len(markers) <= 1:
            continue
        candidate_ids = ", ".join(sorted({item.candidate_id or "sin_id" for item in items}))
        marker_list = ", ".join(sorted(markers))
        raise ValueError(
            f"Reemplazo ambiguo: multiples codigos canonicos intentan reemplazar el mismo rango "
            f"{start}-{end} ({marker_list}) para candidatos {candidate_ids}."
        )


def marked_docx_filename(original_filename: str) -> str:
    path = Path(original_filename)
    stem = path.stem or "documento"
    return f"{stem} - marcado.docx"


def iter_docx_paragraphs(docx_document):
    yield from _iter_blocks(docx_document)


def _iter_blocks(parent, prefix: str = ""):
    paragraph_index = 0
    table_index = 0
    for block in _iter_block_items(parent):
        if isinstance(block, Paragraph):
            paragraph_index += 1
            location = f"{prefix}paragraph {paragraph_index}" if prefix else f"paragraph {paragraph_index}"
            yield block, location
        elif isinstance(block, Table):
            table_index += 1
            yield from _iter_table_blocks(block, table_index)


def _iter_table_blocks(table: Table, table_index: int):
    seen_cells: set[int] = set()
    for row_index, row in enumerate(table.rows, start=1):
        for cell_index, cell in enumerate(row.cells, start=1):
            cell_id = id(cell._tc)
            if cell_id in seen_cells:
                continue
            seen_cells.add(cell_id)
            prefix = f"table {table_index} row {row_index} cell {cell_index} "
            yield from _iter_blocks(cell, prefix=prefix)


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


def mark_text_in_paragraph(paragraph, text: str, marker: str | None = None) -> int:
    target = text.strip()
    if not target:
        return 0
    replacement = marker or target
    matches = list(re.finditer(re.escape(target), paragraph.text or ""))
    marked = 0
    for match in reversed(matches):
        affected = _affected_runs(paragraph, match.start(), match.end())
        if not affected:
            continue
        _replace_affected_runs(paragraph, affected, match.start(), match.end(), replacement, RED_COLOR)
        marked += 1
    return marked


def _affected_runs(paragraph, start: int, end: int) -> list[dict]:
    runs_info: list[dict] = []
    position = 0
    for run in paragraph.runs:
        run_end = position + len(run.text)
        runs_info.append({"run": run, "start": position, "end": run_end})
        position = run_end
    return [info for info in runs_info if info["end"] > start and info["start"] < end]


def _replace_affected_runs(paragraph, affected: list[dict], start: int, end: int, value: str, color: RGBColor) -> None:
    first = affected[0]
    last = affected[-1]
    first_run = first["run"]
    last_run = last["run"]
    prefix = first_run.text[: start - first["start"]]
    suffix = last_run.text[end - last["start"] :]
    first_run.text = prefix
    for info in affected[1:]:
        info["run"].text = ""
    inserted = _insert_run_after(paragraph, first_run, value, template_run=first_run, color=color)
    if suffix:
        _insert_run_after(paragraph, inserted, suffix, template_run=last_run)


def _insert_run_after(paragraph, anchor_run, text: str, template_run=None, color: RGBColor | None = None):
    new_r = OxmlElement("w:r")
    anchor_run._r.addnext(new_r)
    new_run = Run(new_r, paragraph)
    if template_run is not None and template_run._r.rPr is not None:
        new_run._r.insert(0, deepcopy(template_run._r.rPr))
    new_run.text = text
    if color is not None and text:
        new_run.font.color.rgb = color
    return new_run
