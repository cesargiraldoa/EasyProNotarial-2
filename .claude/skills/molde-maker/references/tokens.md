# Vocabulario de tokens

Estos son los únicos tokens válidos. Cada uno mapea 1:1 a un campo de
`CompraventaState` que el formulario rellena. Si un dato variable no está aquí, NO
inventes un token: es un hueco `no_capturado_por_tokens` (ver SKILL.md).

Sintaxis en el HTML: `{{token}}`. Ejemplo: `{{matricula}}`, `{{C.0.nombre}}`.

## Encabezado / otorgamiento
| token | qué es |
|---|---|
| `numEscritura` | Número de escritura |
| `fechaOtorg` | Fecha de otorgamiento (el motor la formatea a texto) |

## Inmueble
| token | qué es |
|---|---|
| `matricula` | Folio de matrícula inmobiliaria |
| `catastral` | Código catastral |
| `nupre` | NUPRE |
| `inmdesc` | Descripción/ubicación del inmueble |
| `linderos` | Linderos del inmueble |
| `phReg` | Escritura del reglamento de propiedad horizontal |
| `avaluoCatastral` | Avalúo catastral (monto) |

## Acto
| token | qué es | valores |
|---|---|---|
| `derecho` | Derecho que se transfiere | dominio/nuda/usufructo/cuota/uso |
| `tipoNegocio` | Tipo de negocio | compraventa/permuta/dación/… |
| `gravamen` | Estado de gravámenes | libre/… |
| `afect` | Afectación a vivienda familiar | `no`/`si`/`nosabe` (ver condicionales) |
| `vis` | Vivienda de Interés Social | `no`/`sfve`/`otra` |
| `subsidio` | ¿Aplica subsidio? | booleano |
| `subsidioEnt` | Entidad que otorga el subsidio | texto |

## Montos
| token | qué es |
|---|---|
| `total` | Precio total de la compraventa |
| `inicial` | Cuota inicial / recursos propios |
| `saldo` | Saldo financiado (monto del crédito e hipoteca) |

## Título de adquisición del vendedor (tradición)
| token | qué es |
|---|---|
| `tituloTipo` | Tipo de título de adquisición |
| `tituloNum` | Número de escritura del título |
| `tituloFecha` | Fecha del título |
| `tituloNotaria` | Notaría del título |

## Hipoteca / banco
| token | qué es |
|---|---|
| `plazoAnios` | Plazo del crédito en años |
| `numCuotas` | Número de cuotas mensuales |
| `apoderadoBanco` | Nombre del apoderado especial del banco |
| `poderBancoEP` | Escritura pública del poder del banco |
| `poderBancoNot` | Notaría del poder del banco |

> El **nombre y NIT del banco van fijos en el texto** (el molde es propio de ese
> banco). Solo el apoderado, el poder E.P. y su notaría son tokens.

## Partes (vendedor V, comprador C)
El índice empieza en 0. Para varias partes se repite con `.1`, `.2`, etc.
(`{{V.1.nombre}}`, `{{C.1.id}}`…). Un molde base cubre 1 vendedor y 1 comprador;
si la minuta real tiene más, agrega los índices que haga falta.

| token | qué es |
|---|---|
| `V.0.nombre` | Nombre vendedor 1 |
| `V.0.id` | Cédula vendedor 1 |
| `V.0.ciudad` | Ciudad/domicilio vendedor 1 |
| `V.0.estado` | Estado civil vendedor 1 |
| `C.0.nombre` | Nombre comprador 1 |
| `C.0.id` | Cédula comprador 1 |
| `C.0.ciudad` | Ciudad/domicilio comprador 1 |
| `C.0.estado` | Estado civil comprador 1 |

Valores de estado civil: `soltero`, `casado_sc` (casado con sociedad conyugal),
`union` (unión marital), `divorciado`, `viudo`.

## Datos que típicamente NO tienen token (van a `no_capturado_por_tokens`)
No hay campo para estos; déjalos como hueco visible y anótalos:
- Nombre y cargo del notario / encargado que autoriza (lo maneja otro selector).
- Ciudad de expedición de la cédula de cada parte.
- Nombre del tradente/propietario anterior en la cláusula de tradición.
- Cónyuge o compañero(a) permanente del comprador (no hay campo de cónyuge).
- Cédula del apoderado del banco (solo se guarda el nombre).
- Cuenta de desembolso / AFC y su titular.
- Números, fechas y vigencias de los paz y salvo (predial, valorización, admin).
