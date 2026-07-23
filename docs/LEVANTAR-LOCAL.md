# Cómo levantar EasyPro Notarial en local (Windows / PowerShell)

Guía práctica para correr el proyecto completo (backend + frontend) en tu máquina.

---

## 0. Lo más importante: la carpeta correcta

El proyecto **NO** está en `C:\EasyProNotarial-2` (esa carpeta padre es basura vieja, ni siquiera es un repo git).
El repositorio real vive en:

```
C:\EasyProNotarial-2\easypro2
```

**Trabaja SIEMPRE desde `easypro2`.** Ahí `git status` funciona y están `backend`, `frontend`, `scripts`, `docker-compose.yml`, `SESSION.md`.

Para confirmar que estás en el lugar correcto:

```powershell
cd C:\EasyProNotarial-2\easypro2
git status          # debe mostrar la rama, NO "fatal: not a git repository"
```

---

## 1. Puertos (importante si tienes Helexium/Gari corriendo)

| Servicio            | Puerto | Nota                                          |
|---------------------|--------|-----------------------------------------------|
| Backend (FastAPI)   | `8001` | El `8000` queda reservado para Gari/Helexium  |
| Frontend (Next.js)  | `5179` |                                               |
| Postgres            | `5432` | vía Docker                                     |
| Redis               | `6379` | vía Docker                                     |

El frontend sabe a qué puerto pegarle por la variable `NEXT_PUBLIC_API_URL`
(archivo `frontend/.env.local`). Si no existe, cae por defecto a `8000` — por eso
hay que crear el `.env.local` (ver más abajo).

---

## 2. Preparación (solo la PRIMERA vez)

### Backend
```powershell
cd C:\EasyProNotarial-2\easypro2\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Si `.\.venv\Scripts\Activate.ps1` da error de *execution policy*:
```powershell
Set-ExecutionPolicy -Scope Process -Bypass
```

### Frontend
```powershell
cd C:\EasyProNotarial-2\easypro2\frontend
npm install
Copy-Item .env.example .env.local -Force   # deja NEXT_PUBLIC_API_URL apuntando a 8001
```

> `NEXT_PUBLIC_API_URL` se lee **solo al arrancar Next**. Si creas/editas `.env.local`
> con el frontend ya corriendo, reinícialo (Ctrl+C y volver a `npm run dev:next`).

---

## 3. Levantar (cada vez que trabajas)

### Infraestructura (Postgres + Redis)
```powershell
cd C:\EasyProNotarial-2\easypro2
docker compose up -d postgres redis
```

### Opción A — Launcher automático (recomendado)
Abre backend y frontend en dos ventanas y libera los puertos solo:
```powershell
cd C:\EasyProNotarial-2\easypro2
powershell -ExecutionPolicy Bypass -File .\scripts\START_LOCAL_EASYPRO.ps1
```
Backend por defecto en **8001**. Para otro puerto:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\START_LOCAL_EASYPRO.ps1 -BackendPort 8002
```

### Opción B — Manual, dos ventanas (deja ambas abiertas)

**Ventana 1 — Backend:**
```powershell
cd C:\EasyProNotarial-2\easypro2\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8001
```
Espera a ver: `Application startup complete` y `Uvicorn running on http://127.0.0.1:8001`.

**Ventana 2 — Frontend:**
```powershell
cd C:\EasyProNotarial-2\easypro2\frontend
npm run dev:next
```

> No uses `npm run dev` a secas si estás depurando; `dev:next` arranca Next directo
> en `127.0.0.1:5179`.

---

## 4. Abrir la app

- App: **http://127.0.0.1:5179**
- Login: `superadmin@easypro.co`
- Salud del backend: **http://127.0.0.1:8001/health** (debe responder `200 OK`)

Tras cambios de entorno, refresca con **Ctrl + F5**.

---

## 5. Verificar que todo conecta

Backend sano:
```powershell
Invoke-WebRequest http://127.0.0.1:8001/health
```
En la ventana del frontend deberías ver algo como:
`Backend health: OK http://127.0.0.1:8001/health`

---

## 6. Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| `fatal: not a git repository` | Estás en `C:\EasyProNotarial-2` (carpeta padre) | `cd C:\EasyProNotarial-2\easypro2` |
| `Could not open requirements file: requirements.txt` | Carpeta equivocada, o venv sin deps | Estar en `easypro2\backend` y correr `pip install -r requirements.txt` |
| `Could not import module "app.main"` | El `.venv` no tiene dependencias instaladas | `pip install -r requirements.txt` dentro del venv activado |
| Login: *"No fue posible conectarse con el servidor"* | Backend caído, o front apuntando a 8000 | Levantar backend en 8001 **y** tener `frontend/.env.local` con `NEXT_PUBLIC_API_URL=http://127.0.0.1:8001` (reiniciar Next) |
| `&&` no es separador válido | Es PowerShell (Windows), no bash | Un comando por línea |
| `Unable to stop PID 0 on port 5179` | Nada ocupaba ese puerto | Inofensivo, ignóralo |
| El backend se cae al cerrar la ventana | Cada servicio vive en su ventana | Deja backend y frontend en ventanas separadas mientras trabajas |

---

## 7. Apagar

- Cierra las ventanas de backend y frontend (o Ctrl+C en cada una).
- Infra Docker (opcional): `docker compose down`
