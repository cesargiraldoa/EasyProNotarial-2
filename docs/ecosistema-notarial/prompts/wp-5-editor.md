# Prompt Codex — WP-5: Editor propio (modo Redacción)

> Pegar en Codex. Contexto: `docs/ecosistema-notarial/plan-port-software.md`, `adr-escritura-asistida.md`. Al terminar, **un PR** contra `claude/notaria16-escritura-asistida-fsro6n`.

---

## ⚠ Antes de empezar
1. `git fetch origin` y **basa el trabajo en `claude/notaria16-escritura-asistida-fsro6n`** (trae WP-1..WP-4 mergeados). Frontend en `frontend/` (NO `easypro2/`).
2. **Spec del editor:** el HTML congelado `docs/ecosistema-notarial/prototipos/escritura-asistida.html`, **segundo IIFE** ("Motor de redacción", ~líneas 1235–1530) y su toolbar/paneles en el HTML (`data-act="vincular|desvincular|comentar|track"`, paleta `.hl-sw`, panel `#comentarios`). NO modifiques el HTML.
3. **Alcance: el modo Redacción.** Extiende el workspace de WP-4 (no lo rehagas); Captura ya funciona.

## Rol y objetivo
Eres ingeniero frontend senior (Next.js 15 / React 19 / Tailwind). Porta el **editor propio** del HTML al workspace de escritura: un `contenteditable` con toolbar que permite editar la escritura a mano, con vincular/desvincular, comentarios, resaltado, control de cambios, biblioteca insertable y exportar. **No OnlyOffice.**

## Integración con lo existente
- `frontend/components/escritura/escritura-workspace.tsx` (WP-4) ya tiene `acto`, `state`, `resultado = generar(acto, state)`, `EscrituraPreview`. Añade un **toggle de modo Captura ↔ Redacción**.
- En **Captura**: como ahora (React rinde `generar().html`).
- En **Redacción**: el HTML de `generar().html` se vuelca UNA vez a un `contenteditable`; **React deja de re-renderizar ese nodo** (el DOM editado es la fuente de verdad). Manipula por `ref` + Selection/Range API — no re-render de React sobre el contenido editado.

## Funciones a portar (del 2.º IIFE del HTML — checklist)
- [ ] **Toggle de modo** Captura/Redacción (al entrar a Redacción, vuelca el `html` actual; al volver a Captura, advierte que se perderán ediciones no exportadas o guárdalas).
- [ ] **Vincular / desvincular**: envolver la selección como `span.campo[data-field]`; editar un campo vinculado **cascadea** a todas sus apariciones (porta la lógica posicional).
- [ ] **Comentarios estilo Word**: anclar a la selección, panel lateral (`#comentarios`) con cita + texto + resolver/eliminar.
- [ ] **Resaltado multicolor**: paleta de 5 colores + quitar (`span.hl`).
- [ ] **Control de cambios**: inserciones verde (`ins.track`) / borrados rojo (`del.track`), aceptar/rechazar todo.
- [ ] **Biblioteca insertable** en el cursor, según el acto (porta `BIBLIO`/`BIBLIO_CANC` del HTML a un módulo del front; _follow-up: cablear al servicio `biblioteca_motor` vía API_).
- [ ] **Guiones de relleno**: colapsados en edición, se materializan al exportar (porta `fillLeaders`).
- [ ] **Preservar la selección** al pulsar el toolbar (`mousedown`→`preventDefault`).

## Exportar / persistir (reutiliza WP-3)
- **Exportar Word (.docx):** usa el endpoint de WP-3 `POST /escritura/cases/{id}/documento` con el **HTML editado** (materializando guiones) → versión DOCX. Respeta el 409 de bloqueantes.
- **Exportar PDF:** impresión del `contenteditable` con print-CSS A4 (como el HTML), o `convert_docx_to_pdf` del backend si es directo.
- **Guardar borrador de Redacción:** persiste el HTML editado (vía el mismo `POST documento` como versión, o un `PUT` que lo guarde). Que al recargar se recupere la última versión.

## Criterios de aceptación
1. Toggle Captura↔Redacción; en Redacción se edita a mano sin que React pise las ediciones.
2. Vincular + cascada, comentarios (anclar/resolver), resaltado (poner/quitar), control de cambios (aceptar/rechazar), biblioteca (insertar en cursor) — todas funcionan como en el HTML.
3. Exportar Word crea una versión (DOCX) vía WP-3; con bloqueantes muestra 409.
4. No se rompe la Captura de WP-4 ni los golden tests del motor.
5. Compila (`tsc`/build) sin `any` gratuitos; sin tocar HTML/corpus/backend/motor.

## Pruebas
- Test(s) de componente (Vitest + happy-dom, como en WP-4): entrar a Redacción → editar un campo vinculado → cascada visible; insertar una cláusula de biblioteca → aparece en el documento; aplicar resaltado/comentario → nodo con la clase/ancla correcta.

## Restricciones
- Reutiliza el motor, la API (WP-3) y el workspace (WP-4). No dupliques generación ni liquidación.
- Un solo PR, base correcta, rutas en `frontend/`. Descripción con checklist de funciones portadas y resultado de pruebas.
- **Ojo con React + contenteditable:** el contenido editado es *uncontrolled*; no lo vuelvas a montar desde estado de React mientras se edita.
