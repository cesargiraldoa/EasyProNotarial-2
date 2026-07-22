# Prompt Codex — WP-1: Corpus jurídico (esquema + siembra desde el HTML)

> Pegar en Codex. Contexto de fondo: `docs/ecosistema-notarial/plan-port-software.md` y `adr-escritura-asistida.md`. Al terminar, abrir **un PR** contra `claude/notaria16-escritura-asistida-fsro6n`.

---

## Rol y objetivo
Eres un ingeniero backend senior trabajando en el repo EasyProNotarial-2 (FastAPI + SQLAlchemy 2.0 + Alembic + Postgres). Vas a crear el **corpus jurídico** (fuente de verdad legal del producto) como: (a) archivos JSON versionados en Git, (b) tablas nuevas en Postgres, (c) un seed idempotente que carga (a)→(b). NO toques modelos ni tablas existentes.

## Fuentes de datos (leer y transcribir)
- `docs/ecosistema-notarial/prototipos/escritura-asistida.html` — objetos JS `NORMAS` (diccionario de normas y jurisprudencia con `norma/estado/art/texto/fuente`), `TARIFAS` (tarifas 2026), `BIBLIO` y `BIBLIO_CANC` (biblioteca de cláusulas por acto).
- `docs/ecosistema-notarial/normograma-compraventa.md` — normas de compraventa con su estado.
- `docs/ecosistema-notarial/corpus-juridico/verificacion-fuentes-2026-07-21.md` — **estado/artículo/URL/confianza verificados**, correcciones C1–C5 y jurisprudencia. **Esta fuente manda** cuando hay conflicto.
- `docs/ecosistema-notarial/corpus-notaria16/capa-notaria16-compraventa.md` y `capa-notaria16-cancelacion-hipoteca.md` — cláusulas verbatim por acto.

## Entregables

### 1. Modelos SQLAlchemy — `backend/app/models/legal_*.py`
Sigue el estilo existente (mira `backend/app/models/case.py`): `Mapped[...]` + `mapped_column`, `Base` y `TimestampMixin` desde `app.models.base`, y regístralos en `backend/app/models/__init__.py`. Usa `JSONB` (Postgres) para campos JSON y columnas `String` para los enums (con validación en el schema Pydantic, no `SQLEnum`, para no romper migraciones futuras).

- **`legal_norma`** (`legal_normas`): `id`; `tipo` (Ley/Decreto/Decreto-Ley/Resolución/Circular/Sentencia/Código); `numero` (str); `anio` (int); `articulo` (str, nullable — **vigencia artículo por artículo**); `materia` (str); `autoridad` (str); `estado` (vigente/modificada/derogada_parcial/derogada_total/inexequible/suspendida/compilada); `vigencia_formal` (str); `aplicabilidad_operativa` (str); `vigencia_desde` (Date, nullable); `vigencia_hasta` (Date, nullable); `url_oficial` (str, nullable); `confianza` (alta/media/baja); `fecha_verificacion` (Date, nullable); `texto` (Text, nullable); `notas` (Text, nullable); `slug` (str, unique — p.ej. `ley-258-1996-art-3`).
- **`legal_norma_relacion`** (`legal_norma_relaciones`): `id`; `norma_origen_id` (FK legal_normas); `norma_destino_id` (FK legal_normas); `tipo` (modifica/deroga_total/deroga_parcial/compila/desarrolla/reglamenta); `articulo_afectado` (str, nullable); `fecha_efecto` (Date, nullable); `notas` (Text, nullable).
- **`legal_clausula`** (`legal_clausulas`): `id`; `acto_code` (str — compraventa/hipoteca/cancelacion_hipoteca); `orden` (int); `titulo` (str); `texto` (Text, con slots `{slot}`); `capa` (por_ley/estilo); `norma_id` (FK, nullable); `notaria_id` (int, nullable — capa por notaría); `condicional` (bool, default false); `vigencia_desde`/`vigencia_hasta` (Date, nullable); `notas` (Text, nullable).
- **`legal_regla`** (`legal_reglas`): `id`; `acto_code` (str); `codigo` (str, unique); `condicion_json` (JSONB); `efecto` (str); `severidad` (BLOCK/REVIEW/WARN); `mensaje` (str); `norma_id` (FK, nullable); `vigencia_desde`/`vigencia_hasta` (Date, nullable).
- **`legal_tarifa`** (`legal_tarifas`): `id`; `anio` (int); `concepto` (str); `valor` (Numeric, nullable); `formula` (str, nullable); `unidad` (str, nullable); `norma_id` (FK, nullable); `vigencia_desde`/`vigencia_hasta` (Date, nullable).
- **`legal_jurisprudencia`** (`legal_jurisprudencias`): `id`; `tipo` (C/SU/T/CSJ/CE); `numero` (str); `anio` (int); `providencia` (str); `regla_operacional` (Text); `norma_relacionada_id` (FK legal_normas, nullable); `fecha` (Date, nullable); `url_oficial` (str, nullable); `confianza` (alta/media/baja).

### 2. Migración Alembic — `backend/alembic/versions/`
Una migración que crea las 6 tablas con sus índices y FKs. `upgrade` y `downgrade` completos. No modificar tablas existentes.

### 3. Corpus en JSON — `corpus-juridico/*.json`
Transcribe las fuentes a JSON curado (una lista de objetos por archivo, campos = columnas del modelo): `normas.json`, `norma_relaciones.json`, `clausulas.json`, `reglas.json`, `tarifas.json`, `jurisprudencia.json`. Este JSON es la **fuente de verdad** (revisable por PR); el seed lo carga.

**Aplica obligatoriamente estas correcciones verificadas (C1–C5):**
- **C1:** la regla/nota "registro dentro de 2 meses + intereses" se ancla a **`art. 231 Ley 223/1995`** (NO Ley 1579/2012). En Ley 1579, el art. 28 fija 90 días hábiles para hipoteca/patrimonio.
- **C2:** crea una `legal_norma_relacion` **`Dcto 2148/1983 art.12` —compila→ `Dcto 1069/2015 art. 2.2.6.1.2.1.5`**. La cláusula/nota de "firma fuera de sede" cita el artículo del 1069.
- **C3:** regla de retención: vendedor **persona natural** → 1% recaudado por el notario (art. 398 E.T.); vendedor **persona jurídica** → el notario NO retiene, retiene el comprador (art. 401 E.T.).
- **C4:** exención casa de habitación **5.000 UVT** + condición cuenta AFC (art. 311-1 E.T., Ley 2277/2022).
- **C5:** `Dcto 0732/2026` **modifica el DUR 1069/2015** (no "deroga el 1227/2015").

Incluye además la jurisprudencia de `verificacion-fuentes` (C-159/2021, C-193/2016, SU-214/2016, C-112/2000, C-039/2025) y las tarifas 2026 (Res. SNR 2026-000964-6, 3‰, IVA 19%, VIS −50%, UVT $52.374). Marca `confianza` y `url_oficial` según esa verificación; lo no confirmado, `confianza=baja` y una nota.

### 4. Seed idempotente — `backend/app/seeds/seed_corpus.py`
Lee los JSON de `corpus-juridico/` y hace upsert por `slug`/`codigo` (idempotente: correrlo dos veces no duplica). Función `seed_corpus(session)` + entrypoint CLI.

### 5. Consulta de vigencia — helper + prueba
Una función `normas_vigentes(session, acto_code, fecha)` (y equivalentes para cláusulas/reglas/tarifas) que devuelve solo lo aplicable a esa fecha (`vigencia_desde <= fecha <= vigencia_hasta or null`) y `aplicabilidad_operativa='vigente'`.

## Criterios de aceptación
1. `alembic upgrade head` y `alembic downgrade -1` funcionan sin error.
2. `seed_corpus` carga los JSON; correrlo dos veces no duplica filas.
3. `normas_vigentes(s, 'compraventa', date(2026,8,14))` devuelve las normas núcleo (258/1996, 1579/2012, 223/1995, 90 E.T., etc.) y NO devuelve las inexequibles/derogadas para esa fecha.
4. Las 5 correcciones C1–C5 son verificables por consulta (test explícito por cada una).
5. Existe la relación `Dcto 2148/1983 art.12 → compila → Dcto 1069/2015 art. 2.2.6.1.2.1.5`.

## Pruebas — `backend/app/tests/test_corpus.py`
- Migración + seed en BD de prueba.
- Idempotencia del seed.
- `normas_vigentes` por fecha (incluye un caso con norma inexequible que NO debe aparecer).
- Un test por cada corrección C1–C5.

## Restricciones
- SQLAlchemy 2.0 estilo `Mapped`; Alembic; Postgres/JSONB. Seguir convenciones del repo.
- **No** modificar modelos/tablas existentes ni el HTML (spec congelada).
- Un solo PR, con descripción que liste qué tablas/JSON crea y cómo correr el seed. Incluir las pruebas verdes en la descripción.
