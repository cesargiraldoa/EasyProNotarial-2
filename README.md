# EasyPro 2

Base de producto para un software notarial multinotar?a y multiusuario, construido como proyecto nuevo con frontend en Next.js y backend en FastAPI.

## Estructura
- `frontend/`: experiencia p?blica, login y shell autenticado.
- `backend/`: API, modelos base, auth, notar?as, usuarios y roles.
- `docs/`: arquitectura, backlog y dise?o previsto para operaci?n masiva.
- `scripts/`: ayudas de arranque local.

## Frontend
- Landing p?blica premium.
- Login visual de alto impacto.
- Shell autenticado alineado con los mockups.
- Sistema base de branding por notar?a con variables CSS.
- Separaci?n entre rutas p?blicas y privadas mediante middleware.
- Puerto de desarrollo fijo: `5179`.

## Backend
- FastAPI modular.
- Configuraci?n local lista para arrancar hoy con SQLite.
- Estructura preparada para PostgreSQL con SQLAlchemy 2.
- Modelos base para notar?as, usuarios, roles y asignaciones.
- JWT para autenticaci?n inicial.
- Seeds para roles y usuarios de arranque.
- `GET /health` para health check.
- Puerto recomendado para demo local: `8001` sobre `127.0.0.1`.

## Variables de entorno
1. Copie `backend/.env.example` a `backend/.env` si necesita regenerarlo.
2. Copie `frontend/.env.example` a `frontend/.env.local` si necesita regenerarlo.

## C?mo correr
### Backend
```bash
cd easypro2/backend
.venv\Scripts\python -m uvicorn app.main:app --app-dir . --host 127.0.0.1 --port 8001
```

### Frontend
```bash
cd easypro2/frontend
npm run dev
```

## URLs locales
- Frontend: `http://localhost:5179`
- Backend: `http://127.0.0.1:8001`
- Health: `http://127.0.0.1:8001/health`

## Credenciales semilla
- `superadmin@easypro.co` / `ChangeMe123!`
- `admin@notaria75.co` / `ChangeMe123!`
- `notario@notaria75.co` / `ChangeMe123!`

## Endpoints iniciales
- `GET /health`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/notaries`
- `GET /api/v1/users`

## Supuesto local actual
Para dejar desarrollo local funcionando hoy sin depender de un PostgreSQL levantado en la m?quina, el entorno por defecto usa SQLite en `backend/easypro2.db`. La capa de datos sigue preparada para volver a PostgreSQL cuando el servicio est? disponible.

