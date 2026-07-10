from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.services.minuta.inverse_conversion_engine.llm_contracts import EngineFinalResult
from app.services.minuta.inverse_conversion_engine.models import EngineOptions
from app.services.minuta.inverse_conversion_engine.service import InverseConversionEngineService
from app.services.minuta.inverse_conversion_writer.models import MarkedCandidate
from app.services.minuta.inverse_conversion_writer.service import InverseConversionMarkedDocxService


router = APIRouter(prefix="/inverse-conversion", tags=["inverse-conversion-engine"])


class AnalyzeOptions(BaseModel):
    use_llm: bool = False
    use_semantic: bool = False
    persist_audit: bool = True
    limit: int = Field(default=8, ge=1, le=50)


class AnalyzeRequest(BaseModel):
    text: str | None = None
    marker: str | None = None
    context_before: str | None = None
    context_after: str | None = None
    options: AnalyzeOptions = Field(default_factory=AnalyzeOptions)


@router.post("/analyze", response_model=EngineFinalResult)
def analyze_inverse_conversion(payload: AnalyzeRequest, db: Session = Depends(get_db)) -> Any:
    service = InverseConversionEngineService(db)
    options = EngineOptions(
        use_llm=payload.options.use_llm,
        use_semantic=payload.options.use_semantic,
        persist_audit=payload.options.persist_audit,
        limit=payload.options.limit,
    )
    if payload.marker:
        return service.analyze_marker(payload.marker, payload.context_before, payload.context_after, options=options)
    if payload.text:
        return service.analyze_text(payload.text, options=options)
    raise HTTPException(status_code=422, detail="Provide text or marker.")


@router.post("/generate-marked-docx")
async def generate_marked_docx(
    archivo: UploadFile = File(..., description="Archivo .docx original diligenciado"),
    candidates: str = Form(..., description="Candidatos revisados en JSON"),
):
    if not archivo.filename or not archivo.filename.lower().endswith(".docx"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El archivo debe ser un .docx valido.",
        )

    content = await archivo.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El archivo esta vacio.",
        )

    reviewed_candidates = _parse_marked_candidates(candidates)
    if not any(candidate.is_accepted for candidate in reviewed_candidates):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Debes aceptar al menos un candidato antes de generar el DOCX marcado.",
        )

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            source_path = Path(tmp_dir) / "source.docx"
            output_path = Path(tmp_dir) / "marked.docx"
            source_path.write_bytes(content)
            result = InverseConversionMarkedDocxService().generate(
                source_path=source_path,
                destination_path=output_path,
                original_filename=archivo.filename,
                candidates=reviewed_candidates,
            )
            output_bytes = result.output_path.read_bytes()
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"No fue posible generar el DOCX marcado: {exc}",
        ) from exc

    encoded_filename = quote(result.filename)
    return Response(
        content=output_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"},
    )


def _parse_marked_candidates(raw_candidates: str) -> list[MarkedCandidate]:
    try:
        payload = json.loads(raw_candidates)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El listado de candidatos no es JSON valido.",
        ) from exc
    if not isinstance(payload, list):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El listado de candidatos debe ser un arreglo.",
        )
    return [MarkedCandidate.from_dict(item) for item in payload if isinstance(item, dict)]
