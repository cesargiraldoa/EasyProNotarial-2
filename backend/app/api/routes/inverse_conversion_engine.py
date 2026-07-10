from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.services.minuta.inverse_conversion_engine.llm_contracts import EngineFinalResult
from app.services.minuta.inverse_conversion_engine.models import EngineOptions
from app.services.minuta.inverse_conversion_engine.service import InverseConversionEngineService


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
