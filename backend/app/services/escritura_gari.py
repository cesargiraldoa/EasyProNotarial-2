from __future__ import annotations

import io
import json
import logging
import re
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Protocol

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.services.document_generation import extract_text_from_docx
from app.services.gari_document_service import get_openai_client

logger = logging.getLogger(__name__)

PROMPT_VERSION = "escritura-gari-v1-2026-07-21"
AI_VALIDATION_LABEL = "por validar"

ALLOWED_ACTOS = {"compraventa", "hipoteca", "cancelacion"}
KNOWN_RAMOS = {
    "afectacion_vivienda_familiar",
    "patrimonio_familia",
    "hipoteca",
    "cancelacion_hipoteca",
    "vis_vip",
    "propiedad_horizontal",
    "representacion_apoderado",
    "persona_juridica",
    "retencion_fuente",
    "registro",
    "laf_t",
    "firma_fuera_sede",
    "precio_forma_pago",
}


class GariLLMClient(Protocol):
    model_version: str

    def complete_json(self, *, purpose: str, prompt: str) -> dict[str, Any]:
        ...

    def complete_text(self, *, purpose: str, prompt: str) -> str:
        ...


@dataclass(frozen=True)
class UploadText:
    filename: str
    text: str


class OpenAIGariLLMClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.model_version = settings.gari_model
        self._client = get_openai_client()

    def complete_json(self, *, purpose: str, prompt: str) -> dict[str, Any]:
        logger.info("Gari prompt purpose=%s model=%s prompt=%s", purpose, self.model_version, prompt)
        response = self._client.chat.completions.create(
            model=self.model_version,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _system_prompt()},
                {"role": "user", "content": prompt},
            ],
        )
        content = response.choices[0].message.content or "{}"
        return _json_object(content)

    def complete_text(self, *, purpose: str, prompt: str) -> str:
        logger.info("Gari prompt purpose=%s model=%s prompt=%s", purpose, self.model_version, prompt)
        response = self._client.chat.completions.create(
            model=self.model_version,
            temperature=0,
            messages=[
                {"role": "system", "content": _system_prompt()},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content or ""


def get_gari_llm_client() -> GariLLMClient:
    return OpenAIGariLLMClient()


def _system_prompt() -> str:
    return (
        "Eres Gari, asistente notarial de EasyPro. Gari asiste, no decide. "
        "Nunca generas clausulas obligatorias, cifras ni citas por cuenta propia. "
        "Todo resultado es sugerencia por validar por humano. No inventes datos; "
        "si falta evidencia, devuelve vacio o confianza baja. Responde exactamente "
        "en el formato solicitado."
    )


def _json_object(content: str) -> dict[str, Any]:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        parsed = json.loads(match.group(0)) if match else {}
    return parsed if isinstance(parsed, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _confidence(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.5
    return max(0.0, min(1.0, number))


def _clip(text: str, limit: int) -> str:
    clean = re.sub(r"\s+", " ", text).strip()
    return clean[:limit]


def _strip_cite_spans(html: str) -> str:
    return re.sub(r"<span[^>]*class=[\"'][^\"']*\bcite\b[^\"']*[\"'][^>]*>.*?</span>", "", html, flags=re.IGNORECASE | re.DOTALL)


def _sanitize_clause_html(html: str) -> str:
    clean = re.sub(r"<script\b[^>]*>.*?</script>", "", html, flags=re.IGNORECASE | re.DOTALL)
    clean = re.sub(r"<style\b[^>]*>.*?</style>", "", clean, flags=re.IGNORECASE | re.DOTALL)
    clean = _strip_cite_spans(clean).strip()
    if not re.search(r"<p\b", clean, flags=re.IGNORECASE):
        clean = f'<p class="cl">{clean}</p>'
    return clean


async def extract_upload_text(filename: str | None, content: bytes) -> UploadText:
    safe_filename = filename or "documento"
    suffix = Path(safe_filename).suffix.lower()
    if suffix == ".docx":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)
        try:
            return UploadText(filename=safe_filename, text=extract_text_from_docx(tmp_path))
        finally:
            tmp_path.unlink(missing_ok=True)

    if suffix in {".txt", ".md", ".html", ".htm"}:
        return UploadText(filename=safe_filename, text=content.decode("utf-8", errors="ignore"))

    try:
        from unstructured.partition.auto import partition

        elements = partition(file=io.BytesIO(content), filename=safe_filename)
        return UploadText(filename=safe_filename, text="\n".join(str(item) for item in elements))
    except Exception:
        text = content.decode("utf-8", errors="ignore")
        return UploadText(filename=safe_filename, text=text)


def proponer_campos_desde_texto(llm: GariLLMClient, *, filename: str, text: str) -> dict[str, Any]:
    prompt = json.dumps(
        {
            "tarea": "extraer_sugerencias_case_state",
            "prompt_version": PROMPT_VERSION,
            "guardrails": [
                "No sobrescribas datos del caso.",
                "Extrae solo valores literalmente soportados por el documento.",
                "Cada sugerencia debe incluir campo, valor, confianza 0..1 y fuente textual breve.",
            ],
            "campos_prioritarios": [
                "matricula",
                "cMatricula",
                "linderos",
                "inmdesc",
                "cInmdesc",
                "catastral",
                "cCatastral",
                "nupre",
                "tituloNum",
                "tituloFecha",
                "tituloNotaria",
                "cHipEP",
                "cHipFecha",
                "cHipNotaria",
                "cHipRegFecha",
                "cBanco",
                "cBancoNit",
                "cDeudor",
                "V.0.nombre",
                "V.0.id",
                "C.0.nombre",
                "C.0.id",
            ],
            "archivo": filename,
            "texto": _clip(text, 14000),
            "salida_json": {"sugerencias": {"campo": {"valor": "string", "confianza": 0.0, "fuente": "cita textual"}}},
        },
        ensure_ascii=False,
    )
    raw = _as_dict(llm.complete_json(purpose="extraccion", prompt=prompt).get("sugerencias"))
    sugerencias: dict[str, dict[str, Any]] = {}
    for campo, spec in raw.items():
        item = _as_dict(spec)
        valor = item.get("valor")
        if valor in (None, "", []):
            continue
        sugerencias[str(campo)] = {
            "valor": valor,
            "confianza": _confidence(item.get("confianza")),
            "fuente": str(item.get("fuente") or filename),
        }
    return {
        "sugerencias": sugerencias,
        "por_validar": True,
        "estado": AI_VALIDATION_LABEL,
        "modelo": llm.model_version,
        "prompt_version": PROMPT_VERSION,
    }


def redactar_prosa(llm: GariLLMClient, *, acto: str, contexto: dict[str, Any], instruccion: str) -> dict[str, Any]:
    prompt = json.dumps(
        {
            "tarea": "redactar_clausula_atipica",
            "prompt_version": PROMPT_VERSION,
            "acto": acto,
            "contexto": contexto,
            "instruccion": instruccion,
            "guardrails": [
                "Redacta solo una sugerencia de prosa atipica en estilo notarial.",
                "No redactes clausulas obligatorias.",
                "No calcules ni inventes cifras.",
                "No agregues citas legales ni span.cite.",
                "Devuelve HTML editable en un bloque p.cl o p.para.",
            ],
        },
        ensure_ascii=False,
    )
    html = _sanitize_clause_html(llm.complete_text(purpose="prosa", prompt=prompt))
    return {
        "html_sugerido": html,
        "sugerencia": True,
        "estado": AI_VALIDATION_LABEL,
        "modelo": llm.model_version,
        "prompt_version": PROMPT_VERSION,
    }


def clasificar_acto(llm: GariLLMClient, *, descripcion: str, mapa_situaciones: str) -> dict[str, Any]:
    prompt = json.dumps(
        {
            "tarea": "clasificar_acto_escritura",
            "prompt_version": PROMPT_VERSION,
            "descripcion": descripcion,
            "actos_permitidos": sorted(ALLOWED_ACTOS),
            "ramas_permitidas": sorted(KNOWN_RAMOS),
            "mapa_situaciones_resumen": _clip(mapa_situaciones, 12000),
            "guardrails": [
                "Sugiere, no decidas.",
                "Usa solo actos y ramas permitidas.",
                "No inventes subactos fuera del mapa.",
            ],
            "salida_json": {"acto_sugerido": "compraventa", "ramas": ["hipoteca"]},
        },
        ensure_ascii=False,
    )
    parsed = llm.complete_json(purpose="clasificacion", prompt=prompt)
    acto = str(parsed.get("acto_sugerido") or "").strip()
    if acto not in ALLOWED_ACTOS:
        acto = "compraventa"
    ramas = [str(item) for item in _as_list(parsed.get("ramas")) if str(item) in KNOWN_RAMOS]
    return {
        "acto_sugerido": acto,
        "ramas": ramas,
        "sugerencia": True,
        "estado": AI_VALIDATION_LABEL,
        "modelo": llm.model_version,
        "prompt_version": PROMPT_VERSION,
    }


def revisar_escritura(
    llm: GariLLMClient,
    session: Session,
    *,
    acto: str,
    corpus_acto_code: str,
    fecha: date,
    html_o_texto: str,
    rag_searcher,
) -> dict[str, Any]:
    grounding = rag_searcher(session, _clip(html_o_texto, 1200), fecha, acto_code=corpus_acto_code, top_k=6)
    evidencias = [
        {
            "cita_slug": getattr(item, "source_ref", ""),
            "titulo": getattr(item, "titulo", ""),
            "texto": _clip(getattr(item, "chunk_text", ""), 800),
        }
        for item in grounding
    ]
    prompt = json.dumps(
        {
            "tarea": "qa_sugerido_escritura",
            "prompt_version": PROMPT_VERSION,
            "acto": acto,
            "documento": _clip(html_o_texto, 14000),
            "evidencias_corpus": evidencias,
            "guardrails": [
                "Senala posibles inconsistencias o faltantes como sugerencias.",
                "No decidas procedencia ni bloquees.",
                "No inventes citas. No devuelvas cita_slug; el sistema la asigna desde RAG.",
            ],
            "salida_json": {"hallazgos": [{"tipo": "faltante", "detalle": "texto breve"}]},
        },
        ensure_ascii=False,
    )
    parsed = llm.complete_json(purpose="revision", prompt=prompt)
    hallazgos: list[dict[str, Any]] = []
    for item in _as_list(parsed.get("hallazgos")):
        spec = _as_dict(item)
        detalle = str(spec.get("detalle") or "").strip()
        if not detalle:
            continue
        tipo = str(spec.get("tipo") or "revision").strip() or "revision"
        hit = _first_rag_hit(rag_searcher(session, detalle, fecha, acto_code=corpus_acto_code, top_k=3))
        if hit is None:
            hit = _first_rag_hit(grounding)
        hallazgos.append(
            {
                "tipo": tipo,
                "detalle": detalle,
                "cita_slug": getattr(hit, "source_ref", None) if hit is not None else None,
            }
        )
    return {
        "hallazgos": hallazgos,
        "sugerencia": True,
        "estado": AI_VALIDATION_LABEL,
        "modelo": llm.model_version,
        "prompt_version": PROMPT_VERSION,
    }


def _first_rag_hit(hits) -> Any | None:
    for hit in hits or []:
        if getattr(hit, "source_ref", None):
            return hit
    return None
