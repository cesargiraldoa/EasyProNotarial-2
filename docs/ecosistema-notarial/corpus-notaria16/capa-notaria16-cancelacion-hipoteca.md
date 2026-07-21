# Capa Notaría 16 — Cancelación de Hipoteca

> **Insumo directo del motor.** Producto del análisis del corpus real de la Notaría 16 de Medellín (**5 escrituras** de cancelación de hipoteca, carpeta de Ana María). Separa lo que la **ley exige** (→ normograma compartido) de lo que es **estilo/orden de la Notaría 16** (→ esta capa). Alimenta las tablas `norma` / `clausula` / `regla` del backend y la biblioteca de cláusulas del editor.
>
> Fuente: extracción `strings -e S | iconv cp1252→utf8` de los 5 `.doc` del ZIP `NOTARIA 16 - MEDELLÍN` (LibreOffice no carga los binarios en este entorno). Slots marcados `{así}`.
>
> _Última actualización: sesión 2026-07-21._

---

## 0. Corpus analizado

| # | Escritura (E.P.) | Otorgante (firma por el banco) | Acreedor | Propietario / deudor | Modelo |
|---|---|---|---|---|---|
| 1 | 1.206 — 6 mar 2026 | Paulina Andrea Beltrán (Apoderada Especial) | Bancolombia S.A. | Angélica María Román Ruiz | **A** (poder E.P.) |
| 2 | 4.089 — 17 jun 2026 | Martha Elizabeth Areiza (Rep. Legal Suplente) | Bancolombia S.A. | Claudia Marroquín y Nelson Ochoa | **B** (cert. Cámara) |
| 3 | 418 — 6 feb 2026 | Kelly Johanna Borrero (Apoderada Especial) | Bancolombia S.A. | Jorge Enrique Marín y Sebastián Marín | **A** (poder E.P.) |
| 4 | 2.664 — 28 abr 2026 | Tatiana Marín Herrera (Rep. Legal Suplente) | Bancolombia S.A. | Luis Fernando Alzate y Jhon Alexander Alzate | **B** (cert. Cámara) |
| 5 | 2.817 — 5 may 2026 | Luis Alfredo Cardona (Apoderado Especial) | **Itaú Colombia S.A.** (vía Cibergestión) | María Clara Giraldo y Diego Naranjo | **C** (Itaú / no-Bancolombia) |

**Hallazgo clave:** el acto tiene **un solo compareciente** — el **apoderado o representante del banco acreedor**. El deudor/propietario **no comparece ni firma**: el banco, como acreedor, es quien tiene el interés jurídico de liberar el gravamen que constituyó a su favor. Esto invierte el patrón de la compraventa (donde el titular transfiere): aquí el acreedor renuncia a la garantía.

**Práctica constante de la 16 (NOTA 1):** el apoderado del banco **firma fuera de las instalaciones de la Notaría** (en el despacho del banco), al amparo del art. 12 del Decreto 2148 de 1983. Es el rasgo operativo más distintivo del acto en esta notaría.

---

## 1. Dos modelos de representación del acreedor (variación entre protocolistas)

El esqueleto legal es idéntico; cambia **cómo se acredita la representación del banco**:

- **Modelo A — Apoderado Especial (poder por escritura):** *"…en su carácter de Apoderad{o/a} Especial, según Poder Especial otorgado mediante la Escritura Pública número {poder_num} de fecha {poder_fecha} de la Notaría {poder_notaria}, copia del cual se adjunta para su protocolización con el presente instrumento."* (docs 1, 3, 5)
- **Modelo B — Representante Legal (certificado de Cámara):** *"…en su carácter de Representante Legal Suplente, circunstancias que se acreditan con el correspondiente certificado de existencia y representación legal expedido por la Cámara de Comercio de Medellín para Antioquia; copia del cual se adjunta para su protocolización con el presente instrumento."* (docs 2, 4)

→ El motor ofrece un **selector "tipo de representación" (Apoderado especial / Representante legal)** que conmuta el bloque, con los slots del poder solo visibles en modo A.

**Caso C (Itaú, doc 5):** cadena de poderes larga (apoderado → apoderado general → Cibergestión), banco con historial de razones sociales, y estructura de cláusulas distinta (ver §3). Se soporta como **variante de acreedor no-Bancolombia** con un campo de "personería" de texto libre.

---

## 2. Orden canónico de las secciones (Notaría 16)

🟥 = mínimo por ley · 🟦 = estilo/orden de la 16 · 🟨 = condicional.

1. 🟦 **Carátula / rubro** — `ESCRITURA PÚBLICA NRO. {num_letras}. {num_cifra}` → `CANCELACIÓN DE HIPOTECA.` → `DE: {banco}` / `A: {propietario}`
2. 🟥 **Formato de calificación SNR** — folio(s) de matrícula, código catastral, NUPRE, ubicación del predio (art. 8 Ley 1579/2012)
3. 🟦 **Datos de la escritura** — número, día/mes/año, Notaría Dieciséis
4. 🟦 **Naturaleza jurídica del acto** — código SNR **`775` CANCELACIÓN DE HIPOTECA** + valor del acto
5. 🟥 **Personas que intervienen** — banco (NIT) + propietario/deudor (C.C.)
6. 🟥 **Comparecencia / apertura notarial** — lugar, fecha, Notaría 16, notario y su calidad (titular / interina / encargad@) con su acto administrativo (Decreto/Resolución)
7. 🟥 **PRIMERO — Representación del acreedor** — apoderado especial (poder) o representante legal (certificado) — ver §1
8. 🟥 **SEGUNDO — Identificación de la hipoteca a cancelar** — E.P. de constitución, notaría, registro, folio(s), deudor(es), acreedor, monto inicial, inmueble + linderos por remisión
9. 🟥 **TERCERO — Declaración de cancelación y liberación** — el acreedor CANCELA; el inmueble queda libre del gravamen
10. 🟨 **Acto sin cuantía Ley 546/1999** — leyenda para crédito de vivienda (docs 1, 3, 4, 5; ausente en doc 2)
11. 🟥 **Cierre notarial** — lectura y firma, advertencia de registro, hojas de papel notarial, RECAUDO SUPERINTENDENCIA Y FONDO
12. 🟥 **NOTAS 1–5** — firma fuera de sede · registro 2 meses · verificación de datos · notificaciones electrónicas · SARLAFT/STRADATA
13. 🟥 **Firmas** — apoderado/representante del banco + notario

---

## 3. Biblioteca de cláusulas — CANCELACIÓN DE HIPOTECA (con clasificación de capa)

Texto de apertura verbatim (estilo Notaría 16). **[FIJO]** = clausulado idéntico entre las 5 escrituras (candidato directo a estándar único).

### Encabezamiento notarial · 🟦 estilo **[FIJO]**
> *"En la ciudad de Medellín, Departamento de Antioquia, República de Colombia, a los {dia_letras} ({dia_cifra}) días del mes de {mes} del año {anio_letras} ({anio_cifra}), al despacho de la NOTARÍA DIECISEIS DEL CÍRCULO NOTARIAL DE MEDELLIN, cuy{o/a} Notari{o/a} {calidad} es {el/la} doctor{/a} {notario} (según {acto_admin} Nro. {acto_num} del {acto_fecha})"*
> Calidad observada: Titular · Interina · Encargad@ (según disponibilidad; el notario firmante NO determina el estilo — lo determina el protocolista).

### Comparecencia · 🟥 por ley · art. 13 Dcto 960/1970 (identificación plena)
> *"Se presentó {el/la} señor{/a} {apoderado}, quien dijo ser mayor de edad, domiciliad{o/a} en la ciudad de Medellín, identificad{o/a} con la cédula de ciudadanía número {apoderado_cc} y manifestó."*
> _Variante C (Itaú): "Compareció el señor: {apoderado}, mayor de edad, domiciliado en Medellín, identificado con la cédula… obrando en nombre y representación de {banco}…"_

### PRIMERO — Representación del acreedor · 🟥 por ley · C. de Comercio (representación de personas jurídicas)
> **Modelo A:** *"PRIMERO: Que comparece al otorgamiento del presente instrumento, obrando en nombre y representación de {banco}, establecimiento bancario, con domicilio principal en la ciudad de {banco_domicilio}, representación que ejerce en su carácter de Apoderad{o/a} Especial, según Poder Especial otorgado mediante la Escritura Pública número {poder_num} de fecha {poder_fecha} de la Notaría {poder_notaria}, copia del cual se adjunta para su protocolización con el presente instrumento."*
> **Modelo B:** *"…representación que ejerce en su carácter de Representante Legal Suplente, circunstancias que se acreditan con el correspondiente certificado de existencia y representación legal expedido por la Cámara de Comercio de Medellín para Antioquia; copia del cual se adjunta para su protocolización con el presente instrumento."*
> Slots: `{banco}` `{banco_domicilio}` `{apoderado_cargo}` `{poder_num}` `{poder_fecha}` `{poder_notaria}`

### SEGUNDO — Identificación de la hipoteca a cancelar · 🟥 por ley · art. 2457 CC + Ley 1579/2012 (tracto registral) **[FIJO en su estructura]**
> *"SEGUNDO: Que por medio de la Escritura Pública número {hip_num} del {hip_fecha} de la Notaría {hip_notaria}, debidamente registrada el {hip_reg_fecha} en la Oficina de Registro de Instrumentos Públicos de {orip}, bajo el (los) FOLIO (S) DE MATRICULA INMOBILIARIA NÚMERO (S) {matricula} el (la, los) señor (a, es) {deudor}, constituyó (eron) en favor de {banco}, Hipoteca Global o Abierta de Primer Grado y sin límite en la cuantía, por la cantidad inicial de {monto_letras} ($ {monto_cifra}), sobre el siguiente bien inmueble:"*
> — descripción del inmueble + `FOLIO (S) DE MATRICULA INMOBILIARIA NRO (S): {matricula}` —
> *"Inmueble que se determina por los linderos y demás especificaciones consignados en la mencionada escritura pública que se cancela."*
> Slots: `{hip_num}` `{hip_fecha}` `{hip_notaria}` `{hip_reg_fecha}` `{orip}` `{matricula}` `{deudor}` `{monto_letras}` `{monto_cifra}` `{descripcion_inmueble}`

### TERCERO — Cancelación y liberación del gravamen · 🟥 por ley · art. 2457 CC **[FIJO]**
> *"TERCERO: Que obrando en el carácter expresado CANCELA la Hipoteca Constituida mediante la Escritura Pública número {hip_num} del {hip_fecha} de la Notaría {hip_notaria}, debidamente registrada el {hip_reg_fecha} en la Oficina de Registro de Instrumentos Públicos de {orip}, bajo el (los) FOLIO (S) DE MATRICULA INMOBILIARIA NÚMERO (S) {matricula} antes mencionada, y en consecuencia, queda (n) libre (s) del gravamen el (los) inmueble (s) descrito (s) en la cláusula segunda de esta escritura."*

### Acto sin cuantía · 🟨 condicional (crédito de vivienda) · art. 23 Ley 546/1999
> *"EL PRESENTE INSTRUMENTO SE CONSIDERA COMO ACTO SIN CUANTIA DE CONFORMIDAD CON LA LEY 546 DE 1999."*
> Presente en docs 1, 3, 4, 5. Ausente en doc 2 (el motor lo ofrece como **casilla**, marcada por defecto para vivienda).

### Variante C (Itaú, doc 5) — cláusulas adicionales · 🟨 según acreedor
- **Valor asignado para liquidación:** *"Para efectos de la liquidación de derechos notariales y de registro, se asignó al contrato de hipoteca un valor de {monto_letras} ($ {monto_cifra})."*
- **No paz y salvo:** *"La cancelación de esta hipoteca no implica paz y salvo a favor del Deudor, ya que este acto solo conlleva la cancelación del gravamen hipotecario identificado en el numeral primero, sin que se refiera a un paz y salvo o exoneración total de las obligaciones que por otros conceptos pudiere tener el Deudor, ya sea como deudor principal, avalista o deudor solidario."*
- **Parágrafo Ley 546:** *"PARAGRAFO: Que de acuerdo con el artículo Veintitrés (23) de la Ley Quinientos Cuarenta y Seis (546) de Diciembre Veintitrés (23) de Mil Novecientos Noventa y Nueve (1999), que establece la cancelación de gravámenes hipotecarios de créditos para vivienda, la presente cancelación se considerará un acto sin cuantía."*

---

## 4. Constancias y NOTAS de cierre (con capa)

### Constancias · 🟥 por ley **[FIJO]**
> *"L{a/e} exponente leyó personalmente el presente instrumento, lo aprobó y en constancia lo firma."*
> *"Se advirtió el registro dentro del término legal para ello."*
> *"Se extendió en las hojas de papel notarial números: {hojas}"*
> *"RECAUDO SUPERINTENDENCIA Y FONDO: $ {recaudo}"* (observado: $19.300 base; $28.900 en un caso)

### NOTA 1 — Firma fuera de la sede · 🟦 estilo (rasgo distintivo de la 16) · art. 12 Dcto 2148/1983 **[FIJO]**
> *"NOTA 1: {El/La} {doctor/a} {apoderado}, identificad{o/a} con la cédula de ciudadanía número {apoderado_cc} actuando en su condición de {apoderado_cargo} de {banco} por autorización de la suscrita notaria, suscribe la presente escritura pública fuera de las instalaciones de la Notaría Dieciséis de Medellín, en su despacho, de conformidad con el artículo del Artículo 12 del Decreto 2148 de 1983."*

### NOTA 2 — Advertencia de registro · 🟥 por ley · art. 5 Ley 1579/2012 **[FIJO]**
> *"NOTA 2: A los otorgantes se les hizo la advertencia que deben presentar esta escritura para registro, en la Oficina correspondiente, dentro del término perentorio de dos (2) meses contados a partir de la fecha de otorgamiento de este instrumento, cuyo incumplimiento causará intereses moratorios por mes o fracción de mes de retardo."*

### NOTA 3 — Verificación de datos · 🟦 estilo **[FIJO]**
> *"NOTA 3: Los comparecientes hacen constar que han verificado cuidadosamente sus nombres completos, el número de sus documentos de identidad, igualmente declaran que todas las informaciones consignadas en el presente instrumento son correctas y que en consecuencia, asumen la responsabilidad que se derive de cualquier inexactitud en las mismas."*

### NOTA 4 — Notificaciones electrónicas · 🟥 por ley · art. 15 Dcto 1579/2012 + art. 56 CPACA **[FIJO]**
> *"NOTA 4: NOTIFICACIONES ELECTRONICAS.- Los comparecientes manifiesta (n) que NO ( ) SI (X) dan su consentimiento… para ser notificado por medio electrónico sobre el estado del trámite… a través del correo electrónico: {correo_notif}."*
> Correo fijo observado en la 16: `escriturasrelusuario@gmail.com`.

### NOTA 5 — SARLAFT + STRADATA · 🟥 por ley · Ley 1581/2012 + Circular 1536/2013 SNR + art. 17 Ley 282/1996 **[FIJO]**
> *"NOTA 5: SARLAF: AUTORIZACIÓN DE TRATAMIENTO DE DATOS PERSONALES… STRADATA SEARCH: en cumplimiento con la Circular 1536 del 17 de Septiembre de 2013 expedida por la SNR y del Artículo 17 de la Ley 282 de Junio 6 de 1996, se consultó información de el (la, los) otorgante (s)…"*
> Presente en docs 1, 3 (y esperado en 5). Ausente en la extracción de docs 2, 4 → el motor la incluye por defecto (mínimo por ley).

---

## 5. Campos que captura el motor (formulario del acto)

| Grupo | Campos |
|---|---|
| **Escritura** | número, fecha de otorgamiento, notario y calidad + acto administrativo |
| **Acreedor (banco)** | nombre, NIT, domicilio principal, tipo de representación (apoderado especial / representante legal), datos del poder (E.P. núm/fecha/notaría) si aplica |
| **Otorgante (firma)** | nombre del apoderado/representante, género, C.C., cargo |
| **Propietario / deudor** | nombre(s), C.C.(s) — solo se nombran, no firman |
| **Hipoteca a cancelar** | E.P. núm, fecha, notaría, fecha de registro, ORIP (ciudad-zona), folio(s) de matrícula, monto inicial |
| **Inmueble** | descripción, dirección, municipio, urbano/rural, código catastral, NUPRE, linderos (por remisión) |
| **Opciones** | acto sin cuantía Ley 546 (vivienda) · no paz y salvo (Itaú) · SARLAFT · notificaciones electrónicas + correo · hojas de papel notarial · recaudo |

---

## 6. Mínimos por ley (bloqueantes del cumplimiento)

El motor EXIGE, para dejar generar:
1. **Identificación plena** del compareciente (apoderado/representante) — art. 13 Dcto 960/1970.
2. **Personería del acreedor** acreditada — poder (E.P.) o certificado de Cámara de Comercio (protocolizado).
3. **Identificación exacta de la hipoteca** a cancelar: E.P., notaría, fecha de registro, folio(s) de matrícula — sin esto no hay tracto y el registro rechaza (Ley 1579/2012).
4. **Declaración expresa de cancelación** por el titular del crédito (art. 2457 CC).
5. **Advertencia de registro** (2 meses) — NOTA 2.
6. **Notificaciones electrónicas** — NOTA 4.
7. **SARLAFT / tratamiento de datos** — NOTA 5 (Ley 1581/2012).

---

## 7. Insight para el pitch

Hoy la 16 arma cada cancelación **reutilizando una escritura anterior parecida** (misma carpeta de Ana María). Se ve en el corpus: dos protocolistas dejan una `NOTA 2` duplicada/cortada al final (residuo de copy-paste), y la `NOTA 5 (SARLAFT)` aparece o desaparece según de qué escritura se partió — no según la ley. El motor, arrancando desde datos + reglas, hace que la NOTA 5 (mínimo por ley) **nunca falte** y que las notas de otro cliente **nunca se arrastren**.
