from __future__ import annotations

from app.services.minuta.inverse_conversion_writer.docx_marked_writer import (
    DocxMarkedWriter,
    PreparedCandidate,
)
from app.services.minuta.inverse_conversion_writer.models import MarkedCandidate


class TolerantDocxMarkedWriter(DocxMarkedWriter):
    """Prepare every safe candidate without aborting for one unmapped field.

    Reverse conversion is a human-review workflow. A candidate that still lacks a
    canonical catalog assignment must remain pending instead of blocking the valid
    candidates selected by the protocolist.
    """

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
            try:
                code = self._resolve_canonical_code(candidate, allowed, aliases, ambiguous_aliases)
            except ValueError:
                # The candidate stays reviewable in the UI, but it is not written
                # until a protocolist assigns or creates a valid field.
                continue
            marker = f"{{{{{code}}}}}"
            locations = frozenset(context.location for context in candidate.contexts if context.location)
            prepared.append(PreparedCandidate(candidate=candidate, marker=marker, locations=locations))

        if not prepared:
            raise ValueError(
                "Ningun candidato aceptado tiene un campo canonico valido. Cambie, cree u omita al menos un candidato."
            )
        return prepared


__all__ = ["TolerantDocxMarkedWriter"]
