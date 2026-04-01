# SESSION.md — EasyPro Notarial 2
> Última actualización: 31 Mar 2026 — cierre del día

---

## OBJETIVO DEL PROYECTO

Software notarial SaaS multinotaría para digitalizar la operación documental de notarías colombianas. Go-live con Notaría de Caldas el 9 de abril de 2026.

---

## ENTORNO DE TRABAJO

### Backend
```powershell
cd C:\EasyProNotarial-2\easypro2\backend
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

### Frontend
```powershell
cd C:\EasyProNotarial-2\easypro2\frontend
npm run dev
```

### URLs locales
- Frontend: http://localhost:5179
- Backend: http://127.0.0.1:8001
- Health: http://127.0.0.1:8001/health

### Credenciales semilla
- superadmin@easypro.co / ChangeMe123!
- admin@notaria75.co / ChangeMe123!
- notario@notaria75.co / ChangeMe123!

### Base de datos
- SQLite local: backend/easypro2.db
- Backup del día: backend/easypro2_backup_20260331_1903.db

---

## STACK

- Frontend: Next.js 15 + React 19 + TypeScript + Tailwind
- Backend: FastAPI + Python + SQLAlchemy + Pydantic + Uvicorn
- BD: SQLite local (migrar a Supabase PostgreSQL antes del go-live)
- Puerto frontend: 5179
- Puerto backend: 8001

---

## INFRAESTRUCTURA OBJETIVO

| Servicio | Plan | Estado |
|---|---|---|
| Supabase | Pro $25/mes | Proyecto creado — São Paulo — pendiente migración datos |
| Railway | Starter $10-20/mes | Pendiente crear cuenta |
| Vercel | Hobby $0/mes | Pendiente crear cuenta |
| Dominio | helexium.co subdominios | Pendiente configurar DNS |

### Subdominios objetivo
- caldas.easypro.co → Notaría de Caldas (go-live 9 Abr)

### Costos estimados
- Infraestructura: USD $35-45/mes
- Herramientas IA (Claude + ChatGPT): USD $40-200/mes
- Total: USD $85-270/mes

---

## ESTADO DEL REPO

- Repo: C:\EasyProNotarial-2\easypro2
- Rama: master
- Último commit: 333dfc8
- BD: SQLite local

---

## COMMITS DEL 31 MAR 2026

| Commit | Descripción |
|---|---|
| 8eabf12 | feat: estado inicial EasyPro2 — estructura base frontend Next.js + backend FastAPI |
| 333dfc8 | feat: landing Finaktiva completa + login imagen notarial + footer + botones flotantes WhatsApp |

---

## PALETA DE COLORES — FINAKTIVA ADAPTADA

| Variable | Color | Uso |
|---|---|---|
| Fondo principal | #0D1B2A | Fondo oscuro hero, login, secciones |
| Fondo alterno | #112236 | Secciones secundarias |
| Cards | #1A3350 | Tarjetas y paneles |
| Bordes | #1E3A5F | Bordes sutiles |
| Acento principal | #00E5A0 | Verde lima — botones, íconos, highlights |
| Acento hover | #00C98A | Hover del acento |
| Texto secundario | #8892A4 | Subtítulos y descripciones |
| Blanco | #FFFFFF | Títulos principales |

---

## LANDING PAGE — ESTADO ACTUAL

Archivo: frontend/components/marketing/landing-page.tsx

### Secciones implementadas
1. **Navbar** — sticky, logo EP verde, links de navegación, dos botones
2. **Hero** — fondo #0D1B2A, imagen notarial a la derecha, título gigante, "hoy" en verde lima, métricas
3. **De lo manual a EasyPro** — comparación antes/después en dos columnas
4. **Características** — 6 cards oscuras con íconos verdes
5. **Identidad institucional** — mock Notaría de Caldas con branding
6. **FAQs** — acordeón con useState, 5 preguntas, borde verde al abrir
7. **CTA final** — título gigante, botón verde
8. **Footer suscripción** — input email + checkbox tratamiento de datos
9. **Footer corporativo** — 4 columnas: logo, producto, empresa, dirección Medellín
10. **Footer copyright** — © 2026 EasyPro Notarial · Colombia

### Botones flotantes
- WhatsApp: https://wa.me/573107932844 — fondo #25D366
- Llamada: tel:+573107932844 — fondo #00E5A0

### Imagen hero
- Archivo: frontend/public/notario-hero.png
- Ilustración notarial colombiana con sello NOTARY PUBLIC COLOMBIA

---

## LOGIN — ESTADO ACTUAL

Archivo: frontend/components/marketing/login-panel.tsx

### Implementado
- Layout dos columnas: imagen izquierda enmarcada en card / formulario derecha
- Imagen: /notario-hero.png en card con bordes redondeados
- Badge "PLATAFORMA ACTIVA — Notaría de Caldas — Go-live 9 Abr 2026"
- Fondo formulario: #0D1B2A paleta Finaktiva
- Campos email y contraseña con estilo oscuro
- Checkbox tratamiento de datos obligatorio antes de ingresar
- Checkbox recordar sesión
- Botón "Ingresar" verde #00E5A0
- Encoding UTF-8 limpio

### Pendiente
- Login dinámico por notaría — imagen y colores desde BD por slug
- Endpoint público GET /api/v1/notaries/public/{slug}

---

## MOTOR DOCUMENTAL — ESTADO ACTUAL

### Lo que existe
- `render_docx_template()` — reemplazo de {{ETIQUETAS}} en Word via zipfile ✅
- `build_placeholder_replacements()` — hardcodeado para poderdante/apoderado ⚠️
- `generate_draft_for_case()` — orquestador del borrador ✅
- `TemplateField` — campos configurables por plantilla con placeholder_key ✅
- `TemplateRequiredRole` — roles de intervinientes por plantilla ✅
- `extract_placeholders_from_docx()` — extrae {{variables}} del Word ✅ (pendiente integrar)
- Flujo completo: borrador → revisión → aprobación → firma ✅

### Pendiente — Motor dinámico
- `build_placeholder_replacements()` dinámico — cualquier role_code ⬜
- Endpoint GET /document-flow/templates/{id}/placeholder-schema ⬜
- Endpoint GET /document-flow/templates/{id}/extract-placeholders ⬜
- Frontend del flujo de caso alineado con paleta Finaktiva ⬜

### Flujo de un acto notarial
```
1. Protocolista selecciona plantilla del acto
2. Sistema crea caso con número CAS-YYYY-NNNN
3. Protocolista ingresa intervinientes (uno a uno o masivo)
4. Protocolista ingresa datos del acto
5. Sistema genera borrador Word automáticamente
6. Revisor/Aprobador revisa y aprueba
7. Notario firma (titular o suplente)
8. Sistema asigna número de escritura oficial
9. Caso cerrado — PDF final disponible
```

### Motor dinámico — diseño
```
Notaría sube Word con {{NOMBRE_VENDEDOR}}, {{NOMBRE_COMPRADOR}}
↓
Admin configura plantilla:
  - Roles: vendedor, comprador
  - Campos del acto: valor_inmueble → {{VALOR_INMUEBLE}}
↓
Sistema genera variables dinámicamente por role_code:
  prefix = role_code.upper() → "VENDEDOR"
  {{NOMBRE_VENDEDOR}}, {{DOCUMENTO_VENDEDOR}}, etc.
↓
Word generado sin tocar código
```

---

## ENDPOINTS DISPONIBLES

| Método | Endpoint | Descripción |
|---|---|---|
| GET | /health | Health check |
| POST | /api/v1/auth/login | Login JWT |
| GET | /api/v1/auth/me | Usuario actual |
| GET | /api/v1/notaries | Listado notarías |
| GET | /api/v1/users | Listado usuarios |
| GET/POST | /api/v1/cases | Casos notariales |
| GET/POST | /api/v1/persons | Intervinientes |
| GET/POST | /api/v1/templates | Plantillas |
| POST | /api/v1/document-flow/cases/from-template | Crear caso |
| PUT | /api/v1/document-flow/cases/{id}/participants | Guardar intervinientes |
| PUT | /api/v1/document-flow/cases/{id}/act-data | Guardar datos del acto |
| POST | /api/v1/document-flow/cases/{id}/generate-draft | Generar borrador |
| POST | /api/v1/document-flow/cases/{id}/approve | Aprobar caso |
| POST | /api/v1/document-flow/cases/{id}/export | Exportar Word/PDF |

---

## ARQUITECTURA DE NAVEGACIÓN

| Ruta | Página | Estado |
|---|---|---|
| / | LandingPage | ✅ Completo |
| /login | LoginPanel | ✅ Completo |
| /dashboard | Dashboard | ✅ Operativo |
| /dashboard/casos | Casos | ✅ Operativo |
| /dashboard/casos/crear | Wizard creación | ✅ Operativo |
| /dashboard/casos/{id} | Detalle caso | ✅ Operativo |
| /dashboard/plantillas | Plantillas | ✅ Operativo |
| /dashboard/lotes | Lotes masivos | 🔧 Parcial |
| /dashboard/notarías | Notarías | ✅ Operativo |
| /dashboard/usuarios | Usuarios | ✅ Operativo |
| /dashboard/comercial | CRM | ✅ Operativo |

---

## PENDIENTES CRÍTICOS — GO-LIVE 9 ABRIL

### Bloquean salida
1. ⬜ Motor documental dinámico — build_placeholder_replacements() dinámico
2. ⬜ Migración BD SQLite → Supabase PostgreSQL
3. ⬜ Deploy Railway (backend) + Vercel (frontend)
4. ⬜ DNS subdominios en helexium.co
5. ⬜ Login dinámico por notaría con imagen y colores desde BD
6. ⬜ Validación operativa Notaría de Caldas

### Importantes post go-live
- Paleta Finaktiva en dashboard/sistema autenticado
- Operación masiva de lotes
- Integración IA (Gari)
- Integraciones externas (RNEC, firma digital)

---

## NOTARÍA PILOTO

### Notaría de Caldas
- Go-live: 9 de abril de 2026
- Migra desde: EasyPro 1 (Django)
- URL objetivo: caldas.easypro.co
- Estado: configuración pendiente en Supabase

---

## REGLAS DE DESARROLLO

- NUNCA usar tag form en React — usar div con onClick
- SIEMPRE UTF-8 sin BOM — tildes y ñ directamente en JSX y Python
- NUNCA caracteres corruptos en strings
- Puerto frontend: 5179
- Puerto backend: 8001
- BD local: SQLite en backend/easypro2.db
- Backup BD antes de cambios grandes

---

## DOCUMENTO EJECUTIVO

- Archivo: EasyPro2_Ejecutivo_31Mar2026.docx
- Secciones: resumen ejecutivo, qué hace, lo construido, arquitectura, hoja de ruta, modelo de negocio, diferenciadores, estado técnico, próximos pasos, requerimientos de aprovisionamiento
- Go-live: 9 abril con Notaría de Caldas
- Desde: 21 marzo 2026 — desarrollo ágil e iterativo