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
1. ✅ **RESUELTO (2026-07-20) — Concordancia de género (4 categorías legales).** Campo **género — componente sexo** con las **4 categorías del Decreto 0732 de 2026** (Sent. T-033/2022): Femenino, Masculino, No Binario, Transgénero. Propagado por `genEnding()` (M→o · F→a · NB/T→e, lenguaje incluyente) a "identificad{o/a/e}", "domiciliad{o/a/e}" y estado civil (`labelEstado(e,genero)`); ficha de firma concuerda. Añadido al normograma. Verificado en navegador: 4/4 categorías + toggle en vivo.
2. ✅ **RESUELTO (2026-07-20) — Guiones de relleno.** `.fill` ahora es un line-leader que rellena la línea hasta el margen derecho: CSS `inline-block; overflow:hidden; white-space:nowrap` + `fillLeaders()` que mide el espacio restante de la última línea y ajusta el ancho; recalcula en `resize`. Verificado: 17-18/18 spans rellenan según el ancho.
3. **One-pager Hoy vs. Ecosistema** — DESCARTADO por ahora (sin desgaste). No retomar salvo que se pida.

## Próximas tareas (en orden sugerido)
1. **Extraer el corpus de la Notaría 16** (35 documentos, 5 protocolistas, en `uploads/.../notaria16/`). Producir la **capa por notaría**: biblioteca de cláusulas, orden de los actos, notas y ficha de firma. **Clasificar cada cláusula/nota en dos capas**: _por ley_ (→ normograma compartido) vs _estilo/orden_ (→ capa Notaría 16). Detectar variaciones entre protocolistas y proponer estándar único.
   - Actos vistos en el corpus: compraventa, venta de nuda propiedad, compraventa+hipoteca, hipoteca, cancelación de hipoteca, cancelación de patrimonio de familia, donación, insinuación+donación, sucesión, aporte a sociedad, liquidación soc. conyugal/renuncia a gananciales, leasing, minutas semilla (vivienda/leasing).
2. ✅ **RESUELTO (2026-07-20) — Paso 2 — Hipoteca (2.º acto).** Implementado el **encadenamiento compraventa + hipoteca** completo en el wizard, con fidelidad al corpus real de la 16: 12 cláusulas de hipoteca (constitución, solidaridad, título del hipotecante, obligaciones garantizadas con monto/plazo/cuotas, valor del acto, declaraciones, seguros, extinción del plazo, vigencia/novación, cesión, gastos), **comparecencia y aceptación del acreedor** (apoderado del banco), y ratificación Ley 258. Nuevos campos de formulario: plazo, cuotas, apoderado del banco, poder E.P., avalúo catastral, NUPRE. Verificado en navegador (con y sin crédito). _Pendiente futuro: normograma/árbol dedicados de hipoteca como acto raíz independiente._
3. ✅ **RESUELTO (2026-07-20) — Conectar editor ↔ wizard.** El wizard tiene botón **"✎ Abrir en el editor del protocolista"** que serializa la escritura completa (transforma los `<span class="ins" data-f>` en `<span class="campo" data-field>`, quita badges de citas y guiones) y la pasa por `localStorage` (`easypro_editor_handoff`). El editor la recibe al cargar, fusiona etiquetas amigables de los ~37 campos y muestra aviso; los campos **cascadean** (editar en panel → actualiza todas las copias) y quedan listos para biblioteca y control de cambios. Verificado end-to-end en navegador (sin residuos, sin errores). _Nota: usa `localStorage`, que en Chrome se comparte entre archivos `file://`; en otros navegadores conviene servirlo desde un mismo origen (servidor local)._
4. **Captura por extracción** (decisión 10): prototipar la extracción de **linderos** desde una escritura registrada (tenemos el texto de las minutas de la 16) que **prellena** el campo con resaltado "por validar". Luego cédula (PDF417) y voz.
5. **Port al software real** (cuando se dé el OK): tablas `norma`/`clausula`/`regla`, servicios FastAPI en Gari, frontend Next.js + OnlyOffice.

## Decisiones/insights clave (para no re-litigar)
- **Tipo de acto = raíz del árbol.** Escogerlo carga {normograma + biblioteca + árbol + orden}. NO es una plantilla fija (eso se abandonó); son **reglas + cláusulas**. Casi nunca es un solo acto: se **encadenan** (compraventa+hipoteca, +cancelación, +afectación).
- **Dos capas:** _mínimos obligatorios por ley_ (normograma, compartido, el motor los EXIGE vía cumplimiento: obligatoria/bloqueante) + _orden y estilo_ (por notaría). La notaría no puede quitar un mínimo legal; solo ordenarlo/redactarlo.
- **Captura por extracción → validación → cascada** (decisión 10): no digitar lo que se puede leer (linderos de la escritura registrada, cédula por PDF417, voz para prosa). Distinto de la marcación de campos (abandonada): aquí se extrae un dato conocido a un campo con nombre, con validación humana.
- **Política de completitud (demo = real).** Una demo NO es un resumen: la escritura generada debe contener **todos** los elementos que tendría la escritura real (todas las cláusulas y parágrafos, notas 1‑8, SARLAFT/STRADATA, REDAM, biometría, anexos, avalúo, fichas de firma completas). Aplicar esta regla a todo acto nuevo.
- **Comparación Hoy vs. Ecosistema** (dolores reales de la 16 y la 1, jul-2026): hoy reutilizan una escritura vieja parecida y la editan (arrastra datos del cliente anterior, errores de copy-paste, cláusulas que sobran/faltan; revisión difícil; cada protocolista su formato). Nuestra respuesta: arrancar limpio desde datos+reglas, digitar poco por cascada, red de cumplimiento aunque no haya jurídico, biblioteca por notaría como estándar sin rigidez.

## Escritura asistida — vista única (nuevo prototipo principal)
`prototipos/escritura-asistida.html` (sesión 2026-07-20, tarde) — **unifica captura + escritura editable + biblioteca en UNA sola vista** (antes eran wizard + editor separados). Incluye:
- **Renombre** wizard→"Escritura asistida"; **"BETA"** en vez de "datos ficticios".
- **Miles y centavos en vivo** en los campos de dinero (`.money`, `fmtMoneyStr`/`parseMoney`; `pts()`/`money()` con decimales).
- **Guiones de relleno en TODOS los párrafos** (cláusulas, parágrafos y notas) — `fillLeaders()` los añade automáticamente.
- **Liquidación integrada al cuerpo** de la escritura (bloque "DERECHOS, RECAUDOS Y VALORES A PAGAR" tras las constancias fiscales, donde va según el corpus).
- **Modo Captura ↔ Redacción:** en Captura la escritura se genera en vivo; en Redacción es editable (contenteditable) con toolbar (vincular/desvincular, control de cambios, aceptar/rechazar), **biblioteca de la Notaría 16** que inserta cláusulas, y panel "Datos vinculados" que cascadea.
- Verificado end-to-end en navegador (modo, biblioteca, cascada, control de cambios; sin errores).
- **Capa 2 (2026-07-20, tarde) — RESUELTO:** en Redacción se añadieron **comentarios estilo Word** (anclados a la selección, panel lateral con cita + texto + resolver/eliminar), **resaltado multicolor** (paleta de 5 colores + quitar), **dictado por voz** en linderos (Web Speech API `es-CO`, degrada si el navegador no lo soporta) y **exportar a PDF** (botón que recalcula los guiones al ancho de página A4 y abre imprimir con print-CSS que muestra solo la escritura). `mousedown`→preventDefault en el toolbar para no perder la selección. Verificado en navegador.

## Demo clickeable (para ver el HTML renderizado)
- **Artifact combinado (wizard + editor con el handoff en vivo):** https://claude.ai/code/artifact/814ac9b7-a9b4-43b6-b27d-3c4b317093a0 — una sola página con 2 pestañas; en “Captura” se pulsa “Abrir en el editor” y el borrador salta al editor con los campos vinculados. Generado por `prototipos/_build-demo.py` (empaqueta `wizard-compraventa.html` + `editor-vinculado.html` en `prototipos/demo-ecosistema-notarial.html` vía iframes + postMessage; regenerar tras editar los prototipos: `python3 prototipos/_build-demo.py`).
- **Recordatorio:** GitHub NO renderiza HTML (muestra el código fuente). Para ver los prototipos: abrir el Artifact, o abrir los `.html` localmente en el navegador.

## Guardado / continuidad
- **Git**: rama `claude/github-integration-gl79ne` (todo pusheado).
- **Artifacts** (persisten fuera del contenedor): índice del sandbox, wizard, normograma, mapa, árbol, demo, minuta-banco-slots, editor vinculado. URLs en el índice.
- **Corpus Notaría 16**: en `~/.claude/uploads/.../notaria16/` (efímero — si se pierde, el usuario lo vuelve a subir).
