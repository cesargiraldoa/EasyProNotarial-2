from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.services.minuta.reverse_template_builder import SingleDocumentReverseTemplateBuilder

router = APIRouter(prefix="/template-builder", tags=["template-builder"])


@router.post("/reverse/single/analyze")
async def analyze_single_document_reverse_template(
    archivo: UploadFile = File(..., description="Archivo .docx de minuta diligenciada"),
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

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        return SingleDocumentReverseTemplateBuilder().analyze(tmp_path, archivo.filename)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"No fue posible analizar el documento .docx: {exc}",
        ) from exc
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)
