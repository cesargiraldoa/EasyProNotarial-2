# Capa Notaría 16 — Compraventa y Compraventa + Hipoteca

> **Insumo directo del motor.** Producto del análisis del corpus real de la Notaría 16 de Medellín (13 documentos: 4 compraventas simples + 9 compraventa/hipoteca). Separa lo que la **ley exige** (→ normograma compartido) de lo que es **estilo/orden de la Notaría 16** (→ esta capa). Alimenta las tablas `norma` / `clausula` / `regla` del backend y la biblioteca de cláusulas del editor.
>
> Fuente: extracción cp1252 de los `.doc`/`.docx` del ZIP `NOTARIA 16 - MEDELLÍN`. Slots marcados `{así}`.
>
> _Última actualización: sesión 2026-07-20._

---

## 0. Hallazgo estructural clave

La escritura es **un solo instrumento con comparecencias sucesivas**, no varias escrituras. Los actos se **apilan** dentro del mismo documento (compraventa → hipoteca → afectación → aclaración → cancelaciones), unidos por el hilo material del crédito. Esto confirma la decisión de diseño *"los actos se encadenan"*: el tipo de acto raíz (compraventa) arrastra, según el caso, hipoteca + afectación vivienda familiar + renuncia a condición resolutoria + cancelaciones + aclaración.

**Cuatro plantillas conviven en la misma notaría** (una por protocolista), con el mismo esqueleto legal pero redacción y orden distintos:

| Protocolista | Estilo | Rasgo distintivo |
|---|---|---|
| **Alejandra Velilla** | Plantilla A | Carátula `COMPRAVENTA` + tabla `NATURALEZA JURÍDICA` y `PERSONAS QUE INTERVIENEN`; doble parágrafo de precio real (base ×4) |
| **Juan Camilo Orozco** | Plantilla B | Carátula `ACTOS:`, C.C. en línea DE/A, sin tablas; cláusula SÉPTIMO paz y salvo; leyenda `PASA/VIENE HOJA` |
| **Ana María** | Plantilla C | Compraventa+hipoteca Bancolombia; comparecencias sucesivas; 8 NOTAS de cierre; dos sub-plantillas de hipoteca (vivienda / comercial) |
| **Alexandra Suaza** | Plantilla D | Compraventa+hipoteca a entidades públicas/cooperativas (EPM, Metro, COOSANLUIS); **inserta la minuta de la entidad como bloque cerrado** entre sus propios bloques de apertura y cierre |

**Insight operativo:** la plantilla la determina **quién redacta el borrador (el protocolista), no quién firma (el notario encargado)**. Ejemplo real: dos escrituras firmadas por el mismo notario (Juan Camilo Orozco) siguen plantillas distintas según las redactara Velilla u Orozco. → El motor debe ofrecer **un estándar único** por notaría, no cuatro estilos personales.

---

## 1. Orden canónico de las secciones (Notaría 16)

Orden real observado, de principio a fin. Se marca la **capa** de cada bloque: 🟥 = mínimo por ley · 🟦 = estilo/orden de la 16 · 🟨 = condicional (según caso).

1. 🟦 **Carátula / rubro** — `ESCRITURA PÚBLICA NRO.` → `ACTOS:` (enumera todos los actos encadenados) → `DE:` / `A:` / `HIPOTECA A FAVOR DE:` → valor
2. 🟥 **Formato de calificación SNR** — folios de matrícula, código catastral, NUPRE, ubicación (art. 8 Ley 1579/2012)
3. 🟦 **Datos de la escritura** — número, día/mes/año, notaría
4. 🟦 **Naturaleza jurídica del acto** — tabla con **códigos SNR** por acto: `125` compraventa · `205`/`219` hipoteca abierta sin límite · `304` afectación vivienda familiar · `901` aclaración · `716`/`803`/`744` cancelaciones. Con valor por acto
5. 🟥 **Personas que intervienen** — nombre + identificación (identificación plena de partes, art. 13 Dcto 960)
6. 🟥 **Comparecencia / apertura notarial** — lugar, fecha, notaría, notario y su calidad (encargado/interino) con acto administrativo
7. 🟨 **Actos preliminares** (si aplica) — aclaración (sanea la cadena registral antes de vender), cancelación de usufructo/prohibición/derecho de preferencia
8. 🟥 **ACTO DE COMPRAVENTA** — cláusulas ordinales PRIMERO…N (ver §2)
9. 🟥 **Aceptación del comprador + indagación Ley 258** (art. 6 Ley 258)
10. 🟨 **ACTO DE HIPOTECA** (si hay crédito) — el comprador re-comparece como DEUDOR/HIPOTECANTE; cláusulas propias (ver §3)
11. 🟨 **Comparecencia del acreedor** — apoderado del banco/entidad acepta la garantía y firma
12. 🟨 **Ratificación Ley 258** (si afectado) — los compradores confirman que la afectación no es oponible a la hipoteca
13. 🟥 **Cierre notarial** — constancia de lectura y firma (fases art. 13), hojas de papel notarial, derechos/recaudo/retención, **NOTAS 1–8**, STRADATA, ANEXOS, avalúo catastral, fichas de firma, firma del notario

---

## 2. Biblioteca de cláusulas — COMPRAVENTA (con clasificación de capa)

Para cada cláusula: **texto de apertura verbatim** (estilo Notaría 16), **slots**, **capa** y **norma** que la respalda (capa por-ley → normograma). El texto es fijo salvo los `{slots}`; se marca **[FIJO]** el clausulado idéntico entre protocolistas (candidato directo a estándar único).

### PRIMERO — Transferencia de dominio · 🟥 por ley · art. 1857 CC (solemnidad) + art. 16 Ley 1579 (identificación plena — **BLOQUEANTE**)
> *"Que obrando en la calidad indicada, transfiere (n) el {porcentaje} que tiene, a título de venta, en favor de {comprador} identificado con la cédula de ciudadanía número {comprador_cc}… del derecho de dominio y posesión real y material que el (la, los) exponente (s) tiene (n) y ejerce (n) sobre el (los) siguiente (s) bien (es) inmueble(s):"*
> Slots: `{porcentaje}` `{comprador}` `{comprador_cc}` `{comprador_estado_civil}` `{descripcion_inmueble}` `{linderos}` `{area}` `{matricula}` `{direccion_catastral}` `{codigo_catastral}` `{nupre}`

### Parágrafo — Cuerpo cierto · 🟦 estilo **[FIJO]**
> *"No obstante la mención de la cabida, área y linderos, (los) inmueble (s) se transfiere (n) como cuerpo (s) cierto (s).-"*

### Parágrafo — Régimen de propiedad horizontal · 🟨 condicional (solo PH) · Ley 675/2001
> *"El (los) inmueble (s) anteriormente descrito (s) se encuentra sometido al régimen de propiedad horizontal, mediante escritura pública número {esc_rph} del {fecha_rph} otorgada en la {notaria_rph}, debidamente registrada."*
> Slots: `{esc_rph}` `{fecha_rph}` `{notaria_rph}`

### Parágrafo — Copropiedad / coeficiente · 🟨 condicional (solo PH) · arts. 25-26 Ley 675
> *"…comprende no sólo los bienes susceptibles de dominio particular y exclusivo… sino además el derecho de copropiedad en el porcentaje señalado para el inmueble en el respectivo reglamento."* ⚠ *En el corpus NO se transcribe el coeficiente numérico — oportunidad de mejora del motor (exigir el % real).*

### SEGUNDO — Títulos de adquisición y modo · 🟥 por ley (tradición / cadena registral)
> *"Títulos de adquisición y modo: La parte vendedora garantiza a la parte compradora que los derechos que enajena… los adquirió por {modo_adquisicion}, tal como consta en la escritura pública número {esc_titulo} del {fecha_titulo} otorgada en la {notaria_titulo}, debidamente registrada."*
> Slots: `{modo_adquisicion}` (compraventa/sucesión/adjudicación/sentencia) `{esc_titulo}` `{fecha_titulo}` `{notaria_titulo}`

### TERCERO — Garantía de libertad de gravámenes · 🟦 estilo **[FIJO]** (refuerza saneamiento, art. 1893 CC)
> *"Garantiza(n) el (la, los) vendedor(a, es) la absoluta propiedad de el (los) inmueble (s) que se transfiere (n), el (los) cual (es) no lo (s) ha (n) gravado en forma alguna ni su dominio se encuentra en pleito alguno…"*

### Parágrafo — Ley 258 (indagación al vendedor) · 🟥 por ley **[FIJO]** · art. 6 Ley 258/1996
> *"Para dar cumplimiento a la ley 258 de 1996 el Notario indagó a el (la, los) vendedor (a, es) quien (es) expresamente y bajo la gravedad del juramento manifestó (aron) que sobre el inmueble objeto de venta no se ha constituido la afectación de vivienda familiar…"*

### CUARTO — Precio · 🟥 por ley · art. 1849 CC (precio en dinero)
> *"Que el precio de el (los) inmueble (s) vendido (s) lo constituye la cantidad de {valor_letras} MONEDA LEGAL COLOMBIANA ($ {valor_cifra})…"*
> Slots: `{valor_letras}` `{valor_cifra}` `{forma_pago}` (contado / recursos propios + crédito {acreedor} / fondo pensiones / AFC)

### Parágrafo — Declaración de precio real · 🟥 por ley **[FIJO]** · art. 90 ET (mod. art. 61 Ley 2010/2019)
> *"…declaramos bajo la gravedad de juramento, que el precio incluido en la escritura es real y no ha sido objeto de pacto privado…"*

### Parágrafo — Base gravable ×4 · 🟥 por ley (consecuencia art. 90 ET) · *presente en plantilla A/C, ausente en B* → **unificar en estándar**
> *"…sin las referidas declaraciones… serán liquidados sobre una base equivalente a cuatro veces el valor incluido en la escritura…"*

### Parágrafo — Origen de los ingresos / SARLAFT · 🟥 por ley **[FIJO]** · Ley 2195/2022 + SIPLAFT
> *"origen de los ingresos: {comprador}, declara que… los recursos… provienen de actividades lícitas, que no se encuentra con registros negativos en listados de prevención de lavado de activos… ni… en los listados de la OFAC…"*

### QUINTO / SEXTO — Entrega real y material · 🟥 por ley (tradición) — 🟨 entrega **diferida al desembolso** cuando hay crédito
> *"Que la entrega real y material… se hará hoy a la firma de esta escritura pública…"* (contado) **/** *"…se hará a la fecha del desembolso del crédito otorgado por {acreedor}."* (financiado)

### Parágrafo — Renuncia a la condición resolutoria · 🟨 negocial (financiado) · art. 1546 CC. **Dos variantes:**
- **Forma de pago** (renuncia el **vendedor**): *"El Vendedor expresamente renuncia a la condición resolutoria que pudiera derivarse de la forma de pago pactada y otorga la presente escritura sin limitación alguna, quedando por lo tanto firme y definitiva."*
- **Forma de entrega** (renuncia el **comprador**): *"…LA PARTE COMPRADORA renuncia expresamente… y en consecuencia otorga el presente título firme e irresoluble."*

### SEXTO — Saneamiento · 🟦 estilo **[FIJO]** · arts. 1893 ss CC (evicción / vicios redhibitorios)
> *"Que el (la, los) vendedor (a, es) se obliga (n) a acudir al saneamiento… bien sea por evicción o por vicios redhibitorios."*

### SÉPTIMO — Gastos / retención en la fuente · 🟥 por ley · art. 398 ET (retención 1%)
> *"La Retención en la Fuente será de cuenta exclusiva del Vendedor"* + parágrafo: gastos de la hipoteca a cargo del comprador.

### Parágrafo — Paz y salvo de administración + solidaridad · 🟨 condicional (solo PH) · art. 29 Ley 675
> *"…SI presentó (aron) paz y salvo de administración… pero que de todas formas se hace solidario (s) por las deudas… por las expensas comunes."* (o forma negativa: no hay administración → comprador solidario)

### Aceptación del comprador + indagación Ley 258 al comprador · 🟥 por ley · art. 6 Ley 258
> *"Presente el (la, los) comprador (a, es) {comprador}… a) Que actúa en nombre propio b) Que ACEPTA esta escritura en todas sus partes… d) Que acepta el reglamento de propiedad horizontal… e) Para dar cumplimiento a la ley 258…"*
> **Resultado bifurca:** `NO queda afectado` (por no darse los presupuestos) **/** `SÍ queda afectado` (comparece cónyuge/compañero, firma) → dispara código SNR `304` + advertencia de nulidad absoluta.

### Parágrafo — REDAM · 🟥 por ley **[FIJO]** · Ley 2097/2021 + Dcto 1310/2022
> *"En virtud de la imposibilidad de dar aplicación… la base de datos del REDAM… no se encuentra disponible… el compareciente declara que no tiene pendientes obligaciones alimentarias superiores a tres meses."* (variante: se protocoliza certificado REDAM real del MINTIC)

---

## 3. Biblioteca de cláusulas — HIPOTECA

La hipoteca casi siempre es **minuta del acreedor** insertada en la escritura. Capa: 🟨 negocial/entidad, salvo el mínimo de constitución (🟥 art. 2432 ss CC + escritura pública). Dos familias:

### 3.A Hipoteca bancaria de vivienda (Bancolombia — plantilla C)
Orden: PRIMERO Objeto · SEGUNDO Solidaridad · TERCERO Título · CUARTO Obligaciones garantizadas · QUINTO Valor del acto (base fiscal) · SEXTO Declaraciones (a–i) · SÉPTIMO Seguros · OCTAVO Extinción del plazo (causales a–ñ) · NOVENO Vigencia · DÉCIMO Ausencia de novación · 11 Cesión · 12 Desafectación · 13 Convenio · 14 Patrimonio de familia · 15 Privilegios reales.
> **Objeto:** *"Que constituye(n) Hipoteca Abierta sin Límite de Cuantía a favor de {acreedor}… en adelante EL ACREEDOR, sobre el (los) siguiente(s) inmueble(s), conforme con el artículo 2432 y siguientes del Código Civil…"*
> **Obligaciones garantizadas:** *"…se garantiza el Crédito Hipotecario de Vivienda… por la suma de {monto_hipoteca} ($…), que será pagada dentro del plazo de {plazo_anios} en {n_cuotas} cuotas mensuales…"*
> Slots: `{acreedor}` `{monto_hipoteca}` `{plazo_anios}` `{n_cuotas}` `{valor_base_fiscal}` `{apoderado_banco}` `{ep_poder}`
> **Sub-variante comercial/genérica** (empleada del banco): sujeto solo "HIPOTECANTE" (no "DEUDOR"), obligaciones amplias (mutuo/factoring/leasing/tarjetas), sin plazo/cuotas, + nota Dcto 1809/1989 (préstamo > 70% por ser empleado).

### 3.B Hipoteca de entidad pública / cooperativa (EPM, Metro, COOSANLUIS — plantilla D)
La entidad **impone su minuta**; la notaría la inserta como bloque cerrado ("Hasta acá la minuta presentada por…"). Rasgos:
- **EPM** — mutuo laboral: descuento de nómina, pignoración de cesantías (40% parciales / 100% al retiro), seguros elegidos por EPM, autorización sindical. Constituida como **hipoteca especial de primer grado por suma determinada** (aunque la carátula diga "abierta sin límite" ⚠).
- **Metro** — mutuo Programa de Vivienda (Res. 0302/2024): cuotas quincenales, cónyuge deudora solidaria, cláusula aceleratoria, remite a Ley 546/1999, requiere **acta de reparto notarial**.
- **COOSANLUIS** — clausulado cooperativo tipo bancario clásico (14 cláusulas), sin descuento de nómina.

### Comparecencia y aceptación del acreedor · 🟨 (siempre firma)
> *"Presente {apoderado_banco}… en su condición de Apoderada Especial de {acreedor}, según Poder Especial… Escritura Pública Nro. {ep_poder}… acepta para {acreedor} la garantía y demás declaraciones…"*
> **Firma fuera del despacho** (NOTA 2, art. 12 Dcto 2148/1983) cuando el apoderado no acude a la notaría.

---

## 4. Notas estándar de cierre (NOTAS 1–8) y clasificación

Bloque de cierre casi idéntico entre protocolistas (Ana María / Suaza lo estandarizan como NOTA 1..8; Velilla/Orozco lo dispersan sin numerar). **Candidato fuerte a estándar único.**

| Nota | Contenido | Capa | Norma |
|---|---|---|---|
| NOTA 1 | Valor base de liquidación = carta de la entidad crediticia protocolizada | 🟦 operativo/fiscal | tarifas notariales |
| NOTA 2 | Firma del acreedor **fuera del despacho** por delegación | 🟥 por ley | art. 12 Dcto 2148/1983 (comp. 1069/2015) |
| NOTA 3 | Registro en 90 días / intereses moratorios tras 2 meses | 🟥 por ley | registro (Ley 1579) |
| NOTA 4 | Verificación de nombres y documentos por el compareciente | 🟦 estilo/operativo | — |
| NOTA 5 | Notificaciones electrónicas SI/NO + correo | 🟦 estilo (consentimiento) | habeas data |
| NOTA 6 | Paz y salvo de expensas (PH) / **identificación biométrica** | 🟥 por ley | art. 29 Ley 675 · art. 18 Dcto 019/2012 |
| NOTA 7 | Autorización tratamiento de datos + **STRADATA SEARCH** (SARLAFT) | 🟥 por ley | Circular SNR 1536/2013 · Ley 1581 · SIPLAFT |
| NOTA 8 | REDAM | 🟥 por ley | Ley 2097/2021 |

Notas adicionales situacionales observadas: identificación sin huella (art. 24 Dcto 960/1970), partes se conocieron personalmente (art. 9 Dcto 960/1970), paz y salvo de servicios públicos (Instr. Adm. 10/2004).

---

## 5. Ficha de firma / otorgamiento (estándar Notaría 16)

Campos por compareciente (unión de las 4 plantillas → **ficha canónica propuesta**):
`Nombre completo` · `Dirección` · `Municipio` · `Teléfono` · `Correo electrónico` · `Profesión u ocupación / Actividad económica` · `Estado civil` · `Autoriza notificaciones electrónicas: SÍ/NO` · `Persona expuesta políticamente (Dcto 1674/2016): SÍ/NO` · `Biometría`.

- Firman: vendedor(es), comprador(es), **cónyuge/compañero** (si afectación), **apoderado del acreedor** (si hipoteca), apoderados de parte (si los hay).
- **Constancia de fases (art. 13 Dcto 960):** *"Los exponentes leyeron personalmente el presente instrumento, lo aprobaron y en constancia lo firman"* + advertencia de registro. ⚠ Ninguna escritura enuncia las 4 fases explícitamente — el wizard ya lo hace mejor que el corpus real.
- **Hojas de papel notarial** (papel de seguridad): rango `{primera}`–`{última}` con leyenda `PASA A LA HOJA` / `VIENE DE LA HOJA` para continuidad de folio.
- **Firma del notario:** nombre + calidad (encargado/interino).

---

## 6. Variaciones entre protocolistas → propuesta de estándar único

**Lo idéntico entre las 4 plantillas (núcleo reutilizable directo):** TERCERO garantía, Parágrafo Ley 258 vendedor, CUARTO precio, precio real, origen de fondos/SARLAFT, QUINTO/SEXTO entrega y saneamiento, REDAM, STRADATA, constancia de verificación. → van al estándar como **texto fijo**.

**Lo que varía y hay que unificar:**

| Punto de divergencia | Velilla (A) | Orozco (B) | Ana María (C) | Suaza (D) | Estándar propuesto |
|---|---|---|---|---|---|
| Carátula | `COMPRAVENTA` + tablas | `ACTOS:` sin tablas | tablas + códigos | tablas + códigos | **Tabla naturaleza jurídica con códigos SNR** (más completa y registrable) |
| Base gravable ×4 | Sí | No | Sí | Sí | **Incluir siempre** (protege al notario) |
| Numeración origen ingresos | Par. 3 | Par. 2 | Par. 5.3 | Par. varios | Numeración estable por regla, no por persona |
| Notas de cierre | dispersas | dispersas | NOTAS 1–8 | NOTAS 1–8 | **NOTAS 1–8 numeradas** |
| Ficha de firma | 6 campos | 7 campos | 8 campos | 8 campos | **Ficha canónica de §5** (unión) |
| Correo notificaciones | del protocolista | del protocolista | — | del protocolista | Correo de la **notaría**, no del protocolista |

**Regla de oro del estándar:** el estándar único de la Notaría 16 = **esqueleto de §1** + **clausulado fijo del núcleo** + **módulos condicionales** (PH sí/no · afectación sí/no · financiado/contado · actos preliminares · minuta de entidad pública). El motor **exige** los mínimos 🟥 vía cumplimiento (obligatoria/bloqueante) y ofrece los 🟨 según el árbol de decisiones.

---

## 7. Irregularidades detectadas en el corpus (validan el problema que resolvemos)

Errores reales encontrados en las escrituras de producción de la 16 — exactamente los "dolores" que el ecosistema elimina al arrancar limpio desde datos+reglas en vez de reusar una escritura vieja:

1. **Carátula ≠ cuerpo:** EPM y Metro rotulan la hipoteca "abierta sin límite" pero la constituyen como "especial de primer grado por suma determinada".
2. **Numeración duplicada:** en Metro hay dos cláusulas "QUINTO" y dos "NOTA 7".
3. **Datos cruzados:** en Metro el comprador aparece con dos cédulas distintas (una es la del vendedor) — típico error de copy-paste de una minuta anterior.
4. **Campos sin diligenciar:** paz y salvos "el 00 de Julio de 2026".
5. **Coeficiente de copropiedad no transcrito** (solo "el porcentaje señalado en el reglamento").

→ **El informe de cumplimiento del motor** (matrícula/linderos bloqueante, valor real, retención 1%, origen de fondos, REDAM, afectación Ley 258) atrapa 1, 3, 4 y 5 antes de firmar. Refuerza el pitch "Hoy vs. Ecosistema".

---

## 8. Próximos pasos con este insumo
1. **Cargar el núcleo fijo** (§2 clausulado [FIJO]) como cláusulas `estilo/Notaría 16` en la biblioteca del editor.
2. **Mapear cada 🟥 al normograma** (`normograma-compraventa.md`) como regla obligatoria/bloqueante — ya casi todas están; añadir: NOTA 2 (art. 12 Dcto 2148), código SNR por acto, retención 1% explícita.
3. **Modelar los módulos condicionales** (PH, afectación, financiado, entidad pública) como ramas del árbol de compraventa.
4. **Acto 2 — Hipoteca:** usar §3 como base del wizard de hipoteca y del encadenamiento compraventa+hipoteca (comparecencia sucesiva + nexo forma de pago/entrega).
