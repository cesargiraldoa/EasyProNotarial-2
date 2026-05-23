"""
EasyPro 2 - Concordancia de genero con IA
============================================

Cuando el protocolista cambia el genero de una persona (Juan H -> Maria F),
este modulo identifica todas las palabras del documento que deben cambiar
para mantener concordancia gramatical respecto a esa persona especifica.

Estrategia:
1. Recibe: texto del documento + persona vieja (con genero) + persona nueva (con genero)
2. Si los generos son iguales, retorna lista vacia (no hay cambios)
3. Si son distintos, llama a IA con prompt especializado
4. Retorna lista de cambios propuestos con contexto, para que protocolista confirme
"""
import json
import os
import re

import httpx
from openai import OpenAI


def _make_openai_client(api_key: str) -> OpenAI:
    if os.environ.get("OPENAI_DISABLE_SSL_VERIFY", "").lower() == "true":
        return OpenAI(api_key=api_key, http_client=httpx.Client(verify=False))
    return OpenAI(api_key=api_key)


MODEL = "gpt-4o-mini"


PROMPT_CONCORDANCIA = """Eres experto en gramatica espanola y redaccion notarial colombiana.

CONTEXTO:
En un documento notarial, una persona cambio de genero gramatical. Necesitas identificar
TODAS las palabras y frases del documento que deben cambiar para mantener concordancia
respecto a ESA persona especifica (no respecto a otras personas del documento).

IMPORTANTE: La persona puede cumplir MULTIPLES roles en el documento (por ejemplo,
ser comprador, deudor hipotecante, otorgante, poderdante, todo a la vez). Debes detectar
concordancias en TODOS sus roles.

DATOS:
- Persona vieja: {nombre_viejo} ({genero_viejo})
- Persona nueva: {nombre_nuevo} ({genero_nuevo})
- Roles que cumple esta persona: {rol}

PERSONAS QUE DEBEN QUEDAR INTACTAS:
Las siguientes personas aparecen en el documento con su propio genero. NO cambies
nada en parrafos donde aparezcan exclusivamente estas personas (a menos que el parrafo
tambien mencione a {nombre_nuevo}):
{personas_resto_lista}

INSTRUCCIONES CRITICAS:

Tu tarea es EXCLUSIVAMENTE cambiar los articulos y sustantivos de ROL.
NO cambies palabras de genero descriptivo (varon/mujer, identificado/a,
domiciliado/a, soltero/a, colombiano/a, etc.) — esas las maneja otro sistema.

1. SOLO devuelves JSON valido. Sin explicaciones.

2. ARTICULOS — SIEMPRE como FRASE COMPLETA (articulo + sustantivo del rol). NUNCA articulo solo.
   CORRECTO:   "EL COMPRADOR"  -> "LA COMPRADORA"
   INCORRECTO: "EL"            -> "LA"   <-- esto daniaria TODO el documento, no lo hagas

   Para cada rol de la persona, detecta en el texto y devuelve estas frases si aparecen:
   - "EL {{ROL}}"  -> "LA {{ROL-F}}"       ej: "EL COMPRADOR"  -> "LA COMPRADORA"
   - "el {{rol}}"  -> "la {{rol-f}}"        ej: "el comprador"  -> "la compradora"
   - "DEL {{ROL}}" -> "DE LA {{ROL-F}}"    ej: "DEL COMPRADOR" -> "DE LA COMPRADORA"
   - "del {{rol}}" -> "de la {{rol-f}}"     ej: "del comprador" -> "de la compradora"
   - "AL {{ROL}}"  -> "A LA {{ROL-F}}"     ej: "AL COMPRADOR"  -> "A LA COMPRADORA"
   - "al {{rol}}"  -> "a la {{rol-f}}"      ej: "al comprador"  -> "a la compradora"
   - "UN {{ROL}}"  -> "UNA {{ROL-F}}"      ej: "UN COMPRADOR"  -> "UNA COMPRADORA"
   - "un {{rol}}"  -> "una {{rol-f}}"
   Incluye solo las variantes que REALMENTE APARECEN en el texto del documento.

3. SUSTANTIVOS de rol solos (sin articulo inmediato, ej: "en calidad de COMPRADOR"):
   - "COMPRADOR" -> "COMPRADORA",  "comprador" -> "compradora"
   - "VENDEDOR"  -> "VENDEDORA",   "vendedor"  -> "vendedora"
   - "DEUDOR"    -> "DEUDORA",     "deudor"    -> "deudora"
   - "DEUDOR HIPOTECANTE" -> "DEUDORA HIPOTECANTE"
   - "APODERADO" -> "APODERADA",   "apoderado" -> "apoderada"
   - "SENOR"     -> "SENORA"       (solo instancias sin articulo ya cubiertas en seccion 2)
   - "representante legal", "poderdante", "otorgante", "constituyente" — NO CAMBIAR (neutros)

4. FORMULAS MIXTAS notariales — devolver el cambio exacto incluyendo los parentesis:
   - "EL(LOS) COMPRADOR(ES)"  -> "LA(LAS) COMPRADORA(S)"
   - "EL(LOS) DEUDOR(ES)"     -> "LA(LAS) DEUDORA(S)"
   - "COMPRADOR(ES)"          -> "COMPRADORA(S)"
   - "DEUDOR(ES)"             -> "DEUDORA(S)"

5. NO devuelvas cambios para:
   - Frases hechas: "el de la voz", "el suscrito notario", "el presente instrumento"
   - Referencias a OTRAS personas del documento con genero distinto
   - Palabras neutras: otorgante, poderdante, constituyente, representante legal
   - Entidades juridicas
   - Palabras descriptivas de genero: varon, mujer, identificado/a, domiciliado/a,
     soltero/a, casado/a, colombiano/a, venezolano/a, autorizado/a, obligado/a,
     el mismo, ella misma, dicho, dicha — estas NO son tu responsabilidad

6. Una entrada por frase/palabra exacta. Mayusculas y minusculas como entradas SEPARADAS
   si AMBAS variantes aparecen en el texto.

7. Para CADA cambio devuelve:
   - palabra_antes: frase o palabra exacta a buscar (respetando mayusculas del documento)
   - palabra_despues: frase o palabra exacta de reemplazo
   - contexto_ejemplo: fragmento de ~15 palabras alrededor del cambio en el documento
   - confianza: float 0-1
   - razon: breve explicacion

ESQUEMA JSON:
{{
  "cambios": [
    {{
      "palabra_antes": "EL COMPRADOR",
      "palabra_despues": "LA COMPRADORA",
      "contexto_ejemplo": "PRIMERA: EL COMPRADOR declara que ha recibido",
      "confianza": 0.98,
      "razon": "Articulo + sustantivo de rol referido a esta persona"
    }},
    {{
      "palabra_antes": "DEL COMPRADOR",
      "palabra_despues": "DE LA COMPRADORA",
      "contexto_ejemplo": "los derechos DEL COMPRADOR sobre el inmueble",
      "confianza": 0.98,
      "razon": "Contraccion DEL + sustantivo de rol"
    }},
    {{
      "palabra_antes": "COMPRADOR",
      "palabra_despues": "COMPRADORA",
      "contexto_ejemplo": "actuando como COMPRADOR del inmueble ubicado",
      "confianza": 1.0,
      "razon": "Sustantivo de rol sin articulo"
    }}
  ]
}}

TEXTO DEL DOCUMENTO:
\"\"\"
{texto_documento}
\"\"\"

Devuelve SOLO el JSON con la lista COMPLETA de cambios. Si no hay cambios, devuelve {{"cambios": []}}.
"""


def necesita_concordancia(persona_vieja: dict, persona_nueva: dict) -> bool:
    """
    Determina si una persona necesita pasada de concordancia.

    Solo se dispara si:
    1. Cambio el nombre
    2. El genero declarado es distinto al original
    3. Ningun genero es J (juridica) - empresas no tienen concordancia gramatical
    """
    nombre_viejo = (persona_vieja or {}).get("nombre_completo", "")
    nombre_nuevo = (persona_nueva or {}).get("nombre_completo", "")
    genero_viejo = (persona_vieja or {}).get("genero", "")
    genero_nuevo = (persona_nueva or {}).get("genero", "")

    # No hay cambio de nombre
    if not nombre_viejo or not nombre_nuevo or nombre_viejo == nombre_nuevo:
        return False

    # Empresas no tienen concordancia (J = juridica)
    if genero_viejo == "J" or genero_nuevo == "J":
        return False

    # Sin generos definidos
    if not genero_viejo or not genero_nuevo:
        return False

    # Solo si cambia M<->F
    return genero_viejo != genero_nuevo


def detectar_concordancia(
    texto_documento: str,
    persona_vieja: dict,
    persona_nueva: dict,
    api_key: str,
    personas_resto: list[dict] | None = None,
) -> dict:
    """
    Llama a IA para detectar cambios de concordancia necesarios.

    Returns:
        {
            "cambios": [
                {
                    "palabra_antes": str,
                    "palabra_despues": str,
                    "contexto_ejemplo": str,
                    "confianza": float,
                    "razon": str,
                    "ocurrencias_estimadas": int,
                }
            ],
            "costo_usd": float,
            "tokens": dict,
            "necesario": bool,
        }
    """
    if not necesita_concordancia(persona_vieja, persona_nueva):
        return {
            "cambios": [],
            "costo_usd": 0.0,
            "tokens": {},
            "necesario": False,
            "razon": "No hay cambio de genero relevante",
        }

    nombre_viejo = persona_vieja.get("nombre_completo") or persona_vieja.get("NOMBRE_COMPLETO") or ""
    nombre_nuevo = persona_nueva.get("nombre_completo") or persona_nueva.get("NOMBRE_COMPLETO") or ""
    genero_viejo = persona_vieja.get("genero") or persona_vieja.get("GENERO") or ""
    genero_nuevo = persona_nueva.get("genero") or persona_nueva.get("GENERO") or ""
    rol = persona_vieja.get("rol") or persona_vieja.get("ROL") or "persona"

    genero_legible = {"M": "Masculino", "F": "Femenino", "J": "Juridica"}

    personas_resto_lineas = []
    for p in (personas_resto or []):
        nombre_p = (p.get("nombre") or "").strip()
        genero_p = genero_legible.get(p.get("genero", ""), p.get("genero", ""))
        if nombre_p:
            personas_resto_lineas.append(f"  - {nombre_p} ({genero_p})")
    personas_resto_lista = (
        "\n".join(personas_resto_lineas)
        if personas_resto_lineas
        else "  (ninguna otra persona identificada)"
    )

    prompt_final = PROMPT_CONCORDANCIA.format(
        nombre_viejo=nombre_viejo,
        nombre_nuevo=nombre_nuevo,
        genero_viejo=genero_legible.get(genero_viejo, genero_viejo),
        genero_nuevo=genero_legible.get(genero_nuevo, genero_nuevo),
        rol=rol.replace("_", " "),
        personas_resto_lista=personas_resto_lista,
        texto_documento=texto_documento[:80000],
    )

    client = _make_openai_client(api_key)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Eres experto en concordancia gramatical en espanol notarial colombiano."},
            {"role": "user", "content": prompt_final},
        ],
        temperature=0.1,
        max_tokens=32000,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content or "{}"
    usage = response.usage

    # Quitar bloques ```json ... ``` por si el modelo los agrega igual
    raw_limpio = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    raw_limpio = re.sub(r"\s*```$", "", raw_limpio.strip())

    try:
        data = json.loads(raw_limpio)
    except json.JSONDecodeError as exc:
        print(f"[concordancia] JSONDecodeError: {exc}")
        print(f"[concordancia] finish_reason: {response.choices[0].finish_reason}")
        print(f"[concordancia] completion_tokens: {usage.completion_tokens}")
        print(f"[concordancia] raw (primeros 2000 chars):\n{raw[:2000]}")
        raise
    cambios = data.get("cambios", [])

    # Enriquecer cada cambio con conteo de ocurrencias en el texto
    for cambio in cambios:
        palabra = cambio.get("palabra_antes", "")
        if palabra:
            # Contar ocurrencias case-insensitive como palabra completa
            patron = r"\b" + re.escape(palabra) + r"\b"
            cambio["ocurrencias_estimadas"] = len(re.findall(patron, texto_documento, re.IGNORECASE))
        else:
            cambio["ocurrencias_estimadas"] = 0

    # Calcular costo (gpt-4o-mini)
    costo = round(
        (usage.prompt_tokens / 1_000_000) * 0.15 +
        (usage.completion_tokens / 1_000_000) * 0.60,
        4
    )

    return {
        "cambios": cambios,
        "costo_usd": costo,
        "tokens": {
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
        },
        "necesario": True,
        "persona_vieja": persona_vieja,
        "persona_nueva": persona_nueva,
    }


def aplicar_cambios_concordancia_a_reemplazos(cambios_seleccionados: list[dict]) -> list[dict]:
    """
    Convierte los cambios de concordancia confirmados en el formato de reemplazos
    que entiende el motor (reemplazador.aplicar_reemplazos_docx).

    Ordena por longitud descendente para que las frases compuestas (ej: "EL COMPRADOR")
    se procesen antes que sus partes ("COMPRADOR"). Esto evita que el sustantivo se
    cambie primero dejando la frase "EL COMPRADORA" sin match posterior.

    Args:
        cambios_seleccionados: lista de cambios marcados por el usuario para aplicar

    Returns:
        lista de dicts {viejo, nuevo, etiqueta} compatible con aplicar_reemplazos_docx
    """
    cambios_ordenados = sorted(
        cambios_seleccionados,
        key=lambda c: len(c.get("palabra_antes", "")),
        reverse=True,
    )
    reemplazos = []
    for c in cambios_ordenados:
        palabra_antes = c.get("palabra_antes", "").strip()
        palabra_despues = c.get("palabra_despues", "").strip()
        if not palabra_antes or not palabra_despues:
            continue
        reemplazos.append({
            "viejo": palabra_antes,
            "nuevo": palabra_despues,
            "etiqueta": f"concordancia.{palabra_antes}",
            "palabra_completa": True,
        })
    return reemplazos
