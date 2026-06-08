# Arranque local de EasyPro

- `8001` = EasyPro backend
- `5179` = EasyPro frontend
- `8000` = Gari Billing

## Flujo recomendado

- `npm run dev` ya usa el arranque seguro y valida CSS al levantar.
- `scripts/dev/start-frontend-local.ps1` sigue siendo el arranque limpio manual.
- `npm run dev:next` queda solo para depuracion tecnica puntual.
- `scripts/dev/check-frontend-css.ps1` valida una instancia ya levantada en `5179`.
- `scripts/dev/start-backend-local.ps1` levanta el backend.
- `scripts/dev/start-easypro-local.ps1` abre backend y frontend en ventanas separadas en Windows.

## Si el frontend sale sin CSS

- No sigas probando funcionalidad.
- Ejecuta `scripts/dev/check-frontend-css.ps1`.
- Si falla, revisa el error exacto que reporta el script.
- El arranque seguro ya verifica:
  - `frontend/app/layout.tsx` importa `./globals.css`
  - `frontend/app/globals.css` contiene las directivas Tailwind
  - el HTML de `http://127.0.0.1:5179/dashboard/minutas/nueva` referencia `/_next/static/css/`
  - el asset CSS responde `200`

## URL utiles

- Frontend: `http://127.0.0.1:5179/dashboard/minutas/nueva`
- Backend health: `http://127.0.0.1:8001/health`
