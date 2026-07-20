# Ecosistema Notarial — Sandbox de diseño (compraventa)

Trabajo de diseño y validación del motor de generación de escrituras (acto piloto: **compraventa de inmueble**).
Estos documentos son el **insumo durable** que alimenta el software real (backend FastAPI + Gari + OnlyOffice).

> **Origen:** prototipado en un sandbox HTML (iteración rápida, cero riesgo). Lo validado aquí se porta al software.

## 👉 Empezar aquí al retomar

**[`estado-y-proximos-pasos.md`](./estado-y-proximos-pasos.md)** — punto de retomar: qué está hecho, pendientes, próximas tareas y decisiones clave. Es lo primero que se lee cada sesión (la continuidad depende del repo, no de la memoria del asistente).

## Conocimiento (Markdown — porta al backend como datos)

| Archivo | Contenido |
|---|---|
| [`normograma-compraventa.md`](./normograma-compraventa.md) | Corpus normativo verificado de la compraventa: cada norma con estado de vigencia, artículos clave, qué exige y fuente. |
| [`mapa-situaciones.md`](./mapa-situaciones.md) | Índice de las ~320 situaciones posibles del acto (21 sub-dimensiones). El detalle completo por fila está en `prototipos/mapa-situaciones.html`. |
| [`decisiones-diseno.md`](./decisiones-diseno.md) | Decisiones de arquitectura y producto: por qué se abandona la marcación de campos, el modelo de slots, por-notaría, semillas de banco, sandbox, etc. |

## Prototipos (HTML — se abren en el navegador; demo del patrón)

Carpeta [`prototipos/`](./prototipos/):

| Archivo | Qué es |
|---|---|
| `normograma-compraventa.html` | 📚 La base legal verificada (18 normas). |
| `mapa-situaciones.html` | 🗺️ Las ~320 situaciones con norma, frecuencia y cobertura. |
| `arbol-compraventa.html` | 🌳 El árbol de preguntas anclado al normograma (especificación). |
| `demo-escritura.html` | ⚖️ Demo del flujo preguntas → escritura → cumplimiento. |
| `wizard-compraventa.html` | ▶️ Wizard interactivo dinámico (N intervinientes, fidelidad real, resaltado, popups de norma, liquidación 2026). **Pieza principal validada.** |
| `minuta-banco-slots.html` | 🏦 Ejemplo aislado: importar minuta de banco con slots semánticos (no marcación). |

## Cómo esto se convierte en el software

1. **Datos** (`normograma`, `mapa`) → tablas en el backend: `norma`, `clausula`, `regla`.
2. **Lógica** (motor de cláusulas + cumplimiento) → servicios FastAPI enganchados a Gari.
3. **Experiencia** (wizard) → frontend Next.js (`minutas`/`casos`) + OnlyOffice para el control de cambios en rojo.

## Alcances y salvedades

- El **normograma** (reglas legales) es **nacional/compartido**. El **estilo, las cláusulas semilla y el orden de los actos** son **por notaría**. Las **semillas de hipoteca** son **por banco** (versionadas).
- Verificación realizada en julio de 2026 contra fuentes oficiales (Función Pública, SUIN-Juriscol, Senado, DIAN, SNR). Los puntos marcados **POR_VERIFICAR** requieren confirmación literal antes de producción. La **validación jurídica final** corresponde al notario.
