# Resumen de sesión EasyPro 2 — 02/05/2026

Rama de trabajo: `feature/auditoria-easypro1`  
Base protegida: `main`  
Estado de la sesión: trabajo funcional en rama de prueba, sin merge a producción todavía.

## Decisión general de producto

EasyPro 2 debe quedar listo para que Will pruebe el flujo con usuarios reales de notaría, no con superadmin. El superadmin se mantiene como usuario de configuración, auditoría y soporte, pero no como actor natural del trámite notarial.

La lógica de producto acordada es:

- **Superadmin:** configura, audita, administra usuarios, roles, notarías, plantillas y puede ver historial técnico.
- **Protocolista:** elabora la minuta, diligencia el formulario, genera Word, corrige según observaciones y vuelve a generar.
- **Aprobador / revisor:** revisa la minuta, descarga o visualiza el documento, solicita ajustes con comentarios y aprueba si corresponde.
- **Notario:** revisa y aprueba u observa según el rol asignado.

No se implementa revisión con IA en esta versión. La revisión debe ser manual, inspirada en EasyPro 1.

## Referencia de EasyPro 1

EasyPro 1 operaba con plantillas Word etiquetadas. La plantilla definía los campos del formulario y algunos campos eran listas asociadas a `TableMaster`.

En EasyPro 1 existía el flujo:

```text
Seguimiento → Verificar Documento → Aprobar / Rechazar → Comentarios → Generar PDF/DOCX
```

La aprobación/rechazo no era un flujo del superadmin; dependía de permisos de seguimiento/revisión.

## Avances implementados en EasyPro 2

### 1. Flujo de creación de minuta simplificado

Se reorganizó el wizard de creación para eliminar pasos redundantes. El flujo deseado quedó:

```text
Plantilla → Datos de la minuta → Diligenciar → Guardar y generar Word → Detalle de la minuta
```

Se eliminó la pantalla intermedia confusa de “Revisar y generar Word” como paso separado.

### 2. Lenguaje notarial

Se reemplazó el lenguaje visible de “casos/documentos” por “minutas” en la operación del usuario. Las rutas internas como `/dashboard/casos` permanecen sin cambios para no romper arquitectura.

### 3. Selección de plantilla mejorada

Se mejoró la vista de selección de plantilla:

- La plantilla seleccionada queda destacada visualmente.
- Se añadió buscador por nombre, tipo de minuta o descripción.
- Se añadió filtro por tipo de minuta.
- Se muestra contador de resultados.
- El resumen de plantilla seleccionada persiste aunque los filtros oculten la tarjeta.

### 4. Selects reales desde EasyPro 1

Se extrajo la tabla `web_tablemaster` de EasyPro 1 desde `easypro1_tablemaster_raw.sql`.

Se creó un catálogo frontend generado desde datos reales de EasyPro 1:

- `frontend/lib/easypro1-notarial-catalogs.ts`
- `scripts/convert_easypro1_tablemaster_to_catalogs.py`

Catálogos reales importados, entre otros:

- `TIPO DE DOCUMENTO`
- `ESTADO CIVIL`
- `NACIONALIDAD`
- `GENERO`
- `DE TRANSITO`
- `SI O NO`
- `MES`
- `DÍAS`
- `CUOTA INICIAL`
- `PATRIMONIO DE FAMILIA`
- `PROTOCOLISTA`
- `MUNICIPIO`
- `PAIS`
- `PADRES`
- `NOTARIO`

La lógica del formulario dinámico ahora intenta resolver opciones así:

```text
1. options_json del campo, si existe.
2. table_master o catálogo inferido desde EasyPro 1.
3. input normal si no hay catálogo.
```

No se inventaron valores: los selects vienen de EasyPro 1.

### 5. Valores monetarios en letras calculados automáticamente

Se agregó cálculo automático de campos monetarios en letras, por ejemplo:

- `VALOR_DE_LA_VENTA_EN_NUMEROS` → `VALOR_APARTAMENTO_EN_LETRAS` / `EN_LETRAS_VALOR_DE_LA_VENTA`
- `VALOR_DEL_ACTO_DE_LA_HIPOTECA` → `VALOR_DEL_ACTO_DE_LA_HIPOTECA_EN_LETRAS`
- `NUMEROS_VALOR_HIPOTECA` → `LETRAS_VALOR_HIPOTECA`
- `EN_NUMEROS_CUOTA_INICIAL` → `EN_LETRAS_CUOTA_INICIAL`

Estos campos quedan como solo lectura y se guardan como string dentro de `data_json`, para que el motor Word los reemplace normalmente.

### 6. Detalle de minuta y roles

Se ajustó la vista de detalle para separar el flujo operativo de la auditoría técnica.

Superadmin ve:

```text
Minuta | Diligenciamiento | Observaciones | Historial técnico
```

Usuarios de notaría ven:

```text
Minuta | Diligenciamiento | Observaciones
```

La pestaña de historial técnico con JSON, `old_value`, `new_value` y `metadata_json` queda solo para superadmin.

### 7. Observaciones

Se creó una pestaña propia de observaciones internas. La intención funcional es que sirva como mecanismo manual de ajustes:

```text
Revisor observa → protocolista corrige → regenera Word → revisor vuelve a revisar → aprueba
```

La vista aún necesita evolucionar porque actualmente se siente más como una caja de comentarios que como un flujo de revisión completo.

### 8. Selectores de notaría

Se detectó que las notarías sí estaban cargadas en backend. Por ejemplo:

```text
Caldas · Única
id: 21
slug: caldas-unica
```

El problema era que los selectores mostraban solo `Única`, `Primera`, `Segunda`, etc. Se ajustó la UI para mostrar:

```text
Municipio · Notaría
```

Ejemplos esperados:

- `Caldas · Única`
- `Bello · Primera`
- `Bello · Segunda`
- `Medellín · Tercera`

Esto es indispensable para asignar usuarios por notaría sin confusión.

### 9. Scripts locales

Se crearon scripts para facilitar pruebas locales:

- `scripts/START_LOCAL_EASYPRO.ps1`
- `scripts/CLEAN_FRONTEND_NEXT.ps1`

Se corrigió un bug en `START_LOCAL_EASYPRO.ps1`: no debe usar `$pid` como variable, porque PowerShell reserva `$PID`.

Regla operativa acordada para pruebas:

```text
Backend: 127.0.0.1:8001
Frontend: 127.0.0.1:5179
```

Para pruebas finales se debe preferir:

```text
npm run build
npm run start
```

y no `npm run dev`, porque Next ha generado errores recurrentes de chunks/caché.

## Problemas detectados durante la sesión

### 1. Errores recurrentes de Next / chunks

Se presentaron errores como:

```text
ChunkLoadError
Cannot find module './611.js'
Failed to load resource: 400 Bad Request
Application error: client-side exception
```

La causa principal parece ser caché de `.next` y navegador después de cambios grandes en frontend.

Protocolo de mitigación:

```powershell
cd C:\EasyProNotarial-2\easypro2\frontend
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
Remove-Item -Recurse -Force .next -ErrorAction SilentlyContinue
npm run build
npm run start
```

Probar en ventana incógnita.

### 2. Bug del formulario de usuarios: contraseña

Se pidió mejorar el campo de contraseña para poder:

- Ver / ocultar.
- Generar contraseña temporal.
- Copiar contraseña.

Aunque Codex reportó haberlo implementado varias veces, el archivo real seguía mostrando el input simple:

```tsx
<input
  type="password"
  value={editorState.password}
  onChange={(event) => updateField("password", event.target.value)}
  placeholder="Dejar vacío para conservar"
  className="ep-input h-12 w-full rounded-2xl px-4"
/>
```

Al final se vio en UI una versión con botones:

```text
Ver / Ocultar
Generar contraseña
Copiar
```

pero debe confirmarse con `git status`, búsqueda local y commit/push. Verificación recomendada:

```powershell
Select-String -Path frontend\components\users\users-admin-workspace.tsx -Pattern "showPassword|Generar contraseña|Copiar|type=\{showPassword|type=\`"password\`""
```

Debe existir `showPassword`, `Generar contraseña`, `Copiar` y `type={showPassword ? "text" : "password"}`.

### 3. Bug al seleccionar usuarios

Se observó un bug en el formulario de usuarios: al seleccionar un usuario, los datos de edición pueden mostrar datos del superadmin. Esto debe revisarse con prioridad.

Hipótesis iniciales:

- Estado `editorState` no se está reseteando correctamente por usuario.
- `openUserId` / `resetEditor` no está sincronizando bien después de `loadWorkspace()`.
- Después de guardar, se busca el usuario en un arreglo `users` anterior al refresh.
- La UI puede conservar estado del último usuario abierto.

Pendiente para mañana:

```text
Corregir bug: al editar un usuario, el formulario debe cargar exactamente los datos del usuario seleccionado, no los del superadmin ni del último usuario abierto.
```

### 4. Falta flujo real de revisión

La vista de observaciones todavía se siente insuficiente. Debe evolucionar hacia un flujo claro:

```text
Protocolista elabora → envía a revisión → revisor acepta o rechaza/solicita ajustes → protocolista corrige → revisor aprueba
```

Actualmente hay observaciones, pero no se ve un proceso completo de “enviar a revisión”, “aprobar” y “solicitar ajustes” con estado claro.

### 5. Falta visualizador del documento

Se identificó que descargar Word no es suficiente para el revisor. Debe existir una forma de revisar el documento generado sin depender únicamente de la descarga.

Opciones:

1. Vista rápida de texto extraído del Word.
2. Previsualización PDF si se puede generar.
3. Visor embebido de documento si la infraestructura lo permite.

Para Will, esto es importante: el revisor debe poder observar el documento generado y decidir aprobar o solicitar ajustes.

### 6. Falta tablero/balance operativo por rol y estado

Debe existir balance operativo tipo:

```text
Total minutas
En elaboración
En revisión
Aprobadas
Rechazadas / ajustes solicitados
```

Y por:

- protocolista
- aprobador
- notaría
- estado
- tipo de minuta

Esto debe ayudar a Will y a la notaría a ver carga de trabajo y avance.

## Flujo objetivo pendiente

### Protocolista

```text
Crear minuta
Seleccionar plantilla
Diligenciar formulario dinámico
Generar Word
Enviar a revisión
Ver observaciones
Corregir
Regenerar Word
```

### Revisor / aprobador

```text
Ver bandeja de minutas en revisión
Abrir minuta
Visualizar/descargar Word
Solicitar ajustes con comentario obligatorio
Aprobar minuta
```

### Notario

```text
Ver minutas asignadas
Revisar documento
Aprobar u observar
```

### Superadmin

```text
Auditar
Configurar
Ver historial técnico
No ser el flujo operativo natural
```

## Pendientes priorizados para mañana

### Prioridad 1 — Usuarios y roles

- Confirmar que el campo contraseña quedó realmente aplicado, visible y commiteado.
- Corregir bug: editar un usuario debe cargar los datos del usuario seleccionado, no superadmin.
- Crear/confirmar usuarios de prueba:
  - `test.protocolista@notariacaldas.co`
  - `test.aprobador@notariacaldas.co`
  - `test.notario@notariacaldas.co`
  - `test.admin@notariacaldas.co`
- Todos asociados a `Caldas · Única`.

### Prioridad 2 — Flujo real de revisión

Implementar o confirmar estados y acciones:

```text
Borrador / En elaboración
En revisión
Ajustes solicitados
Aprobada
Rechazada si aplica
Firmada / cerrada
```

Acciones por rol:

- Protocolista: `Enviar a revisión`.
- Revisor: `Solicitar ajustes` y `Aprobar`.
- Notario: `Aprobar` u observar.

### Prioridad 3 — Visualizador de documento

Agregar una forma de revisar el documento generado:

- Preview de texto extraído.
- O generación/visualización PDF.
- Mantener descarga Word.

### Prioridad 4 — Balance operativo

Agregar métricas por rol/estado:

```text
Total minutas
En elaboración
En revisión
Aprobadas
Ajustes solicitados / rechazadas
```

### Prioridad 5 — Prueba completa con Will

Will debe probar con usuarios de notaría, no superadmin.

Checklist:

```text
Login protocolista
Crear minuta
Generar Word
Enviar a revisión

Login aprobador
Abrir minuta
Ver documento
Solicitar ajustes

Login protocolista
Ver observación
Corregir
Regenerar
Enviar a revisión

Login aprobador/notario
Aprobar

Login superadmin
Auditar historial técnico
```

## No tocar salvo necesidad crítica

- Motor documental.
- Generación Word.
- Reemplazo de etiquetas.
- Tab stop / leader para guiones notariales.
- Lectura dinámica de plantillas.
- Catálogos reales migrados desde EasyPro 1.
- Cálculo de valores en letras, salvo bug puntual.

## Estado final de la sesión

La rama de trabajo mantiene los cambios principales en `feature/auditoria-easypro1`. `main` sigue protegida.

Antes de avanzar a producción, Will debe validar con roles reales de notaría y se deben corregir los bugs pendientes de usuarios/flujo de revisión.
