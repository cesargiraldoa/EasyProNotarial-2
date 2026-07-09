from __future__ import annotations

from collections import OrderedDict

from app.services.minuta.reverse_template_builder.models import Candidate, CandidateOccurrence


def group_candidates(occurrences: list[CandidateOccurrence]) -> list[Candidate]:
    grouped: OrderedDict[tuple[str, str], Candidate] = OrderedDict()

    for occurrence in occurrences:
        key = (occurrence.text, occurrence.suggested_key)
        candidate = grouped.get(key)
        if candidate is None:
            candidate = Candidate(
                id="",
                text=occurrence.text,
                suggested_key=occurrence.suggested_key,
                label=occurrence.label,
                section=occurrence.section,
                type=occurrence.type,
                confidence=occurrence.confidence,
                occurrences=0,
                contexts=[],
            )
            grouped[key] = candidate
        candidate.occurrences += 1
        candidate.contexts.append(occurrence.context)
        candidate.confidence = min(0.99, max(candidate.confidence, occurrence.confidence) + min(0.06, (candidate.occurrences - 1) * 0.02))

    candidates = list(grouped.values())
    candidates.sort(key=lambda item: (-item.confidence, item.section, item.suggested_key, item.text))
    for index, candidate in enumerate(candidates, start=1):
        candidate.id = f"cand_{index:03d}"
    return candidates
