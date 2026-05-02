# Diagnóstico de seguimiento y revisión de minutas en EasyPro 2

## 1. Qué existe hoy para seguimiento/revisión

EasyPro 2 ya tiene un flujo documental operativo para revisión de minutas, pero la experiencia está repartida entre la lista/bandeja, el detalle de la minuta y los eventos de backend.

- La bandeja de minutas permite abrir el detalle de cada registro, filtrar por estado, tipo, responsable y notaría, y ver una acción sugerida.
- El detalle de la minuta tiene pestañas para ver el documento, el diligenciamiento y el historial.
- En el detalle existen acciones para generar Word, descargar Word, cargar el documento final firmado y registrar aprobación con comentario.
- El historial muestra eventos de workflow con actor, fecha, comentario y nuevo valor cuando aplica.
- El backend ya guarda estados, comentarios, eventos de timeline y workflow, y metadatos de aprobación.

La parte que todavía no está tan simple como EasyPro 1 es la lectura operativa: el revisor debe interpretar más estados y más acciones de las que la UI le presenta de forma directa.

## 2. Qué acciones de aprobación/rechazo existen en backend

### Aprobación

En `backend/app/modules/document_flow/router.py` existe el endpoint:

- `POST /api/v1/document-flow/cases/{case_id}/approve`

Comportamiento actual:

- Acepta `role_code` en `approver`, `titular_notary` o `substitute_notary`.
- Si el `role_code` es `approver`, mueve la minuta a `revision_notario`.
- Si el `role_code` es `titular_notary` o `substitute_notary`, registra aprobación final y mueve la minuta a `aprobado_notario`.
- Guarda `approved_at`, `approved_by_user_id`, `approved_by_role_code` y `approved_document_version_id`.
- Registra eventos en timeline y workflow con comentario opcional.

### Rechazo

No se encontró un endpoint explícito de rechazo en el router revisado.

- El esquema de estados sí contiene `rechazado_notario`.
- También existen estados de devolución como `devuelto_aprobador` y `ajustes_solicitados`.
- Pero en el flujo revisado no aparece una acción backend directa tipo `reject` o `reject_case`.

### Comentarios

Sí existen acciones de comentarios:

- `POST /api/v1/document-flow/cases/{case_id}/client-comments`
- `POST /api/v1/document-flow/cases/{case_id}/internal-notes`

Además, el endpoint de aprobación acepta `comment`.

## 3. Qué acciones están visibles en frontend

### Bandeja de minutas

En `frontend/components/cases/cases-workspace.tsx` la bandeja hoy permite:

- Ver el listado de minutas.
- Abrir el detalle de cada una.
- Crear una minuta desde plantilla.
- Filtrar por estado, tipo de minuta, responsable, notaría y búsqueda libre.
- Ver una acción sugerida según el estado.

### Detalle de minuta

En `frontend/components/cases/case-detail-workspace.tsx` el usuario ve:

- Pestaña `Documento`
  - Botón `Generar Word`
  - Botón `Descargar Word`
  - Lista de versiones del borrador
  - Carga del documento final firmado
  - Bloque de revisión y aprobación con comentario y botón `Aprobar`
- Pestaña `Diligenciamiento`
  - Campos diligenciados
  - Intervinientes
- Pestaña `Historial`
  - Eventos del workflow con actor, fecha, comentario y nuevo valor

### Lo que no está visible como acción directa

- No hay botón visible de `Rechazar`.
- No hay una bandeja separada de revisión/aprobación.
- No hay una vista simplificada de solo lectura para el revisor.
- No hay un flujo visual explícito de "abrir, revisar, comentar, aprobar o rechazar" tan directo como en EasyPro 1.

## 4. Qué falta para que sea simple como EasyPro 1

La lógica existe, pero la UI todavía mezcla demasiadas responsabilidades en una sola pantalla.

Faltan principalmente estas simplificaciones:

- Una bandeja de revisión más clara para quien aprueba o rechaza.
- Una vista de lectura rápida con foco en el Word y sus datos esenciales.
- Acciones de decisión más obvias: aprobar, rechazar, comentar.
- Separar mejor el rol del protocolista del rol del revisor.
- Mostrar el estado operativo en lenguaje notarial, no en lenguaje técnico de workflow.
- Evitar que el detalle muestre demasiados elementos de edición cuando el usuario solo debe revisar.

## 5. Flujo recomendado por rol

### Protocolista

1. Escoge la plantilla.
2. Crea la minuta.
3. Diligencia el formulario dinámico.
4. Guarda la información.
5. Genera Word.
6. Descarga Word.
7. Si aplica, carga el documento final firmado.

### Revisor / aprobador

1. Entra a la bandeja de minutas pendientes.
2. Abre la minuta.
3. La revisa en modo lectura.
4. Deja comentario.
5. Aprueba o rechaza.
6. Si rechaza, la minuta debe volver con estado y comentario claros.

### Notario

1. Revisa las minutas asignadas o pendientes.
2. Verifica el contenido final.
3. Aprueba o devuelve con comentario.
4. Consulta historial y trazabilidad si necesita contexto.

### Superadmin

1. Ve la bandeja general.
2. Revisa estados y trazabilidad.
3. Supervisa asignaciones y cuellos de botella.
4. Puede intervenir en aprobaciones según permisos actuales.

## 6. Propuesta de implementación en fases

### Fase 1: Claridad de UI

- Renombrar la experiencia a `Minutas`.
- Separar visualmente protocolo de revisión.
- Dar prioridad a estado, responsable, plantilla y acción sugerida.
- Reducir ruido visual en el detalle.

### Fase 2: Bandeja de revisión

- Crear una vista específica para pendientes de aprobación.
- Mostrar comentario y decisión de forma directa.
- Diferenciar claramente aprobar, rechazar y devolver.

### Fase 3: Decisiones y trazabilidad

- Exponer la acción de rechazo si el backend ya la soporta o dejarla documentada como pendiente de implementación.
- Unificar estados mostrados al usuario con lenguaje de notaría.
- Mejorar lectura del historial para auditoría rápida.

### Fase 4: Ajustes finos

- Refinar textos por rol.
- Reducir campos visibles según permisos.
- Mantener el detalle como espacio de consulta, no de edición permanente.

## 7. Lista de archivos revisados

- `frontend/components/cases/cases-workspace.tsx`
- `frontend/components/cases/case-detail-workspace.tsx`
- `frontend/lib/document-flow.ts`
- `backend/app/modules/document_flow/router.py`
- `backend/app/schemas/case.py`

## 8. Cosas que NO deben tocarse

- Motor documental.
- Generación Word.
- Descarga Word.
- Reemplazo de etiquetas.
- Tab stops y leaders para guiones notariales.
- Contratos API existentes.
- Endpoints ya funcionales de generación, aprobación y descarga.
- Migraciones.
- Persistencia documental ya operativa.

## Conclusión

EasyPro 2 ya tiene la base funcional para seguimiento y revisión de minutas, pero la experiencia sigue siendo más técnica de lo que necesita una operación notarial. La mejora principal no es de motor, sino de presentación: una bandeja más clara, una pantalla de revisión más simple y una decisión visible por rol.
