---
name: molde-maker
description: >-
  Convierte una minuta notarial colombiana real (.docx o .doc) en un MOLDE
  (plantilla semilla) listo para EasyProNotarial: un cuerpo HTML parametrizado
  con {{tokens}} y condicionales [[if ...]], más su archivo .map.json. Úsala
  SIEMPRE que te pasen una escritura/minuta de compraventa, hipoteca, compraventa
  + hipoteca o cancelación de hipoteca (de cualquier banco: Bancolombia,
  Davivienda, BBVA, etc.) y haya que "hacer el molde", "templatizar", "marcar los
  campos variables", "convertir el docx a plantilla" o "cargar el molde de X
  banco". Conserva el texto legal VERBATIM y reemplaza solo los datos que cambian
  entre casos por tokens. No adivina a ciegas: sigue un vocabulario fijo de tokens
  y se autovalida antes de entregar.
---

# Molde Maker — de minuta real a plantilla semilla

## Qué produce y por qué

EasyProNotarial genera escrituras rellenando **moldes**: un cuerpo HTML donde los
datos que cambian caso a caso (nombres, cédulas, matrícula, montos…) están como
`{{tokens}}`, y las secciones que aparecen o no según el caso están envueltas en
`[[if ...]] … [[/if]]`. El formulario del sistema rellena esos tokens en vivo.

Tu trabajo: tomar la **minuta real de una notaría** (un .docx con un caso ya
diligenciado) y devolver **dos archivos**:

1. `<slug>.html` — el cuerpo del molde (texto legal **verbatim** + `{{tokens}}` + `[[if]]`).
2. `<slug>.map.json` — metadatos (banco, acto, notaría) + la lista de tokens.

El `<slug>` es descriptivo: `davivienda-medellin-compraventa-hipoteca`.

**El principio que hace esto confiable:** no intentas *adivinar* qué es variable.
Reemplazas **solo** los datos concretos de ESTE caso que corresponden a un token
del vocabulario conocido (`references/tokens.md`). Todo lo demás —cláusulas, notas,
lenguaje legal— se copia **letra por letra**. Un molde correcto es la minuta real
con los datos del caso sacados y puestos como tokens; nada más, nada menos.

## Flujo (síguelo en orden)

### 1. Extraer el texto
Los .docx modernos se leen con `python-docx`; los .doc viejos hay que convertirlos
antes (o pedir el .docx). Usa el script:

```bash
python scripts/extract_docx.py "ruta/al/minuta.docx" > /tmp/minuta.txt
```

Lee el texto completo. Es un documento legal largo; entiéndelo antes de tocarlo.

### 2. Clasificar (banco · acto · ciudad)
Del texto, identifica:
- **Banco acreedor** (busca "Hipoteca a favor de", "BANCO …", el NIT). Si no hay
  hipoteca/banco, el molde es genérico (fuente `particular`).
- **Acto**: compraventa sola, compraventa + hipoteca (acto `hipoteca`), o
  cancelación de hipoteca (acto `cancelacion`).
- **Ciudad / Notaría** (del encabezado: "NOTARÍA … DE MEDELLÍN"). Importa: la
  misma cadena de banco puede tener minutas distintas por ciudad.

Esto define el `<slug>`, el `name` y el `bank_nit` del `.map.json`.

### 3. Templatizar (el corazón)
Recorre el texto y aplica **solo dos operaciones**:

- **Dato variable → token.** Cuando un fragmento es un dato de ESTE caso que existe
  en el vocabulario (`references/tokens.md`), reemplázalo por su `{{token}}`.
  Ejemplo: el nombre del comprador "VICTOR HUGO QUIROZ PORTILLA" → `{{C.0.nombre}}`;
  la matrícula "01N-5081553" → `{{matricula}}`.
- **Sección condicional → `[[if …]]`.** Los bloques que solo aparecen en algunos
  casos (toda la hipoteca, propiedad horizontal, afectación a vivienda familiar,
  VIS, subsidio, ratificación del cónyuge) se envuelven en su marca. Lee
  `references/conditionales.md` — tiene las marcas exactas y **trampas** (p. ej.
  `afect` va como `[[if afect in si]]`, no `[[if afect]]`).

Todo lo demás se conserva **verbatim**. Limpia solo ruido de OCR obvio (líneas de
guiones `-----`, tabs raros), nunca el contenido legal.

**Datos sin token.** Si un dato variable NO tiene token en el vocabulario (p. ej. el
cónyuge del comprador, la cuenta de desembolso, la cédula del apoderado), NO
inventes un token. Déjalo como un hueco visible y anótalo en
`no_capturado_por_tokens` del `.map.json`. Formato del hueco:
`·····<span class="nota-hueco" title="qué es y por qué no hay token">[descripción]</span>·····`

La estructura HTML (clases, encabezado, formato SNR) y el formato exacto del
`.map.json` están en `references/estructura.md`, con un ejemplo. **Imita un molde
existente** como patrón: son el estándar de oro.

### 4. Validar (obligatorio antes de entregar)
Nunca entregues sin correr el validador. Atrapa los errores típicos (marcadores
sin cerrar, tokens mal escritos, condicionales que dejan basura):

```bash
python scripts/validate_molde.py <slug>.html <slug>.map.json
```

Debe pasar: (a) `[[if]]` y `[[/if]]` balanceados, (b) `{{` y `}}` balanceados,
(c) el `.map.json` parsea, (d) prueba de relleno: al rellenar con datos de prueba
no quedan `{{`, `[[if` ni `[[/if]]` sueltos, y las secciones condicionales
aparecen/desaparecen según el valor. Si algo falla, corrígelo y vuelve a validar.

### 5. Entregar
Devuelve los dos archivos (o escríbelos donde te indiquen) y un resumen corto:
banco/acto/ciudad detectados, cuántos tokens usaste, qué condicionales incluiste,
y qué datos quedaron en `no_capturado_por_tokens`.

## Reglas que no se rompen

- **Verbatim el texto legal.** Una escritura mal copiada la devuelve el registro.
  Ante la duda entre "parafraseo más limpio" y "copio exacto", copia exacto.
- **Solo tokens del vocabulario.** No inventes nombres de token. Si falta, es un
  hueco `no_capturado`.
- **El banco va fijo en el texto** (este es el molde propio de ese banco). Solo el
  apoderado, el poder E.P. y la notaría del poder son tokens.
- **Valida siempre.** El validador es barato; un molde roto en producción no.

## Archivos de referencia

- `references/tokens.md` — vocabulario completo de tokens y a qué campo mapea cada uno.
- `references/conditionales.md` — marcas `[[if]]`, cómo las evalúa el motor, y trampas.
- `references/estructura.md` — estructura HTML, clases, formato del `.map.json` y ejemplo.
- `scripts/extract_docx.py` — extrae texto limpio de un .docx.
- `scripts/validate_molde.py` — valida el molde (balance, parseo, prueba de relleno).
