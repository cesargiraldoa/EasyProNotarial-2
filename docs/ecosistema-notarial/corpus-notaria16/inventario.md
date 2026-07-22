# Inventario — Corpus Notaría 16 de Medellín

> Insumo para la **capa por notaría** (biblioteca de cláusulas + orden + notas + ficha de firma).
> Fuente: ZIP `NOTARIA 16 - MEDELLÍN` subido por el usuario (2026-07-20).
> **40 archivos · 5 protocolistas** (35 `.doc` binarios + 5 `.docx`).

_Última actualización: sesión 2026-07-20 (inventario inicial, antes de extracción de texto)._

## Resumen por tipo de acto

| # | Tipo de acto | Ejemplares | Relevancia roadmap |
|---|--------------|-----------:|--------------------|
| 1 | **Compraventa** (venta simple) | 4 | Acto piloto (validado) |
| 2 | **Compraventa + Hipoteca** (encadenamiento) | 9 | Acto piloto + Acto 2 + encadenamiento |
| 3 | **Hipoteca** (sola, a banco/entidad) | 2 | **Acto 2 (hipoteca)** |
| 4 | **Cancelación de hipoteca** | 5 | Acto futuro |
| 5 | **Cancelación de patrimonio de familia** | 5 | Acto futuro |
| 6 | **Donación / Insinuación + Donación** | 3 | Acto futuro |
| 7 | **Venta de nuda propiedad** | 1 | Variante de compraventa |
| 8 | **Sucesión** | 1 | Acto futuro |
| 9 | **Aporte a sociedad** | 2 | Acto futuro |
| 10 | **Liquidación soc. conyugal / renuncia a gananciales** | 1 | Acto futuro |
| 11 | **Leasing** (habitacional/inmobiliario) | 6 | Acto futuro |
| 12 | **Minuta semilla — vivienda** | 1 | Plantilla banco/vivienda |
| | **TOTAL** | **40** | |

## Detalle por protocolista

### ALEJANDRA VELILLA (5)
- Compraventa — `VENTA- EDISON DAVID a YENNY.doc`
- Compraventa — `VENTA-GILMA AYDEE.doc`
- Compraventa — `VENTA-JUAN JOSE - DR. DANIEL CASTAÑEDA.doc`
- Venta de nuda propiedad — `VENTA NUDA PROPIEDAD _ BIFRANCY.doc`
- Sucesión — `SUCESION JOSE GUSTAVO- DR. ALFONSO MARIN.doc`

### ALEXANDRA MARÍA SUAZA VILLA (5)
- Compraventa + Hipoteca (no PH) — `MINUTA COMPRAVENTA Y CONSTITUCION HIPOTECA A COOSANLUIS - NO PH.doc`
- Compraventa + Hipoteca (a EPM) + afectación viv. familiar + renuncia cond. resolutoria — `EPM.docx`
- Compraventa + Hipoteca (a Metro de Medellín) + afectación viv. familiar + aclaración — `MINUTA METRO - DIEGO FERNANDO MEJIA OBANDO.doc`
- Aporte a sociedad — `APORTE.docx`
- Leasing — `LEASING.doc`

### ANA MARÍA (23) — la carpeta más rica, organizada por sub-acto
**Venta e Hipoteca (6):**
- `FELIPE MEJIA GOMEZ.doc`, `IVAN DARIO FLOREZ GUERRERO.doc`, `JUAN CAMILO HENAO TORRES.doc`, `PAULA ANDREA VERA GUTIERREZ.doc`, `XIOMARA BERRIO CALLEJAS - EMPLEADA.doc`, `YOLIMA MARIA BOTERO ARANGO.doc`

**Cancelación de hipoteca (5):**
- `ANGELICA MARIA ROMAN RUIZ - PAULINA BELTRAN.doc`, `CLAUDIA MARCELA MARROQUIN Y NELSON ANIBAL OCHOA...doc`, `JORGE ENRIQUE MARIN HERNANDEZ y SEBATIAN MARIN GAVIRIA.doc`, `LUIS FERNANDO ALZATE MOLINA y JHON ALEXANDER ALZATE MARIN.doc`, `MARIA CLARA GIRALDO ACEVEDO y DIEGO ALEXIS NARANJO USUGA BANCO ITAU.doc`

**Cancelación de patrimonio de familia (5):**
- `CESAR ANTONIO SALINAS AGUDELO - 2.doc`, `DANIEL ADOLFO OCAMPO MARIN 2.doc`, `DANIEL VANEGAS COSSIO y GUSTAVO ANDRES QUINTANA COSSIO 2.doc`, `FELIPE MEJIA GOMEZ II CON HIJOS SIN HIPOTECA.doc`, `FRANK ALEJANDRO RAMIREZ RAMIREZ - 2.doc`

**Leasing (4):**
- `LEASING SUSANA MARCELA PEREZ GUERRA y WILMAR LOPEZ CASTAÑO.doc`, `LEASING SUSANA - LEISON DE J. MONTOYA.doc`, `LINA ISABEL DUARTE RODRIGUEZ.doc`, `LUISA FERNANDA FORONDA CORREA.doc`

**Varios actos (3):**
- Aporte a sociedad — `000 -APORTE - INVERGORA S.A.S. - ULTIMA.doc`
- Insinuación + Donación — `INSINUACION Y DONACION CONSUELITO.doc`
- Liquidación soc. conyugal / renuncia a gananciales — `LIQ.S.C. - RENUNCIA A GANANCIALES - JULIANA y DIEGO - DEFINITIVA.doc`

### JUAN CAMILO OROZCO (4)
- Compraventa — `VENTA-NORBEY SANCLEMENTE CARDONA.doc`
- Hipoteca (a Bancolombia) — `HIPOTECA BANCOLOMBIA - ALEJANDRO CASTRO BUITRAGO Y OTROS.doc`
- Donación — `DONACION - LUISA FERNANDA CARDONA SANCHEZ.doc`
- Insinuación + Donación (nuda propiedad) — `INSINUACION – DONACION (NUDA PROPIEDAD) - LILIA SEPÚLVEDA VALENCIA.doc`

### YURANI NARVAEZ (3) — minutas semilla
- Hipoteca — `HIPOTECA.docx`
- Leasing — `MINUTA DE LEASING.docx`
- Vivienda (semilla banco) — `MINUTA DE VIVIENDA.docx`

## Notas de método (para la fase de extracción)
- **`.doc` binarios (35):** `strings <archivo>.doc` extrae el texto legible al instante (línea ACTOS, comparecencia, cláusulas). LibreOffice headless funciona pero arranca demasiado lento en este entorno — usar `strings` como vía principal y LibreOffice solo si se necesita formato/tablas.
- **`.docx` (5):** extracción por descompresión ZIP + regex sobre `word/document.xml` (ya probado).
- **Encadenamientos frecuentes:** la compraventa casi nunca va sola — se encadena con hipoteca, afectación a vivienda familiar, renuncia a condición resolutoria, aclaración. Confirma la decisión de diseño "los actos se encadenan".

## Próximo paso
Extracción de texto de los 40 documentos → clasificación de cada cláusula/nota en **dos capas** (por-ley → normograma compartido · estilo/orden → capa Notaría 16) → detección de variaciones entre protocolistas → propuesta de estándar único. Empezar por **compraventa** y **compraventa+hipoteca** (13 documentos) por ser el acto piloto y el acto 2.
