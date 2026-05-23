# SESSION.md — EasyProNotarial-2

---
## Sesión 2026-05-23 (tarde)

**Objetivo de la sesión:** Completar el motor de minutas — fixes de género/guiones, secciones editables de inmueble/notaría/valores en el frontend, y cobertura completa de reemplazos en el backend.

**Realizado:**
- **reemplazador.py — _normalizar_guiones (9fdb543, 1b57295, f878b7b, c7c9eec):** Múltiples iteraciones: primero consolidar texto en runs[0] vaciar el resto; luego refactors con guard `not run.text`, colapso de `--` solo cuando rodeado de espacios, y finalmente reemplazar dentro de cada run para preservar formato
- **router.py — todos_nombres_doc (9fdb543, fc5e004, e2883dc):** Enriquecer con scanner de secuencias MAYÚSCULAS del documento; luego cambiar a escanear todo el doc sin filtro de línea conocida; finalmente procesar personas F antes que M y filtrar falsos positivos
- **router.py — aplicar genero contextual (433b345):** Aplicar reemplazos de género a TODAS las personas nuevas con género definido, no solo las que cambian M↔F
- **concordancia.py — refactor y fixes (a2099bb, e6ab5c8, ff9f84c, 715d304, afab702):** Concordancia vía Claude solo maneja artículos de rol; recibe `personas_resto` para preservar género de otras personas; max_tokens 8000 → 32000 → 16384 (límite real del modelo); strip markdown; try/except con diagnóstico
- **reemplazador.py — construir_lista_reemplazos (12bba1d, 2eddc5b):** Agrega secciones `notaria` (nombre_notaria, municipio_notaria, numero_escritura), `fechas` (fecha_otorgamiento) e `inmueble` completo (municipio, departamento); guard contra valores non-string
- **nueva-minuta-workspace.tsx — secciones editables:** Tres nuevas cards en Paso 1: `InmuebleCard`, `NotariaCard`, `ValoresCard`; estado `inmuebleEdit`/`notariaEdit`/`valoresEdit`; `handleGenerar` pasa los tres al backend; fix `n.trim is not a function` con `?? ""`; null-checks en inicialización desde `analisisResult.datos`
- **nueva-minuta-workspace.tsx — numeroALetras:** Función de conversión número a letras (pesos moneda corriente) integrada en el workspace
- **navigation.ts:** "Crear Minuta" redirige a `/dashboard/minutas/nueva` en lugar de `/dashboard/casos/crear`

**Archivos creados/modificados:**
- `backend/app/modules/minuta/router.py` — scanner nombres, genero contextual todas las personas, todos_nombres_doc
- `backend/app/services/minuta/reemplazador.py` — _normalizar_guiones (múltiples fixes), construir_lista_reemplazos completo, guard non-string
- `backend/app/services/minuta/concordancia.py` — max_tokens 16384, strip markdown, try/except, refactor a solo artículos, personas_resto
- `frontend/components/minutas/nueva-minuta-workspace.tsx` — 3 secciones editables, numeroALetras, null-checks, fix trim
- `frontend/lib/navigation.ts` — "Crear Minuta" apunta a /minutas/nueva

**Pendientes para la próxima sesión:**
1. **[CRÍTICO] Verificar bug SEBASTIÁN en producción** — Múltiples fixes aplicados (scanner, orden F→M, genero contextual ampliado). Generar minuta real con SEBASTIÁN y DANIELA, revisar logs Railway para confirmar que SEBASTIÁN no recibe reemplazos incorrectos
2. **[CRÍTICO] Verificar concordancia con Claude** — Concordancia ahora usa Claude en lugar de GPT-4o-mini para artículos; confirmar que el modelo está configurado correctamente en Railway (ANTHROPIC_API_KEY) y que los reemplazos de artículos funcionan
3. **[MEDIA] Guiones dobles `-- -` sin resolver del todo** — _normalizar_guiones tuvo múltiples iteraciones; confirmar con documento real que los guiones dobles quedan bien
4. **[MEDIA] Concordancia de artículos EL→LA, DEL→DE LA** — Verificar que el refactor a Claude (solo artículos de rol) produce resultados correctos
5. **[BAJA] Alembic out-of-sync** — `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';` en Supabase producción (pendiente desde sesiones anteriores)
6. **[BAJA] debug prints en router.py y reemplazador.py** — Hay prints de debug (`GENERO DEBUG`) que deben removerse antes de demo

**Estado al cierre:**
- Backend: Railway operativo — commit `afab702` activo
- Frontend: Vercel operativo — easypronotarial.com, último deploy con null-checks
- BD producción: operativa, alembic_version desincronizada (pendiente)
- Git: `nueva-minuta-workspace.tsx` y `navigation.ts` modificados localmente — se commitean en este cierre

---
## Sesión 2026-05-23

**Objetivo de la sesión:** Corregir bugs de género (SEBASTIÁN y concordancia global) y agregar lógica de auto-cascada de nacionalidad/estado civil en el formulario frontend.

**Realizado:**
- **router.py — reemplazos de género deterministas (ee93a7e):** Agregar `_GENERO_M_A_F` y `_GENERO_F_A_M` con `varón/mujer`, `soltero/a`, `colombiano/a`, `domiciliado/a`, `identificado/a` — todos con `palabra_completa: True`
- **reemplazador.py — aplicar_reemplazos_por_contexto (d266d6f):** Nueva función que aplica reemplazos de género solo en párrafos que contienen el nombre de la persona específica
- **reemplazador.py — aplicar_genero_contextual_docx (d266d6f):** Nueva función que orquesta los pares persona→reemplazos con exclusión mutua entre personas del documento
- **router.py — integrar género contextual (d266d6f):** Paso 5 del endpoint `/generar` llama `aplicar_genero_contextual_docx` pasando `pares_genero` y `todos_nombres_doc`
- **reemplazador.py + router.py — colombiano/a (a101c26):** Agregar entradas `colombiano→colombiana` y `colombiana→colombiano` a los bloques M→F y F→M
- **router.py — fix exclusión SEBASTIÁN (610a817):** `todos_nombres_doc` ahora combina `datos_ant.personas + datos_nv.personas` con set para deduplicar — así personas que no cambiaron (como SEBASTIÁN) están en `nombres_excluir`
- **reemplazador.py — _normalizar_guiones:** Nueva función que colapsa guiones dobles (`--` → `-`, `- --` → `- -`) y espacios dobles; se llama en `aplicar_reemplazos_docx` antes de `doc.save`
- **nueva-minuta-workspace.tsx — handleChange con cascada de género:** `PersonaCard` ahora tiene `handleChange` que al cambiar género auto-actualiza `nacionalidad` (via diccionario `GENTILICIOS_M_A_F`/`GENTILICIOS_F_A_M` de 25 gentilicios) y `estado_civil` (soltero/casado/divorciado/viudo ↔ femeninos)

**Archivos creados/modificados:**
- `backend/app/modules/minuta/router.py` — género determinista, pares_genero, todos_nombres_doc combinado
- `backend/app/services/minuta/reemplazador.py` — `aplicar_reemplazos_por_contexto`, `aplicar_genero_contextual_docx`, `_normalizar_guiones`
- `frontend/components/minutas/nueva-minuta-workspace.tsx` — `GENTILICIOS_M_A_F`, `GENTILICIOS_F_A_M`, `handleChange` con cascada

**Pendientes para la próxima sesión:**
1. **[CRÍTICO] Debug SEBASTIÁN persiste:** El fix `610a817` está en producción pero el bug puede seguir. Agregar prints de debug en `aplicar_genero_contextual_docx` (imprimir `todos_nombres`, `otros`, y qué párrafos se procesan), hacer deploy, generar minuta real, revisar logs Railway
2. **[MEDIA] Guiones dobles `-- -` sin resolver:** `_normalizar_guiones` existe pero no resuelve porque los guiones están partidos entre múltiples runs. Corregir para que una el texto de todos los runs del párrafo antes de aplicar regex, o implementar solución EasyPro1 (tab stops + `[[--]]` → `\t` en plantillas)
3. **[MEDIA] Concordancia de artículos** — EL→LA, DEL→DE LA (pendiente de sesión anterior)
4. **[BAJA] Alembic out-of-sync** — `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';` en Supabase producción
5. **[BAJA] Grabar videos demo** — si SEBASTIÁN y guiones quedan resueltos, preparar caso demo para notarías

**Estado al cierre:**
- Backend: Railway operativo — commit `610a817` activo (3a59eb6 es force redeploy vacío)
- Frontend: Vercel operativo — easypronotarial.com, deploy esta noche
- BD producción: operativa, alembic_version desincronizada (pendiente)
- Git: `reemplazador.py` y `nueva-minuta-workspace.tsx` modificados localmente sin commitear — se commitean en este cierre

---
## Sesión 2026-05-22

**Objetivo de la sesión:** Conectar el motor de minutas con OnlyOffice (abrir el .docx generado directamente en el editor) e integrar concordancia de género al flujo de generación.

**Realizado:**
- Análisis completo del flujo existente de minutas (detector, reemplazador, concordancia, router, frontend) y del flujo de OnlyOffice en document_flow
- Backend router.py minuta: POST /generar ahora integra concordancia de género por persona (detecta cambio M↔F, aplica reemplazos con palabra_completa=True), sube el .docx resultante a Supabase Storage en `minutas/notary_{id}/{uuid}_minuta.docx`, genera JWT firmado con storage_path y retorna JSON con `onlyoffice_path`
- Backend router.py minuta: 3 nuevos endpoints para servir el archivo al Document Server — GET /onlyoffice-config, GET /onlyoffice/file, POST /onlyoffice/callback (guarda versión editada de vuelta en Supabase)
- concordancia.py: fix menor — `aplicar_cambios_concordancia_a_reemplazos` ahora incluye `"palabra_completa": True` para respetar límites de palabra
- frontend/lib/minuta.ts: `generateMinuta` retorna `{ onlyoffice_path, filename }` en lugar de Blob; nueva función `getMinutaOnlyOfficeConfig(token)`; `sanitizeDatos()` limpia `\r\n\t\0` de strings antes de JSON.stringify (fix JSON malformado)
- frontend/components/minutas/nueva-minuta-workspace.tsx: `PersonaField` extraído a nivel de módulo (fix bug foco perdido por componente anidado que se desmontaba en cada render); paso 3 navega con `router.push(onlyoffice_path)` en lugar de descargar blob
- frontend/app/(app)/dashboard/minutas/editor/[token]/page.tsx: nueva página editor OnlyOffice para minutas — recibe JWT en URL, carga config desde `/api/v1/minuta/onlyoffice-config`, inicializa `DocEditor`
- frontend/lib/navigation.ts: entrada "Motor de Minutas" agregada al sidebar después de "Crear Minuta"
- frontend/next.config.mjs: `generateBuildId` con timestamp para forzar cache bust en Vercel
- Diagnóstico de problema en Vercel deploy: Root Directory mal configurado — path duplicado `frontend/easypro2/frontend`. URL settings: https://vercel.com/cesar-giraldo-aristizabals-projects/easypro-notarial-2/settings

**Archivos creados/modificados:**
- `backend/app/modules/minuta/router.py` — generar con concordancia + Supabase + JWT + 3 endpoints OnlyOffice
- `backend/app/services/minuta/concordancia.py` — `palabra_completa: True` en reemplazos de concordancia
- `frontend/app/(app)/dashboard/minutas/editor/[token]/page.tsx` — nueva página editor OnlyOffice para minutas
- `frontend/lib/minuta.ts` — generateMinuta retorna JSON, sanitizeDatos, getMinutaOnlyOfficeConfig
- `frontend/components/minutas/nueva-minuta-workspace.tsx` — PersonaField a nivel módulo, paso 3 navega al editor
- `frontend/lib/navigation.ts` — entrada Motor de Minutas en sidebar
- `frontend/next.config.mjs` — generateBuildId para cache bust

**Pendientes para la próxima sesión:**
1. **[CRÍTICO] Concordancia de artículos** — El motor cambia sustantivos (COMPRADOR→COMPRADORA) pero NO cambia artículos ni pronombres (EL→LA, LOS→LAS). Ajustar PROMPT_CONCORDANCIA en `concordancia.py`.
2. **[CRÍTICO] Fórmulas compuestas** — Expresiones como "EL(LOS) DEUDORA(ES)" quedan mal al cambiar género. El prompt debe manejar estas fórmulas mixtas.
3. **[CRÍTICO] Alembic out-of-sync** — Ejecutar en Supabase: `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';`
4. **[MEDIA] Verificar menú lateral por rol** — "Motor de Minutas" está en navigation.ts, confirmar que aparece correctamente según permisos del usuario
5. **[MEDIA] Personas incompletas en análisis B2** — Algunos docs devuelven menos personas de las esperadas. Revisar chunking o prompt del detector
6. **[MEDIA] Caso B1 (plantilla en blanco)** — El detector clasifica B1 pero el formulario dinámico es el mismo que B2. Pendiente diferenciar UX y prompt
7. **[BAJA] Reset contraseña** — No implementado
8. **[BAJA] Historial de minutas** — Guardar minutas generadas por notaría (estructura BD + UI)

**Estado al cierre:**
- Backend: Railway operativo — https://easypronotarial-2-production.up.railway.app
- Frontend: Vercel operativo — https://easypronotarial.com (deploy vía CLI `vercel --cwd frontend --prod`)
- BD producción: operativa, alembic_version desincronizada (pendiente UPDATE manual)
- Git: árbol limpio (solo uvicorn_start.log sin trackear)

**Deploy frontend (procedimiento correcto):**
```bash
cd c:\EasyProNotarial-2\easypro2
$env:NODE_OPTIONS="--use-system-ca"
vercel --cwd frontend --prod
```

---
## Sesión 2026-05-21

**Objetivo de la sesión:** Integrar motor de análisis de minutas IA al backend y crear pantalla frontend de 3 pasos para subir, analizar y generar minutas.

**Realizado:**
- Documentación inicial: SESSION.md operativo, AGENTS.md, protocolo iniciar-sesion y cerrar-sesion en .claude/commands/
- Verificación Supabase producción: alembic_version en 20260420, act_catalog ✅ 11 registros, legal_entities ✅ 6 registros, columnas document_type/document_number ✅ aplicadas (fuera de alembic_version)
- Backend motor minutas: detector.py (GPT-4o-mini, modo B1/B2 automático), reemplazador.py (reemplazos preservando formato .docx), concordancia.py (concordancia de género con IA), utils_letras.py (números a letras notarial)
- Backend endpoints: POST /api/v1/minuta/analizar + POST /api/v1/minuta/generar registrados en api_router. Instalado num2words y python-multipart
- Fix SSL local: OPENAI_DISABLE_SSL_VERIFY=true en .env + _make_openai_client() en detector.py y concordancia.py
- Prueba real con jaggua_limpio.docx: B2 detectado, 4 personas, 2 valores, inmueble Caldas/Antioquia, 8 actos, $0.0052 USD, 30 segundos respuesta
- Frontend lib/minuta.ts: tipos TypeScript + analyzeMinuta() + generateMinuta() usando getToken()
- Frontend components/minutas/nueva-minuta-workspace.tsx: wizard 3 pasos (subir+analizar, revisar personas con campos pendientes en amarillo, generar+descargar)
- Frontend app/(app)/dashboard/minutas/nueva/page.tsx: ruta nueva en Next.js 15
- tailwind.config.ts: aliases semánticos para CSS vars faltantes (muted, soft, panel-soft, panel-highlight, line-strong, etc.)
- Alembic desincronizado corregido: columnas 20260512 y 20260513 están en Supabase pero alembic_version no las registra. Pendiente UPDATE alembic_version.
- Comandos de sesión: iniciar-sesion.md y cerrar-sesion.md en easypro2/.claude/commands/ (para el repo) y C:\EasyProNotarial-2\.claude\commands\ (para Claude Code)

**Archivos creados/modificados:**
- `backend/app/services/minuta/detector.py` — motor B1/B2 con GPT-4o-mini
- `backend/app/services/minuta/reemplazador.py` — reemplazos en .docx preservando formato
- `backend/app/services/minuta/concordancia.py` — concordancia de género con IA
- `backend/app/services/minuta/utils_letras.py` — números a letras formato notarial
- `backend/app/modules/minuta/router.py` — 2 endpoints FastAPI
- `backend/app/api/router.py` — registra minuta_router
- `backend/requirements.txt` — +num2words +python-multipart
- `backend/.env` — +OPENAI_DISABLE_SSL_VERIFY=true (solo desarrollo local, no commitear)
- `frontend/lib/minuta.ts` — tipos + funciones API multipart
- `frontend/components/minutas/nueva-minuta-workspace.tsx` — wizard 3 pasos completo
- `frontend/app/(app)/dashboard/minutas/nueva/page.tsx` — ruta nueva
- `frontend/tailwind.config.ts` — aliases semánticos CSS vars
- `SESSION.md` — reescrito como documento operativo
- `AGENTS.md` — inventario de agentes del sistema
- `.claude/commands/iniciar-sesion.md` — protocolo arranque de sesión
- `.claude/commands/cerrar-sesion.md` — protocolo cierre de sesión

**Pendientes para la próxima sesión:**
1. **Alembic out-of-sync en producción** — Ejecutar `UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';` en Supabase para sincronizar. Las migraciones YA están aplicadas pero alembic_version dice 20260420.
2. **Frontend minutas — integrar al menú lateral** — La ruta /dashboard/minutas/nueva existe pero no aparece en el sidebar de AppShell. Agregar entrada de navegación.
3. **Placeholders del dashboard** — /lotes, /ayuda, /configuracion muestran páginas vacías. Limpiar del menú o agregar contenido mínimo antes de demo.
4. **Personas incompletas en análisis** — jaggua_limpio.docx devolvió 4 personas cuando debería tener más (compradores, banco, etc.). Investigar si es problema de contexto de GPT-4o-mini (110k chars) o del prompt.
5. **Reset de contraseña** — No existe. Usuarios no pueden cambiar su contraseña.

**Estado al cierre:**
- Backend: operativo local en puerto 8001, apuntando a Supabase producción
- Frontend: build ✅, dev server corriendo en 5179
- BD producción: operativa, legal_entities y act_catalog con datos, alembic_version desincronizada
- Git: árbol limpio (solo uvicorn_start.log sin trackear, no debe commitearse)

---

## Stack confirmado

| Capa | Tecnología |
|---|---|
| Backend | FastAPI 0.115 + SQLAlchemy 2.0 + Alembic + Uvicorn |
| Base de datos prod | PostgreSQL vía Supabase (egwdrdgtgmogcahhdtdy.supabase.co) |
| Base de datos local | SQLite (easypro2.db) |
| Frontend | Next.js 15.3 + React 19 + TypeScript + Tailwind CSS 3 |
| IA documental | OpenAI GPT-4o (Gari — generación .docx escrituras) |
| IA minutas | OpenAI GPT-4o-mini (detector B1/B2 + concordancia) |
| Storage | Supabase Storage (cases/case-{id}/draft/) |
| Despliegue frontend | Vercel — https://easypronotarial.com |
| Despliegue backend | Railway — https://easypronotarial-2-production.up.railway.app |
| Editor documentos | OnlyOffice — https://onlyoffice.easypronotarial.com |

---

## URLs de producción / servicios

| Servicio | URL |
|---|---|
| Frontend producción | https://easypronotarial.com |
| Backend producción | https://easypronotarial-2-production.up.railway.app |
| Supabase BD | https://egwdrdgtgmogcahhdtdy.supabase.co |
| OnlyOffice | https://onlyoffice.easypronotarial.com |
| Backend local | http://127.0.0.1:8001 |
| Frontend local | http://127.0.0.1:5179 |

---

## Estado git

Repositorio en `c:\EasyProNotarial-2\easypro2\` — rama `main`.
Remoto: https://github.com/cesargiraldoa/EasyProNotarial-2.git

---

## Migraciones Alembic — estado real en Supabase

| Migración | Schema real | alembic_version |
|---|---|---|
| base | ✅ aplicada | parte del head |
| 20260418_add_role_permissions_table | ✅ tabla existe | parte del head |
| 20260419_add_legal_entities | ✅ tabla existe, 6 registros | parte del head |
| 20260420_add_act_catalog | ✅ 11 registros | ✅ HEAD registrado |
| 20260512_add_user_identification | ✅ columnas existen en users | ❌ no registrada |
| 20260513_promote_legacy_notary_to_titular | desconocido (data migration) | ❌ no registrada |

**ACCIÓN PENDIENTE:** Ejecutar en Supabase:
```sql
UPDATE alembic_version SET version_num = '20260513_promote_legacy_notary_to_titular';
```

---

## Lo que existe y funciona hoy

### Backend — endpoints operativos (79 rutas totales)

| Módulo | Rutas | Estado |
|---|---|---|
| Auth | POST /login, GET /me | ✅ |
| Notarías | GET /notaries, GET /notaries/{id} | ✅ |
| Usuarios | CRUD + roles + permisos | ✅ |
| Plantillas | GET/PUT templates, 8 plantillas activas | ✅ |
| Personas naturales | GET/POST /persons + lookup | ✅ |
| Entidades jurídicas | GET/POST /legal-entities + apoderados | ✅ |
| Flujo documental | Wizard 5 pasos + Gari .docx | ✅ |
| Dashboard | GET /dashboard KPIs | ✅ |
| Catálogo de actos | act_catalog | ✅ |
| **Motor minutas** | POST /api/v1/minuta/analizar | ✅ nuevo |
| **Motor minutas** | POST /api/v1/minuta/generar | ✅ nuevo |

### Frontend — rutas operativas

| Ruta | Estado |
|---|---|
| /login | ✅ |
| /dashboard | ✅ KPIs |
| /dashboard/casos | ✅ |
| /dashboard/casos/crear | ✅ Wizard 5 pasos |
| /dashboard/casos/[caseId] | ✅ |
| /dashboard/notarias | ✅ |
| /dashboard/comercial | ✅ CRM |
| /dashboard/usuarios | ✅ |
| /dashboard/roles | ✅ |
| /dashboard/perfil | ✅ |
| /dashboard/actos-plantillas | ✅ |
| /dashboard/system-status | ✅ |
| **/dashboard/minutas/nueva** | ✅ nuevo — wizard 3 pasos |
| /dashboard/lotes | ⚠️ placeholder vacío |
| /dashboard/ayuda | ⚠️ placeholder vacío |
| /dashboard/configuracion | ⚠️ placeholder vacío |

### Agente Gari (escrituras)
- Motor: GPT-4o, max_tokens=16000, temperature=0.2
- ACTOS_POR_VARIANTE hardcodeado en gari_service.py

### Motor Minutas (nuevo)
- Detector B1/B2: GPT-4o-mini, temperature=0.1, max_tokens=8000
- Concordancia: GPT-4o-mini, temperature=0.1, max_tokens=4000
- SSL local: OPENAI_DISABLE_SSL_VERIFY=true en .env (no commitear)

### Entidades jurídicas en Supabase (6 — seed aplicado)
Fiduciaria Bancolombia, Constructora Contex S.A.S. BIC, Bancolombia S.A.,
Banco Davivienda, Fondo Nacional del Ahorro, Banco de Bogotá

---

## Pendientes críticos

### Para próxima sesión
1. **Alembic out-of-sync** — UPDATE alembic_version en Supabase (ver arriba)
2. **Menú lateral** — Agregar /dashboard/minutas/nueva al sidebar de AppShell
3. **Placeholders dashboard** — /lotes, /ayuda, /configuracion vacíos — limpiar antes de demo
4. **Personas incompletas en análisis** — jaggua devolvió 4/~10 personas. Revisar chunking o prompt
5. **Reset contraseña** — No implementado

### Deuda técnica
6. ACTOS_POR_VARIANTE hardcodeado → mover a BD
7. Búsqueda entidades con q corta retorna todo (falta filtro mínimo de chars)
8. Módulo facturación electrónica → diseñado, cero código
9. Módulo nómina electrónica → diseñado, cero código
10. Provider Adapter (Plemsi) → pendiente cotización

---

## Comandos para levantar entorno local

```bash
# Backend
cd c:\EasyProNotarial-2\easypro2\backend
.venv\Scripts\activate
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload

# Frontend (terminal separada)
cd c:\EasyProNotarial-2\easypro2\frontend
npm run dev
# → http://127.0.0.1:5179

# Verificar migraciones Alembic (contra producción)
cd c:\EasyProNotarial-2\easypro2\backend
alembic current
alembic heads
```

**NOTA:** .env del backend apunta a Supabase (ENVIRONMENT=production).
Para desarrollo local con SQLite: cambiar DATABASE_URL a `sqlite:///./easypro2.db`.

---

## Reglas técnicas del proyecto

1. **Multinotaría estricto** — Toda consulta filtra por notary_id. Nunca exponer datos cruzados.
2. **Roles** — Validar con require_roles() / has_role(). Roles: super_admin, admin_notary, notary, approver, protocolist, client.
3. **Provider Adapter** — Facturación/nómina NUNCA directo a Plemsi. Siempre vía ElectronicDocumentProvider.
4. **Sin secretos en código** — Solo en .env (excluido de git).
5. **Intervinientes dinámicos** — N compradores + N entidades. template_required_roles es obsoleto.
6. **Snapshot JSON** — CaseParticipant guarda snapshot en momento de guardado.
7. **Alembic obligatorio** — Todo schema change vía migración YYYYMMDD_descripcion.py.
8. **CORS** — FlexibleCORSMiddleware. Agregar dominios en _load_allowed_origins().
9. **Gari** — No cambiar max_tokens ni temperature sin revisar calidad de escrituras.
10. **Supabase Storage** — Archivos en cases/case-{id}/draft/. No mover sin actualizar gari_service.py.
11. **SSL local** — OPENAI_DISABLE_SSL_VERIFY=true solo en .env local. NO en Railway.

---

## Módulos diseñados — pendientes de implementar

### Facturación Electrónica
- Decisión: proveedor intermediario (Plemsi evaluado como principal)
- Arquitectura: Provider Adapter desacoplado
- Estado: **Solo diseño. Cero código.**

### Nómina Electrónica
- Mismo enfoque que facturación
- Estado: **Solo diseño. Cero código.**
