# Protocolo de arranque — EasyProNotarial-2
# Solo lectura en este paso. No modificar archivos ni ejecutar migraciones.

## Fase 1 — Leer contexto

Ejecuta estos comandos en orden y guarda los resultados en contexto:

1. Lee `SESSION.md` completo.
2. Ejecuta `git log --oneline -10` para ver los últimos commits.
3. Ejecuta `git status` para ver cambios sin commitear.
4. Ejecuta `git branch` para confirmar la rama activa.

## Fase 2 — Verificar estado del backend (si se va a trabajar en backend)

Solo si la sesión involucra cambios al backend:

```bash
cd easypro2/backend
# Verificar migraciones aplicadas vs pendientes
alembic current
alembic heads
```

Si `alembic current` ≠ `alembic heads`, hay migraciones pendientes. Reportarlo en el resumen.

## Fase 3 — Sintetizar y reportar

Produce el resumen de arranque con EXACTAMENTE esta estructura, en máximo 15 líneas:

---

**SESIÓN INICIADA — [fecha de hoy]**

**Rama activa:** [rama]
**Último commit:** [hash corto] — [mensaje]

**Estado del proyecto:**
[2-3 líneas con qué módulos están operativos y cuál es el foco actual]

**Cambios sin commitear:**
[lista breve o "Árbol limpio"]

**Pendientes críticos:**
1. [pendiente 1 con prioridad]
2. [pendiente 2]
3. [pendiente 3]

**Para levantar entorno local:**
```bash
# Backend
cd easypro2/backend && uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload

# Frontend (terminal separada)
cd easypro2/frontend && npm run dev
```

**Contexto cargado. Esperando instrucción.**

---

## Regla de cierre de esta fase

NO tocar ningún archivo ni ejecutar migraciones hasta que el usuario dé una instrucción explícita después de leer el resumen.
Si hay migraciones pendientes o conflictos detectados, advertirlo claramente en el resumen antes de cualquier otra cosa.
