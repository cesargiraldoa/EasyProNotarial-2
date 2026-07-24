# Estructura del molde

## El HTML

Imita **siempre** un molde existente como patrón (son el estándar de oro; si tienes
acceso al repo, míralos en
`backend/app/seeds/templates/plantillas-semilla/*.html`). Estructura general:

```html
<!--
  Comentario de cabecera: fuente (qué escritura real), banco, acto, ciudad, y las
  convenciones de condicionalidad usadas. Documenta que el texto legal es verbatim.
-->
<article class="escritura" lang="es">

  <header class="caratula">
    <p class="titulo-escritura">ESCRITURA PÚBLICA NRO. {{numEscritura}}</p>
    <p class="acto">COMPRAVENTA, … <!-- [[if credito]] -->, HIPOTECA … <!-- [[/if]] --><!-- [[if afect in si]] --> y AFECTACIÓN A VIVIENDA FAMILIAR<!-- [[/if]] -->.</p>
    <p>Otorgada por: {{V.0.nombre}}.</p>
    <p>A favor de: {{C.0.nombre}}.</p>
    <!-- [[if credito]] --><p>Hipoteca a favor de: BANCO XXXX S.A.</p><!-- [[/if]] -->
  </header>

  <section class="snr formato-calificacion">
    <h2>SUPERINTENDENCIA DE NOTARIADO Y REGISTRO</h2>
    <!-- folio, catastral, nupre, tabla de naturaleza jurídica del acto … -->
  </section>

  <!-- Cláusulas: PRIMERO objeto, SEGUNDO tradición, TERCERO saneamiento, precio,
       entrega, gastos … cada una en <p class="cl"> con <span class="clh">TÍTULO:</span> -->

  <!-- [[if credito]] --> …toda la sección de hipoteca… <!-- [[/if]] -->

  <!-- OTORGAMIENTO, AUTORIZACIÓN, NOTAS, ANEXOS, AVALÚO, FIRMAS -->
</article>
```

Clases CSS que usa el sistema (respétalas): `escritura`, `caratula`,
`titulo-escritura`, `acto`, `snr`, `formato-calificacion`, `cl` (cláusula),
`clh` (encabezado de cláusula, en negrita), `para` (parágrafo), `epigrafe`,
`nota-hueco` (para los huecos de datos no capturados). El banco va **fijo** en el
texto (BANCO DAVIVIENDA S.A., BANCOLOMBIA S.A., …).

## El `.map.json`

```json
{
  "name": "Davivienda · Medellín · Compraventa + Hipoteca (semilla)",
  "acto": "hipoteca",
  "fuente": "banco",
  "bank_nit": "860.034.313-7",
  "bank_name": "Banco Davivienda S.A.",
  "notaria": "Notaría Dieciséis de Medellín",
  "descripcion": "Breve: qué escritura la originó, banco acreedor, y particularidades (PH, afectación, VIS…).",
  "condicionales": [
    { "marca": "[[if credito]]", "campo": "credito", "descripcion": "Toda la hipoteca…" },
    { "marca": "[[if afect in si]]", "campo": "afect", "descripcion": "Afectación a vivienda familiar (cód. 304)…" }
  ],
  "no_capturado_por_tokens": [
    "Notario/encargado que autoriza.",
    "Cónyuge del comprador (no hay campo)."
  ],
  "tokens": [
    { "token": "numEscritura", "label": "Número de escritura", "field": "numEscritura", "section": "encabezado" },
    { "token": "matricula", "label": "Folio de matrícula", "field": "matricula", "section": "inmueble" }
  ]
}
```

Reglas:
- `acto`: `"hipoteca"` para compraventa+hipoteca, `"compraventa"` para compraventa
  sola, `"cancelacion"` para cancelación.
- `fuente`: `"banco"` si hay banco acreedor; `"particular"` si es genérico sin banco.
- `bank_nit`: el NIT tal cual (con puntos y guion). El sistema lo empareja al banco
  del catálogo. Sin banco → omite `bank_nit`/`bank_name`.
- `tokens`: incluye un objeto por cada token que USASTE en el HTML (mismo formato
  que arriba). Es la lista que ve el sistema; que coincida con el HTML.
- El `<slug>` de los archivos = `banco-ciudad-acto`, en minúsculas con guiones
  (`davivienda-medellin-compraventa-hipoteca`). El `.html` y el `.map.json`
  comparten el mismo slug.
