# Verificación contra fuentes oficiales — corpus jurídico maestro

> **Propósito.** Antes de consolidar el mapa legal-normativo (Issue #132 + `normograma-compraventa.md` + `mapa-situaciones.md`) en un maestro versionado, se verificó contra fuentes oficiales el estado, los artículos y las fechas de las normas y jurisprudencia marcadas `POR_VERIFICAR` y las de 2025–2026. Este documento es la **capa de verificación**: cada afirmación del maestro debe apoyarse en una fila de aquí.
>
> _Fecha de verificación: 2026-07-21._

---

## ⚠ Advertencia metodológica (leer antes de usar)

La verificación se hizo con búsqueda web + lectura de fuentes oficiales. **Los portales oficiales (`suin-juriscol.gov.co`, `funcionpublica.gov.co`, `secretariasenado.gov.co`, `corteconstitucional.gov.co`, `dian.gov.co`, `igac.gov.co`) devolvieron HTTP 403 a la lectura automatizada** (rechazo del agente, no del proxy). Por eso muchos ítems se corroboraron mediante **extractos oficiales indexados por el buscador y fuentes concordantes**, no por apertura íntegra del PDF.

**Regla de uso:** los ítems de confianza **Alta** son fiables para diseño; los de confianza **Media/Baja** y toda la lista **NO CONFIRMADO** deben cerrarse **abriendo manualmente el Diario Oficial / SUIN-Juriscol** antes de codificarlos como regla bloqueante o de imprimirlos en una escritura real. La IA detecta y cita; **no reemplaza la validación del notario**.

---

## 1. Correcciones a lo que YA teníamos (impacto directo)

Estas verificaciones **corrigen o precisan** nuestro `normograma-compraventa.md` y el prototipo `escritura-asistida.html`:

| # | Lo que teníamos | Corrección verificada | Confianza | Acción |
|---|---|---|---|---|
| C1 | NOTA de registro "2 meses" citada como **Ley 1579/2012** (en compraventa y en cancelación de hipoteca) | El término de **2 meses** (3 si se otorgó en el exterior) e **intereses moratorios** los fija el **art. 231 de la Ley 223/1995** (reglamentado por Dcto 650/1996), **no** la Ley 1579. En la Ley 1579, el art. 27 fija el trámite interno (5 días hábiles) y el **art. 28** un término especial de **90 días hábiles** para hipoteca y patrimonio de familia. | **Alta** | Cambiar la cita de esa NOTA a `art. 231 Ley 223/1995` en ambos actos. |
| C2 | Cancelación NOTA 1 citaba `art. 12 Dcto 2148/1983` (compilado en 1069/2015), sin el artículo exacto | Equivalente vigente confirmado: **art. 2.2.6.1.2.1.5 del Decreto 1069/2015** ("Suscripción de instrumentos fuera de la sede de la notaría"). El Dcto 2148/1983 fue **derogado íntegramente y compilado** en el 1069/2015. | **Alta** | Citar `art. 2.2.6.1.2.1.5 Dcto 1069/2015 (ex art. 12 Dcto 2148/1983)`. |
| C3 | Retención en la fuente a **persona jurídica** vendedora: `POR_VERIFICAR` | Cuando el vendedor es persona jurídica, el **notario NO es agente retenedor**: retiene el **comprador** (art. 401 E.T., parágrafo), con pago previo a la escritura (recibo DIAN form. 490). Tarifa general de "otros ingresos" ~2,5% (a confirmar según operación). | **Media** | Ramificar la liquidación: vendedor natural → retención 1% por el notario; vendedor jurídico → sin retención notarial. |
| C4 | Exención casa de habitación: normograma decía "hasta 5.000 UVT (art. 311-1)" | Confirmado: **5.000 UVT** (reducido desde 7.500 por la **Ley 2277/2022, art. 31**); condición: depósito en cuenta **AFC** y destino a otra vivienda o crédito hipotecario. Se eliminó el tope por valor catastral. | **Alta** | Mantener; añadir la condición AFC. |
| C5 | Dcto 0732/2026: normograma decía que "sustituye" el régimen anterior (1227/2015) | Preciso: el Dcto 0732/2026 **modifica el Decreto Único 1069/2015** (donde estaba compilado el 1227/2015); funcionalmente lo reemplaza. 4 variables F/M/NB/T; gratuidad. Responde a T-033/2022. | **Alta** (contenido) / **Media** (fecha) | Redactar como "modifica el DUR 1069/2015", no "deroga el 1227". |

---

## 2. Confirmaciones (base para el maestro)

### 2.1 Núcleo civil / registral / notarial

| Norma | Dato confirmado | Fuente | Confianza |
|---|---|---|---|
| **Dcto 1069/2015, art. 2.2.6.1.2.1.5** | Suscripción de instrumentos fuera de la sede (ex art. 12 Dcto 2148/1983) | funcionpublica i=5227; cancilleria decreto_1069_2015_pr029 | Alta |
| **Ley 1579/2012, art. 8** | Definición del folio de matrícula inmobiliaria | secretariasenado ley_1579_2012; SUIN id=1684387 | Alta |
| **Ley 1579/2012, art. 16 (par. 1)** | No se inscribe si el inmueble no está plenamente identificado (matrícula, linderos, área) y las partes por su documento → causal de devolución | igac ley_1579_de_2012.pdf; secretariasenado | Alta |
| **Ley 223/1995, art. 231** | Término de registro 2 meses (país) / 3 (exterior) + intereses moratorios | secretariasenado ley_0223_1995_pr004; funcionpublica i=6968 | Alta |
| **Ley 258/1996, art. 3** | Enajenar/gravar inmueble afectado a vivienda familiar exige consentimiento libre de **ambos cónyuges** (doble firma) | SUIN id=1657012; funcionpublica i=10794 | Alta |
| **Ley 258/1996, art. 6** | Deber del notario de indagar bajo juramento sobre matrimonio/unión y afectación | (mismas URLs Ley 258) | Alta |
| **Ley 854/2003** | Modificó el **art. 1** de la Ley 258 (no el art. 3) | funcionpublica | Alta |
| **C.C. art. 2457** | La hipoteca se extingue, entre otras, "por la cancelación que el acreedor acordare por escritura pública, de que se tome razón al margen de la inscripción" | secretariasenado codigo_civil_pr076 | Alta |
| **Dcto 1712/1989** | Insinuación de donación **> 50 SMLMV**: autorización por escritura; exige prueba del valor comercial, calidad de propietario y congrua subsistencia del donante | SUIN 1335778; normograma.mincultura | Alta |
| **C.C. art. 1931 (Ley 45/1930)** | Entregada la cosa, el comprador se hace dueño **aunque se pacte reserva de dominio**; el pacto opera como **condición resolutoria**. Sobre inmuebles la reserva **no** suspende la transferencia (eficacia real solo en muebles no fungibles inscritos, C.Co. 952 ss). | leyes.co codigo_civil; accesoalajusticia | Media/Baja |

### 2.2 Tributario de la compraventa (cifras 2026)

| Concepto | Norma | Dato 2026 | Fuente | Confianza |
|---|---|---|---|---|
| Retención enajenación (persona natural, activo fijo) | Art. 398 E.T. | **1%** del valor, recaudada por el notario, previa a la escritura | secretariasenado estatuto_tributario_pr012 | Alta |
| Disminución retención (casa de habitación) | Art. 399 E.T. | −10% por cada año entre compra y venta | secretariasenado | Media |
| Retención venta por persona jurídica | Art. 401 E.T. | Notario no retiene; retiene el comprador; pago previo a escritura | secretariasenado estatuto_tributario_pr013 | Media |
| Ganancia ocasional (activo fijo ≥ 2 años) | Arts. 300, 313 E.T. (Ley 2277/2022) | **15%** | funcionpublica i=199883 | Alta |
| Exención casa de habitación | Art. 311-1 E.T. (Ley 2277/2022) | **5.000 UVT** + cuenta AFC | secretariasenado; DIAN Concepto 820/006970 | Alta |
| Impuesto de registro | Ley 223/1995 arts. 226–235 + ordenanza Antioquia | Con cuantía 0,5–1%; **Antioquia 1%**; base ≥ avalúo catastral | funcionpublica i=6968 | Media |
| Derechos notariales 2026 | **Res. SNR 2026-000964-6** (20-ene-2026) | Rige 1-feb-2026; IPC **5,10%**; **3 por mil** + mínimo | supernotariado.gov.co (noticia tarifas) | Media |
| Descuento VIS/VIP | Res. SNR tarifas 2026 | **−50%** en derechos notariales | supernotariado | Media |
| IVA sobre derechos notariales | Art. 468 E.T. | **19%** sobre los derechos (no sobre el precio) | secretariasenado estatuto_tributario_pr019 | Alta |
| Descuento crédito hipotecario | **Ley 2434/2024** | **30%** de descuento en derechos por crédito hipotecario de largo plazo, antes de calcular IVA | (por confirmar en texto) | Media |
| UVT 2026 | Res. DIAN 000238 (15-dic-2025) | **$52.374** | dian.gov.co | Alta |
| SMLMV 2026 | Dcto 1469/2025 (+ Dcto transitorio 0159/2026) | **$1.750.905** (+ transporte $249.095) | presidencia.gov.co | Media |

### 2.3 Normas recientes y jurisprudencia (marco maestro)

| Norma/Sentencia | Confirmado | Fuente | Confianza |
|---|---|---|---|
| **Dcto 0732/2026** | Corrección componente sexo (F/M/NB/T); modifica DUR 1069/2015; gratuidad; responde a T-033/2022 | minjusticia; SUIN id=30055407 | Alta (contenido) / Media (fecha) |
| **Dcto 906/2025** | Exención de derechos por copias digitales para la **ANT** (Ley 160/1994, DL 902/2017) y donaciones de predios a resguardos/Fondo de Tierras — alcance acotado, no exención general | funcionpublica i=262136 | Alta (alcance) / Media (fecha) |
| **Ley 2447/2025** | Prohíbe matrimonio y unión con menores de 18 (sin excepción) | funcionpublica i=258236; Cámara | Alta (existencia) / Baja (fecha) |
| **C-039/2025** | Inconstitucional el matrimonio/unión de menores de 18; edad mínima 18 | corteconstitucional c-039-25 | Alta (decisión) / Media (fecha) |
| **Ley 2442/2024** | Divorcio por voluntad unilateral → **ruta judicial** (no notarial) | Rama Judicial LEY 2442; Alcaldía Bogotá i=171777 | Alta |
| **C-159/2021** | Inexequibles arts. 59–63 Dcto 2106/2019 (escritura electrónica); **efectos desde 20-06-2023** | corteconstitucional c-159-21; SUIN id=30041794 | Alta |
| **C-193/2016** | Eliminó el plazo de "un año" para la UMH (Ley 54/1990 art. 2 lit. b); mantuvo disolución previa de sociedad conyugal | corteconstitucional C-193-16; SUIN id=30032816 | Alta |
| **SU-214/2016** | Notarios deben celebrar matrimonio civil de parejas del mismo sexo | corteconstitucional su214-16 | Alta |
| **C-112/2000** | Matrimonio ante notario del domicilio de **cualquiera** de los contrayentes (inexequible "de la mujer") | corteconstitucional C-112-00; SUIN id=20007801 | Alta (decisión) / Media (día) |
| **Ley 160/1994, art. 72** | Restringe adquisición/acumulación de baldíos adjudicados por encima de una UAF; nulidad de actos que superen el límite | funcionpublica i=66789 | Alta |

---

## 3. NO CONFIRMADO — cerrar antes de codificar como regla dura

1. **Derecho mínimo notarial 2026 (valor exacto en pesos)** y tabla de rangos — abrir la Resolución SNR 2026-000964-6.
2. **Ordenanza tarifaria de Antioquia vigente 2026** (el 1% es histórico/consistente, falta la ordenanza específica del año).
3. **Tarifa exacta de retención para venta por persona jurídica** (el 2,5% es la general de compras; verificar según operación).
4. **Sentencia concreta de la Corte Suprema (Sala Civil)** sobre eficacia de la reserva de dominio en inmuebles (radicado) — la doctrina está confirmada, la providencia no.
5. **Artículo exacto de la sanción de nulidad absoluta** en la Ley 258/1996 (la sanción existe; su ubicación exacta —¿parágrafo del art. 3?— no quedó fijada).
6. **Fechas exactas de Diario Oficial:** Ley 2447/2025 (sanción/vigencia), Dcto 0732/2026, Dcto 906/2025; y día/parte resolutiva literal de C-039/2025.
7. **Ley 2434/2024** — texto del descuento del 30% en derechos por crédito hipotecario (confirmar artículo).

---

## 4. Qué cambia esto para el Issue #132 y el maestro

- **Valida** el grueso de #132: las familias, las reglas "no procede" y la jurisprudencia citada se corroboraron (con las precisiones de fecha anotadas).
- **Precisa** dos citas que #132 y nuestro normograma traían aproximadas: el término de registro (Ley 223/1995 art. 231, no Ley 1579) y el artículo vigente de la firma fuera de sede (2.2.6.1.2.1.5 Dcto 1069/2015).
- **Confirma** la arquitectura de datos propuesta en #132 (§8): `legal_sources` con estado doble `vigencia_formal`/`aplicabilidad_operativa`, versión por fecha de otorgamiento, y `non_proceed_rules` con severidad. Este documento es el primer lote de `legal_sources` verificados.
- **Deja lista** la corrección de las 5 filas de la §1 para aplicarlas al prototipo cuando se retome el desarrollo.
