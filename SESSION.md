# SESSION.md â€” EasyProNotarial-2

---
## Sesión 2026-07-23 — Rebranding "Minutas Asistidas" + arreglos UX de la escritura (resaltado en vivo, PDF, guiones, popup de norma)

**Objetivo de la sesión:** Revisión visual del port de "Escritura asistida" con datos reales y corregir los defectos de UX detectados por el usuario en el navegador, dejándolos verificados con tests.

**Rama de trabajo:** `claude/escritura-asistida-produccion-7oc57i` (11 commits, `26b10a6`..`5779155`). **NO** se mergeó a `main` (queda para PR/merge cuando el usuario lo apruebe).

**Realizado (cada punto = uno o más commits):**
- **Rebranding a "Minutas Asistidas"** (`26b10a6`): renombrado en menú lateral, landing, botones, título del workspace y CTA del detalle del caso. Recorte del menú para **superadmin**: se ocultan Biblioteca, Actos/Plantillas, Revisión Documental y Ayuda (siguen visibles para los demás roles notariales). Superadmin ve: Resumen · Comercial · Notarías · Usuarios · Roles · Minutas · Crear Minuta · Minutas Asistidas · System Status · Configuración · Mi Perfil.
- **3 comportamientos del prototipo HTML portados** (`99db5ca`): resaltado en vivo, popup de norma al hover (diccionario `NORMAS` 1:1 + tooltip flotante sobre badges `.cite` del preview y liquidación), y botón Imprimir/PDF en Captura.
- **Bug PDF pestaña en blanco** (`1ce5095`): `window.open(..., "noopener,noreferrer")` devolvía null; se quitaron esas flags (aplica a Captura y al Exportar PDF de Redacción).
- **Botón PDF en ambos modos + guiones de relleno** (`362b027`): botón Imprimir/PDF visible en Captura y Redacción; portado `fillLeaders()` (rayas `—` que rellenan el renglón hasta el margen para impedir intercalar texto), medido en vivo en el preview y al ancho A4 en la ventana de impresión.
- **Arranque local robusto** (`b54f1cb`): `npm run dev:next` ahora corre `scripts/dev.mjs` que **libera el puerto 5179** antes de arrancar (fin del `EADDRINUSE` que dejaba el navegador viendo código viejo). `outputFileTracingRoot` fijado en `next.config.mjs`. `dev:raw` conserva el arranque directo.
- **Resaltado: de "no funciona" a robusto y correcto** (`a1f178f`, `1f66c64`, `24279e8`, `fc6a9c9`, `32246f5`):
  - Amarillo aplicado con **estilos inline** (no depende del CSS).
  - **Causa raíz encontrada:** los ids de partes del form usan lado en MAYÚSCULA (`V-0-nombre`) pero el motor emite `data-f` en minúscula (`v0nombre`) → normalización case-insensitive.
  - Mapeo **exacto** id→data-f (`DATAF_ALIAS`, inmuebles single/multi, encadenamientos, divisas, rural, capacidad) para resaltar el **valor** en el cuerpo, no un párrafo equivocado.
  - **Resaltado por coincidencia de texto** (para firmas/testigos/contacto que sí van al cuerpo pero sin `data-f`). Subió de 44 → **67 campos** que resaltan su valor exacto.
  - Se quitó el "último recurso" que pintaba párrafos equivocados; el preview tiene su **propio scroll** (sticky + overflow).
- **Scroll centrado + color del cambio** (`5779155`): `scrollIntoView({block:"center"})` centra el cambio sin mover el form; el valor resaltado va en **azul fuerte + negrita** sobre el amarillo para que el protocolista vea qué cambia.
- **Diagnóstico confirmado (no eran bugs):** los selects SÍ cambian el texto (tipoDoc/estado/género/derecho/tipoNegocio) y los datos de firma SÍ se renderizan — el problema era solo de resaltado, ya resuelto.

**Archivos creados/modificados:**
- `frontend/lib/navigation.ts` — rebranding + recorte de menú superadmin
- `frontend/lib/authorization.ts` — (lectura; base de roles)
- `frontend/lib/escritura-normas.ts` — **nuevo**: diccionario `NORMAS` (37 normas, popups)
- `frontend/lib/escritura-print.ts` — **nuevo**: `printEscrituraHtml()` + guiones al ancho A4
- `frontend/components/escritura/escritura-preview-fx.ts` — **nuevo**: `applyHighlight` (data-f + texto + sección), `sectionForId`, `fillLeaders`, `useNormaTooltip`
- `frontend/components/escritura/escritura-preview.tsx` — reescrito: resaltado + scroll centrado + tooltips + guiones
- `frontend/components/escritura/escritura-preview.module.css` — estilos `.hl`/`.hl-sec`/`.fill`/tooltip
- `frontend/components/escritura/escritura-workspace.tsx` — captura de campo/valor editado, botón PDF ambos modos, preview con scroll propio
- `frontend/components/escritura/liquidacion-panel.tsx` — tooltips de norma
- `frontend/components/escritura/escritura-editor.tsx` — fix noopener del Exportar PDF
- `frontend/components/escritura/escritura-index.tsx`, `frontend/components/cases/case-detail-workspace.tsx` — rebranding
- `frontend/scripts/dev.mjs` — **nuevo**: arranque que libera el puerto
- `frontend/next.config.mjs`, `frontend/package.json` — `outputFileTracingRoot`, script `dev:next`/`dev:raw`
- `frontend/components/escritura/__tests__/escritura-highlight*.test.ts` — **nuevos**: 4 tests (integración, cobertura de 145 ids, barrido de 191 controles, correctitud del valor)

**Pendientes para la próxima sesión:**
1. **Decidir merge de la rama** `claude/escritura-asistida-produccion-7oc57i` → `main` (PR o fast-forward) cuando el usuario apruebe la revisión visual. NO se ha mergeado.
2. **Revisión visual a fondo** de los 3 actos con datos reales end-to-end (captura → generar → cumplimiento/liquidación → PDF), anotando ajustes de redacción/UX que falten.
3. **Casos de resaltado por sección** (los ~10 campos sin valor en el cuerpo: teléfono/correo en ciertas condiciones, `divisas-moneda` condicional, `apoyoActo`): validar que la sección resaltada sea la más natural; afinar mapeo si el notario lo pide.
4. Confirmar color/estilo del resaltado (azul actual) con el usuario; ajustable en `HL_TEXT` de `escritura-preview-fx.ts`.
5. **Pendientes del corpus jurídico** heredados: aplicar 2.ª verificación de GPT (7 normas), adjudicación del notario de conflictos de estado (`corpus-juridico/reporte-conflictos-gpt-2026-07-21.md`), extraer resto del corpus Notaría 16, afinar capa Gari.

**Estado al cierre:**
- Backend: sin cambios esta sesión (todo fue frontend). Operativo al arrancar.
- Frontend: **operativo** — `tsc --noEmit` sin errores, **173/173 tests**, `next build` limpio. Verificado por el usuario en el navegador (resaltado, PDF, guiones, popups funcionando).
- BD producción: sin migraciones nuevas.
- Git: rama `claude/escritura-asistida-produccion-7oc57i` pusheada (`5779155`), árbol limpio. **No mergeada a main.**

---
## Sesión 2026-07-22 — Port de "Escritura asistida" al software (front + back + BD) + salida en producción

**Objetivo de la sesión:** Llevar el prototipo HTML congelado `escritura-asistida.html` al software real (Next.js + FastAPI + BD), reutilizando la infraestructura existente y SIN reprocesar; construir la capa de corpus jurídico real (normas verificadas contra fuente oficial); y dejarlo **visible y funcionando** para el usuario, accesible desde el menú lateral.

### Modelo de trabajo usado
- **Codex escribe el código**, los prompts los co-diseñamos aquí, y yo (Claude) **reviso cada PR en GitHub y hago el merge**. El HTML congelado (`docs/ecosistema-notarial/prototipos/escritura-asistida.html`) es la ESPECIFICACIÓN — nunca se modifica; el motor TS se porta 1:1 y se valida con golden tests (equivalencia byte a byte).
- Los prompts para Codex quedaron guardados en `docs/ecosistema-notarial/prompts/` (WP-0 a WP-5 + Bloques A/B/C/D + briefs para GPT).

**Realizado (todo mergeado a `main`, commit final `fc02318` vía PR #142 — fast-forward, 55 commits):**

- **3.er acto — Cancelación de hipoteca** (commit `ebe1da8`): extraído del corpus real de la Notaría 16 (5 documentos de cancelación). Acto sin cuantía, inmueble liberado, banco/apoderado, firma fuera de sede. Sumado como 3.ª tarjeta en el lanzador.

- **WP-0 (ADR + plan)** (`4c26c61`, `43ba224`): decisiones de arquitectura y plan detallado del port (`plan-port-software.md`, `adr-escritura-asistida.md`).

- **WP-1 — Corpus jurídico: esquema + migración + seed + vigencia** (PR #133, `59fd981`): modelos SQLAlchemy `legal_norma`, `norma_relacion`, `clausula`, `regla`, `tarifa`, `jurisprudencia`. Vigencia temporal artículo por artículo, **doble estado** (vigencia_formal / aplicabilidad_operativa), regla "nunca borrar, versionar", filtro por **fecha de otorgamiento**. (Nota: el 1.er PR de Codex venía sobre un checkout STALE `easypro2/`; se corrigió re-basando en la rama con `backend/` en la RAÍZ.)

- **WP-2 — Motor determinístico en TypeScript + golden tests** (PR #134, `9e52677`): `frontend/lib/motor-escritura/index.ts` portado 1:1 del JS del HTML. Golden fixtures (compraventa, compraventa+hipoteca, cancelación) que garantizan equivalencia byte a byte con el HTML congelado. `generar(acto, state, corpus?)`.

- **WP-3 — API backend de escritura asistida** (PR #135, `2bdf55c`): `backend/app/modules/escritura/router.py`. Motor de reglas server-side (`escritura_reglas.py`): recalcula desde el corpus y devuelve **409 en BLOCK** (no confía en el cliente).

- **WP-4 — UI de Captura** (PR #136, `bd8bf38`): componentes `frontend/components/escritura/` (workspace, form, preview + `.module.css`, panel de cumplimiento, panel de liquidación).

- **WP-5 — Editor propio (modo Redacción)** (PR #137, `1c573d2`): editor tipo HTML (NO OnlyOffice — decisión del usuario: "creamos nuestro editor como el HTML").

- **Bloque A — Corpus vivo + RAG + gobernanza** (PR #138, `473b1cc`): `legal_rag.py`, `legal_gobernanza.py`, `legal_corpus.py`. Citas desde corpus/RAG, no inventadas por el modelo.

- **Bloque B — Gari (capa IA)** (PR #139, `5483e02`): `escritura_gari.py`. Principio de frontera: **Gari sugiere + humano valida**; el motor determinístico manda; el notario decide.

- **Bloque C — Compraventa de todo tipo, lote 1** (PR #140, `1b96f3c`): varios inmuebles (matrícula/linderos por inmueble), estado del folio (segregado → Ley 1579/2012; falsa tradición → Ley 1561/2012), encadenamientos en orden canónico (cancelación hipoteca previa → cancelación patrimonio familia → afectación vivienda familiar).

- **Bloque D — Compraventa de todo tipo, lote 2** (PR #141, `c596a9a`): extranjería/divisas (Banco de la República, Circular DCIN, canalización mercado cambiario, registro inversión extranjera), predio rural/UAF/baldíos (arts. 39 y 72 Ley 160/1994, autorización ANT, derecho de preferencia), capacidad/representación/apoyos (venta de bien de menor, discapacidad con apoyos — redacción incluyente, nunca "incapaz").

- **Entrada de UI** (`ffa1b73`, `194eaaf`): botón "✒ Escritura asistida" en el detalle del caso (`/dashboard/casos/[caseId]/escritura`) + ítem **"Escritura asistida"** en el menú lateral (`/dashboard/escritura`, landing que lista los casos reales).

- **Merge a producción** (PR #142, `fc02318`): la rama `claude/notaria16-escritura-asistida-fsro6n` se mergeó a `main` (fast-forward limpio). **Verificado corriendo en el navegador del usuario**: menú → landing de casos → workspace con las 3 tarjetas de acto. `npx next build` pasa limpio con las rutas `/dashboard/escritura` y `/dashboard/casos/[caseId]/escritura`.

### Lo que hizo GPT (verificación normativa — corpus capa 3)
- **1.ª verificación (67 normas)** — aplicada en commit `99156fa`. GPT cotejó las 67 normas contra **fuente oficial** (Gestor Normativo de Función Pública, compilaciones oficiales) y entregó: **URL oficial, texto del artículo, vigencia y nivel de confianza** por norma. Se aplicaron esos 4 campos al corpus.
  - **Importante:** NO se pisó el campo `estado` para no importar una clasificación dudosa ni alterar la aplicabilidad operativa del motor. Las **discrepancias de estado** (nuestro → GPT) quedaron listadas en `corpus-juridico/reporte-conflictos-gpt-2026-07-21.md` para **decisión del notario**. Ejemplos: Dcto-ley 960/1970 arts. 13/14/38/39 (nosotros "modificada" → GPT "vigente"); Dcto 1069/2015 y Ley 1579/2012 (nosotros "vigente" → GPT "modificada"); C.C. art. 1521 ord. 4 → "derogada_parcial"; C.C. art. 1931 → "derogada_total" (derogado por Ley 45/1930).
- **Correcciones de fuentes previas** aplicadas antes (verificación C1–C5, `verificacion-fuentes-2026-07-21.md`): registro → Ley 223/1995 art. 231; art. 12 Dcto 2148/1983 → art. 2.2.6.1.2.1.5 Dcto 1069/2015; retención personas jurídicas art. 401; exención 5000 UVT; Dcto 0732 modifica 1069.
- **2.ª verificación (7 normas nuevas de baja)** — brief entregado a GPT en `docs/ecosistema-notarial/prompts/tarea-gpt-normas-nuevas-2.md`. **PENDIENTE:** GPT aún no ha devuelto el JSON; falta aplicarlo al corpus.

### Estado del corpus jurídico (`corpus-juridico/*.json`) al cierre
- `normas.json` → **74** registros
- `reglas.json` → **40**
- `clausulas.json` → **55**
- `tarifas.json` → **13**
- `jurisprudencia.json` → **5**
- `norma_relaciones.json` → **6**

**Archivos creados/modificados (principales):**
- `frontend/lib/motor-escritura/index.ts` — motor determinístico TS (port 1:1 del HTML)
- `frontend/lib/motor-escritura/__fixtures__/{compraventa,hipoteca,cancelacion}.json` + `README.md` — golden fixtures
- `frontend/lib/motor-escritura/__tests__/{golden,unit,ramas-compraventa}.test.ts` — tests (motor + ramas todo-tipo)
- `frontend/components/escritura/{escritura-workspace,escritura-form,escritura-preview(+.module.css),escritura-editor,cumplimiento-panel,liquidacion-panel,escritura-index}.tsx` — UI completa
- `frontend/app/(app)/dashboard/escritura/page.tsx` — landing de casos
- `frontend/lib/navigation.ts` — ítem "Escritura asistida" en el menú lateral (línea 36)
- `frontend/components/cases/case-detail-workspace.tsx` — botón "✒ Escritura asistida" en el detalle del caso
- `backend/app/modules/escritura/router.py` — API de escritura
- `backend/app/services/{escritura_reglas,escritura_gari,legal_rag,legal_gobernanza,legal_corpus}.py` — reglas server-side, Gari, RAG, gobernanza, corpus
- `backend/app/models/legal_*.py` — modelos del corpus jurídico
- `corpus-juridico/*.json` — corpus (normas/reglas/cláusulas/tarifas/jurisprudencia/relaciones)
- `corpus-juridico/reporte-conflictos-gpt-2026-07-21.md` — conflictos de estado para el notario
- `docs/ecosistema-notarial/prompts/*.md` — prompts Codex (WP-0..5, Bloques A/B/C/D) + briefs GPT
- `docs/ecosistema-notarial/{plan-port-software,adr-escritura-asistida}.md` — plan y decisiones
- `docs/ecosistema-notarial/corpus-notaria16/capa-notaria16-cancelacion-hipoteca.md` — corpus del 3.er acto
- `docs/ecosistema-notarial/corpus-juridico/verificacion-fuentes-2026-07-21.md` — correcciones C1–C5

### Cómo queda funcionando (para retomar mañana)
- **Repo real del usuario (Windows):** `C:\EasyProNotarial-2\easypro2` (ahí viven `.git` y `frontend/`). OJO: `C:\EasyProNotarial-2` NO es el repo, es la carpeta contenedora.
- **Arranque limpio que SÍ funcionó** (evita el script PowerShell `dev` que se trababa por PATH):
  ```powershell
  cd C:\EasyProNotarial-2\easypro2
  git fetch origin
  git checkout main
  git reset --hard origin/main   # garantiza el commit fc02318
  cd frontend
  npm run dev:next               # = next dev -H 127.0.0.1 -p 5179 (directo, sin el .ps1)
  ```
  Luego `http://127.0.0.1:5179` + **Ctrl+Shift+R**. Login `superadmin@easypro.co` / `ChangeMe123!`.
- **Ruta en la app:** menú lateral → "Escritura asistida" → elegir caso → workspace con 3 actos (Compraventa · Compraventa+Hipoteca · Cancelación de hipoteca) → captura determinística + redacción manual + Generar documento.
- El **ítem del menú NO depende del backend** (se renderiza desde `navigation.ts`); la **lista de casos** de la landing sí consume la API (`getCases`).

**Pendientes para la próxima sesión:**
1. **Aplicar la 2.ª verificación de GPT** (7 normas de baja): entregar/recibir el JSON de `docs/ecosistema-notarial/prompts/tarea-gpt-normas-nuevas-2.md` y aplicarlo al corpus.
2. **Adjudicación del notario** de las discrepancias de `estado` en `corpus-juridico/reporte-conflictos-gpt-2026-07-21.md` (Dcto-ley 960/1970, Dcto 1069/2015, Ley 1579/2012, C.C. arts. 1521 y 1931, etc.).
3. **Revisión visual a fondo** de los 3 actos con datos reales (recorrer captura → generar → cumplimiento/liquidación) y anotar ajustes de redacción/UX. Requiere backend + BD corriendo para cargar casos.
4. **Extraer los documentos restantes** del corpus de la Notaría 16 (capa por-notaría de los demás actos) y seguir poblando el corpus.
5. Conectar/afinar la **capa Gari (IA)** sobre la escritura una vez el corpus esté validado por el notario.

**Estado al cierre:**
- Backend: código en `main` (módulo escritura + servicios legales). Operativo al arrancar; no se dejó corriendo en esta sesión.
- Frontend: **operativo y verificado en el navegador del usuario** (menú + landing + workspace con los 3 actos). `next build` limpio.
- BD producción: sin migraciones nuevas aplicadas a producción esta sesión (el corpus vive en JSON + seed; verificación de GPT pendiente de 2.ª tanda).
- Git: rama `claude/notaria16-escritura-asistida-fsro6n` **mergeada a `main`** (PR #142, `fc02318`). Árbol limpio.

---
## Sesión 2026-07-20 — Ecosistema Notarial: "Escritura asistida"

**Objetivo de la sesión:** Retomar el ecosistema notarial (contexto del doc `Ecosistema_notarial_19jul26`), analizar el corpus real de la Notaría 16, y evolucionar los prototipos hacia UNA sola herramienta lista para grabar demo.

**Realizado:**
- **Corpus Notaría 16 analizado:** inventario de 40 docs (5 protocolistas) + extracción y análisis de los 13 de compraventa/compraventa+hipoteca → biblioteca de cláusulas, orden canónico, notas 1–8, ficha de firma, clasificación en dos capas (por-ley vs estilo) y estándar único. Docs en `docs/ecosistema-notarial/corpus-notaria16/`.
- **Arreglos del wizard de compraventa:** concordancia de género con **4 categorías legales** (Dcto 0732/2026 · Sent. T-033/2022: F/M/No Binario/Transgénero) y guiones de relleno hasta el margen.
- **Acto 2 — Hipoteca:** encadenamiento compraventa+hipoteca completo (12 cláusulas + comparecencia del acreedor + ratificación Ley 258).
- **Prototipo principal nuevo `escritura-asistida.html`** (unifica wizard+editor en una vista): pantalla de arranque "elige el acto → carga plantilla" (Compraventa · Compraventa+Hipoteca), captura en vivo ↔ redacción a mano, biblioteca de la 16, comentarios estilo Word, resaltado multicolor, control de cambios, dictado por voz, exportar **PDF y Word**, miles/centavos, liquidación integrada al cuerpo, edición inmediata (sync posicional), 5 tipos de derecho. Todo verificado en navegador (Playwright).
- **Política registrada:** "demo = real" (la escritura contiene todos los elementos, no un resumen).

**Archivos creados/modificados:**
- `docs/ecosistema-notarial/prototipos/escritura-asistida.html` — **prototipo principal** (nuevo)
- `docs/ecosistema-notarial/prototipos/wizard-compraventa.html` — género 4-cat, guiones, acto 2, handoff
- `docs/ecosistema-notarial/prototipos/editor-vinculado.html` — recepción del handoff
- `docs/ecosistema-notarial/prototipos/demo-ecosistema-notarial.html` + `_build-demo.py` — demo combinada (nuevo)
- `docs/ecosistema-notarial/corpus-notaria16/inventario.md` + `capa-notaria16-compraventa.md` — análisis del corpus (nuevo)
- `docs/ecosistema-notarial/normograma-compraventa.md` — Dcto 0732/2026 (género)
- `docs/ecosistema-notarial/estado-y-proximos-pasos.md` — punto de retomar actualizado

**Pendientes para la próxima sesión:**
1. **3.er acto** (elegir: hipoteca sola / cancelación de hipoteca / cancelación de patrimonio de familia) → extraer su corpus y sumar tarjeta al lanzador de `escritura-asistida.html`.
2. **Extraer los 27 documentos restantes** del corpus de la Notaría 16 (capa por-notaría de los demás actos).
3. **Captura por extracción** (linderos desde escritura registrada → prellenado con "por validar"; luego cédula PDF417 y voz).
4. Exportar 100% robusto y probar la demo desde el `.html` local (dentro del Artifact el sandbox bloquea popups/descargas/micrófono).

**Estado al cierre:**
- Backend: sin cambios esta sesión (trabajo en prototipos HTML del ecosistema).
- Frontend: sin cambios esta sesión.
- BD producción: sin cambios.
- Git: árbol limpio; todo en la rama `claude/previous-work-context-pz5704` (pusheado). Artifact principal: https://claude.ai/code/artifact/b33c60bd-ae04-412f-95d4-29d01ffed0aa

---
## SesiÃ³n 2026-05-28 (sesiÃ³n 3)

**Objetivo de la sesiÃ³n:** Resolver 2 bugs reportados: (1) no se detecta ADQUISICIÃ“N, (2) no se detecta/muestra INDAGACIÃ“N SOBRE AFECTACIÃ“N A VIVIENDA FAMILIAR.

**Realizado:**
- **Bug 2 â€” Decisiones (vivienda familiar):** Implementadas 2 capas faltantes: `DecisionesCard` en frontend con 3 toggles SÃ­/No/? y bloque `# DECISIONES` en `construir_lista_reemplazos()`. âœ…
- **Bug 1 â€” AdquisiciÃ³n:** Implementadas 5 capas desde cero: secciÃ³n ADQUISICION PREVIA en PROMPT_B2 del detector, `MinutaAdquisicion` en `minuta.ts`, bloque `# ADQUISICION` en reemplazador, `AdquisicionCard` en frontend, payload verificado en `/generar`. âœ…
- **Bug A â€” NOâ†’SÃ destruÃ­a texto legal:** Eliminado bloque `# DECISIONES` del reemplazador â€” las decisiones son booleanos para UI, no variables de plantilla. âœ…
- **Bug B â€” Notariaâ†’SÃ­taria:** Resuelto al eliminar el bloque DECISIONES que reemplazaba NOâ†’SÃ sin `palabra_completa=True`. âœ…
- **Bug C â€” 854 contaminaba ley 854 y parÃ¡grafo PH:** Guard `len(str(valor)) > 4` en `escritura_numero_adquisicion` â€” el valor "854" (3 chars) no pasa el guard. âœ…
- **forma_adquisicion contaminaba pÃ¡rrafos legales:** Eliminado del reemplazador â€” campo informativo, no variable de plantilla. âœ…
- **VerificaciÃ³n con diff exacto:** 4 generados analizados con diff entre plantilla y generado. Ãšltimo diff limpio â€” solo cambios esperados (valores en letras, vendedor original en clÃ¡usula ADQUISICIÃ“N). âœ…

**Archivos creados/modificados:**
- `backend/app/services/minuta/detector.py` â€” secciÃ³n ADQUISICION PREVIA en PROMPT_B2
- `backend/app/services/minuta/reemplazador.py` â€” bloque ADQUISICION con guards, bloque DECISIONES eliminado, `forma_adquisicion` eliminada
- `backend/app/modules/minuta/router.py` â€” sin cambios
- `frontend/lib/minuta.ts` â€” tipo `MinutaAdquisicion`, campo `adquisicion?` en `MinutaDatos`
- `frontend/components/minutas/nueva-minuta-workspace.tsx` â€” `AdquisicionCard`, `DecisionesCard`, estados, payload

**Pendientes para la prÃ³xima sesiÃ³n:**
1. **[CRÃTICO] Remover console.log debug** â€” `console.log("TOUR VISIBLE:", tourVisible)` en `nueva-minuta-workspace.tsx`
2. **[CRÃTICO] Fix gap 1 â€” agregar `actividad_economica` a PersonaCard**
3. **[CRÃTICO] Fix gap 2 â€” agregar `domicilio` y `estado_civil` a `construir_lista_reemplazos()`**
4. **[CRÃTICO] Fix gap 4 â€” concordancia cuando solo cambia gÃ©nero** en `concordancia.py`
5. **[MEDIA] Verificar tour en producciÃ³n** â€” click en upload no debe cerrar el tour
6. **[MEDIA] Remover prints `[GENERO DEBUG]`** de `reemplazador.py`
7. **[BAJA] Alembic out-of-sync** â€” `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';`

**Estado al cierre:**
- Backend: Railway desplegado â€” fixes reemplazador y detector activos
- Frontend: Vercel desplegado â€” `AdquisicionCard` y `DecisionesCard` activos
- BD producciÃ³n: operativa, alembic_version desincronizada (pendiente)
- Git: Ã¡rbol limpio

---
## SesiÃ³n 2026-05-28 (sesiÃ³n 2)

**Objetivo de la sesiÃ³n:** Implementar campo ADQUISICIÃ“N en las 5 capas del motor de minutas y corregir 3 bugs crÃ­ticos de reemplazo en `reemplazador.py`.

**Realizado:**
- **ADQUISICIÃ“N â€” Capa 1 (detector.py):** SecciÃ³n `5. ADQUISICION PREVIA` insertada en PROMPT_B2 entre INMUEBLE y NOTARIA (secciones 6-9 renumeradas). 6 campos: `forma_adquisicion`, `escritura_numero`, `fecha_escritura_anterior`, `notaria_anterior`, `municipio_notaria_anterior`, `vendedor_original`. InstrucciÃ³n explÃ­cita de devolver `null` si no hay antecedente de adquisiciÃ³n. Ejemplo JSON actualizado con caso real.
- **ADQUISICIÃ“N â€” Capa 2 (minuta.ts):** Tipo `MinutaAdquisicion` exportado con 6 campos `string | null`. Campo `adquisicion?: MinutaAdquisicion | null` agregado a `MinutaDatos`.
- **ADQUISICIÃ“N â€” Capa 3 (reemplazador.py):** Bloque `# ADQUISICION` en `construir_lista_reemplazos()` con 6 campos, guard `{} or {}`, etiquetas sufijadas `_adquisicion`, `palabra_completa=True` en todos.
- **ADQUISICIÃ“N â€” Capa 4 (nueva-minuta-workspace.tsx):** `AdquisicionCard` con 6 `SectionField` en grid 2 columnas. Estado `adquisicionEdit` (EMPTY_ADQUISICION), inicializado desde `result.datos.adquisicion` en `handleAnalizar`, reseteado en `clearFile`, handler `updateAdquisicion`. Card insertada en Paso 2 entre InmuebleCard y NotariaCard.
- **ADQUISICIÃ“N â€” Capa 5 (payload verificado):** `adquisicion: adquisicionEdit` explÃ­cito en `datosNuevos` en `handleGenerar` (sobreescribe el spread de `analisisResult.datos`).
- **BUG A+B â€” Decisiones destruyen texto legal (fix):** `"NO" â†’ "SÃ"` sin lÃ­mites de palabra corrompÃ­a "Notaria" â†’ "SÃ­taria", "conocimiento" â†’ "cosÃ­cimiento", e invertÃ­a "NO ESTÃ AFECTADO" â†’ "SÃ ESTÃ AFECTADO". Fix: `agregar_reemplazo()` extendida con parÃ¡metro `palabra_completa: bool = False` propagado al dict. Bloque DECISIONES llama con `palabra_completa=True`.
- **BUG C â€” escritura_numero contamina referencias legales (fix):** El nÃºmero corto (ej: "854") reemplazaba en "ley 854 de 2003" y otros contextos. Fix: bloque ADQUISICION usa `palabra_completa=True` en todos sus campos. Guard existente `viejo == nuevo` ya cubre el caso de nÃºmero idÃ©ntico sin lÃ³gica adicional.

**Archivos creados/modificados:**
- `backend/app/services/minuta/detector.py` â€” PROMPT_B2: secciÃ³n ADQUISICION, renumeraciÃ³n 5â†’9, ejemplo JSON actualizado
- `frontend/lib/minuta.ts` â€” tipo `MinutaAdquisicion` + campo `adquisicion` en `MinutaDatos`
- `backend/app/services/minuta/reemplazador.py` â€” `agregar_reemplazo` con `palabra_completa`, bloque ADQUISICION, bloque DECISIONES con `palabra_completa=True`
- `frontend/components/minutas/nueva-minuta-workspace.tsx` â€” import `MinutaAdquisicion`, `EMPTY_ADQUISICION`, `AdquisicionCard`, estado + handler + inicializaciÃ³n + reset + payload

**Pendientes para la prÃ³xima sesiÃ³n:**
1. **[CRÃTICO] Deploy frontend a Vercel** â€” MÃºltiples sesiones acumuladas sin deploy: `vercel --cwd frontend --prod`
2. **[CRÃTICO] Deploy backend a Railway** â€” `detector.py` y `reemplazador.py` modificados; push al repo activa Railway automÃ¡ticamente
3. **[CRÃTICO] Verificar fix tour en producciÃ³n** â€” Remover `console.log("TOUR VISIBLE:", tourVisible)` en `nueva-minuta-workspace.tsx` antes de demo
4. **[CRÃTICO] Fix gap 1 â€” agregar `actividad_economica` a PersonaCard** â€” campo en tipo y reemplazador pero sin UI en el formulario
5. **[CRÃTICO] Fix gap 2 â€” agregar `domicilio` y `estado_civil` a `construir_lista_reemplazos()`** en `reemplazador.py`
6. **[CRÃTICO] Fix gap 4 â€” concordancia cuando solo cambia gÃ©nero** (sin cambio de nombre) en `concordancia.py:152`
7. **[BAJA] Remover prints `[GENERO DEBUG]`** de `reemplazador.py`
8. **[BAJA] Alembic out-of-sync** â€” `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';` en Supabase

**Estado al cierre:**
- Backend: Railway pendiente deploy â€” `detector.py` y `reemplazador.py` modificados, commits `ad7dc06` y `eb15519` en main sin deploy activo
- Frontend: Vercel pendiente deploy â€” `nueva-minuta-workspace.tsx` y `minuta.ts` modificados, mÃºltiples commits acumulados
- BD producciÃ³n: operativa, alembic_version desincronizada (pendiente UPDATE manual)
- Git: Ã¡rbol limpio â€” 2 commits nuevos en main (`ad7dc06`, `eb15519`)

---
## SesiÃ³n 2026-05-28

**Objetivo de la sesiÃ³n:** DiagnÃ³stico de dos bugs en el motor de minutas (campos ADQUISICIÃ“N y VIVIENDA FAMILIAR) e implementaciÃ³n de la UI y lÃ³gica de reemplazo para las decisiones notariales.

**Realizado:**
- **DiagnÃ³stico Bug 1 â€” ADQUISICIÃ“N:** Confirmada ausencia total en todas las capas â€” prompt detector, tipo TypeScript, reemplazador, UI y payload. Requiere implementaciÃ³n completa desde cero.
- **DiagnÃ³stico Bug 2 â€” VIVIENDA FAMILIAR:** Confirmado gap parcial â€” detector y tipo TS existen (`datos.decisiones`), faltaban UI y bloque en reemplazador.
- **nueva-minuta-workspace.tsx â€” DecisionesCard:** Nuevo componente con 3 toggles de 3 estados (`?`/`SÃ­`/`No`) para `vivienda_familiar`, `patrimonio_familia`, `notificacion_electronica`; colores amber/emerald/rose consistentes con el design system; badge "pendiente" cuando el valor es null.
- **nueva-minuta-workspace.tsx â€” estado y flujo:** `decisionesEdit` aÃ±adido como `useState`; inicializaciÃ³n desde `result.datos.decisiones` en `handleAnalizar` (merge con defaults null para los 3 campos); reset en `clearFile`; `updateDecision` handler; `decisiones: decisionesEdit` incluido en `datosNuevos` de `handleGenerar` (sobrescribe el spread de `analisisResult.datos`).
- **nueva-minuta-workspace.tsx â€” render Paso 2:** `<DecisionesCard>` renderizado despuÃ©s de ValoresCard, antes del botÃ³n "Continuar a generar".
- **reemplazador.py â€” construir_lista_reemplazos:** Bloque `# DECISIONES` aÃ±adido al final; itera los 3 campos; guarda contra `None` en cualquier extremo; convierte bool â†’ `"SÃ"`/`"NO"` antes de llamar `agregar_reemplazo`; reutiliza el guard `viejo == nuevo` existente para no generar par inÃºtil cuando no hay cambio.

**Archivos creados/modificados:**
- `backend/app/services/minuta/reemplazador.py` â€” bloque DECISIONES en construir_lista_reemplazos (L474â€“487)
- `frontend/components/minutas/nueva-minuta-workspace.tsx` â€” DecisionesCard, estado decisionesEdit, inicializaciÃ³n, handler, render y payload

**Pendientes para la prÃ³xima sesiÃ³n:**
1. **[CRÃTICO] Deploy frontend a Vercel** â€” MÃºltiples sesiones de cambios acumulados sin deploy: `vercel --cwd frontend --prod`
2. **[CRÃTICO] Deploy backend a Railway** â€” reemplazador.py modificado; push al repo activa Railway automÃ¡ticamente
3. **[CRÃTICO] Verificar fix tour en producciÃ³n** â€” Confirmar que click en zona de upload no cierra el tour; remover `console.log("TOUR VISIBLE:", tourVisible)` en `nueva-minuta-workspace.tsx` lÃ­nea ~1340 antes de demo
4. **[CRÃTICO] Bug 1 ADQUISICIÃ“N â€” implementar desde cero** â€” Requiere: (a) nueva secciÃ³n en PROMPT_B2 con campos `forma_adquisicion`, `escritura_anterior`, `notaria_anterior`, `vendedor_original`; (b) nuevo tipo `MinutaAdquisicion` en minuta.ts; (c) secciÃ³n en construir_lista_reemplazos; (d) `AdquisicionCard` en el formulario
5. **[CRÃTICO] Fix gap 1 â€” agregar `actividad_economica` a PersonaCard** â€” campo en tipo y reemplazador pero sin UI en el formulario
6. **[CRÃTICO] Fix gap 2 â€” agregar `domicilio` y `estado_civil` a `construir_lista_reemplazos()`** en `reemplazador.py:408`
7. **[CRÃTICO] Fix gap 4 â€” concordancia cuando solo cambia gÃ©nero** (sin cambio de nombre) en `concordancia.py:152`
8. **[MEDIA] Fix gap 3 â€” UI para decisiones** âœ… RESUELTO en esta sesiÃ³n
9. **[BAJA] Remover prints `[GENERO DEBUG]`** de `reemplazador.py`
10. **[BAJA] Alembic out-of-sync** â€” `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';` en Supabase

**Estado al cierre:**
- Backend: Railway operativo â€” `reemplazador.py` modificado, pendiente push/deploy
- Frontend: Vercel pendiente deploy â€” mÃºltiples sesiones acumuladas sin deploy a producciÃ³n
- BD producciÃ³n: operativa, alembic_version desincronizada (pendiente UPDATE manual)
- Git: 2 archivos modificados sin commitear â€” se commitean en este cierre

---
## SesiÃ³n 2026-05-26 (noche 4)

**Objetivo de la sesiÃ³n:** Diagnosticar y corregir bugs del tour guiado de minutas: cierre accidental al hacer click en la zona de upload (BUG 1) y ausencia de botÃ³n de relaunch visible (BUG 2).

**Realizado:**
- **DiagnÃ³stico BUG 1 (tour se cierra al subir documento):** Identificada causa raÃ­z â€” el backdrop div de `MinutasTour` (z-index 9998, `onClick={onSkip}`) capturaba todos los clicks del Ã¡rea visible, incluyendo los dirigidos a la zona de upload. El spotlight tenÃ­a `pointerEvents:none`, lo que dejaba pasar los clicks al backdrop en lugar de al `<label>` del upload zone.
- **Fix BUG 1 â€” minutas-tour.tsx:** (1) Spotlight cambiado a `pointerEvents:"auto"` para que capture sus propios clicks antes de que lleguen al backdrop. (2) Backdrop `onClick` reemplazado por `handleBackdropClick` inline que verifica `currentTargetEl.contains(e.target)` antes de llamar `onSkip`.
- **Fix BUG 2 â€” nueva-minuta-workspace.tsx:** Agregado botÃ³n fijo `?` en esquina inferior derecha con `fixed bottom-6 right-6 z-[9997]`, importado `HelpCircle` de lucide-react, llama `handleTourRelaunch`.
- **Debug log â€” nueva-minuta-workspace.tsx:** Agregado `console.log("TOUR VISIBLE:", tourVisible)` antes del return para confirmar diagnÃ³stico BUG 1 (pendiente de limpiar).
- **âš  Tour no activa en local:** El tour no se activa en el entorno de desarrollo local. No se pudo verificar el fix. Pendiente revisar 2026-05-27.

**Archivos creados/modificados:**
- `frontend/components/minutas/minutas-tour.tsx` â€” backdrop: contains check antes de onSkip; spotlight: pointerEvents noneâ†’auto
- `frontend/components/minutas/nueva-minuta-workspace.tsx` â€” import HelpCircle, console.log debug, botÃ³n relaunch fijo z-[9997]

**Pendientes para la prÃ³xima sesiÃ³n:**
1. **[CRÃTICO] Verificar fix tour en producciÃ³n o entorno funcional** â€” Confirmar que: (a) click en zona de upload no cierra el tour, (b) file picker abre mientras el tour estÃ¡ activo, (c) click fuera del spotlight sÃ­ cierra el tour. Si el file picker no abre con pointerEvents:auto en spotlight, agregar `onClick` al spotlight que reenvÃ­e el click: `el?.querySelector('input[type="file"], label')?.click()`
2. **[CRÃTICO] Remover console.log debug** â€” `console.log("TOUR VISIBLE:", tourVisible)` en `nueva-minuta-workspace.tsx` lÃ­nea 1248 antes de deploy
3. **[CRÃTICO] Fix gap 1 â€” agregar `actividad_economica` a PersonaCard** en `nueva-minuta-workspace.tsx:446`
4. **[CRÃTICO] Fix gap 2 â€” agregar `domicilio` y `estado_civil` a `construir_lista_reemplazos()`** en `reemplazador.py:408`
5. **[CRÃTICO] Fix gap 4 â€” concordancia cuando solo cambia gÃ©nero** (sin cambio de nombre) en `concordancia.py:152`
6. **[MEDIA] Fix gap 3 â€” UI para decisiones** (vivienda_familiar, patrimonio_familia, notificacion_electronica)
7. **[BAJA] Remover prints `[GENERO DEBUG]`** de `reemplazador.py`
8. **[BAJA] Alembic out-of-sync** â€” `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';`

**Estado al cierre:**
- Backend: Railway operativo â€” sin cambios de backend en esta sesiÃ³n
- Frontend: Vercel pendiente deploy â€” `minutas-tour.tsx` y `nueva-minuta-workspace.tsx` modificados sin deploy a producciÃ³n; tour no verificado en local
- BD producciÃ³n: operativa, alembic_version desincronizada (pendiente UPDATE manual)
- Git: 2 archivos sin commitear â€” se commitean en este cierre

---
## SesiÃ³n 2026-05-26 (noche 3)

**Objetivo de la sesiÃ³n:** Implementar tour guiado del mÃ³dulo de minutas con overlay spotlight, tooltip posicionado dinÃ¡micamente y estado persistente entre re-renders.

**Realizado:**
- **minutas-tour.tsx â€” nuevo componente (v1):** Tour de 7 pasos con overlay `box-shadow: 0 0 0 9999px` (mÃ¡s confiable que SVG mask), tooltip con flecha CSS border-trick posicionado automÃ¡ticamente (top/bottom/left/right segÃºn espacio disponible), animaciÃ³n pulse en el elemento destacado, progress dots, botÃ³n `?` fijo para relanzar
- **nueva-minuta-workspace.tsx â€” IDs de tour:** Agregados 7 `id` a elementos target: `tour-upload-zone`, `tour-btn-analizar`, `tour-validacion-banner`, `tour-persona-0`, `tour-inmueble-card`, `tour-valores-card`, `tour-btn-generar`; `PersonaCard` recibe prop `id?: string`
- **minutas-tour.tsx â€” fix overlay SVG:** Reemplazado `<svg mask>` por `div` con `box-shadow: 0 0 0 9999px rgba(0,0,0,0.60)` â€” el SVG usaba `fill="rgba()"` que no es vÃ¡lido en atributos SVG; tambien eliminado `rgba(var(--primary))` que tampoco es vÃ¡lido CSS en `rgba()`
- **minutas-tour.tsx â€” fix delay inicial:** Eliminado `setTimeout(setActive, 750)` â€” el tour ahora activa inmediatamente en el `useEffect` de mount; reducida latencia total de ~1150ms a ~400ms
- **minutas-tour.tsx â€” refactor state lifting:** Estado `active`/`currentStep`/`visible` movido al padre `NuevaMinutaWorkspace`; `MinutasTour` pasa a ser componente controlado que recibe `visible`, `currentStep`, `onNext`, `onPrev`, `onSkip`, `onFinish`, `onRelaunch` como props â€” asÃ­ el estado del tour sobrevive cualquier re-render del workspace (file upload, drag, ediciÃ³n de campos, etc.)
- **nueva-minuta-workspace.tsx â€” tour state:** `tourVisible` + `tourStep` como `useState`; `useEffect([], ...)` chequea localStorage (`easypro_minutas_tour_done`) y activa el tour en primera visita; handlers: `handleTourNext/Prev/Skip/Finish/Relaunch`

**Archivos creados/modificados:**
- `frontend/components/minutas/minutas-tour.tsx` â€” nuevo: tour guiado 7 pasos, overlay box-shadow, tooltip auto-posicionado, estado controlado por props
- `frontend/components/minutas/nueva-minuta-workspace.tsx` â€” IDs de tour en 7 elementos, prop `id` en PersonaCard, estado del tour (`tourVisible`/`tourStep`), handlers, `<MinutasTour>` con props completos

**Pendientes para la prÃ³xima sesiÃ³n:**
1. **[CRÃTICO] Fix gap 1 â€” agregar `actividad_economica` a PersonaCard** en `nueva-minuta-workspace.tsx:446` (campo en tipo y reemplazador pero sin UI)
2. **[CRÃTICO] Fix gap 2 â€” agregar `domicilio` y `estado_civil` a `construir_lista_reemplazos()`** en `reemplazador.py:408`
3. **[CRÃTICO] Fix gap 4 â€” concordancia cuando solo cambia gÃ©nero** (sin cambio de nombre) en `concordancia.py:152`
4. **[CRÃTICO] Reescribir detector con Structured Outputs** (`json_schema` + `strict: True`) per gap 5
5. **[MEDIA] Fix gap 3 â€” UI para decisiones** (vivienda_familiar, patrimonio_familia, notificacion_electronica)
6. **[BAJA] Remover `[GENERO DEBUG]` prints** de `reemplazador.py`
7. **[BAJA] Alembic out-of-sync** â€” `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';`

**Estado al cierre:**
- Backend: Railway operativo â€” sin cambios de backend en esta sesiÃ³n
- Frontend: Vercel pendiente deploy â€” `minutas-tour.tsx` nuevo + `nueva-minuta-workspace.tsx` modificado sin deploy a producciÃ³n
- BD producciÃ³n: operativa, alembic_version desincronizada (pendiente UPDATE manual)
- Git: 2 archivos sin commitear â€” se commitean en este cierre

---
## SesiÃ³n 2026-05-26 (noche 2)

**Objetivo de la sesiÃ³n:** AuditorÃ­a tÃ©cnica completa del motor de minutas â€” lectura y anÃ¡lisis de todos los archivos del sistema sin modificar cÃ³digo.

**Realizado:**
- **Lectura completa de 9 archivos clave:** `router.py`, `detector.py`, `reemplazador.py`, `concordancia.py`, `validador.py`, `nueva-minuta-workspace.tsx`, `minuta.ts`, `listas-notariales.ts`, `colombia-geo.ts`
- **Flujo completo documentado:** desde upload del .docx hasta apertura en OnlyOffice, con cada funciÃ³n, endpoint y transformaciÃ³n identificada paso a paso
- **AnÃ¡lisis del formulario:** PersonaCard estÃ¡tica (11 campos visibles, `actividad_economica` ausente), InmuebleCard 18 campos, NotariaCard con selectores geo encadenados, ValoresCard dinÃ¡mica
- **Detector auditado:** clasificaciÃ³n B1/B2 heurÃ­stica, PROMPT_B2 con 8 secciones, uso de `json_object` sin schema estricto, `max_tokens=8000`
- **Reemplazador auditado:** `construir_lista_reemplazos` cubre 14 campos inmueble + personas + notarÃ­a + fechas; `domicilio` y `estado_civil` se editan en UI pero NO se reemplazan; `_normalizar_guiones` parcialmente inefectivo
- **Validador auditado:** capa determinista + GPT-4o-mini; valida datos del detector, no los editados por el usuario; `CAMPOS_OBLIGATORIOS_POR_ACTO` incompleto
- **Concordancia auditada:** solo se dispara si nombre Y gÃ©nero cambian; artÃ­culos de rol ordenados por longitud; texto truncado a 40k chars
- **10 gaps crÃ­ticos identificados** con archivos y lÃ­neas exactas

**Archivos creados/modificados:**
- (ninguno â€” sesiÃ³n de solo lectura)

**Pendientes para la prÃ³xima sesiÃ³n:**
1. **[CRÃTICO] Fix gap 1 â€” agregar `actividad_economica` a PersonaCard** en `nueva-minuta-workspace.tsx:446` (campo en tipo y reemplazador pero sin UI)
2. **[CRÃTICO] Fix gap 2 â€” agregar `domicilio` y `estado_civil` a `construir_lista_reemplazos()`** en `reemplazador.py:408`
3. **[CRÃTICO] Fix gap 4 â€” concordancia cuando solo cambia gÃ©nero** (sin cambio de nombre) en `concordancia.py:152`
4. **[CRÃTICO] Reescribir detector con Structured Outputs** (`json_schema` + `strict: True`) per gap 5
5. **[MEDIA] Fix gap 3 â€” UI para decisiones** (vivienda_familiar, patrimonio_familia, notificacion_electronica)
6. **[BAJA] Remover `[GENERO DEBUG]` prints** de `reemplazador.py:319`
7. **[BAJA] Alembic out-of-sync** â€” `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';`

**Estado al cierre:**
- Backend: Railway operativo â€” Ãºltimo commit `9ec57a5`, sin cambios de backend en esta sesiÃ³n
- Frontend: Vercel operativo â€” easypronotarial.com, sin cambios de frontend en esta sesiÃ³n
- BD producciÃ³n: operativa, alembic_version desincronizada (pendiente UPDATE manual)
- Git: Ã¡rbol limpio â€” solo `tsconfig.tsbuildinfo` (ignorar)

---
## SesiÃ³n 2026-05-26 (tarde 2)

**Objetivo de la sesiÃ³n:** Mejorar el formulario de minutas â€” normalizaciÃ³n de campos del inmueble, selectores geogrÃ¡ficos Colombia, separador de miles en valores monetarios.

**Realizado:**
- **nueva-minuta-workspace.tsx â€” normalizar tipo inmueble (977724e):** `handleAnalizar` aplica `TIPOS_INMUEBLE_MAP` antes de `setInmuebleEdit` para que `"apartamento"` â†’ `"Apartamento"` coincida con las opciones del select; cast a `Partial<MinutaInmueble>` para resolver error TypeScript
- **detector.py â€” campos catastrales y orden actos (c11cbb0):** SecciÃ³n INMUEBLE del PROMPT_B2 expandida con instrucciones precisas para `cedula_catastral`, `codigo_catastral`, `area_construida`, `area_privada`, `area_total`, `piso`, `barrio`, `direccion`, `nota_linderos`, `linderos` (NO resumir). SecciÃ³n ACTOS con regla de ordenamiento: acto principal primero, accesorios despuÃ©s. Ejemplo JSON actualizado con nuevos campos
- **detector.py â€” reforzar cÃ³digo catastral (9da8500):** InstrucciÃ³n diferencia explÃ­citamente cÃ³digo alfanumÃ©rico corto (ej: `AAX0009PUYC`) vs cÃ©dula numÃ©rica larga de 28 dÃ­gitos
- **nueva-minuta-workspace.tsx â€” ancho campos catastrales (9da8500):** Grid de 3 columnas partido en dos filas de 2 columnas â€” matrÃ­cula+cÃ©dula catastral en primera fila, cÃ³digo catastral en segunda; mÃ¡s espacio para valores largos
- **colombia-geo.ts â€” nuevo archivo (5eaf153):** 33 departamentos (incluyendo BogotÃ¡ D.C.) con ~900 municipios segÃºn DANE. Helpers `getMunicipiosByDepartamento()` y `getDepartamentoByMunicipio()`
- **nueva-minuta-workspace.tsx â€” selectores encadenados (5eaf153):** InmuebleCard reemplaza inputs de texto por selects departamentoâ†’municipio; al cambiar departamento, municipio se limpia automÃ¡ticamente. NotariaCard agrega estado local `depNotaria` + selects encadenados con sincronizaciÃ³n por ref desde `municipio_notaria`. `handleAnalizar` infiere departamento con `getDepartamentoByMunicipio()` si el detector no lo devuelve
- **nueva-minuta-workspace.tsx â€” separador de miles (1df8011):** Helpers `formatCOP()` (â†’ `200.000.000`) y `parseCOP()` (quita puntos antes de guardar); input de monto reemplaza `SectionField` con `type="text" inputMode="numeric"` que muestra valor formateado pero envÃ­a nÃºmero limpio al backend

**Archivos creados/modificados:**
- `frontend/lib/colombia-geo.ts` â€” nuevo: 33 departamentos, ~900 municipios DANE, helpers geo
- `frontend/components/minutas/nueva-minuta-workspace.tsx` â€” normalizaciÃ³n tipo inmueble, selectores geo encadenados, separador miles, ancho campos catastrales
- `backend/app/services/minuta/detector.py` â€” PROMPT_B2: campos catastrales expandidos, orden actos, cÃ³digo catastral diferenciado

**Pendientes para la prÃ³xima sesiÃ³n:**
1. **[CRÃTICO] Reescribir detector con Structured Outputs de OpenAI** â€” Cambiar `response_format=json_object` por `json_schema` con `strict: True`; schema completo con `linderos` (norte/sur/oriente/occidente), `adquisicion` (forma, escritura previa, notarÃ­a, vendedor original), `poderes`, `valores_notariales` (derechos notariales, superfondo, IVA); prompts mejorados basados en documentos reales de NotarÃ­a de Bello
2. **[CRÃTICO] Verificar bug SEBASTIÃN en producciÃ³n** â€” Generar minuta real con SEBASTIÃN y DANIELA, revisar logs Railway
3. **[CRÃTICO] Verificar concordancia en producciÃ³n** â€” Confirmar que fix `finish_reason` resuelve crash con documento real
4. **[MEDIA] Formulario dinÃ¡mico â€” campos faltantes persona** â€” `actividad_economica` no en PersonaCard; decisiones (vivienda_familiar, patrimonio_familia, notificacion_electronica) sin UI
5. **[BAJA] Debug prints `GENERO DEBUG`** â€” Remover de `router.py` y `reemplazador.py`
6. **[BAJA] Alembic out-of-sync** â€” `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';` en Supabase

**Estado al cierre:**
- Backend: Railway con deploy activo â€” `c11cbb0` y `9da8500` pusheados (Railway despliega automÃ¡ticamente)
- Frontend: Vercel operativo â€” easypronotarial.com, 5 deploys realizados en esta sesiÃ³n
- BD producciÃ³n: operativa, alembic_version desincronizada (pendiente UPDATE manual)
- Git: Ã¡rbol limpio â€” solo `tsconfig.tsbuildinfo` modificado (ignorar)

---
## SesiÃ³n 2026-05-27

**Objetivo de la sesiÃ³n:** Fix JSON truncado en concordancia + expandir secciÃ³n inmueble del formulario de minutas (18 campos, select tipo, textarea linderos).

**Realizado:**
- **concordancia.py â€” Fix 1 (texto truncado):** `texto_documento[:80000]` â†’ `[:40000]` para reducir tokens enviados al modelo
- **concordancia.py â€” Fix 2 (max_tokens + finish_reason):** `max_tokens=16384` â†’ `8000`; si `finish_reason == "length"` retorna `{"cambios": [], "truncado": True}` sin crash
- **concordancia.py â€” Fix 3 (prompt simplificado):** Eliminados `contexto_ejemplo` y `razon` del esquema JSON; solo `palabra_antes`, `palabra_despues`, `confianza` â€” respuestas mÃ¡s cortas
- **router.py â€” Fix 4 (try/except concordancia):** `detectar_concordancia` envuelto en try/except; si falla, `resultado_conc = {"cambios": []}` y el endpoint `/generar` continÃºa sin bloqueo
- **minuta.ts â€” MinutaInmueble extendida:** 8 campos â†’ 18 campos nuevos: `cedula_catastral`, `codigo_catastral`, `area_construida`, `area_privada`, `area_total`, `direccion`, `barrio`, `piso`, `nota_linderos`, `propiedad_horizontal`
- **nueva-minuta-workspace.tsx â€” InmuebleCard expandida:** 5 inputs â†’ 9 filas: select tipo de inmueble (8 opciones), nÃºmero/piso, conjunto+barrio, direcciÃ³n full-width, municipio+departamento+select propiedad horizontal, matrÃ­cula+cÃ©dula catastral+cÃ³digo catastral, 3 Ã¡reas mÂ², coeficiente copropiedad, select nota de linderos (NOTAS_LINDEROS), textarea linderos (rows=5 con resize); `EMPTY_INMUEBLE` actualizado; import `NOTAS_LINDEROS` agregado
- **reemplazador.py â€” construir_lista_reemplazos:** Loop inmueble expandido de 5 a 14 campos; `tipo`/`direccion`/`barrio`/`piso` usan etiquetas sufijadas `_inmueble` para evitar conflicto con campos de persona en los logs

**Archivos creados/modificados:**
- `backend/app/services/minuta/concordancia.py` â€” fix tokens, prompt simplificado, manejo finish_reason
- `backend/app/modules/minuta/router.py` â€” try/except alrededor de detectar_concordancia
- `backend/app/services/minuta/reemplazador.py` â€” construir_lista_reemplazos inmueble expandido
- `frontend/lib/minuta.ts` â€” MinutaInmueble extendida a 18 campos
- `frontend/components/minutas/nueva-minuta-workspace.tsx` â€” InmuebleCard expandida, EMPTY_INMUEBLE, import NOTAS_LINDEROS

**Pendientes para la prÃ³xima sesiÃ³n:**
1. **[CRÃTICO] Deploy frontend a Vercel** â€” `vercel --cwd frontend --prod` (commits de esta sesiÃ³n + sesiones anteriores sin deploy)
2. **[CRÃTICO] Deploy backend a Railway** â€” concordancia.py fix crÃ­tico para producciÃ³n; push al repo ya lo activa en Railway
3. **[CRÃTICO] Verificar bug SEBASTIÃN en producciÃ³n** â€” Generar minuta real con SEBASTIÃN y DANIELA, revisar logs Railway
4. **[CRÃTICO] Verificar concordancia en producciÃ³n** â€” Confirmar que fix finish_reason resuelve el crash; probar con documento real que tenga cambio de gÃ©nero
5. **[MEDIA] Formulario dinÃ¡mico â€” campos faltantes persona** â€” `actividad_economica` no estÃ¡ en PersonaCard; decisiones (vivienda_familiar, patrimonio_familia, notificacion_electronica) sin UI
6. **[BAJA] Debug prints `GENERO DEBUG`** â€” Remover de `router.py` y `reemplazador.py` antes de demo
7. **[BAJA] Alembic out-of-sync** â€” `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';` en Supabase

**Estado al cierre:**
- Backend: Railway pendiente deploy â€” fixes concordancia y reemplazador sin push todavÃ­a
- Frontend: Vercel pendiente deploy â€” InmuebleCard expandida sin deploy a producciÃ³n
- BD producciÃ³n: operativa, alembic_version desincronizada (pendiente UPDATE manual)
- Git: 5 archivos modificados sin commitear â€” se commitean en este cierre

---
## SesiÃ³n 2026-05-26 (noche)

**Objetivo de la sesiÃ³n:** Implementar Capa 2 del motor de minutas â€” listas notariales oficiales, fix estado civil dinÃ¡mico por gÃ©nero, validador notarial con IA.

**Realizado:**
- **listas-notariales.ts â€” nuevo archivo (46255cf):** `ESTADOS_CIVILES_F` (12 opciones), `ESTADOS_CIVILES_M` (11 opciones), `ESTADOS_CIVILES_COMPARTIDOS`, `TIPOS_DOCUMENTO` (7 tipos con values C.C/C.E/T.I/PAS/P.P.T/R.C/NIT), `NOTAS_LINDEROS`, helper `getEstadosCiviles(genero)`
- **nueva-minuta-workspace.tsx â€” fix estado civil (46255cf):** Select dinÃ¡mico filtrado por gÃ©nero (solo opciones femeninas/masculinas segÃºn selecciÃ³n); `handleChange` corregido â€” limpia estado_civil si el valor actual no aplica al nuevo gÃ©nero; cascada nacionalidad preservada; eliminadas `TIPO_DOC_OPTIONS` y `ESTADO_CIVIL_OPTIONS` hardcodeadas
- **detector.py â€” fix tipo_documento en prompt (3a94650):** Valores estandarizados `"C.C", "C.E", "T.I", "PAS", "P.P.T", "R.C", "NIT"` en PROMPT_B2; ejemplo JSON actualizado `CC â†’ C.C`
- **minuta.ts â€” tipos completos (3a94650, 461f958):** Nueva interfaz `MinutaFechas`; `MinutaDatos` incluye `fechas?: MinutaFechas`; `MinutaAnalisisResult` incluye `texto_original?: string`; nuevas interfaces `MinutaValidacionCampo`, `MinutaValidacion`; `MinutaAnalisisResult` incluye `validacion?: MinutaValidacion`
- **validador.py â€” nuevo servicio Capa 2 (461f958, 9a1e643):** Validaciones deterministas sin IA (formato cÃ©dulas/NIT/T.I., matrÃ­cula, nÃºmero escritura, roles por acto); validaciÃ³n IA con GPT-4o-mini usando `PROMPT_VALIDADOR`; retorna semÃ¡foros `ok/advertencia/faltante/inferido` por campo + alertas crÃ­ticas + inferencias aplicadas + resumen con `listo_para_generar`; usa `_make_openai_client()` igual que `detector.py`
- **router.py â€” integraciÃ³n validador (461f958, 9a1e643):** Endpoint `/analizar` llama `validar_documento(datos, actos, api_key)` tras el anÃ¡lisis; try/except garantiza que fallo no bloquea
- **nueva-minuta-workspace.tsx â€” banner validaciÃ³n (461f958):** Paso 2 muestra banner verde/amarillo/rojo con nivel de confianza, conteo de campos, alertas crÃ­ticas en rojo con âš , inferencias en azul con â†’

**Archivos creados/modificados:**
- `frontend/lib/listas-notariales.ts` â€” nuevo: listas oficiales notariales colombianas
- `frontend/components/minutas/nueva-minuta-workspace.tsx` â€” fix estado civil dinÃ¡mico + banner validaciÃ³n
- `frontend/lib/minuta.ts` â€” MinutaFechas, MinutaValidacion, validacion? en AnalisisResult
- `backend/app/services/minuta/detector.py` â€” tipo_documento estandarizado en prompt
- `backend/app/services/minuta/validador.py` â€” nuevo: validador notarial Capa 2
- `backend/app/modules/minuta/router.py` â€” integrar validar_documento en /analizar
- `backend/requirements.txt` â€” sin anthropic (se agregÃ³ y se revirtiÃ³ en la misma sesiÃ³n)
- `backend/app/core/config.py` â€” sin anthropic_api_key (idem)

**Pendientes para la prÃ³xima sesiÃ³n:**
1. **[CRÃTICO] Verificar validador en producciÃ³n** â€” Hacer deploy a Railway y analizar un documento real; revisar que el banner aparece en Paso 2 y que las alertas/inferencias son correctas
2. **[CRÃTICO] Verificar bug SEBASTIÃN** â€” Generar minuta real con SEBASTIÃN y DANIELA, revisar logs Railway; mÃºltiples fixes aplicados pero sin verificaciÃ³n en producciÃ³n desde sesiÃ³n 2026-05-23
3. **[CRÃTICO] Verificar concordancia con Claude** â€” SESSION anterior indica que concordancia.py fue migrada a Claude; confirmar ANTHROPIC_API_KEY en Railway y que artÃ­culos ELâ†’LA funcionan
4. **[MEDIA] Debug prints `GENERO DEBUG`** â€” Hay prints de debug activos en `router.py` y `reemplazador.py` â€” remover antes de demo
5. **[MEDIA] Validador â€” probar con documentos reales** â€” Confirmar que inferencias (departamento desde municipio, zona desde matrÃ­cula) funcionan y que no hay falsos positivos en alertas crÃ­ticas
6. **[BAJA] Alembic out-of-sync** â€” `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';` en Supabase producciÃ³n (pendiente desde sesiones anteriores)

**Estado al cierre:**
- Backend: Railway operativo â€” Ãºltimo commit en repo `9a1e643`; pendiente deploy para activar validador
- Frontend: Vercel operativo â€” easypronotarial.com; pendiente deploy para activar banner validaciÃ³n
- BD producciÃ³n: operativa, alembic_version desincronizada (pendiente)
- Git: Ã¡rbol limpio â€” 4 commits nuevos pusheados

---
## SesiÃ³n 2026-05-26 (tarde)

**Objetivo de la sesiÃ³n:** Fixes visuales del dashboard ejecutivo (pie chart, filtros, KPIs) y diagnÃ³stico del formulario dinÃ¡mico de minutas para planificar prÃ³xima iteraciÃ³n.

**Realizado:**
- **dashboard.tsx â€” rediseÃ±o PieActCard (b3404e6):** Donut chart (`innerRadius=55`), leyenda lateral custom con scroll, `CustomTooltip` con nombre + cantidad + porcentaje; removidos `label`/`labelLine`/`Legend`/`ResponsiveContainer`
- **dashboard.tsx â€” filtros grid fluido (16e2f76):** Grid `md:grid-cols-2 xl:grid-cols-12` con `col-span-2` fijo â†’ `sm:grid-cols-2 lg:grid-cols-3`; `rounded-2xl` â†’ `rounded-lg` en todos los controles; botones de `rounded-full` + `ep-card-soft` â†’ `rounded-lg` con CSS vars del design system
- **dashboard.tsx â€” fixes post-deploy (87eea3f, bcb7646):** Grid reducido a `lg:grid-cols-3` (5 filtros quedan 3+2 sin solitarios); tÃ­tulo "Tipos de acto" `uppercase tracking-widest` removido; botÃ³n submit `bg-[var(--primary)]` â†’ `bg-primary` (clase Tailwind directa, CSS var no resolvÃ­a en producciÃ³n)
- **dashboard.tsx â€” fixes visuales tanda 2 (4730d95):** KPI labels sin `uppercase tracking-[0.18em]`; `formatEstado()` convierte `revision_aprobador` â†’ "Revision Aprobador" en docsByState; card notarÃ­a navy full-width reemplazada por tarjeta discreta con icono `Building2`; tÃ­tulo pie chart `text-accent` â†’ `text-[var(--ink)]`
- **DiagnÃ³stico detector.py + /analizar:** Lectura completa â€” detector usa `gpt-4o-mini`, heurÃ­stica local para B1/B2, `max_tokens=8000`, endpoint `/analizar` es wrapper directo sin lÃ³gica adicional
- **DiagnÃ³stico formulario dinÃ¡mico:** El formulario del Paso 2 es completamente estÃ¡tico â€” no hay lÃ³gica por tipo de acto. Campos del backend que no se muestran: `actividad_economica`, `inmueble.tipo`, `inmueble.coeficiente_copropiedad`, `inmueble.linderos`, `datos.decisiones` (vivienda_familiar, patrimonio_familia, notificacion_electronica). `datos.fechas` se accede vÃ­a cast manual, no estÃ¡ en el tipo `MinutaDatos`.

**Archivos creados/modificados:**
- `frontend/components/app-shell/dashboard.tsx` â€” PieActCard donut, filtros grid fluido, fixes visuales KPIs/estados/notarÃ­a/pie title

**Pendientes para la prÃ³xima sesiÃ³n:**
1. **[CRÃTICO] Deploy frontend a Vercel** â€” 4 commits locales sin deploy a producciÃ³n: `vercel --cwd frontend --prod`
2. **[CRÃTICO] Verificar bug SEBASTIÃN en producciÃ³n** â€” Generar minuta real con SEBASTIÃN y DANIELA, revisar logs Railway
3. **[CRÃTICO] Verificar concordancia Claude** â€” Confirmar `ANTHROPIC_API_KEY` en Railway y artÃ­culos ELâ†’LA / DELâ†’DE LA
4. **[MEDIA] Formulario dinÃ¡mico â€” campos faltantes** â€” Agregar `actividad_economica` a `PersonaCard`; UI para `decisiones` (checkboxes vivienda_familiar, patrimonio_familia, notificacion_electronica); tipar `fechas` en `MinutaDatos`
5. **[BAJA] Debug prints `GENERO DEBUG`** â€” Remover de `router.py` y `reemplazador.py` antes de demo
6. **[BAJA] Alembic out-of-sync** â€” `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';` en Supabase

**Estado al cierre:**
- Backend: Railway operativo â€” sin cambios de backend en esta sesiÃ³n
- Frontend: Vercel desactualizado â€” 4 commits locales pendientes de deploy
- BD producciÃ³n: operativa, alembic_version desincronizada (pendiente UPDATE manual)
- Git: Ã¡rbol limpio â€” 4 commits ahead de origin/main (se pushean en este cierre)

---
## SesiÃ³n 2026-05-26

**Objetivo de la sesiÃ³n:** RenovaciÃ³n del design system (tipografÃ­a, tokens semÃ¡nticos, colores de grÃ¡ficas) e implementaciÃ³n de estados de progreso por pasos para las acciones IA.

**Realizado:**
- **globals.css â€” tipografÃ­a:** `font-family` cambia de Aptos a `var(--font-jakarta)` con fallback a Segoe UI
- **layout.tsx â€” Plus Jakarta Sans (1059f62):** `next/font/google` con pesos 300/400/500/600, variable CSS `--font-jakarta` inyectada en `<body>`
- **globals.css â€” variables semÃ¡nticas (1059f62):** Nuevas vars en `:root` y `[data-theme="dark"]`: `--primary-light`, `--error`, `--error-text`, `--error-border`, `--warning-text`, `--warning-border`, `--success-text`, `--success-border`, `--info-bg`, `--info-text`, `--info-border`
- **globals.css â€” componentes .ep-* (1059f62):** `.ep-card` con `0.5px` border + hover state con sombra suave; `.ep-nav-item` con `transition: 0.12s`; 5 nuevas clases `.ep-badge-{success,warning,error,info,neutral}`; sombras inset dark-safe (0.04 light / 0.02 dark con override `[data-theme="dark"]`)
- **validated-input.tsx (1059f62):** Colores de error usan `var(--error-text)` y `var(--error-border)` en lugar de `rose-500`
- **color-constants.ts (1059f62):** Nuevo archivo `frontend/lib/color-constants.ts` con `CHART_COLORS` y `CHART_PALETTE` sincronizados con el design system
- **dashboard.tsx (1059f62 + b3404e6):** `CHART_PALETTE` reemplaza array hardcodeado; luego rediseÃ±o completo del PieActCard: donut chart (`innerRadius=55`), leyenda lateral custom con color swatches, tooltip personalizado usando CSS vars del sistema
- **ai-progress-modal.tsx (b12bb3b):** Nuevo componente reutilizable con pasos `done/active/pending`, barra de progreso animada y `PulseDots` con `@keyframes ep-pulse`; dark-mode nativo vÃ­a CSS vars
- **nueva-minuta-workspace.tsx (b12bb3b):** `handleAnalizar` y `handleGenerar` integran `AiProgressModal` con 4 pasos cada uno; progreso simulado + cierre automÃ¡tico; modal se cierra en `catch`
- **create-case-wizard.tsx (b12bb3b):** `handlePrimaryAction` paso 2 (Gari) muestra `AiProgressModal` con 5 pasos (plantilla â†’ intervinientes â†’ redactar â†’ clÃ¡usulas â†’ guardar); modal se cierra en `catch`

**Archivos creados/modificados:**
- `frontend/app/layout.tsx` â€” Plus Jakarta Sans, variable --font-jakarta
- `frontend/app/globals.css` â€” font-family, vars semÃ¡nticas, .ep-badge-*, sombras inset, @keyframes ep-pulse
- `frontend/components/ui/validated-input.tsx` â€” error colors con CSS vars
- `frontend/lib/color-constants.ts` â€” nuevo archivo, CHART_COLORS + CHART_PALETTE
- `frontend/components/app-shell/dashboard.tsx` â€” CHART_PALETTE + rediseÃ±o PieActCard donut
- `frontend/components/ui/ai-progress-modal.tsx` â€” nuevo componente AiProgressModal
- `frontend/components/minutas/nueva-minuta-workspace.tsx` â€” AiProgressModal en analizar y generar
- `frontend/components/cases/create-case-wizard.tsx` â€” AiProgressModal en Gari paso 2

**Pendientes para la prÃ³xima sesiÃ³n:**
1. **[CRÃTICO] Verificar bug SEBASTIÃN en producciÃ³n** â€” Generar minuta real con SEBASTIÃN y DANIELA, revisar logs Railway para confirmar que SEBASTIÃN no recibe reemplazos incorrectos
2. **[CRÃTICO] Verificar concordancia con Claude** â€” Confirmar `ANTHROPIC_API_KEY` en Railway y que artÃ­culos ELâ†’LA / DELâ†’DE LA funcionan
3. **[CRÃTICO] Deploy a producciÃ³n** â€” `vercel --cwd frontend --prod` (3 commits nuevos pendientes de deploy) + push a Railway del backend si hay cambios
4. **[MEDIA] Guiones dobles `-- -` sin resolver del todo** â€” Confirmar con documento real que `_normalizar_guiones` funciona correctamente
5. **[BAJA] Alembic out-of-sync** â€” Ejecutar en Supabase: `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';`
6. **[BAJA] Debug prints `GENERO DEBUG`** â€” Remover prints de debug en `router.py` y `reemplazador.py` antes de demo

**Estado al cierre:**
- Backend: Railway operativo â€” commit `afab702` activo (sin cambios de backend hoy)
- Frontend: Vercel pendiente deploy â€” 3 commits nuevos locales no pusheados a Vercel
- BD producciÃ³n: operativa, alembic_version desincronizada (pendiente UPDATE manual)
- Git: Ã¡rbol limpio â€” 3 commits ahead de origin/main (se pushean en este cierre)

---
## SesiÃ³n 2026-05-23 (tarde)

**Objetivo de la sesiÃ³n:** Completar el motor de minutas â€” fixes de gÃ©nero/guiones, secciones editables de inmueble/notarÃ­a/valores en el frontend, y cobertura completa de reemplazos en el backend.

**Realizado:**
- **reemplazador.py â€” _normalizar_guiones (9fdb543, 1b57295, f878b7b, c7c9eec):** MÃºltiples iteraciones: primero consolidar texto en runs[0] vaciar el resto; luego refactors con guard `not run.text`, colapso de `--` solo cuando rodeado de espacios, y finalmente reemplazar dentro de cada run para preservar formato
- **router.py â€” todos_nombres_doc (9fdb543, fc5e004, e2883dc):** Enriquecer con scanner de secuencias MAYÃšSCULAS del documento; luego cambiar a escanear todo el doc sin filtro de lÃ­nea conocida; finalmente procesar personas F antes que M y filtrar falsos positivos
- **router.py â€” aplicar genero contextual (433b345):** Aplicar reemplazos de gÃ©nero a TODAS las personas nuevas con gÃ©nero definido, no solo las que cambian Mâ†”F
- **concordancia.py â€” refactor y fixes (a2099bb, e6ab5c8, ff9f84c, 715d304, afab702):** Concordancia vÃ­a Claude solo maneja artÃ­culos de rol; recibe `personas_resto` para preservar gÃ©nero de otras personas; max_tokens 8000 â†’ 32000 â†’ 16384 (lÃ­mite real del modelo); strip markdown; try/except con diagnÃ³stico
- **reemplazador.py â€” construir_lista_reemplazos (12bba1d, 2eddc5b):** Agrega secciones `notaria` (nombre_notaria, municipio_notaria, numero_escritura), `fechas` (fecha_otorgamiento) e `inmueble` completo (municipio, departamento); guard contra valores non-string
- **nueva-minuta-workspace.tsx â€” secciones editables:** Tres nuevas cards en Paso 1: `InmuebleCard`, `NotariaCard`, `ValoresCard`; estado `inmuebleEdit`/`notariaEdit`/`valoresEdit`; `handleGenerar` pasa los tres al backend; fix `n.trim is not a function` con `?? ""`; null-checks en inicializaciÃ³n desde `analisisResult.datos`
- **nueva-minuta-workspace.tsx â€” numeroALetras:** FunciÃ³n de conversiÃ³n nÃºmero a letras (pesos moneda corriente) integrada en el workspace
- **navigation.ts:** "Crear Minuta" redirige a `/dashboard/minutas/nueva` en lugar de `/dashboard/casos/crear`

**Archivos creados/modificados:**
- `backend/app/modules/minuta/router.py` â€” scanner nombres, genero contextual todas las personas, todos_nombres_doc
- `backend/app/services/minuta/reemplazador.py` â€” _normalizar_guiones (mÃºltiples fixes), construir_lista_reemplazos completo, guard non-string
- `backend/app/services/minuta/concordancia.py` â€” max_tokens 16384, strip markdown, try/except, refactor a solo artÃ­culos, personas_resto
- `frontend/components/minutas/nueva-minuta-workspace.tsx` â€” 3 secciones editables, numeroALetras, null-checks, fix trim
- `frontend/lib/navigation.ts` â€” "Crear Minuta" apunta a /minutas/nueva

**Pendientes para la prÃ³xima sesiÃ³n:**
1. **[CRÃTICO] Verificar bug SEBASTIÃN en producciÃ³n** â€” MÃºltiples fixes aplicados (scanner, orden Fâ†’M, genero contextual ampliado). Generar minuta real con SEBASTIÃN y DANIELA, revisar logs Railway para confirmar que SEBASTIÃN no recibe reemplazos incorrectos
2. **[CRÃTICO] Verificar concordancia con Claude** â€” Concordancia ahora usa Claude en lugar de GPT-4o-mini para artÃ­culos; confirmar que el modelo estÃ¡ configurado correctamente en Railway (ANTHROPIC_API_KEY) y que los reemplazos de artÃ­culos funcionan
3. **[MEDIA] Guiones dobles `-- -` sin resolver del todo** â€” _normalizar_guiones tuvo mÃºltiples iteraciones; confirmar con documento real que los guiones dobles quedan bien
4. **[MEDIA] Concordancia de artÃ­culos ELâ†’LA, DELâ†’DE LA** â€” Verificar que el refactor a Claude (solo artÃ­culos de rol) produce resultados correctos
5. **[BAJA] Alembic out-of-sync** â€” `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';` en Supabase producciÃ³n (pendiente desde sesiones anteriores)
6. **[BAJA] debug prints en router.py y reemplazador.py** â€” Hay prints de debug (`GENERO DEBUG`) que deben removerse antes de demo

**Estado al cierre:**
- Backend: Railway operativo â€” commit `afab702` activo
- Frontend: Vercel operativo â€” easypronotarial.com, Ãºltimo deploy con null-checks
- BD producciÃ³n: operativa, alembic_version desincronizada (pendiente)
- Git: `nueva-minuta-workspace.tsx` y `navigation.ts` modificados localmente â€” se commitean en este cierre

---
## SesiÃ³n 2026-05-23

**Objetivo de la sesiÃ³n:** Corregir bugs de gÃ©nero (SEBASTIÃN y concordancia global) y agregar lÃ³gica de auto-cascada de nacionalidad/estado civil en el formulario frontend.

**Realizado:**
- **router.py â€” reemplazos de gÃ©nero deterministas (ee93a7e):** Agregar `_GENERO_M_A_F` y `_GENERO_F_A_M` con `varÃ³n/mujer`, `soltero/a`, `colombiano/a`, `domiciliado/a`, `identificado/a` â€” todos con `palabra_completa: True`
- **reemplazador.py â€” aplicar_reemplazos_por_contexto (d266d6f):** Nueva funciÃ³n que aplica reemplazos de gÃ©nero solo en pÃ¡rrafos que contienen el nombre de la persona especÃ­fica
- **reemplazador.py â€” aplicar_genero_contextual_docx (d266d6f):** Nueva funciÃ³n que orquesta los pares personaâ†’reemplazos con exclusiÃ³n mutua entre personas del documento
- **router.py â€” integrar gÃ©nero contextual (d266d6f):** Paso 5 del endpoint `/generar` llama `aplicar_genero_contextual_docx` pasando `pares_genero` y `todos_nombres_doc`
- **reemplazador.py + router.py â€” colombiano/a (a101c26):** Agregar entradas `colombianoâ†’colombiana` y `colombianaâ†’colombiano` a los bloques Mâ†’F y Fâ†’M
- **router.py â€” fix exclusiÃ³n SEBASTIÃN (610a817):** `todos_nombres_doc` ahora combina `datos_ant.personas + datos_nv.personas` con set para deduplicar â€” asÃ­ personas que no cambiaron (como SEBASTIÃN) estÃ¡n en `nombres_excluir`
- **reemplazador.py â€” _normalizar_guiones:** Nueva funciÃ³n que colapsa guiones dobles (`--` â†’ `-`, `- --` â†’ `- -`) y espacios dobles; se llama en `aplicar_reemplazos_docx` antes de `doc.save`
- **nueva-minuta-workspace.tsx â€” handleChange con cascada de gÃ©nero:** `PersonaCard` ahora tiene `handleChange` que al cambiar gÃ©nero auto-actualiza `nacionalidad` (via diccionario `GENTILICIOS_M_A_F`/`GENTILICIOS_F_A_M` de 25 gentilicios) y `estado_civil` (soltero/casado/divorciado/viudo â†” femeninos)

**Archivos creados/modificados:**
- `backend/app/modules/minuta/router.py` â€” gÃ©nero determinista, pares_genero, todos_nombres_doc combinado
- `backend/app/services/minuta/reemplazador.py` â€” `aplicar_reemplazos_por_contexto`, `aplicar_genero_contextual_docx`, `_normalizar_guiones`
- `frontend/components/minutas/nueva-minuta-workspace.tsx` â€” `GENTILICIOS_M_A_F`, `GENTILICIOS_F_A_M`, `handleChange` con cascada

**Pendientes para la prÃ³xima sesiÃ³n:**
1. **[CRÃTICO] Debug SEBASTIÃN persiste:** El fix `610a817` estÃ¡ en producciÃ³n pero el bug puede seguir. Agregar prints de debug en `aplicar_genero_contextual_docx` (imprimir `todos_nombres`, `otros`, y quÃ© pÃ¡rrafos se procesan), hacer deploy, generar minuta real, revisar logs Railway
2. **[MEDIA] Guiones dobles `-- -` sin resolver:** `_normalizar_guiones` existe pero no resuelve porque los guiones estÃ¡n partidos entre mÃºltiples runs. Corregir para que una el texto de todos los runs del pÃ¡rrafo antes de aplicar regex, o implementar soluciÃ³n EasyPro1 (tab stops + `[[--]]` â†’ `\t` en plantillas)
3. **[MEDIA] Concordancia de artÃ­culos** â€” ELâ†’LA, DELâ†’DE LA (pendiente de sesiÃ³n anterior)
4. **[BAJA] Alembic out-of-sync** â€” `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';` en Supabase producciÃ³n
5. **[BAJA] Grabar videos demo** â€” si SEBASTIÃN y guiones quedan resueltos, preparar caso demo para notarÃ­as

**Estado al cierre:**
- Backend: Railway operativo â€” commit `610a817` activo (3a59eb6 es force redeploy vacÃ­o)
- Frontend: Vercel operativo â€” easypronotarial.com, deploy esta noche
- BD producciÃ³n: operativa, alembic_version desincronizada (pendiente)
- Git: `reemplazador.py` y `nueva-minuta-workspace.tsx` modificados localmente sin commitear â€” se commitean en este cierre

---
## SesiÃ³n 2026-05-22

**Objetivo de la sesiÃ³n:** Conectar el motor de minutas con OnlyOffice (abrir el .docx generado directamente en el editor) e integrar concordancia de gÃ©nero al flujo de generaciÃ³n.

**Realizado:**
- AnÃ¡lisis completo del flujo existente de minutas (detector, reemplazador, concordancia, router, frontend) y del flujo de OnlyOffice en document_flow
- Backend router.py minuta: POST /generar ahora integra concordancia de gÃ©nero por persona (detecta cambio Mâ†”F, aplica reemplazos con palabra_completa=True), sube el .docx resultante a Supabase Storage en `minutas/notary_{id}/{uuid}_minuta.docx`, genera JWT firmado con storage_path y retorna JSON con `onlyoffice_path`
- Backend router.py minuta: 3 nuevos endpoints para servir el archivo al Document Server â€” GET /onlyoffice-config, GET /onlyoffice/file, POST /onlyoffice/callback (guarda versiÃ³n editada de vuelta en Supabase)
- concordancia.py: fix menor â€” `aplicar_cambios_concordancia_a_reemplazos` ahora incluye `"palabra_completa": True` para respetar lÃ­mites de palabra
- frontend/lib/minuta.ts: `generateMinuta` retorna `{ onlyoffice_path, filename }` en lugar de Blob; nueva funciÃ³n `getMinutaOnlyOfficeConfig(token)`; `sanitizeDatos()` limpia `\r\n\t\0` de strings antes de JSON.stringify (fix JSON malformado)
- frontend/components/minutas/nueva-minuta-workspace.tsx: `PersonaField` extraÃ­do a nivel de mÃ³dulo (fix bug foco perdido por componente anidado que se desmontaba en cada render); paso 3 navega con `router.push(onlyoffice_path)` en lugar de descargar blob
- frontend/app/(app)/dashboard/minutas/editor/[token]/page.tsx: nueva pÃ¡gina editor OnlyOffice para minutas â€” recibe JWT en URL, carga config desde `/api/v1/minuta/onlyoffice-config`, inicializa `DocEditor`
- frontend/lib/navigation.ts: entrada "Motor de Minutas" agregada al sidebar despuÃ©s de "Crear Minuta"
- frontend/next.config.mjs: `generateBuildId` con timestamp para forzar cache bust en Vercel
- DiagnÃ³stico de problema en Vercel deploy: Root Directory mal configurado â€” path duplicado `frontend/easypro2/frontend`. URL settings: https://vercel.com/cesar-giraldo-aristizabals-projects/easypro-notarial-2/settings

**Archivos creados/modificados:**
- `backend/app/modules/minuta/router.py` â€” generar con concordancia + Supabase + JWT + 3 endpoints OnlyOffice
- `backend/app/services/minuta/concordancia.py` â€” `palabra_completa: True` en reemplazos de concordancia
- `frontend/app/(app)/dashboard/minutas/editor/[token]/page.tsx` â€” nueva pÃ¡gina editor OnlyOffice para minutas
- `frontend/lib/minuta.ts` â€” generateMinuta retorna JSON, sanitizeDatos, getMinutaOnlyOfficeConfig
- `frontend/components/minutas/nueva-minuta-workspace.tsx` â€” PersonaField a nivel mÃ³dulo, paso 3 navega al editor
- `frontend/lib/navigation.ts` â€” entrada Motor de Minutas en sidebar
- `frontend/next.config.mjs` â€” generateBuildId para cache bust

**Pendientes para la prÃ³xima sesiÃ³n:**
1. **[CRÃTICO] Concordancia de artÃ­culos** â€” El motor cambia sustantivos (COMPRADORâ†’COMPRADORA) pero NO cambia artÃ­culos ni pronombres (ELâ†’LA, LOSâ†’LAS). Ajustar PROMPT_CONCORDANCIA en `concordancia.py`.
2. **[CRÃTICO] FÃ³rmulas compuestas** â€” Expresiones como "EL(LOS) DEUDORA(ES)" quedan mal al cambiar gÃ©nero. El prompt debe manejar estas fÃ³rmulas mixtas.
3. **[CRÃTICO] Alembic out-of-sync** â€” Ejecutar en Supabase: `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';`
4. **[MEDIA] Verificar menÃº lateral por rol** â€” "Motor de Minutas" estÃ¡ en navigation.ts, confirmar que aparece correctamente segÃºn permisos del usuario
5. **[MEDIA] Personas incompletas en anÃ¡lisis B2** â€” Algunos docs devuelven menos personas de las esperadas. Revisar chunking o prompt del detector
6. **[MEDIA] Caso B1 (plantilla en blanco)** â€” El detector clasifica B1 pero el formulario dinÃ¡mico es el mismo que B2. Pendiente diferenciar UX y prompt
7. **[BAJA] Reset contraseÃ±a** â€” No implementado
8. **[BAJA] Historial de minutas** â€” Guardar minutas generadas por notarÃ­a (estructura BD + UI)

**Estado al cierre:**
- Backend: Railway operativo â€” https://easypronotarial-2-production.up.railway.app
- Frontend: Vercel operativo â€” https://easypronotarial.com (deploy vÃ­a CLI `vercel --cwd frontend --prod`)
- BD producciÃ³n: operativa, alembic_version desincronizada (pendiente UPDATE manual)
- Git: Ã¡rbol limpio (solo uvicorn_start.log sin trackear)

**Deploy frontend (procedimiento correcto):**
```bash
cd c:\EasyProNotarial-2\easypro2
$env:NODE_OPTIONS="--use-system-ca"
vercel --cwd frontend --prod
```

---
## SesiÃ³n 2026-05-21

**Objetivo de la sesiÃ³n:** Integrar motor de anÃ¡lisis de minutas IA al backend y crear pantalla frontend de 3 pasos para subir, analizar y generar minutas.

**Realizado:**
- DocumentaciÃ³n inicial: SESSION.md operativo, AGENTS.md, protocolo iniciar-sesion y cerrar-sesion en .claude/commands/
- VerificaciÃ³n Supabase producciÃ³n: alembic_version en 20260420, act_catalog âœ… 11 registros, legal_entities âœ… 6 registros, columnas document_type/document_number âœ… aplicadas (fuera de alembic_version)
- Backend motor minutas: detector.py (GPT-4o-mini, modo B1/B2 automÃ¡tico), reemplazador.py (reemplazos preservando formato .docx), concordancia.py (concordancia de gÃ©nero con IA), utils_letras.py (nÃºmeros a letras notarial)
- Backend endpoints: POST /api/v1/minuta/analizar + POST /api/v1/minuta/generar registrados en api_router. Instalado num2words y python-multipart
- Fix SSL local: OPENAI_DISABLE_SSL_VERIFY=true en .env + _make_openai_client() en detector.py y concordancia.py
- Prueba real con jaggua_limpio.docx: B2 detectado, 4 personas, 2 valores, inmueble Caldas/Antioquia, 8 actos, $0.0052 USD, 30 segundos respuesta
- Frontend lib/minuta.ts: tipos TypeScript + analyzeMinuta() + generateMinuta() usando getToken()
- Frontend components/minutas/nueva-minuta-workspace.tsx: wizard 3 pasos (subir+analizar, revisar personas con campos pendientes en amarillo, generar+descargar)
- Frontend app/(app)/dashboard/minutas/nueva/page.tsx: ruta nueva en Next.js 15
- tailwind.config.ts: aliases semÃ¡nticos para CSS vars faltantes (muted, soft, panel-soft, panel-highlight, line-strong, etc.)
- Alembic desincronizado corregido: columnas 20260512 y 20260513 estÃ¡n en Supabase pero alembic_version no las registra. Pendiente UPDATE alembic_version.
- Comandos de sesiÃ³n: iniciar-sesion.md y cerrar-sesion.md en easypro2/.claude/commands/ (para el repo) y C:\EasyProNotarial-2\.claude\commands\ (para Claude Code)

**Archivos creados/modificados:**
- `backend/app/services/minuta/detector.py` â€” motor B1/B2 con GPT-4o-mini
- `backend/app/services/minuta/reemplazador.py` â€” reemplazos en .docx preservando formato
- `backend/app/services/minuta/concordancia.py` â€” concordancia de gÃ©nero con IA
- `backend/app/services/minuta/utils_letras.py` â€” nÃºmeros a letras formato notarial
- `backend/app/modules/minuta/router.py` â€” 2 endpoints FastAPI
- `backend/app/api/router.py` â€” registra minuta_router
- `backend/requirements.txt` â€” +num2words +python-multipart
- `backend/.env` â€” +OPENAI_DISABLE_SSL_VERIFY=true (solo desarrollo local, no commitear)
- `frontend/lib/minuta.ts` â€” tipos + funciones API multipart
- `frontend/components/minutas/nueva-minuta-workspace.tsx` â€” wizard 3 pasos completo
- `frontend/app/(app)/dashboard/minutas/nueva/page.tsx` â€” ruta nueva
- `frontend/tailwind.config.ts` â€” aliases semÃ¡nticos CSS vars
- `SESSION.md` â€” reescrito como documento operativo
- `AGENTS.md` â€” inventario de agentes del sistema
- `.claude/commands/iniciar-sesion.md` â€” protocolo arranque de sesiÃ³n
- `.claude/commands/cerrar-sesion.md` â€” protocolo cierre de sesiÃ³n

**Pendientes para la prÃ³xima sesiÃ³n:**
1. **Alembic out-of-sync en producciÃ³n** â€” Ejecutar `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';` en Supabase para sincronizar. Las migraciones YA estÃ¡n aplicadas pero alembic_version dice 20260420.
2. **Frontend minutas â€” integrar al menÃº lateral** â€” La ruta /dashboard/minutas/nueva existe pero no aparece en el sidebar de AppShell. Agregar entrada de navegaciÃ³n.
3. **Placeholders del dashboard** â€” /lotes, /ayuda, /configuracion muestran pÃ¡ginas vacÃ­as. Limpiar del menÃº o agregar contenido mÃ­nimo antes de demo.
4. **Personas incompletas en anÃ¡lisis** â€” jaggua_limpio.docx devolviÃ³ 4 personas cuando deberÃ­a tener mÃ¡s (compradores, banco, etc.). Investigar si es problema de contexto de GPT-4o-mini (110k chars) o del prompt.
5. **Reset de contraseÃ±a** â€” No existe. Usuarios no pueden cambiar su contraseÃ±a.

**Estado al cierre:**
- Backend: operativo local en puerto 8001, apuntando a Supabase producciÃ³n
- Frontend: build âœ…, dev server corriendo en 5179
- BD producciÃ³n: operativa, legal_entities y act_catalog con datos, alembic_version desincronizada
- Git: Ã¡rbol limpio (solo uvicorn_start.log sin trackear, no debe commitearse)

---

## Stack confirmado

| Capa | TecnologÃ­a |
|---|---|
| Backend | FastAPI 0.115 + SQLAlchemy 2.0 + Alembic + Uvicorn |
| Base de datos prod | PostgreSQL vÃ­a Supabase (egwdrdgtgmogcahhdtdy.supabase.co) |
| Base de datos local | SQLite (easypro2.db) |
| Frontend | Next.js 15.3 + React 19 + TypeScript + Tailwind CSS 3 |
| IA documental | OpenAI GPT-4o (Gari â€” generaciÃ³n .docx escrituras) |
| IA minutas | OpenAI GPT-4o-mini (detector B1/B2 + concordancia) |
| Storage | Supabase Storage (cases/case-{id}/draft/) |
| Despliegue frontend | Vercel â€” https://easypronotarial.com |
| Despliegue backend | Railway â€” https://easypronotarial-2-production.up.railway.app |
| Editor documentos | OnlyOffice â€” https://onlyoffice.easypronotarial.com |

---

## URLs de producciÃ³n / servicios

| Servicio | URL |
|---|---|
| Frontend producciÃ³n | https://easypronotarial.com |
| Backend producciÃ³n | https://easypronotarial-2-production.up.railway.app |
| Supabase BD | https://egwdrdgtgmogcahhdtdy.supabase.co |
| OnlyOffice | https://onlyoffice.easypronotarial.com |
| Backend local | http://127.0.0.1:8001 |
| Frontend local | http://127.0.0.1:5179 |

---

## Estado git

Repositorio en `c:\EasyProNotarial-2\easypro2\` â€” rama `main`.
Remoto: https://github.com/cesargiraldoa/EasyProNotarial-2.git

---

## Migraciones Alembic â€” estado real en Supabase

| MigraciÃ³n | Schema real | alembic_version |
|---|---|---|
| base | âœ… aplicada | parte del head |
| 20260418_add_role_permissions_table | âœ… tabla existe | parte del head |
| 20260419_add_legal_entities | âœ… tabla existe, 6 registros | parte del head |
| 20260420_add_act_catalog | âœ… 11 registros | âœ… HEAD registrado |
| 20260512_add_user_identification | âœ… columnas existen en users | âŒ no registrada |
| 20260513_promote_legacy_notary_to_titular | desconocido (data migration) | âŒ no registrada |

**ACCIÃ“N PENDIENTE:** Ejecutar en Supabase:
```sql
UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';
```

---

## Lo que existe y funciona hoy

### Backend â€” endpoints operativos (79 rutas totales)

| MÃ³dulo | Rutas | Estado |
|---|---|---|
| Auth | POST /login, GET /me | âœ… |
| NotarÃ­as | GET /notaries, GET /notaries/{id} | âœ… |
| Usuarios | CRUD + roles + permisos | âœ… |
| Plantillas | GET/PUT templates, 8 plantillas activas | âœ… |
| Personas naturales | GET/POST /persons + lookup | âœ… |
| Entidades jurÃ­dicas | GET/POST /legal-entities + apoderados | âœ… |
| Flujo documental | Wizard 5 pasos + Gari .docx | âœ… |
| Dashboard | GET /dashboard KPIs | âœ… |
| CatÃ¡logo de actos | act_catalog | âœ… |
| **Motor minutas** | POST /api/v1/minuta/analizar | âœ… nuevo |
| **Motor minutas** | POST /api/v1/minuta/generar | âœ… nuevo |

### Frontend â€” rutas operativas

| Ruta | Estado |
|---|---|
| /login | âœ… |
| /dashboard | âœ… KPIs |
| /dashboard/casos | âœ… |
| /dashboard/casos/crear | âœ… Wizard 5 pasos |
| /dashboard/casos/[caseId] | âœ… |
| /dashboard/notarias | âœ… |
| /dashboard/comercial | âœ… CRM |
| /dashboard/usuarios | âœ… |
| /dashboard/roles | âœ… |
| /dashboard/perfil | âœ… |
| /dashboard/actos-plantillas | âœ… |
| /dashboard/system-status | âœ… |
| **/dashboard/minutas/nueva** | âœ… nuevo â€” wizard 3 pasos |
| /dashboard/lotes | âš ï¸ placeholder vacÃ­o |
| /dashboard/ayuda | âš ï¸ placeholder vacÃ­o |
| /dashboard/configuracion | âš ï¸ placeholder vacÃ­o |

### Agente Gari (escrituras)
- Motor: GPT-4o, max_tokens=16000, temperature=0.2
- ACTOS_POR_VARIANTE hardcodeado en gari_service.py

### Motor Minutas (nuevo)
- Detector B1/B2: GPT-4o-mini, temperature=0.1, max_tokens=8000
- Concordancia: GPT-4o-mini, temperature=0.1, max_tokens=4000
- SSL local: OPENAI_DISABLE_SSL_VERIFY=true en .env (no commitear)

### Entidades jurÃ­dicas en Supabase (6 â€” seed aplicado)
Fiduciaria Bancolombia, Constructora Contex S.A.S. BIC, Bancolombia S.A.,
Banco Davivienda, Fondo Nacional del Ahorro, Banco de BogotÃ¡

---

## Pendientes crÃ­ticos

### Para prÃ³xima sesiÃ³n
1. **Alembic out-of-sync** â€” UPDATE alembic_version en Supabase (ver arriba)
2. **MenÃº lateral** â€” Agregar /dashboard/minutas/nueva al sidebar de AppShell
3. **Placeholders dashboard** â€” /lotes, /ayuda, /configuracion vacÃ­os â€” limpiar antes de demo
4. **Personas incompletas en anÃ¡lisis** â€” jaggua devolviÃ³ 4/~10 personas. Revisar chunking o prompt
5. **Reset contraseÃ±a** â€” No implementado

### Deuda tÃ©cnica
6. ACTOS_POR_VARIANTE hardcodeado â†’ mover a BD
7. BÃºsqueda entidades con q corta retorna todo (falta filtro mÃ­nimo de chars)
8. MÃ³dulo facturaciÃ³n electrÃ³nica â†’ diseÃ±ado, cero cÃ³digo
9. MÃ³dulo nÃ³mina electrÃ³nica â†’ diseÃ±ado, cero cÃ³digo
10. Provider Adapter (Plemsi) â†’ pendiente cotizaciÃ³n

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
# â†’ http://127.0.0.1:5179

# Verificar migraciones Alembic (contra producciÃ³n)
cd c:\EasyProNotarial-2\easypro2\backend
alembic current
alembic heads
```

**NOTA:** .env del backend apunta a Supabase (ENVIRONMENT=production).
Para desarrollo local con SQLite: cambiar DATABASE_URL a `sqlite:///./easypro2.db`.

---

## Reglas tÃ©cnicas del proyecto

1. **MultinotarÃ­a estricto** â€” Toda consulta filtra por notary_id. Nunca exponer datos cruzados.
2. **Roles** â€” Validar con require_roles() / has_role(). Roles: super_admin, admin_notary, notary, approver, protocolist, client.
3. **Provider Adapter** â€” FacturaciÃ³n/nÃ³mina NUNCA directo a Plemsi. Siempre vÃ­a ElectronicDocumentProvider.
4. **Sin secretos en cÃ³digo** â€” Solo en .env (excluido de git).
5. **Intervinientes dinÃ¡micos** â€” N compradores + N entidades. template_required_roles es obsoleto.
6. **Snapshot JSON** â€” CaseParticipant guarda snapshot en momento de guardado.
7. **Alembic obligatorio** â€” Todo schema change vÃ­a migraciÃ³n YYYYMMDD_descripcion.py.
8. **CORS** â€” FlexibleCORSMiddleware. Agregar dominios en _load_allowed_origins().
9. **Gari** â€” No cambiar max_tokens ni temperature sin revisar calidad de escrituras.
10. **Supabase Storage** â€” Archivos en cases/case-{id}/draft/. No mover sin actualizar gari_service.py.
11. **SSL local** â€” OPENAI_DISABLE_SSL_VERIFY=true solo en .env local. NO en Railway.

---

## MÃ³dulos diseÃ±ados â€” pendientes de implementar

### FacturaciÃ³n ElectrÃ³nica
- DecisiÃ³n: proveedor intermediario (Plemsi evaluado como principal)
- Arquitectura: Provider Adapter desacoplado
- Estado: **Solo diseÃ±o. Cero cÃ³digo.**

### NÃ³mina ElectrÃ³nica
- Mismo enfoque que facturaciÃ³n
- Estado: **Solo diseÃ±o. Cero cÃ³digo.**

-------------------------------------------------------
## Sesión 2026-06-08 — MVP minutas marcadas sin IA y control OnlyOffice

**Objetivo de la sesión:** Consolidar en producción el nuevo flujo MVP de minutas marcadas sin IA, validar apertura en OnlyOffice y cerrar el bloqueo de descarga en Word/formatos editables.

**Realizado:**
- **Merge a `main` confirmado:** PR #91 mergeado desde `feature/mvp-docx-sin-ia`.
  - Commit merge: `a3fb85a`
  - Commit funcional: `175f8a3 feat(minutas): add deterministic marked template flow`
- **Backend Railway actualizado:** deploy activo y respondiendo correctamente.
- **Frontend Vercel actualizado:** redeploy manual realizado y producción quedó sirviendo el nuevo frontend.
- **Nuevo flujo de minutas marcadas funcionando en producción:**
  - subir DOCX marcado
  - detectar campos marcados sin IA
  - diligenciar formulario dinámico
  - generar documento
  - abrir en OnlyOffice
- **OnlyOffice validado en producción:** el documento generado abre correctamente en el editor.
- **Bloqueo de descarga en Word y otros formatos:** agregado `permissions.download = false` en `GET /api/v1/minuta/onlyoffice-config`.
  - Commit: `310599e fix(onlyoffice): disable document downloads`
  - Validado en producción: ya no aparece `Archivo -> Descargar como`.
- **Seguridad documental mejorada:** se bloqueó descarga directa desde el menú nativo de OnlyOffice para DOCX, ODT, RTF, TXT, HTML, etc.
- **Mensaje operativo para el equipo preparado:** Will debe probar mañana con documentos reales y reportar errores/campos faltantes/formato.

**Archivos modificados principales:**
- `backend/app/modules/minuta/router.py`
- `backend/app/modules/minutas/router.py`
- `backend/app/services/minuta/marked_template_detector.py`
- `backend/app/services/minuta/marked_template_generator.py`
- `backend/app/schemas/minuta.py`
- `frontend/components/minutas/nueva-minuta-workspace.tsx`
- `frontend/lib/minuta.ts`
- `frontend/lib/listas-notariales.ts`
- `frontend/app/layout.tsx`
- `frontend/package.json`
- `docs/dev/local-start.md`
- `scripts/dev/start-backend-local.ps1`
- `scripts/dev/start-frontend-local.ps1`
- `scripts/dev/start-easypro-local.ps1`
- `scripts/dev/check-frontend-css.ps1`

**Pendientes para la próxima sesión:**
1. **[CRÍTICO] Guiones / separadores `[[--]]`:** corregirlos al estilo EasyPro 1, usando tabulación/líder visual correcto y no texto bruto.
2. **[ALTA] Pruebas de Will:** recibir resultados con documentos reales: minutas largas, varios compradores, hipotecas, compraventas y variaciones notariales.
3. **[ALTA] Ajustar campos no detectados o mal agrupados** según pruebas reales.
4. **[MEDIA] Exportar PDF propio de EasyPro:** si se requiere PDF, implementarlo como botón propio controlado por backend, no desde menú nativo de OnlyOffice.
5. **[MEDIA] Revisar guardado/callback OnlyOffice** con documentos generados en producción.
6. **[BAJA] Evaluar si `SESSION.md` debe quedar fuera de deploys automáticos para evitar builds innecesarios por documentación.**

**Estado al cierre:**
- Producción operativa.
- Railway backend actualizado.
- Vercel frontend actualizado.
- Flujo MVP marcado sin IA validado hasta OnlyOffice.
- Descarga Word/otros formatos bloqueada en OnlyOffice.
- Git local quedó limpio después del commit `310599e`.
- Próximo foco: guiones `[[--]]` + feedback de pruebas reales.
