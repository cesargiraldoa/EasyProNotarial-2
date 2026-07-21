# Prompt Codex — WP-2: Motor-escritura (TypeScript) + golden tests

> Pegar en Codex. Contexto: `docs/ecosistema-notarial/plan-port-software.md` y `adr-escritura-asistida.md`. Al terminar, **un PR** contra `claude/notaria16-escritura-asistida-fsro6n`.

---

## ⚠ Antes de empezar (evita el error del checkout viejo)
1. `git fetch origin` y **basa el trabajo en `claude/notaria16-escritura-asistida-fsro6n`** (ya trae WP-1 mergeado y los fixtures). El frontend está en **`frontend/`** en la raíz (NO `easypro2/`).
2. La **spec congelada** es `docs/ecosistema-notarial/prototipos/escritura-asistida.html`. NO la modifiques.

## Rol y objetivo
Eres ingeniero frontend senior (Next.js 15 / React 19 / TypeScript). Porta el **motor determinista** del HTML congelado a un módulo TypeScript en `frontend/lib/motor-escritura/`, **1:1** en comportamiento, con **golden tests** que reproducen los fixtures de referencia ya commiteados.

## Qué portar (funciones puras del HTML, dentro del IIFE principal)
- **Números/fecha:** `UNI/DEC/CEN`, `dos`, `tres`, `enLetras`, `pts`, `parseMoney`, `fmtMoneyStr`, `money`, `diaTexto`, `fechaText`, `fechaCorta`.
- **Helpers de string HTML:** `esc`, `attr`, `I`, `IF`, `R`, `D` (producen los `<span>` de campo/cita — pórtalos verbatim; el golden test depende de ellos).
- **Género/estado:** `GENEROS`, `genEnding`, `genArt`, `labelEstado`.
- **Partes:** `pers`, `persList`, `buyersFavor`, `casadoOUnion`, `anyNatural`, `anyJuridica`, `sumaCuotas`.
- **Render:** `renderEscritura`, `otorgamiento`, `renderCancelacion` (y sus helpers internos `firmante`/`ficha`/`fichaAux`).
- **Cumplimiento:** `evaluar`, `evaluarCanc` (devuelven la lista de ítems `{t,h,p,n}`); expón también el conteo por tipo (Cumple/Advertencia/Bloqueante).
- **Liquidación:** `liquidar`, `liquidarCanc`, `renderLiquidacion`, `renderLiquidacionCanc`, y la constante `TARIFAS`.
- **Estado del caso:** define tipos TypeScript a partir de `G()` (compraventa/hipoteca) y `Gc()` (cancelación), y **extrae los datos de muestra por defecto** del HTML como fixtures de entrada.

## API pública del módulo (`frontend/lib/motor-escritura/index.ts`)
```ts
type ActoCode = 'compraventa' | 'hipoteca' | 'cancelacion';
interface Resultado {
  html: string;                 // la escritura (string HTML, como en el HTML)
  liquidacionHtml: string;
  cumplimiento: { items: {tipo:'ok'|'obl'|'warn'|'crit'; titulo:string; detalle:string; norma:string}[];
                  tiles: {cumple:number; advertencia:number; bloqueante:number} };
  estado: { ok: boolean; texto: string };
}
export function generar(acto: ActoCode, state: CaseState): Resultado;
export const defaults: Record<ActoCode, CaseState>;   // datos de muestra portados del HTML
```
(Nombres internos a tu criterio; respeta la forma.)

## Reglas de fidelidad (no re-arquitecturar)
- **Porta la lógica de ensamblado tal cual** (las ramas condicionales de PH, VIS, crédito, género, etc.). NO reconstruyas el render leyendo filas del corpus.
- **`TARIFAS` y las citas de norma van como constantes portadas del HTML** (ya coinciden con el corpus WP-1 y las correcciones C1–C5). El cableado al corpus/BD se hará en un WP posterior; aquí prima la equivalencia con el HTML.
- El motor es **puro TS sin DOM ni navegador** en runtime; las funciones devuelven strings HTML.

## Golden tests — `frontend/lib/motor-escritura/__tests__/golden.test.ts`
Fixtures de referencia en `frontend/lib/motor-escritura/__fixtures__/{compraventa,hipoteca,cancelacion}.json` (ver su `README.md`). Para cada acto:
1. `const r = generar(acto, defaults[acto])`.
2. Aplica **exactamente** la función `normalize` documentada en el README de fixtures a `r.html` y `r.liquidacionHtml`.
3. Asserts:
   - `normalize(r.html) === fixture.doc_text`
   - `normalize(r.liquidacionHtml) === fixture.liquidacion_text`
   - `r.cumplimiento.items.map(i=>i.titulo) === fixture.cumplimiento_items` (mismo orden)
   - los conteos de `tiles` coinciden con `fixture.cumplimiento_tiles`
   - `r.estado.texto` coincide con `fixture.estado` (normalizando espacios)

Si algún assert falla, **corrige el port hasta que coincida byte a byte** (no cambies el fixture ni el HTML).

## Tests unitarios — `frontend/lib/motor-escritura/__tests__/unit.test.ts`
- `enLetras`: 0→CERO, 1→UNO, 21→VEINTIUNO, 1_000_000→UN MILLÓN, 69_714_000→"SESENTA Y NUEVE MILLONES SETECIENTOS CATORCE MIL".
- `money(69714000)` incluye "…PESOS MONEDA LEGAL COLOMBIANA ($69.714.000)".
- `genEnding`: M→o, F→a, NB/T→e.
- `fechaText('2026-03-06')` → "seis (6) días del mes de marzo del año dos mil veintiséis (2026)".
- `diaTexto(21)` → "veintiún"; `diaTexto(1)` → "un".

## Runner
Usa **vitest** (agrégalo como devDependency si no existe) o el runner del repo si ya hay uno. Configura `npm test` para correr estos tests. No agregues dependencias pesadas.

## Criterios de aceptación
1. Los 3 golden tests pasan (equivalencia exacta con los fixtures).
2. Los tests unitarios pasan.
3. El módulo compila con el TS del repo (sin `any` gratuitos; tipos para `CaseState`).
4. No se modificó el HTML congelado ni el corpus.

## Restricciones
- Un solo PR con descripción: qué funciones portó, cómo correr los tests, y el resultado (verde).
- Base correcta (`claude/notaria16-escritura-asistida-fsro6n`), rutas en `frontend/` (sin `easypro2/`).
