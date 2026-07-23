"use client";

import { Plus, Trash2 } from "lucide-react";
import { useEffect, useState, type ReactNode } from "react";
import {
  getLegalEntityRepresentatives,
  searchLegalEntities,
  type LegalEntityRecord,
  type LegalEntityRepresentativeRecord,
} from "@/lib/legal-entities";
import {
  casadoOUnion,
  fechaText,
  parseMoney,
  pts,
  sumaCuotas,
  type ActoCode,
  type ApoyoTipo,
  type AuxParty,
  type CancelacionState,
  type CaseState,
  type CompraventaCapacidad,
  type CompraventaDivisas,
  type CompraventaInmueble,
  type CompraventaRural,
  type CompraventaState,
  type EncadenamientosCompraventa,
  type EstadoCivil,
  type FolioEstado,
  type GeneroCode,
  type Party,
  type TipoDoc,
  type TipoPersona,
} from "@/lib/motor-escritura";

type Props = {
  acto: ActoCode;
  state: CaseState;
  onChange: (state: CaseState) => void;
};

type FieldProps = {
  id: string;
  label: string;
  hint?: string;
  children: ReactNode;
};

const inputClass = "w-full rounded-lg border border-line-strong bg-white px-3 py-2 text-sm text-primary shadow-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20 disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-secondary";
const labelClass = "mb-1 block text-xs font-semibold uppercase tracking-[0.04em] text-secondary";
const fieldsetClass = "border-t border-line py-4 first:border-t-0";
const row2Class = "grid gap-3 sm:grid-cols-2";
const checkClass = "flex items-start gap-2 text-sm text-primary";

const generoOptions: Array<[GeneroCode, string]> = [
  ["M", "Masculino"],
  ["F", "Femenino"],
  ["NB", "No binario"],
  ["T", "Transgenero"],
];

const estadoOptions: Array<[EstadoCivil, string]> = [
  ["soltero", "Soltero(a)"],
  ["casado_sc", "Casado(a) con sociedad conyugal"],
  ["union", "Union marital"],
  ["divorciado", "Divorciado(a)"],
  ["viudo", "Viudo(a)"],
];

const tipoDocOptions: Array<[TipoDoc, string]> = [
  ["CC", "Cedula de ciudadania"],
  ["CE", "Cedula de extranjeria"],
  ["PA", "Pasaporte"],
  ["TI", "Tarjeta de identidad"],
  ["RC", "Registro civil"],
  ["PPT", "PPT / Permiso"],
  ["NIT", "NIT"],
];

const folioEstadoOptions: Array<[FolioEstado, string]> = [
  ["matriz", "Matriz / ordinario"],
  ["segregado", "Segregado"],
  ["englobe", "Englobe"],
  ["desenglobe", "Desenglobe"],
  ["mayor_extension", "Mayor extension"],
  ["falsa_tradicion", "Falsa tradicion"],
];

const apoyoTipoOptions: Array<[ApoyoTipo, string]> = [
  ["acuerdo", "Acuerdo de apoyos"],
  ["adjudicacion", "Adjudicacion judicial de apoyos"],
];

const emptyParty: Party = {
  tipo: "natural",
  genero: "M",
  tipoDoc: "CC",
  nombre: "",
  id: "",
  ciudad: "Medellin",
  estado: "soltero",
  repr: "",
  cuota: 0,
  direccion: "",
  telefono: "",
  correo: "",
  ocupacion: "",
  notiElec: true,
  pep: false,
};

const emptyInmueble: CompraventaInmueble = {
  descripcion: "",
  linderos: "",
  matricula: "",
  catastral: "",
  nupre: "",
  avaluoCatastral: 0,
};

function Field({ id, label, hint, children }: FieldProps) {
  return (
    <div className="mt-3">
      <label className={labelClass} htmlFor={id}>{label}</label>
      {children}
      {hint ? <p className="mt-1 text-xs leading-5 text-secondary">{hint}</p> : null}
    </div>
  );
}

function Fieldset({ marker, title, children }: { marker: string; title: string; children: ReactNode }) {
  return (
    <fieldset className={fieldsetClass}>
      <legend className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.08em] text-primary">
        <span className="grid h-5 w-5 place-items-center rounded-md bg-primary text-[10px] text-white">{marker}</span>
        {title}
      </legend>
      {children}
    </fieldset>
  );
}

function Checkbox({ id, checked, label, disabled, onChange }: { id: string; checked: boolean; label: string; disabled?: boolean; onChange: (checked: boolean) => void }) {
  return (
    <label className={`${checkClass} mt-3 ${disabled ? "text-secondary" : ""}`} htmlFor={id}>
      <input
        id={id}
        type="checkbox"
        checked={checked}
        disabled={disabled}
        onChange={(event) => onChange(event.currentTarget.checked)}
        className="mt-0.5 h-4 w-4 rounded border-line-strong text-primary accent-[rgb(var(--primary))]"
      />
      <span>{label}</span>
    </label>
  );
}

function TextField({ id, label, value, hint, onChange, type = "text" }: { id: string; label: string; value: string; hint?: string; type?: "text" | "date"; onChange: (value: string) => void }) {
  return (
    <Field id={id} label={label} hint={hint}>
      <input id={id} type={type} value={value} onChange={(event) => onChange(event.currentTarget.value)} className={inputClass} />
    </Field>
  );
}

function TextAreaField({ id, label, value, onChange }: { id: string; label: string; value: string; onChange: (value: string) => void }) {
  return (
    <Field id={id} label={label}>
      <textarea id={id} value={value} onChange={(event) => onChange(event.currentTarget.value)} className={`${inputClass} min-h-20 resize-y leading-5`} />
    </Field>
  );
}

function NumberField({ id, label, value, onChange }: { id: string; label: string; value: number; onChange: (value: number) => void }) {
  return (
    <Field id={id} label={label}>
      <input id={id} type="number" value={Number.isFinite(value) ? value : 0} onChange={(event) => onChange(Number(event.currentTarget.value) || 0)} className={inputClass} />
    </Field>
  );
}

function MoneyField({ id, label, value, onChange }: { id: string; label: string; value: number; onChange: (value: number) => void }) {
  return (
    <Field id={id} label={label}>
      <input
        id={id}
        inputMode="decimal"
        value={Number.isFinite(value) && value > 0 ? pts(value) : ""}
        onChange={(event) => onChange(parseMoney(event.currentTarget.value))}
        className={inputClass}
      />
    </Field>
  );
}

function SelectField<T extends string>({ id, label, value, options, onChange }: { id: string; label: string; value: T; options: Array<[T, string]>; onChange: (value: T) => void }) {
  return (
    <Field id={id} label={label}>
      <select id={id} value={value} onChange={(event) => onChange(event.currentTarget.value as T)} className={inputClass}>
        {options.map(([optionValue, optionLabel]) => (
          <option key={optionValue} value={optionValue}>{optionLabel}</option>
        ))}
      </select>
    </Field>
  );
}

function equalizeCuotas(list: Party[]) {
  if (list.length === 0) return list;
  const base = Math.floor(100 / list.length);
  return list.map((party, index) => ({ ...party, cuota: index === list.length - 1 ? 100 - base * (list.length - 1) : base }));
}

function isCancelacionState(state: CaseState): state is CancelacionState {
  return "cNum" in state;
}

function legacyInmueble(state: CompraventaState): CompraventaInmueble {
  return {
    descripcion: state.inmdesc,
    linderos: state.linderos,
    matricula: state.matricula,
    catastral: state.catastral,
    nupre: state.nupre,
    avaluoCatastral: state.avaluoCatastral,
  };
}

function inmueblesForm(state: CompraventaState): CompraventaInmueble[] {
  return state.inmuebles?.length ? state.inmuebles : [legacyInmueble(state)];
}

function syncInmuebleLegacy(state: CompraventaState, inmuebles: CompraventaInmueble[]): CompraventaState {
  const first = inmuebles[0] || emptyInmueble;
  return {
    ...state,
    inmuebles,
    inmdesc: first.descripcion,
    linderos: first.linderos,
    matricula: first.matricula,
    catastral: first.catastral,
    nupre: first.nupre,
    avaluoCatastral: first.avaluoCatastral || 0,
  };
}

export function EscrituraForm({ acto, state, onChange }: Props) {
  if (acto === "cancelacion") {
    if (!isCancelacionState(state)) return null;
    return <CancelacionForm state={state} onChange={onChange} />;
  }
  if (isCancelacionState(state)) return null;
  return <CompraventaForm acto={acto} state={state} onChange={onChange} />;
}

function BancoSelector({
  onPickBanco,
  onPickRepresentante,
  bancoActual,
}: {
  onPickBanco: (entity: LegalEntityRecord) => void;
  onPickRepresentante: (name: string) => void;
  bancoActual: string;
}) {
  const [entidades, setEntidades] = useState<LegalEntityRecord[]>([]);
  const [representantes, setRepresentantes] = useState<LegalEntityRepresentativeRecord[]>([]);
  const [selId, setSelId] = useState<number | null>(null);
  const [cargaError, setCargaError] = useState<string | null>(null);
  const [cargado, setCargado] = useState(false);
  const [dbg, setDbg] = useState<string>("(sin selección)");

  useEffect(() => {
    let active = true;
    searchLegalEntities("")
      .then((list) => {
        if (!active) return;
        setEntidades(list);
        setCargado(true);
        setCargaError(null);
      })
      .catch((err) => {
        if (!active) return;
        setEntidades([]);
        setCargado(true);
        setCargaError(err instanceof Error ? err.message : "No se pudieron cargar los bancos.");
      });
    return () => {
      active = false;
    };
  }, []);

  async function handlePickEntity(index: number) {
    const entity = entidades[index];
    if (!entity) {
      setDbg(`onChange idx=${index} pero entidad no encontrada`);
      return;
    }
    setDbg(`elegido: ${entity.name} · id=${String(entity.id)} · idx=${index}`);
    setSelId(index);
    setRepresentantes([]);
    onPickBanco(entity);
    if (entity.id == null) return;
    try {
      const reps = await getLegalEntityRepresentatives(entity.id);
      setRepresentantes(reps.filter((rep) => rep.is_active));
    } catch {
      setRepresentantes([]);
    }
  }

  return (
    <div className="mb-3 rounded-md border border-dashed border-line-strong bg-white/60 p-2">
      <label htmlFor="banco-registro" className={labelClass}>
        Banco del registro (autocompleta)
      </label>
      <select
        id="banco-registro"
        className={inputClass}
        value={selId ?? ""}
        onChange={(event) => {
          const si = event.currentTarget.selectedIndex; // 0 = placeholder
          setDbg(`onChange selectedIndex=${si} value="${event.currentTarget.value}"`);
          if (si > 0) handlePickEntity(si - 1);
        }}
      >
        <option value="">— Seleccionar banco —</option>
        {entidades.map((entity, index) => (
          <option key={entity.id ?? index} value={index}>
            {entity.name} · NIT {entity.nit}
          </option>
        ))}
      </select>
      {cargaError ? (
        <p className="mt-1 text-[11px] font-semibold text-red-600">Error cargando bancos: {cargaError}</p>
      ) : cargado && entidades.length === 0 ? (
        <p className="mt-1 text-[11px] font-semibold text-amber-600">No hay bancos registrados. Siembra: <code>python -m app.seeds.seed_legal_entities</code></p>
      ) : cargado ? (
        <p className="mt-1 text-[11px] text-secondary">{entidades.length} banco(s) disponibles.</p>
      ) : null}
      <p className="mt-1 text-[11px] font-mono text-blue-600">dbg: {dbg} · selId={String(selId)} · banco.estado="{bancoActual}"</p>
      {representantes.length > 0 ? (
        <select
          className={`${inputClass} mt-2`}
          defaultValue=""
          onChange={(event) => {
            if (event.currentTarget.value) onPickRepresentante(event.currentTarget.value);
          }}
        >
          <option value="">— Apoderado(a) del banco —</option>
          {representantes.map((rep) => (
            <option key={rep.id} value={rep.person_name}>
              {rep.person_name}
              {rep.power_type ? ` · ${rep.power_type}` : ""}
            </option>
          ))}
        </select>
      ) : null}
    </div>
  );
}

function CompraventaForm({ acto, state, onChange }: { acto: Exclude<ActoCode, "cancelacion">; state: CompraventaState; onChange: (state: CaseState) => void }) {
  const effectiveCredito = acto === "hipoteca" || state.credito;
  const showAfectacion = casadoOUnion(state.V);
  const pagosCuadran = state.inicial + state.saldo === state.total;
  const compradorCuotas = sumaCuotas(state.C);
  const vendedorCuotas = sumaCuotas(state.V);
  const inmuebles = inmueblesForm(state);
  const encadenamientos = state.encadenamientos || {};
  const divisas = state.divisas || {};
  const rural = state.rural || {};
  const capacidad = state.capacidad || {};

  function setField<K extends keyof CompraventaState>(key: K, value: CompraventaState[K]) {
    onChange({ ...state, [key]: value });
  }

  function applyPatch(patch: Partial<CompraventaState>) {
    onChange({ ...state, ...patch } as CompraventaState);
  }

  function setAx<K extends keyof CompraventaState["ax"]>(key: K, value: boolean) {
    onChange({ ...state, ax: { ...state.ax, [key]: value } });
  }

  function setParty(side: "V" | "C", index: number, patch: Partial<Party>) {
    const next = state[side].map((party, itemIndex) => {
      if (itemIndex !== index) return party;
      const updated = { ...party, ...patch };
      if (patch.tipo === "juridica") {
        updated.tipoDoc = "NIT";
        updated.genero = "F";
        updated.estado = "soltero";
      }
      if (patch.tipo === "natural" && updated.tipoDoc === "NIT") {
        updated.tipoDoc = "CC";
      }
      return updated;
    });
    onChange({ ...state, [side]: next } as CompraventaState);
  }

  function addParty(side: "V" | "C") {
    const next = equalizeCuotas([...state[side], { ...emptyParty }]);
    onChange({ ...state, [side]: next } as CompraventaState);
  }

  function removeParty(side: "V" | "C", index: number) {
    const current = state[side];
    if (current.length <= 1) return;
    const next = equalizeCuotas(current.filter((_party, itemIndex) => itemIndex !== index));
    onChange({ ...state, [side]: next } as CompraventaState);
  }

  function setAuxList(index: number, patch: Partial<AuxParty>) {
    const next = state.testigos.map((party, itemIndex) => itemIndex === index ? { ...party, ...patch } : party);
    setField("testigos", next);
  }

  function setRuego(patch: Partial<AuxParty>) {
    setField("ruego", { ...state.ruego, ...patch });
  }

  function setInmueble(index: number, patch: Partial<CompraventaInmueble>) {
    const next = inmuebles.map((inmueble, itemIndex) => itemIndex === index ? { ...inmueble, ...patch } : inmueble);
    onChange(syncInmuebleLegacy(state, next));
  }

  function addInmueble() {
    onChange(syncInmuebleLegacy(state, [...inmuebles, { ...emptyInmueble }]));
  }

  function removeInmueble(index: number) {
    if (inmuebles.length <= 1) return;
    onChange(syncInmuebleLegacy(state, inmuebles.filter((_inmueble, itemIndex) => itemIndex !== index)));
  }

  function setEncadenamiento<K extends keyof EncadenamientosCompraventa>(key: K, value: EncadenamientosCompraventa[K]) {
    onChange({ ...state, encadenamientos: { ...encadenamientos, [key]: value } });
  }

  function setHipotecaPrevia(patch: NonNullable<EncadenamientosCompraventa["hipotecaPrevia"]>) {
    setEncadenamiento("hipotecaPrevia", { ...(encadenamientos.hipotecaPrevia || {}), ...patch });
  }

  function setPatrimonioFamilia(patch: NonNullable<EncadenamientosCompraventa["patrimonioFamilia"]>) {
    setEncadenamiento("patrimonioFamilia", { ...(encadenamientos.patrimonioFamilia || {}), ...patch });
  }

  function setAfectacion(patch: NonNullable<EncadenamientosCompraventa["afectacion"]>) {
    setEncadenamiento("afectacion", { ...(encadenamientos.afectacion || {}), ...patch });
  }

  function setDivisas(patch: Partial<CompraventaDivisas>) {
    onChange({ ...state, divisas: { ...divisas, ...patch } });
  }

  function setRural(patch: Partial<CompraventaRural>) {
    const nextRural = { ...rural, ...patch };
    onChange({ ...state, ph: nextRural.predioRural ? false : state.ph, rural: nextRural });
  }

  function setCapacidad(patch: Partial<CompraventaCapacidad>) {
    onChange({ ...state, capacidad: { ...capacidad, ...patch } });
  }

  return (
    <form className="ep-card max-h-none overflow-auto rounded-[1.25rem] p-5 lg:sticky lg:top-4 lg:max-h-[calc(100vh-2rem)]" autoComplete="off">
      <Fieldset marker="0" title="Acto">
        <SelectField
          id="derecho"
          label="Derecho que se transfiere"
          value={state.derecho}
          onChange={(value) => setField("derecho", value)}
          options={[
            ["dominio", "Pleno dominio"],
            ["nuda", "Nuda propiedad"],
            ["usufructo", "Usufructo"],
            ["cuota", "Derechos y acciones"],
            ["uso", "Uso y habitacion"],
          ]}
        />
        <Checkbox
          id="credito"
          checked={effectiveCredito}
          disabled={acto === "hipoteca"}
          label="La parte compradora paga con credito hipotecario"
          onChange={(checked) => setField("credito", checked)}
        />
        {effectiveCredito ? (
          <div className="mt-3 rounded-lg border-l-2 border-primary bg-primary/8 p-3">
            <BancoSelector
              bancoActual={state.banco}
              onPickBanco={(entity) =>
                applyPatch({
                  banco: entity.name,
                  bancoNit: entity.nit,
                  ...(entity.legal_representative ? { apoderadoBanco: entity.legal_representative } : {}),
                })
              }
              onPickRepresentante={(name) => setField("apoderadoBanco", name)}
            />
            <div className={row2Class}>
              <TextField id="banco" label="Banco acreedor" value={state.banco} onChange={(value) => setField("banco", value)} />
              <TextField id="bancoNit" label="NIT del banco" value={state.bancoNit} onChange={(value) => setField("bancoNit", value)} />
            </div>
            <div className={row2Class}>
              <NumberField id="plazoAnios" label="Plazo en anos" value={state.plazoAnios} onChange={(value) => setField("plazoAnios", value)} />
              <NumberField id="numCuotas" label="Numero de cuotas" value={state.numCuotas} onChange={(value) => setField("numCuotas", value)} />
            </div>
            <TextField id="apoderadoBanco" label="Apoderado(a) del banco" value={state.apoderadoBanco} onChange={(value) => setField("apoderadoBanco", value)} />
            <div className={row2Class}>
              <TextField id="poderBancoEP" label="Poder del banco - E.P." value={state.poderBancoEP} onChange={(value) => setField("poderBancoEP", value)} />
              <TextField id="poderBancoNot" label="Notaria del poder" value={state.poderBancoNot} onChange={(value) => setField("poderBancoNot", value)} />
            </div>
          </div>
        ) : null}
      </Fieldset>

      <Fieldset marker="1" title="Parte vendedora">
        <Checkbox id="apoderado" checked={state.apod} label="Comparece por apoderado" onChange={(checked) => setField("apod", checked)} />
        {state.apod ? (
          <div className="mt-3 rounded-lg border-l-2 border-primary bg-primary/8 p-3">
            <TextField id="apodNombre" label="Apoderado - nombre" value={state.apodN} onChange={(value) => setField("apodN", value)} />
            <TextField id="apodPoder" label="Poder" value={state.apodP} onChange={(value) => setField("apodP", value)} />
          </div>
        ) : null}
        <PartyList title="Vendedor" side="V" parties={state.V} onPatch={setParty} onAdd={() => addParty("V")} onRemove={(index) => removeParty("V", index)} />
        <p className={`mt-2 text-xs ${vendedorCuotas === 100 ? "text-emerald-700" : "text-amber-700"}`}>Cuotas vendedoras: {vendedorCuotas}%.</p>
        {showAfectacion ? (
          <SelectField
            id="afectada"
            label="El inmueble esta afectado a vivienda familiar"
            value={state.afect}
            onChange={(value) => setField("afect", value)}
            options={[
              ["no", "No, se declara"],
              ["si", "Si"],
              ["nosabe", "No se sabe"],
            ]}
          />
        ) : null}
      </Fieldset>

      <Fieldset marker="1b" title="Parte compradora">
        <PartyList title="Comprador" side="C" parties={state.C} onPatch={setParty} onAdd={() => addParty("C")} onRemove={(index) => removeParty("C", index)} />
        <p className={`mt-2 text-xs ${compradorCuotas === 100 ? "text-emerald-700" : "text-red-700"}`}>Cuotas compradoras: {compradorCuotas}%.</p>
      </Fieldset>

      <Fieldset marker="2" title="Inmuebles">
        <InmuebleList inmuebles={inmuebles} onPatch={setInmueble} onAdd={addInmueble} onRemove={removeInmueble} />
        <Checkbox id="ph" checked={state.ph} label="Sometido a propiedad horizontal" onChange={(checked) => setField("ph", checked)} />
        {state.ph ? <TextField id="phReg" label="Reglamento de P.H." value={state.phReg} onChange={(value) => setField("phReg", value)} /> : null}
        <SelectField
          id="vis"
          label="Vivienda de interes social"
          value={state.vis}
          onChange={(value) => setField("vis", value)}
          options={[
            ["no", "No"],
            ["sfve", "Si - subsidio 100% en especie"],
            ["otra", "Si - otra modalidad"],
          ]}
        />
      </Fieldset>

      <Fieldset marker="3" title="Titulo y estado juridico">
        <div className={row2Class}>
          <TextField id="tituloNum" label="Titulo - numero de escritura" value={state.tituloNum} onChange={(value) => setField("tituloNum", value)} />
          <TextField id="tituloFecha" label="Titulo - fecha" type="date" value={state.tituloFecha} onChange={(value) => setField("tituloFecha", value)} />
        </div>
        <TextField id="tituloNotaria" label="Titulo - notaria de origen" value={state.tituloNotaria} onChange={(value) => setField("tituloNotaria", value)} />
        <SelectField
          id="gravamen"
          label="Gravamenes o limitaciones"
          value={state.gravamen}
          onChange={(value) => setField("gravamen", value)}
          options={[
            ["libre", "Libre de gravamenes"],
            ["hipoteca_previa", "Hipoteca previa"],
            ["patrimonio", "Patrimonio de familia"],
            ["usufructo", "Usufructo vigente"],
            ["servidumbre", "Servidumbre"],
            ["leasing", "Leasing habitacional"],
            ["embargo", "Embargo / demanda"],
          ]}
        />
        <SelectField<FolioEstado>
          id="folioEstado"
          label="Estado del folio"
          value={state.folioEstado || "matriz"}
          onChange={(value) => setField("folioEstado", value)}
          options={folioEstadoOptions}
        />
      </Fieldset>

      <Fieldset marker="3b" title="Encadenamientos">
        <Checkbox
          id="enc-cancelacion-hipoteca"
          checked={Boolean(encadenamientos.cancelacionHipotecaPrevia)}
          label="Agregar cancelacion de hipoteca previa"
          onChange={(checked) => setEncadenamiento("cancelacionHipotecaPrevia", checked)}
        />
        {encadenamientos.cancelacionHipotecaPrevia ? (
          <div className="mt-3 rounded-lg border-l-2 border-primary bg-primary/8 p-3">
            <div className={row2Class}>
              <TextField id="enc-hip-acreedor" label="Acreedor que cancela" value={encadenamientos.hipotecaPrevia?.acreedor || ""} onChange={(value) => setHipotecaPrevia({ acreedor: value })} />
              <TextField id="enc-hip-nit" label="NIT acreedor" value={encadenamientos.hipotecaPrevia?.nit || ""} onChange={(value) => setHipotecaPrevia({ nit: value })} />
            </div>
            <div className={row2Class}>
              <TextField id="enc-hip-escritura" label="E.P. hipoteca" value={encadenamientos.hipotecaPrevia?.escritura || ""} onChange={(value) => setHipotecaPrevia({ escritura: value })} />
              <TextField id="enc-hip-fecha" label="Fecha hipoteca" type="date" value={encadenamientos.hipotecaPrevia?.fecha || ""} onChange={(value) => setHipotecaPrevia({ fecha: value })} />
            </div>
            <TextField id="enc-hip-notaria" label="Notaria hipoteca" value={encadenamientos.hipotecaPrevia?.notaria || ""} onChange={(value) => setHipotecaPrevia({ notaria: value })} />
            <div className={row2Class}>
              <TextField id="enc-hip-registro" label="Fecha registro" value={encadenamientos.hipotecaPrevia?.registroFecha || ""} onChange={(value) => setHipotecaPrevia({ registroFecha: value })} />
              <TextField id="enc-hip-orip" label="ORIP" value={encadenamientos.hipotecaPrevia?.orip || ""} onChange={(value) => setHipotecaPrevia({ orip: value })} />
            </div>
          </div>
        ) : null}
        <Checkbox
          id="enc-cancelacion-patrimonio"
          checked={Boolean(encadenamientos.cancelacionPatrimonioFamilia)}
          label="Agregar cancelacion de patrimonio de familia"
          onChange={(checked) => setEncadenamiento("cancelacionPatrimonioFamilia", checked)}
        />
        {encadenamientos.cancelacionPatrimonioFamilia ? (
          <div className="mt-3 rounded-lg border-l-2 border-primary bg-primary/8 p-3">
            <div className={row2Class}>
              <TextField id="enc-pat-escritura" label="E.P. patrimonio" value={encadenamientos.patrimonioFamilia?.escritura || ""} onChange={(value) => setPatrimonioFamilia({ escritura: value })} />
              <TextField id="enc-pat-fecha" label="Fecha patrimonio" type="date" value={encadenamientos.patrimonioFamilia?.fecha || ""} onChange={(value) => setPatrimonioFamilia({ fecha: value })} />
            </div>
            <TextField id="enc-pat-notaria" label="Notaria patrimonio" value={encadenamientos.patrimonioFamilia?.notaria || ""} onChange={(value) => setPatrimonioFamilia({ notaria: value })} />
            <TextField id="enc-pat-beneficiarios" label="Beneficiarios / interesados" value={encadenamientos.patrimonioFamilia?.beneficiarios || ""} onChange={(value) => setPatrimonioFamilia({ beneficiarios: value })} />
          </div>
        ) : null}
        <Checkbox
          id="enc-afectacion"
          checked={Boolean(encadenamientos.afectacionViviendaFamiliar)}
          label="Agregar afectacion a vivienda familiar"
          onChange={(checked) => setEncadenamiento("afectacionViviendaFamiliar", checked)}
        />
        {encadenamientos.afectacionViviendaFamiliar ? (
          <div className="mt-3 rounded-lg border-l-2 border-primary bg-primary/8 p-3">
            <TextField id="enc-afectacion-beneficiarios" label="Nucleo familiar / beneficiarios" value={encadenamientos.afectacion?.beneficiarios || ""} onChange={(value) => setAfectacion({ beneficiarios: value })} />
          </div>
        ) : null}
      </Fieldset>

      <Fieldset marker="3c" title="Extranjeria y divisas">
        <Checkbox
          id="parteExtranjeraNoResidente"
          checked={Boolean(divisas.parteExtranjeraNoResidente)}
          label="Interviene parte extranjera o no residente"
          onChange={(checked) => setDivisas({ parteExtranjeraNoResidente: checked })}
        />
        <Checkbox
          id="pagoDivisas"
          checked={Boolean(divisas.pagoDivisas)}
          label="El precio se paga total o parcialmente en divisas"
          onChange={(checked) => setDivisas({ pagoDivisas: checked })}
        />
        {divisas.parteExtranjeraNoResidente || divisas.pagoDivisas ? (
          <div className="mt-3 rounded-lg border-l-2 border-primary bg-primary/8 p-3">
            <div className={row2Class}>
              <TextField id="divisas-moneda" label="Moneda" value={divisas.moneda || ""} onChange={(value) => setDivisas({ moneda: value })} />
              <NumberField id="divisas-valor" label="Valor en divisas" value={divisas.valorDivisas || 0} onChange={(value) => setDivisas({ valorDivisas: value })} />
            </div>
            <div className={row2Class}>
              <TextField id="divisas-declaracion" label="Declaracion de cambio" value={divisas.declaracionCambio || ""} onChange={(value) => setDivisas({ declaracionCambio: value })} />
              <TextField id="divisas-origen" label="Pais / origen de fondos" value={divisas.paisOrigenFondos || ""} onChange={(value) => setDivisas({ paisOrigenFondos: value })} />
            </div>
            <div className="grid gap-2 sm:grid-cols-2">
              <Checkbox id="divisas-canalizacion" checked={Boolean(divisas.canalizacionMercadoCambiario)} label="Canalizado por mercado cambiario" onChange={(checked) => setDivisas({ canalizacionMercadoCambiario: checked })} />
              <Checkbox id="divisas-registro" checked={Boolean(divisas.registroInversionExtranjera)} label="Registro de inversion extranjera" onChange={(checked) => setDivisas({ registroInversionExtranjera: checked })} />
              <Checkbox id="divisas-apostilla" checked={Boolean(divisas.poderExteriorApostillado)} label="Poder exterior apostillado/legalizado" onChange={(checked) => setDivisas({ poderExteriorApostillado: checked })} />
            </div>
          </div>
        ) : null}
      </Fieldset>

      <Fieldset marker="3d" title="Rural / UAF / baldios">
        <Checkbox
          id="predioRural"
          checked={Boolean(rural.predioRural)}
          label="Predio rural no sometido a PH"
          onChange={(checked) => setRural({ predioRural: checked })}
        />
        {rural.predioRural || rural.baldioAdjudicado || rural.superaUaf ? (
          <div className="mt-3 rounded-lg border-l-2 border-primary bg-primary/8 p-3">
            <div className={row2Class}>
              <NumberField id="rural-area" label="Area hectareas" value={rural.areaHectareas || 0} onChange={(value) => setRural({ areaHectareas: value })} />
              <NumberField id="rural-uaf" label="UAF hectareas" value={rural.uafHectareas || 0} onChange={(value) => setRural({ uafHectareas: value })} />
            </div>
            <TextField id="rural-region" label="Municipio / region UAF" value={rural.municipioRegionUaf || ""} onChange={(value) => setRural({ municipioRegionUaf: value })} />
            <div className="grid gap-2 sm:grid-cols-2">
              <Checkbox id="rural-baldio" checked={Boolean(rural.baldioAdjudicado)} label="Baldio adjudicado por ANT/INCORA" onChange={(checked) => setRural({ baldioAdjudicado: checked })} />
              <Checkbox id="rural-restriccion" checked={Boolean(rural.restriccionTemporal)} label="Restriccion temporal vigente" onChange={(checked) => setRural({ restriccionTemporal: checked })} />
              <Checkbox id="rural-supera-uaf" checked={Boolean(rural.superaUaf)} label="Supera la UAF" onChange={(checked) => setRural({ superaUaf: checked })} />
              <Checkbox id="rural-autorizacion-ant" checked={Boolean(rural.autorizacionAnt)} label="Autorizacion ANT acreditada" onChange={(checked) => setRural({ autorizacionAnt: checked })} />
              <Checkbox id="rural-preferencia" checked={Boolean(rural.derechoPreferencia)} label="Derecho de preferencia por revisar" onChange={(checked) => setRural({ derechoPreferencia: checked })} />
            </div>
          </div>
        ) : null}
      </Fieldset>

      <Fieldset marker="3e" title="Capacidad y apoyos">
        <Checkbox id="menorVendedor" checked={Boolean(capacidad.menorVendedor)} label="Otorgante vendedor menor de edad" onChange={(checked) => setCapacidad({ menorVendedor: checked, ventaBienMenor: checked || capacidad.ventaBienMenor })} />
        <Checkbox id="ventaBienMenor" checked={Boolean(capacidad.ventaBienMenor)} label="Venta de bien de persona menor de edad" onChange={(checked) => setCapacidad({ ventaBienMenor: checked })} />
        <Checkbox id="discapacidadConApoyos" checked={Boolean(capacidad.discapacidadConApoyos)} label="Persona con discapacidad usa apoyos" onChange={(checked) => setCapacidad({ discapacidadConApoyos: checked })} />
        {capacidad.menorVendedor || capacidad.ventaBienMenor || capacidad.discapacidadConApoyos ? (
          <div className="mt-3 rounded-lg border-l-2 border-primary bg-primary/8 p-3">
            <Checkbox id="autorizacionVentaMenor" checked={Boolean(capacidad.autorizacionVentaMenor)} label="Autorizacion judicial/notarial vigente" onChange={(checked) => setCapacidad({ autorizacionVentaMenor: checked })} />
            <TextField id="capacidad-autorizacion" label="Detalle de autorizacion" value={capacidad.autorizacionDetalle || ""} onChange={(value) => setCapacidad({ autorizacionDetalle: value })} />
            {capacidad.discapacidadConApoyos ? (
              <>
                <Checkbox id="apoyoAcreditado" checked={Boolean(capacidad.apoyoAcreditado)} label="Apoyo acreditado" onChange={(checked) => setCapacidad({ apoyoAcreditado: checked })} />
                <SelectField<ApoyoTipo> id="apoyoTipo" label="Tipo de apoyo" value={capacidad.apoyoTipo || "acuerdo"} onChange={(value) => setCapacidad({ apoyoTipo: value })} options={apoyoTipoOptions} />
                <div className={row2Class}>
                  <TextField id="apoyoNombre" label="Persona de apoyo" value={capacidad.apoyoNombre || ""} onChange={(value) => setCapacidad({ apoyoNombre: value })} />
                  <TextField id="apoyoDocumento" label="Documento apoyo" value={capacidad.apoyoDocumento || ""} onChange={(value) => setCapacidad({ apoyoDocumento: value })} />
                </div>
                <TextField id="apoyoActo" label="Acuerdo / adjudicacion de apoyos" value={capacidad.apoyoActo || ""} onChange={(value) => setCapacidad({ apoyoActo: value })} />
              </>
            ) : null}
          </div>
        ) : null}
      </Fieldset>

      <Fieldset marker="4" title="Precio">
        <MoneyField id="total" label="Precio total" value={state.total} onChange={(value) => setField("total", value)} />
        <div className={row2Class}>
          <MoneyField id="inicial" label="Cuota inicial" value={state.inicial} onChange={(value) => setField("inicial", value)} />
          <MoneyField id="saldo" label="Saldo con credito" value={state.saldo} onChange={(value) => setField("saldo", value)} />
        </div>
        <p className={`mt-2 text-xs ${pagosCuadran ? "text-emerald-700" : "text-red-700"}`}>
          {pagosCuadran ? "Los pagos cuadran con el total." : `Inicial + saldo = ${pts(state.inicial + state.saldo)} y total = ${pts(state.total)}.`}
        </p>
      </Fieldset>

      <Fieldset marker="5" title="Acto avanzado">
        <SelectField
          id="tipoNegocio"
          label="Tipo de negocio"
          value={state.tipoNegocio}
          onChange={(value) => setField("tipoNegocio", value)}
          options={[
            ["compraventa", "Compraventa"],
            ["permuta", "Permuta"],
            ["dacion", "Dacion en pago"],
            ["retroventa", "Compraventa con pacto de retroventa"],
            ["reserva", "Compraventa con reserva de dominio"],
          ]}
        />
        <SelectField
          id="tituloTipo"
          label="Titulo de adquisicion del vendedor"
          value={state.tituloTipo}
          onChange={(value) => setField("tituloTipo", value)}
          options={[
            ["compraventa", "Compraventa anterior"],
            ["sucesion", "Sucesion / adjudicacion"],
            ["donacion", "Donacion"],
            ["remate", "Adjudicacion en remate"],
            ["prescripcion", "Prescripcion"],
          ]}
        />
        <Checkbox id="subsidio" checked={state.subsidio} label="Pago con subsidio de vivienda" onChange={(checked) => setField("subsidio", checked)} />
        {state.subsidio ? <TextField id="subsidioEnt" label="Entidad del subsidio" value={state.subsidioEnt} onChange={(value) => setField("subsidioEnt", value)} /> : null}
        <Checkbox id="posesion2" checked={state.posesion2} label="El vendedor poseyo el inmueble 2 anos o mas" onChange={(checked) => setField("posesion2", checked)} />
        <Checkbox id="firmaRuego" checked={state.firmaRuego} label="Un otorgante firma a ruego" onChange={(checked) => setField("firmaRuego", checked)} />
        {state.firmaRuego ? (
          <div className="mt-3 rounded-lg border-l-2 border-primary bg-primary/8 p-3">
            <AuxPartyFields title="Firmante a ruego" scope="ruego" party={state.ruego} onPatch={setRuego} />
          </div>
        ) : null}
        <Checkbox id="interprete" checked={state.interprete} label="Requiere interprete / traductor" onChange={(checked) => setField("interprete", checked)} />
        <Checkbox id="pep" checked={state.pep} label="Alguna parte es PEP" onChange={(checked) => setField("pep", checked)} />
        <Checkbox id="cuentaTercero" checked={state.cuentaTercero} label="Alguna parte actua por cuenta de tercero" onChange={(checked) => setField("cuentaTercero", checked)} />
        <Checkbox id="pep_indagado" checked={state.pep_indagado} label="Indagacion PEP realizada y con constancia" onChange={(checked) => setField("pep_indagado", checked)} />
        <Checkbox id="rupta_verificado" checked={state.rupta_verificado} label="Verificacion RUPTA (tierras despojadas/protegidas) realizada" onChange={(checked) => setField("rupta_verificado", checked)} />
      </Fieldset>

      <Fieldset marker="6" title="Otorgamiento y firmas">
        <div className={row2Class}>
          <TextField id="numEscritura" label="Numero de escritura" value={state.numEscritura} onChange={(value) => setField("numEscritura", value)} />
          <TextField id="hojaInicial" label="Hoja de papel notarial" value={state.hojaInicial} onChange={(value) => setField("hojaInicial", value)} />
        </div>
        <TextField
          id="fechaOtorg"
          label="Fecha de otorgamiento"
          type="date"
          value={state.fechaOtorg}
          hint={state.fechaOtorg ? `En la escritura: a los ${fechaText(state.fechaOtorg)}.` : "Seleccione la fecha de otorgamiento."}
          onChange={(value) => setField("fechaOtorg", value)}
        />
        <Checkbox id="huella" checked={state.huella} label="Se toma impresion dactilar de los otorgantes" onChange={(checked) => setField("huella", checked)} />
        <Checkbox id="testigos" checked={state.testigosOn} label="Concurren testigos instrumentales" onChange={(checked) => setField("testigosOn", checked)} />
        {state.testigosOn || state.firmaRuego ? (
          <div className="mt-3 rounded-lg border-l-2 border-primary bg-primary/8 p-3">
            {state.testigos.map((party, index) => (
              <AuxPartyFields key={index} title={`Testigo ${index + 1}`} scope={`testigo-${index}`} party={party} onPatch={(patch) => setAuxList(index, patch)} />
            ))}
          </div>
        ) : null}
      </Fieldset>

      <Fieldset marker="7" title="Anexos aportados">
        <div className="grid gap-2 sm:grid-cols-2">
          <Checkbox id="ax_tradicion" checked={state.ax.tradicion} label="Certificado de tradicion" onChange={(checked) => setAx("tradicion", checked)} />
          <Checkbox id="ax_predial" checked={state.ax.predial} label="Paz y salvo predial" onChange={(checked) => setAx("predial", checked)} />
          <Checkbox id="ax_admin" checked={state.ax.admin} label="Paz y salvo administracion" onChange={(checked) => setAx("admin", checked)} />
          <Checkbox id="ax_cedulas" checked={state.ax.cedulas} label="Cedulas" onChange={(checked) => setAx("cedulas", checked)} />
        </div>
      </Fieldset>
    </form>
  );
}

function InmuebleList({
  inmuebles,
  onPatch,
  onAdd,
  onRemove,
}: {
  inmuebles: CompraventaInmueble[];
  onPatch: (index: number, patch: Partial<CompraventaInmueble>) => void;
  onAdd: () => void;
  onRemove: (index: number) => void;
}) {
  return (
    <div className="mt-3 space-y-3">
      {inmuebles.map((inmueble, index) => (
        <div key={index} className="rounded-lg border border-line bg-white p-3">
          <div className="flex items-center justify-between gap-3">
            <h3 className="text-sm font-bold text-primary">Inmueble {index + 1}</h3>
            {inmuebles.length > 1 ? (
              <button type="button" onClick={() => onRemove(index)} className="inline-flex items-center gap-1 rounded-md border border-line-strong px-2 py-1 text-xs font-semibold text-secondary hover:border-red-300 hover:text-red-700">
                <Trash2 className="h-3.5 w-3.5" aria-hidden="true" />
                Quitar
              </button>
            ) : null}
          </div>
          <TextAreaField id={`inmueble-${index}-descripcion`} label={`Descripcion inmueble ${index + 1}`} value={inmueble.descripcion} onChange={(value) => onPatch(index, { descripcion: value })} />
          <TextAreaField id={`inmueble-${index}-linderos`} label={`Linderos inmueble ${index + 1}`} value={inmueble.linderos} onChange={(value) => onPatch(index, { linderos: value })} />
          <div className={row2Class}>
            <TextField id={`inmueble-${index}-matricula`} label={`Matricula inmueble ${index + 1}`} value={inmueble.matricula} onChange={(value) => onPatch(index, { matricula: value })} />
            <TextField id={`inmueble-${index}-catastral`} label={`Cedula catastral inmueble ${index + 1}`} value={inmueble.catastral} onChange={(value) => onPatch(index, { catastral: value })} />
          </div>
          <div className={row2Class}>
            <MoneyField id={`inmueble-${index}-avaluo`} label={`Avaluo catastral inmueble ${index + 1}`} value={inmueble.avaluoCatastral || 0} onChange={(value) => onPatch(index, { avaluoCatastral: value })} />
            <TextField id={`inmueble-${index}-nupre`} label={`NUPRE inmueble ${index + 1}`} value={inmueble.nupre} onChange={(value) => onPatch(index, { nupre: value })} />
          </div>
        </div>
      ))}
      <button type="button" onClick={onAdd} className="inline-flex w-full items-center justify-center gap-2 rounded-lg border border-dashed border-primary/40 bg-primary/8 px-3 py-2 text-sm font-semibold text-primary hover:bg-primary/12">
        <Plus className="h-4 w-4" aria-hidden="true" />
        Agregar inmueble
      </button>
    </div>
  );
}

function PartyList({ title, side, parties, onPatch, onAdd, onRemove }: { title: "Vendedor" | "Comprador"; side: "V" | "C"; parties: Party[]; onPatch: (side: "V" | "C", index: number, patch: Partial<Party>) => void; onAdd: () => void; onRemove: (index: number) => void }) {
  return (
    <div className="mt-3 space-y-3">
      {parties.map((party, index) => (
        <div key={index} className="rounded-lg border border-line bg-white p-3">
          <div className="flex items-center justify-between gap-3">
            <h3 className="text-sm font-bold text-primary">{title} {index + 1}</h3>
            {parties.length > 1 ? (
              <button type="button" onClick={() => onRemove(index)} className="inline-flex items-center gap-1 rounded-md border border-line-strong px-2 py-1 text-xs font-semibold text-secondary hover:border-red-300 hover:text-red-700">
                <Trash2 className="h-3.5 w-3.5" aria-hidden="true" />
                Quitar
              </button>
            ) : null}
          </div>
          <SelectField<TipoPersona>
            id={`${side}-${index}-tipo`}
            label="Naturaleza"
            value={party.tipo}
            onChange={(value) => onPatch(side, index, { tipo: value })}
            options={[
              ["natural", "Persona natural"],
              ["juridica", "Persona juridica"],
            ]}
          />
          <TextField id={`${side}-${index}-nombre`} label={`Nombre ${title.toLowerCase()} ${index + 1}`} value={party.nombre} onChange={(value) => onPatch(side, index, { nombre: value })} />
          {party.tipo === "juridica" ? (
            <>
              <div className={row2Class}>
                <TextField id={`${side}-${index}-id`} label="NIT" value={party.id} onChange={(value) => onPatch(side, index, { id: value })} />
                <NumberField id={`${side}-${index}-cuota`} label="Cuota %" value={party.cuota} onChange={(value) => onPatch(side, index, { cuota: value })} />
              </div>
              <TextField id={`${side}-${index}-ciudad`} label="Domicilio" value={party.ciudad} onChange={(value) => onPatch(side, index, { ciudad: value })} />
              <TextField id={`${side}-${index}-repr`} label="Representante legal" value={party.repr} onChange={(value) => onPatch(side, index, { repr: value })} />
            </>
          ) : (
            <>
              <SelectField<TipoDoc> id={`${side}-${index}-tipoDoc`} label="Tipo de documento" value={party.tipoDoc} onChange={(value) => onPatch(side, index, { tipoDoc: value })} options={tipoDocOptions.filter(([code]) => code !== "NIT")} />
              <div className={row2Class}>
                <TextField id={`${side}-${index}-id`} label="Numero de documento" value={party.id} onChange={(value) => onPatch(side, index, { id: value })} />
                <NumberField id={`${side}-${index}-cuota`} label="Cuota %" value={party.cuota} onChange={(value) => onPatch(side, index, { cuota: value })} />
              </div>
              <div className={row2Class}>
                <TextField id={`${side}-${index}-ciudad`} label="Domicilio" value={party.ciudad} onChange={(value) => onPatch(side, index, { ciudad: value })} />
                <SelectField<GeneroCode> id={`${side}-${index}-genero`} label="Genero / sexo" value={party.genero} onChange={(value) => onPatch(side, index, { genero: value })} options={generoOptions} />
              </div>
              <SelectField<EstadoCivil> id={`${side}-${index}-estado`} label="Estado civil" value={party.estado} onChange={(value) => onPatch(side, index, { estado: value })} options={estadoOptions} />
            </>
          )}
          <div className="mt-3 rounded-lg border-l-2 border-primary bg-primary/8 p-3">
            <p className="text-[10px] font-bold uppercase tracking-[0.08em] text-primary">Datos para firma</p>
            <TextField id={`${side}-${index}-direccion`} label="Direccion" value={party.direccion} onChange={(value) => onPatch(side, index, { direccion: value })} />
            <div className={row2Class}>
              <TextField id={`${side}-${index}-telefono`} label="Telefono" value={party.telefono} onChange={(value) => onPatch(side, index, { telefono: value })} />
              <TextField id={`${side}-${index}-ocupacion`} label={party.tipo === "juridica" ? "Actividad economica" : "Profesion u ocupacion"} value={party.ocupacion} onChange={(value) => onPatch(side, index, { ocupacion: value })} />
            </div>
            <TextField id={`${side}-${index}-correo`} label="Correo electronico" value={party.correo} onChange={(value) => onPatch(side, index, { correo: value })} />
            <Checkbox id={`${side}-${index}-notiElec`} checked={party.notiElec} label="Autoriza notificaciones electronicas" onChange={(checked) => onPatch(side, index, { notiElec: checked })} />
            <Checkbox id={`${side}-${index}-pep`} checked={party.pep} label="Persona Expuesta Politicamente" onChange={(checked) => onPatch(side, index, { pep: checked })} />
          </div>
        </div>
      ))}
      <button type="button" onClick={onAdd} className="inline-flex w-full items-center justify-center gap-2 rounded-lg border border-dashed border-primary/40 bg-primary/8 px-3 py-2 text-sm font-semibold text-primary hover:bg-primary/12">
        <Plus className="h-4 w-4" aria-hidden="true" />
        Agregar {title.toLowerCase()}
      </button>
    </div>
  );
}

function AuxPartyFields({ title, scope, party, onPatch }: { title: string; scope: string; party: AuxParty; onPatch: (patch: Partial<AuxParty>) => void }) {
  return (
    <div className="mt-3 rounded-lg border border-line bg-white p-3">
      <h3 className="text-sm font-bold text-primary">{title}</h3>
      <TextField id={`${scope}-nombre`} label="Nombre" value={party.nombre} onChange={(value) => onPatch({ nombre: value })} />
      <SelectField<TipoDoc> id={`${scope}-tipoDoc`} label="Tipo de documento" value={party.tipoDoc} onChange={(value) => onPatch({ tipoDoc: value })} options={tipoDocOptions.filter(([code]) => code !== "NIT")} />
      <div className={row2Class}>
        <TextField id={`${scope}-id`} label="Numero de documento" value={party.id} onChange={(value) => onPatch({ id: value })} />
        <TextField id={`${scope}-ciudad`} label="Municipio" value={party.ciudad} onChange={(value) => onPatch({ ciudad: value })} />
      </div>
      <TextField id={`${scope}-direccion`} label="Direccion" value={party.direccion} onChange={(value) => onPatch({ direccion: value })} />
      <div className={row2Class}>
        <TextField id={`${scope}-telefono`} label="Telefono" value={party.telefono} onChange={(value) => onPatch({ telefono: value })} />
        <TextField id={`${scope}-ocupacion`} label="Profesion u ocupacion" value={party.ocupacion} onChange={(value) => onPatch({ ocupacion: value })} />
      </div>
      <TextField id={`${scope}-correo`} label="Correo electronico" value={party.correo} onChange={(value) => onPatch({ correo: value })} />
    </div>
  );
}

function CancelacionForm({ state, onChange }: { state: CancelacionState; onChange: (state: CaseState) => void }) {
  function setField<K extends keyof CancelacionState>(key: K, value: CancelacionState[K]) {
    onChange({ ...state, [key]: value });
  }

  return (
    <form className="ep-card max-h-none overflow-auto rounded-[1.25rem] p-5 lg:sticky lg:top-4 lg:max-h-[calc(100vh-2rem)]" autoComplete="off">
      <Fieldset marker="1" title="Acreedor">
        <div className={row2Class}>
          <TextField id="cBanco" label="Banco acreedor" value={state.cBanco} onChange={(value) => setField("cBanco", value)} />
          <TextField id="cBancoNit" label="NIT" value={state.cBancoNit} onChange={(value) => setField("cBancoNit", value)} />
        </div>
        <TextField id="cBancoDom" label="Domicilio principal" value={state.cBancoDom} onChange={(value) => setField("cBancoDom", value)} />
        <SelectField
          id="cRepTipo"
          label="Como se acredita la representacion"
          value={state.cRepTipo}
          onChange={(value) => setField("cRepTipo", value)}
          options={[
            ["apoderado", "Apoderado(a) especial"],
            ["replegal", "Representante legal"],
          ]}
        />
        <TextField id="cRepCargo" label="Cargo con que obra" value={state.cRepCargo} onChange={(value) => setField("cRepCargo", value)} />
        {state.cRepTipo === "apoderado" ? (
          <div className={row2Class}>
            <TextField id="cPoderEP" label="Poder - E.P. numero" value={state.cPoderEP} onChange={(value) => setField("cPoderEP", value)} />
            <TextField id="cPoderFecha" label="Poder - fecha" value={state.cPoderFecha} onChange={(value) => setField("cPoderFecha", value)} />
          </div>
        ) : null}
        {state.cRepTipo === "apoderado" ? <TextField id="cPoderNotaria" label="Poder - notaria" value={state.cPoderNotaria} onChange={(value) => setField("cPoderNotaria", value)} /> : null}
      </Fieldset>

      <Fieldset marker="2" title="Otorgante del banco">
        <TextField id="cApoNombre" label="Nombre" value={state.cApoNombre} onChange={(value) => setField("cApoNombre", value)} />
        <div className={row2Class}>
          <TextField id="cApoCC" label="Cedula de ciudadania" value={state.cApoCC} onChange={(value) => setField("cApoCC", value)} />
          <SelectField<GeneroCode> id="cApoGenero" label="Genero / sexo" value={state.cApoGenero} onChange={(value) => setField("cApoGenero", value)} options={generoOptions} />
        </div>
      </Fieldset>

      <Fieldset marker="3" title="Propietario / deudor">
        <TextField id="cDeudor" label="Nombre(s) del deudor" value={state.cDeudor} onChange={(value) => setField("cDeudor", value)} />
        <p className="mt-2 text-xs leading-5 text-secondary">El deudor no firma: el acreedor libera el gravamen constituido a su favor.</p>
      </Fieldset>

      <Fieldset marker="4" title="Hipoteca que se cancela">
        <div className={row2Class}>
          <TextField id="cHipEP" label="E.P. de constitucion - numero" value={state.cHipEP} onChange={(value) => setField("cHipEP", value)} />
          <TextField id="cHipFecha" label="E.P. - fecha" value={state.cHipFecha} onChange={(value) => setField("cHipFecha", value)} />
        </div>
        <TextField id="cHipNotaria" label="Notaria de constitucion" value={state.cHipNotaria} onChange={(value) => setField("cHipNotaria", value)} />
        <div className={row2Class}>
          <TextField id="cHipRegFecha" label="Fecha de registro" value={state.cHipRegFecha} onChange={(value) => setField("cHipRegFecha", value)} />
          <MoneyField id="cHipMonto" label="Monto inicial" value={state.cHipMonto} onChange={(value) => setField("cHipMonto", value)} />
        </div>
        <TextField id="cOrip" label="Oficina de Registro" value={state.cOrip} onChange={(value) => setField("cOrip", value)} />
      </Fieldset>

      <Fieldset marker="5" title="Inmueble liberado">
        <TextAreaField id="cInmdesc" label="Descripcion y ubicacion" value={state.cInmdesc} onChange={(value) => setField("cInmdesc", value)} />
        <div className={row2Class}>
          <TextField id="cMatricula" label="Folio de matricula" value={state.cMatricula} onChange={(value) => setField("cMatricula", value)} />
          <TextField id="cCatastral" label="Codigo catastral" value={state.cCatastral} onChange={(value) => setField("cCatastral", value)} />
        </div>
        <TextField id="cNupre" label="NUPRE" value={state.cNupre} onChange={(value) => setField("cNupre", value)} />
      </Fieldset>

      <Fieldset marker="6" title="Escritura, notario y opciones">
        <div className={row2Class}>
          <TextField id="cNum" label="Numero de escritura" value={state.cNum} onChange={(value) => setField("cNum", value)} />
          <TextField id="cFechaOtorg" label="Fecha de otorgamiento" type="date" value={state.cFechaOtorg} onChange={(value) => setField("cFechaOtorg", value)} />
        </div>
        <TextField id="cNotario" label="Notario(a) que autoriza" value={state.cNotario} onChange={(value) => setField("cNotario", value)} />
        <div className={row2Class}>
          <SelectField<GeneroCode> id="cNotarioGenero" label="Genero del notario" value={state.cNotarioGenero} onChange={(value) => setField("cNotarioGenero", value)} options={generoOptions} />
          <TextField id="cCalidad" label="Calidad" value={state.cCalidad} onChange={(value) => setField("cCalidad", value)} />
        </div>
        <TextField id="cActoAdmin" label="Acto administrativo" value={state.cActoAdmin} onChange={(value) => setField("cActoAdmin", value)} />
        <div className={row2Class}>
          <TextField id="cHojas" label="Hojas de papel notarial" value={state.cHojas} onChange={(value) => setField("cHojas", value)} />
          <MoneyField id="cRecaudo" label="Recaudo Superintendencia y Fondo" value={state.cRecaudo} onChange={(value) => setField("cRecaudo", value)} />
        </div>
        <TextField id="cCorreoNotif" label="Correo para notificaciones electronicas" value={state.cCorreoNotif} onChange={(value) => setField("cCorreoNotif", value)} />
        <Checkbox id="cSinCuantia" checked={state.cSinCuantia} label="Acto sin cuantia - credito de vivienda" onChange={(checked) => setField("cSinCuantia", checked)} />
        <Checkbox id="cNoPazSalvo" checked={state.cNoPazSalvo} label="Incluir clausula de no paz y salvo" onChange={(checked) => setField("cNoPazSalvo", checked)} />
        <Checkbox id="cSarlaft" checked={state.cSarlaft} label="Incluir nota SARLAFT / tratamiento de datos" onChange={(checked) => setField("cSarlaft", checked)} />
        <Checkbox id="cNotiElec" checked={state.cNotiElec} label="Autoriza notificaciones electronicas" onChange={(checked) => setField("cNotiElec", checked)} />
      </Fieldset>
    </form>
  );
}
