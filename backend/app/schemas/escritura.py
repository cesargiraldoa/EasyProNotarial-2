from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


ActoCode = Literal["compraventa", "hipoteca", "cancelacion"]


class LegalNormaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: str
    numero: str
    anio: int
    articulo: str | None = None
    materia: str
    autoridad: str
    estado: str
    vigencia_formal: str
    aplicabilidad_operativa: str
    vigencia_desde: date | None = None
    vigencia_hasta: date | None = None
    url_oficial: str | None = None
    confianza: str
    fecha_verificacion: date | None = None
    texto: str | None = None
    notas: str | None = None
    slug: str


class LegalClausulaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    acto_code: str
    orden: int
    titulo: str
    texto: str
    capa: str
    norma_id: int | None = None
    notaria_id: int | None = None
    condicional: bool
    vigencia_desde: date | None = None
    vigencia_hasta: date | None = None
    notas: str | None = None


class LegalReglaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    acto_code: str
    codigo: str
    condicion_json: dict[str, Any]
    efecto: str
    severidad: str
    mensaje: str
    norma_id: int | None = None
    vigencia_desde: date | None = None
    vigencia_hasta: date | None = None


class LegalTarifaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    anio: int
    concepto: str
    valor: Decimal | None = None
    formula: str | None = None
    unidad: str | None = None
    norma_id: int | None = None
    vigencia_desde: date | None = None
    vigencia_hasta: date | None = None


class CorpusResponse(BaseModel):
    acto: ActoCode
    corpus_acto_code: str
    fecha: date
    normas: list[LegalNormaOut]
    clausulas: list[LegalClausulaOut]
    reglas: list[LegalReglaOut]
    tarifas: list[LegalTarifaOut]


class HallazgoOut(BaseModel):
    codigo: str
    severidad: str
    mensaje: str
    efecto: str
    norma_id: int | None = None
    norma: str | None = None


class CorpusBusquedaHit(BaseModel):
    source_type: str
    source_id: int
    source_ref: str
    titulo: str
    chunk_text: str
    score: float
    acto_code: str | None = None
    vigencia_desde: date | None = None
    vigencia_hasta: date | None = None


class CorpusBusquedaResponse(BaseModel):
    q: str
    acto: ActoCode | None = None
    corpus_acto_code: str | None = None
    fecha: date
    hits: list[CorpusBusquedaHit]


class BibliotecaClausulaOut(BaseModel):
    id: int
    acto_code: str
    titulo: str
    texto: str
    capa: str
    orden: int
    condicional: bool
    vigencia_desde: date | None = None
    vigencia_hasta: date | None = None


class PlantillaSemillaTokenOut(BaseModel):
    token: str
    label: str | None = None
    field: str | None = None
    section: str | None = None


class PlantillaSemillaOut(BaseModel):
    id: int
    acto: ActoCode
    fuente: str
    name: str
    body_html: str
    tokens: list[PlantillaSemillaTokenOut] = Field(default_factory=list)
    bank_name: str | None = None
    legal_entity_id: int | None = None
    notaria: str | None = None
    is_fallback: bool = False


class CaseMeta(BaseModel):
    id: int
    notary_id: int
    case_type: str
    act_type: str
    consecutive: int
    year: int
    current_state: str
    internal_case_number: str | None = None
    official_deed_number: str | None = None
    official_deed_year: int | None = None
    updated_at: datetime


class EscrituraStateIn(BaseModel):
    acto: ActoCode
    # Lax by design: CaseState is validated by the WP-2 TypeScript engine.
    state: dict[str, Any] = Field(default_factory=dict)


class EscrituraStateOut(BaseModel):
    case_id: int
    acto: ActoCode | None = None
    state: dict[str, Any]
    case: CaseMeta


class DocumentoIn(BaseModel):
    acto: ActoCode
    html: str = Field(min_length=1)
    filename: str | None = Field(default=None, max_length=255)
    cumplimiento_bloqueantes: int = Field(ge=0)


class DocumentoOut(BaseModel):
    version_number: int
    file_format: str
    storage_path: str
    download_url: str | None = None
    document_id: int
    version_id: int


class GariCampoSugerido(BaseModel):
    valor: Any
    confianza: float = Field(ge=0, le=1)
    fuente: str


class GariExtraccionOut(BaseModel):
    sugerencias: dict[str, GariCampoSugerido]
    por_validar: bool
    estado: str
    modelo: str
    prompt_version: str


class GariProsaIn(BaseModel):
    acto: ActoCode
    contexto: dict[str, Any] = Field(default_factory=dict)
    instruccion: str = Field(min_length=1)


class GariProsaOut(BaseModel):
    html_sugerido: str
    sugerencia: bool
    estado: str
    modelo: str
    prompt_version: str


class GariClasificacionIn(BaseModel):
    descripcion: str = Field(min_length=1)


class GariClasificacionOut(BaseModel):
    acto_sugerido: ActoCode
    ramas: list[str]
    sugerencia: bool
    estado: str
    modelo: str
    prompt_version: str


class GariRevisionIn(BaseModel):
    acto: ActoCode
    html: str | None = None


class GariRevisionHallazgo(BaseModel):
    tipo: str
    detalle: str
    cita_slug: str | None = None


class GariRevisionOut(BaseModel):
    hallazgos: list[GariRevisionHallazgo]
    sugerencia: bool
    estado: str
    modelo: str
    prompt_version: str
