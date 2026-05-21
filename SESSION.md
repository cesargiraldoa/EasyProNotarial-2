# SESSION.md — EasyProNotarial-2

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
| Despliegue frontend | Vercel — https://easypro-notarial-2.vercel.app |
| Despliegue backend | Railway |
| Editor documentos | OnlyOffice — https://onlyoffice.easypronotarial.com |

---

## URLs de producción / servicios

| Servicio | URL |
|---|---|
| Frontend producción | https://easypro-notarial-2.vercel.app |
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
