# EasyPro Notarial 2 — Inventario Funcional Completo
Fecha: 16 de abril de 2026

---

## 1. DESCRIPCIÓN DEL PRODUCTO

EasyPro Notarial 2 es un SaaS multinotaría colombiano que digitaliza la operación documental de notarías. Genera escrituras, poderes y actos notariales usando IA (Gari — GPT-4o), gestiona el flujo completo desde la radicación hasta la firma notarial, y administra múltiples notarías desde una sola plataforma.

---

## 2. STACK TÉCNICO

### Frontend
- Next.js 15.3.1 + React 19.1.0 + TypeScript 5.8.3 + Tailwind CSS 3.4.17
- Iconos: Lucide React | Utilidades: clsx, tailwind-merge
- Puerto local: 5179

### Backend
- FastAPI 0.115.12 + Python 3.13 + SQLAlchemy 2.0.40
- Auth: JWT (python-jose) + passlib[bcrypt]
- BD driver: psycopg2-binary 2.9.10
- Docs Word: python-docx | IA: openai >= 1.0.0
- Storage: supabase-py (Supabase Storage SDK)
- Puerto local: 8001

### Base de Datos
- PostgreSQL en Supabase — proyecto easypro-notarial-2
- Project ID: egwdrdgtgmogcahhdtdy — Región: São Paulo

### Storage de Documentos
- Supabase Storage — bucket "documentos" (privado)
- Documentos generados por Gari → se suben en memoria → signed URL (1h)
- NUNCA usar filesystem local de Railway (efímero)

### IA
- Modelo: GPT-4o | Temperature: 0.2 | Max tokens: dinámico por variante (5200–7200)
- Separador párrafos Gari: [[--]] (legacy EasyPro 1)

---

## 3. INFRAESTRUCTURA Y ENTORNOS

### GitHub
- Usuario: cesargiraldoa
- Repo: github.com/cesargiraldoa/EasyProNotarial-2
- Rama: main
- Estructura: easypro2/backend/ + easypro2/frontend/

### Railway (Backend Producción)
- URL: https://easypronotarial-2-production.up.railway.app
- Health: https://easypronotarial-2-production.up.railway.app/health
- Root Directory: backend
- Start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
- Config: backend/railway.toml
- Region: us-west1 — Auto-deploy: sí, en cada push a main
- Variables:
  - DATABASE_URL: postgresql://postgres.egwdrdgtgmogcahhdtdy:[PASS]@aws-1-sa-east-1.pooler.supabase.com:5432/postgres
  - SECRET_KEY: [token hex 32]
  - OPENAI_API_KEY: [sk-...]
  - FRONTEND_URL: https://easypro-notarial-2.vercel.app
  - ENVIRONMENT: production
  - DEBUG: false
  - SUPABASE_URL: https://egwdrdgtgmogcahhdtdy.supabase.co
  - SUPABASE_SERVICE_KEY: sb_secret_YbrE_bg0iPzU7GwIHPKPhw_jfrR6UID

### Vercel (Frontend Producción)
- URL: https://easypro-notarial-2.vercel.app
- Deploy: npx vercel --prod desde C:\EasyProNotarial-2\easypro2\frontend
- Variables:
  - NEXT_PUBLIC_API_URL: https://easypronotarial-2-production.up.railway.app
  - NEXT_PUBLIC_APP_NAME: EasyPro 2
  - NEXT_PUBLIC_FRONTEND_URL: https://easypro-notarial-2.vercel.app

### Supabase
- Project ID: egwdrdgtgmogcahhdtdy | Region: sa-east-1
- Conexion local: db.egwdrdgtgmogcahhdtdy.supabase.co:5432
- Conexion produccion: aws-1-sa-east-1.pooler.supabase.com:5432 (Session Pooler)
- Usuario pooler: postgres.egwdrdgtgmogcahhdtdy
- CRITICO: Railway usa Session Pooler porque es IPv4. Dedicated Pooler es IPv6.
- Storage bucket: "documentos" (privado) — para documentos generados

---

## 4. CREDENCIALES

### Usuarios de prueba
- superadmin@easypro.co / ChangeMe123! — Super administrador global
- admin@notaria75.co / ChangeMe123! — Admin notaria 75
- notario@notaria75.co / ChangeMe123! — Notario notaria 75

### Notaria piloto
- Nombre: Notaria Unica del Circulo de Caldas
- URL objetivo: caldas.easypro.co
- Contacto: +57 310 793 2844
- Notario titular: Dr. José Manuel Hernández Franco

---

## 5. COMANDOS ESENCIALES

### Levantar local
```powershell
# Backend
cd C:\EasyProNotarial-2\easypro2\backend
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload

# Frontend
cd C:\EasyProNotarial-2\easypro2\frontend
npm run dev
```

### Deploy produccion
```powershell
# Push a Railway (auto-deploy backend)
cd C:\EasyProNotarial-2\easypro2
git add .
git commit -m "mensaje"
git push origin main

# Deploy Vercel frontend
cd C:\EasyProNotarial-2\easypro2\frontend
npx vercel --prod
```

### Repomix (contexto para IA)
```powershell
cd C:\EasyProNotarial-2\easypro2
npx repomix --output repomix-backend.xml backend/
npx repomix --output repomix-frontend.xml frontend/
```

### Reset secuencias PostgreSQL (Supabase SQL Editor)
```sql
DO $$
DECLARE t text;
BEGIN
  FOREACH t IN ARRAY ARRAY['cases','case_documents','case_document_versions','case_participants','case_act_data','case_timeline_events','case_workflow_events','persons']
  LOOP
    EXECUTE format('SELECT setval(pg_get_serial_sequence(%L, ''id''), COALESCE((SELECT MAX(id) FROM %I), 0) + 1, false)', t, t);
  END LOOP;
END;
$$;
```

---

## 6. ROLES DEL SISTEMA

- super_admin — gestión global, todas las notarías
- admin_notary — gestión administrativa de su notaría
- notary — firma y validación notarial
- approver — revisión y aprobación documental
- protocolist — gestión protocolaria y radicación
- client — consulta y seguimiento del caso

---

## 7. FLUJO PRINCIPAL DE UN CASO

1. Protocolista crea caso (wizard 5 pasos — selecciona plantilla de acto)
2. Ingresa datos generales del caso (notaría, responsables, protocolista, aprobador, notario)
3. Ingresa intervinientes según roles definidos por la plantilla
4. Ingresa datos específicos del acto (campos definidos por la plantilla)
5. Presiona Generar con Gari
6. resolver_escritura() detecta variante → valida campos → retorna configuración
7. build_gari_prompt() construye prompt con intervinientes por role_code + datos acto + instrucciones de variante
8. Gari (GPT-4o) redacta el documento notarial completo
9. save_gari_document_as_docx() genera Word en memoria → sube a Supabase Storage → retorna URL
10. Se guarda como borrador Word versionado (v1, v2, v3...) con URL de Storage
11. Aprobador revisa en previsualizador (Documento Gari tab)
12. Correcciones en lenguaje natural (modo revisor) [pendiente fix]
13. Aprobador aprueba [pendiente fix]
14. Notario firma
15. PDF final generado

---

## 8. MOTOR GARI — ARQUITECTURA DE AGENTE

### Principios heredados de Helexium-2
1. Solo lo pedido — no inventar datos ni cláusulas
2. Cambio mínimo — plantilla fija antes que GPT-4o libre
3. Reutilización máxima — texto jurídico real como base
4. Validar antes de generar — campos_faltantes → 422 antes de GPT-4o
5. Reportar, no arreglar — lista exacta de qué falta
6. Trazabilidad total — variante_id, versión, actor, timestamp

### Funciones principales (gari_document_service.py)

#### resolver_escritura()
- Entrada: proyecto, tipo_inmueble, num_compradores, banco_hipotecante, campos_caso
- Salida: variante_id, actos_requeridos, plantilla_id, campos_requeridos, campos_faltantes, banco_nit, max_tokens_estimado
- 8 variantes soportadas:

| variante_id | proyecto | inmueble | compradores | banco | tokens |
|---|---|---|---|---|---|
| aragua_apto_1c | aragua | apartamento | 1 | Bancolombia | 5500 |
| aragua_apto_2c | aragua | apartamento | 2 | Bancolombia | 5800 |
| aragua_parq_2c | aragua | parqueadero | 2 | Bancolombia | 5200 |
| aragua_parq_3c | aragua | parqueadero | 3 | Bancolombia | 5400 |
| jaggua_fna_1c | jaggua | apartamento | 1 | FNA | 6500 |
| jaggua_fna_2c | jaggua | apartamento | 2 | FNA | 6800 |
| jaggua_bogota_1c | jaggua | apartamento | 1 | Banco Bogotá | 6800 |
| jaggua_bogota_2c | jaggua | apartamento | 2 | Banco Bogotá | 7200 |

#### build_gari_prompt()
- Construye prompt con todos los intervinientes agrupados por role_code
- ROLES_LABEL dict para etiquetas en mayúsculas notariales
- Sección VARIANTE DOCUMENTAL con orden de actos (si aplica)
- Instrucciones de redacción: datos exactos, no inventar, lenguaje notarial colombiano

#### generate_notarial_document()
- Llama GPT-4o con max_tokens dinámico por variante
- temperature=0.2 para consistencia jurídica

#### save_gari_document_as_docx()
- Genera Word en memoria (io.BytesIO)
- Agrega guiones al final de cada párrafo (práctica notarial colombiana)
- Sube a Supabase Storage bucket "documentos"
- Retorna signed URL (3600 segundos de vigencia)

### Roles de intervinientes

| role_code | label | Poder General | Compraventa VIS |
|---|---|---|---|
| poderdante | Poderdante | obligatorio | — |
| apoderado | Apoderado(a) | obligatorio | — |
| comprador_1 | Comprador(a) 1 | — | obligatorio |
| comprador_2 | Comprador(a) 2 | — | opcional |
| comprador_3 | Comprador(a) 3 | — | opcional |
| apoderado_fideicomiso | Apoderado(a) Fideicomiso | — | obligatorio |
| apoderado_fideicomitente | Apoderado(a) Fideicomitente | — | obligatorio |
| apoderado_banco_libera | Apoderado(a) banco que libera | — | obligatorio |
| apoderado_banco_hipoteca | Apoderado(a) banco hipotecante | — | opcional |

---

## 9. PLANTILLAS DISPONIBLES EN BD

### Poder General (slug: poder-general)
- Estado: operativo ✅
- Roles: poderdante, apoderado
- Campos del acto: dia_elaboracion, mes_elaboracion, ano_elaboracion, derechos_notariales, iva, aporte_superintendencia, fondo_notariado, consecutivos_hojas, extension, clase_cuantia
- Archivo físico: backend/storage/templates/poder-general.docx (en git con git add -f)
- storage_path en BD: 'storage/templates/poder-general.docx' (relativo)

### Compraventa VIS (slug: compraventa-vis)
- Estado: definida en seed, pendiente ejecutar en producción ⚠️
- Roles: 7 roles (ver tabla anterior)
- Campos del acto: 29 campos (proyecto, tipo_inmueble, banco_hipotecante, numero_apartamento, matricula_inmobiliaria, cedula_catastral, linderos, numero_piso, area_privada, area_total, altura, coeficiente_copropiedad, avaluo_catastral, valor_venta, valor_venta_letras, cuota_inicial, cuota_inicial_letras, valor_hipoteca, valor_hipoteca_letras, origen_cuota_inicial, fecha_promesa_compraventa, inmueble_sera_casa_habitacion, tiene_bien_afectado, paz_salvo_predial_numero, paz_salvo_predial_fecha, paz_salvo_predial_vigencia, dia_elaboracion, mes_elaboracion, ano_elaboracion)

---

## 10. TABLAS BASE DE DATOS

| Tabla | Descripción | Registros |
|---|---|---|
| notaries | Catálogo de notarías | 119 |
| users | Usuarios del sistema | 9 (prueba) |
| roles | Roles del sistema | — |
| role_assignments | Asignación de roles a usuarios | — |
| cases | Casos notariales | variable |
| case_participants | Intervinientes por caso | variable |
| case_act_data | Datos del acto en JSON + gari_draft_text | variable |
| case_documents | Documentos del caso | variable |
| case_document_versions | Versiones de documentos (v1, v2...) | variable |
| case_timeline_events | Línea de tiempo del caso | variable |
| case_workflow_events | Eventos del flujo con metadata (variante_id) | variable |
| case_state_definitions | Estados del caso por tipo | 12 estados para escritura |
| case_internal_notes | Notas internas | variable |
| case_client_comments | Comentarios del cliente | variable |
| document_templates | Plantillas de actos | 2 (Poder General + Compraventa VIS) |
| template_fields | Campos por plantilla | variable |
| template_required_roles | Roles requeridos por plantilla | variable |
| persons | Catálogo de intervinientes reutilizables | variable |
| numbering_sequences | Secuencias de numeración | variable |
| notary_commercial_activities | Actividad CRM | variable |
| notary_crm_audit_log | Auditoría CRM | variable |

### Estados del caso (escritura)
1. borrador (inicial)
2. en_diligenciamiento
3. revision_cliente
4. ajustes_solicitados
5. revision_aprobador
6. devuelto_aprobador
7. revision_notario
8. rechazado_notario
9. aprobado_notario
10. generado (después de Gari)
11. firmado_cargado
12. cerrado (final)

---

## 11. ENDPOINTS API PRINCIPALES

### Auth
| Método | Ruta | Descripción |
|---|---|---|
| GET | /health | Health check sin auth |
| POST | /api/v1/auth/login | Login JWT |
| GET | /api/v1/auth/me | Usuario actual |

### Catálogos
| Método | Ruta | Descripción |
|---|---|---|
| GET | /api/v1/notaries | Listado notarías |
| GET | /api/v1/users | Listado usuarios |
| GET | /api/v1/users/options | Usuarios para selects |
| GET | /api/v1/cases | Listado casos |
| GET/POST | /api/v1/persons | Intervinientes |
| GET | /api/v1/templates | Plantillas |
| GET | /api/v1/templates/active | Plantillas activas |
| GET | /api/v1/dashboard | Resumen ejecutivo |

### Flujo documental
| Método | Ruta | Descripción |
|---|---|---|
| POST | /api/v1/document-flow/cases/from-template | Crear caso desde plantilla |
| GET | /api/v1/document-flow/cases/{id} | Detalle caso |
| PUT | /api/v1/document-flow/cases/{id}/participants | Guardar intervinientes |
| PUT | /api/v1/document-flow/cases/{id}/act-data | Guardar datos acto |
| POST | /api/v1/document-flow/cases/{id}/generate-with-gari | Generar con Gari (principal) |
| POST | /api/v1/document-flow/cases/{id}/generate-draft | Generar borrador plantilla Word |
| POST | /api/v1/document-flow/cases/{id}/approve | Aprobar caso |
| POST | /api/v1/document-flow/cases/{id}/export | Exportar documento |
| GET | /api/v1/document-flow/cases/{id}/documents/{did}/versions/{vid}/download | Descargar versión |

---

## 12. PÁGINAS FRONTEND

| Ruta | Descripción | Estado |
|---|---|---|
| / | Landing page marketing | operativo ✅ |
| /login | Login institucional | operativo ✅ |
| /dashboard | Resumen ejecutivo | operativo ✅ |
| /dashboard/casos | Listado casos | operativo ✅ |
| /dashboard/casos/crear | Wizard 5 pasos | operativo ✅ (roles/campos hardcodeados Poder General) |
| /dashboard/casos/{id} | Detalle + Gari + Previsualizador | operativo ✅ |
| /dashboard/actos-plantillas | Plantillas notariales | operativo ✅ |
| /dashboard/notarias | Gestión notarías | operativo ✅ |
| /dashboard/notarias/{id} | Detalle notaría | operativo ✅ |
| /dashboard/usuarios | Gestión usuarios | operativo ✅ |
| /dashboard/comercial | CRM notarías | operativo ✅ |
| /dashboard/lotes | Operación masiva | parcial ⚠️ |
| /dashboard/system-status | Estado sistema | operativo ✅ |
| /dashboard/configuracion | Configuración | operativo ✅ |
| /dashboard/perfil | Perfil usuario | operativo ✅ |
| /dashboard/ayuda | Ayuda | operativo ✅ |

---

## 13. ARCHIVOS CLAVE

### Backend
| Archivo | Descripción |
|---|---|
| app/main.py | FastAPI app + FlexibleCORSMiddleware (orígenes hardcodeados) |
| app/core/config.py | Settings pydantic |
| app/core/deps.py | Dependencies JWT + roles |
| app/core/security.py | Hash + JWT |
| app/db/session.py | Engine SQLAlchemy |
| app/db/seed.py | ensure_power_general_template() + ensure_compraventa_vis_template() |
| app/services/gari_document_service.py | Motor IA: resolver_escritura, build_gari_prompt, generate_notarial_document, save_gari_document_as_docx → Supabase Storage |
| app/services/storage.py | Rutas de storage con BASE_DIR relativo |
| app/modules/document_flow/router.py | Flujo documental con validación de variante |
| app/modules/notaries/router.py | Notarías (fix GROUP BY con subquery) |
| app/modules/cases/router.py | Casos |
| backend/railway.toml | Config Railway |
| backend/requirements.txt | Dependencias (incluye supabase-py) |
| backend/storage/templates/poder-general.docx | Plantilla Word Poder General (en git con -f) |

### Frontend
| Archivo | Descripción |
|---|---|
| app/(marketing)/page.tsx | Landing |
| app/(marketing)/login/page.tsx | Login |
| components/cases/create-case-wizard.tsx | Wizard 5 pasos (grid 2 cols, SearchableSelect mejorado) |
| lib/api.ts | Cliente API + cookies SameSite=None; Secure + createDocumentCase + saveCaseParticipants |
| middleware.ts | Protección rutas con request.nextUrl.origin |

---

## 14. PENDIENTES Y ROADMAP

### Críticos — próxima sesión
1. **Fix descarga Word** — signed URL de Supabase Storage no llega bien al endpoint de descarga del frontend. Revisar cómo se pasa la URL desde case_document_versions al endpoint de descarga
2. **Fix correcciones lenguaje natural** — "Aplicar correcciones" no ejecuta. Revisar el endpoint que recibe el texto de corrección y llama a Gari
3. **Fix aprobación** — botón "Aprobar documento" no funciona. Revisar endpoint approve y flujo de estado revision_notario → aprobado_notario
4. **Wizard dinámico** — paso 3 debe leer template.required_roles de BD y renderizar un bloque por rol. Paso 4 debe leer template.fields y renderizar campo según field_type (text, number, select, textarea). Actualmente hardcodeado para Poder General
5. **Seed compraventa-vis en producción** — ejecutar ensure_compraventa_vis_template() en Railway Shell: `PYTHONPATH=/app python /app/app/db/seed.py`

### Sprint siguiente
6. Prueba end-to-end compraventa VIS completa con 7 intervinientes y 29 campos
7. Más tipos de acto: sucesión, declaraciones, hipoteca independiente
8. RNEC integración
9. Firma digital certificada
10. Operación masiva de lotes completa
11. Portal cliente
12. DNS caldas.easypro.co → Vercel
13. Branding dinámico por notaría (slug, colores, imagen desde BD)
14. Validación operativa con Notaría de Caldas (+57 310 793 2844)
15. Cambiar contraseñas por defecto (ChangeMe123!)

---

## 15. DATOS DEL SISTEMA EN PRODUCCIÓN (16 ABR 2026)

- Notarías en catálogo: 119
- Usuarios: 9
- Plantillas activas: 1 (Poder General) + 1 pendiente activar (Compraventa VIS)
- Casos de prueba: variable
- Caso de prueba exitoso: CAS-2026-0914 (Poder General — Gari v6 generado)

---

## 16. REGLAS DE DESARROLLO

- NUNCA usar tag form en React — usar div con onClick
- SIEMPRE UTF-8 sin BOM
- NUNCA subir .env ni .db a GitHub
- Puerto frontend local: 5179 | backend local: 8001
- Deploy frontend: npx vercel --prod desde CLI (no auto-deploy GitHub)
- PostgreSQL: subqueries en vez de GROUP BY con joins
- Cookies producción: SameSite=None; Secure
- Middleware Next.js: usar request.nextUrl.origin para redirects
- Limpiar .next si hay errores webpack
- NUNCA guardar archivos en disco de Railway (filesystem efímero) — usar Supabase Storage
- Archivos binarios en git: git add -f para forzar si está en .gitignore
- Secuencias PostgreSQL: resetear con DO $$ en Supabase SQL Editor cuando hay UniqueViolation
- Codex no puede hacer PR con archivos binarios — pedir commit directo a main
- storage_path en BD debe ser ruta relativa (no absoluta de Windows)
- Todos los intervinientes son dinámicos — NUNCA hardcodear nombres de personas en código o prompts
