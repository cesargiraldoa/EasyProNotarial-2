# Prompt Codex — Bloque D (Lote 2): Compraventa de todo tipo — extranjero/divisas, rural/UAF, capacidad

> Pegar en Codex. Contexto: `docs/ecosistema-notarial/plan-port-software.md`, `mapa-situaciones.md`, `normograma-compraventa.md`. **Un PR** contra `claude/notaria16-escritura-asistida-fsro6n`.

---

## ⚠ Antes de empezar
1. `git fetch origin` y **basa el trabajo en `claude/notaria16-escritura-asistida-fsro6n`** (WP-1..WP-5 + Bloques A/B/C). Backend `backend/`, frontend `frontend/`.
2. **Construcción NUEVA** (no está en el HTML congelado): tests propios; **golden de los 3 actos base verdes**.
3. Fidelidad: `mapa-situaciones.md` (dimensiones 2, 4, 11, 16) y `normograma` (§ "normas nuevas": Ley 160/1994, régimen cambiario, Ley 1996/2019).

## Objetivo
Ampliar la compraventa con 3 situaciones especiales, como ramas activables (motor + formulario + corpus):

### 1. Extranjero / no residente / divisas (dim. 4 y 16)
- Rama: parte **extranjera no residente** y/o **pago en divisas** (inversión extranjera).
- Documento: cláusula de **declaración de cambio** (Banrep — régimen cambiario, Circular DCIN), apostilla del poder si viene del exterior, identificación por pasaporte/PPT.
- Cumplimiento (WARN/obl): registro de inversión extranjera; canalización por el mercado cambiario.
- Corpus: añadir norma(s) del **régimen cambiario** (marca `confianza=baja` si no verificada) + regla.

### 2. Rural / UAF / baldíos (dim. 11)
- Rama: predio **rural**; si es **baldío adjudicado (ANT)** o supera la **UAF** → advertencia/bloqueo (Ley 160/1994 art. 72, ya en el corpus): restricciones de enajenación/acumulación, derecho de preferencia.
- Documento: identificación del predio rural (sin PH), cláusula de restricciones si aplica.
- Cumplimiento: BLOCK si supera UAF sin autorización; WARN si baldío con restricción temporal.

### 3. Capacidad / apoyos (dim. 2)
- Rama: otorgante **menor de edad** (venta de bien de menor → autorización) o **persona con discapacidad** bajo el régimen de **apoyos (Ley 1996/2019 + Dcto 1429/2020)**.
- Documento: comparecencia con **persona de apoyo** / representante; **NO** usar lenguaje de "incapaz" (INM-026); constancia de la autorización aplicable.
- Cumplimiento: obl — autorización judicial/notarial vigente; apoyos acreditados.
- Corpus: Ley 1996/2019 art. 6/15-16 y Dcto 1429/2020 ya deberían existir; añade la regla de "venta de bien de representado".

## Corpus (añadir, sin borrar)
- Nuevas `legal_regla` + `legal_clausula` para las 3 ramas, con `norma_slug` y vigencia. Normas que falten (régimen cambiario) se añaden a `normas.json` (con `confianza` honesta). Actualiza el seed.

## Motor + UI + tests
- Extiende `CaseState`, render, `evaluar`, formulario para las 3 ramas. **Retrocompatible** (sin activar ramas, output idéntico → golden verdes).
- **Tests nuevos** por rama: extranjero→cláusula de cambio; rural sobre UAF→BLOCK; menor→comparecencia con autorización.

## Criterios de aceptación
1. Las 3 ramas se activan desde el formulario y el documento/cumplimiento las reflejan con su cita.
2. UAF excedida → BLOCK; menor sin autorización → advertencia/obl; divisas → cláusula de declaración de cambio.
3. **Golden de los 3 actos base: verdes.** Reglas server-side (Bloque A) operando.
4. Backend + frontend con tests nuevos verdes; `tsc`/build OK.

## Restricciones
- No tocar el HTML congelado. Corpus se amplía. Base correcta, sin `easypro2/`.
- Un PR; descripción con ramas, normas nuevas (y su confianza) y resultados de tests.

---

> Nota: tras C y D, la **cobertura de "compraventa de todo tipo"** queda en las dimensiones de alta frecuencia. Las variantes raras restantes (multipropiedad, fiducia como parte, etc.) se atienden luego como flujo asistido + advertencia, según la "estrategia de cobertura" del `mapa-situaciones.md`.
