# SESSION.md — EasyProNotarial-2

---
## Sesión 2026-05-28

**Objetivo de la sesión:** Diagnóstico de dos bugs en el motor de minutas (campos ADQUISICIÓN y VIVIENDA FAMILIAR) e implementación de la UI y lógica de reemplazo para las decisiones notariales.

**Realizado:**
- **Diagnóstico Bug 1 — ADQUISICIÓN:** Confirmada ausencia total en todas las capas — prompt detector, tipo TypeScript, reemplazador, UI y payload. Requiere implementación completa desde cero.
- **Diagnóstico Bug 2 — VIVIENDA FAMILIAR:** Confirmado gap parcial — detector y tipo TS existen (`datos.decisiones`), faltaban UI y bloque en reemplazador.
- **nueva-minuta-workspace.tsx — DecisionesCard:** Nuevo componente con 3 toggles de 3 estados (`?`/`Sí`/`No`) para `vivienda_familiar`, `patrimonio_familia`, `notificacion_electronica`; colores amber/emerald/rose consistentes con el design system; badge "pendiente" cuando el valor es null.
- **nueva-minuta-workspace.tsx — estado y flujo:** `decisionesEdit` añadido como `useState`; inicialización desde `result.datos.decisiones` en `handleAnalizar` (merge con defaults null para los 3 campos); reset en `clearFile`; `updateDecision` handler; `decisiones: decisionesEdit` incluido en `datosNuevos` de `handleGenerar` (sobrescribe el spread de `analisisResult.datos`).
- **nueva-minuta-workspace.tsx — render Paso 2:** `<DecisionesCard>` renderizado después de ValoresCard, antes del botón "Continuar a generar".
- **reemplazador.py — construir_lista_reemplazos:** Bloque `# DECISIONES` añadido al final; itera los 3 campos; guarda contra `None` en cualquier extremo; convierte bool → `"SÍ"`/`"NO"` antes de llamar `agregar_reemplazo`; reutiliza el guard `viejo == nuevo` existente para no generar par inútil cuando no hay cambio.

**Archivos creados/modificados:**
- `backend/app/services/minuta/reemplazador.py` — bloque DECISIONES en construir_lista_reemplazos (L474–487)
- `frontend/components/minutas/nueva-minuta-workspace.tsx` — DecisionesCard, estado decisionesEdit, inicialización, handler, render y payload

**Pendientes para la próxima sesión:**
1. **[CRÍTICO] Deploy frontend a Vercel** — Múltiples sesiones de cambios acumulados sin deploy: `vercel --cwd frontend --prod`
2. **[CRÍTICO] Deploy backend a Railway** — reemplazador.py modificado; push al repo activa Railway automáticamente
3. **[CRÍTICO] Verificar fix tour en producción** — Confirmar que click en zona de upload no cierra el tour; remover `console.log("TOUR VISIBLE:", tourVisible)` en `nueva-minuta-workspace.tsx` línea ~1340 antes de demo
4. **[CRÍTICO] Bug 1 ADQUISICIÓN — implementar desde cero** — Requiere: (a) nueva sección en PROMPT_B2 con campos `forma_adquisicion`, `escritura_anterior`, `notaria_anterior`, `vendedor_original`; (b) nuevo tipo `MinutaAdquisicion` en minuta.ts; (c) sección en construir_lista_reemplazos; (d) `AdquisicionCard` en el formulario
5. **[CRÍTICO] Fix gap 1 — agregar `actividad_economica` a PersonaCard** — campo en tipo y reemplazador pero sin UI en el formulario
6. **[CRÍTICO] Fix gap 2 — agregar `domicilio` y `estado_civil` a `construir_lista_reemplazos()`** en `reemplazador.py:408`
7. **[CRÍTICO] Fix gap 4 — concordancia cuando solo cambia género** (sin cambio de nombre) en `concordancia.py:152`
8. **[MEDIA] Fix gap 3 — UI para decisiones** ✅ RESUELTO en esta sesión
9. **[BAJA] Remover prints `[GENERO DEBUG]`** de `reemplazador.py`
10. **[BAJA] Alembic out-of-sync** — `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';` en Supabase

**Estado al cierre:**
- Backend: Railway operativo — `reemplazador.py` modificado, pendiente push/deploy
- Frontend: Vercel pendiente deploy — múltiples sesiones acumuladas sin deploy a producción
- BD producción: operativa, alembic_version desincronizada (pendiente UPDATE manual)
- Git: 2 archivos modificados sin commitear — se commitean en este cierre

---
## Sesión 2026-05-26 (noche 4)

**Objetivo de la sesión:** Diagnosticar y corregir bugs del tour guiado de minutas: cierre accidental al hacer click en la zona de upload (BUG 1) y ausencia de botón de relaunch visible (BUG 2).

**Realizado:**
- **Diagnóstico BUG 1 (tour se cierra al subir documento):** Identificada causa raíz — el backdrop div de `MinutasTour` (z-index 9998, `onClick={onSkip}`) capturaba todos los clicks del área visible, incluyendo los dirigidos a la zona de upload. El spotlight tenía `pointerEvents:none`, lo que dejaba pasar los clicks al backdrop en lugar de al `<label>` del upload zone.
- **Fix BUG 1 — minutas-tour.tsx:** (1) Spotlight cambiado a `pointerEvents:"auto"` para que capture sus propios clicks antes de que lleguen al backdrop. (2) Backdrop `onClick` reemplazado por `handleBackdropClick` inline que verifica `currentTargetEl.contains(e.target)` antes de llamar `onSkip`.
- **Fix BUG 2 — nueva-minuta-workspace.tsx:** Agregado botón fijo `?` en esquina inferior derecha con `fixed bottom-6 right-6 z-[9997]`, importado `HelpCircle` de lucide-react, llama `handleTourRelaunch`.
- **Debug log — nueva-minuta-workspace.tsx:** Agregado `console.log("TOUR VISIBLE:", tourVisible)` antes del return para confirmar diagnóstico BUG 1 (pendiente de limpiar).
- **⚠ Tour no activa en local:** El tour no se activa en el entorno de desarrollo local. No se pudo verificar el fix. Pendiente revisar 2026-05-27.

**Archivos creados/modificados:**
- `frontend/components/minutas/minutas-tour.tsx` — backdrop: contains check antes de onSkip; spotlight: pointerEvents none→auto
- `frontend/components/minutas/nueva-minuta-workspace.tsx` — import HelpCircle, console.log debug, botón relaunch fijo z-[9997]

**Pendientes para la próxima sesión:**
1. **[CRÍTICO] Verificar fix tour en producción o entorno funcional** — Confirmar que: (a) click en zona de upload no cierra el tour, (b) file picker abre mientras el tour está activo, (c) click fuera del spotlight sí cierra el tour. Si el file picker no abre con pointerEvents:auto en spotlight, agregar `onClick` al spotlight que reenvíe el click: `el?.querySelector('input[type="file"], label')?.click()`
2. **[CRÍTICO] Remover console.log debug** — `console.log("TOUR VISIBLE:", tourVisible)` en `nueva-minuta-workspace.tsx` línea 1248 antes de deploy
3. **[CRÍTICO] Fix gap 1 — agregar `actividad_economica` a PersonaCard** en `nueva-minuta-workspace.tsx:446`
4. **[CRÍTICO] Fix gap 2 — agregar `domicilio` y `estado_civil` a `construir_lista_reemplazos()`** en `reemplazador.py:408`
5. **[CRÍTICO] Fix gap 4 — concordancia cuando solo cambia género** (sin cambio de nombre) en `concordancia.py:152`
6. **[MEDIA] Fix gap 3 — UI para decisiones** (vivienda_familiar, patrimonio_familia, notificacion_electronica)
7. **[BAJA] Remover prints `[GENERO DEBUG]`** de `reemplazador.py`
8. **[BAJA] Alembic out-of-sync** — `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';`

**Estado al cierre:**
- Backend: Railway operativo — sin cambios de backend en esta sesión
- Frontend: Vercel pendiente deploy — `minutas-tour.tsx` y `nueva-minuta-workspace.tsx` modificados sin deploy a producción; tour no verificado en local
- BD producción: operativa, alembic_version desincronizada (pendiente UPDATE manual)
- Git: 2 archivos sin commitear — se commitean en este cierre

---
## Sesión 2026-05-26 (noche 3)

**Objetivo de la sesión:** Implementar tour guiado del módulo de minutas con overlay spotlight, tooltip posicionado dinámicamente y estado persistente entre re-renders.

**Realizado:**
- **minutas-tour.tsx — nuevo componente (v1):** Tour de 7 pasos con overlay `box-shadow: 0 0 0 9999px` (más confiable que SVG mask), tooltip con flecha CSS border-trick posicionado automáticamente (top/bottom/left/right según espacio disponible), animación pulse en el elemento destacado, progress dots, botón `?` fijo para relanzar
- **nueva-minuta-workspace.tsx — IDs de tour:** Agregados 7 `id` a elementos target: `tour-upload-zone`, `tour-btn-analizar`, `tour-validacion-banner`, `tour-persona-0`, `tour-inmueble-card`, `tour-valores-card`, `tour-btn-generar`; `PersonaCard` recibe prop `id?: string`
- **minutas-tour.tsx — fix overlay SVG:** Reemplazado `<svg mask>` por `div` con `box-shadow: 0 0 0 9999px rgba(0,0,0,0.60)` — el SVG usaba `fill="rgba()"` que no es válido en atributos SVG; tambien eliminado `rgba(var(--primary))` que tampoco es válido CSS en `rgba()`
- **minutas-tour.tsx — fix delay inicial:** Eliminado `setTimeout(setActive, 750)` — el tour ahora activa inmediatamente en el `useEffect` de mount; reducida latencia total de ~1150ms a ~400ms
- **minutas-tour.tsx — refactor state lifting:** Estado `active`/`currentStep`/`visible` movido al padre `NuevaMinutaWorkspace`; `MinutasTour` pasa a ser componente controlado que recibe `visible`, `currentStep`, `onNext`, `onPrev`, `onSkip`, `onFinish`, `onRelaunch` como props — así el estado del tour sobrevive cualquier re-render del workspace (file upload, drag, edición de campos, etc.)
- **nueva-minuta-workspace.tsx — tour state:** `tourVisible` + `tourStep` como `useState`; `useEffect([], ...)` chequea localStorage (`easypro_minutas_tour_done`) y activa el tour en primera visita; handlers: `handleTourNext/Prev/Skip/Finish/Relaunch`

**Archivos creados/modificados:**
- `frontend/components/minutas/minutas-tour.tsx` — nuevo: tour guiado 7 pasos, overlay box-shadow, tooltip auto-posicionado, estado controlado por props
- `frontend/components/minutas/nueva-minuta-workspace.tsx` — IDs de tour en 7 elementos, prop `id` en PersonaCard, estado del tour (`tourVisible`/`tourStep`), handlers, `<MinutasTour>` con props completos

**Pendientes para la próxima sesión:**
1. **[CRÍTICO] Fix gap 1 — agregar `actividad_economica` a PersonaCard** en `nueva-minuta-workspace.tsx:446` (campo en tipo y reemplazador pero sin UI)
2. **[CRÍTICO] Fix gap 2 — agregar `domicilio` y `estado_civil` a `construir_lista_reemplazos()`** en `reemplazador.py:408`
3. **[CRÍTICO] Fix gap 4 — concordancia cuando solo cambia género** (sin cambio de nombre) en `concordancia.py:152`
4. **[CRÍTICO] Reescribir detector con Structured Outputs** (`json_schema` + `strict: True`) per gap 5
5. **[MEDIA] Fix gap 3 — UI para decisiones** (vivienda_familiar, patrimonio_familia, notificacion_electronica)
6. **[BAJA] Remover `[GENERO DEBUG]` prints** de `reemplazador.py`
7. **[BAJA] Alembic out-of-sync** — `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';`

**Estado al cierre:**
- Backend: Railway operativo — sin cambios de backend en esta sesión
- Frontend: Vercel pendiente deploy — `minutas-tour.tsx` nuevo + `nueva-minuta-workspace.tsx` modificado sin deploy a producción
- BD producción: operativa, alembic_version desincronizada (pendiente UPDATE manual)
- Git: 2 archivos sin commitear — se commitean en este cierre

---
## Sesión 2026-05-26 (noche 2)

**Objetivo de la sesión:** Auditoría técnica completa del motor de minutas — lectura y análisis de todos los archivos del sistema sin modificar código.

**Realizado:**
- **Lectura completa de 9 archivos clave:** `router.py`, `detector.py`, `reemplazador.py`, `concordancia.py`, `validador.py`, `nueva-minuta-workspace.tsx`, `minuta.ts`, `listas-notariales.ts`, `colombia-geo.ts`
- **Flujo completo documentado:** desde upload del .docx hasta apertura en OnlyOffice, con cada función, endpoint y transformación identificada paso a paso
- **Análisis del formulario:** PersonaCard estática (11 campos visibles, `actividad_economica` ausente), InmuebleCard 18 campos, NotariaCard con selectores geo encadenados, ValoresCard dinámica
- **Detector auditado:** clasificación B1/B2 heurística, PROMPT_B2 con 8 secciones, uso de `json_object` sin schema estricto, `max_tokens=8000`
- **Reemplazador auditado:** `construir_lista_reemplazos` cubre 14 campos inmueble + personas + notaría + fechas; `domicilio` y `estado_civil` se editan en UI pero NO se reemplazan; `_normalizar_guiones` parcialmente inefectivo
- **Validador auditado:** capa determinista + GPT-4o-mini; valida datos del detector, no los editados por el usuario; `CAMPOS_OBLIGATORIOS_POR_ACTO` incompleto
- **Concordancia auditada:** solo se dispara si nombre Y género cambian; artículos de rol ordenados por longitud; texto truncado a 40k chars
- **10 gaps críticos identificados** con archivos y líneas exactas

**Archivos creados/modificados:**
- (ninguno — sesión de solo lectura)

**Pendientes para la próxima sesión:**
1. **[CRÍTICO] Fix gap 1 — agregar `actividad_economica` a PersonaCard** en `nueva-minuta-workspace.tsx:446` (campo en tipo y reemplazador pero sin UI)
2. **[CRÍTICO] Fix gap 2 — agregar `domicilio` y `estado_civil` a `construir_lista_reemplazos()`** en `reemplazador.py:408`
3. **[CRÍTICO] Fix gap 4 — concordancia cuando solo cambia género** (sin cambio de nombre) en `concordancia.py:152`
4. **[CRÍTICO] Reescribir detector con Structured Outputs** (`json_schema` + `strict: True`) per gap 5
5. **[MEDIA] Fix gap 3 — UI para decisiones** (vivienda_familiar, patrimonio_familia, notificacion_electronica)
6. **[BAJA] Remover `[GENERO DEBUG]` prints** de `reemplazador.py:319`
7. **[BAJA] Alembic out-of-sync** — `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';`

**Estado al cierre:**
- Backend: Railway operativo — último commit `9ec57a5`, sin cambios de backend en esta sesión
- Frontend: Vercel operativo — easypronotarial.com, sin cambios de frontend en esta sesión
- BD producción: operativa, alembic_version desincronizada (pendiente UPDATE manual)
- Git: árbol limpio — solo `tsconfig.tsbuildinfo` (ignorar)

---
## Sesión 2026-05-26 (tarde 2)

**Objetivo de la sesión:** Mejorar el formulario de minutas — normalización de campos del inmueble, selectores geográficos Colombia, separador de miles en valores monetarios.

**Realizado:**
- **nueva-minuta-workspace.tsx — normalizar tipo inmueble (977724e):** `handleAnalizar` aplica `TIPOS_INMUEBLE_MAP` antes de `setInmuebleEdit` para que `"apartamento"` → `"Apartamento"` coincida con las opciones del select; cast a `Partial<MinutaInmueble>` para resolver error TypeScript
- **detector.py — campos catastrales y orden actos (c11cbb0):** Sección INMUEBLE del PROMPT_B2 expandida con instrucciones precisas para `cedula_catastral`, `codigo_catastral`, `area_construida`, `area_privada`, `area_total`, `piso`, `barrio`, `direccion`, `nota_linderos`, `linderos` (NO resumir). Sección ACTOS con regla de ordenamiento: acto principal primero, accesorios después. Ejemplo JSON actualizado con nuevos campos
- **detector.py — reforzar código catastral (9da8500):** Instrucción diferencia explícitamente código alfanumérico corto (ej: `AAX0009PUYC`) vs cédula numérica larga de 28 dígitos
- **nueva-minuta-workspace.tsx — ancho campos catastrales (9da8500):** Grid de 3 columnas partido en dos filas de 2 columnas — matrícula+cédula catastral en primera fila, código catastral en segunda; más espacio para valores largos
- **colombia-geo.ts — nuevo archivo (5eaf153):** 33 departamentos (incluyendo Bogotá D.C.) con ~900 municipios según DANE. Helpers `getMunicipiosByDepartamento()` y `getDepartamentoByMunicipio()`
- **nueva-minuta-workspace.tsx — selectores encadenados (5eaf153):** InmuebleCard reemplaza inputs de texto por selects departamento→municipio; al cambiar departamento, municipio se limpia automáticamente. NotariaCard agrega estado local `depNotaria` + selects encadenados con sincronización por ref desde `municipio_notaria`. `handleAnalizar` infiere departamento con `getDepartamentoByMunicipio()` si el detector no lo devuelve
- **nueva-minuta-workspace.tsx — separador de miles (1df8011):** Helpers `formatCOP()` (→ `200.000.000`) y `parseCOP()` (quita puntos antes de guardar); input de monto reemplaza `SectionField` con `type="text" inputMode="numeric"` que muestra valor formateado pero envía número limpio al backend

**Archivos creados/modificados:**
- `frontend/lib/colombia-geo.ts` — nuevo: 33 departamentos, ~900 municipios DANE, helpers geo
- `frontend/components/minutas/nueva-minuta-workspace.tsx` — normalización tipo inmueble, selectores geo encadenados, separador miles, ancho campos catastrales
- `backend/app/services/minuta/detector.py` — PROMPT_B2: campos catastrales expandidos, orden actos, código catastral diferenciado

**Pendientes para la próxima sesión:**
1. **[CRÍTICO] Reescribir detector con Structured Outputs de OpenAI** — Cambiar `response_format=json_object` por `json_schema` con `strict: True`; schema completo con `linderos` (norte/sur/oriente/occidente), `adquisicion` (forma, escritura previa, notaría, vendedor original), `poderes`, `valores_notariales` (derechos notariales, superfondo, IVA); prompts mejorados basados en documentos reales de Notaría de Bello
2. **[CRÍTICO] Verificar bug SEBASTIÁN en producción** — Generar minuta real con SEBASTIÁN y DANIELA, revisar logs Railway
3. **[CRÍTICO] Verificar concordancia en producción** — Confirmar que fix `finish_reason` resuelve crash con documento real
4. **[MEDIA] Formulario dinámico — campos faltantes persona** — `actividad_economica` no en PersonaCard; decisiones (vivienda_familiar, patrimonio_familia, notificacion_electronica) sin UI
5. **[BAJA] Debug prints `GENERO DEBUG`** — Remover de `router.py` y `reemplazador.py`
6. **[BAJA] Alembic out-of-sync** — `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';` en Supabase

**Estado al cierre:**
- Backend: Railway con deploy activo — `c11cbb0` y `9da8500` pusheados (Railway despliega automáticamente)
- Frontend: Vercel operativo — easypronotarial.com, 5 deploys realizados en esta sesión
- BD producción: operativa, alembic_version desincronizada (pendiente UPDATE manual)
- Git: árbol limpio — solo `tsconfig.tsbuildinfo` modificado (ignorar)

---
## Sesión 2026-05-27

**Objetivo de la sesión:** Fix JSON truncado en concordancia + expandir sección inmueble del formulario de minutas (18 campos, select tipo, textarea linderos).

**Realizado:**
- **concordancia.py — Fix 1 (texto truncado):** `texto_documento[:80000]` → `[:40000]` para reducir tokens enviados al modelo
- **concordancia.py — Fix 2 (max_tokens + finish_reason):** `max_tokens=16384` → `8000`; si `finish_reason == "length"` retorna `{"cambios": [], "truncado": True}` sin crash
- **concordancia.py — Fix 3 (prompt simplificado):** Eliminados `contexto_ejemplo` y `razon` del esquema JSON; solo `palabra_antes`, `palabra_despues`, `confianza` — respuestas más cortas
- **router.py — Fix 4 (try/except concordancia):** `detectar_concordancia` envuelto en try/except; si falla, `resultado_conc = {"cambios": []}` y el endpoint `/generar` continúa sin bloqueo
- **minuta.ts — MinutaInmueble extendida:** 8 campos → 18 campos nuevos: `cedula_catastral`, `codigo_catastral`, `area_construida`, `area_privada`, `area_total`, `direccion`, `barrio`, `piso`, `nota_linderos`, `propiedad_horizontal`
- **nueva-minuta-workspace.tsx — InmuebleCard expandida:** 5 inputs → 9 filas: select tipo de inmueble (8 opciones), número/piso, conjunto+barrio, dirección full-width, municipio+departamento+select propiedad horizontal, matrícula+cédula catastral+código catastral, 3 áreas m², coeficiente copropiedad, select nota de linderos (NOTAS_LINDEROS), textarea linderos (rows=5 con resize); `EMPTY_INMUEBLE` actualizado; import `NOTAS_LINDEROS` agregado
- **reemplazador.py — construir_lista_reemplazos:** Loop inmueble expandido de 5 a 14 campos; `tipo`/`direccion`/`barrio`/`piso` usan etiquetas sufijadas `_inmueble` para evitar conflicto con campos de persona en los logs

**Archivos creados/modificados:**
- `backend/app/services/minuta/concordancia.py` — fix tokens, prompt simplificado, manejo finish_reason
- `backend/app/modules/minuta/router.py` — try/except alrededor de detectar_concordancia
- `backend/app/services/minuta/reemplazador.py` — construir_lista_reemplazos inmueble expandido
- `frontend/lib/minuta.ts` — MinutaInmueble extendida a 18 campos
- `frontend/components/minutas/nueva-minuta-workspace.tsx` — InmuebleCard expandida, EMPTY_INMUEBLE, import NOTAS_LINDEROS

**Pendientes para la próxima sesión:**
1. **[CRÍTICO] Deploy frontend a Vercel** — `vercel --cwd frontend --prod` (commits de esta sesión + sesiones anteriores sin deploy)
2. **[CRÍTICO] Deploy backend a Railway** — concordancia.py fix crítico para producción; push al repo ya lo activa en Railway
3. **[CRÍTICO] Verificar bug SEBASTIÁN en producción** — Generar minuta real con SEBASTIÁN y DANIELA, revisar logs Railway
4. **[CRÍTICO] Verificar concordancia en producción** — Confirmar que fix finish_reason resuelve el crash; probar con documento real que tenga cambio de género
5. **[MEDIA] Formulario dinámico — campos faltantes persona** — `actividad_economica` no está en PersonaCard; decisiones (vivienda_familiar, patrimonio_familia, notificacion_electronica) sin UI
6. **[BAJA] Debug prints `GENERO DEBUG`** — Remover de `router.py` y `reemplazador.py` antes de demo
7. **[BAJA] Alembic out-of-sync** — `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';` en Supabase

**Estado al cierre:**
- Backend: Railway pendiente deploy — fixes concordancia y reemplazador sin push todavía
- Frontend: Vercel pendiente deploy — InmuebleCard expandida sin deploy a producción
- BD producción: operativa, alembic_version desincronizada (pendiente UPDATE manual)
- Git: 5 archivos modificados sin commitear — se commitean en este cierre

---
## Sesión 2026-05-26 (noche)

**Objetivo de la sesión:** Implementar Capa 2 del motor de minutas — listas notariales oficiales, fix estado civil dinámico por género, validador notarial con IA.

**Realizado:**
- **listas-notariales.ts — nuevo archivo (46255cf):** `ESTADOS_CIVILES_F` (12 opciones), `ESTADOS_CIVILES_M` (11 opciones), `ESTADOS_CIVILES_COMPARTIDOS`, `TIPOS_DOCUMENTO` (7 tipos con values C.C/C.E/T.I/PAS/P.P.T/R.C/NIT), `NOTAS_LINDEROS`, helper `getEstadosCiviles(genero)`
- **nueva-minuta-workspace.tsx — fix estado civil (46255cf):** Select dinámico filtrado por género (solo opciones femeninas/masculinas según selección); `handleChange` corregido — limpia estado_civil si el valor actual no aplica al nuevo género; cascada nacionalidad preservada; eliminadas `TIPO_DOC_OPTIONS` y `ESTADO_CIVIL_OPTIONS` hardcodeadas
- **detector.py — fix tipo_documento en prompt (3a94650):** Valores estandarizados `"C.C", "C.E", "T.I", "PAS", "P.P.T", "R.C", "NIT"` en PROMPT_B2; ejemplo JSON actualizado `CC → C.C`
- **minuta.ts — tipos completos (3a94650, 461f958):** Nueva interfaz `MinutaFechas`; `MinutaDatos` incluye `fechas?: MinutaFechas`; `MinutaAnalisisResult` incluye `texto_original?: string`; nuevas interfaces `MinutaValidacionCampo`, `MinutaValidacion`; `MinutaAnalisisResult` incluye `validacion?: MinutaValidacion`
- **validador.py — nuevo servicio Capa 2 (461f958, 9a1e643):** Validaciones deterministas sin IA (formato cédulas/NIT/T.I., matrícula, número escritura, roles por acto); validación IA con GPT-4o-mini usando `PROMPT_VALIDADOR`; retorna semáforos `ok/advertencia/faltante/inferido` por campo + alertas críticas + inferencias aplicadas + resumen con `listo_para_generar`; usa `_make_openai_client()` igual que `detector.py`
- **router.py — integración validador (461f958, 9a1e643):** Endpoint `/analizar` llama `validar_documento(datos, actos, api_key)` tras el análisis; try/except garantiza que fallo no bloquea
- **nueva-minuta-workspace.tsx — banner validación (461f958):** Paso 2 muestra banner verde/amarillo/rojo con nivel de confianza, conteo de campos, alertas críticas en rojo con ⚠, inferencias en azul con →

**Archivos creados/modificados:**
- `frontend/lib/listas-notariales.ts` — nuevo: listas oficiales notariales colombianas
- `frontend/components/minutas/nueva-minuta-workspace.tsx` — fix estado civil dinámico + banner validación
- `frontend/lib/minuta.ts` — MinutaFechas, MinutaValidacion, validacion? en AnalisisResult
- `backend/app/services/minuta/detector.py` — tipo_documento estandarizado en prompt
- `backend/app/services/minuta/validador.py` — nuevo: validador notarial Capa 2
- `backend/app/modules/minuta/router.py` — integrar validar_documento en /analizar
- `backend/requirements.txt` — sin anthropic (se agregó y se revirtió en la misma sesión)
- `backend/app/core/config.py` — sin anthropic_api_key (idem)

**Pendientes para la próxima sesión:**
1. **[CRÍTICO] Verificar validador en producción** — Hacer deploy a Railway y analizar un documento real; revisar que el banner aparece en Paso 2 y que las alertas/inferencias son correctas
2. **[CRÍTICO] Verificar bug SEBASTIÁN** — Generar minuta real con SEBASTIÁN y DANIELA, revisar logs Railway; múltiples fixes aplicados pero sin verificación en producción desde sesión 2026-05-23
3. **[CRÍTICO] Verificar concordancia con Claude** — SESSION anterior indica que concordancia.py fue migrada a Claude; confirmar ANTHROPIC_API_KEY en Railway y que artículos EL→LA funcionan
4. **[MEDIA] Debug prints `GENERO DEBUG`** — Hay prints de debug activos en `router.py` y `reemplazador.py` — remover antes de demo
5. **[MEDIA] Validador — probar con documentos reales** — Confirmar que inferencias (departamento desde municipio, zona desde matrícula) funcionan y que no hay falsos positivos en alertas críticas
6. **[BAJA] Alembic out-of-sync** — `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';` en Supabase producción (pendiente desde sesiones anteriores)

**Estado al cierre:**
- Backend: Railway operativo — último commit en repo `9a1e643`; pendiente deploy para activar validador
- Frontend: Vercel operativo — easypronotarial.com; pendiente deploy para activar banner validación
- BD producción: operativa, alembic_version desincronizada (pendiente)
- Git: árbol limpio — 4 commits nuevos pusheados

---
## Sesión 2026-05-26 (tarde)

**Objetivo de la sesión:** Fixes visuales del dashboard ejecutivo (pie chart, filtros, KPIs) y diagnóstico del formulario dinámico de minutas para planificar próxima iteración.

**Realizado:**
- **dashboard.tsx — rediseño PieActCard (b3404e6):** Donut chart (`innerRadius=55`), leyenda lateral custom con scroll, `CustomTooltip` con nombre + cantidad + porcentaje; removidos `label`/`labelLine`/`Legend`/`ResponsiveContainer`
- **dashboard.tsx — filtros grid fluido (16e2f76):** Grid `md:grid-cols-2 xl:grid-cols-12` con `col-span-2` fijo → `sm:grid-cols-2 lg:grid-cols-3`; `rounded-2xl` → `rounded-lg` en todos los controles; botones de `rounded-full` + `ep-card-soft` → `rounded-lg` con CSS vars del design system
- **dashboard.tsx — fixes post-deploy (87eea3f, bcb7646):** Grid reducido a `lg:grid-cols-3` (5 filtros quedan 3+2 sin solitarios); título "Tipos de acto" `uppercase tracking-widest` removido; botón submit `bg-[var(--primary)]` → `bg-primary` (clase Tailwind directa, CSS var no resolvía en producción)
- **dashboard.tsx — fixes visuales tanda 2 (4730d95):** KPI labels sin `uppercase tracking-[0.18em]`; `formatEstado()` convierte `revision_aprobador` → "Revision Aprobador" en docsByState; card notaría navy full-width reemplazada por tarjeta discreta con icono `Building2`; título pie chart `text-accent` → `text-[var(--ink)]`
- **Diagnóstico detector.py + /analizar:** Lectura completa — detector usa `gpt-4o-mini`, heurística local para B1/B2, `max_tokens=8000`, endpoint `/analizar` es wrapper directo sin lógica adicional
- **Diagnóstico formulario dinámico:** El formulario del Paso 2 es completamente estático — no hay lógica por tipo de acto. Campos del backend que no se muestran: `actividad_economica`, `inmueble.tipo`, `inmueble.coeficiente_copropiedad`, `inmueble.linderos`, `datos.decisiones` (vivienda_familiar, patrimonio_familia, notificacion_electronica). `datos.fechas` se accede vía cast manual, no está en el tipo `MinutaDatos`.

**Archivos creados/modificados:**
- `frontend/components/app-shell/dashboard.tsx` — PieActCard donut, filtros grid fluido, fixes visuales KPIs/estados/notaría/pie title

**Pendientes para la próxima sesión:**
1. **[CRÍTICO] Deploy frontend a Vercel** — 4 commits locales sin deploy a producción: `vercel --cwd frontend --prod`
2. **[CRÍTICO] Verificar bug SEBASTIÁN en producción** — Generar minuta real con SEBASTIÁN y DANIELA, revisar logs Railway
3. **[CRÍTICO] Verificar concordancia Claude** — Confirmar `ANTHROPIC_API_KEY` en Railway y artículos EL→LA / DEL→DE LA
4. **[MEDIA] Formulario dinámico — campos faltantes** — Agregar `actividad_economica` a `PersonaCard`; UI para `decisiones` (checkboxes vivienda_familiar, patrimonio_familia, notificacion_electronica); tipar `fechas` en `MinutaDatos`
5. **[BAJA] Debug prints `GENERO DEBUG`** — Remover de `router.py` y `reemplazador.py` antes de demo
6. **[BAJA] Alembic out-of-sync** — `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';` en Supabase

**Estado al cierre:**
- Backend: Railway operativo — sin cambios de backend en esta sesión
- Frontend: Vercel desactualizado — 4 commits locales pendientes de deploy
- BD producción: operativa, alembic_version desincronizada (pendiente UPDATE manual)
- Git: árbol limpio — 4 commits ahead de origin/main (se pushean en este cierre)

---
## Sesión 2026-05-26

**Objetivo de la sesión:** Renovación del design system (tipografía, tokens semánticos, colores de gráficas) e implementación de estados de progreso por pasos para las acciones IA.

**Realizado:**
- **globals.css — tipografía:** `font-family` cambia de Aptos a `var(--font-jakarta)` con fallback a Segoe UI
- **layout.tsx — Plus Jakarta Sans (1059f62):** `next/font/google` con pesos 300/400/500/600, variable CSS `--font-jakarta` inyectada en `<body>`
- **globals.css — variables semánticas (1059f62):** Nuevas vars en `:root` y `[data-theme="dark"]`: `--primary-light`, `--error`, `--error-text`, `--error-border`, `--warning-text`, `--warning-border`, `--success-text`, `--success-border`, `--info-bg`, `--info-text`, `--info-border`
- **globals.css — componentes .ep-* (1059f62):** `.ep-card` con `0.5px` border + hover state con sombra suave; `.ep-nav-item` con `transition: 0.12s`; 5 nuevas clases `.ep-badge-{success,warning,error,info,neutral}`; sombras inset dark-safe (0.04 light / 0.02 dark con override `[data-theme="dark"]`)
- **validated-input.tsx (1059f62):** Colores de error usan `var(--error-text)` y `var(--error-border)` en lugar de `rose-500`
- **color-constants.ts (1059f62):** Nuevo archivo `frontend/lib/color-constants.ts` con `CHART_COLORS` y `CHART_PALETTE` sincronizados con el design system
- **dashboard.tsx (1059f62 + b3404e6):** `CHART_PALETTE` reemplaza array hardcodeado; luego rediseño completo del PieActCard: donut chart (`innerRadius=55`), leyenda lateral custom con color swatches, tooltip personalizado usando CSS vars del sistema
- **ai-progress-modal.tsx (b12bb3b):** Nuevo componente reutilizable con pasos `done/active/pending`, barra de progreso animada y `PulseDots` con `@keyframes ep-pulse`; dark-mode nativo vía CSS vars
- **nueva-minuta-workspace.tsx (b12bb3b):** `handleAnalizar` y `handleGenerar` integran `AiProgressModal` con 4 pasos cada uno; progreso simulado + cierre automático; modal se cierra en `catch`
- **create-case-wizard.tsx (b12bb3b):** `handlePrimaryAction` paso 2 (Gari) muestra `AiProgressModal` con 5 pasos (plantilla → intervinientes → redactar → cláusulas → guardar); modal se cierra en `catch`

**Archivos creados/modificados:**
- `frontend/app/layout.tsx` — Plus Jakarta Sans, variable --font-jakarta
- `frontend/app/globals.css` — font-family, vars semánticas, .ep-badge-*, sombras inset, @keyframes ep-pulse
- `frontend/components/ui/validated-input.tsx` — error colors con CSS vars
- `frontend/lib/color-constants.ts` — nuevo archivo, CHART_COLORS + CHART_PALETTE
- `frontend/components/app-shell/dashboard.tsx` — CHART_PALETTE + rediseño PieActCard donut
- `frontend/components/ui/ai-progress-modal.tsx` — nuevo componente AiProgressModal
- `frontend/components/minutas/nueva-minuta-workspace.tsx` — AiProgressModal en analizar y generar
- `frontend/components/cases/create-case-wizard.tsx` — AiProgressModal en Gari paso 2

**Pendientes para la próxima sesión:**
1. **[CRÍTICO] Verificar bug SEBASTIÁN en producción** — Generar minuta real con SEBASTIÁN y DANIELA, revisar logs Railway para confirmar que SEBASTIÁN no recibe reemplazos incorrectos
2. **[CRÍTICO] Verificar concordancia con Claude** — Confirmar `ANTHROPIC_API_KEY` en Railway y que artículos EL→LA / DEL→DE LA funcionan
3. **[CRÍTICO] Deploy a producción** — `vercel --cwd frontend --prod` (3 commits nuevos pendientes de deploy) + push a Railway del backend si hay cambios
4. **[MEDIA] Guiones dobles `-- -` sin resolver del todo** — Confirmar con documento real que `_normalizar_guiones` funciona correctamente
5. **[BAJA] Alembic out-of-sync** — Ejecutar en Supabase: `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';`
6. **[BAJA] Debug prints `GENERO DEBUG`** — Remover prints de debug en `router.py` y `reemplazador.py` antes de demo

**Estado al cierre:**
- Backend: Railway operativo — commit `afab702` activo (sin cambios de backend hoy)
- Frontend: Vercel pendiente deploy — 3 commits nuevos locales no pusheados a Vercel
- BD producción: operativa, alembic_version desincronizada (pendiente UPDATE manual)
- Git: árbol limpio — 3 commits ahead de origin/main (se pushean en este cierre)

---
## Sesión 2026-05-23 (tarde)

**Objetivo de la sesión:** Completar el motor de minutas — fixes de género/guiones, secciones editables de inmueble/notaría/valores en el frontend, y cobertura completa de reemplazos en el backend.

**Realizado:**
- **reemplazador.py — _normalizar_guiones (9fdb543, 1b57295, f878b7b, c7c9eec):** Múltiples iteraciones: primero consolidar texto en runs[0] vaciar el resto; luego refactors con guard `not run.text`, colapso de `--` solo cuando rodeado de espacios, y finalmente reemplazar dentro de cada run para preservar formato
- **router.py — todos_nombres_doc (9fdb543, fc5e004, e2883dc):** Enriquecer con scanner de secuencias MAYÚSCULAS del documento; luego cambiar a escanear todo el doc sin filtro de línea conocida; finalmente procesar personas F antes que M y filtrar falsos positivos
- **router.py — aplicar genero contextual (433b345):** Aplicar reemplazos de género a TODAS las personas nuevas con género definido, no solo las que cambian M↔F
- **concordancia.py — refactor y fixes (a2099bb, e6ab5c8, ff9f84c, 715d304, afab702):** Concordancia vía Claude solo maneja artículos de rol; recibe `personas_resto` para preservar género de otras personas; max_tokens 8000 → 32000 → 16384 (límite real del modelo); strip markdown; try/except con diagnóstico
- **reemplazador.py — construir_lista_reemplazos (12bba1d, 2eddc5b):** Agrega secciones `notaria` (nombre_notaria, municipio_notaria, numero_escritura), `fechas` (fecha_otorgamiento) e `inmueble` completo (municipio, departamento); guard contra valores non-string
- **nueva-minuta-workspace.tsx — secciones editables:** Tres nuevas cards en Paso 1: `InmuebleCard`, `NotariaCard`, `ValoresCard`; estado `inmuebleEdit`/`notariaEdit`/`valoresEdit`; `handleGenerar` pasa los tres al backend; fix `n.trim is not a function` con `?? ""`; null-checks en inicialización desde `analisisResult.datos`
- **nueva-minuta-workspace.tsx — numeroALetras:** Función de conversión número a letras (pesos moneda corriente) integrada en el workspace
- **navigation.ts:** "Crear Minuta" redirige a `/dashboard/minutas/nueva` en lugar de `/dashboard/casos/crear`

**Archivos creados/modificados:**
- `backend/app/modules/minuta/router.py` — scanner nombres, genero contextual todas las personas, todos_nombres_doc
- `backend/app/services/minuta/reemplazador.py` — _normalizar_guiones (múltiples fixes), construir_lista_reemplazos completo, guard non-string
- `backend/app/services/minuta/concordancia.py` — max_tokens 16384, strip markdown, try/except, refactor a solo artículos, personas_resto
- `frontend/components/minutas/nueva-minuta-workspace.tsx` — 3 secciones editables, numeroALetras, null-checks, fix trim
- `frontend/lib/navigation.ts` — "Crear Minuta" apunta a /minutas/nueva

**Pendientes para la próxima sesión:**
1. **[CRÍTICO] Verificar bug SEBASTIÁN en producción** — Múltiples fixes aplicados (scanner, orden F→M, genero contextual ampliado). Generar minuta real con SEBASTIÁN y DANIELA, revisar logs Railway para confirmar que SEBASTIÁN no recibe reemplazos incorrectos
2. **[CRÍTICO] Verificar concordancia con Claude** — Concordancia ahora usa Claude en lugar de GPT-4o-mini para artículos; confirmar que el modelo está configurado correctamente en Railway (ANTHROPIC_API_KEY) y que los reemplazos de artículos funcionan
3. **[MEDIA] Guiones dobles `-- -` sin resolver del todo** — _normalizar_guiones tuvo múltiples iteraciones; confirmar con documento real que los guiones dobles quedan bien
4. **[MEDIA] Concordancia de artículos EL→LA, DEL→DE LA** — Verificar que el refactor a Claude (solo artículos de rol) produce resultados correctos
5. **[BAJA] Alembic out-of-sync** — `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';` en Supabase producción (pendiente desde sesiones anteriores)
6. **[BAJA] debug prints en router.py y reemplazador.py** — Hay prints de debug (`GENERO DEBUG`) que deben removerse antes de demo

**Estado al cierre:**
- Backend: Railway operativo — commit `afab702` activo
- Frontend: Vercel operativo — easypronotarial.com, último deploy con null-checks
- BD producción: operativa, alembic_version desincronizada (pendiente)
- Git: `nueva-minuta-workspace.tsx` y `navigation.ts` modificados localmente — se commitean en este cierre

---
## Sesión 2026-05-23

**Objetivo de la sesión:** Corregir bugs de género (SEBASTIÁN y concordancia global) y agregar lógica de auto-cascada de nacionalidad/estado civil en el formulario frontend.

**Realizado:**
- **router.py — reemplazos de género deterministas (ee93a7e):** Agregar `_GENERO_M_A_F` y `_GENERO_F_A_M` con `varón/mujer`, `soltero/a`, `colombiano/a`, `domiciliado/a`, `identificado/a` — todos con `palabra_completa: True`
- **reemplazador.py — aplicar_reemplazos_por_contexto (d266d6f):** Nueva función que aplica reemplazos de género solo en párrafos que contienen el nombre de la persona específica
- **reemplazador.py — aplicar_genero_contextual_docx (d266d6f):** Nueva función que orquesta los pares persona→reemplazos con exclusión mutua entre personas del documento
- **router.py — integrar género contextual (d266d6f):** Paso 5 del endpoint `/generar` llama `aplicar_genero_contextual_docx` pasando `pares_genero` y `todos_nombres_doc`
- **reemplazador.py + router.py — colombiano/a (a101c26):** Agregar entradas `colombiano→colombiana` y `colombiana→colombiano` a los bloques M→F y F→M
- **router.py — fix exclusión SEBASTIÁN (610a817):** `todos_nombres_doc` ahora combina `datos_ant.personas + datos_nv.personas` con set para deduplicar — así personas que no cambiaron (como SEBASTIÁN) están en `nombres_excluir`
- **reemplazador.py — _normalizar_guiones:** Nueva función que colapsa guiones dobles (`--` → `-`, `- --` → `- -`) y espacios dobles; se llama en `aplicar_reemplazos_docx` antes de `doc.save`
- **nueva-minuta-workspace.tsx — handleChange con cascada de género:** `PersonaCard` ahora tiene `handleChange` que al cambiar género auto-actualiza `nacionalidad` (via diccionario `GENTILICIOS_M_A_F`/`GENTILICIOS_F_A_M` de 25 gentilicios) y `estado_civil` (soltero/casado/divorciado/viudo ↔ femeninos)

**Archivos creados/modificados:**
- `backend/app/modules/minuta/router.py` — género determinista, pares_genero, todos_nombres_doc combinado
- `backend/app/services/minuta/reemplazador.py` — `aplicar_reemplazos_por_contexto`, `aplicar_genero_contextual_docx`, `_normalizar_guiones`
- `frontend/components/minutas/nueva-minuta-workspace.tsx` — `GENTILICIOS_M_A_F`, `GENTILICIOS_F_A_M`, `handleChange` con cascada

**Pendientes para la próxima sesión:**
1. **[CRÍTICO] Debug SEBASTIÁN persiste:** El fix `610a817` está en producción pero el bug puede seguir. Agregar prints de debug en `aplicar_genero_contextual_docx` (imprimir `todos_nombres`, `otros`, y qué párrafos se procesan), hacer deploy, generar minuta real, revisar logs Railway
2. **[MEDIA] Guiones dobles `-- -` sin resolver:** `_normalizar_guiones` existe pero no resuelve porque los guiones están partidos entre múltiples runs. Corregir para que una el texto de todos los runs del párrafo antes de aplicar regex, o implementar solución EasyPro1 (tab stops + `[[--]]` → `\t` en plantillas)
3. **[MEDIA] Concordancia de artículos** — EL→LA, DEL→DE LA (pendiente de sesión anterior)
4. **[BAJA] Alembic out-of-sync** — `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';` en Supabase producción
5. **[BAJA] Grabar videos demo** — si SEBASTIÁN y guiones quedan resueltos, preparar caso demo para notarías

**Estado al cierre:**
- Backend: Railway operativo — commit `610a817` activo (3a59eb6 es force redeploy vacío)
- Frontend: Vercel operativo — easypronotarial.com, deploy esta noche
- BD producción: operativa, alembic_version desincronizada (pendiente)
- Git: `reemplazador.py` y `nueva-minuta-workspace.tsx` modificados localmente sin commitear — se commitean en este cierre

---
## Sesión 2026-05-22

**Objetivo de la sesión:** Conectar el motor de minutas con OnlyOffice (abrir el .docx generado directamente en el editor) e integrar concordancia de género al flujo de generación.

**Realizado:**
- Análisis completo del flujo existente de minutas (detector, reemplazador, concordancia, router, frontend) y del flujo de OnlyOffice en document_flow
- Backend router.py minuta: POST /generar ahora integra concordancia de género por persona (detecta cambio M↔F, aplica reemplazos con palabra_completa=True), sube el .docx resultante a Supabase Storage en `minutas/notary_{id}/{uuid}_minuta.docx`, genera JWT firmado con storage_path y retorna JSON con `onlyoffice_path`
- Backend router.py minuta: 3 nuevos endpoints para servir el archivo al Document Server — GET /onlyoffice-config, GET /onlyoffice/file, POST /onlyoffice/callback (guarda versión editada de vuelta en Supabase)
- concordancia.py: fix menor — `aplicar_cambios_concordancia_a_reemplazos` ahora incluye `"palabra_completa": True` para respetar límites de palabra
- frontend/lib/minuta.ts: `generateMinuta` retorna `{ onlyoffice_path, filename }` en lugar de Blob; nueva función `getMinutaOnlyOfficeConfig(token)`; `sanitizeDatos()` limpia `\r\n\t\0` de strings antes de JSON.stringify (fix JSON malformado)
- frontend/components/minutas/nueva-minuta-workspace.tsx: `PersonaField` extraído a nivel de módulo (fix bug foco perdido por componente anidado que se desmontaba en cada render); paso 3 navega con `router.push(onlyoffice_path)` en lugar de descargar blob
- frontend/app/(app)/dashboard/minutas/editor/[token]/page.tsx: nueva página editor OnlyOffice para minutas — recibe JWT en URL, carga config desde `/api/v1/minuta/onlyoffice-config`, inicializa `DocEditor`
- frontend/lib/navigation.ts: entrada "Motor de Minutas" agregada al sidebar después de "Crear Minuta"
- frontend/next.config.mjs: `generateBuildId` con timestamp para forzar cache bust en Vercel
- Diagnóstico de problema en Vercel deploy: Root Directory mal configurado — path duplicado `frontend/easypro2/frontend`. URL settings: https://vercel.com/cesar-giraldo-aristizabals-projects/easypro-notarial-2/settings

**Archivos creados/modificados:**
- `backend/app/modules/minuta/router.py` — generar con concordancia + Supabase + JWT + 3 endpoints OnlyOffice
- `backend/app/services/minuta/concordancia.py` — `palabra_completa: True` en reemplazos de concordancia
- `frontend/app/(app)/dashboard/minutas/editor/[token]/page.tsx` — nueva página editor OnlyOffice para minutas
- `frontend/lib/minuta.ts` — generateMinuta retorna JSON, sanitizeDatos, getMinutaOnlyOfficeConfig
- `frontend/components/minutas/nueva-minuta-workspace.tsx` — PersonaField a nivel módulo, paso 3 navega al editor
- `frontend/lib/navigation.ts` — entrada Motor de Minutas en sidebar
- `frontend/next.config.mjs` — generateBuildId para cache bust

**Pendientes para la próxima sesión:**
1. **[CRÍTICO] Concordancia de artículos** — El motor cambia sustantivos (COMPRADOR→COMPRADORA) pero NO cambia artículos ni pronombres (EL→LA, LOS→LAS). Ajustar PROMPT_CONCORDANCIA en `concordancia.py`.
2. **[CRÍTICO] Fórmulas compuestas** — Expresiones como "EL(LOS) DEUDORA(ES)" quedan mal al cambiar género. El prompt debe manejar estas fórmulas mixtas.
3. **[CRÍTICO] Alembic out-of-sync** — Ejecutar en Supabase: `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';`
4. **[MEDIA] Verificar menú lateral por rol** — "Motor de Minutas" está en navigation.ts, confirmar que aparece correctamente según permisos del usuario
5. **[MEDIA] Personas incompletas en análisis B2** — Algunos docs devuelven menos personas de las esperadas. Revisar chunking o prompt del detector
6. **[MEDIA] Caso B1 (plantilla en blanco)** — El detector clasifica B1 pero el formulario dinámico es el mismo que B2. Pendiente diferenciar UX y prompt
7. **[BAJA] Reset contraseña** — No implementado
8. **[BAJA] Historial de minutas** — Guardar minutas generadas por notaría (estructura BD + UI)

**Estado al cierre:**
- Backend: Railway operativo — https://easypronotarial-2-production.up.railway.app
- Frontend: Vercel operativo — https://easypronotarial.com (deploy vía CLI `vercel --cwd frontend --prod`)
- BD producción: operativa, alembic_version desincronizada (pendiente UPDATE manual)
- Git: árbol limpio (solo uvicorn_start.log sin trackear)

**Deploy frontend (procedimiento correcto):**
```bash
cd c:\EasyProNotarial-2\easypro2
$env:NODE_OPTIONS="--use-system-ca"
vercel --cwd frontend --prod
```

---
## Sesión 2026-05-21

**Objetivo de la sesión:** Integrar motor de análisis de minutas IA al backend y crear pantalla frontend de 3 pasos para subir, analizar y generar minutas.

**Realizado:**
- Documentación inicial: SESSION.md operativo, AGENTS.md, protocolo iniciar-sesion y cerrar-sesion en .claude/commands/
- Verificación Supabase producción: alembic_version en 20260420, act_catalog ✅ 11 registros, legal_entities ✅ 6 registros, columnas document_type/document_number ✅ aplicadas (fuera de alembic_version)
- Backend motor minutas: detector.py (GPT-4o-mini, modo B1/B2 automático), reemplazador.py (reemplazos preservando formato .docx), concordancia.py (concordancia de género con IA), utils_letras.py (números a letras notarial)
- Backend endpoints: POST /api/v1/minuta/analizar + POST /api/v1/minuta/generar registrados en api_router. Instalado num2words y python-multipart
- Fix SSL local: OPENAI_DISABLE_SSL_VERIFY=true en .env + _make_openai_client() en detector.py y concordancia.py
- Prueba real con jaggua_limpio.docx: B2 detectado, 4 personas, 2 valores, inmueble Caldas/Antioquia, 8 actos, $0.0052 USD, 30 segundos respuesta
- Frontend lib/minuta.ts: tipos TypeScript + analyzeMinuta() + generateMinuta() usando getToken()
- Frontend components/minutas/nueva-minuta-workspace.tsx: wizard 3 pasos (subir+analizar, revisar personas con campos pendientes en amarillo, generar+descargar)
- Frontend app/(app)/dashboard/minutas/nueva/page.tsx: ruta nueva en Next.js 15
- tailwind.config.ts: aliases semánticos para CSS vars faltantes (muted, soft, panel-soft, panel-highlight, line-strong, etc.)
- Alembic desincronizado corregido: columnas 20260512 y 20260513 están en Supabase pero alembic_version no las registra. Pendiente UPDATE alembic_version.
- Comandos de sesión: iniciar-sesion.md y cerrar-sesion.md en easypro2/.claude/commands/ (para el repo) y C:\EasyProNotarial-2\.claude\commands\ (para Claude Code)

**Archivos creados/modificados:**
- `backend/app/services/minuta/detector.py` — motor B1/B2 con GPT-4o-mini
- `backend/app/services/minuta/reemplazador.py` — reemplazos en .docx preservando formato
- `backend/app/services/minuta/concordancia.py` — concordancia de género con IA
- `backend/app/services/minuta/utils_letras.py` — números a letras formato notarial
- `backend/app/modules/minuta/router.py` — 2 endpoints FastAPI
- `backend/app/api/router.py` — registra minuta_router
- `backend/requirements.txt` — +num2words +python-multipart
- `backend/.env` — +OPENAI_DISABLE_SSL_VERIFY=true (solo desarrollo local, no commitear)
- `frontend/lib/minuta.ts` — tipos + funciones API multipart
- `frontend/components/minutas/nueva-minuta-workspace.tsx` — wizard 3 pasos completo
- `frontend/app/(app)/dashboard/minutas/nueva/page.tsx` — ruta nueva
- `frontend/tailwind.config.ts` — aliases semánticos CSS vars
- `SESSION.md` — reescrito como documento operativo
- `AGENTS.md` — inventario de agentes del sistema
- `.claude/commands/iniciar-sesion.md` — protocolo arranque de sesión
- `.claude/commands/cerrar-sesion.md` — protocolo cierre de sesión

**Pendientes para la próxima sesión:**
1. **Alembic out-of-sync en producción** — Ejecutar `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';` en Supabase para sincronizar. Las migraciones YA están aplicadas pero alembic_version dice 20260420.
2. **Frontend minutas — integrar al menú lateral** — La ruta /dashboard/minutas/nueva existe pero no aparece en el sidebar de AppShell. Agregar entrada de navegación.
3. **Placeholders del dashboard** — /lotes, /ayuda, /configuracion muestran páginas vacías. Limpiar del menú o agregar contenido mínimo antes de demo.
4. **Personas incompletas en análisis** — jaggua_limpio.docx devolvió 4 personas cuando debería tener más (compradores, banco, etc.). Investigar si es problema de contexto de GPT-4o-mini (110k chars) o del prompt.
5. **Reset de contraseña** — No existe. Usuarios no pueden cambiar su contraseña.

**Estado al cierre:**
- Backend: operativo local en puerto 8001, apuntando a Supabase producción
- Frontend: build ✅, dev server corriendo en 5179
- BD producción: operativa, legal_entities y act_catalog con datos, alembic_version desincronizada
- Git: árbol limpio (solo uvicorn_start.log sin trackear, no debe commitearse)

---

## Stack confirmado

| Capa | Tecnología |
|---|---|
| Backend | FastAPI 0.115 + SQLAlchemy 2.0 + Alembic + Uvicorn |
| Base de datos prod | PostgreSQL vía Supabase (egwdrdgtgmogcahhdtdy.supabase.co) |
| Base de datos local | SQLite (easypro2.db) |
| Frontend | Next.js 15.3 + React 19 + TypeScript + Tailwind CSS 3 |
| IA documental | OpenAI GPT-4o (Gari — generación .docx escrituras) |
| IA minutas | OpenAI GPT-4o-mini (detector B1/B2 + concordancia) |
| Storage | Supabase Storage (cases/case-{id}/draft/) |
| Despliegue frontend | Vercel — https://easypronotarial.com |
| Despliegue backend | Railway — https://easypronotarial-2-production.up.railway.app |
| Editor documentos | OnlyOffice — https://onlyoffice.easypronotarial.com |

---

## URLs de producción / servicios

| Servicio | URL |
|---|---|
| Frontend producción | https://easypronotarial.com |
| Backend producción | https://easypronotarial-2-production.up.railway.app |
| Supabase BD | https://egwdrdgtgmogcahhdtdy.supabase.co |
| OnlyOffice | https://onlyoffice.easypronotarial.com |
| Backend local | http://127.0.0.1:8001 |
| Frontend local | http://127.0.0.1:5179 |

---

## Estado git

Repositorio en `c:\EasyProNotarial-2\easypro2\` — rama `main`.
Remoto: https://github.com/cesargiraldoa/EasyProNotarial-2.git

---

## Migraciones Alembic — estado real en Supabase

| Migración | Schema real | alembic_version |
|---|---|---|
| base | ✅ aplicada | parte del head |
| 20260418_add_role_permissions_table | ✅ tabla existe | parte del head |
| 20260419_add_legal_entities | ✅ tabla existe, 6 registros | parte del head |
| 20260420_add_act_catalog | ✅ 11 registros | ✅ HEAD registrado |
| 20260512_add_user_identification | ✅ columnas existen en users | ❌ no registrada |
| 20260513_promote_legacy_notary_to_titular | desconocido (data migration) | ❌ no registrada |

**ACCIÓN PENDIENTE:** Ejecutar en Supabase:
```sql
UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';
```

---

## Lo que existe y funciona hoy

### Backend — endpoints operativos (79 rutas totales)

| Módulo | Rutas | Estado |
|---|---|---|
| Auth | POST /login, GET /me | ✅ |
| Notarías | GET /notaries, GET /notaries/{id} | ✅ |
| Usuarios | CRUD + roles + permisos | ✅ |
| Plantillas | GET/PUT templates, 8 plantillas activas | ✅ |
| Personas naturales | GET/POST /persons + lookup | ✅ |
| Entidades jurídicas | GET/POST /legal-entities + apoderados | ✅ |
| Flujo documental | Wizard 5 pasos + Gari .docx | ✅ |
| Dashboard | GET /dashboard KPIs | ✅ |
| Catálogo de actos | act_catalog | ✅ |
| **Motor minutas** | POST /api/v1/minuta/analizar | ✅ nuevo |
| **Motor minutas** | POST /api/v1/minuta/generar | ✅ nuevo |

### Frontend — rutas operativas

| Ruta | Estado |
|---|---|
| /login | ✅ |
| /dashboard | ✅ KPIs |
| /dashboard/casos | ✅ |
| /dashboard/casos/crear | ✅ Wizard 5 pasos |
| /dashboard/casos/[caseId] | ✅ |
| /dashboard/notarias | ✅ |
| /dashboard/comercial | ✅ CRM |
| /dashboard/usuarios | ✅ |
| /dashboard/roles | ✅ |
| /dashboard/perfil | ✅ |
| /dashboard/actos-plantillas | ✅ |
| /dashboard/system-status | ✅ |
| **/dashboard/minutas/nueva** | ✅ nuevo — wizard 3 pasos |
| /dashboard/lotes | ⚠️ placeholder vacío |
| /dashboard/ayuda | ⚠️ placeholder vacío |
| /dashboard/configuracion | ⚠️ placeholder vacío |

### Agente Gari (escrituras)
- Motor: GPT-4o, max_tokens=16000, temperature=0.2
- ACTOS_POR_VARIANTE hardcodeado en gari_service.py

### Motor Minutas (nuevo)
- Detector B1/B2: GPT-4o-mini, temperature=0.1, max_tokens=8000
- Concordancia: GPT-4o-mini, temperature=0.1, max_tokens=4000
- SSL local: OPENAI_DISABLE_SSL_VERIFY=true en .env (no commitear)

### Entidades jurídicas en Supabase (6 — seed aplicado)
Fiduciaria Bancolombia, Constructora Contex S.A.S. BIC, Bancolombia S.A.,
Banco Davivienda, Fondo Nacional del Ahorro, Banco de Bogotá

---

## Pendientes críticos

### Para próxima sesión
1. **Alembic out-of-sync** — UPDATE alembic_version en Supabase (ver arriba)
2. **Menú lateral** — Agregar /dashboard/minutas/nueva al sidebar de AppShell
3. **Placeholders dashboard** — /lotes, /ayuda, /configuracion vacíos — limpiar antes de demo
4. **Personas incompletas en análisis** — jaggua devolvió 4/~10 personas. Revisar chunking o prompt
5. **Reset contraseña** — No implementado

### Deuda técnica
6. ACTOS_POR_VARIANTE hardcodeado → mover a BD
7. Búsqueda entidades con q corta retorna todo (falta filtro mínimo de chars)
8. Módulo facturación electrónica → diseñado, cero código
9. Módulo nómina electrónica → diseñado, cero código
10. Provider Adapter (Plemsi) → pendiente cotización

---

## Comandos para levantar entorno local

```bash
# Backend
cd c:\EasyProNotarial-2\easypro2\backend
.venv\Scripts\activate
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload

# Frontend (terminal separada)
cd c:\EasyProNotarial-2\easypro2\frontend
npm run dev
# → http://127.0.0.1:5179

# Verificar migraciones Alembic (contra producción)
cd c:\EasyProNotarial-2\easypro2\backend
alembic current
alembic heads
```

**NOTA:** .env del backend apunta a Supabase (ENVIRONMENT=production).
Para desarrollo local con SQLite: cambiar DATABASE_URL a `sqlite:///./easypro2.db`.

---

## Reglas técnicas del proyecto

1. **Multinotaría estricto** — Toda consulta filtra por notary_id. Nunca exponer datos cruzados.
2. **Roles** — Validar con require_roles() / has_role(). Roles: super_admin, admin_notary, notary, approver, protocolist, client.
3. **Provider Adapter** — Facturación/nómina NUNCA directo a Plemsi. Siempre vía ElectronicDocumentProvider.
4. **Sin secretos en código** — Solo en .env (excluido de git).
5. **Intervinientes dinámicos** — N compradores + N entidades. template_required_roles es obsoleto.
6. **Snapshot JSON** — CaseParticipant guarda snapshot en momento de guardado.
7. **Alembic obligatorio** — Todo schema change vía migración YYYYMMDD_descripcion.py.
8. **CORS** — FlexibleCORSMiddleware. Agregar dominios en _load_allowed_origins().
9. **Gari** — No cambiar max_tokens ni temperature sin revisar calidad de escrituras.
10. **Supabase Storage** — Archivos en cases/case-{id}/draft/. No mover sin actualizar gari_service.py.
11. **SSL local** — OPENAI_DISABLE_SSL_VERIFY=true solo en .env local. NO en Railway.

---

## Módulos diseñados — pendientes de implementar

### Facturación Electrónica
- Decisión: proveedor intermediario (Plemsi evaluado como principal)
- Arquitectura: Provider Adapter desacoplado
- Estado: **Solo diseño. Cero código.**

### Nómina Electrónica
- Mismo enfoque que facturación
- Estado: **Solo diseño. Cero código.**
