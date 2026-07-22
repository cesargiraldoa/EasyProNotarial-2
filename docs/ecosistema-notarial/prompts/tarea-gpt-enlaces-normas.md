# Tarea para GPT — Verificar y normalizar enlaces oficiales del corpus jurídico notarial (Colombia)

## Contexto
Estamos construyendo el "corpus jurídico" de un software notarial colombiano: una base de datos de normas (con su artículo, estado de vigencia y cita) que alimenta un motor de redacción de escrituras y su informe de cumplimiento. Cada norma ya tiene metadatos estructurados, pero su campo `url_oficial` hoy contiene **citas o ids sueltos** (p. ej. "SUIN id=1657012", "funcionpublica i=10794", "corteconstitucional c-159-21"), **no URLs verificables**. Además, **33 de 67 normas están marcadas con `confianza=baja`** porque se corroboraron por extractos y no por lectura directa de la fuente (el entorno donde corre el sistema tiene bloqueado el acceso a los portales `.gov.co`).

**Tú (GPT) sí puedes navegar.** Tu tarea es cerrar esa brecha.

## Objetivo
Para **cada una de las 67 normas** de la lista de abajo (identificadas por su `slug`), verificar contra **fuente oficial** y devolver:
1. **`url_oficial`**: la **URL http real y directa** al texto de la norma/artículo en una fuente oficial.
2. **`estado`**: vigente / modificada / derogada_parcial / derogada_total / inexequible / suspendida / compilada (confirmado).
3. **`vigencia_desde`** y/o **`vigencia_hasta`** (ISO `YYYY-MM-DD`) si aplica (p. ej. fecha de una sentencia de inexequibilidad, fecha de una ley nueva).
4. **`texto_articulo`**: transcripción del **texto oficial del artículo** citado (o su extracto pertinente) — más completo que un resumen.
5. **`confianza`**: `alta` si lo confirmaste abriendo la fuente oficial; `media` si por fuente secundaria fiable; `baja`/`NO CONFIRMADO` si no lo hallaste.
6. **`notas`**: cualquier salvedad (p. ej. "modificado por Ley X art. Y", "artículo renumerado", etc.).

## Fuentes oficiales aceptables (en este orden)
- SUIN-Juriscol — https://www.suin-juriscol.gov.co
- Gestor Normativo (Función Pública) — https://www.funcionpublica.gov.co/eva/gestornormativo
- Secretaría del Senado (leyes y códigos) — https://www.secretariasenado.gov.co/senado/basedoc
- Corte Constitucional (relatoría) — https://www.corteconstitucional.gov.co/relatoria
- Diario Oficial / Imprenta Nacional — para fechas de promulgación de normas 2024-2026
- DIAN (normograma) y Superintendencia de Notariado y Registro — para tributario y tarifas

## Regla dura
**No inventes.** Si no encuentras la norma en una fuente oficial, marca `confianza: "NO CONFIRMADO"` y explica en `notas` qué buscaste. Prefiere SIEMPRE la URL oficial; si citas una secundaria, dilo en `notas`.

## Prioridad
1. **Las 33 con `confianza=baja`** (primeras en la tabla) — son las que más lo necesitan.
2. **Cierra estos 7 puntos que quedaron sin confirmar** (críticos):
   - `ley-2434-2024-descuento-credito-hipotecario`: artículo exacto y texto del descuento del 30% en derechos notariales por crédito hipotecario de vivienda; ¿aplica antes del IVA?
   - `ley-258-1996-art-3`: ¿en qué artículo/parágrafo de la Ley 258/1996 está la sanción de **nulidad absoluta** por falta de doble firma? (el art. 3 exige el consentimiento; falta ubicar la nulidad).
   - `codigo-civil-art-1931`/`1935`: número de radicado/fecha de una sentencia de la **Corte Suprema (Sala Civil)** sobre la (in)eficacia real de la reserva de dominio en inmuebles.
   - `resolucion-snr-2026-000964-6`: **valor exacto del derecho notarial mínimo 2026** y tabla de rangos (Resolución SNR 2026-000964-6).
   - `ley-223-1995-art-230`: **ordenanza tarifaria de Antioquia vigente 2026** que fija el 1% del impuesto de registro.
   - `estatuto-tributario-art-401`: **tarifa exacta** de retención cuando el vendedor es persona jurídica.
   - Fechas de Diario Oficial de: `ley-2447-2025`, `decreto-0732-2026`, `decreto-906-2025`, y fecha/parte resolutiva de la Sentencia **C-039/2025**.

## Formato de salida (para reincorporarlo automáticamente)
Devuelve **un único JSON**: un objeto donde cada clave es el `slug` y el valor trae los campos verificados. Ejemplo:
```json
{
  "ley-258-1996-art-3": {
    "url_oficial": "https://www.suin-juriscol.gov.co/viewDocument.asp?id=1657012",
    "estado": "vigente",
    "vigencia_desde": "1996-02-05",
    "vigencia_hasta": null,
    "texto_articulo": "Los inmuebles afectados a vivienda familiar solo podrán enajenarse...",
    "confianza": "alta",
    "notas": "La nulidad absoluta por falta de doble firma está en el art. ___."
  }
}
```
Incluye una entrada por cada slug de la tabla (67 en total). No cambies los `slug`.

## Lista de las 67 normas a verificar
(Ordenadas: primero las `confianza=baja`.)

| slug | norma / artículo | materia | confianza actual |
|---|---|---|---|
| `circular-snr-1536-2013-ley-1581-2012` | Circular 1536/2013 | datos personales | baja |
| `codigo-civil-art-1546` | Código Civil/1887 art. 1546 | civil | baja |
| `codigo-civil-art-1521` | Código Civil/1887 art. 1521 | civil | baja |
| `codigo-civil-art-1849` | Código Civil/1887 art. 1849 | civil | baja |
| `codigo-civil-art-1857` | Código Civil/1887 art. 1857 | civil | baja |
| `codigo-civil-art-1893-1914` | Código Civil/1887 art. 1893,1914 | civil | baja |
| `codigo-civil-art-1931` | Código Civil/1887 art. 1931 | civil | baja |
| `codigo-civil-art-1935` | Código Civil/1887 art. 1935 | civil | baja |
| `codigo-civil-art-1939` | Código Civil/1887 art. 1939 | civil | baja |
| `codigo-civil-art-2432` | Código Civil/1887 art. 2432 | civil | baja |
| `codigo-civil-art-2445-2446` | Código Civil/1887 art. 2445-2446 | civil | baja |
| `codigo-comercio-representacion-personas-juridicas` | Código Comercio/1971 | comercial | baja |
| `estatuto-tributario-art-90` | Código ET/1989 art. 90 | tributario | baja |
| `decreto-830-2021` | Decreto 830/2021 | LA/FT | baja |
| `decreto-ley-960-1970-art-38` | Decreto-Ley 960/1970 art. 38 | notarial | baja |
| `decreto-ley-960-1970-art-39` | Decreto-Ley 960/1970 art. 39 | notarial | baja |
| `ley-1579-2012-art-4` | Ley 1579/2012 art. 4 | registro | baja |
| `ley-1996-2019-art-6` | Ley 1996/2019 art. 6 | capacidad legal | baja |
| `ley-1996-2019-art-15-16` | Ley 1996/2019 art. 15-16 | capacidad legal | baja |
| `ley-2079-2021-art-13` | Ley 2079/2021 art. 13 | VIS | baja |
| `ley-2097-2021-redam` | Ley 2097/2021 | REDAM | baja |
| `ley-2195-2022-siplaft` | Ley 2195/2022 | LA/FT | baja |
| `ley-2434-2024-descuento-credito-hipotecario` | Ley 2434/2024 | tarifas notariales | baja |
| `ley-2447-2025` | Ley 2447/2025 | familia | baja |
| `ley-3-1991-subsidio-vivienda` | Ley 3/1991 | subsidio familiar de vivienda | baja |
| `ley-546-1999-art-23` | Ley 546/1999 art. 23 | financiación vivienda | baja |
| `ley-546-1999-art-24` | Ley 546/1999 art. 24 | financiación vivienda | baja |
| `ley-675-2001` | Ley 675/2001 | propiedad horizontal | baja |
| `ley-675-2001-art-25-26` | Ley 675/2001 art. 25-26 | propiedad horizontal | baja |
| `ley-675-2001-art-29` | Ley 675/2001 art. 29 | propiedad horizontal | baja |
| `ley-70-1931-ley-495-1999-patrimonio-familia` | Ley 70/495/1931 | patrimonio de familia | baja |
| `ley-795-2003-leasing-habitacional` | Ley 795/2003 | leasing habitacional | baja |
| `resolucion-snr-2026-001726-6` | Resolución SNR 2026-001726-6/2026 | tarifas registrales 2026 | baja |
| `codigo-civil-art-2457` | Código Civil/1887 art. 2457 | civil | alta |
| `estatuto-tributario-art-300` | Código ET/1989 art. 300 | tributario | alta |
| `estatuto-tributario-art-311-1` | Código ET/1989 art. 311-1 | tributario | alta |
| `estatuto-tributario-art-313` | Código ET/1989 art. 313 | tributario | alta |
| `estatuto-tributario-art-398` | Código ET/1989 art. 398 | tributario | alta |
| `estatuto-tributario-art-399` | Código ET/1989 art. 399 | tributario | media |
| `estatuto-tributario-art-401` | Código ET/1989 art. 401 | tributario | media |
| `estatuto-tributario-art-468` | Código ET/1989 art. 468 | tributario | alta |
| `decreto-0732-2026` | Decreto 0732/2026 | identidad | media |
| `decreto-1069-2015-dur-sector-justicia` | Decreto 1069/2015 | notarial | alta |
| `decreto-1069-2015-art-2-2-6-1-2-1-5` | Decreto 1069/2015 art. 2.2.6.1.2.1.5 | notarial | alta |
| `decreto-1469-2025-0159-2026-smlmv-2026` | Decreto 1469/0159/2025 | SMLMV 2026 | media |
| `decreto-1712-1989` | Decreto 1712/1989 | donación | alta |
| `decreto-2148-1983-art-12` | Decreto 2148/1983 art. 12 | notarial | alta |
| `decreto-906-2025` | Decreto 906/2025 | agrario | media |
| `decreto-ley-2106-2019-arts-59-63` | Decreto-Ley 2106/2019 art. 59-63 | escritura pública electrónica | alta |
| `decreto-ley-960-1970-art-13` | Decreto-Ley 960/1970 art. 13 | notarial | alta |
| `decreto-ley-960-1970-art-14` | Decreto-Ley 960/1970 art. 14 | notarial | alta |
| `ley-1579-2012` | Ley 1579/2012 | registro | alta |
| `ley-1579-2012-art-8` | Ley 1579/2012 art. 8 | registro | alta |
| `ley-1579-2012-art-16` | Ley 1579/2012 art. 16 | registro | alta |
| `ley-1579-2012-art-27` | Ley 1579/2012 art. 27 | registro | alta |
| `ley-1579-2012-art-28` | Ley 1579/2012 art. 28 | registro | alta |
| `ley-160-1994-art-72` | Ley 160/1994 art. 72 | agrario | alta |
| `ley-223-1995-art-230` | Ley 223/1995 art. 230 | tributario | media |
| `ley-223-1995-art-231` | Ley 223/1995 art. 231 | tributario | alta |
| `ley-2277-2022-art-31` | Ley 2277/2022 art. 31 | tributario | alta |
| `ley-2442-2024` | Ley 2442/2024 | familia | alta |
| `ley-258-1996-art-3` | Ley 258/1996 art. 3 | vivienda familiar | alta |
| `ley-258-1996-art-6` | Ley 258/1996 art. 6 | vivienda familiar | alta |
| `ley-54-1990-art-2` | Ley 54/1990 art. 2 | unión marital | alta |
| `ley-854-2003` | Ley 854/2003 | vivienda familiar | alta |
| `resolucion-dian-000238-2025-uvt-2026` | Resolución DIAN 000238/2025 | UVT 2026 | alta |
| `resolucion-snr-2026-000964-6` | Resolución SNR 2026-000964-6/2026 | tarifas notariales 2026 | media |
