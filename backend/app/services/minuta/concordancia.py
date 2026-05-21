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
TODAS las palabras del documento que deben cambiar para mantener concordancia respecto
a ESA persona especifica (no respecto a otras personas del documento).

IMPORTANTE: La persona puede cumplir MULTIPLES roles en el documento (por ejemplo,
ser comprador, deudor hipotecante, otorgante, poderdante, todo a la vez). Debes detectar
concordancias en TODOS sus roles.

DATOS:
- Persona vieja: {nombre_viejo} ({genero_viejo})
- Persona nueva: {nombre_nuevo} ({genero_nuevo})
- Roles que cumple esta persona: {rol}

INSTRUCCIONES CRITICAS:

1. SOLO devuelves JSON valido. Sin explicaciones.

2. Identifica palabras que se refieren a ESTA persona (en CUALQUIERA de sus roles) y deben cambiar de genero:
   - Articulos: "el comprador" -> "la compradora", "el deudor" -> "la deudora"
   - Sustantivos con genero por rol:
     * "comprador" -> "compradora"
     * "vendedor" -> "vendedora"
     * "deudor" -> "deudora"
     * "deudor hipotecante" -> "deudora hipotecante"
     * "apoderado" -> "apoderada"
     * "poderdante" se mantiene (es neutro)
     * "otorgante" se mantiene (es neutro)
     * "constituyente" se mantiene (es neutro)
   - Adjetivos: "identificado" -> "identificada", "domiciliado" -> "domiciliada",
     "casado" -> "casada", "soltero" -> "soltera", "mayor de edad" se mantiene
   - Sustantivos descriptivos: "varon" -> "mujer", "el senor" -> "la senora"
   - Gentilicios: "colombiano" -> "colombiana", "venezolano" -> "venezolana"

3. INCLUYE TODAS las palabras con genero que aparezcan en el documento referidas a esta persona.
   Si "deudor" aparece 63 veces refiriendose a esta persona, devuelve UN solo objeto
   con "deudor" -> "deudora" (con esas 63 ocurrencias acumuladas).

4. NO devuelvas cambios para:
   - Frases hechas notariales: "el de la voz", "el suscrito notario", etc.
   - Referencias a OTRAS personas del documento que tienen distinto genero
   - Palabras que no tienen genero gramatical o ya son neutras (otorgante, poderdante)
   - Palabras que aplican a una entidad juridica diferente

5. AGRUPA por palabra: una sola entrada por palabra a cambiar, no una por ocurrencia.

6. Considera variantes en MAYUSCULAS y minusculas del documento.

7. Para CADA cambio propuesto, devuelve:
   - palabra_antes: la palabra exacta a buscar (case-sensitive)
   - palabra_despues: la palabra que la reemplaza
   - contexto_ejemplo: fragmento de ~15 palabras alrededor del cambio
   - confianza: float 0-1 (1.0 = certeza absoluta, 0.5 = duda)
   - razon: breve explicacion de por que cambia

ESQUEMA JSON:
{{
  "cambios": [
    {{
      "palabra_antes": "deudor",
      "palabra_despues": "deudora",
      "contexto_ejemplo": "DEUDOR HIPOTECANTE: ... en calidad de deudor",
      "confianza": 0.95,
      "razon": "Sustantivo masculino referente a la persona como deudora hipotecante"
    }}
  ]
}}

TEXTO DEL DOCUMENTO:
\"\"\"
{texto_documento}
\"\"\"

Devuelve SOLO el JSON con la lista COMPLETA de cambios propuestos para mantener concordancia
con la nueva persona en TODOS sus roles. Si no hay cambios necesarios, devuelve {{"cambios": []}}.
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

    nombre_viejo = persona_vieja["nombre_completo"]
    nombre_nuevo = persona_nueva["nombre_completo"]
    genero_viejo = persona_vieja["genero"]
    genero_nuevo = persona_nueva["genero"]
    rol = persona_vieja.get("rol", "persona")

    genero_legible = {"M": "Masculino", "F": "Femenino"}

    prompt_final = PROMPT_CONCORDANCIA.format(
        nombre_viejo=nombre_viejo,
        nombre_nuevo=nombre_nuevo,
        genero_viejo=genero_legible.get(genero_viejo, genero_viejo),
        genero_nuevo=genero_legible.get(genero_nuevo, genero_nuevo),
        rol=rol.replace("_", " "),
        texto_documento=texto_documento[:80000],  # Limite seguro tokens
    )

    client = _make_openai_client(api_key)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Eres experto en concordancia gramatical en espanol notarial colombiano."},
            {"role": "user", "content": prompt_final},
        ],
        temperature=0.1,
        max_tokens=4000,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content or "{}"
    usage = response.usage
    data = json.loads(raw)
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

    Args:
        cambios_seleccionados: lista de cambios marcados por el usuario para aplicar

    Returns:
        lista de dicts {viejo, nuevo, etiqueta} compatible con aplicar_reemplazos_docx
    """
    reemplazos = []
    for c in cambios_seleccionados:
        palabra_antes = c.get("palabra_antes", "").strip()
        palabra_despues = c.get("palabra_despues", "").strip()
        if not palabra_antes or not palabra_despues:
            continue
        reemplazos.append({
            "viejo": palabra_antes,
            "nuevo": palabra_despues,
            "etiqueta": f"concordancia.{palabra_antes}",
        })
    return reemplazos
