# Decisiones de diseño — Ecosistema Notarial

Registro de las decisiones de producto y arquitectura tomadas durante el sandbox. Es la memoria del "por qué".

## 1. Del formulario pasivo al motor agéntico

- **Rechazado:** el flujo de EasyPro 1 (plantilla con campos que alguien rellena) y la **marcación de campos fijos/variables**. Es esfuerzo O(n) recurrente, convierte al protocolista en operario de casillas y no escala.
- **Adoptado:** **preguntas → construcción de la escritura respetando el estilo y la normatividad.** El humano responde lo que *cambia* la escritura; el motor ensambla.

## 2. Por qué muere la "detección/marcación de campos variables"

Es el enfoque que ha sido **difícil e inexacto**. La razón de fondo: se le pide a la máquina la pregunta imposible *"¿cuál de estas 3.000 palabras es un campo variable?"*, que es ambigua:

- La misma palabra es dato en un lugar y texto fijo en otro (una fecha puede ser la de esta escritura o la de otra referida).
- Un número suelto no dice si es precio, saldo o cuantía (falta significado).
- Se rompe con cualquier cambio de redacción; sobre-detecta artículos, fechas y mayúsculas.
- Las plantillas traen errores de copy-paste → "aprender" de ellas produce basura.

**Giro correcto:** se deja de **detectar** variables y se pasa a **inyectar datos del caso en texto fijo**.

| Viejo (falló) | Correcto |
|---|---|
| Documento → detectar qué es variable | Datos del caso → inyectar en texto fijo |
| La IA adivina los campos | Se **definen** pocos slots con nombre, una vez |
| Datos salen de parsear el documento | Datos salen de las **preguntas del caso** (validados) |

**Regla:** el documento aporta las **palabras** (estilo/clausulado); el caso aporta los **datos**. Nunca al revés.

## 3. Construcción anclada (grounded), no generación libre

En notarial la generación libre es peligrosa (inventar un lindero/matrícula = falla de fe pública). El motor:

- **Datos** solo de las respuestas o documentos aportados (nunca inventados).
- **Cláusulas** solo de la biblioteca aprobada de la notaría.
- **Normas** como reglas de qué cláusula/advertencia es obligatoria + verificación final.
- La IA es creativa en **seleccionar, ordenar, adaptar y resolver** (concordancias de género/número), **no** en inventar texto jurídico.

## 4. Alcance por capa (qué es compartido y qué es propio)

| Qué | Alcance |
|---|---|
| Normograma (reglas legales) | **Nacional / compartido** |
| Cláusulas, semillas, estilo | **Por notaría** |
| Semillas de hipoteca | **Por banco** (versionadas) |
| Orden de los actos en la minuta | **Por notaría** |
| Guiones (`----`) y bloque de firmas/autorización | Generados por el motor |
| Texto que el motor no genera | Editor OnlyOffice + bucle de aprendizaje |

## 5. Minuta semilla del banco → slots semánticos

Cuando el banco manda su minuta (a veces compraventa + hipoteca):

- Su clausulado es **texto fijo** (va verbatim) con **pocos slots con nombre** (`{{banco}}`, `{{nit}}`, `{{hipotecante}}`, `{{cedula}}`, `{{matricula}}`, `{{monto}}`).
- **Onboarding = definir esos ~6 slots una vez** por banco → sirve para todos los casos con ese banco.
- Si el banco manda la minuta llena con datos de otro cliente, se **ignoran esos datos** y solo se toma el clausulado.
- Prototipo: `prototipos/minuta-banco-slots.html`.

## 6. El humano siempre en el centro (fe pública)

- El informe de cumplimiento **asiste**, no reemplaza. Estados: **cumple / obligatoria / advertencia / bloqueante**, cada uno con su norma y severidad.
- Bloqueantes de la compraventa: afectación a vivienda familiar sin doble firma (art. 3 Ley 258/96), patrimonio de familia sin cancelar, inmueble no identificado (art. 16 Ley 1579/12), embargo (objeto ilícito), leasing vigente.
- Límite honesto: verificar gravámenes exige el **certificado de tradición**; sin fuentes oficiales el informe solo valida consistencia interna y presencia de anexos.

## 7. Método de trabajo (sandbox)

- **El HTML es el sandbox**: iteración rápida, cero riesgo. Lo validado se **congela**.
- **Las ideas nuevas van en archivos/enlaces aparte**; experimentar nunca rompe lo bueno.
- **Nada se mezcla al software real sin OK** explícito.
- Orden de construcción por acto: **normograma (verificado) → árbol de preguntas → wizard → validación con notario → port al backend**.

## 8. Verificación en dos rondas — hallazgos que evitaron errores

- **VIS: 5 años, no 10** (Ley 2079/2021; solo subsidio 100% en especie).
- **Ganancia ocasional: 15%**, no 10% (Ley 2277/2022); exención casa de habitación bajó a 5.000 UVT.
- **Escritura pública electrónica: inexequible** (C-159/2021, efectos desde 20-jun-2023) — nunca insertar cláusula basada en artículo tumbado.
- **Decreto 2148/1983** derogado como norma autónoma pero **compilado** en Decreto 1069/2015.
- **Uso y habitación intransferibles**; territorios étnicos inalienables; reserva de dominio sobre inmuebles de eficacia discutida.
