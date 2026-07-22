# Reporte de conflictos — verificación GPT vs corpus (2026-07-21)

> GPT verificó las 67 normas contra fuente oficial. Se aplicaron al corpus **URL oficial, texto del artículo, vigencia y confianza**. El `estado` NO se pisó (para no importar una clasificación dudosa ni alterar la aplicabilidad operativa del motor). Estas discrepancias de `estado` requieren **decisión del notario**.

## Discrepancias de estado (nuestro → GPT)

| slug | nuestro | GPT | nota GPT |
|---|---|---|---|
| decreto-ley-960-1970-art-13 | modificada | **vigente** | Texto cotejado en Gestor Normativo. |
| decreto-ley-960-1970-art-14 | modificada | **vigente** | Texto cotejado en Gestor Normativo. |
| decreto-ley-960-1970-art-38 | modificada | **vigente** | Texto cotejado en Gestor Normativo de Función Pública. |
| decreto-ley-960-1970-art-39 | modificada | **vigente** | Texto cotejado en Gestor Normativo de Función Pública. |
| decreto-1069-2015-dur-sector-justicia | vigente | **modificada** | Decreto Único Reglamentario del Sector Justicia y del Derecho, versión integrada. |
| ley-1579-2012 | vigente | **modificada** | El slug corresponde a la ley completa. |
| ley-1579-2012-art-4 | vigente | **modificada** | Texto operativo cotejado en la compilación oficial. La ley ha recibido modificaciones posteriores. |
| ley-1579-2012-art-8 | vigente | **modificada** | Transcripción parcial verificada del artículo 8. El artículo continúa con datos de identificación y estructura |
| ley-223-1995-art-230 | vigente | **modificada** | La tarifa departamental concreta debe verificarse en la ordenanza vigente. Para Antioquia 2026 se identificó l |
| ley-258-1996-art-3 | modificada | **vigente** | La sanción de nulidad absoluta no está en este artículo sino en el inciso final del artículo 6. |
| codigo-civil-art-1521 | vigente | **derogada_parcial** | El ordinal 4 está derogado; los ordinales 1 a 3 permanecen en la compilación vigente. |
| codigo-civil-art-1931 | vigente | **derogada_total** | El artículo 1931 fue derogado expresamente por la Ley 45 de 1930. La regla civil sustitutiva está en el artícu |
| ley-70-1931-ley-495-1999-patrimonio-familia | vigente | **modificada** | El slug agrupa dos leyes. Deben integrarse los condicionamientos constitucionales posteriores sobre beneficiar |
| decreto-0732-2026 | vigente | **compilada** | Expedido el 8 de julio de 2026, publicado en el Diario Oficial 53.548 del 9 de julio de 2026 y vigente desde e |
| estatuto-tributario-art-398 | vigente | **modificada** | Aplica a enajenación de activos fijos por personas naturales. |
| estatuto-tributario-art-399 | vigente | **derogada_parcial** | La compilación oficial muestra un inciso derogado por el artículo 376 de la Ley 1819 de 2016. |
| estatuto-tributario-art-401 | vigente | **modificada** | La tarifa operativa para adquisición de inmuebles por persona jurídica se desarrolla reglamentariamente: vivie |
| estatuto-tributario-art-468 | vigente | **modificada** | Artículo modificado por el artículo 184 de la Ley 1819 de 2016. |
| decreto-830-2021 | vigente | **compilada** | El decreto fue incorporado al Decreto 1081 de 2015. Se transcribe el encabezado operativo del artículo 2 y el  |
| ley-2097-2021-redam | vigente | **modificada** | El slug cubre la ley completa, pero la regla notarial específica se encuentra en el artículo 6 numeral 3. |
| ley-3-1991-subsidio-vivienda | vigente | **modificada** | Se transcribe el núcleo vigente del artículo 6 según sus reformas. |
| ley-795-2003-leasing-habitacional | vigente | **modificada** | Artículo declarado exequible de forma condicionada por la Sentencia C-936 de 2003. |
| ley-546-1999-art-23 | vigente | **modificada** | El parágrafo fue añadido por el artículo 2 de la Ley 2434 de 2024. NO CONFIRMADO expresamente el orden de cálc |
| ley-546-1999-art-24 | vigente | **modificada** | Artículo modificado por el artículo 38 de la Ley 1537 de 2012. |
| resolucion-snr-2026-001726-6 | vigente | **modificada** | Resolución expedida el 29 de enero de 2026. Su artículo de vigencia fue modificado por la Resolución RES-2026- |
| resolucion-dian-000238-2025-uvt-2026 | vigente | **compilada** | Resolución expedida el 15 de diciembre de 2025, publicada en el Diario Oficial 53.338 del 17 de diciembre de 2 |
| decreto-1469-2025-0159-2026-smlmv-2026 | vigente | **suspendida** | El Decreto 1469 de 2025 fijó el mismo valor, pero quedó suspendido provisionalmente desde el 19 de febrero de  |
| ley-160-1994-art-72 | vigente | **modificada** | El artículo 72 es extenso y contiene más reglas y excepciones. |
| decreto-906-2025 | vigente | **compilada** | Expedido el 13 de agosto de 2025, publicado y vigente el 14 de agosto de 2025, Diario Oficial 53.212. |
| ley-2447-2025 | vigente | **modificada** | Diario Oficial 53.029 del 13 de febrero de 2025; rige desde su promulgación según el artículo 21. Algunos erro |

### Prioridad de revisión (impacto legal alto)
- **codigo-civil-art-1521**: GPT dice `derogada_parcial` (teníamos `vigente`). Confirmar antes de usar en escritura.
- **codigo-civil-art-1931**: GPT dice `derogada_total` (teníamos `vigente`). Confirmar antes de usar en escritura.
- **estatuto-tributario-art-399**: GPT dice `derogada_parcial` (teníamos `vigente`). Confirmar antes de usar en escritura.
- **decreto-1469-2025-0159-2026-smlmv-2026**: GPT dice `suspendida` (teníamos `vigente`). Confirmar antes de usar en escritura.

## NO CONFIRMADO por GPT (quedan en confianza=baja)
- **ley-2195-2022-siplaft**: No se confirmó que la Ley 2195 de 2022 sea la fuente jurídica específica del SIPLAFT notarial. La ley contiene reglas de debida diligencia y prevención de corrupción, pero el SIPLAFT de notarías provi
- **circular-snr-1536-2013-ley-1581-2012**: Se localizó el PDF en dominio oficial SNR, pero no fue posible extraer y cotejar directamente su texto íntegro. La clasificación del slug como 'Ley 1581/datos personales' no coincide con el objeto rep
- **resolucion-snr-2026-000964-6**: La SNR confirma oficialmente la Resolución RES-2026-000964-6, el ajuste IPC de 5,10%, la vigencia desde el 1 de febrero de 2026 y la tarifa del 3 por mil sobre el excedente. No se localizó el texto of
