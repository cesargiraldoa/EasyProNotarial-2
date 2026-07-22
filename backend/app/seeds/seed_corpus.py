from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

ROOT_DIR = Path(__file__).resolve().parents[2]
REPO_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.session import SessionLocal
from app.models.legal_clausula import LegalClausula
from app.models.legal_jurisprudencia import LegalJurisprudencia
from app.models.legal_norma import LegalNorma, LegalNormaRelacion
from app.models.legal_regla import LegalRegla
from app.models.legal_tarifa import LegalTarifa
from app.schemas.legal_corpus import (
    LegalClausulaPayload,
    LegalJurisprudenciaPayload,
    LegalNormaPayload,
    LegalNormaRelacionPayload,
    LegalReglaPayload,
    LegalTarifaPayload,
)

CORPUS_DIR = REPO_DIR / "corpus-juridico"


def _load_json(filename: str) -> list[dict[str, Any]]:
    path = CORPUS_DIR / filename
    return json.loads(path.read_text(encoding="utf-8"))


def _upsert(session: Session, model: type, lookup: dict[str, Any], values: dict[str, Any]) -> tuple[Any, bool]:
    existing = session.execute(select(model).filter_by(**lookup)).scalar_one_or_none()
    if existing is None:
        instance = model(**values)
        session.add(instance)
        return instance, True
    for key, value in values.items():
        setattr(existing, key, value)
    return existing, False


def _norma_id_by_slug(session: Session) -> dict[str, int]:
    rows = session.execute(select(LegalNorma.slug, LegalNorma.id)).all()
    return {slug: norma_id for slug, norma_id in rows}


def _resolve_norma_id(slugs: dict[str, int], slug: str | None, filename: str) -> int | None:
    if slug is None:
        return None
    norma_id = slugs.get(slug)
    if norma_id is None:
        raise ValueError(f"{filename}: norma_slug no existe en normas.json: {slug}")
    return norma_id


def _seed_normas(session: Session) -> dict[str, int]:
    counts = {"created": 0, "updated": 0}
    for raw in _load_json("normas.json"):
        payload = LegalNormaPayload.model_validate(raw)
        values = payload.model_dump()
        _, created = _upsert(session, LegalNorma, {"slug": payload.slug}, values)
        counts["created" if created else "updated"] += 1
    session.flush()
    return counts


def _seed_relaciones(session: Session, norma_ids: dict[str, int]) -> dict[str, int]:
    counts = {"created": 0, "updated": 0}
    for raw in _load_json("norma_relaciones.json"):
        payload = LegalNormaRelacionPayload.model_validate(raw)
        origen_id = _resolve_norma_id(norma_ids, payload.norma_origen_slug, "norma_relaciones.json")
        destino_id = _resolve_norma_id(norma_ids, payload.norma_destino_slug, "norma_relaciones.json")
        values = {
            "norma_origen_id": origen_id,
            "norma_destino_id": destino_id,
            "tipo": payload.tipo,
            "articulo_afectado": payload.articulo_afectado,
            "fecha_efecto": payload.fecha_efecto,
            "notas": payload.notas,
        }
        stmt = (
            select(LegalNormaRelacion)
            .where(LegalNormaRelacion.norma_origen_id == origen_id)
            .where(LegalNormaRelacion.norma_destino_id == destino_id)
            .where(LegalNormaRelacion.tipo == payload.tipo)
        )
        if payload.articulo_afectado is None:
            stmt = stmt.where(LegalNormaRelacion.articulo_afectado.is_(None))
        else:
            stmt = stmt.where(LegalNormaRelacion.articulo_afectado == payload.articulo_afectado)
        existing = session.execute(stmt).scalar_one_or_none()
        if existing is None:
            session.add(LegalNormaRelacion(**values))
            counts["created"] += 1
            continue
        for key, value in values.items():
            setattr(existing, key, value)
        counts["updated"] += 1
    session.flush()
    return counts


def _seed_clausulas(session: Session, norma_ids: dict[str, int]) -> dict[str, int]:
    counts = {"created": 0, "updated": 0}
    for raw in _load_json("clausulas.json"):
        payload = LegalClausulaPayload.model_validate(raw)
        values = payload.model_dump(exclude={"norma_slug"})
        values["norma_id"] = _resolve_norma_id(norma_ids, payload.norma_slug, "clausulas.json")
        _, created = _upsert(
            session,
            LegalClausula,
            {"acto_code": payload.acto_code, "orden": payload.orden},
            values,
        )
        counts["created" if created else "updated"] += 1
    session.flush()
    return counts


def _seed_reglas(session: Session, norma_ids: dict[str, int]) -> dict[str, int]:
    counts = {"created": 0, "updated": 0}
    for raw in _load_json("reglas.json"):
        payload = LegalReglaPayload.model_validate(raw)
        values = payload.model_dump(exclude={"norma_slug"})
        values["norma_id"] = _resolve_norma_id(norma_ids, payload.norma_slug, "reglas.json")
        _, created = _upsert(session, LegalRegla, {"codigo": payload.codigo}, values)
        counts["created" if created else "updated"] += 1
    session.flush()
    return counts


def _seed_tarifas(session: Session, norma_ids: dict[str, int]) -> dict[str, int]:
    counts = {"created": 0, "updated": 0}
    for raw in _load_json("tarifas.json"):
        payload = LegalTarifaPayload.model_validate(raw)
        values = payload.model_dump(exclude={"norma_slug"})
        values["norma_id"] = _resolve_norma_id(norma_ids, payload.norma_slug, "tarifas.json")
        _, created = _upsert(
            session,
            LegalTarifa,
            {"anio": payload.anio, "concepto": payload.concepto},
            values,
        )
        counts["created" if created else "updated"] += 1
    session.flush()
    return counts


def _seed_jurisprudencia(session: Session, norma_ids: dict[str, int]) -> dict[str, int]:
    counts = {"created": 0, "updated": 0}
    for raw in _load_json("jurisprudencia.json"):
        payload = LegalJurisprudenciaPayload.model_validate(raw)
        values = payload.model_dump(exclude={"norma_relacionada_slug"})
        values["norma_relacionada_id"] = _resolve_norma_id(
            norma_ids,
            payload.norma_relacionada_slug,
            "jurisprudencia.json",
        )
        _, created = _upsert(
            session,
            LegalJurisprudencia,
            {"tipo": payload.tipo, "numero": payload.numero, "anio": payload.anio},
            values,
        )
        counts["created" if created else "updated"] += 1
    session.flush()
    return counts


def seed_corpus(session: Session) -> dict[str, dict[str, int]]:
    results = {"normas": _seed_normas(session)}
    norma_ids = _norma_id_by_slug(session)
    results["norma_relaciones"] = _seed_relaciones(session, norma_ids)
    results["clausulas"] = _seed_clausulas(session, norma_ids)
    results["reglas"] = _seed_reglas(session, norma_ids)
    results["tarifas"] = _seed_tarifas(session, norma_ids)
    results["jurisprudencia"] = _seed_jurisprudencia(session, norma_ids)
    session.commit()
    return results


def main() -> None:
    with SessionLocal() as session:
        results = seed_corpus(session)
    summary = ", ".join(
        f"{name}: +{counts['created']}/~{counts['updated']}" for name, counts in results.items()
    )
    print(f"[OK] Corpus jurídico cargado ({summary}).")


if __name__ == "__main__":
    main()
