import json
import tempfile
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.models.user import User
from app.services.minuta.detector import analizar_documento
from app.services.minuta.reemplazador import aplicar_reemplazos_docx, construir_lista_reemplazos

router = APIRouter(prefix="/minuta", tags=["minuta"])


def _get_api_key() -> str:
    key = get_settings().openai_api_key
    if not key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPENAI_API_KEY no configurada en el servidor.",
        )
    return key


@router.post("/analizar")
async def analizar_minuta(
    archivo: UploadFile = File(..., description="Archivo .docx de la minuta a analizar"),
    current_user: User = Depends(get_current_user),
):
    """
    Recibe un .docx, detecta si es B1 (plantilla en blanco) o B2 (ya diligenciada)
    y extrae personas, valores, inmueble, actos y decisiones.
    """
    if not archivo.filename or not archivo.filename.lower().endswith(".docx"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El archivo debe ser un .docx válido.",
        )

    api_key = _get_api_key()

    # Guardar upload en archivo temporal
    suffix = Path(archivo.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await archivo.read())
        tmp_path = tmp.name

    try:
        resultado = analizar_documento(tmp_path, api_key)
    except Exception as exc:
        Path(tmp_path).unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al analizar el documento: {exc}",
        )

    Path(tmp_path).unlink(missing_ok=True)
    return resultado


@router.post("/generar")
async def generar_minuta(
    background_tasks: BackgroundTasks,
    archivo: UploadFile = File(..., description="Archivo .docx base con los datos anteriores"),
    datos_anteriores: str = Form(..., description="JSON con datos del caso anterior (salida de /analizar)"),
    datos_nuevos: str = Form(..., description="JSON con los nuevos datos a aplicar (misma estructura)"),
    current_user: User = Depends(get_current_user),
):
    """
    Recibe el .docx original + datos_anteriores + datos_nuevos.
    Aplica los reemplazos preservando el formato Word y devuelve el .docx modificado.
    """
    if not archivo.filename or not archivo.filename.lower().endswith(".docx"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El archivo debe ser un .docx válido.",
        )

    try:
        datos_ant = json.loads(datos_anteriores)
        datos_nv = json.loads(datos_nuevos)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"JSON inválido en datos_anteriores o datos_nuevos: {exc}",
        )

    # Archivos temporales: entrada y salida
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_in:
        tmp_in.write(await archivo.read())
        path_entrada = tmp_in.name

    tmp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    path_salida = tmp_out.name
    tmp_out.close()

    try:
        reemplazos = construir_lista_reemplazos(datos_ant, datos_nv)
        estadisticas = aplicar_reemplazos_docx(path_entrada, reemplazos, path_salida)
    except Exception as exc:
        Path(path_entrada).unlink(missing_ok=True)
        Path(path_salida).unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al aplicar reemplazos: {exc}",
        )

    Path(path_entrada).unlink(missing_ok=True)

    nombre_salida = f"minuta_generada_{Path(archivo.filename).stem}.docx"

    # Limpiar el archivo de salida después de enviar la respuesta
    background_tasks.add_task(Path(path_salida).unlink, missing_ok=True)

    return FileResponse(
        path=path_salida,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=nombre_salida,
        headers={"X-Reemplazos-Total": str(estadisticas["total_reemplazos"])},
    )
