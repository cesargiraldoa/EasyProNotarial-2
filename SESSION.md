EasyPro Notarial 2 — SESSION.md
Fecha última actualización: 16 de abril de 2026

QUÉ ES
Software notarial SaaS multinotaría para digitalizar la operación documental de notarías colombianas. Genera escrituras, poderes y actos notariales usando IA (Gari — GPT-4o). Primera notaría piloto: Notaría Única del Círculo de Caldas (Antioquia).

STACK TÉCNICO

Frontend: Next.js 15 + React 19 + TypeScript + Tailwind CSS
Backend: FastAPI + Python 3.13 + SQLAlchemy + Pydantic + Uvicorn
BD: Supabase PostgreSQL — proyecto easypro-notarial-2 — región São Paulo
Storage documentos: Supabase Storage — bucket "documentos" (privado)
IA: OpenAI GPT-4o (Gari — motor documental notarial)
Repo: github.com/cesargiraldoa/EasyProNotarial-2 — rama main


URLS DE PRODUCCIÓN

Frontend: https://easypro-notarial-2.vercel.app
Backend: https://easypronotarial-2-production.up.railway.app
Health: https://easypronotarial-2-production.up.railway.app/health


URLS LOCALES

Frontend: http://127.0.0.1:5179
Backend: http://127.0.0.1:8001
Health: http://127.0.0.1:8001/health


CREDENCIALES DE PRUEBA

superadmin@easypro.co / ChangeMe123!
admin@notaria75.co / ChangeMe123!
notario@notaria75.co / ChangeMe123!


COMANDOS PARA LEVANTAR EN LOCAL
Backend
powershellcd C:\EasyProNotarial-2\easypro2\backend
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
Frontend
powershellcd C:\EasyProNotarial-2\easypro2\frontend
npm run dev
Deploy a producción (Vercel desde CLI)
powershellcd C:\EasyProNotarial-2\easypro2\frontend
npx vercel --prod
Git push (Railway redespliega automáticamente)
powershellcd C:\EasyProNotarial-2\easypro2
git add .
git commit -m "mensaje"
git push origin main
Reset secuencias PostgreSQL (ejecutar en Supabase SQL Editor cuando hay UniqueViolation)
sqlDO $$
DECLARE t text;
BEGIN
  FOREACH t IN ARRAY ARRAY['cases','case_documents','case_document_versions','case_participants','case_act_data','case_timeline_events','case_workflow_events','persons']
  LOOP
    EXECUTE format('SELECT setval(pg_get_serial_sequence(%L, ''id''), COALESCE((SELECT MAX(id) FROM %I), 0) + 1, false)', t, t);
  END LOOP;
END;
$$;

INFRAESTRUCTURA
GitHub

Usuario: cesargiraldoa
Repo: github.com/cesargiraldoa/EasyProNotarial-2
Rama principal: main
Estructura repo: easypro2/backend + easypro2/frontend

Railway (Backend)

Proyecto: EasyProNotarial-2
URL: easypronotarial-2-production.up.railway.app
Root Directory: backend
Start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
Region: us-west1
Auto-deploy: sí, en cada push a main

Variables Railway

DATABASE_URL: postgresql://postgres.egwdrdgtgmogcahhdtdy:[PASSWORD]@aws-1-sa-east-1.pooler.supabase.com:5432/postgres
SECRET_KEY: [generada con secrets.token_hex(32)]
OPENAI_API_KEY: [key OpenAI]
FRONTEND_URL: https://easypro-notarial-2.vercel.app
ENVIRONMENT: production
DEBUG: false
SUPABASE_URL: https://egwdrdgtgmogcahhdtdy.supabase.co
SUPABASE_SERVICE_KEY: sb_secret_YbrE_bg0iPzU7GwIHPKPhw_jfrR6UID

Vercel (Frontend)

Proyecto: easypro-notarial-2
URL: easypro-notarial-2.vercel.app
Deploy: npx vercel --prod desde C:\EasyProNotarial-2\easypro2\frontend

Variables Vercel

NEXT_PUBLIC_API_URL: https://easypronotarial-2-production.up.railway.app
NEXT_PUBLIC_APP_NAME: EasyPro 2
NEXT_PUBLIC_FRONTEND_URL: https://easypro-notarial-2.vercel.app

Supabase

Proyecto: easypro-notarial-2
Project ID: egwdrdgtgmogcahhdtdy
Región: São Paulo (sa-east-1)
Conexión producción: Session Pooler — aws-1-sa-east-1.pooler.supabase.com:5432
Conexión local: db.egwdrdgtgmogcahhdtdy.supabase.co:5432
Usuario pooler: postgres.egwdrdgtgmogcahhdtdy
IMPORTANTE: Railway usa Session Pooler (no Direct) porque Railway es IPv4
Storage bucket: "documentos" — privado — para documentos generados por Gari


LO REALIZADO — 16 ABR 2026
Arquitectura Gari — motor documental de excelencia

Análisis profundo de 9 documentos Word reales de la Notaría de Caldas ✅
Identificadas 2 familias de escrituras: ARAGUA (Bancolombia/Davivienda) y JAGGUA (FNA/Banco Bogotá) ✅
Identificadas 8 variantes documentales con actos, roles e intervinientes específicos ✅
Decisión arquitectónica clave: modelo es "texto fijo legal + sustitución dinámica de campos" NO generación libre ✅
Principios de agente tomados de Helexium-2: solo lo pedido, cambio mínimo, validar antes de generar, trazabilidad ✅

Nueva función resolver_escritura()

Archivo: backend/app/services/gari_document_service.py
Detecta variante exacta: proyecto + tipo_inmueble + num_compradores + banco_hipotecante
8 variantes: aragua_apto_1c, aragua_apto_2c, aragua_parq_2c, aragua_parq_3c, jaggua_fna_1c, jaggua_fna_2c, jaggua_bogota_1c, jaggua_bogota_2c
Devuelve: variante_id, actos_requeridos, plantilla_id, campos_requeridos, campos_faltantes, banco_nit, max_tokens_estimado
max_tokens dinámico por variante (5200 a 7200 según complejidad) ✅

Integración resolver_escritura en endpoint generate-with-gari

Archivo: backend/app/modules/document_flow/router.py
Ejecuta resolver_escritura SOLO si act_data contiene clave "proyecto" (no aplica a Poder General)
Valida campos_faltantes antes de llamar GPT-4o → HTTP 422 con lista exacta de faltantes ✅
max_tokens dinámico según variante ✅
variante_id trazada en metadata de timeline y workflow ✅

Mejora build_gari_prompt()

Roles de intervinientes agrupados por role_code con labels notariales en mayúsculas ✅
ROLES_LABEL dict: comprador_1/2/3, apoderado_fideicomiso, apoderado_fideicomitente, apoderado_banco_libera, apoderado_banco_hipoteca ✅
Instrucciones de redacción correctas: datos exactos, no inventar, orden de actos por variante ✅
Práctica notarial colombiana: guiones rellenan espacio DESPUÉS del texto en save_gari_document_as_docx() ✅

Nueva plantilla compraventa-vis en seed

Archivo: backend/app/db/seed.py — función ensure_compraventa_vis_template()
7 roles: comprador_1, comprador_2, comprador_3, apoderado_fideicomiso, apoderado_fideicomitente, apoderado_banco_libera, apoderado_banco_hipoteca
29 campos: proyecto, tipo_inmueble, banco_hipotecante, numero_apartamento, matricula_inmobiliaria, cedula_catastral, linderos, numero_piso, area_privada, area_total, altura, coeficiente_copropiedad, avaluo_catastral, valor_venta, valor_venta_letras, cuota_inicial, cuota_inicial_letras, valor_hipoteca, valor_hipoteca_letras, origen_cuota_inicial, fecha_promesa_compraventa, inmueble_sera_casa_habitacion, tiene_bien_afectado, paz_salvo_predial_numero, paz_salvo_predial_fecha, paz_salvo_predial_vigencia, dia_elaboracion, mes_elaboracion, ano_elaboracion ✅

Fix CORS producción

FlexibleCORSMiddleware corregida en backend/app/main.py ✅
Orígenes hardcodeados: localhost:3000, localhost:5179, 127.0.0.1:5179, easypro-notarial-2.vercel.app ✅
CORS responde correctamente a preflight OPTIONS ✅
CORS falla silenciosamente cuando el backend devuelve 500 — normal ✅

Fix secuencias PostgreSQL

Secuencias desincronizadas por seeds con IDs manuales ✅
Reset ejecutado en Supabase SQL Editor para todas las tablas de casos ✅
Comando DO $$ incluido en SESSION.md para futura referencia ✅

Fix storage_path en BD

Template poder-general tenía path Windows hardcodeado en BD ✅
Actualizado a ruta relativa: 'storage/templates/poder-general.docx' ✅
storage.py usa BASE_DIR relativo al archivo en vez de path absoluto ✅

Supabase Storage para documentos generados

Bucket "documentos" creado en Supabase Storage (privado) ✅
Variables SUPABASE_URL y SUPABASE_SERVICE_KEY agregadas en Railway ✅
save_gari_document_as_docx() ahora sube a Supabase Storage en vez de filesystem local ✅
Retorna URL firmada (signed URL con 1 hora de vigencia) ✅
supabase-py agregado a requirements.txt ✅

Mejora UX wizard — paso 2 y 3

SearchableSelect cierra al seleccionar opción ✅
Grid de 2 columnas en paso 2 (datos generales) y paso 3 (intervinientes) ✅
Layout limpio y ordenado ✅

Fix wizard paso 2 — Failed to fetch

Variables de entorno faltaban en Vercel (NEXT_PUBLIC_API_URL no estaba configurada) ✅
Agregadas las 3 variables en Vercel → redeploy ✅

Prueba end-to-end Poder General — EXITOSA ✅

Caso CAS-2026-0914 creado en producción ✅
Intervinientes: Néstor William Herrera Díaz (poderdante) + Carlos Manuel Pérez Rendón (apoderado) ✅
Gari generó v6 del documento — Poder General completo en lenguaje notarial colombiano ✅
Documento con cabecera, facultades en capítulos, constancias legales, liquidación de derechos, firmas ✅


ESTADO ACTUAL — 16 ABR 2026
Completado

Landing page completa — paleta oscura Finaktiva ✅
Login con imagen notarial ✅
Dashboard operativo con PostgreSQL ✅
Motor Gari — genera documentos notariales completos ✅
Previsualizador con modo revisor ✅
Versionado de documentos (v1, v2, v3...) ✅
Deploy Railway — backend FastAPI en producción ✅
Deploy Vercel — frontend Next.js en producción ✅
CORS resuelto con FlexibleCORSMiddleware ✅
resolver_escritura() — detección de variante documental ✅
Validación de campos antes de generar ✅
Plantilla compraventa-vis con 7 roles y 29 campos en seed ✅
Supabase Storage configurado para documentos ✅
Práctica notarial de guiones en documentos ✅

Pendientes críticos

Descarga Word — botón "Descargar Word" no funciona (signed URL expira o URL no se pasa bien al frontend)
Correcciones en lenguaje natural — "Aplicar correcciones" no ejecuta
Aprobación — botón "Aprobar documento" no funciona
Wizard dinámico — paso 3 y 4 deben renderizar roles y campos según la plantilla seleccionada (no hardcodeados para Poder General)
Seed compraventa-vis en producción — ejecutar ensure_compraventa_vis_template() en Railway
DNS caldas.easypro.co apuntar a Vercel
Branding dinámico por notaría
Validación operativa con Notaría de Caldas
Cambiar contraseñas por defecto


PRÓXIMO SPRINT — PRIORIDADES
Crítico inmediato

Fix descarga Word — el signed URL de Supabase Storage debe llegar correctamente al endpoint de descarga del frontend
Fix correcciones — el endpoint de correcciones en lenguaje natural debe llamar a Gari con el texto de corrección
Fix aprobación — revisar endpoint approve y flujo de estado

Sprint siguiente

Wizard dinámico — paso 3 renderiza template.required_roles, paso 4 renderiza template.fields
Seed en producción — correr ensure_compraventa_vis_template() vía Railway shell
Prueba end-to-end compraventa VIS — caso completo con 7 intervinientes y 29 campos
Más tipos de acto en Gari (sucesión, declaraciones)
RNEC integración
Firma digital certificada
Operación masiva de lotes completa
Portal cliente


ARQUITECTURA GARI — PRINCIPIOS (de Helexium-2)

Solo lo pedido — no inventar datos ni cláusulas no solicitadas
Cambio mínimo — plantilla fija antes que generación libre con GPT-4o
Reutilización máxima — texto jurídico ya validado como base
Validar antes de generar — campos_faltantes → 422 antes de llamar GPT-4o
Reportar, no arreglar — si detecta problema, informa exactamente qué falta
Trazabilidad total — variante_id, versión, actor, timestamp en cada generación


TIPOS DE ESCRITURA IDENTIFICADOS
Familia ARAGUA (Fideicomiso P.A. Aragua de Primavera)

Fideicomiso: NIT 830.054.539-0 vocera Fiduciaria Bancolombia S.A.
Fideicomitente: Constructora Contex S.A.S. BIC NIT 900.082.107-5
Banco que libera: Bancolombia S.A. NIT 890.903.938-8 (Etapas 1-2) o Davivienda NIT 860.034.313-7 (Etapa 5)
Variantes: aragua_apto_1c, aragua_apto_2c, aragua_parq_2c, aragua_parq_3c

Familia JAGGUA (Fideicomiso P.A. Jaggua)

Fideicomiso: NIT 830.054.539-0 vocera Fiduciaria Bancolombia S.A.
Fideicomitente: Constructora Contex S.A.S. BIC NIT 900.082.107-5
Banco que libera: FNA NIT 899.999.284-4
Banco hipotecante nuevo: FNA o Banco de Bogotá NIT 860.002.964-4
Variantes: jaggua_fna_1c, jaggua_fna_2c, jaggua_bogota_1c, jaggua_bogota_2c

IMPORTANTE: Todos los intervinientes son dinámicos

Los representantes del fideicomiso, fideicomitente y bancos rotan y cambian
NUNCA hardcodear nombres de personas en el código
Todos van como participantes del caso con role_code específico


ROLES DE INTERVINIENTES POR TIPO DE ESCRITURA
Poder General

poderdante (obligatorio)
apoderado (obligatorio)

Compraventa VIS

comprador_1 (obligatorio)
comprador_2 (opcional — 2c y 3c)
comprador_3 (opcional — solo 3c)
apoderado_fideicomiso (obligatorio)
apoderado_fideicomitente (obligatorio)
apoderado_banco_libera (obligatorio)
apoderado_banco_hipoteca (opcional — solo variantes con hipoteca nueva)


TABLAS BASE DE DATOS

notaries — catálogo de notarías (119 registros)
users — usuarios (9 registros de prueba)
roles + role_assignments — control de acceso
cases — casos notariales
case_participants — intervinientes por caso
case_act_data — datos del acto en JSON + gari_draft_text
case_documents + case_document_versions — docs y versiones
case_timeline_events — línea de tiempo del caso
case_workflow_events — eventos del flujo
case_state_definitions — estados del caso
case_internal_notes — notas internas
case_client_comments — comentarios cliente
document_templates + template_fields — plantillas de actos
template_required_roles — roles requeridos por plantilla
persons — catálogo de intervinientes reutilizables
numbering_sequences — secuencias de numeración


ENDPOINTS API PRINCIPALES

GET /health
POST /api/v1/auth/login
GET /api/v1/auth/me
GET /api/v1/notaries
GET /api/v1/users
GET /api/v1/cases
GET/POST /api/v1/persons
GET/POST /api/v1/templates
GET /api/v1/templates/active
GET /api/v1/dashboard
POST /api/v1/document-flow/cases/from-template
GET /api/v1/document-flow/cases/{id}
PUT /api/v1/document-flow/cases/{id}/participants
PUT /api/v1/document-flow/cases/{id}/act-data
POST /api/v1/document-flow/cases/{id}/generate-with-gari
POST /api/v1/document-flow/cases/{id}/generate-draft
POST /api/v1/document-flow/cases/{id}/approve
POST /api/v1/document-flow/cases/{id}/export
GET /api/v1/document-flow/cases/{id}/documents/{did}/versions/{vid}/download


ARCHIVOS CLAVE
Backend

app/main.py — FastAPI app + FlexibleCORSMiddleware (orígenes hardcodeados)
app/core/config.py — Settings pydantic
app/core/deps.py — Dependencies JWT + roles
app/services/gari_document_service.py — Motor IA Gari + resolver_escritura() + build_gari_prompt() + save_gari_document_as_docx() → Supabase Storage
app/services/storage.py — Rutas relativas con BASE_DIR
app/modules/document_flow/router.py — Flujo documental con validación de variante
app/db/seed.py — ensure_power_general_template() + ensure_compraventa_vis_template()
backend/railway.toml — Config Railway

Frontend

app/(marketing)/page.tsx — Landing
app/(marketing)/login/page.tsx — Login
app/(app)/dashboard/ — Dashboard y subpáginas
components/cases/create-case-wizard.tsx — Wizard 5 pasos (roles y campos actualmente hardcodeados para Poder General)
lib/api.ts — Cliente API + cookies SameSite=None; Secure


MOTOR GARI
Archivo principal
backend/app/services/gari_document_service.py
Funciones

resolver_escritura() — detecta variante, valida campos, retorna config completa
build_gari_prompt() — construye prompt con intervinientes por role_code + datos acto + instrucciones por variante
generate_notarial_document() — llama GPT-4o con max_tokens dinámico
save_gari_document_as_docx() — genera Word en memoria → sube a Supabase Storage → retorna URL firmada
get_supabase_client() — cliente Supabase para storage

Endpoint principal
POST /api/v1/document-flow/cases/{id}/generate-with-gari
Flujo

Carga act_data de BD
Si act_data tiene "proyecto" → llama resolver_escritura() → valida campos
Construye lista de participantes con role_code
Llama build_gari_prompt() con variante_id
Llama generate_notarial_document() con max_tokens dinámico
Guarda texto en case_act_data.gari_draft_text
Genera Word en memoria → sube a Supabase Storage
Crea case_document_version con URL de Storage
Actualiza estado del caso y traza en timeline/workflow


NOTARÍA PILOTO

Nombre: Notaría Única del Círculo de Caldas
URL objetivo: caldas.easypro.co
Contacto: +57 310 793 2844
Notario titular: Dr. José Manuel Hernández Franco


PALETA DE COLORES

Fondo principal: #0D1B2A
Fondo alterno: #112236
Cards: #1A3350
Acento principal: #00E5A0
Acento hover: #00C98A
Texto secundario: #8892A4


REGLAS DE DESARROLLO

NUNCA usar tag form en React — usar div con onClick
SIEMPRE UTF-8 sin BOM
NUNCA subir .env ni .db a GitHub
Puerto frontend local: 5179 | backend local: 8001
Deploy frontend: npx vercel --prod desde CLI (no auto-deploy GitHub)
PostgreSQL: subqueries en vez de GROUP BY con joins
Cookies producción: SameSite=None; Secure
Middleware Next.js: usar request.nextUrl.origin para redirects
Limpiar .next si hay errores webpack
Railway filesystem es efímero — NUNCA guardar archivos en disco en producción, usar Supabase Storage
Archivos binarios (.docx) en git: usar git add -f para forzar si está en .gitignore
Secuencias PostgreSQL: resetear con DO $$ cuando hay UniqueViolation en cases o tablas relacionadas
Codex no puede hacer PR con archivos binarios — hacer commit directo a main