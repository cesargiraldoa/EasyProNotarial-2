# Prompt Codex — WP-4: UI de Captura (formulario + preview en vivo)

> Pegar en Codex. Contexto: `docs/ecosistema-notarial/plan-port-software.md` y `adr-escritura-asistida.md`. Al terminar, **un PR** contra `claude/notaria16-escritura-asistida-fsro6n`.

---

## ⚠ Antes de empezar
1. `git fetch origin` y **basa el trabajo en `claude/notaria16-escritura-asistida-fsro6n`** (trae WP-1 corpus, WP-2 motor, WP-3 API mergeados). Frontend en **`frontend/`** en la raíz (NO `easypro2/`).
2. **Spec visual y de comportamiento:** el HTML congelado `docs/ecosistema-notarial/prototipos/escritura-asistida.html` (modo **Captura**). NO lo modifiques.
3. **Alcance de este WP: solo el modo Captura.** El editor (vincular/comentarios/resaltado/control de cambios) es WP-5 — NO lo hagas aquí.

## Rol y objetivo
Eres ingeniero frontend senior (Next.js 15 App Router, React 19, TailwindCSS, lucide-react). Construye la **UI de Captura** de la escritura asistida dentro del software, reutilizando el **motor TS** (WP-2) y la **API** (WP-3).

## Piezas a REUTILIZAR
- **Motor:** `@/lib/motor-escritura` → `generar(acto, state)`, `defaults`, tipos `CaseState`, `ActoCode`, y helpers (`money`, etc.). El preview y los paneles salen de `generar(...)`.
- **API base:** patrón de `@/lib/api.ts` (token vía `@/lib/auth`, cookie `easypro2_session`). Crea `@/lib/api-escritura.ts` siguiendo ese patrón.
- **Convenciones de workspace:** mira `frontend/components/biblioteca/biblioteca-workspace.tsx` (`"use client"`, hooks, estados de loading/error, iconos lucide, Tailwind).

## Entregables

### 1. Cliente de API — `frontend/lib/api-escritura.ts`
Funciones tipadas sobre el fetch base:
- `getCorpus(acto, fecha?)` → `GET /escritura/corpus`.
- `getEscrituraState(caseId)` → `GET /escritura/cases/{caseId}`.
- `saveEscrituraState(caseId, acto, state)` → `PUT /escritura/cases/{caseId}`.
- `generarDocumento(caseId, {acto, html, cumplimiento_bloqueantes, filename?})` → `POST /escritura/cases/{caseId}/documento`.

### 2. Componentes — `frontend/components/escritura/`
- `escritura-workspace.tsx` (`"use client"`): orquesta todo.
  - **Lanzador** "Elige el acto" (3 tarjetas: Compraventa · Compraventa+Hipoteca · Cancelación de hipoteca) — como en el HTML.
  - Al elegir acto: carga estado con `getEscrituraState(caseId)`; si viene vacío, usa `defaults[acto]`.
  - **Layout de 3 columnas** (como el HTML): formulario (izq) · escritura en vivo (centro) · cumplimiento + liquidación (der).
- `escritura-form.tsx`: formulario controlado que edita el objeto `CaseState`. **Porta los campos del HTML congelado** (acto, partes con agregar/quitar y N intervinientes, inmueble, título, precio, otorgamiento; y para cancelación sus campos propios). Replica el comportamiento: formato de **miles/centavos** en dinero, selects de **género (4 categorías)** y estado civil, cascada (cada cambio re-renderiza el preview).
- `escritura-preview.tsx`: renderiza `generar(acto, state).html` (via `dangerouslySetInnerHTML`) con un stylesheet que **porte los estilos del documento** del HTML (`.sheet`, `.cl`, `.para`, `.clh`, `.calif`, `.cite`, `.sech`, etc.) en un CSS module `escritura-preview.module.css`. Los guiones de relleno (`.fill`) se ocultan en el preview (son concern de impresión → WP-5/PDF).
- `cumplimiento-panel.tsx` y `liquidacion-panel.tsx`: rinden `resultado.cumplimiento` (tiles + items) y `resultado.liquidacionHtml`.
- Barra superior con **Guardar** (`saveEscrituraState`) y **Generar documento** (`generarDocumento` con `html` del motor + `cumplimiento.tiles.bloqueante`); si la API responde **409**, muestra "hay bloqueantes por resolver" y no descarga; si OK, ofrece el enlace/descarga de la versión.

### 3. Ruta — `frontend/app/(app)/dashboard/casos/[caseId]/escritura/page.tsx`
Monta `<EscrituraWorkspace caseId={...} />`. Sigue el patrón de las rutas existentes de `casos/[caseId]`.

## Criterios de aceptación
1. En `/dashboard/casos/{id}/escritura` se elige el acto y se captura; **la escritura, el cumplimiento y la liquidación se actualizan en vivo** desde el motor.
2. Los 3 actos funcionan (compraventa, hipoteca, cancelación) con sus formularios.
3. **Guardar** persiste (`PUT`) y al recargar se recupera el estado (`GET`).
4. **Generar documento** crea la versión (descarga/enlace); con bloqueantes muestra el 409 sin generar.
5. El preview se ve fiel al HTML (mismos estilos de documento). No se implementa el editor (eso es WP-5).
6. Compila con el TS/lint del repo; sin `any` gratuitos.

## Pruebas
- Al menos un test de componente (React Testing Library o el runner del repo) del `escritura-workspace`: elegir acto → el preview contiene una cláusula esperada; cambiar un campo → el preview refleja el cambio. (Si el repo no tiene setup de test de componentes, agrega uno mínimo con vitest + @testing-library/react como devDeps.)

## Restricciones
- **Solo Captura.** Sin editor, sin comentarios/track-changes (WP-5).
- Reutiliza el motor y la API; no dupliques la lógica de render ni de liquidación.
- Un solo PR, base correcta, rutas en `frontend/`. Descripción con capturas o pasos para probar y resultado de las pruebas.
