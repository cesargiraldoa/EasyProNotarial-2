# SESSION.md — EasyPro Notarial 2
> Última actualización: 31 Mar 2026 — 20:00

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

### Si el puerto 5179 está ocupado
```powershell
$pid5179 = (netstat -ano | findstr :5179 | findstr LISTENING) -split '\s+' | Select-Object -Last 1
taskkill /PID $pid5179 /F
npm run dev
```

### Si hay error de caché de Next.js
```powershell
cd C:\EasyProNotarial-2\easypro2\frontend
Remove-Item -Recurse -Force .next
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

| Servicio | Plan | Costo/mes | Estado |
|---|---|---|---|
| Supabase Pro | Pro | USD $25 | Proyecto creado — São Paulo — pendiente migración |
| Railway | Starter | USD $10-20 | Pendiente crear cuenta |
| Vercel | Hobby | USD $0 | Pendiente crear cuenta |
| Dominio helexium.co | Subdominios | — | Pendiente configurar DNS |
| Claude API | Pro | USD $20-100 | Activo |
| OpenAI API | GPT-4o | USD $20-100 | Activo — key configurada en .env |
| Línea telefónica | 2FA | COP $30-50k | Pendiente |

### Subdominios objetivo
- caldas.easypro.co → Notaría de Caldas (go-live 9 Abr)

### Costos estimados totales
- Infraestructura: USD $35-45/mes
- Herramientas IA: USD $40-200/mes
- Total: USD $85-270/mes

---

## ESTADO DEL REPO

- Repo: C:\EasyProNotarial-2\easypro2
- Rama: master
- Último commit: 56f2107

---

## COMMITS DEL 31 MAR 2026

| Commit | Descripción |
|---|---|
| 8eabf12 | feat: estado inicial EasyPro2 — estructura base frontend + backend |
| 333dfc8 | feat: landing Finaktiva completa + login imagen notarial + footer + botones flotantes WhatsApp |
| 0d5a6ea | feat: Gari motor documental LLM — generación notarial dinámica con GPT-4o |
| 56f2107 | feat: Gari UI completa — botón generar, tab Documento Gari, descarga autenticada |

---

## PALETA DE COLORES — FINAKTIVA ADAPTADA

| Variable | Color | Uso |
|---|---|---|
| Fondo principal | #0D1B2A | Hero, login, secciones oscuras |
| Fondo alterno | #112236 | Secciones secundarias |
| Cards | #1A3350 | Tarjetas y paneles |
| Bordes | #1E3A5F | Bordes sutiles |
| Acento principal | #00E5A0 | Verde lima — botones, íconos |
| Acento hover | #00C98A | Hover del acento |
| Texto secundario | #8892A4 | Subtítulos y descripciones |
| WhatsApp | #25D366 | Botón flotante |

---

## LANDING PAGE ✅ COMPLETA

Archivo: `frontend/components/marketing/landing-page.tsx`

### Secciones
1. Navbar — sticky, logo EP verde, links, dos botones
2. Hero — fondo #0D1B2A, imagen notarial derecha, título gigante, "hoy" verde lima
3. De lo manual a EasyPro — comparación antes/después
4. Características — 6 cards oscuras con íconos verdes
5. Identidad institucional — mock Notaría de Caldas
6. FAQs — acordeón useState, 5 preguntas
7. CTA final — título gigante, botón verde
8. Footer suscripción — email + checkbox tratamiento de datos
9. Footer corporativo — logo, producto, empresa, Medellín Carrera 43B #1A Sur-70
10. Footer copyright — © 2026 EasyPro Notarial · Colombia
11. Botón flotante WhatsApp: https://wa.me/573107932844
12. Botón flotante Llamada: tel:+573107932844

### Imagen hero
- `/notario-hero.png` — ilustración notarial colombiana con sello NOTARY PUBLIC COLOMBIA

---

## LOGIN ✅ COMPLETO

Archivo: `frontend/components/marketing/login-panel.tsx`

### Implementado
- Layout dos columnas: imagen izquierda enmarcada en card / formulario derecha
- Imagen: /notario-hero.png enmarcada con bordes redondeados
- Badge "PLATAFORMA ACTIVA — Notaría de Caldas — Go-live 9 Abr 2026"
- Fondo formulario: #0D1B2A paleta Finaktiva
- Campos email y contraseña oscuros
- Checkbox tratamiento de datos obligatorio
- Checkbox recordar sesión
- Botón "Ingresar" verde #00E5A0
- Encoding UTF-8 limpio

### Pendiente
- Login dinámico por notaría — imagen y colores desde BD por slug

---

## MOTOR DOCUMENTAL GARI ✅ OPERATIVO

### Arquitectura
```
Protocolista crea caso → ingresa intervinientes → ingresa datos del acto
→ presiona "Generar con Gari"
→ Backend llama GPT-4o con: tipo de acto + datos + plantilla de referencia
→ Gari redacta documento notarial completo en español jurídico colombiano
→ Se guarda como borrador Word versionado (v1, v2, v3...)
→ Aprobador revisa en tab "Documento Gari"
→ Puede regenerar con correcciones
→ Aprueba → Notario firma → PDF final
```

### Archivos creados/modificados
- `backend/app/services/gari_document_service.py` — servicio completo
  - `get_openai_client()` — cliente OpenAI desde .env
  - `build_gari_prompt()` — prompt con todos los datos del caso
  - `generate_notarial_document()` — llama GPT-4o, retorna texto
  - `save_gari_document_as_docx()` — guarda Word con formato notarial
- `backend/app/modules/document_flow/router.py` — endpoint agregado
  - `POST /document-flow/cases/{id}/generate-with-gari`
- `backend/app/services/document_generation.py` — `extract_text_from_docx()`
- `backend/app/models/case_act_data.py` — campo `gari_draft_text`
- `backend/app/schemas/case.py` — `gari_draft_text` en respuesta
- `frontend/components/cases/case-detail-workspace.tsx` — UI completa
  - Tab "Documento Gari" con vista del texto
  - Botón "Generar con Gari" con spinner
  - Descarga autenticada de documentos con Bearer token
- `frontend/lib/auth.ts` — `getToken()` para descargas autenticadas
- `frontend/lib/document-flow.ts` — `generateWithGari()`

### Configuración
- `backend/.env` — OPENAI_API_KEY configurada
- `backend/requirements.txt` — openai>=1.0.0, python-docx>=0.8.11
- Modelo: gpt-4o, temperature: 0.2, max_tokens: 4000

### Prueba exitosa
- Caso CAS-2026-0003 (ID 22)
- 2 intervinientes: Gerónimo Giraldo Campo (poderdante) + Daniela Campo (apoderada)
- Gari generó Poder General completo con cláusulas, constancias legales y liquidación
- Word descargado y verificado — tildes y ñ correctas
- v1 y v2 generados y versionados

---

## ENDPOINTS DISPONIBLES

| Método | Endpoint | Descripción |
|---|---|---|
| GET | /health | Health check |
| POST | /api/v1/auth/login | Login JWT |
| GET | /api/v1/auth/me | Usuario actual |
| GET | /api/v1/notaries | Listado notarías |
| GET | /api/v1/users | Listado usuarios |
| GET | /api/v1/cases | Listado casos |
| GET/POST | /api/v1/persons | Intervinientes |
| GET/POST | /api/v1/templates | Plantillas |
| POST | /api/v1/document-flow/cases/from-template | Crear caso |
| GET | /api/v1/document-flow/cases/{id} | Detalle caso |
| PUT | /api/v1/document-flow/cases/{id}/participants | Guardar intervinientes |
| PUT | /api/v1/document-flow/cases/{id}/act-data | Guardar datos del acto |
| POST | /api/v1/document-flow/cases/{id}/generate-draft | Borrador por etiquetas |
| POST | /api/v1/document-flow/cases/{id}/generate-with-gari | **Borrador con Gari LLM** |
| POST | /api/v1/document-flow/cases/{id}/approve | Aprobar caso |
| POST | /api/v1/document-flow/cases/{id}/export | Exportar Word/PDF |
| GET | /api/v1/document-flow/cases/{id}/documents/{did}/versions/{vid}/download | Descargar |

---

## ARQUITECTURA DE NAVEGACIÓN

| Ruta | Página | Estado |
|---|---|---|
| / | LandingPage | ✅ Completo |
| /login | LoginPanel | ✅ Completo |
| /dashboard | Dashboard | ✅ Operativo |
| /dashboard/casos | Listado casos | ✅ Operativo |
| /dashboard/casos/crear | Wizard creación | ✅ Operativo |
| /dashboard/casos/{id} | Detalle caso + Gari | ✅ Operativo |
| /dashboard/plantillas | Plantillas | ✅ Operativo |
| /dashboard/lotes | Lotes masivos | 🔧 Parcial |
| /dashboard/notarías | Notarías | ✅ Operativo |
| /dashboard/usuarios | Usuarios | ✅ Operativo |
| /dashboard/comercial | CRM | ✅ Operativo |

---

## PENDIENTES CRÍTICOS — GO-LIVE 9 ABRIL

### Bloquean salida a producción
1. ⬜ Deploy Railway (backend FastAPI)
2. ⬜ Deploy Vercel (frontend Next.js)
3. ⬜ Migración BD SQLite → Supabase PostgreSQL
4. ⬜ DNS subdominios helexium.co → caldas.easypro.co
5. ⬜ Variables de entorno en producción (OPENAI_API_KEY, DATABASE_URL, etc.)
6. ⬜ Validación operativa con Notaría de Caldas

### Importantes antes del go-live
- Login dinámico por notaría (imagen y colores desde BD)
- Paleta Finaktiva en dashboard/sistema autenticado
- Flujo de aprobación completo en UI (revisor → aprobador → notario)

### Post go-live
- Operación masiva de lotes
- Más tipos de acto en Gari (compraventa, sucesión, declaraciones)
- Integraciones externas (RNEC, firma digital certificada)

---

## AGENDA PRÓXIMA

### Mañana 1 Abr 2026
- **10:00 AM** — Revisión OMA/Helexium-2 — mostrar avances academia
- **6:00 PM** — Reunión socios EasyPro — mostrar demo + documento ejecutivo

### Demo EasyPro para la reunión de las 6 PM
1. Abrir http://localhost:5179 — landing Finaktiva
2. Hacer login con superadmin@easypro.co / ChangeMe123!
3. Ir a Casos → CAS-2026-0003
4. Mostrar tab Documentos → botón "Generar con Gari"
5. Mostrar tab "Documento Gari" con el Poder General generado
6. Descargar el Word y mostrarlo

### Documento ejecutivo listo
- `EasyPro2_Ejecutivo_31Mar2026.docx` — para la reunión de las 6 PM

---

## NOTARÍA PILOTO

### Notaría de Caldas
- Go-live: 9 de abril de 2026
- Migra desde: EasyPro 1 (Django)
- URL objetivo: caldas.easypro.co
- Contacto: +57 310 793 2844
- Estado: pendiente configuración en Supabase

---

## REGLAS DE DESARROLLO

- NUNCA usar tag `<form>` en React — usar `div` con `onClick`
- SIEMPRE UTF-8 sin BOM — tildes y ñ directamente en JSX y Python
- NUNCA caracteres corruptos en strings JSX
- Puerto frontend: 5179
- Puerto backend: 8001
- BD local: SQLite en `backend/easypro2.db`
- Backup BD antes de cambios grandes
- Limpiar `.next` si hay errores de módulo webpack