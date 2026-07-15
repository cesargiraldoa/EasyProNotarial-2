from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.biblioteca_learning import FieldSignal, NotaryPromptProfile


DEFAULT_PROFILE_SIGNAL_THRESHOLD = 12
MIN_PATTERN_COUNT = 2
MAX_RETRIEVAL_EXAMPLES = 8


def active_profile_payload(db: Session, notary_id: int | None) -> tuple[dict[str, Any] | None, int | None]:
    if notary_id is None:
        return None, None
    profile = (
        db.query(NotaryPromptProfile)
        .filter(NotaryPromptProfile.notary_id == notary_id, NotaryPromptProfile.is_active.is_(True), NotaryPromptProfile.status == "active")
        .order_by(NotaryPromptProfile.version.desc())
        .first()
    )
    if profile is None:
        return None, None
    return {
        "compiled_rules": _json(profile.compiled_rules_json, {}),
        "aliases": _json(profile.aliases_json, {}),
        "positive_patterns": _json(profile.positive_patterns_json, []),
        "negative_patterns": _json(profile.negative_patterns_json, []),
        "field_preferences": _json(profile.field_preferences_json, {}),
    }, profile.version


def retrieve_relevant_examples(
    db: Session,
    *,
    notary_id: int | None,
    document_type: str | None = None,
    section_key: str | None = None,
    role: str | None = None,
    candidate_type: str | None = None,
    limit: int = MAX_RETRIEVAL_EXAMPLES,
) -> list[dict[str, Any]]:
    if notary_id is None:
        return []
    query = db.query(FieldSignal).filter(FieldSignal.notary_id == notary_id)
    if document_type:
        query = query.filter(FieldSignal.document_type == document_type)
    rows = query.order_by(FieldSignal.created_at.desc(), FieldSignal.id.desc()).limit(max(1, limit * 4)).all()
    scored = []
    for row in rows:
        score = 0
        if row.document_type and document_type and row.document_type == document_type:
            score += 40
        if row.section_key and section_key and row.section_key == section_key:
            score += 20
        if row.role and role and row.role == role:
            score += 15
        if row.candidate_type and candidate_type and row.candidate_type == candidate_type:
            score += 10
        score += min(10, int(row.id or 0) % 10)
        scored.append((score, row))
    scored.sort(key=lambda item: (-item[0], -_created_timestamp(item[1]), -(item[1].id or 0)))
    return [_signal_example(row) for _score, row in scored[:limit]]


def maybe_compile_profile(
    db: Session,
    *,
    notary_id: int | None,
    threshold: int = DEFAULT_PROFILE_SIGNAL_THRESHOLD,
) -> NotaryPromptProfile | None:
    if notary_id is None:
        return None
    active = (
        db.query(NotaryPromptProfile)
        .filter(NotaryPromptProfile.notary_id == notary_id, NotaryPromptProfile.is_active.is_(True))
        .order_by(NotaryPromptProfile.version.desc())
        .first()
    )
    last_signal_id = active.last_source_signal_id if active is not None else 0
    pending_count = (
        db.query(func.count(FieldSignal.id))
        .filter(FieldSignal.notary_id == notary_id, FieldSignal.id > (last_signal_id or 0))
        .scalar()
        or 0
    )
    if pending_count < threshold:
        return None
    return compile_profile(db, notary_id=notary_id)


def compile_profile(db: Session, *, notary_id: int) -> NotaryPromptProfile | None:
    signals = (
        db.query(FieldSignal)
        .filter(FieldSignal.notary_id == notary_id)
        .order_by(FieldSignal.id.asc())
        .all()
    )
    if not signals:
        return None

    positives: Counter[str] = Counter()
    negatives: Counter[str] = Counter()
    aliases: dict[str, Counter[str]] = defaultdict(Counter)
    preferences: dict[str, Counter[str]] = defaultdict(Counter)
    for signal in signals:
        key = "|".join(
            [
                signal.document_type or "",
                signal.section_key or "",
                signal.role or "",
                signal.candidate_type or "",
                signal.anonymized_context or "",
            ],
        )
        if signal.human_decision in {"accepted", "changed", "created_field"} and signal.final_field_code:
            positives[key] += 1
            preferences[signal.candidate_type or "unknown"][signal.final_field_code] += 1
            aliases[signal.role or "unknown"][signal.final_field_code] += 1
        elif signal.human_decision == "rejected":
            negatives[key] += 1

    positive_patterns = [key for key, count in positives.items() if count >= MIN_PATTERN_COUNT]
    negative_patterns = [key for key, count in negatives.items() if count >= MIN_PATTERN_COUNT]
    field_preferences = {
        candidate_type: [field for field, _count in counter.most_common(6)]
        for candidate_type, counter in preferences.items()
    }
    aliases_payload = {
        role: [field for field, _count in counter.most_common(6)]
        for role, counter in aliases.items()
    }
    compiled_rules = {
        "min_pattern_count": MIN_PATTERN_COUNT,
        "source_signal_count": len(signals),
        "privacy": "contexts anonymized; exact text stored only as sha256",
    }

    latest_version = (
        db.query(func.max(NotaryPromptProfile.version))
        .filter(NotaryPromptProfile.notary_id == notary_id)
        .scalar()
        or 0
    )
    for existing in db.query(NotaryPromptProfile).filter(NotaryPromptProfile.notary_id == notary_id, NotaryPromptProfile.is_active.is_(True)).all():
        existing.is_active = False
        existing.status = "superseded"

    now = datetime.now(timezone.utc)
    profile = NotaryPromptProfile(
        notary_id=notary_id,
        version=int(latest_version) + 1,
        status="active",
        is_active=True,
        compiled_rules_json=json.dumps(compiled_rules, ensure_ascii=False, sort_keys=True),
        aliases_json=json.dumps(aliases_payload, ensure_ascii=False, sort_keys=True),
        positive_patterns_json=json.dumps(positive_patterns, ensure_ascii=False),
        negative_patterns_json=json.dumps(negative_patterns, ensure_ascii=False),
        field_preferences_json=json.dumps(field_preferences, ensure_ascii=False, sort_keys=True),
        source_signal_count=len(signals),
        last_source_signal_id=max(signal.id for signal in signals),
        generated_at=now,
        activated_at=now,
    )
    db.add(profile)
    db.flush()
    return profile


def _signal_example(signal: FieldSignal) -> dict[str, Any]:
    return {
        "document_type": signal.document_type,
        "section_key": signal.section_key,
        "entity_type": signal.entity_type,
        "role": signal.role,
        "candidate_type": signal.candidate_type,
        "anonymized_context": signal.anonymized_context,
        "human_decision": signal.human_decision,
        "final_field_code": signal.final_field_code,
        "confidence": signal.confidence,
    }


def _created_timestamp(signal: FieldSignal) -> float:
    created_at = getattr(signal, "created_at", None)
    if created_at is None:
        return 0.0
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return created_at.timestamp()


def _json(value: str | None, fallback: Any) -> Any:
    try:
        parsed = json.loads(value or "")
        return parsed if parsed is not None else fallback
    except json.JSONDecodeError:
        return fallback
