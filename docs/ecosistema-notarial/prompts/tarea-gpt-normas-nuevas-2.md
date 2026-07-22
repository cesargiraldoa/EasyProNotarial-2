# Tarea para GPT — Verificar 7 normas nuevas del corpus (2.ª tanda)

## Contexto
En el corpus jurídico notarial (Colombia) se añadieron **7 normas** para las ramas de compraventa de "todo tipo" (saneamiento/falsa tradición, régimen cambiario, agrario/UAF, capacidad/apoyos). Entraron marcadas **`confianza=baja`** porque no se verificaron contra fuente oficial. Tu tarea es verificarlas (tú sí puedes navegar los `.gov.co`).

## Objetivo
Para **cada `slug`** de la tabla, devolver: `url_oficial` (URL http real y directa), `estado` (vigente/modificada/derogada_parcial/derogada_total/inexequible/suspendida/compilada), `vigencia_desde`/`vigencia_hasta` (ISO, si aplica), `texto_articulo` (transcripción del artículo pertinente), `confianza` (alta/media/baja) y `notas`.

## Fuentes oficiales (en orden)
SUIN-Juriscol · Gestor Normativo (Función Pública) · Secretaría del Senado · **Banco de la República** (banrep.gov.co — para el régimen cambiario: Resolución Externa 1/2018 de la JDBR y la Circular Reglamentaria Externa DCIN-83) · Diario Oficial · Corte Constitucional.

## Regla dura
**No inventes.** Si no lo confirmas en fuente oficial, `confianza: "NO CONFIRMADO"` + explica en `notas`.

## Puntos específicos a resolver
- **`ley-1561-2012`**: proceso verbal especial de saneamiento de la falsa tradición y titulación de la posesión — confirmar alcance y competencia (¿notarial o judicial?).
- **Régimen cambiario** (`ley-9-1991`, `decreto-1068-2015`, `resolucion-externa-jdbr-1-2018`, `circular-dcin-banrep`): confirmar el marco de **inversión extranjera** en inmuebles y la **canalización por el mercado cambiario** (declaración de cambio — **Formulario No. 4**). Para la Circular DCIN, dar la referencia vigente exacta (DCIN-83) y su URL en banrep.gov.co.
- **`ley-160-1994-art-39`**: confirmar el texto del art. 39 (además del art. 72 que ya está verificado) sobre restricciones/UAF.
- **`decreto-1429-2020-apoyos`**: acuerdos de apoyo y directivas anticipadas ante notario (reglamenta la Ley 1996/2019) — confirmar vigencia y alcance notarial.

## Formato de salida
Un **único JSON** con una entrada por `slug` (7 en total), campos: `url_oficial`, `estado`, `vigencia_desde`, `vigencia_hasta`, `texto_articulo`, `confianza`, `notas`. No cambies los `slug`.

## Lista de las 7 normas

| slug | norma / artículo | materia | confianza actual |
|---|---|---|---|
| ley-1561-2012 | Ley 1561/2012 | saneamiento / falsa tradición | baja |
| ley-9-1991-regimen-cambiario | Ley 9/1991 | régimen cambiario | baja |
| decreto-1068-2015-regimen-cambiario | Decreto 1068/2015 | DUR sector hacienda (cambiario) | baja |
| resolucion-externa-jdbr-1-2018-regimen-cambiario | Resolución Externa 1/2018 (JDBR) | Banco de la República | baja |
| circular-dcin-banrep-regimen-cambiario | Circular DCIN (DCIN-83) | Banco de la República | baja |
| ley-160-1994-art-39 | Ley 160/1994 art. 39 | agrario / UAF | baja |
| decreto-1429-2020-apoyos | Decreto 1429/2020 | capacidad legal / apoyos | baja |

> Cuando devuelvas el JSON, se aplica al corpus con el mismo criterio conservador que la tanda anterior (se toman URL/texto/vigencia/confianza; el `estado` se contrasta y los conflictos van a reporte para el notario).
