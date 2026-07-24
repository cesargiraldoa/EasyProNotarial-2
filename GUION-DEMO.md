# Guion de demo — EasyProNotarial · Minutas Asistidas

> Formato: **[CLICO]** lo que haces · **[DIGO]** lo que dices. Duración ~10-12 min.

---

## ⭐ EL MENSAJE CENTRAL (con esto abres y cierras)

**La frase que remata:**
> **"El protocolista no arma la escritura. Describe el caso, y la escritura se arma sola — con las cláusulas correctas, los datos en su lugar, y validada contra la ley en tiempo real."**

**La idea brutal (dilo con tus palabras):**
Esto NO es un formulario que rellena una plantilla fija. Es un sistema donde **el documento se adapta al caso**. Cada situación jurídica (hipoteca previa, patrimonio de familia, afectación, divisas, predio rural, menor de edad…) es un **bloque que se ensambla solo**: trae **su cláusula legal + su formulario + el cableado entre ambos**. El protocolista no decide qué cláusula escribir ni de dónde copiarla: marca lo que aplica, llena los datos de ese tema, y el resto lo pone el sistema. **El conocimiento legal está incorporado** — un junior produce la misma calidad que el más experto.

**Antes vs Ahora (el contraste que vende):**

| Hoy en la notaría | Con el sistema |
|---|---|
| Copiar-pegar de una minuta vieja | Describir el caso con clics |
| Riesgo de dejar datos de OTRO caso | Cada dato se captura una vez y se inserta solo |
| El protocolista debe *saber* qué cláusula aplica | El sistema **arma** las cláusulas correctas |
| Errores que el registro **devuelve** | Validación legal **en vivo**; no deja generar con bloqueantes |
| Cada persona lo hace distinto | Documento **consistente y determinístico** |

**Cierre potente:** *"Esto convierte años de experiencia notarial en algo que cualquiera opera en minutos, sin errores."*

---

## Antes de empezar (montaje, 2 min antes)
- Backend y frontend corriendo (`npm run restart` o las dos terminales).
- Navegador en `http://localhost:5179/dashboard`, sesión iniciada.
- Ten a mano: los dos moldes ya cargados (Bancolombia y Davivienda) y el archivo `.skill`.
- **Ctrl+Shift+R** una vez para arrancar limpio.

---

## Acto 1 · El problema (30 seg, sin pantalla)
**[DIGO]** "Hoy un protocolista arma una escritura copiando y pegando de una minuta vieja, con el riesgo de dejar datos de otro caso. Nosotros lo convertimos en un flujo guiado, determinístico y con validación legal en vivo. Se los muestro."

---

## Acto 2 · Captura asistida (2 min)
**[CLICO]** Menú lateral → **Minutas Asistidas** → **Nueva escritura**.
**[DIGO]** "No hay que subir ningún documento. Se empieza eligiendo el acto."

**[CLICO]** Elijo **Compraventa + Hipoteca**.
**[DIGO]** "El sistema ya sabe qué normas y reglas aplican a este acto — miren, corpus vigente con sus validaciones."

**[CLICO]** Muestro el formulario a la izquierda (partes, inmueble, precio…).
**[DIGO]** "Captura por campos, no texto libre. Fíjense: un solo campo por fila, campos grandes, y en descripción/linderos hay **dictado por voz** —" **[CLICO]** el ícono de micrófono — "para que el protocolista dicte los linderos en vez de teclearlos. Y el correo tiene atajos de dominio."

---

## Acto 3 · Flujo guiado + primer banco (2 min)
**[DIGO]** "Como la fuente es Banco, el sistema **obliga a elegir el banco primero** — así no se llena nada por error."

**[CLICO]** En "Paso 1", elijo **Bancolombia**.
**[DIGO]** "Al elegir el banco pasan tres cosas solas:" (señalo)
- "Se llenan sus datos: nombre, NIT, apoderado."
- "Se **carga automáticamente la minuta base de Bancolombia**" — señalo el mensaje verde.
- "Y se habilita el formulario."

**[CLICO]** Pestaña **Redacción**.
**[DIGO]** "Este es el molde **real** de Bancolombia, con el texto legal de la notaría, y los datos del caso ya insertados."

---

## Acto 3.5 · EL MOMENTO CLAVE — las cláusulas se ensamblan solas (1.5 min)
> Este es el beat que prueba el mensaje central. No te lo saltes.

**[CLICO]** En Captura, sección **Encadenamientos**, marco **"Agregar afectación a vivienda familiar"** (o "Cancelación de hipoteca previa").
**[DIGO]** "Miren lo que pasa al marcar esto:" (señalo)
- "Apareció **el formulario** que ese tema necesita — solo esos campos."
- "Y en el documento se **insertó la cláusula legal** de ese tema, ya conectada."

**[CLICO]** Lleno el campo del escenario (beneficiarios / acreedor previo).
**[DIGO]** "Escribo el dato y **se mete solo** en la cláusula. **El protocolista no escribió una línea de derecho — solo describió el caso.** Y fíjense: el nombre del comprador ya está en la cláusula, no lo repetí; se captura una vez y el sistema lo reutiliza."

**[CLICO]** Desmarco el checkbox.
**[DIGO]** "Y si no aplica, desaparece. El documento **se adapta al caso**, no al revés. Esto es lo que ningún Word con campos hace."

---

## Acto 4 · Validación + generar el Word (2 min)
**[CLICO]** Vuelvo a **Captura**. Señalo el panel de Cumplimiento (bloqueantes).
**[DIGO]** "El motor valida en vivo contra la ley. Ahora hay 2 bloqueantes: falta matrícula y linderos. **No deja generar** hasta resolverlos — es la protección legal."

**[CLICO]** Lleno **Matrícula** y **Linderos** del inmueble (dicto los linderos con el micrófono).
**[DIGO]** "Miren cómo bajan los bloqueantes a cero…" (señalo) "…y el cuerpo se rellena solo."

**[CLICO]** **Generar documento**.
**[DIGO]** "Y sale el Word listo para firma. Todo determinístico: mismos datos, mismo documento, siempre."

---

## Acto 5 · Multi-banco: el diferencial (1.5 min)
**[DIGO]** "Lo importante: cada banco tiene su **propia** minuta. Miren con Davivienda."

**[CLICO]** Nueva escritura → Compraventa + Hipoteca → banco **Davivienda** → Redacción.
**[DIGO]** "Es un molde **distinto** — su hipoteca, sus notas, su cuenta AFC, y hasta la **afectación a vivienda familiar** que Bancolombia no trae. Cambias de banco y cambia el documento correcto."

---

## Acto 6 · Autonomía: Registro de moldes (1.5 min)
**[CLICO]** Menú → **Registro de moldes**.
**[DIGO]** "Y esto es clave para el negocio: los moldes se cargan y editan **desde la app, sin programar**."

**[CLICO]** Abro Bancolombia → cambio algo del nombre → **Guardar molde** (sale verde).
**[DIGO]** "Lo que guardo aquí se usa al instante en el flujo. La notaría mantiene sus propios moldes sin depender de nosotros."

---

## Acto 7 · Cómo escala a 500 notarías (1.5 min)
**[DIGO]** "¿Y cómo llevamos esto a 500 notarías sin volvernos locos? Dos ideas:"
1. "Los moldes son por **banco + acto + ciudad** — un molde de Bancolombia-Medellín sirve para **todas** las notarías de Medellín. No se hace uno por notaría; se hace una vez y se hereda."
2. "Y para convertir la minuta de una notaría en molde, tenemos una **IA especializada**: la notaría manda su `.docx`, y devuelve el molde listo y **auto-validado** — sin marcado manual, sin adivinar."

**[DIGO]** "En resumen: la notaría solo manda su documento; el sistema hace el resto."

---

## Cierre (20 seg)
**[DIGO]** "Entonces: captura guiada, validación legal en vivo, un molde por banco, generación determinística del Word, y todo cargable y escalable sin código. Eso es Minutas Asistidas."

---

## Frases de rescate (si algo falla)
- Si algo no carga: "Esto es un ambiente de desarrollo; en producción va sobre servidor." → sigue con la siguiente pantalla.
- Si preguntan por precisión legal: "El texto legal se conserva **verbatim** de la minuta real de la notaría; el sistema solo inserta los datos del caso."
- Si preguntan por la IA: "No adivina campos —eso falla—; sigue un vocabulario fijo y **se autovalida** antes de entregar."
