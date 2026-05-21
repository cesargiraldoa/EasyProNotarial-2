# Protocolo de cierre — EasyProNotarial-2
# Actualiza SESSION.md, commitea y pushea. Confirma que todo quedó guardado.

## Fase 1 — Recopilar lo que se hizo

Si la conversación no deja claro qué se trabajó en esta sesión, pregunta:

> "¿Qué hiciste hoy? Dame un resumen de los cambios realizados para actualizar SESSION.md."

Espera la respuesta antes de continuar.

Si la conversación sí contiene el historial completo de la sesión, infiere el resumen directamente sin preguntar.

## Fase 2 — Revisar cambios reales

Ejecuta estos comandos y guarda los resultados:

```bash
git status
git diff --stat HEAD
git log --oneline -5
```

Con eso, identifica:
- Archivos modificados (nuevos, cambiados, eliminados)
- Commits nuevos desde el inicio de la sesión
- Cambios sin stagear que el usuario olvidó commitear

## Fase 3 — Actualizar SESSION.md

Abre `SESSION.md` y agrega una nueva sección al **inicio** del archivo (después del encabezado principal), con esta estructura exacta:

```markdown
---
## Sesión [YYYY-MM-DD]

**Objetivo de la sesión:** [1 línea con el foco principal]

**Realizado:**
- [item 1: módulo o archivo + qué se hizo]
- [item 2]
- [item 3...]

**Archivos creados/modificados:**
- `ruta/archivo.ext` — [descripción breve]
- `ruta/archivo2.ext` — [descripción breve]

**Pendientes para la próxima sesión:**
1. [pendiente concreto con contexto suficiente para retomarlo]
2. [pendiente 2]
3. [pendiente 3]

**Estado al cierre:**
- Backend: [operativo / con errores / pendiente arrancar]
- Frontend: [operativo / con errores / pendiente arrancar]
- BD producción: [en sync / migraciones pendientes]
- Git: [árbol limpio / cambios pendientes]

---
```

No borres ni muevas el contenido anterior de SESSION.md — solo agrega esta sección al inicio.

## Fase 4 — Stagear y commitear

Stagea SESSION.md y cualquier archivo modificado que no haya sido commiteado:

```bash
git add SESSION.md
# Si hay otros archivos sin commitear que forman parte del trabajo de hoy:
git add [archivos relevantes]
git status   # verificar que solo están los archivos correctos
```

**REGLA:** No stagear `.env`, `*.log`, `tsconfig.tsbuildinfo`, `*.db`, `.next/`, `__pycache__/`, ni backups. Si alguno aparece, excluirlo explícitamente con `git reset HEAD <archivo>`.

Crea el commit con este mensaje exacto (sustituyendo la fecha):

```bash
git commit -m "chore: actualizar SESSION.md post-sesión YYYY-MM-DD"
```

## Fase 5 — Push

```bash
git push origin main
```

Si el push es rechazado porque el remoto tiene commits nuevos:
1. Ejecuta `git pull --rebase origin main`
2. Si hay conflicto en SESSION.md: toma la versión local (`git checkout --theirs SESSION.md` durante rebase, ya que en rebase "theirs" es el parche que se aplica, es decir, nuestra versión)
3. `git add SESSION.md && git rebase --continue`
4. `git push origin main`

## Fase 6 — Confirmación

Cuando el push sea exitoso, reporta:

---

**SESIÓN CERRADA — [fecha]**

**Commit:** `[hash]` — chore: actualizar SESSION.md post-sesión [fecha]
**Push:** ✅ main actualizado en GitHub
**SESSION.md:** ✅ actualizado con resumen de la sesión

**Resumen de lo que quedó guardado:**
- [archivo 1]
- [archivo 2]
- [...]

**Próxima sesión arranca con:** `/iniciar-sesion`

---
