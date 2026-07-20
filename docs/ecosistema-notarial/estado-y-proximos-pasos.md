# Estado y próximos pasos — Ecosistema Notarial (punto de retomar)

> **Documento vivo.** Es lo primero que se lee al retomar. La continuidad NO depende de la memoria del asistente (cada sesión arranca en limpio): depende de este repo. Al empezar una sesión, leer: este archivo → `README.md` → `decisiones-diseno.md` → `normograma-compraventa.md` → `mapa-situaciones.md`, y abrir los prototipos.

_Última actualización: sesión del 2026-07-20._

## Dónde vamos (una línea)
Acto piloto **compraventa** validado en el sandbox (wizard de alta fidelidad + editor del protocolista). Siguiente: arreglos menores, extracción del corpus de la Notaría 16, y arrancar el 2.º acto (hipoteca).

## Hecho hasta hoy (todo en la rama `claude/github-integration-gl79ne`)
- **Wizard de compraventa** (`prototipos/wizard-compraventa.html`), pieza principal, con:
  - N intervinientes (natural/jurídica, cuota proindiviso), **tipo de documento** como selector (no se asume C.C.).
  - Bloque completo de **otorgamiento y firmas** (4 fases art. 13) y **ficha de firma estilo Notaría 16**.
  - **Datos de firma por persona** como campos (dirección, teléfono, correo, ocupación, notif. electrónicas, PEP), **testigos** y **firmante a ruego** con ficha completa.
  - **Fecha de otorgamiento** con selector → texto notarial (con apócope: un/veintiún/treinta y un día(s)).
  - **Título de adquisición** estructurado (número + fecha + notaría → texto).
  - **Número de hoja de papel notarial** + constancia.
  - Cumplimiento en vivo + liquidación 2026 + popups de norma + resaltado en cascada.
- **Editor del protocolista** (`prototipos/editor-vinculado.html`), POC: texto libre tipo Word + **campos vinculados en cascada** + **vincular/desvincular selección** + **biblioteca de cláusulas** + **control de cambios en rojo** (aceptar/rechazar). Modelo OnlyOffice.
- Documentación: `README.md`, `decisiones-diseno.md` (10 decisiones), `normograma-compraventa.md` (18 normas), `mapa-situaciones.md` (~320 situaciones).
- **Corpus Notaría 16 analizado** (sesión 2026-07-20): `corpus-notaria16/inventario.md` (40 docs, 5 protocolistas) + `corpus-notaria16/capa-notaria16-compraventa.md` (biblioteca de cláusulas, orden canónico, notas 1–8, ficha de firma, **clasificación en dos capas** por-ley vs estilo, propuesta de estándar único, e irregularidades detectadas que validan el pitch). Analizados 13 docs (4 compraventa + 9 compraventa/hipoteca); pendientes de extraer los otros 27 (cancelaciones, donaciones, leasing, sucesión, aporte, liquidación SC).

## Pendientes inmediatos (arreglos)
1. ✅ **RESUELTO (2026-07-20) — Concordancia de género.** Añadido campo **género** (M/F) por persona natural en el formulario (`partyCard`), en el modelo (`nueva()` + seed) y propagado en `pers()` a "identificad{o/a}" y "domiciliad{o/a}", y en `labelEstado(e,genero)` al estado civil (solter{o/a}, casad{o/a}, divorciad{o/a}, viud{o/a}); la ficha de firma también concuerda el estado civil. Verificado en navegador (Playwright): Rodrigo→M, Marta→F, Laura→F correctos + toggle en vivo.
2. ✅ **RESUELTO (2026-07-20) — Guiones de relleno.** `.fill` ahora es un line-leader que rellena la línea hasta el margen derecho: CSS `inline-block; overflow:hidden; white-space:nowrap` + `fillLeaders()` que mide el espacio restante de la última línea y ajusta el ancho; recalcula en `resize`. Verificado: 17-18/18 spans rellenan según el ancho.
3. **One-pager Hoy vs. Ecosistema** — DESCARTADO por ahora (sin desgaste). No retomar salvo que se pida.

## Próximas tareas (en orden sugerido)
1. **Extraer el corpus de la Notaría 16** (35 documentos, 5 protocolistas, en `uploads/.../notaria16/`). Producir la **capa por notaría**: biblioteca de cláusulas, orden de los actos, notas y ficha de firma. **Clasificar cada cláusula/nota en dos capas**: _por ley_ (→ normograma compartido) vs _estilo/orden_ (→ capa Notaría 16). Detectar variaciones entre protocolistas y proponer estándar único.
   - Actos vistos en el corpus: compraventa, venta de nuda propiedad, compraventa+hipoteca, hipoteca, cancelación de hipoteca, cancelación de patrimonio de familia, donación, insinuación+donación, sucesión, aporte a sociedad, liquidación soc. conyugal/renuncia a gananciales, leasing, minutas semilla (vivienda/leasing).
2. **Paso 2 — Hipoteca** (2.º acto): normograma → árbol → wizard. Probar el **encadenamiento compraventa + hipoteca** de verdad.
3. **Conectar editor ↔ wizard**: el wizard genera el borrador con campos → se abre en el editor para rematar (texto libre, biblioteca, vincular, rojo).
4. **Captura por extracción** (decisión 10): prototipar la extracción de **linderos** desde una escritura registrada (tenemos el texto de las minutas de la 16) que **prellena** el campo con resaltado "por validar". Luego cédula (PDF417) y voz.
5. **Port al software real** (cuando se dé el OK): tablas `norma`/`clausula`/`regla`, servicios FastAPI en Gari, frontend Next.js + OnlyOffice.

## Decisiones/insights clave (para no re-litigar)
- **Tipo de acto = raíz del árbol.** Escogerlo carga {normograma + biblioteca + árbol + orden}. NO es una plantilla fija (eso se abandonó); son **reglas + cláusulas**. Casi nunca es un solo acto: se **encadenan** (compraventa+hipoteca, +cancelación, +afectación).
- **Dos capas:** _mínimos obligatorios por ley_ (normograma, compartido, el motor los EXIGE vía cumplimiento: obligatoria/bloqueante) + _orden y estilo_ (por notaría). La notaría no puede quitar un mínimo legal; solo ordenarlo/redactarlo.
- **Captura por extracción → validación → cascada** (decisión 10): no digitar lo que se puede leer (linderos de la escritura registrada, cédula por PDF417, voz para prosa). Distinto de la marcación de campos (abandonada): aquí se extrae un dato conocido a un campo con nombre, con validación humana.
- **Comparación Hoy vs. Ecosistema** (dolores reales de la 16 y la 1, jul-2026): hoy reutilizan una escritura vieja parecida y la editan (arrastra datos del cliente anterior, errores de copy-paste, cláusulas que sobran/faltan; revisión difícil; cada protocolista su formato). Nuestra respuesta: arrancar limpio desde datos+reglas, digitar poco por cascada, red de cumplimiento aunque no haya jurídico, biblioteca por notaría como estándar sin rigidez.

## Guardado / continuidad
- **Git**: rama `claude/github-integration-gl79ne` (todo pusheado).
- **Artifacts** (persisten fuera del contenedor): índice del sandbox, wizard, normograma, mapa, árbol, demo, minuta-banco-slots, editor vinculado. URLs en el índice.
- **Corpus Notaría 16**: en `~/.claude/uploads/.../notaria16/` (efímero — si se pierde, el usuario lo vuelve a subir).
