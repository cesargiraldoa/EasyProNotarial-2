markdown# SESSION.md — EasyPro Notarial 2
> Última actualización: 15 de abril de 2026 — 20:00

---

## OBJETIVO DEL PROYECTO
Software notarial SaaS multinotaría para digitalizar la operación documental de notarías colombianas.

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

### URLs locales
- Frontend: http://127.0.0.1:5179
- Backend: http://127.0.0.1:8001
- Health: http://127.0.0.1:8001/health

### Credenciales semilla
- superadmin@easypro.co / ChangeMe123!
- admin@notaria75.co / ChangeMe123!
- notario@notaria75.co / ChangeMe123!

---

## STACK
- Frontend: Next.js 15 + React 19 + TypeScript + Tailwind
- Backend: FastAPI + Python + SQLAlchemy + Pydantic + Uvicorn
- BD: Supabase PostgreSQL (migrado desde SQLite el 15 abr 2026)
- Puerto frontend: 5179
- Puerto backend: 8001

---

## INFRAESTRUCTURA

| Servicio | Estado |
|---|---|
| Supabase Pro — easypro-notarial-2 | ✅ Activo — São Paulo |
| GitHub — cesargiraldoa/EasyProNotarial-2 | ✅ Publicado — rama main |
| Railway | ⬜ Pendiente |
| Vercel | ⬜ Pendiente |
| DNS caldas.easypro.co | ⬜ Pendiente |

---

## ESTADO DEL REPO
- Repo: https://github.com/cesargiraldoa/EasyProNotarial-2
- Rama: main
- Último commit: 2e842b2

---

## COMMITS IMPORTANTES

| Commit | Descripción |
|---|---|
| 8eabf12 | feat: estado inicial EasyPro2 — estructura base frontend + backend |
| 333dfc8 | feat: landing Finaktiva completa + login imagen notarial |
| 0d5a6ea | feat: Gari motor documental LLM — GPT-4o |
| 56f2107 | feat: Gari UI completa — previsualizador, descarga Word |
| 7f27441 | feat: casos de éxito landing + branding + SESSION.md |
| 2e842b2 | feat: migración PostgreSQL Supabase + CORS flexible + fix datetime |

---

## BASE DE DATOS SUPABASE

- Proyecto: easypro-notarial-2
- Región: South America (São Paulo)
- 21 tablas migradas desde SQLite
- Registros migrados: 119 notarías, 9 usuarios, 23 casos, 40 versiones docs

### Datos de conexión (en .env — NO subir a GitHub)
DATABASE_URL=postgresql://postgres:JuanV1959%2F%2F%2A@db.egwdrdgtgmogcahhdtdy.supabase.co:5432/postgres

---

## LO REALIZADO — 15 ABR 2026

### GitHub
- ✅ Repo creado y publicado — cesargiraldoa/EasyProNotarial-2
- ✅ .gitignore limpio — excluye .db, storage/, .env, repomix

### PostgreSQL / Supabase
- ✅ Proyecto Supabase creado — easypro-notarial-2 São Paulo
- ✅ Migración completa SQLite → PostgreSQL con script migrate_to_postgres.py
- ✅ Foreign keys deshabilitados durante migración (session_replication_role = replica)
- ✅ Booleanos convertidos correctamente (0/1 → True/False)
- ✅ Seed idempotente — no falla al reiniciar si ya hay datos

### CORS
- ✅ FlexibleCORSMiddleware implementado (buena práctica de Helexium-2)
- ✅ Acepta localhost:5179, 127.0.0.1:5179, *.vercel.app, *.easypro.co

### Bug fixes
- ✅ Dashboard 500 — datetime timezone mismatch resuelto
  - Causa: datetime.utcnow() (naive) vs PostgreSQL timestamps (aware)
  - Fix: datetime.now(timezone.utc) en dashboard/router.py línea ~89

---

## PENDIENTES CRÍTICOS — GO-LIVE NOTARÍA CALDAS

### Bloquean producción
1. ⬜ Deploy Railway — backend FastAPI
2. ⬜ Deploy Vercel — frontend Next.js
3. ⬜ DNS caldas.easypro.co
4. ⬜ Variables de entorno en producción
5. ⬜ Validación operativa con Notaría de Caldas
6. ⬜ Secret key segura en producción

### Buenas prácticas pendientes de Helexium-2
- ⬜ Branding dinámico por notaría — resolveBranding() lee slug desde BD
- ⬜ Login dinámico por notaría — imagen y colores desde BD por slug
- ⬜ Multitenancy robusto — contexto por notaría en cada request

### Post go-live
- ⬜ Más tipos de acto en Gari (compraventa, sucesión, declaraciones)
- ⬜ Integraciones RNEC, firma digital
- ⬜ Operación masiva de lotes

---

## NOTARÍA PILOTO
- Notaría Única del Círculo de Caldas
- URL objetivo: caldas.easypro.co
- Contacto: +57 310 793 2844

---

## REGLAS DE DESARROLLO
- NUNCA usar tag `<form>` en React — usar `div` con `onClick`
- SIEMPRE UTF-8 sin BOM
- NUNCA subir .env ni .db a GitHub
- Separador párrafos Gari: `[[--]]`
- Puerto frontend: 5179 | backend: 8001
- Backup BD antes de cambios grandes
- Limpiar `.next` si hay errores webpack