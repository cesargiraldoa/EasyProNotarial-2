# Arquitectura Base EasyPro 2

## Principios
- Proyecto nuevo, sin heredar arquitectura de EasyPro 1.
- Multinotar?a como capacidad nativa.
- Separaci?n clara entre experiencia p?blica, experiencia autenticada y API.
- Branding institucional como configuraci?n de dominio, no como detalle visual aislado.
- Preparaci?n expl?cita para operaci?n masiva de casos y documentos.

## Frontend
- Next.js App Router con TypeScript y Tailwind.
- Route groups separados para marketing y app autenticada.
- Middleware para rutas protegidas por cookie de sesi?n.
- Theming por notar?a con CSS variables listas para hidratarse desde backend.
- Shell preparado para m?dulos: dashboard, cat?logo, casos, lotes, notar?as, configuraci?n.

## Backend
- FastAPI modular con routers por dominio.
- SQLAlchemy 2 sobre PostgreSQL.
- Modelos iniciales: `Notary`, `User`, `Role`, `RoleAssignment`.
- JWT para autenticaci?n base.
- Seed inicial para roles y usuarios de prueba.

## Modelo multinotar?a
- `Notary` concentra branding, datos institucionales y activaci?n.
- `User` define usuario base y notar?a principal.
- `RoleAssignment` permite asignar roles globales o por notar?a.
- `Role.scope` diferencia alcance global y alcance por notar?a.

## Evoluci?n prevista
- Casos, actos, intervinientes y estados.
- Plantillas notariales versionadas.
- Motor de lotes para operaci?n masiva.
- Auditor?a, adjuntos, eventos y observabilidad.
- Integraci?n de Gari IA como m?dulo transversal.
