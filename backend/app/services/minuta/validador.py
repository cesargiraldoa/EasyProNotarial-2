# backend/app/services/minuta/validador.py
# Capa 2 — Validador notarial
# Recibe el dict `datos` del detector y retorna un reporte de validación

import json
import re
from anthropic import Anthropic

MODEL = "claude-sonnet-4-20250514"

# ── Reglas notariales por tipo de acto ──────────────────────────────────────

CAMPOS_OBLIGATORIOS_POR_ACTO = {
    "COMPRAVENTA_VIS": {
        "personas": ["vendedor", "comprador"],
        "inmueble": ["matricula_inmobiliaria", "linderos", "municipio"],
        "valores": ["valor_compraventa"],
        "decisiones": [],
    },
    "HIPOTECA": {
        "personas": ["deudor_hipotecante", "acreedor_hipotecario"],
        "inmueble": ["matricula_inmobiliaria", "linderos"],
        "valores": ["valor_hipoteca"],
        "decisiones": [],
    },
    "LIBERACION_HIPOTECA": {
        "personas": ["acreedor_hipotecario", "deudor_hipotecante"],
        "inmueble": ["matricula_inmobiliaria"],
        "valores": ["valor_liberacion"],
        "decisiones": [],
    },
    "PODER_GENERAL": {
        "personas": ["poderdante", "apoderado"],
        "inmueble": [],
        "valores": [],
        "decisiones": [],
    },
    "PODER_ESPECIAL": {
        "personas": ["poderdante", "apoderado"],
        "inmueble": [],
        "valores": [],
        "decisiones": [],
    },
    "AFECTACION_VIVIENDA_FAMILIAR": {
        "personas": ["propietario", "conyuge"],
        "inmueble": ["matricula_inmobiliaria"],
        "valores": [],
        "decisiones": ["vivienda_familiar"],
    },
    "CAPITULACIONES_MATRIMONIALES": {
        "personas": ["otorgante_1", "otorgante_2"],
        "inmueble": [],
        "valores": [],
        "decisiones": [],
    },
    "CORRECCION_REGISTRO_CIVIL": {
        "personas": ["inscrito"],
        "inmueble": [],
        "valores": [],
        "decisiones": [],
    },
    "AUTORIZACION_SALIDA_PAIS": {
        "personas": ["padre_o_madre_autorizante", "menor"],
        "inmueble": [],
        "valores": [],
        "decisiones": [],
    },
}

# Zonas de registro por prefijo de matrícula
ZONAS_MATRICULA = {
    "01N": "Medellín Zona Norte",
    "01S": "Medellín Zona Sur",
    "001": "Caldas - Zona Sur",
    "142": "Montelíbano",
    "020": "Envigado",
    "019": "Itagüí",
}

PROMPT_VALIDADOR = """Eres un experto validador notarial colombiano con 20 años de experiencia en la Superintendencia de Notariado y Registro.

Recibes un JSON con datos extraídos de una escritura pública. Tu tarea es:

1. VALIDAR que los datos sean correctos y coherentes
2. DETECTAR campos faltantes obligatorios según el tipo de acto
3. INFERIR datos que se pueden deducir lógicamente
4. ALERTAR sobre inconsistencias graves

Para cada campo evaluado asigna un estado:
- "ok": dato presente, formato correcto, coherente
- "advertencia": dato presente pero posiblemente incorrecto o incompleto
- "faltante": campo obligatorio ausente para este tipo de acto
- "inferido": valor completado por deducción lógica (no estaba explícito)

REGLAS DE VALIDACIÓN NOTARIAL COLOMBIANA:

PERSONAS:
- Toda cédula de ciudadanía colombiana tiene entre 4 y 10 dígitos
- Toda tarjeta de identidad tiene 10 u 11 dígitos
- NIT tiene formato XXXXXXXXX-X (9 dígitos + dígito verificador)
- Si el rol es "apoderado" debe existir también el "poderdante"
- Si alguien actúa "en nombre y representación" debe haber datos del poder
- Estado civil "casado/a" implica que puede haber sociedad conyugal — alertar si no se aclara
- Persona jurídica (genero=J) no tiene estado civil ni género personal

INMUEBLE:
- Matrícula inmobiliaria formato: XXX-XXXXXXX (ej: 01N-296573, 001-1282297)
- Prefijo 01N = Medellín Zona Norte, 001 = Caldas Sur, etc.
- Si hay matrícula, el municipio de registro se puede inferir del prefijo
- Cédula catastral tiene entre 15 y 30 dígitos
- Si menciona "propiedad horizontal" debe haber datos del reglamento RPH
- Linderos vacíos en compraventa = advertencia crítica

VALORES:
- Valor en letras debe ser coherente con valor numérico
- Si hay "valor_compraventa" y "valor_hipoteca", la hipoteca no debe superar el 80% del valor de venta (VIS)
- Derechos notariales, IVA y superfondo son proporcionales al valor — alertar si faltan en actos con cuantía

FECHAS:
- Fecha de otorgamiento debe ser una fecha válida
- Si hay escritura de adquisición anterior, su fecha debe ser anterior a la actual
- Número de escritura "PENDIENTE" = advertencia (plantilla sin completar)

NOTARÍA:
- Si el número de escritura está vacío o es "PENDIENTE" = advertencia
- Notario encargado diferente al titular = verificar resolución de nombramiento

COHERENCIA:
- Si acto es COMPRAVENTA: debe haber vendedor Y comprador
- Si acto es HIPOTECA: debe haber deudor Y acreedor
- Si hay poder: apoderado debe ser diferente al poderdante
- Estado civil "casado/a con sociedad conyugal vigente" + acto de venta = puede requerir cónyuge

INFERENCIAS PERMITIDAS:
- municipio_notaria desde nombre_notaria ("Notaría Primera de Bello" → municipio = "Bello")
- departamento desde municipio (Bello, Caldas, Medellín, Envigado → "Antioquia")
- zona_registro desde prefijo de matrícula (01N → "Medellín Zona Norte")
- genero desde nombre cuando es obvio (MARIA → F, CARLOS → M) — marcar como inferido

Responde SOLO con JSON válido con esta estructura exacta:
{
  "resumen": {
    "total_campos": int,
    "campos_ok": int,
    "campos_advertencia": int,
    "campos_faltantes": int,
    "campos_inferidos": int,
    "nivel_confianza": "alto"|"medio"|"bajo",
    "listo_para_generar": boolean
  },
  "personas": [
    {
      "rol": string,
      "nombre": string,
      "validaciones": {
        "numero_documento": { "estado": "ok"|"advertencia"|"faltante", "mensaje": string|null },
        "estado_civil": { "estado": "ok"|"advertencia"|"faltante", "mensaje": string|null },
        "genero": { "estado": "ok"|"advertencia"|"inferido", "mensaje": string|null }
      }
    }
  ],
  "inmueble": {
    "matricula_inmobiliaria": { "estado": string, "mensaje": string|null, "valor_inferido": string|null },
    "linderos": { "estado": string, "mensaje": string|null },
    "municipio": { "estado": string, "mensaje": string|null, "valor_inferido": string|null },
    "departamento": { "estado": string, "mensaje": string|null, "valor_inferido": string|null },
    "zona_registro": { "estado": string, "mensaje": string|null, "valor_inferido": string|null }
  },
  "notaria": {
    "numero_escritura": { "estado": string, "mensaje": string|null },
    "fecha_otorgamiento": { "estado": string, "mensaje": string|null }
  },
  "valores": [
    {
      "tipo": string,
      "estado": string,
      "mensaje": string|null
    }
  ],
  "alertas_criticas": [string],
  "inferencias_aplicadas": [string],
  "campos_faltantes_obligatorios": [string]
}
"""


def _make_anthropic_client() -> Anthropic:
    import ssl
    import httpx
    from app.core.config import get_settings
    api_key = get_settings().anthropic_api_key
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY no configurada en el servidor.")
    try:
        ctx = ssl.create_default_context()
        transport = httpx.HTTPTransport(verify=ctx)
        http_client = httpx.Client(transport=transport)
        return Anthropic(api_key=api_key, http_client=http_client)
    except Exception:
        return Anthropic(api_key=api_key)


def validar_documento(datos: dict, actos_detectados: list[str]) -> dict:
    """
    Capa 2 — Validador notarial.
    Recibe datos{} del detector y retorna reporte de validación.
    """
    # Validaciones deterministas (sin IA) — rápidas y baratas
    alertas_previas = _validar_determinista(datos, actos_detectados)

    # Preparar contexto para Claude
    contexto = {
        "actos": actos_detectados,
        "datos": datos,
        "alertas_previas": alertas_previas,
    }

    client = _make_anthropic_client()
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        temperature=0,
        system=PROMPT_VALIDADOR,
        messages=[
            {
                "role": "user",
                "content": f"Valida este documento notarial:\n\n{json.dumps(contexto, ensure_ascii=False, indent=2)}"
            }
        ]
    )

    raw = response.content[0].text.strip()
    # Strip markdown si viene envuelto
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    resultado = json.loads(raw)

    # Agregar costo (Sonnet 4: $3/M input, $15/M output)
    resultado["tokens"] = {
        "prompt_tokens": response.usage.input_tokens,
        "completion_tokens": response.usage.output_tokens,
        "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
    }
    resultado["costo_usd"] = round(
        response.usage.input_tokens * 3 / 1_000_000 +
        response.usage.output_tokens * 15 / 1_000_000,
        6
    )

    return resultado


def _validar_determinista(datos: dict, actos: list[str]) -> list[str]:
    """Validaciones rápidas sin IA."""
    alertas = []

    personas = datos.get("personas", [])
    inmueble = datos.get("inmueble") or {}
    notaria = datos.get("notaria") or {}

    # Validar cédulas
    for p in personas:
        doc = (p.get("numero_documento") or "").replace(".", "").replace("-", "")
        tipo = p.get("tipo_documento", "")
        nombre = p.get("nombre_completo") or p.get("nombre") or p.get("rol", "?")

        if tipo == "C.C" and doc and not (4 <= len(doc) <= 10):
            alertas.append(f"Cédula de {nombre} tiene {len(doc)} dígitos — formato inválido")
        if tipo == "T.I" and doc and len(doc) not in (10, 11):
            alertas.append(f"T.I. de {nombre} tiene {len(doc)} dígitos — formato inválido")
        if tipo == "NIT" and doc and not re.match(r"^\d{9}-?\d$", doc):
            alertas.append(f"NIT de {nombre} tiene formato inválido")

    # Validar matrícula
    matricula = inmueble.get("matricula_inmobiliaria", "")
    if matricula and not re.match(r"^\d{2,3}[NS]?-\d+$", matricula.replace(" ", "")):
        alertas.append(f"Matrícula '{matricula}' no tiene formato estándar (ej: 01N-296573)")

    # Validar número escritura
    num_escritura = notaria.get("numero_escritura", "")
    if not num_escritura or num_escritura.upper() == "PENDIENTE":
        alertas.append("Número de escritura pendiente — posible plantilla sin completar")

    # Validar actos vs personas
    roles = {(p.get("rol") or "").lower() for p in personas}
    if any("compraventa" in a.lower() for a in actos):
        if not any("vendedor" in r or "comprador" in r for r in roles):
            alertas.append("Acto de compraventa sin vendedor o comprador identificado")
    if any("hipoteca" in a.lower() and "liberacion" not in a.lower() for a in actos):
        if not any("deudor" in r or "acreedor" in r for r in roles):
            alertas.append("Acto de hipoteca sin deudor o acreedor identificado")

    return alertas
