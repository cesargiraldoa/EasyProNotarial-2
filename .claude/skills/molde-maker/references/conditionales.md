# Condicionales `[[if …]]`

Las secciones que aparecen solo en algunos casos se envuelven en marcas de
condicional. El motor las resuelve al rellenar: si la condición es verdadera deja
el contenido; si es falsa, lo borra.

## Cómo escribirlas
Dos formas equivalentes; usa la de **comentario HTML** porque deja la plantilla
legible antes de rellenar (el texto se ve, y las marcas quedan invisibles):

```html
<!-- [[if credito]] --> …contenido de la hipoteca… <!-- [[/if]] -->
```

Regla de oro: **cada `[[if X]]` tiene su `[[/if]]`**. El validador los cuenta.

## Marcas disponibles
| marca | envuelve |
|---|---|
| `[[if credito]] … [[/if]]` | Toda la sección de hipoteca, aceptación del apoderado del banco, filas del banco en las tablas SNR, y las notas propias de la hipoteca. |
| `[[if ph]] … [[/if]]` | Bloques de propiedad horizontal (parágrafos del reglamento, literal del comprador que acata el RPH, nota de expensas). |
| `[[if afect in si]] … [[/if]]` | Afectación a vivienda familiar (código 304): mención en la carátula, fila 304 en la tabla de naturaleza jurídica, y el "SÍ queda afectado". **Ver trampa abajo.** |
| `[[if vis]] … [[/if]]` | Lenguaje de Vivienda de Interés Social (descuentos, Decreto 145/2000). |
| `[[if subsidio]] … [[/if]]` | Mención del subsidio de vivienda (usa `{{subsidioEnt}}` dentro). |
| `[[if C.0.estado in casado_sc\|union]] … [[/if]]` | Comparecencia y ratificación del cónyuge/compañero(a) permanente del comprador para la Ley 258 (cuando el comprador es casado o en unión). |

## Cómo evalúa el motor cada condición (para no equivocarte)
El motor evalúa así:
- `X in a|b` → verdadero si el valor del campo `X` es exactamente `a` o `b`.
- `vis` (caso especial) → verdadero cuando no es `"no"` ni vacío.
- Cualquier otra condición `X` a secas → **verdadero si el valor es "truthy"**
  (booleano `true`, o string NO vacío).

## ⚠️ Trampas (errores reales que ya ocurrieron)

**1. `afect` NO se usa a secas.**
`afect` vale `"no"`, `"si"` o `"nosabe"`. Si escribes `[[if afect]]`, el motor
evalúa `Boolean("no")` = **verdadero** → la afectación saldría **aunque sea "no"**.
Por eso la afectación a vivienda familiar (código 304, el "SÍ queda afectado") va
siempre como **`[[if afect in si]]`**. Solo debe aparecer cuando el inmueble SÍ
queda afectado.

**2. `credito`, `ph`, `subsidio` sí son booleanos** → a secas está bien
(`[[if credito]]`, `[[if ph]]`, `[[if subsidio]]`).

**3. Enums a secas = siempre verdaderos.** Cualquier campo que sea un enum de
strings (como `afect`, `gravamen`, `derecho`) evaluado a secas será truthy. Si
necesitas condicionar por su valor, usa la forma `in`: `[[if campo in valor]]`.

**4. No condiciones por un token, condiciona por su campo.** La marca usa el
**nombre del campo** (`afect`, `credito`, `C.0.estado`), no llaves dobles. Nunca
`[[if {{afect}}]]`.
