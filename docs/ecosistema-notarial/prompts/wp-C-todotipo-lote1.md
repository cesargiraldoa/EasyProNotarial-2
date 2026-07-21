# Prompt Codex — Bloque C (Lote 1): Compraventa de todo tipo — varios inmuebles, folio y encadenamientos

> Pegar en Codex. Contexto: `docs/ecosistema-notarial/plan-port-software.md`, `mapa-situaciones.md` (21 dimensiones), `normograma-compraventa.md`. **Un PR** contra `claude/notaria16-escritura-asistida-fsro6n`.

---

## ⚠ Antes de empezar
1. `git fetch origin` y **basa el trabajo en `claude/notaria16-escritura-asistida-fsro6n`** (WP-1..WP-5 + Bloques A/B). Backend `backend/`, frontend `frontend/`.
2. **Esto es construcción NUEVA** (no está en el HTML congelado). Por tanto: **no hay golden fixtures nuevos**; escribe **tests propios**. Los **golden tests de los 3 actos base deben seguir verdes** (no rompas compraventa/hipoteca/cancelación existentes).
3. Fidelidad: apóyate en `docs/ecosistema-notarial/mapa-situaciones.md` (dimensiones 7, 10, 21) y en `normograma-compraventa.md`. Política **demo=real**: cada rama nueva trae su clausulado, su regla de cumplimiento y su cita de norma.

## Objetivo
Ampliar la compraventa con las 3 situaciones comunes que aún faltan, como **ramas activables** del motor + formulario + corpus:

### 1. Varios inmuebles en un mismo instrumento (dim. 10)
- Estado/motor: permitir **N inmuebles** (hoy es 1). Cada inmueble con su descripción/matrícula/linderos/catastral/NUPRE; la cláusula de objeto los enumera.
- Cumplimiento: cada inmueble exige matrícula+linderos (regla BLOCK por inmueble).

### 2. Estado del folio (dim. 10)
- Rama activable: **segregado / englobe / desenglobe / mayor extensión / falsa tradición**. Cada uno añade su párrafo y su advertencia (WARN) con cita (Ley 1579/2012; falsa tradición → Ley 1561/2012).

### 3. Encadenamientos en un mismo instrumento (dim. 21)
- Permitir apilar sobre la compraventa: **+ cancelación de hipoteca previa**, **+ cancelación de patrimonio de familia**, **+ afectación a vivienda familiar**. Reutiliza el clausulado que ya tenemos (cancelación de hipoteca es un acto existente; afectación ya se menciona en Ley 258). El documento los redacta como comparecencias/cláusulas sucesivas, en el orden canónico del `mapa`/`capa-notaria16`.

## Corpus (añadir, sin borrar)
- En `corpus-juridico/`: nuevas `legal_regla` (varios inmuebles; falsa tradición; encadenamientos) y `legal_clausula` para los párrafos nuevos, con su `norma_slug` y vigencia. Si falta alguna norma (p. ej. **Ley 1561/2012** saneamiento/falsa tradición), añádela a `normas.json` con su estado/confianza (marca `baja` si no verificada). Actualiza el seed.

## Motor (frontend/lib/motor-escritura)
- Extiende `CaseState` y `renderEscritura`/`evaluar`/`liquidar` para soportar N inmuebles, estado del folio y los encadenamientos. **Retrocompatible**: con 1 inmueble y sin ramas nuevas, el output es idéntico al actual (golden verdes).
- Añade **tests nuevos** para cada rama (no golden): p. ej. 2 inmuebles → ambos aparecen; folio segregado → párrafo presente; encadenar cancelación → su cláusula presente.

## Formulario / UI
- En `escritura-form.tsx`: agregar/quitar inmuebles; selector de estado del folio; casillas de encadenamiento (cancelación previa / patrimonio / afectación) con sus campos.

## Criterios de aceptación
1. Se pueden capturar **varios inmuebles**; el documento y el cumplimiento los reflejan (matrícula/linderos exigidos por inmueble).
2. El **estado del folio** añade su párrafo + advertencia con cita.
3. Los **encadenamientos** se apilan en el documento en el orden correcto.
4. **Golden de los 3 actos base: verdes.** Reglas server-side (Bloque A) siguen operando.
5. Backend + frontend con tests nuevos en verde; `tsc`/build OK.

## Restricciones
- No tocar el HTML congelado. Corpus se **amplía**, no se reescribe. Base correcta, sin `easypro2/`.
- Un PR; descripción con las ramas añadidas, normas nuevas y resultados de tests.
