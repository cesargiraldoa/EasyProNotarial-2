from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


LegalNormaTipo = Literal["Ley", "Decreto", "Decreto-Ley", "Resolución", "Circular", "Sentencia", "Código"]
LegalNormaEstado = Literal["vigente", "modificada", "derogada_parcial", "derogada_total", "inexequible", "suspendida", "compilada"]
LegalConfianza = Literal["alta", "media", "baja"]
LegalRelacionTipo = Literal["modifica", "deroga_total", "deroga_parcial", "compila", "desarrolla", "reglamenta"]
LegalClausulaCapa = Literal["por_ley", "estilo"]
LegalReglaSeveridad = Literal["BLOCK", "REVIEW", "WARN"]
LegalJurisprudenciaTipo = Literal["C", "SU", "T", "CSJ", "CE"]


class LegalNormaPayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tipo: LegalNormaTipo
    numero: str = Field(min_length=1, max_length=80)
    anio: int
    articulo: str | None = Field(default=None, max_length=80)
    materia: str = Field(min_length=1, max_length=160)
    autoridad: str = Field(min_length=1, max_length=160)
    estado: LegalNormaEstado
    vigencia_formal: str = Field(min_length=1, max_length=80)
    aplicabilidad_operativa: str = Field(min_length=1, max_length=80)
    vigencia_desde: date | None = None
    vigencia_hasta: date | None = None
    url_oficial: str | None = Field(default=None, max_length=1000)
    confianza: LegalConfianza
    fecha_verificacion: date | None = None
    texto: str | None = None
    notas: str | None = None
    slug: str = Field(min_length=1, max_length=180)


class LegalNormaRelacionPayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    norma_origen_slug: str = Field(min_length=1, max_length=180)
    norma_destino_slug: str = Field(min_length=1, max_length=180)
    tipo: LegalRelacionTipo
    articulo_afectado: str | None = Field(default=None, max_length=80)
    fecha_efecto: date | None = None
    notas: str | None = None


class LegalClausulaPayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    acto_code: str = Field(min_length=1, max_length=80)
    orden: int
    titulo: str = Field(min_length=1, max_length=240)
    texto: str
    capa: LegalClausulaCapa
    norma_slug: str | None = Field(default=None, max_length=180)
    notaria_id: int | None = None
    condicional: bool = False
    vigencia_desde: date | None = None
    vigencia_hasta: date | None = None
    notas: str | None = None


class LegalReglaPayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    acto_code: str = Field(min_length=1, max_length=80)
    codigo: str = Field(min_length=1, max_length=160)
    condicion_json: dict[str, Any]
    efecto: str
    severidad: LegalReglaSeveridad
    mensaje: str
    norma_slug: str | None = Field(default=None, max_length=180)
    vigencia_desde: date | None = None
    vigencia_hasta: date | None = None


class LegalTarifaPayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    anio: int
    concepto: str = Field(min_length=1, max_length=240)
    valor: Decimal | None = None
    formula: str | None = Field(default=None, max_length=500)
    unidad: str | None = Field(default=None, max_length=80)
    norma_slug: str | None = Field(default=None, max_length=180)
    vigencia_desde: date | None = None
    vigencia_hasta: date | None = None


class LegalJurisprudenciaPayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tipo: LegalJurisprudenciaTipo
    numero: str = Field(min_length=1, max_length=40)
    anio: int
    providencia: str = Field(min_length=1, max_length=160)
    regla_operacional: str
    norma_relacionada_slug: str | None = Field(default=None, max_length=180)
    fecha: date | None = None
    url_oficial: str | None = Field(default=None, max_length=1000)
    confianza: LegalConfianza
