# Normograma verificado — Compraventa de inmueble

Corpus normativo de la compraventa. Cada norma con estado de vigencia (verificado contra fuente oficial, jul-2026),
artículos clave, qué exige en la escritura y fuente. Insumo directo de las tablas `norma` / `clausula` / `regla` del backend.

**Estados:** `VIGENTE` · `VIGENTE_MODIFICADA` · `COMPILADA` · `DEROGADA` · `INEXEQUIBLE` · `POR_VERIFICAR`

> Prototipo visual: `prototipos/normograma-compraventa.html`. Verificación por búsqueda restringida a fuentes oficiales; el acceso directo a portales `.gov.co` estuvo bloqueado (403), por lo que el contenido proviene de extractos oficiales indexados. Validación jurídica final: el notario.

## 1. Núcleo notarial y registral

### Decreto-Ley 960 de 1970 — Estatuto del Notariado · `VIGENTE_MODIFICADA`
- **Art. 13:** la escritura pública se perfecciona en cuatro fases: recepción, extensión, otorgamiento y autorización.
- **Art. 14:** define cada fase; la autorización es la fe que imprime el notario verificados los requisitos.
- Todo acto de disposición o gravamen de inmueble consta en escritura pública.
- **Exige:** constancia de las 4 fases, identificación plena, incorporación al protocolo, autorización notarial.
- **Fuente:** Gestor Normativo i=149249 · SUIN 1692245.
- *Verificado:* la Ley 2466/2025 es reforma laboral, no afecta al notariado (falsa alarma descartada).

### Decreto 2148 de 1983 — Reglamento notarial · `DEROGADA` (COMPILADA en Dcto 1069/2015)
- Derogado como norma autónoma; su articulado subsiste compilado en el Decreto 1069/2015. **Citar el 1069/2015.**
- Materias: documentos que se transcriben/protocolizan, firma/numeración/fecha, poderes, identificación del inmueble en poderes especiales, segregaciones.
- **Fuente:** Gestor i=5227 · SUIN 1408127.

### Decreto 1069 de 2015 — DUR Sector Justicia · `VIGENTE`
- Compila la reglamentación notarial (Libro 2, Parte 2). Norma vigente para otorgamiento/autorización, protocolización, poderes y segregaciones.
- **Fuente:** Gestor i=74174. *POR_VERIFICAR:* numeración interna exacta equivalente al 2148/1983.

### Ley 1579 de 2012 — Estatuto de Registro de Instrumentos Públicos · `VIGENTE`
- **Art. 4:** títulos sujetos a registro (todo acto que constituya, modifique, grave o extinga dominio).
- **Art. 8:** matrícula inmobiliaria (código, oficina, municipio, cédula catastral, urbano/rural, linderos, cabida).
- **Art. 16:** calificación; no procede registro si el inmueble no está plenamente identificado y las partes por su documento → nota de devolución (**causal de rechazo**).
- **Art. 18:** suspensión. **Art. 22:** devolución/inadmisión. **Art. 104:** derogó el Decreto 1250/1970.
- **Fuente:** Gestor i=49731 · SUIN 1684387.

## 2. Sustantivo civil (Código Civil) · `VIGENTE`
- **Art. 1849:** el precio de la compraventa debe pactarse en dinero.
- **Art. 1857:** la venta de bienes raíces solo se perfecciona con escritura pública (solemnidad).
- **Arts. 1893 ss.:** saneamiento por evicción (art. 1913: prescribe en 4 años).
- **Arts. 1914-1915:** vicios redhibitorios.
- **Art. 1546:** condición resolutoria tácita en contratos bilaterales.
- **Art. 1939:** pacto de retroventa (plazo máx. 4 años).
- **Arts. 2445-2446:** extensión de la hipoteca a mejoras y aumentos.

## 3. Cargas, protecciones y capacidad

### Ley 258 de 1996 (mod. Ley 854 de 2003) — Afectación a vivienda familiar · `VIGENTE_MODIFICADA`
- **Art. 3:** enajenar/gravar bien afectado requiere consentimiento (firma) de **ambos** cónyuges/compañeros — so pena de nulidad (**BLOQUEANTE**).
- **Art. 6:** el notario indaga estado civil y afectación; declaración bajo juramento.
- Ley 854/2003 modificó los arts. 1 y 4 de la Ley 258; la referencia a unión marital está en el art. 6 de la Ley 258 (no la agregó la 854).
- **Fuente:** Gestor i=10794 (258), i=10793 (854) · Sent. C-192/1998.

### Ley 675 de 2001 (mod. Ley 2079 de 2021) — Propiedad horizontal · `VIGENTE_MODIFICADA`
- **Arts. 25-26:** coeficientes de copropiedad (sobre área privada).
- **Art. 29:** expensas comunes; el notario exige **paz y salvo de administración**; de no obtenerse, constancia + **solidaridad del nuevo propietario**.
- Bienes comunes inseparables del privado; se transfieren con la unidad.
- **Fuente:** Gestor i=4162 · SUIN 1665811.

### Patrimonio de familia — Ley 70/1931 · Ley 495/1999 (+ VIS: Ley 91/1936, Ley 861/2003) · `VIGENTE`
- Constitución por escritura pública (tope 250 SMLMV; dominio pleno, sin proindiviso ni hipoteca).
- Cancelación en la misma forma: escritura con ambos cónyuges o judicial; con menores → autorización judicial.
- Si existe: **cancelar antes de vender** (BLOQUEANTE). En VIS: constituir en la misma escritura.
- **Fuente:** Gestor i=39265, i=38938.

### Ley 54/1990 (mod. Ley 979/2005) — Unión marital y sociedad patrimonial · `VIGENTE_MODIFICADA`
- Presunción de sociedad patrimonial con unión marital ≥ 2 años; declaración/liquidación por escritura.
- Sent. C-075/2007: aplica a parejas del mismo sexo.
- **Exige:** indagar estado civil real (conecta con art. 6 Ley 258); si es bien social, consentimiento del compañero.

### Decreto 0732 de 2026 — Componente "sexo" en documentos de identidad · `VIGENTE`
- Reglamenta la actualización del componente **sexo** e incorpora **4 categorías**: Femenino (F), Masculino (M), No Binario (NB) y Transgénero (T). Desarrolla la exhortación de la **Sent. C.C. T-033 de 2022**.
- El trámite se surte **ante notario** (manifestación de voluntad; sin certificados médicos/psicológicos; primera actualización gratuita) y luego se actualiza ante la Registraduría.
- **Exige (para el motor):** capturar el género en las 4 categorías por persona y **concordar la redacción** de la escritura (identificad{o/a/e}, domiciliad{o/a/e}, estado civil, artículos el/la/le). NB y T → lenguaje incluyente (‑e).
- **Fuente:** Min. Justicia (comunicado, jul-2026).

### Ley 1996 de 2019 — Capacidad legal y régimen de apoyos · `VIGENTE`
- **Art. 6:** capacidad plena; **eliminó la interdicción**.
- **Arts. 15-16:** acuerdos de apoyo (por escritura; el notario entrevista por separado).
- **Exige:** compareciente con discapacidad = plenamente capaz; si usa apoyos, acreditar acuerdo/adjudicación.
- **Fuente:** Gestor i=99712 · Sent. C-022/2021, C-025/2021, C-052/2021.

## 4. Tributario y prevención de lavado

### Art. 90 E.T. (mod. art. 61 Ley 2010/2019) — Valor real · `VIGENTE`
- Declaración bajo juramento: precio real, sin pactos privados, sin sumas por fuera. Base ≥ costo/avalúo/autoavalúo (art. 72).
- Omitir la declaración → base de **4 veces** (renta, ganancia ocasional, impuesto de registro, derechos notariales).

### Ganancia ocasional — arts. 300, 311-1, 313 E.T. (mod. Ley 2277/2022) · `VIGENTE`
- Utilidad con posesión ≥ 2 años → **15%** (no el 10% derogado). Posesión < 2 años → renta ordinaria.
- Exención casa de habitación: primeras **5.000 UVT** (avalúo ≤ 15.000 UVT); condición de cuenta AFC o pago directo del crédito.

### Ley 223 de 1995 (arts. 226-235) — Impuesto de registro · `VIGENTE`
- Hecho generador: inscripción en ORIP. Base: valor del documento, no inferior a avalúo/autoavalúo. Tarifa: Asambleas Departamentales, **0,5%-1%** (1% en Antioquia).

### Arts. 398-399 E.T. — Retención en la fuente · `VIGENTE`
- **Art. 398:** enajenación de activo fijo por persona natural → **1%**, ante el notario (agente retenedor), previa a la enajenación.
- **Art. 399:** reducción para casa/apto de habitación adquirida antes del 1-ene-1987. No aplica a activo movible (constructor).

### Ley 2195 de 2022 + SIPLAFT notarial · `VIGENTE`
- Marco: Circular SNR 1536/2013 + Instrucciones 17/2016 y 08/2017 + Circular 1754/2017 (la "SARLAFT 2.0" de 2024 es de Supervigilancia, **no** aplica a notarías).
- **Exige:** declaración de origen lícito de fondos + actuar por cuenta propia / beneficiario final. Dcto 830/2021: beneficiario final y PEP.

### Tarifas notariales y registrales 2026 (se actualizan cada año por resolución)
- Notarial: **Res. RES-2026-000964-6** (vig. 1-feb-2026, ajuste IPC 5,10%). Actos con cuantía ≤ $189.700: $22.500; sobre el excedente, **3 por mil**. VIS/VIP: **−50%**. + **IVA 19%** sobre los derechos notariales.
- Registral: **Res. RES-2026-001726-6** (vig. 2-feb-2026; UVB 2026 = $12.110).

## 5. Vivienda de interés social

### Ley 2079 de 2021 (art. 13) + Ley 3/1991 + Dcto 1077/2015 — Restricción VIS · `VIGENTE_MODIFICADA`
- Restricción de enajenación hoy: **5 años** (antes 10) y **solo** para vivienda entregada 100% en especie (SFVE); demás modalidades exentas.
- Condición resolutoria por revocatoria del subsidio; anotación registral; patrimonio de familia inembargable.
- **Fuente:** Gestor i=160946 · Minvivienda ER0015805/2021.

## 6. Alerta transversal de vigencia

### Arts. 59-63 Decreto 2106 de 2019 — Escritura pública electrónica · `INEXEQUIBLE`
- Sent. **C-159 de 2021** los declaró inexequibles (el art. 59 habilitaba actos notariales electrónicos), efectos desde el **20-jun-2023**.
- **Regla de oro:** el motor nunca inserta cláusula basada en artículo inexequible. No ofrecer la vía electrónica.
- **Fuente:** Corte Constitucional C-159-21 · Gestor i=189866.

## Reglas bloqueantes de la compraventa (impiden otorgar)
1. Bien afectado a vivienda familiar sin firma de ambos — art. 3 Ley 258/1996.
2. Patrimonio de familia vigente no cancelado — Ley 70/1931 · 495/1999.
3. Inmueble no plenamente identificado (matrícula/linderos) — art. 16 Ley 1579/2012.
4. Embargo/medida cautelar (objeto ilícito) — art. 1521 C.C. · CGP 593.
5. Leasing habitacional vigente (la entidad es la propietaria) — Ley 795/2003.

## Pendientes de verificación (`POR_VERIFICAR`)
- Numeración interna del Dcto 1069/2015 equivalente al 2148/1983.
- Eficacia de la reserva de dominio sobre inmuebles.
- Retención en la fuente a personas jurídicas (base/tarifa).
- Umbrales UIAF de reporte de efectivo.
- Restricciones a extranjeros en zonas de frontera.
- Validación jurídica final por el notario.

## Normas nuevas que salieron del mapa (siguientes a incorporar/verificar)
Ley 160/1994 (agrario/UAF/baldíos), EOSF y Ley 795/2003 (leasing/fiducia), régimen cambiario (no residentes), Ley 1682/2013 (bienes públicos), Ley 397/1997 (BIC), CGP (sucesiones), Ley 1561/2012 (saneamiento/falsa tradición), Ley 1537/2012 (VIS), Ley 2277/2022 (ganancia ocasional).
